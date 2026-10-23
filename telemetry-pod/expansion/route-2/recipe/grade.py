import json,pathlib,subprocess,time,shutil,hashlib
b=pathlib.Path('/home/halbritt/.cache/route-2-agent507');run=b/'run';origin='/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z';out=pathlib.Path('/home/halbritt/.cache/agent-worktrees/fome-mc/route-2-repair/telemetry-pod/expansion/route-2')
assert (b/'exit.json').exists(),'routing must finish first'
r=json.loads((run/'result.json').read_text());print('initial statuses',r['process']['status'],r['routing']['status'],r['validation']['status'],flush=True)
if not (run/'candidate/project/telemetry-pod.kicad_pcb').exists():
 raw=run/'work/krt-out/telemetry-pod.kicad_pcb'
 assert raw.exists(),'no saved board available to inspect'
 shutil.copytree(run/'reference/project',run/'candidate/project',dirs_exist_ok=True)
 shutil.copy2(raw,run/'candidate/project/telemetry-pod.kicad_pcb')
 (b/'checkpoint-only.json').write_text(json.dumps({'status':'REJECTED_CHECKPOINT','reason':'backend did not complete; staged its last saved intermediate only for explicit native inspection; original process FAIL remains authoritative','sha256':hashlib.sha256(raw.read_bytes()).hexdigest()},indent=2))
# If a backend failure bypassed automatic grading, explicitly grade that saved checkpoint.
if not (run/'validate/candidate-facts.json').exists():
 with (b/'against-route1.json').open('w') as f,(b/'against-route1.log').open('w') as err:
  subprocess.run(['native-admit','run','--class','suite','--weight','4','--label','route-2','--max-wait','60','--','kicad-route','--out',str(b/'out'),'--json','validate',str(run)],stdout=f,stderr=err)
 vdir=max((run/'revalidate').iterdir(),key=lambda p:p.name)
else:vdir=run/'validate'
(b/'grade-dirs.json').write_text(json.dumps({'against_route1':str(vdir)}))
cmd=['native-admit','run','--class','suite','--weight','4','--label','route-2','--max-wait','60','--','kicad-route','--out',str(b/'out'),'--json','validate',str(run),'--against',origin]
with (b/'against-r5.json').open('w') as f,(b/'against-r5.log').open('w') as err:p=subprocess.run(cmd,stdout=f,stderr=err)
print('against-r5 exit',p.returncode,flush=True)
a=json.loads((b/'against-r5.json').read_text());(out/'kicad-route').mkdir(exist_ok=True)
for f in ['result.json','attempt.json','snapshot.json']:shutil.copy2(run/f,out/'kicad-route'/f)
shutil.copytree(vdir,out/'kicad-route'/'against-route-1',dirs_exist_ok=True)
# --json output carries its source-bound directory; find the exact newly created validation directory.
grade=max((run/'revalidate-origin').iterdir(),key=lambda p:p.name);shutil.copytree(grade,out/'kicad-route'/'against-r5',dirs_exist_ok=True)
shutil.copy2(b/'against-r5.json',out/'kicad-route'/'against-r5-result.json')
for f in ['command.txt','times.json','exit.json','stdout.json','stderr.log','against-r5.log','against-route1.json','against-route1.log','checkpoint-only.json']:
 if (b/f).exists():shutil.copy2(b/f,out/'logs'/f)
shutil.copy2(run/'work/krt.log',out/'logs'/'router.log')
if (run/'work/krt-out/summary.json').exists():shutil.copy2(run/'work/krt-out/summary.json',out/'kicad-route'/'router-summary.json')
(out/'candidate').mkdir(exist_ok=True)
for f in (run/'candidate/project').iterdir():
 if f.is_file() and f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_dru','.kicad_sch']:shutil.copy2(f,out/'candidate'/f.name)
print('copied evidence',out,flush=True)
