"""AGENTEE-487: execute the DECLARED add-planes step (prepared plan.json, stage 'routing') through agent-ee's own
stage_receipts.run_step/adopt, exactly as a campaign routing turn does, on disposable copies of the candidate tree
with a given board. Runs inside the d96f8e00 image (pipeline.py's runtime). Reports zones before/after.
Usage (in image): planes_phase_proof.py <pipe dir> <work dir> <out.json> <plan.json> LABEL=BOARD ...
The plan replaces composition/planes.json in each disposable tree (before/after regression)."""
import hashlib, json, shutil, sys
from pathlib import Path
sys.path.insert(0, '/work/export/src')
from agent_ee import stage_receipts
import pcbnew
pipe, work, out, plan = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
spec = next(s for s in json.loads((pipe / 'prepared/plan.json').read_text())['implementation_steps'] if s['step'] == 'add-planes')
import os
if os.environ.get('MOUNT_OVERRIDE'):  # AGENTEE-487: run the declared step with a candidate producer source
    spec['mounts'] = [dict(m, source=os.environ['MOUNT_OVERRIDE']) if m['at'] == '/tool/agent-ee' else m for m in spec['mounts']]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def zones(path):
    b = pcbnew.LoadBoard(str(path))
    return [{'rule_area': z.GetIsRuleArea(), 'net': z.GetNetname(), 'layers': [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
             'name': z.GetZoneName()} for z in b.Zones()]
res = {'spec_stage': spec['stage'], 'spec_step': spec['step'], 'plan_sha256': sha(plan), 'plan': json.loads(plan.read_text())}
for arg in sys.argv[5:]:
    label, board = arg.split('=', 1)
    design = work / label / 'design'
    shutil.copytree(pipe / 'emission/design', design, symlinks=False)
    shutil.copyfile(board, design / 'project/telemetry-pod.kicad_pcb')
    shutil.copyfile(plan, design / 'composition/planes.json')
    before = zones(design / 'project/telemetry-pod.kicad_pcb')
    rdir = work / label / 'receipt'
    receipt = stage_receipts.run_step(rdir, design, spec, {'proof': 'AGENTEE-487', 'board': label})
    exit_code = (receipt.get('execution') or {}).get('exit_code', receipt.get('status'))
    adopted = None
    try:
        stage_receipts.adopt(rdir, receipt, design); adopted = True
    except Exception as exc:  # recorded, not hidden
        adopted = f'{type(exc).__name__}: {exc}'
    after_path = design / 'project/telemetry-pod.kicad_pcb'
    res[label] = {'input_board_sha256': sha(board), 'zones_before': before, 'exit': exit_code, 'adopted': adopted, 'producer_mount': spec['mounts'][0]['source'], 'report': json.loads((rdir / 'run/out/planes.json').read_text()) if (rdir / 'run/out/planes.json').exists() else None,
                  'output_board_sha256': sha(after_path), 'zones_after': zones(after_path),
                  'receipt_sha256': sha(rdir / 'receipt.json')}
out.write_text(json.dumps(res, indent=1) + '\n')
for k, v in res.items():
    if isinstance(v, dict) and 'zones_after' in v:
        print(k, 'exit', v['exit'], 'adopted', v['adopted'], 'copper after', [(z['net'], z['layers']) for z in v['zones_after'] if not z['rule_area']])
