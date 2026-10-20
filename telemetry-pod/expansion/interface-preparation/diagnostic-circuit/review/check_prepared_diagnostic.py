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
values={}
def add(net,ref,pin):expected.setdefault(net,set()).add(('diagnostic/'+ref,str(pin)))
for ref,net,mpin in [('R160','DIAG_I2C_SDA','22'),('R161','DIAG_I2C_SCL','23')]:
 values[ref]='2.2 kohm 1% 100ppm/C';add('+3V3',ref,1);add(net,ref,2)
 key=('mcu',mpin);check('host was NC '+mpin,key in enc);enc.discard(key);expected[net].add(key)
for ix in range(3):
 u=f'U{27+ix}';values[u]='ADS1119IPWR'
 for pin in [3,12,13]:add('+3V3',u,pin)
 for pin in [4,5]:add('GND',u,pin)
 add('+3V3' if ix==1 else 'GND',u,1);add('+3V3' if ix==2 else 'GND',u,2)
 add('DIAG_I2C_SDA',u,15);add('DIAG_I2C_SCL',u,16)
 for pin in [6,8,9,14]:enc.add(('diagnostic/'+u,str(pin)))
 for k in range(2):
  c=f'C{118+2*ix+k}';values[c]='1uF 50V X7R';add('+3V3',c,1);add('GND',c,2)
enc.add(('diagnostic/U28','7'))
channels=[('U27',0,'POD_12V_PROTECTED'),('U27',1,'PRE_6V3'),('U27',2,'+3V3'),('U28',0,'EMMC_VCC_3V3'),('U28',1,'POD_5V_SENSOR'),('U29',0,'POD_WHEEL_FRONT_SUPPLY'),('U29',1,'POD_WHEEL_REAR_SUPPLY'),('U29',2,'POD_TIRE_SUPPLY')]
for ix,(u,ch,rail) in enumerate(channels):
 node=f'DIAG_{u}_AIN{ch}';rr=[f'R{128+4*ix+k}' for k in range(4)];c=f'C{110+ix}'
 values.update({r:('499 kohm 0.1% 25ppm/C' if k<3 else '4.99 kohm 0.1% 25ppm/C') for k,r in enumerate(rr)});values[c]='100nF 50V X7R'
 for ref,left,right in [(rr[0],rail,node+'_UPPER1'),(rr[1],node+'_UPPER1',node+'_UPPER2'),(rr[2],node+'_UPPER2',node),(rr[3],node,'GND'),(c,node,'GND')]:add(left,ref,1);add(right,ref,2)
 add(node,u,[11,10,7][ch])
check('51 exact additions',len(values)==51 and set(nc)-set(oc)=={'diagnostic/'+ref for ref in values})
for ref,value in values.items():
 c=nc.get('diagnostic/'+ref,{});check('value '+ref,c.get('value')==value)
 if ref.startswith('R'):fp='Resistor_SMD:R_0603_1608Metric'
 elif ref.startswith('C'):fp='Capacitor_SMD:C_'+('0805_2012Metric' if int(ref[1:])>=118 else '0603_1608Metric')
 else:fp='Package_SO:TSSOP-16_4.4x5mm_P0.65mm'
 check('footprint '+ref,c.get('footprint')==fp)
 if ref.startswith('U'):check('ADC symbol binding '+ref,c.get('lib_id')=='PodDiagnostic:ADS1119_PW')
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
result={'status':'FAIL' if fail else 'PASS','check_count':len(checks),'failures':fail,'parse_errors':parse_errors,'inputs':{'old_intent_sha256':sha(op),'new_intent_sha256':sha(np),'authored_cad_sha256':hashes,'parser_sha256':sha(Path(parser.__file__)),'checker_sha256':sha(Path(__file__))},'scope':'Prepared graph and complete authored library syntax only; no native KiCad/ERC or hardware approval','checks':checks,'holds':['Eight existing rails only; ninth AUX rail absent and U28 AIN2 explicitly NC','Powered-off leakage/backfeed, upstream transient envelope and full error bounds unqualified','I2C timing and analog settling require measured validation','All prior Hall negative transient, thermal and native acceptance holds remain']};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','check_count','failures']}));sys.exit(bool(fail))
