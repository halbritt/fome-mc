"""Select a 30.1k + 1.2k series implementation of the original 31.3k divider top."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from agent_ee.jlc_stock_capture import validate_capture
from agent_ee.part_binding import parse_param_value

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--source-only', action='store_true')
args = parser.parse_args()
if args.out.exists():
    raise SystemExit('Output must be fresh')
manifest = json.loads((ROOT / 'manifest.json').read_text())
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def hashes(directory):
    return {str(p.relative_to(directory)): sha(p) for p in directory.rglob('*') if p.is_file()}
with tempfile.TemporaryDirectory(prefix='pod-series-base-') as td:
    base = Path(td) / 'base'
    subprocess.run([sys.executable, str(ROOT.parent / 'component-fit/prepare.py'), '--source-only', '--out', str(base)], check=True)
    if hashes(base / 'inputs') != manifest['baseline_files_sha256']:
        raise ValueError('Baseline input tree differs')
    shutil.copytree(base / 'inputs', args.out / 'inputs')
inputs = args.out / 'inputs'
intent = json.loads((inputs / 'intent.json').read_text())
components = {c['reference']: c for c in intent['components']}
old = components['R60']
if old != {'footprint':'Resistor_SMD:R_0603_1608Metric','id':'supervisor/R60','lib_id':'Device:R',
           'reference':'R60','units':[1],'value':'31.3 kohm 0.1%'} or 'R181' in components:
    raise ValueError('Original divider or new reference differs')
new = copy.deepcopy(old)
new.update(id='supervisor/R181', reference='R181')
intent['components'].insert(intent['components'].index(old) + 1, new)
components['R181'] = new
catalog = json.loads((ROOT / 'stock/catalog.json').read_text())
if sha(ROOT / 'stock/catalog.json') != manifest['catalog_sha256']:
    raise ValueError('Catalog changed')
validate_capture(catalog, lambda p: (ROOT / 'stock' / p).read_bytes())
observations = []
if {p['reference'] for p in manifest['parts']} != {'R60','R181'} or len(manifest['parts']) != 2:
    raise ValueError('Expected two resistor identities')
for part in manifest['parts']:
    c = components[part['reference']]
    identity = catalog['parts'][part['lcsc']]
    if (identity['mpn'], identity['mfr']) != (part['mpn'], part['manufacturer']):
        raise ValueError('Exact identity mismatch')
    ds = part['datasheet']
    if sha(ROOT / ds['path']) != ds['sha256']:
        raise ValueError('Manufacturer source changed')
    param = json.dumps({'schema':'agent-ee.datasheet-binding/1','sha256':ds['sha256'],'url':ds['url']}, separators=(',', ':'))
    parse_param_value(param, 'PARAM_Datasheet')
    c['value'] = part['value']
    c['part_binding'] = {'Manufacturer':part['manufacturer'],'Partnumber':part['mpn'],'LCSC':part['lcsc'],
                         'Datasheet':ds['url'],'PARAM_Datasheet':param,
                         'Qualification':'Identity and series-divider selection only; assembly and operating qualification pending'}
    request, = [r for r in catalog['requests'] if r['lcsc'] == part['lcsc']]
    raw = json.loads((ROOT / 'stock' / request['response']['path']).read_text())
    row, = [r for r in raw['data']['componentPageInfo']['list'] if r['componentCode'] == part['lcsc']]
    observations.append({'reference':part['reference'],'mpn':part['mpn'],'lcsc':part['lcsc'],
                         'stock_at_capture':identity['stock'],'captured_at':identity['last_seen'],
                         'assemblyComponentFlag':row['assemblyComponentFlag']})
sense, = [n for n in intent['nets'] if n['name'] == 'SUP_U18_SENSE']
terminal = {'component':'supervisor/R60','pin':{'number':'2'}}
if sense['terminals'].count(terminal) != 1:
    raise ValueError('Sense endpoint differs')
sense['terminals'][sense['terminals'].index(terminal)] = {'component':'supervisor/R181','pin':{'number':'2'}}
bridge = {'id':'supervisor-SUP_U18_TOP_SERIES','name':'SUP_U18_TOP_SERIES','terminals':[
    terminal, {'component':'supervisor/R181','pin':{'number':'1'}}]}
if any(n['id'] == bridge['id'] or n['name'] == bridge['name'] for n in intent['nets']):
    raise ValueError('Intermediate net already exists')
intent['nets'].append(bridge)
layout = json.loads((inputs / 'emitter-layout.json').read_text())
group, = [g for g in layout['groups'] if 'supervisor/R60' in g['components']]
group['components'].insert(group['components'].index('supervisor/R60') + 1, 'supervisor/R181')
(inputs / 'intent.json').write_text(json.dumps(intent, indent=2) + '\n')
(inputs / 'emitter-layout.json').write_text(json.dumps(layout, indent=2) + '\n')
receipt = {'schema':'pod-series-divider-receipt/1','components':len(intent['components']),
    'bindings_present':sum(bool(c.get('part_binding')) for c in intent['components']),
    'top_nominal_ohm':31300,'falling_threshold_nominal_v':4.7495,'extra_resistors':1,
    'observations':observations,'native_verification':'NOT_RUN','qualification':'Not qualified for assembly or operation'}
(args.out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
if args.source_only:
    print('SOURCE_ONLY: exact series-divider source prepared; native verification NOT_RUN')
    raise SystemExit(0)
subprocess.run([sys.executable,'-m','agent_ee.schematic_emitter',str(inputs / 'intent.json'),
                '--layout',str(inputs / 'emitter-layout.json'),'--captures',str(inputs),
                '--out',str(args.out / 'project'),'--receipt',str(args.out / 'emission-receipt.json')], check=True)
for name in ['sym-lib-table','fp-lib-table']:
    shutil.copyfile(ROOT.parent / 'native-candidate/captured/project' / name, args.out / 'project' / name)
