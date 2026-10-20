"""PACKET BASE_INPUTS CANDIDATE REPORT: temporary-copy negative controls."""
import json,subprocess,sys,tempfile,shutil
from pathlib import Path
root,base,source,report=map(Path,sys.argv[1:]);results=[]
for name,reason in [('midpoint_attachment','terminal repeated'),('bypassed_series','midpoint exact'),('wrong_resistance','exact component'),('prior_binding_damage','collapse pair'),('layout_wrong_group','R181 layout')]:
 with tempfile.TemporaryDirectory(prefix='series-negative-') as td:
  candidate=Path(td)/'candidate';shutil.copytree(source,candidate)
  p=candidate/'inputs'/('emitter-layout.json' if name=='layout_wrong_group' else 'intent.json');d=json.loads(p.read_text())
  if name=='layout_wrong_group':
   g=next(g for g in d['groups'] if 'supervisor/R181' in g['components']);g['components'].remove('supervisor/R181');g['components'].append('supervisor/R181')
  else:
   components={c['reference']:c for c in d['components']};bridge=next(n for n in d['nets'] if n['name']=='SUP_U18_TOP_SERIES')
   if name=='midpoint_attachment':bridge['terminals'].append({'component':'supervisor/U18','pin':{'number':'1'}})
   elif name=='bypassed_series':bridge['terminals'][1]['pin']['number']='3'
   elif name=='wrong_resistance':components['R60']['value']='31.6 kohm 0.1% 25ppm/K'
   else:components['U20']['part_binding']['LCSC']='C_FAKE'
  p.write_text(json.dumps(d,indent=2)+'\n')
  result=subprocess.run([sys.executable,str(root/'review/check_series.py'),str(root),str(base),str(candidate),str(Path(td)/'result.json'),'--source-only'],capture_output=True,text=True)
  if result.returncode==0 or reason not in result.stderr:raise ValueError('Wrong negative outcome '+name+': '+result.stderr)
  results.append({'probe':name,'status':'REJECTED','evidence':result.stderr.splitlines()[-1]})
report.write_text(json.dumps(results,indent=2)+'\n');print('PASS: five negative controls rejected')
