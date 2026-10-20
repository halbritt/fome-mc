"""Calculate the Hall pull-up continuous negative-short envelope; not qualification."""
import json

# Declared candidate envelope. 6.5 V is a design ceiling still to be proved
# for the protected 6.3 V rail, including tolerance and transient behavior.
rail_max_v = 6.5
fault_v = -24.0
nominal_r = 620.0
initial_tolerance = 0.01
tcr_per_k = 100e-6
film_max_c = 155.0
reference_c = 25.0
life_drift_allowance = 0.02
r_min = nominal_r * (1-initial_tolerance) * (
    1-tcr_per_k*(film_max_c-reference_c)) * (1-life_drift_allowance)
voltage_v = rail_max_v - fault_v  # zero diode drop maximizes dissipation
# P1 = V^2 R1/(R1+R2)^2. For R1,R2 >= Rmin its global maximum
# occurs at R1=R2=Rmin, not at opposite tolerance extremes.
p_each_w = voltage_v**2 / (4*r_min)
i_a = voltage_v/(2*r_min)
report = {
    'status': 'calculated candidate envelope; assembled thermal validation pending',
    'part_candidate': 'Vishay CRCW2512620RFKEG / C3988368',
    'assumptions': {
        'rail_max_v_unverified': rail_max_v, 'continuous_signal_fault_v': fault_v,
        'diode_forward_drop_v_conservative': 0,
        'resistors_per_channel': 2, 'channels': 2,
        'nominal_resistance_ohm': nominal_r,
        'initial_tolerance_fraction': initial_tolerance,
        'tcr_per_kelvin': tcr_per_k,
        'film_temperature_ceiling_c': film_max_c,
        'additional_life_drift_fraction': life_drift_allowance,
        'life_drift_scope': 'design allowance, not indefinite-life guarantee',
    },
    'resistance_min_ohm': r_min,
    'maximum_channel_current_a': i_a,
    'maximum_each_resistor_power_w': p_each_w,
    'maximum_two_channel_resistor_power_w': 4*p_each_w,
    'nominal_family_derating_w': {
        str(t): (film_max_c-t)/(film_max_c-70.0) for t in (85,105,125)},
    'maximum_assembled_film_to_local_ambient_thermal_resistance_k_per_w': {
        str(t): (film_max_c-t)/p_each_w for t in (85,105)},
    'nominal_derating_curve_maximum_local_ambient_c': film_max_c-85*p_each_w,
    'exclusions': [
        'diode heating and transient behavior', 'sensor survival',
        'rail above 6.5 V', 'fault below -24 V',
        'coupled heating without a verified assembled thermal model',
        'assembly availability and exact part binding',
    ],
}
print(json.dumps(report, indent=2))
