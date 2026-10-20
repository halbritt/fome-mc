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
values={'U30':'TPS26625DRCR','R162':'1.05 Mohm 0.1% 25ppm/K','R163':'95.3 kohm 0.1% 25ppm/K','R164':'287 kohm 0.1% 25ppm/K','R165':'44.2 kohm 0.1% 25ppm/K','C124':'1uF 50V X7R','C125':'100nF 50V X7R','C126':'10nF 50V C0G 10%','R166':'499 kohm 0.1% 25ppm/C','R167':'499 kohm 0.1% 25ppm/C','R168':'499 kohm 0.1% 25ppm/C','R169':'4.99 kohm 0.1% 25ppm/C','C127':'100nF 50V X7R'}
def add(net,ref,pin):expected.setdefault(net,set()).add(('aux-power/'+ref,str(pin)))
source='POD_5V_SENSOR';outnet='POD_5V_AUX';uv='SENSOR_POWER_AUX_UVLO';ov='SENSOR_POWER_AUX_OVP';rtn='SENSOR_POWER_AUX_RTN';ilim='SENSOR_POWER_AUX_ILIM';ramp='SENSOR_POWER_AUX_DVDT';diag='DIAG_U28_AIN2'
for pin,net in [(1,source),(2,uv),(3,ov),(5,rtn),(6,'GND'),(7,ilim),(8,ramp),(10,outnet),(11,rtn)]:add(net,'U30',pin)
for pin in [4,9]:enc.add(('aux-power/U30',str(pin)))
for ref,left,right in [('R162',source,uv),('R163',uv,ov),('R164',ov,rtn),('R165',ilim,rtn),('C124',source,'GND'),('C125',outnet,'GND'),('C126',ramp,rtn),('R166',outnet,diag+'_UPPER1'),('R167',diag+'_UPPER1',diag+'_UPPER2'),('R168',diag+'_UPPER2',diag),('R169',diag,'GND'),('C127',diag,'GND')]:add(left,ref,1);add(right,ref,2)
for component,pin,net in [('connector/J1','21',outnet),('connector/J1','22','GND'),('diagnostic/U28','7',diag)]:
 key=(component,pin);check('assigned pin was NC '+str(key),key in enc);enc.discard(key);expected[net].add(key)
check('13 exact additions',len(values)==13 and set(nc)-set(oc)=={'aux-power/'+ref for ref in values})
for ref,value in values.items():
 c=nc.get('aux-power/'+ref,{});check('value '+ref,c.get('value')==value)
 fp='Resistor_SMD:R_0603_1608Metric' if ref.startswith('R') else 'Capacitor_SMD:C_'+('0805_2012Metric' if ref=='C124' else '0603_1608Metric') if ref.startswith('C') else 'Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm'
 check('footprint '+ref,c.get('footprint')==fp)
 check('symbol binding '+ref,c.get('lib_id')==('Device:R' if ref.startswith('R') else 'Device:C' if ref.startswith('C') else 'PodSensorPower:TPS26625_DRC'))
 check('no donor binding '+ref,not any('donor' in k.lower() for k in c))
check('unchanged library manifest',old['libraries']==new['libraries'])
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
want={'1':'A0','2':'A1','3':'RESET_N','4':'DGND','5':'AGND','6':'AIN3','7':'AIN2','8':'REFN','9':'REFP','10':'AIN1','11':'AIN0','12':'AVDD','13':'DVDD','14':'DRDY_N','15':'SDA','16':'SCL'}
check('TSSOP physical pin functions',pins(libs.get('PodDiagnostic',{}).get('ADS1119_PW',[]))==want)
check('TPS26625 physical pin functions',pins(libs.get('PodSensorPower',{}).get('TPS26625_DRC',[]))=={'1':'IN','2':'UVLO','3':'OVP','4':'SHDN','5':'RTN','6':'GND','7':'ILIM','8':'dVdT','9':'FLT','10':'OUT','11':'EP_RTN'})
result={'status':'FAIL' if fail else 'PASS','check_count':len(checks),'failures':fail,'parse_errors':parse_errors,'inputs':{'old_intent_sha256':sha(op),'new_intent_sha256':sha(np),'authored_cad_sha256':hashes,'parser_sha256':sha(Path(parser.__file__)),'checker_sha256':sha(Path(__file__))},'scope':'Prepared graph and complete authored library syntax only; no native KiCad/ERC or hardware approval','checks':checks,'holds':['Ninth diagnostic rail is now connected in prepared source only; auxiliary precision load remains unqualified','Powered-off leakage/backfeed, upstream transient envelope and full error bounds unqualified','I2C timing and analog settling require measured validation','All prior Hall negative transient, thermal and native acceptance holds remain']};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','check_count','failures']}));sys.exit(bool(fail))
