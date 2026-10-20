import json,shutil,tempfile,subprocess,os
from pathlib import Path
root=Path('/home/halbritt/.cache/agent-worktrees/fome-mc/pod-aux-power/telemetry-pod/expansion/interface-preparation');review=Path(__file__).parent;results=[]
for name,component,pin,destination in [('wrong_source','aux-power/U30','1','PRE_6V3'),('grounded_RTN','aux-power/U30','11','GND'),('wrong_ninth_pin','diagnostic/U28','7','GND')]:
 with tempfile.TemporaryDirectory(dir=review) as td:
  p=Path(td)/'inputs';shutil.copytree(root/'aux-power/inputs',p);f=p/'intent.json';d=json.loads(f.read_text());t=None
  for n in d['nets']:
   for x in list(n['terminals']):
    if x['component']==component and str(x['pin']['number'])==pin:n['terminals'].remove(x);t=x
  assert t is not None
  next(n for n in d['nets'] if n['name']==destination)['terminals'].append(t);f.write_text(json.dumps(d));report=Path(td)/'report.json'
  run=subprocess.run(['python3',str(review/'check_prepared_aux.py'),str(root/'diagnostic-circuit/inputs'),str(p),str(report)],capture_output=True,text=True,env={**os.environ,'PYTHONPATH':'/home/halbritt/git/agent-ee/src'});data=json.loads(report.read_text());assert run.returncode!=0 and data['status']=='FAIL';results.append({'probe':name,'exit_code':run.returncode,'failures':data['failures']})
(review/'negative-probes.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
