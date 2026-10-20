"""Independent prepared package-change review: PACKET CANDIDATE REPORT."""
import copy,hashlib,json,sys
from pathlib import Path
from agent_ee.symbol_library import parse_sexpr
source_only='--source-only' in sys.argv[1:]
root,candidate,report=map(Path,[a for a in sys.argv[1:] if a!='--source-only']);expansion=root.parent;checks=0
if not source_only:raise ValueError('This reviewer currently supports --source-only; native review requires a separate completed check')

def check(ok,why):
 global checks
 checks+=1
 if not ok:raise ValueError(why)

def hashes(path):return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}
def pinned(record):
 raw=(expansion/record['path']).read_bytes();check(hashlib.sha256(raw).hexdigest()==record['sha256'],'evidence hash '+record['path']);return raw

def sub(node,name):return [v for v in node[1:] if isinstance(v,list) and v and v[0]==name]
def only(node,name):
 rows=sub(node,name);check(len(rows)==1,'one '+name);return rows[0]

manifest=json.loads((root/'manifest.json').read_text());baseline=expansion/'part-bindings/prepared/inputs'
check(manifest['baseline']['path']=='part-bindings/prepared/inputs','baseline identity')
check(hashes(baseline)==manifest['baseline']['files_sha256'],'full pinned baseline capture')
old=json.loads((baseline/'intent.json').read_text());new=json.loads((candidate/'inputs/intent.json').read_text());normalized=copy.deepcopy(new)
oldmap={c['reference']:c for c in old['components']};newmap={c['reference']:c for c in normalized['components']}
check(len(oldmap)==len(newmap)==332 and set(oldmap)==set(newmap),'332 components preserved')
expected={
'RT0805BRD071M05L':('C7353633',{'R73','R77','R81','R162'},'1.05 Mohm 0.1% 25ppm/K','Resistor_SMD:R_0603_1608Metric','Resistor_SMD:R_0805_2012Metric'),
'C0805C475K4RACTU':('C7224519',{'C64','C66'},'4.7 uF/16 V X7R','Capacitor_SMD:C_0603_1608Metric','Capacitor_SMD:C_0805_2012Metric')}
check(len(manifest['parts'])==2 and {p['mpn'] for p in manifest['parts']}==set(expected),'two exact choices')
observations=[];seen=set()
for part in manifest['parts']:
 lcsc,refs,value,oldfp,newfp=expected[part['mpn']]
 check(part['lcsc']==lcsc and {c['reference'] for c in part['components']}==refs and len(part['components'])==len(refs),'exact allocation')
 check(part['new_footprint']==newfp,'new footprint identity')
 pinned(part['datasheet']);catalog=json.loads(pinned(part['catalog']));identity=catalog['parts'][lcsc]
 check((identity['mpn'],identity['mfr'])==(part['mpn'],part['manufacturer']),'catalog identity')
 req,=[r for r in catalog['requests'] if r['lcsc']==lcsc];raw=((expansion/part['catalog']['path']).parent/req['response']['path']).read_bytes()
 check(hashlib.sha256(raw).hexdigest()==req['response']['sha256'] and len(raw)==req['response']['size_bytes'],'raw capture integrity')
 row,=[r for r in json.loads(raw)['data']['componentPageInfo']['list'] if r['componentCode']==lcsc]
 check((row['componentModelEn'],row['componentBrandEn'],row['stockCount'])==(part['mpn'],part['manufacturer'],identity['stock']),'raw exact identity/stock')
 check(row['assemblyComponentFlag'] is False,'historical false assembly observation')
 for target in part['components']:
  ref=target['reference'];check(ref not in seen,'unique target');seen.add(ref);a=oldmap[ref];b=newmap[ref]
  check(all(a[k]==target[k] for k in ('id','reference','value','footprint')),'manifest target '+ref)
  check(a['value']==value and a['footprint']==oldfp and not a.get('part_binding'),'original selection '+ref)
  check(b['value']==value and b['footprint']==newfp,'only allowed package '+ref)
  binding=b['part_binding'];expectedbinding={'Manufacturer':part['manufacturer'],'Partnumber':part['mpn'],'LCSC':lcsc,'Datasheet':part['datasheet']['url'],'Qualification':'Identity and package selection only; assembly and operating qualification pending'}
  check({k:v for k,v in binding.items() if k!='PARAM_Datasheet'}==expectedbinding,'binding fields '+ref)
  check(json.loads(binding['PARAM_Datasheet'])=={'schema':'agent-ee.datasheet-binding/1','url':part['datasheet']['url'],'sha256':part['datasheet']['sha256']},'source binding '+ref)
  del b['part_binding'];b['footprint']=oldfp
 observations.append({'mpn':part['mpn'],'lcsc':lcsc,'stock_at_capture':identity['stock'],'captured_at':identity['last_seen'],'assemblyComponentFlag':row['assemblyComponentFlag']})
check(normalized==old,'complete source equality after exactly six permitted package/binding deltas')
check(len(seen)==6,'six targets')
check(sum(bool(c.get('part_binding')) for c in new['components'])==320,'320 bindings present')
check({c['reference'] for c in new['components'] if not c.get('part_binding')}=={'R60',*[f'JP{i}' for i in range(1,6)],*[f'#FLG{i:02d}' for i in range(1,7)]},'only R60 plus five copper jumpers and six flags unbound')
oldfiles=hashes(baseline);newfiles=hashes(candidate/'inputs');target='footprints/Resistor_SMD.pretty/R_0805_2012Metric.kicad_mod'
check(set(newfiles)-set(oldfiles)=={target} and not set(oldfiles)-set(newfiles),'one added footprint capture')
for path,digest in oldfiles.items():
 if path!='intent.json':check(newfiles[path]==digest,'preserved capture '+path)
raw=pinned(manifest['footprint_capture']);check(hashlib.sha256(raw).hexdigest()=='f050b6a50cc7e6f86291fb7aa8f87b0d02255e21cfbddf291cdccc87e5889794','reviewed R0805 hash')
check(manifest['footprint_capture']['target']==target and (candidate/'inputs'/target).read_bytes()==raw,'footprint target bytes')
for file,positions,size in [(target,[-.9125,.9125],[1.025,1.4]),('footprints/Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod',[-.95,.95],[1,1.45])]:
 tree=parse_sexpr((candidate/'inputs'/file).read_bytes());pads=sub(tree,'pad');check(len(pads)==2,'two pads '+file)
 for pad,x,num in zip(sorted(pads,key=lambda p:p[1]),positions,['1','2']):
  check(pad[1:4]==[num,'smd','roundrect'],'pad identity/style')
  check(list(map(float,only(pad,'at')[1:]))==[x,0],'pad center')
  check(list(map(float,only(pad,'size')[1:]))==size,'pad size')
  check(only(pad,'layers')[1:]==['F.Cu','F.Mask','F.Paste'],'pad layers')
check(json.loads((candidate/'receipt.json').read_text())=={'schema':'pod-component-fit-receipt/1','footprint_changes':6,'new_bindings':6,'total_bindings_present':320,'observations':observations,'qualification':'Not qualified for assembly or operation'},'exact receipt observations and qualification')
result={'status':'SOURCE_ONLY_PASS','checks':checks,'components':332,'footprint_changes':6,'new_bindings':6,'total_bindings_present':320,'unbound_part_references':['R60'],'observations':observations,'native_verification':'NOT_RUN','scope':'Package/binding preparation only; placement must be rerun; all electrical/thermal/mechanical/assembly qualifications remain open.'}
report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
