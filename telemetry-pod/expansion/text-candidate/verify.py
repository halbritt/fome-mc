"""Verify retained exact artifacts and the explicitly bounded replay results."""
import gzip
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
provenance = json.loads((root / 'provenance.json').read_text())
for name, digest in provenance['files'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
report = json.loads((root / 'native-review.json').read_text())
assert report['status'] == 'PASS' and report['checks'] == 34533
assert report['source_components'] == 333 and report['xml_components'] == 327
assert report['sha256']['schematic'] == hashlib.sha256(
    (root / 'project/telemetry-pod.kicad_sch').read_bytes()).hexdigest()
erc = json.loads((root / 'erc.json').read_text())
assert erc['sheets'] and not any(s['violations'] for s in erc['sheets'])
new = json.loads(gzip.decompress((root / 'text-overlaps.json.gz').read_bytes()))
old = json.loads(gzip.decompress((root / 'baseline-text-overlaps.json.gz').read_bytes()))
assert not new['overlaps'] and len(old['overlaps']) == 17
for kind, count in [('label', 684), ('field', 668)]:
    def texts(report):
        return sorted((t['text'], t.get('reference') or '', t.get('field') or '')
                      for t in report['texts'] if t['kind'] == kind)
    assert texts(new) == texts(old) and len(texts(new)) == count
assert json.loads((root / 'native-text/text-placement.json').read_text()) == {
    'before': [], 'moved': [], 'after': []}
assert provenance['strict_schematic_identical'] is True
execution = json.loads((root / 'native-text/execution.json').read_text())
assert execution['execution'] == 'ok' and execution['exit_code'] == 0
print('PASS: retained hashes, ERC, native correspondence, text multisets and bounded overlap results')
