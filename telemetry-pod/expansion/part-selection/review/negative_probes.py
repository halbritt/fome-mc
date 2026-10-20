"""CLI PART_SELECTION_DIR REPORT; mutate disposable copies only."""
import json,hashlib,shutil,subprocess,sys,tempfile,os
from pathlib import Path
source,out=map(Path,sys.argv[1:]);results=[]
for name in ['swapped_selections','stale_intent','assembly_flag_changed']:
 with tempfile.TemporaryDirectory(prefix='pod-selection-negative-') as temp:
  root=Path(temp)/'part-selection';shutil.copytree(source,root);intent=Path(temp)/'thermistor/inputs/intent.json';intent.parent.mkdir(parents=True);shutil.copyfile(source/'../thermistor/inputs/intent.json',intent)
  if name=='swapped_selections':
   p=root/'selections.json';d=json.loads(p.read_text());d['parts'][0]['components'],d['parts'][1]['components']=d['parts'][1]['components'],d['parts'][0]['components'];p.write_text(json.dumps(d))
  elif name=='stale_intent':
   d=json.loads(intent.read_text());next(c for c in d['components'] if c['id']=='diagnostic/R128')['value']='498 kohm 0.1% 25ppm/C';intent.write_text(json.dumps(d))
  else:
   rp=root/'stock/responses/C515607.json';r=json.loads(rp.read_text());r['data']['componentPageInfo']['list'][0]['assemblyComponentFlag']=True;rp.write_text(json.dumps(r));cp=root/'stock/catalog.json';c=json.loads(cp.read_text());req=next(x for x in c['requests'] if x['lcsc']=='C515607');req['response']['sha256']=hashlib.sha256(rp.read_bytes()).hexdigest();req['response']['size_bytes']=rp.stat().st_size;cp.write_text(json.dumps(c))
  report=Path(temp)/'independent.json';env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
  independent=subprocess.run([sys.executable,str(root/'review/check_selection.py'),str(root),str(report)],capture_output=True,text=True,env=env);data=json.loads(report.read_text());assert independent.returncode and data['status']=='FAIL'
  producer=subprocess.run([sys.executable,str(root/'verify.py')],capture_output=True,text=True,env=env);assert producer.returncode
  results.append({'probe':name,'independent_exit':independent.returncode,'independent_failures':data['failures'],'producer_exit':producer.returncode,'producer_error_tail':producer.stderr.splitlines()[-3:],'hash_updated':name=='assembly_flag_changed'})
out.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps([{'probe':r['probe'],'independent_exit':r['independent_exit'],'producer_exit':r['producer_exit']} for r in results]))
