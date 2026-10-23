"""Regenerate revision-delta.json (fome-pod.requirements-delta/1): the baseline registry record
(../spec-record.json) versus the current microSD record (spec-record.json), over requirement and prose entries.
Usage (fome-mc root): python3 -I telemetry-pod/expansion/requirements/rev3-microsd/make_revision_delta.py"""
import hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
old = json.loads((HERE / 'revision-delta.json').read_text())
base_path, cur_path = HERE.parent / 'spec-record.json', HERE / 'spec-record.json'
spec = ROOT / 'telemetry-pod/REQUIREMENTS.md'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(base_path) != old['baseline']['sha256']:
    raise SystemExit('baseline record changed; the delta baseline is fixed')
B, C = json.loads(base_path.read_text()), json.loads(cur_path.read_text())
def entries(doc):
    out = {r['id']: r['text'] for r in doc['requirements']}
    out.update({p['id']: p['text'] for p in doc['prose']})
    return out
a, b = entries(B), entries(C)
added = [{'id': i, 'text': b[i]} for i in sorted(set(b) - set(a))]
removed = [{'id': i, 'text': a[i]} for i in sorted(set(a) - set(b))]
changed = [{'id': i, 'before_text': a[i], 'after_text': b[i],
            'before_text_sha256': hashlib.sha256(a[i].encode()).hexdigest(),
            'after_text_sha256': hashlib.sha256(b[i].encode()).hexdigest(),
            'authority': ('owner-relayed a13a1ba8@2; accepted AGENTEE-486 / 27c51f73: height ESTIMATE correction, '
                          'not a measured 90 mm cap and not a new owner measurement request; the same ID transfers no '
                          'earlier acceptance') if i == 'POD-ME-1' else None}
           for i in sorted(set(a) & set(b)) if a[i] != b[i]]
doc = dict(old)
doc['current'] = {'path': 'telemetry-pod/REQUIREMENTS.md', 'record_sha256': sha(cur_path), 'repository': 'fome-mc',
                  'spec': {'bytes': spec.stat().st_size, 'name': 'REQUIREMENTS.md', 'sha256': sha(spec)},
                  'note': 'identity by content hash (the accepted revision; no commit pin)'}
doc.update(added=added, removed=removed, changed=changed,
           counts={'added': len(added), 'changed': len(changed), 'removed': len(removed),
                   'unchanged': len(set(a) & set(b)) - len(changed)})
(HERE / 'revision-delta.json').write_text(json.dumps(doc, indent=2 if '\n  "' in (HERE / 'revision-delta.json').read_text()[:5] else 1) + '\n')
print(doc['counts'], [c['id'] for c in changed])
