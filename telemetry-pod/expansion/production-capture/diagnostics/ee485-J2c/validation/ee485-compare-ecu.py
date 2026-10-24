import hashlib
import json
from pathlib import Path
p=Path('telemetry-pod/expansion/production-capture/diagnostics/ee485-J2b/ecu-make-check-summary.json')
before=json.loads(p.read_text())
s=Path('build/runs/project/fome-mc/20261024T014154.621454Z')
summary=json.loads((s/'summary.json').read_text())
after={'project':summary['project'],'status':summary['status'],'steps':{
    name:{'status':r['status'],'design_clean':r.get('design_clean'),
          'violations':r['findings'].get('violations'),'unconnected_items':r['findings'].get('unconnected_items')}
    for name,r in summary['steps'].items()}}
if before != after:
    raise ValueError('existing ECU gate results changed')
snapshot=json.loads((s/'snapshot.json').read_text())
checked={}
for rel,expected in snapshot['files'].items():
    path=Path(rel)
    if not path.is_file():
        continue
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError('ECU snapshot source changed: '+rel)
    checked[rel]=actual
result={'status':'PASS','baseline':str(p),'baseline_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'before':before,'after':after,'unchanged_snapshot_source_files':checked,
        'snapshot_source_git_head':snapshot['source_git_head']}
Path('build/ee485-ecu-before-after.json').write_text(json.dumps(result,indent=1)+'\n')
print('ECU before/after gate results identical;',len(checked),'snapshot source files byte unchanged')
