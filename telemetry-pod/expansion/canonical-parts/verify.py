"""Replay retained records and exact current-instance coverage without network."""
import hashlib
import json
from pathlib import Path
from agent_ee.part_record import qualify_record

packet=Path(__file__).resolve().parent
root=packet.parents[2]
provenance=json.loads((packet/'provenance.json').read_text())
for name,digest in provenance['files'].items():
    assert hashlib.sha256((packet/name).read_bytes()).hexdigest()==digest, name
index=json.loads((packet/'records/index.json').read_text())
source=json.loads((packet.parent/'series-divider/native-candidate/inputs/intent.json').read_text())
components={c['reference']:c for c in source['components'] if 'LCSC' in c.get('part_binding',{})}
seen=set()
for row in index['records']:
    path=packet/'records'/row['file'];raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
    record=json.loads(raw)
    assert qualify_record(record,root)==row['dependencies']
    for ref in row['references']:
        assert ref not in seen;seen.add(ref)
        binding=components[ref]['part_binding'];datasheet=json.loads(binding['PARAM_Datasheet'])
        assert (record['lcsc'],record['mpn'],record['manufacturer'])==(
            binding['LCSC'],binding['Partnumber'],binding['Manufacturer'])
        assert record['artifact']['sha256']==datasheet['sha256']
        assert record['datasheet_url']==datasheet['url']==binding['Datasheet']
assert len(seen)==index['summary']['record_instances']
for row in index['gaps']:
    for ref in row['references']:
        assert ref not in seen;seen.add(ref)
        binding=components[ref]['part_binding'];datasheet=json.loads(binding['PARAM_Datasheet'])
        assert (binding['LCSC'],binding['Partnumber'],datasheet['sha256'],datasheet['url'])==(
            row['lcsc'],row['mpn'],row['bound_sha256'],row['url'])
assert seen==set(components)
assert len(index['records'])==82 and len(index['gaps'])==4 and len(components)==316
print('PASS:82 records/299 instances replay exactly;4 explicit gaps/17 instances; full316-instance partition')
