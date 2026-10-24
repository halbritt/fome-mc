"""Retain this single diagnostic's existing bytes; do not accept a receipt or regenerate a design."""
from collections import Counter
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
root=Path.cwd()
run=root/'build/ee485-J2c-run'
out=root/'telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c'
out.mkdir(parents=True,exist_ok=False)
def copy(src,rel):
    dst=out/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst)
shutil.copytree(run/'cap',out/'cap')
shutil.copytree(run/'pipe/emission/design',out/'pipe/emission/design')
copy(run/'pipe/emission/native.xml','pipe/emission/native.xml')
copy(run/'pipe/pipeline.json','pipeline.json')
for src in sorted((run/'pipe/emission/receipts').glob('*/receipt.json')):
    copy(src,'receipt-metadata/'+src.parent.name+'/receipt.json')
if (run/'pipe/access-rebound').exists():
    shutil.copytree(run/'pipe/access-rebound',out/'pipe/access-rebound')
shutil.copytree(run/'j2-verification',out/'j2-verification')
copy(run/'native-positions.csv','native-positions.csv')
check=Path((run/'native-check-path.txt').read_text().strip().replace('/work/fome-mc',str(root)))
for name in ['summary.json','source.json','positions-command.json','erc/erc.json','erc/result.json','erc/kicad-cli-erc.log','drc/drc.json','drc/result.json','drc/kicad-cli-drc.log']:
    copy(check/name,'native/'+name)
logs=['ee485-initial-gates.log','ee485-controls.log','ee485-controls-final.log','ee485-controls-corrected.log',
      'ee485-producer.log','ee485-producer-f8.log','ee485-composed-final.log','ee485-emission.log',
      'ee485-candidate-checks.log','ee485-verify-inventory.log','ee485-final-source-reproduce.log']
for name in logs:
    copy(root/'build'/name,'logs/'+name)
for name in ['ee485.mk','ee485-native.py','ee485-compare-ecu.py','ee485-producer.py','ee485-producer.sh',
             'ee485-producer-final-check.sh','ee485-f8-record.py','ee485-post-guard-note.txt']:
    copy(root/'build'/name,'validation/'+name)
copy(root/'build/ee485-ecu-before-after.json','ecu-before-after.json')
copy(root/'build/runs/project/fome-mc/20261024T014154.621454Z/summary.json','ecu-make-check-summary.json')
pipeline=json.loads((out/'pipeline.json').read_text())
stages={name:{'status':record['status'],**({'error':record['error']} if 'error' in record else {})}
        for name,record in pipeline['stages'].items()}
(out/'stage-status.json').write_text(json.dumps({'counts':dict(Counter(r['status'] for r in stages.values())),
                                              'stages':stages},indent=1)+'\n')
(out/'STAGES.md').write_text('Actual pipeline.json.stages; pipeline exit 3. No summary key is used.\n\n| Stage | Status |\n|---|---|\n'+
                           ''.join(f'| `{name}` | {r["status"]} |\n' for name,r in stages.items()))
def git(rev):
    return subprocess.run(['git','rev-parse',rev],check=True,capture_output=True,text=True).stdout.strip()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
source={'schema':'agentee485.j2c-diagnostic/1','verdict':'PARTIAL; no candidate or receipt acceptance',
        'assigned_base':git('037fe6c274d25967cc214e22d27e939b9d628446'),
        'worker_start_marker':git('ec6ae4735a7fd479eb60af44369289e99d2eef02'),
        'j2b_input':git('5a1cb6f531141f22937d3b1da0b200b0af2ba247'),
        'merge_commit':git('e1b91c5feb828da4ac88ba6f2bf5585a5a7d2fb2'),
        'emission_source':git((root/'build/ee485-emission-source-head.txt').read_text().strip()),
        'agent_ee':pipeline['agent_ee'],
        'runtime_manifest':'telemetry-pod/expansion/production-capture/runtime/agentee-485j2c.json',
        'runtime_manifest_sha256':sha(root/'telemetry-pod/expansion/production-capture/runtime/agentee-485j2c.json'),
        'limits':{'class':'test','weight':1,'cpus':3,'memory':'12g','timeout_s':1800,'jobs':1},
        'c1':'validation-only-c1-not-in-scope','pipeline_exit':3,'emission_invocations':1,
        'start':(root/'build/ee485-emission-start.txt').read_text().strip(),
        'stop':(root/'build/ee485-emission-stop.txt').read_text().strip(),
        'board_sha256':sha(run/'pipe/emission/design/project/telemetry-pod.kicad_pcb'),
        'late_source_boundary':(root/'build/ee485-post-guard-note.txt').read_text(),
        'receipt_metadata_scope':'Only receipt.json metadata retained here; no receipt acceptance or production retention.',
        'worker_model':'Sol (Codex), HIGH as dispatched; exact runtime model identifier is not exposed by the harness; no subagents'}
(out/'source.json').write_text(json.dumps(source,indent=1)+'\n')
print('Retained diagnostic bytes at',out)
