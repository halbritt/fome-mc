"""Conditional DC and acquisition arithmetic, not a hardware qualification."""
import itertools
import json
import math
import sys
from pathlib import Path


def parallel(a, b):
    return 1 / (1/a + 1/b)


def line_voltage(resistance, excitation=2.495, pullup=10_000, loading=20_000):
    return excitation / (1 + pullup / parallel(resistance, loading))


def recover_resistance(line, excitation, pullup=10_000, loading=20_000):
    if not math.isfinite(line) or not math.isfinite(excitation) or excitation <= 0:
        raise ValueError('Invalid measurement')
    if line <= 0 or line >= excitation * loading / (pullup + loading):
        raise ValueError('Short/open/out-of-range: not a finite sensor resistance')
    return 1 / ((excitation-line)/(line*pullup) - 1/loading)


# Deliberately account for hot resistor FILM, not only ambient. Aging is separate.
bias_delta = (1+.01)*(1+100e-6*130)-1  # Conservative symmetric product bound.
pullup_delta = (1+.001)*(1+25e-6*130)-1
bias_values = (200*(1-bias_delta), 200*(1+bias_delta))
pullup_values = (10_000*(1-pullup_delta), 10_000*(1+pullup_delta))
monitor_min = (3*499_000 + 4_990)*(1-pullup_delta)
excitation_range = (2.4, 2.586)  # Planning envelope, not a full-temperature guarantee.
upper = excitation_range[1]
monitor_load = upper/monitor_min
short_load = 4*upper/min(pullup_values)
cold_min_shunt = (4.95-1.5-upper)/(2*max(bias_values))-short_load-monitor_load
vf_ceiling = 4.95-upper-2*max(bias_values)*(short_load+monitor_load+.001)

faults = {}
for voltage in (16., 24.):
    corners = []
    # All four auxiliary INPUTS and the AUX POWER pin are externally driven.
    # Zero diode drop maximizes bias current/power. Internal24V survival is NOT proved.
    for exc, r1, r2, rp in itertools.product(excitation_range, bias_values,
                                            bias_values, pullup_values):
        bias_current = (voltage-exc)/(r1+r2)
        input_current = (voltage-exc)/rp
        shunt_current = bias_current+4*input_current  # omit monitor load conservatively
        corners.append((shunt_current, exc*shunt_current,
                        bias_current**2*r1, input_current**2*rp))
    faults[str(int(voltage))] = {
        'max_shunt_current_A': max(c[0] for c in corners),
        'max_shunt_power_W': max(c[1] for c in corners),
        'max_each_bias_resistor_power_W': max(c[2] for c in corners),
        'max_each_pullup_power_W': max(c[3] for c in corners),
        'shunt_rise_K_if_board_matches_datasheet_206K_per_W': max(c[1] for c in corners)*206,
    }

examples = []
for rt in (100., 1000., 10_000., 100_000., 1_000_000.):
    line = line_voltage(rt)
    examples.append({'sensor_ohm': rt, 'line_V': line, 'buffer_V': line/2,
                     'ideal_MCP3208_code': line/2/2.5*4096,
                     'recovered_ohm_with_loading': recover_resistance(line, 2.495),
                     'wrong_ohm_if_loading_ignored': 10_000*line/(2.495-line),
                     'sensor_power_W': line**2/rt})
# Independently check the inverse against KCL through a wide resistance range.
for i in range(1, 120):
    rt = 10**(i/20)
    line = line_voltage(rt)
    if not math.isclose((2.495-line)/10_000, line/rt+line/20_000, rel_tol=1e-12):
        raise ValueError('KCL failed')
    if not math.isclose(recover_resistance(line,2.495),rt,rel_tol=1e-10):
        raise ValueError('Loaded-divider inverse failed')
for invalid in (-1., 0., 2.495*2/3, 2.495, math.nan, math.inf):
    try:
        recover_resistance(invalid,2.495)
    except ValueError:
        pass
    else:
        raise ValueError('Invalid/open/short measurement converted to resistance')

rth = parallel(10_000, 10_000+10_000)  # Open sensor, largest nominal pole.
tau = rth*100e-9
conv = 1061/(1.024e6*.98)
result = {
    'status': 'conditional DC/acquisition model; physical qualification pending',
    'planning_excitation_V': list(excitation_range),
    'bias_fractional_allowance': bias_delta,
    'pullup_fractional_allowance': pullup_delta,
    'normal_all_shorted_min_shunt_A_if_VF_le_1_5V': cold_min_shunt,
    'max_diode_VF_for_1mA_shunt_at_min_aux_and_four_shorts_V': vf_ceiling,
    'source_fault_corners': faults,
    'bias_resistor_ambient_derating_W_if_linear_70_to_155C': {
        str(t): 1.5*(155-t)/85 for t in (105,125)},
    'nominal_no_sensor_open_line_V': 2.495*2/3,
    'nominal_short_line_V': 0.,
    'nominal_max_sensor_power_W_any_resistance': (2.495*2/3)**2/(4*parallel(10_000,20_000)),
    'nominal_resistance_at_max_sensor_power_ohm': parallel(10_000,20_000),
    'nominal_max_input_RC_seconds': tau,
    'full_scale_step_to_half_12bit_LSB_seconds': math.log(8192)*tau,
    'ten_channel_four_round_ideal_schedule_seconds': 4*conv+10*162/400_000,
    'diagnostic_excitation_volts_per_code': 2.048/4/32768*301,
    'examples': examples,
    'excludes': ['BAV199 cold VF bound', 'dynamic reverse-current/backfeed and surge',
                 'TL431 full-temperature current-related error and stability',
                 'resistor aging and layout thermal resistance/coupling',
                 'capacitor effective capacitance and ESR',
                 'sensor R-T calibration, tolerance, self-heating temperature, and harness error',
                 'ADC/buffer/reference errors and actual diagnostic timing'],
}
if cold_min_shunt < .001 or faults['24']['max_shunt_current_A'] >= .1:
    raise ValueError('Candidate does not meet its declared conditional DC budget')
root = Path(__file__).resolve().parent
if sys.argv[1:] == ['--check']:
    if json.loads((root/'calculations.json').read_text()) != result:
        raise ValueError('Saved calculation differs from recomputation')
    print('PASS: conditional current/power/transfer/settling calculations; hardware unqualified')
elif not sys.argv[1:]:
    print(json.dumps(result, indent=2, allow_nan=False))
else:
    raise SystemExit('usage: calculate.py [--check]')
