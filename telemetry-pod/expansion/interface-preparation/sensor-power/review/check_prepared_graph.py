#!/usr/bin/env python3
"""Independent prepared intent graph only. Usage: OLD_INTENT NEW_INTENT SYMBOL REPORT.
Does not import producer logic, emit KiCad, or assert ERC/physical acceptance.
"""
import copy,hashlib,json,sys
from agent_ee.symbol_library import parse_library, LibraryError
import agent_ee.symbol_library as library_parser
from pathlib import Path
oldpath,newpath,symbolpath,reportpath=map(Path,sys.argv[1:])
old=json.loads(oldpath.read_text());new=json.loads(newpath.read_text());checks=[];fail=[]
def check(label,ok):
 checks.append(label)
 if not ok:fail.append(label)
def term(t):return (t['component'],str(t['pin']['number']))
def graph(d):
 result={};seen=set()
 for n in d['nets']:
  check('unique net '+n['name'],n['name'] not in result)
  ts=[term(t) for t in n['terminals']]
  check('unique terminals '+n['name'],len(ts)==len(set(ts)) and not(seen&set(ts)))
  seen.update(ts);result[n['name']]=set(ts)
 nc=[term(t) for t in d['no_connects']]
 check('unique and disconnected NC',len(nc)==len(set(nc)) and not(seen&set(nc)))
 return result,set(nc)
a,anc=graph(old);b,bnc=graph(new);expected=copy.deepcopy(a);enc=set(anc)
oc={c['id']:c for c in old['components']};nc={c['id']:c for c in new['components']}
check('unique new IDs',len(nc)==len(new['components']))
check('unique refs',len({c['reference'] for c in new['components']})==len(nc))
for k,c in oc.items():check('preserved component '+k,nc.get(k)==c)
added=set();values={}
def add(net,ref,pin):
 key=('sensor-power/'+ref,str(pin));expected.setdefault(net,set()).add(key)
for ix,(label,outnet,jpin) in enumerate([('FRONT','POD_WHEEL_FRONT_SUPPLY',23),('REAR','POD_WHEEL_REAR_SUPPLY',26),('TIRE','POD_TIRE_SUPPLY',31)]):
 u=f'U{23+ix}';rs=[f'R{73+4*ix+k}' for k in range(4)];cs=[f'C{86+3*ix+k}' for k in range(3)]
 names={s:'SENSOR_POWER_'+label+'_'+s for s in ['UVLO','OVP','RTN','ILIM','DVDT']}
 for ref in [u]+rs+cs:added.add('sensor-power/'+ref)
 values[u]='TPS26625DRCR'
 for ref,value in zip(rs,['1.05 Mohm 0.1% 25ppm/K','68.1 kohm 0.1% 25ppm/K','215 kohm 0.1% 25ppm/K',('26.7' if ix==2 else '44.2')+' kohm 0.1%']):values[ref]=value
 for ref,value in zip(cs,['1uF 50V X7R','100nF 50V X7R','10nF 50V C0G 10%']):values[ref]=value
 for pin,net in [(1,'PRE_6V3'),(2,names['UVLO']),(3,names['OVP']),(5,names['RTN']),(6,'GND'),(7,names['ILIM']),(8,names['DVDT']),(10,outnet),(11,names['RTN'])]:add(net,u,pin)
 enc.update({('sensor-power/'+u,'4'),('sensor-power/'+u,'9')})
 for ref,left,right in [(rs[0],'PRE_6V3',names['UVLO']),(rs[1],names['UVLO'],names['OVP']),(rs[2],names['OVP'],names['RTN']),(rs[3],names['ILIM'],names['RTN']),(cs[0],'PRE_6V3','GND'),(cs[1],outnet,'GND'),(cs[2],names['DVDT'],names['RTN'])]:add(left,ref,1);add(right,ref,2)
 key=('connector/J1',str(jpin));check('connector previously NC '+str(jpin),key in enc);enc.discard(key);expected[outnet].add(key)
for pin in ['25','28']:
 key=('connector/J1',pin);check('return previously NC '+pin,key in enc);enc.discard(key);expected['GND'].add(key)
check('exact added component set',set(nc)-set(oc)==added)
for ref,val in values.items():
 c=nc.get('sensor-power/'+ref,{});check('value '+ref,c.get('value')==val)
 if ref in {'C86','C89','C92'}:
  check('input bypass footprint '+ref,c.get('footprint')=='Capacitor_SMD:C_0805_2012Metric')
 if ref.startswith('U'):
  check('symbol '+ref,c.get('lib_id')=='PodSensorPower:TPS26625_DRC')
  check('footprint '+ref,c.get('footprint')=='Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm')
check('exact net set',set(b)==set(expected))
for n,ts in expected.items():check('exact membership '+n,b.get(n)==ts)
check('exact NC set',bnc==enc)
parsed={}
parse_error=None
try:
 symbols=parse_library(symbolpath.read_bytes())
 check('complete authored symbol library parses',True)
 check('exact authored symbol set',set(symbols)=={'TPS26625_DRC'})
 def walk(node):
  if isinstance(node,list):
   yield node
   for child in node:yield from walk(child)
 for node in walk(symbols.get('TPS26625_DRC',[])):
  if node and node[0]=='pin':
   names=[x for x in node if isinstance(x,list) and x and x[0]=='name']
   numbers=[x for x in node if isinstance(x,list) and x and x[0]=='number']
   check('structured symbol pin fields',len(names)==len(numbers)==1 and len(names[0])>=2 and len(numbers[0])>=2)
   if len(names)==len(numbers)==1 and len(names[0])>=2 and len(numbers[0])>=2:
    pin,name=numbers[0][1],names[0][1]
    check('unique symbol pin '+pin,pin not in parsed);parsed[pin]=name
except LibraryError as exc:
 parse_error=str(exc)
 check('complete authored symbol library parses',False)
check('exact physical pin functions',parsed=={'1':'IN','2':'UVLO','3':'OVP','4':'SHDN','5':'RTN','6':'GND','7':'ILIM','8':'dVdT','9':'FLT','10':'OUT','11':'EP_RTN'})
result={'status':'FAIL' if fail else 'PASS','check_count':len(checks),'failures':fail,'scope':'Prepared intent only; no native emission, ERC, footprint land qualification or electrical acceptance','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [oldpath,newpath,symbolpath]},'checks':checks,'library_parse_error':parse_error,'parser_source_sha256':hashlib.sha256(Path(library_parser.__file__).read_bytes()).hexdigest(),'limits':['C0G10% dVdT minimum nominal9nF; exact binding remains open','1uF nominal input bypass; exact effective capacitance and transient verification open','RTN-island negative-fault waveform and UVLO internal clamp assumptions need validation','No assembly availability or passive rating binding verified']}
reportpath.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','check_count','failures']}));sys.exit(bool(fail))
