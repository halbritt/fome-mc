import subprocess,pathlib,json,time
base=pathlib.Path('/home/halbritt/.cache/route-2-agent507'); tool='/home/halbritt/git/kicad-route/.router-generations/84b30dc286f44df6b465ae8d40aa1363';r=pathlib.Path('/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z')
for name,board in [('r5',r/'reference/project/telemetry-pod.kicad_pcb'),('route1',r/'candidate/project/telemetry-pod.kicad_pcb')]:
 for pad in ['U30.8','U18.5','U2.12']:
  cmd=[tool+'/venv/bin/python',tool+'/router/py_tools/check_reachability.py',str(board),'--pad',pad,'--layers','F.Cu,In2.Cu,B.Cu','--escalation','off','--fab-tier','standard','--strict-sizes','--json','--defect-json',str(base/f'{name}-{pad}-defect.json')]
  st=time.monotonic();p=subprocess.run(cmd,capture_output=True,text=True,timeout=70);(base/f'{name}-{pad}.json').write_text(p.stdout);(base/f'{name}-{pad}.log').write_text(p.stderr);print(name,pad,'exit',p.returncode,'seconds',round(time.monotonic()-st,2),p.stdout[:1800],flush=True)
