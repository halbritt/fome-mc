"""Run package-change negatives against temporary copies: PACKET CANDIDATE REPORT."""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
root,source,report=map(Path,sys.argv[1:]);results=[]
for name,reason in [('old0603_package','only allowed package R73'),('changed_nominal','only allowed package C64'),('prior_binding_damage','complete source equality'),('existing_net_damage','complete source equality'),('changed_pad','footprint target bytes')]:
 with tempfile.TemporaryDirectory(prefix='component-fit-negative-') as td:
  target=Path(td)/'candidate';shutil.copytree(source,target)
  if name=='changed_pad':
   p=target/'inputs/footprints/Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod';p.write_text(p.read_text().replace('(at -0.9125 0)','(at -0.8125 0)'))
   # Full capture hash preservation rejects before geometric parsing.
  else:
   p=target/'inputs/intent.json';d=json.loads(p.read_text());byref={c['reference']:c for c in d['components']}
   if name=='old0603_package':byref['R73']['footprint']='Resistor_SMD:R_0603_1608Metric'
   elif name=='changed_nominal':byref['C64']['value']='10 uF/16 V X7R'
   elif name=='prior_binding_damage':byref['U20']['part_binding']['Partnumber']='OTHER'
   else:d['nets'][0]['terminals'].pop()
   p.write_text(json.dumps(d,indent=2)+'\n')
  result=subprocess.run([sys.executable,str(root/'review/check_fit.py'),str(root),str(target),str(Path(td)/'result.json'),'--source-only'],capture_output=True,text=True)
  if result.returncode==0 or reason not in result.stderr:raise ValueError('Unexpected negative outcome '+name+': '+result.stderr)
  results.append({'probe':name,'status':'REJECTED','evidence':result.stderr.splitlines()[-1]})
report.write_text(json.dumps({'scope':'temporary copies only','results':results},indent=2)+'\n');print('PASS: five targeted negative controls rejected')
