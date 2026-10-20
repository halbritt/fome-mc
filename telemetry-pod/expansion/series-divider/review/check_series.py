"""Independent exact series replacement: PACKET BASE_INPUTS CANDIDATE REPORT --source-only."""
import copy,hashlib,json,sys
from pathlib import Path
if '--source-only' not in sys.argv:raise ValueError('Native topology review is not implemented here')
root,base,candidate,report=map(Path,[x for x in sys.argv[1:] if x!='--source-only']);checks=0

def require(ok,why):
 global checks
 checks+=1
 if not ok:raise ValueError(why)
def hashes(path):return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}
def term(ref,pin):return {'component':'supervisor/'+ref,'pin':{'number':str(pin)}}
manifest=json.loads((root/'manifest.json').read_text());oldhash=hashes(base);newhash=hashes(candidate/'inputs')
require(oldhash==manifest['baseline_files_sha256'],'pinned baseline tree')
require(set(oldhash)==set(newhash),'capture file membership')
for path,digest in oldhash.items():
 if path not in {'intent.json','emitter-layout.json'}:require(newhash[path]==digest,'capture unchanged '+path)
old=json.loads((base/'intent.json').read_text());new=json.loads((candidate/'inputs/intent.json').read_text());normalized=copy.deepcopy(new)
byref={c['reference']:c for c in normalized['components']};byid={c['id']:c for c in normalized['components']}
require(len(byref)==len(byid)==len(normalized['components'])==333,'unique333 component identities')
require(sum(bool(c.get('part_binding')) for c in new['components'])==322,'322 bindings')
expected={'R60':('RT0603BRD0730K1L','C705764','30.1 kohm 0.1% 25ppm/K'),'R181':('RT0603BRD071K2L','C136970','1.2 kohm 0.1% 25ppm/K')}
require(len(manifest['parts'])==2 and {p['reference'] for p in manifest['parts']}==set(expected),'two exact selections')
raw=(root/'stock/catalog.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==manifest['catalog_sha256'],'catalog hash');cat=json.loads(raw);observations=[]
for part in manifest['parts']:
 ref=part['reference'];mpn,lcsc,value=expected[ref]
 require((part['mpn'],part['lcsc'],part['value'],part['manufacturer'])==(mpn,lcsc,value,'YAGEO'),'exact manifest identity '+ref)
 ds=part['datasheet'];require(hashlib.sha256((root/ds['path']).read_bytes()).hexdigest()==ds['sha256'],'datasheet hash')
 identity=cat['parts'][lcsc];require((identity['mpn'],identity['mfr'])==(mpn,'YAGEO'),'catalog identity')
 request,=[r for r in cat['requests'] if r['lcsc']==lcsc];raw=(root/'stock'/request['response']['path']).read_bytes()
 require(hashlib.sha256(raw).hexdigest()==request['response']['sha256'] and len(raw)==request['response']['size_bytes'],'raw capture hash/size')
 row,=[r for r in json.loads(raw)['data']['componentPageInfo']['list'] if r['componentCode']==lcsc]
 require((row['componentModelEn'],row['componentBrandEn'],row['stockCount'])==(mpn,'YAGEO',identity['stock']),'raw identity and stock')
 require(row['assemblyComponentFlag'] is False,'historical false assembly flag')
 c=byref[ref];binding=c.get('part_binding',{})
 require({k:v for k,v in binding.items() if k!='PARAM_Datasheet'}=={'Manufacturer':'YAGEO','Partnumber':mpn,'LCSC':lcsc,'Datasheet':ds['url'],'Qualification':'Identity and series-divider selection only; assembly and operating qualification pending'},'binding fields '+ref)
 require(json.loads(binding['PARAM_Datasheet'])=={'schema':'agent-ee.datasheet-binding/1','sha256':ds['sha256'],'url':ds['url']},'datasheet binding')
 require({k:v for k,v in c.items() if k!='part_binding'}=={'id':'supervisor/'+ref,'reference':ref,'lib_id':'Device:R','units':[1],'footprint':'Resistor_SMD:R_0603_1608Metric','value':value},'exact component '+ref)
 observations.append({'reference':ref,'mpn':mpn,'lcsc':lcsc,'stock_at_capture':identity['stock'],'captured_at':identity['last_seen'],'assemblyComponentFlag':False})
# Each terminal must occur once. The midpoint may contain exactly two pins.
occupied={}
for n in normalized['nets']:
 for t in n['terminals']:
  key=(t['component'],t['pin']['number']);require(key not in occupied,'terminal repeated');occupied[key]=n['name']
bridges=[n for n in normalized['nets'] if n['name']=='SUP_U18_TOP_SERIES'];require(len(bridges)==1,'one midpoint net');bridge=bridges[0]
require(bridge=={'id':'supervisor-SUP_U18_TOP_SERIES','name':'SUP_U18_TOP_SERIES','terminals':[term('R60',2),term('R181',1)]},'midpoint exact two-terminal topology')
sense,=[n for n in normalized['nets'] if n['name']=='SUP_U18_SENSE'];require(sense['terminals'].count(term('R181',2))==1,'new sense endpoint')
sense['terminals'][sense['terminals'].index(term('R181',2))]=term('R60',2)
normalized['nets'].remove(bridge)
normalized['components'].remove(byref['R181']);byref['R60']['value']='31.3 kohm 0.1%';del byref['R60']['part_binding']
require(normalized==old,'collapse pair restores entire old intent including320 bindings and NCs')
layout=json.loads((candidate/'inputs/emitter-layout.json').read_text());oldlayout=json.loads((base/'emitter-layout.json').read_text())
groups=[g for g in layout['groups'] if 'supervisor/R181' in g['components']];require(len(groups)==1,'one R181 layout group');g=groups[0]
require(g['components'].count('supervisor/R181')==1 and g['components'].index('supervisor/R181')==g['components'].index('supervisor/R60')+1,'R181 layout immediately after R60')
g['components'].remove('supervisor/R181');require(layout==oldlayout,'exact prior layout after removal')
receipt=json.loads((candidate/'receipt.json').read_text());require(receipt=={'schema':'pod-series-divider-receipt/1','components':333,'bindings_present':322,'top_nominal_ohm':31300,'falling_threshold_nominal_v':4.7495,'extra_resistors':1,'observations':observations,'native_verification':'NOT_RUN','qualification':'Not qualified for assembly or operation'},'exact receipt')
result={'status':'SOURCE_ONLY_PASS','checks':checks,'components':333,'bindings_present':322,'new_components':1,'series_top_nominal_ohm':31300,'falling_threshold_nominal_v':4.7495,'baseline_intent_sha256':oldhash['intent.json'],'candidate_intent_sha256':newhash['intent.json'],'observations':observations,'native_verification':'NOT_RUN','scope':'Exact source topology replacement only; electrical, placement, thermal, assembly and native qualification remain open.'}
report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
