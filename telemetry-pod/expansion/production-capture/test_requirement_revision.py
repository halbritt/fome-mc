"""AGENTEE-488c controls for requirement_revision.problems: positive exact delta; negatives changed-same-ID,
unrelated row, stale pin, prose/acceptance change, missing correction. Run: python3 -I test_requirement_revision.py"""
import copy, hashlib, importlib.util, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
X = HERE.parent
spec = importlib.util.spec_from_file_location('requirement_revision', HERE / 'requirement_revision.py')
rv = importlib.util.module_from_spec(spec); spec.loader.exec_module(rv)
pinned = json.loads((X / 'requirements/compiled/requirements-map/spec-record.json').read_text())
current = json.loads((X / 'requirements/rev3-microsd/spec-record.json').read_text())
SPEC = hashlib.sha256((X.parent / 'REQUIREMENTS.md').read_bytes()).hexdigest()
REC = hashlib.sha256((X / 'requirements/rev3-microsd/spec-record.json').read_bytes()).hexdigest()
res = []
def case(name, cond):
    res.append(bool(cond)); print(('PASS ' if cond else 'FAIL ') + name)
def row(doc, i):
    return next(r for r in doc['requirements'] if r['id'] == i)
case('positive: exact accepted delta on the real pinned/current records', rv.problems(pinned, current, SPEC, REC) == [])
c = copy.deepcopy(current); r = row(c, 'POD-ME-1'); r['text'] += ' (edited)'; r['text_sha256'] = hashlib.sha256(r['text'].encode()).hexdigest()
case('negative: a different text under the allowed ID refuses', any('exact accepted correction' in p for p in rv.problems(pinned, c, SPEC, REC)))
c = copy.deepcopy(current); row(c, 'POD-ME-1')['kind'] = 'acceptance'
case('negative: POD-ME-1 changed outside its text refuses', any('outside its text' in p for p in rv.problems(pinned, c, SPEC, REC)))
c = copy.deepcopy(current); other = next(r for r in c['requirements'] if r['id'] not in ('POD-ME-1', 'POD-CD-STORAGE')); other['text'] += 'x'
case('negative: an unrelated changed row refuses', any('is not an accepted revision' in p for p in rv.problems(pinned, c, SPEC, REC)))
c = copy.deepcopy(current); c['requirements'] = [r for r in c['requirements'] if r['id'] != c['requirements'][0]['id'] or r['id'] in ('POD-ME-1', 'POD-CD-STORAGE')]
case('negative: a removed row refuses', any('removed rows' in p for p in rv.problems(pinned, c, SPEC, REC)))
case('negative: stale spec pin refuses', any('accepted REQUIREMENTS.md' in p for p in rv.problems(pinned, current, '0' * 64, REC)))
case('negative: stale record pin refuses', any('accepted recapture' in p for p in rv.problems(pinned, current, SPEC, '0' * 64)))
case('negative: the correction absent (pinned text kept) refuses', any('not present (stale)' in p for p in rv.problems(pinned, copy.deepcopy(pinned) | {'requirements': [*pinned['requirements'], row(current, 'POD-CD-STORAGE')]}, SPEC, REC)))
c = copy.deepcopy(current); c['prose'][0]['text'] += 'x'
case('negative: prose change refuses', 'prose differs' in rv.problems(pinned, c, SPEC, REC))
print(f'{sum(res)}/{len(res)} passed'); sys.exit(0 if all(res) else 1)
