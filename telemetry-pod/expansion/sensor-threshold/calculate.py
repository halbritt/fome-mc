"""Conditional static divider comparison; does not select or modify R60."""
import hashlib
import json
from pathlib import Path
from agent_ee.jlc_stock_capture import validate_capture

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'manifest.json').read_text())
for record in manifest['sources']:
    data = (ROOT.parent / record['path']).read_bytes()
    if hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError('Source changed: ' + record['path'])
catalog = json.loads((ROOT / 'stock/catalog.json').read_text())
validate_capture(catalog, lambda path: (ROOT / 'stock' / path).read_bytes())
part = catalog['parts']['C705766']
if (part['mpn'], part['mfr']) != ('RT0603BRD0731K6L', 'YAGEO'):
    raise ValueError('Exact candidate identity changed')
intent = json.loads((ROOT.parent / 'component-fit/prepared/intent.json').read_text())
by_ref = {c['reference']: c for c in intent['components']}
if by_ref['R60']['value'] != '31.3 kohm 0.1%' or by_ref['R60'].get('part_binding'):
    raise ValueError('Unchanged R60 baseline no longer applies')
if by_ref['R61']['part_binding']['Partnumber'] != 'RT0603BRD0710KL':
    raise ValueError('Divider bottom selection changed')
rows = []
for upper_c in [25, 105, 125]:
    # Bound both signs of independent TCR, with reference temperature anywhere20..25C.
    # Interval includes -40C. No matched-resistor TCR cancellation is assumed.
    delta_c = max(abs(t - ref) for t in [-40, upper_c] for ref in [20, 25])
    lo = (1 - .001) * (1 - 25e-6 * delta_c)
    hi = (1 + .001) * (1 + 25e-6 * delta_c)
    for top in [31200, 31300, 31600]:
        rhi, rlo = top * hi, top * lo
        # Signed100nA is an explicit assumption at threshold, not a guaranteed TI bound there.
        fall_min = 1.15 * .99 * (1 + rlo / (10000 * hi)) - 100e-9 * rhi
        fall_max = 1.15 * 1.01 * (1 + rhi / (10000 * lo)) + 100e-9 * rhi
        # Independently combine threshold accuracy and maximum relative hysteresis conservatively.
        rise_max = 1.15 * 1.01 * (1 + .00825) * (1 + rhi / (10000 * lo)) + 100e-9 * rhi
        rows.append({'top_ohm': top, 'temperature_interval_c': [-40, upper_c],
                     'max_delta_from_reference_c': delta_c, 'fall_nominal_v': 1.15 * (1 + top/10000),
                     'fall_min_v': fall_min, 'fall_max_v': fall_max, 'rise_max_v': rise_max,
                     'margin_below_assumed_4p95v': 4.95 - rise_max})
print(json.dumps({'schema': 'pod-supervisor-threshold-study/1', 'status': 'CONDITIONAL_ANALYSIS',
    'selection': 'R60 unchanged; no binding added', 'candidate_mpn': part['mpn'],
    'stock_at_capture': part['stock'], 'captured_at': part['last_seen'],
    'assumptions': {'sense_current_a': [-100e-9, 100e-9], 'healthy_rail_min_v': 4.95,
                    'resistor_reference_temperature_c': [20, 25], 'resistor_tcr_ppm_per_k': 25,
                    'resistor_initial_tolerance': .001, 'sense_threshold_nominal_v': 1.15,
                    'sense_threshold_accuracy': .01, 'maximum_relative_hysteresis': .00825},
    'rows': rows, 'limitations': ['TI sense current limit is specified at VSENSE=5V; use at threshold is conditional.',
    '4.95V is illustrative at the local U6/U18 node; no healthy-load minimum there is established. Downstream drops are separately unobserved by U18.',
    'Resistor temperature interval is local part temperature, not enclosure ambient; self-heating unqualified.',
    'No guaranteed assertion/release timing, noise immunity, transient behavior or hardware acceptance.']}, indent=2))
