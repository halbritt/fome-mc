"""Reproduce package-selection source; native acceptance remains a separate gate."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-only', action='store_true')
args = parser.parse_args()
if not args.source_only:
    parser.error('Native acceptance is not implemented for this stage; use --source-only for bounded source checks')
with tempfile.TemporaryDirectory(prefix='pod-component-fit-') as td:
    candidate = Path(td) / 'candidate'
    subprocess.run([sys.executable, str(root / 'prepare.py'), '--out', str(candidate), '--source-only'], check=True)
    for generated, retained in [('inputs/intent.json', 'intent.json'), ('receipt.json', 'receipt.json')]:
        if (candidate / generated).read_bytes() != (root / 'prepared' / retained).read_bytes():
            raise ValueError('Prepared output does not reproduce: ' + generated)
    intent = json.loads((candidate / 'inputs/intent.json').read_text())
    rows = []
    for c in intent['components']:
        state = ('power_symbol' if c['lib_id'] == 'power:PWR_FLAG' else
                 'copper_feature_policy_pending' if c['reference'] in {'JP1','JP2','JP3','JP4','JP5'} else
                 'binding_present_unqualified' if c.get('part_binding') else 'binding_missing')
        rows.append({'id': c['id'], 'reference': c['reference'], 'value': c['value'], 'state': state})
    inventory = {'schema': 'pod-binding-inventory/1', 'counts': dict(Counter(r['state'] for r in rows)), 'components': rows}
    if inventory != json.loads((root / 'inventory.json').read_text()):
        raise ValueError('Inventory mismatch')
    subprocess.run([sys.executable, str(root / 'review/check_fit.py'), str(root), str(candidate),
                    str(Path(td) / 'review.json'), '--source-only'], check=True)
print('PASS: package-selection source checks; native verification NOT_RUN')
