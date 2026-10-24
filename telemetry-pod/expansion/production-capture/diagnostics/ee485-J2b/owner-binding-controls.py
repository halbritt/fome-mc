"""Native-source boundary controls for optional candidate owner rebinding."""
import ast
import copy
import json
from pathlib import Path
from agent_ee.placement_probe import extract
source=Path('telemetry-pod/expansion/agentee-489-source/materialize.py')
node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='candidate_owners')
namespace={'copy':copy};exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),namespace)
bind=namespace['candidate_owners']
recipe=json.loads(Path('telemetry-pod/expansion/agentee-490-mechanical-inputs/bound-reservations.json').read_text())
capture=extract(Path('telemetry-pod/telemetry-pod.kicad_pcb'))
original=copy.deepcopy(recipe)
row=next(r for r in recipe['base_486_items'] if 'pad_uuid' in r['geometry'])
ref=row['reference'];row['uuid']='stale-owner-fixture';row['geometry']['pad_uuid']='stale-pad-fixture'
fixture=copy.deepcopy(recipe)
updated,migrations=bind(recipe,capture)
assert recipe==fixture
assert sorted(r['id'] for r in updated['base_486_items']+updated['board_side_access_closure']['rows'])==sorted(r['id'] for r in original['base_486_items']+original['board_side_access_closure']['rows'])
assert any(m['reference']==ref and m['source']['uuid']=='stale-owner-fixture' for m in migrations)
for label, changed in [('missing reference',[f for f in capture['footprints'] if f['ref']!=ref]),('duplicate reference',capture['footprints']+[next(f for f in capture['footprints'] if f['ref']==ref)])]:
    try:bind(recipe,{**capture,'footprints':changed})
    except ValueError as exc:print(label,'REFUSED:',exc)
    else:raise AssertionError(label+' accepted')
changed=copy.deepcopy(capture)
fp=next(f for f in changed['footprints'] if f['ref']==ref)
number=row['geometry']['pad_number'];fp['pads'].append(copy.deepcopy(next(p for p in fp['pads'] if p['number']==number)))
try:bind(recipe,changed)
except ValueError as exc:print('duplicate pad identity REFUSED:',exc)
else:raise AssertionError('ambiguous pad accepted')
print('native full-source identity rebinding PASS; recipe unchanged; preserved 44 row ids')
print('scope: control only, not regenerated candidate access acceptance')
