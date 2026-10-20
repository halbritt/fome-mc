"""Produce source identity inventory; binding presence is not qualification."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
selected = json.loads((root/'selections.json').read_text())
raw = (root/selected['intent']['path']).read_bytes()
if hashlib.sha256(raw).hexdigest() != selected['intent']['sha256']:
    raise ValueError('Intent changed; reconcile selections before generating inventory')
intent = json.loads(raw)
by_id = {}
for part in selected['parts']:
    for component in part['components']:
        if component['id'] in by_id:
            raise ValueError('Duplicate selection: '+component['id'])
        by_id[component['id']] = part
rows = []
# Explicit current copper-feature identities; never infer population from a prefix.
copper_ids = {'can2/JP1', 'thermistor/JP2', 'thermistor/JP3', 'thermistor/JP4', 'thermistor/JP5'}
for component in intent['components']:
    ref = component['reference']
    if component['lib_id'] == 'power:PWR_FLAG':
        state = 'power_symbol'
    elif component['id'] in copper_ids:
        state = 'copper_feature_policy_pending'
    elif component['id'] in by_id:
        state = 'selected_not_bound'
    elif component.get('part_binding'):
        state = 'binding_present_unverified'
    else:
        state = 'unselected'
    row = {'id': component['id'], 'reference': ref, 'value': component['value'],
           'lib_id': component['lib_id'], 'footprint': component['footprint'], 'state': state}
    if component['id'] in by_id:
        row['selected_mpn'] = by_id[component['id']]['mpn']
    rows.append(row)
result = {'schema': 'pod-expanded-part-inventory/1',
          'intent_sha256': selected['intent']['sha256'],
          'counts': dict(sorted(Counter(row['state'] for row in rows).items())),
          'components': rows}
if sys.argv[1:] == ['--check']:
    if result != json.loads((root/'inventory.json').read_text()):
        raise ValueError('Inventory differs from captured source and explicit selections')
    print(json.dumps(result['counts'],sort_keys=True))
elif not sys.argv[1:]:
    print(json.dumps(result,indent=2))
else:
    raise SystemExit('usage: inventory.py [--check]')
