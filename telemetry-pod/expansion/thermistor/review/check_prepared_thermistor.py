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
values={'U31':'TL431BQDBZR','D105':'BAV199,215','C128':'10uF 16V X7R','C129':'100nF 50V X7R','R180':'100 kohm 1% 100ppm/K'}
for n in [174,175]:values[f'R{n}']='200 ohm 1% 100ppm/K 1.5W CRCW2512-HP'
for n in range(170,174):values[f'R{n}']='10 kohm 0.1% 25ppm/K'
for n in range(176,180):values[f'R{n}']=('499' if n<179 else '4.99')+' kohm 0.1% 25ppm/K'
for i in range(4):values[f'JP{i+2}']=f'AUX{i+1}_THERM_PULLUP_CLOSE_TO_ENABLE'
def add(net,ref,pin):expected.setdefault(net,set()).add(('thermistor/'+ref,str(pin)))
rail='THERM_EXC_2V495';diag='DIAG_U28_AIN3'
add(rail,'U31',1);add(rail,'U31',2);add('GND','U31',3);add('POD_5V_AUX','D105',1);add('THERM_BIAS_IN','D105',3);enc.add(('thermistor/D105','2'))
for ref,left,right in [('R174','THERM_BIAS_IN','THERM_BIAS_MID'),('R175','THERM_BIAS_MID',rail),('C128',rail,'GND'),('R180','POD_5V_AUX','GND'),('R176',rail,diag+'_UPPER1'),('R177',diag+'_UPPER1',diag+'_UPPER2'),('R178',diag+'_UPPER2',diag),('R179',diag,'GND'),('C129',diag,'GND')]:add(left,ref,1);add(right,ref,2)
for i in range(4):
 add(rail,f'R{170+i}',1);add(f'THERM_AUX{i+1}_SELECT',f'R{170+i}',2);add(f'THERM_AUX{i+1}_SELECT',f'JP{2+i}',1);add(f'POD_AUX{i+1}_SIGNAL',f'JP{2+i}',2)
check('U28 AIN3 was reserved NC',('diagnostic/U28','6') in enc);enc.discard(('diagnostic/U28','6'));expected[diag].add(('diagnostic/U28','6'))
check('19 exact additions',len(values)==19 and set(nc)-set(oc)=={'thermistor/'+r for r in values})
for ref,value in values.items():
 c=nc.get('thermistor/'+ref,{});check('value '+ref,c.get('value')==value)
 if ref.startswith('R'):fp='Resistor_SMD:R_'+('2512_6332Metric' if ref in ['R174','R175'] else '0603_1608Metric');lib='Device:R'
 elif ref.startswith('C'):fp='Capacitor_SMD:C_'+('1206_3216Metric' if ref=='C128' else '0603_1608Metric');lib='Device:C'
 elif ref.startswith('JP'):fp='Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm';lib='CANJumper:SolderJumper_2_Open'
 else:fp='Package_TO_SOT_SMD:SOT-23';lib='PodThermistor:TL431DBZ' if ref=='U31' else 'PodWheel:BAV199'
 check('footprint '+ref,c.get('footprint')==fp);check('symbol binding '+ref,c.get('lib_id')==lib);check('no donor binding '+ref,not any('donor' in k.lower() for k in c))
check('prior library manifest preserved',all(l in new['libraries'] for l in old['libraries']))
check('exact new library',[l['name'] for l in new['libraries'] if l not in old['libraries']]==['PodThermistor'])
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
check('TL431 DBZ pins',pins(libs.get('PodThermistor',{}).get('TL431DBZ',[]))=={'1':'K','2':'REF','3':'A'})
check('BAV199 pins',pins(libs.get('PodWheel',{}).get('BAV199',[]))=={'1':'A1','2':'K2','3':'K1_A2'})
for p in old_dir.rglob('*'):
 if p.is_file() and str(p.relative_to(old_dir)) not in ['intent.json','emitter-layout.json','integration-receipt.json']:
  q=new_dir/p.relative_to(old_dir);check('prior capture preserved '+str(p.relative_to(old_dir)),q.exists() and sha(p)==sha(q))
result={'status':'FAIL' if fail else 'PASS','check_count':len(checks),'failures':fail,'parse_errors':parse_errors,'inputs':{'old_intent_sha256':sha(op),'new_intent_sha256':sha(np),'authored_cad_sha256':hashes,'parser_sha256':sha(Path(parser.__file__)),'checker_sha256':sha(Path(__file__))},'scope':'Prepared graph and complete authored library syntax only; no native KiCad/ERC or hardware approval','checks':checks,'holds':['Four thermistor pullups default open; exact sensor, cold diode VF, shunt stability, thermal and dynamic fault qualification pending','Powered-off leakage/backfeed, upstream transient envelope and full error bounds unqualified','I2C timing and analog settling require measured validation','All prior Hall negative transient, thermal and native acceptance holds remain']};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','check_count','failures']}));sys.exit(bool(fail))
