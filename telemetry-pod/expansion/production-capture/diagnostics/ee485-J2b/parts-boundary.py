"""Actual parts capability at the writer-mutable deviations boundary; no native emission."""
import hashlib
import json
from pathlib import Path
from agent_ee.parts_subset import capability


def evaluate(root):
    doc = json.loads((root / 'composition/parts.json').read_text())
    source = {k: doc['declaration_source'][k] for k in ('path', 'locator')}
    scope = {'checks': [{'id': 'netlist', 'kind': 'netlist'}, {'id': 'parts', 'kind': 'parts'}],
             'baseline': {'requirements': [{'id': 'parts-membership', 'checks': ['parts'], 'source': source}]},
             'mutable_inputs': ['project/telemetry-pod.kicad_pcb', 'project/telemetry-pod.kicad_sch',
                                'composition/intent.writer.json', 'composition/deviations.json']}
    files = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in root.rglob('*') if p.is_file()}
    return capability({'manifest': 'composition/parts.json', 'netlist_check': 'netlist',
                       'requirement_id': 'parts-membership'}, files, root, scope, 'parts')

old = Path('build/ee485-J2b-run/cap')
try:
    evaluate(old)
except ValueError as exc:
    if str(exc) != 'parts dependency cannot be mutable: composition/deviations.json':
        raise
    print('old actual capture REFUSED:', exc)
else:
    raise AssertionError('old mutable provenance was accepted')
new = Path('build/ee485-precheck/capture')
result = evaluate(new)
assert 'composition/deviations.json' not in result['immutable_inputs']
assert 'composition/j1-j2-assembly-source.json' in result['immutable_inputs']
assert json.loads((new / 'composition/deviations.json').read_bytes()) == json.loads(
    (new / 'composition/j1-j2-assembly-source.json').read_bytes())
print('corrected actual capture ACCEPTED:', len(result['immutable_inputs']), 'immutable inputs')
print('scope: parts capability only; no driver or emission rerun')
