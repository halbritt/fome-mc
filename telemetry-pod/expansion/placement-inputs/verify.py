"""Verify candidate sides and preserve the actual change-scope refusal."""
import gzip
import hashlib
import json
from pathlib import Path
from agent_ee.placement_adapter import write_scope
from agent_ee.board_envelope import validate
from agent_ee.placer_runner import _netlist_binding
P=Path(__file__).resolve().parent
raw=gzip.decompress((P/'rejected-seed.kicad_pcb.gz').read_bytes())
facts=json.loads(gzip.decompress((P/'seed-probe.json.gz').read_bytes()))
assert hashlib.sha256(raw).hexdigest()==facts['board_sha256']
expected=json.loads((P/'write-scope.json').read_text())
result=write_scope((P.parent/'probe-import/staged-board.kicad_pcb').read_bytes(),raw,expected['protected'])
assert result==expected and len(result['violations'])==867
assert result['status']!='allowed'
assign=json.loads((P/'side-assignment.json').read_text()); rows=[(r,g['side']) for g in assign['groups'] for r in g['references']]
assert len(rows)==len(dict(rows))==327
sides=dict(rows);sides.update({r:'F' for r in assign['board_only']['references']})
assert sides=={f['ref']:f['side'] for f in facts['footprints']}
assert sum(s=='B' for s in sides.values())==169
_netlist_binding((P.parent/'revised-native/native.xml').read_bytes(),facts,frozenset(assign['board_only']['references']))
assert validate((P/'envelope.json').read_bytes())==json.loads((P/'envelope-validation.json').read_text())
for name,digest in json.loads((P/'provenance.json').read_text())['files'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
print('PASS: candidate side membership/native nets; exact rejected write scope retained; no seed adoption')
