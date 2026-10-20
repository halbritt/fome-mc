"""Reproduce design-study arithmetic; no circuit or hardware qualification."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
for source in json.loads((root / 'sources.json').read_text())['sources']:
    digest = hashlib.sha256((root / source['file']).read_bytes()).hexdigest()
    if digest != source['sha256']:
        raise ValueError(f"Captured source changed: {source['file']}")

upper = 3 * 499_000.0
lower = 4_990.0
ratio = (upper + lower) / lower
# Sum initial tolerance and worst drift from25 C; no aging allowance claimed.
delta = 0.001 + 25e-6 * max(abs(-40 - 25), abs(125 - 25))
fraction_min = lower * (1 - delta) / (upper * (1 + delta) + lower * (1 - delta))
fraction_max = lower * (1 + delta) / (upper * (1 - delta) + lower * (1 + delta))
lsb = 2.048 / 4 / 32768
conversion = 1061 / (1.024e6 * .98)
clocks = 27 + 36 + 18 + 36 + 45
result = {
    'status': 'passive-model arithmetic only; unresolved physical and measurement error bounds',
    'nominal_attenuation': ratio,
    'resistor_individual_fractional_allowance': delta,
    'attenuation_fraction_min': fraction_min,
    'attenuation_fraction_max': fraction_max,
    'max_absolute_pin_V_at_node_60V_unloaded': 60 * fraction_max,
    'absolute_limit_margin_V_at_AVDD_zero_unloaded': .3 - 60 * fraction_max,
    'scale_error_fraction_min': fraction_min * ratio - 1,
    'scale_error_fraction_max': fraction_max * ratio - 1,
    'reference_screening_fraction_if_full_span_box_drift': .0015 + 30e-6 * 165,
    'nominal_RC_seconds_at_100nF': upper * lower / (upper + lower) * 100e-9,
    'nominal_rail_volts_per_code': lsb * ratio,
    'nominal_code_by_rail_V': {str(v): v / (lsb * ratio) for v in (3.3, 5.0, 6.3, 12.0)},
    'single_shot_seconds_at_slowest_clock': conversion,
    'I2C_clocks_per_readback_checked_conversion': clocks,
    'nine_conversion_bus_seconds_at_400kHz': 9 * clocks / 400_000,
    'three_round_ideal_schedule_seconds': 3 * conversion + 9 * clocks / 400_000,
    'excludes': ['input leakage and loading', 'aging', 'ADC offset/gain/noise bounds',
                 'parasitics and ground shift', 'upstream transient clamp proof',
                 'powered-off backfeed', 'host/bus scheduling latency', 'analog settling policy'],
}
if sys.argv[1:] == ['--check']:
    if json.loads((root / 'calculations.json').read_text()) != result:
        raise ValueError('Saved arithmetic differs from recomputation')
    print('PASS: captured hashes and saved design-study arithmetic; no hardware qualification')
elif not sys.argv[1:]:
    print(json.dumps(result, indent=2))
else:
    raise SystemExit('usage: calculate.py [--check]')
