"""Use the repository ERC/DRC adapters on an unchanged emitted-candidate snapshot."""
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from toolchain import eda

run = Path('build/ee485-J2d-run').resolve()
design = run / 'pipe/emission/design'
board = design / 'project/telemetry-pod.kicad_pcb'
schematic = design / 'project/telemetry-pod.kicad_sch'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
identity = {str(p.relative_to(design)): sha(p) for p in (board, schematic, design/'project/telemetry-pod.kicad_pro', design/'project/telemetry-pod.kicad_dru')}
root = (Path('build/runs/project/telemetry-pod-j2d') / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')).resolve()
snapshot = root / 'snapshot'
shutil.copytree(design, snapshot)
snap = snapshot / 'project'
files, instances, problems = eda.sheet_files(snap, 'telemetry-pod.kicad_sch')
eda.ensure_kicad_config()
ctx = {'run_dir': root, 'snap': snap, 'fill': 'asis',
       'cfg': {'schematic':'telemetry-pod.kicad_sch','pcb':'telemetry-pod.kicad_pcb'},
       'manifest': {'missing_sheets':problems,'sheet_instances':instances}}
results = {name: fn(ctx) for name,fn in [('erc',eda.step_erc),('drc',eda.step_drc)]}
(root/'summary.json').write_text(json.dumps(results,indent=1)+'\n')
for name, result in results.items():
    print(name, result['status'], result.get('findings'), flush=True)
    if result['status'] != 'PASS':
        raise SystemExit(f'{name} native tool failed: {result["reasons"]}')
cmd = ['kicad-cli','pcb','export','pos','--format','csv','--units','mm','--side','both','--exclude-dnp',
       '-o',str(run/'native-positions.csv'),str(snap/'telemetry-pod.kicad_pcb')]
completed = subprocess.run(cmd,capture_output=True,text=True,timeout=600,env=eda.tool_env())
(root/'positions-command.json').write_text(json.dumps({'argv':cmd,'exit':completed.returncode,'stdout':completed.stdout,'stderr':completed.stderr},indent=1)+'\n')
print(' '.join(cmd), completed.stdout, completed.stderr, f'\nexit={completed.returncode}',sep='\n',flush=True)
if completed.returncode:
    raise SystemExit(completed.returncode)
for rel,digest in identity.items():
    if sha(design/rel) != digest or sha(snapshot/rel) != digest:
        raise ValueError('native checking changed candidate bytes: '+rel)
(root/'source.json').write_text(json.dumps({'source':str(design),'sha256':identity,'schematic_files':files,'sheet_instances':instances},indent=1)+'\n')
(run/'native-check-path.txt').write_text(str(root)+'\n')
print('Native tools PASS; design findings remain explicit. Source bytes unchanged.')
