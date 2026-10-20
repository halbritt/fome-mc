#!/usr/bin/env python3
"""Usage: OLD_INPUTS NEW_INPUTS REPORT. Needs agent_ee on PYTHONPATH.
Independent intent delta and whole authored-library syntax; no native acceptance.
"""
import copy,hashlib,json,sys
from pathlib import Path
from agent_ee.symbol_library import parse_library,LibraryError
import agent_ee.symbol_library as parser
old_dir,new_dir,out=map(Path,sys.argv[1:]);op=old_dir/'intent.json';np=new_dir/'intent.json';old=json.loads(op.read_text());new=json.loads(np.read_text());checks=[];fail=[];hashes={};parse_errors={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(label,ok):
 checks.append(label)
 if not ok:fail.append(label)
def terminal(t):return t['component'],str(t['pin']['number'])
def graph(d,prefix):
 nets={};seen=set()
 for n in d['nets']:
  ts=[terminal(t) for t in n['terminals']];check(prefix+' unique net '+n['name'],n['name'] not in nets);check(prefix+' unique terminals '+n['name'],len(ts)==len(set(ts)) and not(seen&set(ts)));seen.update(ts);nets[n['name']]=set(ts)
 nc=[terminal(t) for t in d['no_connects']];check(prefix+' NC uniqueness/isolation',len(nc)==len(set(nc)) and not(set(nc)&seen));return nets,set(nc)
a,anc=graph(old,'old');b,bnc=graph(new,'new');expected=copy.deepcopy(a);enc=set(anc)
oc={c['id']:c for c in old['components']};nc={c['id']:c for c in new['components']}
check('unique IDs',len(nc)==len(new['components']));check('unique refs',len({c['reference'] for c in new['components']})==len(nc))
for k,c in oc.items():check('preserved old component '+k,nc.get(k)==c)
values={'U26':'LM2903BQDRQ1','D102':'BAV199,215','D103':'BAV199,215','D104':'PESD2CANFD24V-TR','C95':'220pF C0G','C96':'220pF C0G','C97':'100nF 50V X7R','C98':'1uF 50V X7R'}
def add(net,ref,pin):expected.setdefault(net,set()).add(('wheel-input/'+ref,str(pin)))
for ix,(side,jpin,mpin,minus,plus,output) in enumerate([('FRONT','24','39',2,3,1),('REAR','27','38',6,5,7)]):
 prefix='WHEEL_'+side+'_';supply='POD_WHEEL_'+side+'_SUPPLY';signal='POD_WHEEL_'+side+'_SIGNAL';d=f'D{102+ix}';c=f'C{95+ix}';rr=[f'R{110+9*ix+k}' for k in range(9)]
 v=['620 ohm','620 ohm','10 kohm 0.1%','10 kohm 0.1%','56 kohm 0.1%','10 kohm 0.1%','100 kohm 0.1%','4.7 kohm 1%','100 ohm'];values.update(zip(rr,v))
 for ref,left,right in [(rr[0],supply,prefix+'PULLUP_MID'),(rr[1],prefix+'PULLUP_MID',prefix+'PULLUP'),(rr[2],prefix+'DIODE_OUT',prefix+'FILTERED'),(rr[3],prefix+'FILTERED','GND'),(rr[4],'+3V3',prefix+'THRESHOLD'),(rr[5],prefix+'THRESHOLD','GND'),(rr[6],prefix+'OUT',prefix+'THRESHOLD'),(rr[7],'+3V3',prefix+'OUT'),(rr[8],prefix+'OUT',prefix+'CAPTURE'),(c,prefix+'FILTERED','GND')]:add(left,ref,1);add(right,ref,2)
 for pin,net in [(1,prefix+'PULLUP'),(2,prefix+'DIODE_OUT'),(3,signal)]:add(net,d,pin)
 for pin,net in [(minus,prefix+'FILTERED'),(plus,prefix+'THRESHOLD'),(output,prefix+'OUT')]:add(net,'U26',pin)
 add(signal,'D104',ix+1)
 for key,net in [(('connector/J1',jpin),signal),(('mcu',mpin),prefix+'CAPTURE')]:check('reassigned was NC '+str(key),key in enc);enc.discard(key);expected[net].add(key)
add('PRE_6V3','U26',8);add('GND','U26',4);add('GND','D104',3)
for c in ['C97','C98']:add('PRE_6V3',c,1);add('GND',c,2)
check('26 exact additions',set(nc)-set(oc)=={'wheel-input/'+ref for ref in values} and len(values)==26)
for ref,value in values.items():
 c=nc.get('wheel-input/'+ref,{});check('value '+ref,c.get('value')==value)
 if ref.startswith('R'):fp='Resistor_SMD:R_'+('2512_6332Metric' if ref in ['R110','R111','R119','R120'] else '0603_1608Metric')
 elif ref.startswith('C'):fp='Capacitor_SMD:C_'+('0805_2012Metric' if ref=='C98' else '0603_1608Metric')
 elif ref=='U26':fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
 else:fp='Package_TO_SOT_SMD:SOT-23'
 check('footprint '+ref,c.get('footprint')==fp)
for ref,lib in [('U26','PodWheel:LM2903BQ_D'),('D102','PodWheel:BAV199'),('D103','PodWheel:BAV199'),('D104','PodCAN:PESD2CANFD24V_T')]:check('symbol binding '+ref,nc.get('wheel-input/'+ref,{}).get('lib_id')==lib)
check('exact net set',set(b)==set(expected))
for net,ts in expected.items():check('exact membership '+net,b.get(net)==ts)
check('exact NC set',bnc==enc)
libs={}
for p in sorted((new_dir/'authored-cad').glob('*.kicad_sym')):
 hashes[str(p.relative_to(new_dir))]=sha(p)
 try:libs[p.stem]=parse_library(p.read_bytes());check('complete library parses '+p.name,True)
 except LibraryError as exc:parse_errors[p.name]=str(exc);check('complete library parses '+p.name,False)
for l in new['libraries']:
 p=new_dir/l['path'];check('declared library hash '+l['name'],p.exists() and sha(p)==l['sha256'])
for p in (old_dir/'authored-cad').glob('*.kicad_sym'):check('preserved prior CAD '+p.name,(new_dir/'authored-cad'/p.name).exists() and sha(p)==sha(new_dir/'authored-cad'/p.name))
def walk(n):
 if isinstance(n,list):
  yield n
  for c in n:yield from walk(c)
def pins(symbol):
 result={}
 for node in walk(symbol):
  if node and node[0]=='pin':
   names=[x[1] for x in node if isinstance(x,list) and len(x)>1 and x[0]=='name'];nums=[x[1] for x in node if isinstance(x,list) and len(x)>1 and x[0]=='number'];check('structured pin',len(names)==len(nums)==1)
   if len(names)==len(nums)==1:check('unique physical pin '+nums[0],nums[0] not in result);result[nums[0]]=names[0]
 return result
for lib,name,want in [('PodWheel','LM2903BQ_D',{'1':'OUT1','2':'IN1-','3':'IN1+','4':'GND','5':'IN2+','6':'IN2-','7':'OUT2','8':'VCC'}),('PodWheel','BAV199',{'1':'A1','2':'K2','3':'K1_A2'}),('PodCAN','PESD2CANFD24V_T',{'1':'K1','2':'K2','3':'CC'})]:check('physical functions '+name,pins(libs.get(lib,{}).get(name,[]))==want)
result={'status':'FAIL' if fail else 'PASS','check_count':len(checks),'failures':fail,'parse_errors':parse_errors,'inputs':{'old_intent_sha256':sha(op),'new_intent_sha256':sha(np),'authored_cad_sha256':hashes,'parser_sha256':sha(Path(parser.__file__)),'checker_sha256':sha(Path(__file__))},'scope':'Prepared graph and complete authored library syntax only; no native KiCad/ERC or hardware approval','checks':checks,'holds':['BAV199 negative recovery/transients may violate LM2903 input -0.3V limit','Hall VOL/min pulse widths and temperature endpoints missing','Exact component binding, hot thermal coupling and assembled footprints unqualified']};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','check_count','failures']}));sys.exit(bool(fail))
