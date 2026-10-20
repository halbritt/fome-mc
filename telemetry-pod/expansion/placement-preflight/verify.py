"""Replay the unmodified imported board's placement admission refusal."""
import gzip
import hashlib
import json
from pathlib import Path
from agent_ee.placer import pack
P=Path(__file__).resolve().parent
facts=json.loads(gzip.decompress((P/'probe.json.gz').read_bytes()))
assert facts['board_sha256']==hashlib.sha256((P.parent/'probe-import/staged-board.kicad_pcb').read_bytes()).hexdigest()
policy=json.loads((P/'policy.json').read_text())
result=pack(facts,policy)
assert result==json.loads((P/'result.json').read_text())
assert result['status']=='unsupported_geometry' and result['outcome']=='unknown'
assert result['steps_used']==0 and result['placements']==[]
assert result['reason']=="JP1 pad '1': native pad shape 6 not qualified for packing"
for name,digest in json.loads((P/'provenance.json').read_text())['files'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
print('PASS: exact real-board custom-pad refusal reproduced; no placement search or proposal')
