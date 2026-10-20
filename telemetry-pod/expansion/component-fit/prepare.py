"""Apply six reviewed package/identity changes; preserve electrical intent."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from agent_ee.jlc_stock_capture import validate_capture
from agent_ee.part_binding import parse_param_value

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--source-only', action='store_true')
args = parser.parse_args()
if args.out.exists():
    raise SystemExit('Output must be fresh')
manifest = json.loads((root / 'manifest.json').read_text())
base = root.parent / manifest['baseline']['path']
def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}
def pinned(record):
    raw = (root.parent / record['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('Evidence changed: ' + record['path'])
    return raw
if hashes(base) != manifest['baseline']['files_sha256']:
    raise ValueError('Baseline input tree changed')
intent = json.loads((base / 'intent.json').read_text())
by_id = {c['id']: c for c in intent['components']}
seen = set()
observations = []
for part in manifest['parts']:
    catalog = json.loads(pinned(part['catalog']))
    directory = (root.parent / part['catalog']['path']).parent
    validate_capture(catalog, lambda path: (directory / path).read_bytes())
    identity = catalog['parts'][part['lcsc']]
    if (identity['mpn'], identity['mfr']) != (part['mpn'], part['manufacturer']):
        raise ValueError('Exact identity mismatch')
    pinned(part['datasheet'])
    param = json.dumps({'schema': 'agent-ee.datasheet-binding/1',
        'sha256': part['datasheet']['sha256'], 'url': part['datasheet']['url']}, separators=(',', ':'))
    parse_param_value(param, 'PARAM_Datasheet')
    req, = [r for r in catalog['requests'] if r['lcsc'] == part['lcsc']]
    raw = json.loads((directory / req['response']['path']).read_text())
    row, = [r for r in raw['data']['componentPageInfo']['list'] if r['componentCode'] == part['lcsc']]
    for target in part['components']:
        c = by_id[target['id']]
        if target['id'] in seen or c.get('part_binding'):
            raise ValueError('Already bound or duplicate target')
        if any(c[key] != target[key] for key in ['reference', 'value', 'footprint']):
            raise ValueError('Target changed')
        seen.add(target['id'])
        c['footprint'] = part['new_footprint']
        c['part_binding'] = {'Manufacturer': part['manufacturer'], 'Partnumber': part['mpn'],
            'LCSC': part['lcsc'], 'Datasheet': part['datasheet']['url'], 'PARAM_Datasheet': param,
            'Qualification': 'Identity and package selection only; assembly and operating qualification pending'}
    observations.append({'mpn': part['mpn'], 'lcsc': part['lcsc'], 'stock_at_capture': identity['stock'],
        'captured_at': identity['last_seen'], 'assemblyComponentFlag': row['assemblyComponentFlag']})
if len(seen) != 6:
    raise ValueError('Expected six package and binding changes')
shutil.copytree(base, args.out / 'inputs')
capture = manifest['footprint_capture']
target = args.out / 'inputs' / capture['target']
if target.exists():
    raise ValueError('New footprint would replace an existing capture')
target.write_bytes(pinned(capture))
(args.out / 'inputs/intent.json').write_text(json.dumps(intent, indent=2) + '\n')
receipt = {'schema': 'pod-component-fit-receipt/1', 'footprint_changes': 6, 'new_bindings': 6,
    'total_bindings_present': sum(bool(c.get('part_binding')) for c in intent['components']),
    'observations': observations, 'qualification': 'Not qualified for assembly or operation'}
(args.out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
if args.source_only:
    print('SOURCE_ONLY: six package changes, six bindings; native verification NOT_RUN')
    raise SystemExit(0)
subprocess.run([sys.executable, '-m', 'agent_ee.schematic_emitter', str(args.out / 'inputs/intent.json'),
    '--layout', str(args.out / 'inputs/emitter-layout.json'), '--captures', str(args.out / 'inputs'),
    '--out', str(args.out / 'project'), '--receipt', str(args.out / 'emission-receipt.json')], check=True)
for name in ['sym-lib-table', 'fp-lib-table']:
    shutil.copyfile(root.parent / 'native-candidate/captured/project' / name, args.out / 'project' / name)
