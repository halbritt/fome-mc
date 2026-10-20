"""Attach evidence-backed identities; no assembly or operating approval is implied."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from agent_ee.jlc_stock_capture import validate_capture

root = Path(__file__).resolve().parent
expansion = root.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--source-only', action='store_true',
                    help='prepare identity metadata without claiming native generation')
args = parser.parse_args()
out = args.out
if out.exists():
    raise SystemExit('Output must be fresh')
manifest = json.loads((root / 'manifest.json').read_text())

def pinned(record):
    p = expansion / record['path']
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('Changed evidence: ' + record['path'])
    return raw

intent = json.loads(pinned(manifest['baseline']))
by_id = {c['id']: c for c in intent['components']}
if len(by_id) != len(intent['components']):
    raise ValueError('Duplicate source component ID')
seen = set()
observations = []
validated = {}
for part in manifest['parts']:
    key = part['catalog']['path']
    if key not in validated:
        catalog = json.loads(pinned(part['catalog']))
        directory = (expansion / key).parent
        validate_capture(catalog, lambda path: (directory / path).read_bytes())
        validated[key] = catalog
    catalog = validated[key]
    identity = catalog['parts'][part['lcsc']]
    if (identity['mpn'], identity['mfr']) != (part['mpn'], part['manufacturer']):
        raise ValueError('Supplier identity mismatch')
    pinned(part['datasheet'])
    request, = [r for r in catalog['requests'] if r['lcsc'] == part['lcsc']]
    raw = json.loads(((expansion / key).parent / request['response']['path']).read_text())
    row, = [r for r in raw['data']['componentPageInfo']['list'] if r['componentCode'] == part['lcsc']]
    if 'assemblyComponentFlag' not in row:
        raise ValueError('Missing raw assembly observation')
    binding = {'Manufacturer': part['manufacturer'], 'Partnumber': part['mpn'],
               'LCSC': part['lcsc'], 'Datasheet': part['datasheet']['url'],
               'PARAM_Datasheet': json.dumps({'schema': 'agent-ee.datasheet-binding/1',
                  'sha256': part['datasheet']['sha256'], 'url': part['datasheet']['url']}, separators=(',', ':')),
               'Qualification': 'Identity metadata only; assembly and operating qualification pending'}
    for target in part['components']:
        c = by_id[target['id']]
        if target['id'] in seen or c.get('part_binding'):
            raise ValueError('Duplicate or previously bound component: ' + target['id'])
        if any(c[k] != target[k] for k in ['reference', 'value', 'footprint']):
            raise ValueError('Selected component changed: ' + target['id'])
        c['part_binding'] = binding.copy()
        seen.add(target['id'])
    observations.append({'lcsc': part['lcsc'], 'mpn': part['mpn'],
        'captured_at': identity['last_seen'], 'stock_at_capture': identity['stock'],
        'assemblyComponentFlag': row['assemblyComponentFlag'],
        'references': [c['reference'] for c in part['components']]})
if len(seen) != 171:
    raise ValueError('Expected exactly 171 newly bound components')
shutil.copytree(expansion / 'native-candidate/captured/inputs', out / 'inputs')
(out / 'inputs/intent.json').write_text(json.dumps(intent, indent=2) + '\n')
receipt = {'schema': 'pod-part-binding-receipt/1', 'new_bindings': len(seen),
           'total_bindings_present': sum(bool(c.get('part_binding')) for c in intent['components']),
           'qualification': 'Not qualified for assembly or operation', 'observations': observations}
(out / 'binding-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
if args.source_only:
    print(json.dumps({'out': str(out), 'stage': 'source-only', 'new_bindings': len(seen),
                      'native_verification': 'NOT_RUN'}))
    raise SystemExit(0)
subprocess.run([sys.executable, '-m', 'agent_ee.schematic_emitter', str(out / 'inputs/intent.json'),
               '--layout', str(out / 'inputs/emitter-layout.json'), '--captures', str(out / 'inputs'),
               '--out', str(out / 'project'), '--receipt', str(out / 'emission-receipt.json')], check=True)
for name in ['sym-lib-table', 'fp-lib-table']:
    shutil.copyfile(expansion / 'native-candidate/captured/project' / name, out / 'project' / name)
print(json.dumps({'out': str(out), 'new_bindings': len(seen), 'total_bindings': receipt['total_bindings_present']}))
