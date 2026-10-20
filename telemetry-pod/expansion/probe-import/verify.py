"""Replay retained import checks; this staged board has no placement qualification."""
import hashlib
import json
from pathlib import Path
from agent_ee.forward_annotation import _verify, _canonical
from agent_ee.native_netlist import read_native_inventory
from agent_ee.probe_features import PROPERTY, parse_marker, marker, validate_board

P=Path(__file__).resolve().parent
B=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((P/'plan.json').read_text()); result=json.loads((P/'apply.json').read_text())
assert plan['execution']==result['execution']=='ok' and not plan['findings'] and not result['findings']
assert sha(B/'board-preflight/import-experiment/scaffold.kicad_pcb')==plan['inputs']['board_sha256']
assert sha(B/'revised-native/native.xml')==plan['inputs']['xml_sha256']
assert hashlib.sha256(_canonical(json.loads((B/'board-preflight/footprints.json').read_text()))).hexdigest()==plan['inputs']['manifest_sha256']
for item in plan['inputs']['footprints']:
    assert sha(B/'series-divider/native-candidate/inputs'/item['path'])==item['sha256']
assert sha(P/'staged-board.kicad_pcb')==result['output']['sha256']
assert result['probe_migrations']==plan['probe_migrations'] and len(result['probe_migrations'])==6
before=json.loads((P/'input-board-facts.json').read_text());after=json.loads((P/'saved-board-facts.json').read_text())
_verify(plan,before,after)
graph=read_native_inventory(B/'revised-native/native.xml')
probes={ref:parse_marker(c['properties'][PROPERTY]) for ref,c in graph['components'].items() if PROPERTY in c['properties']}
assert set(probes)=={'TP'+str(i) for i in range(1,7)}
validate_board((P/'staged-board.kicad_pcb').read_bytes(),probes)
for migration in plan['probe_migrations']:
    ref=migration['reference'];assert migration['source']=='netlist'
    assert migration['previous']==graph['components'][ref]['properties'][PROPERTY]
    assert parse_marker(migration['previous'])==parse_marker(migration['canonical'])==probes[ref]
    assert migration['canonical']==marker(probes[ref])
assert len(after['footprints'])==331 and not after['tracks'] and not after['zones']
for name,digest in json.loads((P/'provenance.json').read_text())['files'].items():
    assert sha(P/name)==digest,name
print('PASS: source hashes, 327 additions plus four holes, saved-board correspondence, six identity-preserving probe migrations; zero tracks/zones')
