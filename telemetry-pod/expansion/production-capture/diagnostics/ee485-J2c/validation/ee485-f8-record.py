"""Create a new F8-bound identity/record; retain the J2 historical import unchanged."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,'/work/export/src')
from agent_ee.part_record import prepare_external_record, qualify_external_record
root=Path.cwd()
old=root/'telemetry-pod/expansion/j2-historical-source'
new=root/'telemetry-pod/expansion/production-capture/sources/j2-adoption-f8'
new.mkdir(parents=True,exist_ok=True)
identity=json.loads((old/'identity.json').read_text())
manifest='telemetry-pod/expansion/agentee-494-j2/source-manifest.json'
for ref in identity['evidence_refs']:
    if ref['path']==manifest:
        ref['sha256']=hashlib.sha256((root/manifest).read_bytes()).hexdigest()
(new/'identity.json').write_text(json.dumps(identity,indent=1)+'\n')
def blob(p):
    return {'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
record=prepare_external_record(root,{**blob(new/'identity.json'),'locator':'/'},blob(old/'acquisition/manifest.json'),'J2',{**blob(old/'deviations.json'),'index':0})
qualify_external_record(record,root)
(new/'132134.json').write_text(json.dumps(record,indent=1)+'\n')
print('New external identity/record qualifies against F8; historical acquisition and declarations unchanged.')
