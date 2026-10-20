"""Reproduce package-selection source; native acceptance remains a separate gate."""
import argparse
from collections import Counter
from native_check import check_native
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-only', action='store_true')
parser.add_argument('--out', type=Path, help='fresh retained output directory; required for native checks')
args = parser.parse_args()
if not args.source_only and args.out is None:
    parser.error('--out NEW_DIRECTORY is required to retain native evidence or emission failures')
with tempfile.TemporaryDirectory(prefix='pod-component-fit-') as td:
    candidate = args.out if args.out is not None else Path(td) / 'candidate'
    command = [sys.executable, str(root / 'prepare.py'), '--out', str(candidate)]
    if args.source_only:
        command.append('--source-only')
    subprocess.run(command, check=True)
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
                    str(candidate / 'source-review.json'), '--source-only'], check=True)
    if not args.source_only:
        schematic = candidate / 'project/telemetry-pod.kicad_sch'
        subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml',
                        '-o', str(candidate / 'native.xml'), str(schematic)], check=True)
        subprocess.run(['kicad-cli', 'sch', 'export', 'bom', '--fields',
                        'Reference,Value,Footprint,EXCLUDE_FROM_BOM,EXCLUDE_FROM_BOARD',
                        '--labels', 'Reference,Value,Footprint,ExcludeBOM,ExcludeBoard',
                        '-o', str(candidate / 'native-bom.csv'), str(schematic)], check=True)
        subprocess.run(['kicad-cli', 'sch', 'erc', '--format', 'json',
                        '-o', str(candidate / 'erc.json'), str(schematic)], check=True)
        result = check_native(candidate / 'inputs/intent.json', candidate, root.parent / 'native-candidate')
        (candidate / 'native-review.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS: package-selection source checks; native verification ' + ('NOT_RUN' if args.source_only else 'PASS'))
