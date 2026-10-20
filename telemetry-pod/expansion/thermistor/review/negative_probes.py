import json,shutil,tempfile,subprocess,os,sys,hashlib
from pathlib import Path
old,new,out=map(Path,sys.argv[1:]);checker=Path(__file__).with_name('check_prepared_thermistor.py');results=[]
for name in ['reversed_diode','REF_grounded','upstream_pullup','malformed_library']:
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'inputs';shutil.copytree(new,p);f=p/'intent.json';d=json.loads(f.read_text())
  def move(ref,pin,net):
   found=[]
   for n in d['nets']:
    for t in list(n['terminals']):
     if t['component']==ref and str(t['pin']['number'])==pin:n['terminals'].remove(t);found.append(t)
   assert len(found)==1;next(n for n in d['nets'] if n['name']==net)['terminals'].append(found[0])
  if name=='reversed_diode':move('thermistor/D105','1','THERM_BIAS_IN');move('thermistor/D105','3','POD_5V_AUX')
  elif name=='REF_grounded':move('thermistor/U31','2','GND')
  elif name=='upstream_pullup':move('thermistor/R170','1','POD_5V_SENSOR')
  else:
   sym=p/'authored-cad/PodThermistor.kicad_sym';sym.write_text(sym.read_text().rstrip()[:-1]);next(l for l in d['libraries'] if l['name']=='PodThermistor')['sha256']=hashlib.sha256(sym.read_bytes()).hexdigest()
  f.write_text(json.dumps(d));report=Path(tmp)/'report.json';run=subprocess.run([sys.executable,str(checker),str(old),str(p),str(report)],capture_output=True,text=True);r=json.loads(report.read_text());assert run.returncode and r['status']=='FAIL';results.append({'probe':name,'exit_code':run.returncode,'failures':r['failures']})
out.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
