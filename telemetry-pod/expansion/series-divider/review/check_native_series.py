"""Independent native series candidate: PACKET_DIR CANDIDATE_DIR REPORT_JSON."""
import copy,csv,hashlib,json,re,sys
from collections import Counter
from decimal import Decimal as D
from pathlib import Path
import xml.etree.ElementTree as ET
from agent_ee.symbol_library import parse_sexpr
root,candidate,report=map(Path,sys.argv[1:]);base=root.parent/'native-candidate';checks=0

def need(ok,msg):
 global checks
 checks+=1
 if not ok:raise ValueError(msg)
def children(n,k):return [x for x in n[1:] if isinstance(x,list) and x and x[0]==k]
def one(n,k):
 rows=children(n,k);need(len(rows)==1,'one '+k);return rows[0]
def keyed(rows,key,label):
 out={}
 for row in rows:
  k=key(row);need(k not in out,'duplicate '+label+str(k));out[k]=row
 return out

def pinrows(symbol):
 out={}
 for unit in children(symbol,'symbol'):
  match=re.search(r'_(\d+)_(\d+)$',unit[1]);need(bool(match),'unit name')
  u,style=map(int,match.groups())
  for p in children(unit,'pin'):
   k=(u,style,one(p,'number')[1]);need(k not in out,'duplicate library pin');out[k]=p
 return out

def sourcepins(symbols,name,trail=()):
 need(name not in trail,'inheritance cycle');s=symbols[name];parent=children(s,'extends')
 if parent:
  need(len(parent)==1 and not children(s,'symbol'),'supported inherited pins');return sourcepins(symbols,parent[0][1],(*trail,name))
 return pinrows(s)

intent_path=candidate/'inputs/intent.json';intent=json.loads(intent_path.read_text());components=keyed(intent['components'],lambda c:c['reference'],'source ref');byid=keyed(intent['components'],lambda c:c['id'],'source id')
need(len(components)==333,'333 source components');flags={r for r,c in components.items() if c['lib_id']=='power:PWR_FLAG'};need(len(flags)==6,'six flags')
schematic_path=candidate/'project/telemetry-pod.kicad_sch';tree=parse_sexpr(schematic_path.read_bytes());need(tree[0]=='kicad_sch','schematic root');embedded=keyed(children(one(tree,'lib_symbols'),'symbol'),lambda s:s[1],'embedded symbol')
libraries={}
for lib in intent['libraries']:
 raw=(candidate/'inputs'/lib['path']).read_bytes();need(hashlib.sha256(raw).hexdigest()==lib['sha256'],'source library hash '+lib['name']);libtree=parse_sexpr(raw);need(libtree[0]=='kicad_symbol_lib','library root');libraries[lib['name']]=keyed(children(libtree,'symbol'),lambda s:s[1],'source symbol')
need(set(embedded)=={c['lib_id'] for c in components.values()},'exact embedded library membership')
pins={}
for libid,symbol in embedded.items():
 lib,name=libid.split(':',1);expected=sourcepins(libraries[lib],name);actual=pinrows(symbol);need(actual==expected,'embedded pin function/geometry mismatch '+libid);pins[libid]=actual

previous=parse_sexpr((base/'captured/project/telemetry-pod.kicad_sch').read_bytes())
def instances(t):
 result={}
 for s in children(t,'symbol'):
  props=keyed(children(s,'property'),lambda p:p[1],'property');values={k:v[2] for k,v in props.items()};key=(values['Reference'],int(one(s,'unit')[1]));need(key not in result,'duplicate placed unit');result[key]=(s,values)
 return result
placed=instances(tree);prior=instances(previous);expectedunits={(r,u) for r,c in components.items() for u in c.get('units',[1])};need(set(placed)==expectedunits,'all333 component/unit membership');pinpositions={};pindefs={}
for (ref,unit),(s,props) in placed.items():
 c=components[ref];old=prior[('R60' if ref=='R181' else ref,unit)][0]
 need(one(s,'lib_id')[1]==c['lib_id'],'placed libid '+ref)
 need(props['Value']==c['value'] and props.get('Footprint','')==c.get('footprint',''),'placed value/footprint '+ref)
 need(one(s,'on_board')[1]==('no' if ref in flags else 'yes'),'on_board '+ref)
 excluded=ref in flags or ref in {f'TP{i}' for i in range(1,7)} or c.get('in_bom') is False
 need(one(s,'in_bom')[1]==('no' if excluded else 'yes'),'in_bom '+ref)
 for attribute in ('mirror','dnp','in_pos_files','exclude_from_sim','body_style'):
  rows=children(s,attribute);need(len(rows)<=1 and rows==children(old,attribute),'attribute '+ref+'/'+attribute)
 binding=c.get('part_binding',{})
 need(set(props)<={'Reference','Value','Footprint','Datasheet','Description'}|set(binding) and set(binding)<=set(props),'exact schematic fields '+ref)
 for k,v in binding.items():need(props[k]==v,'schematic binding '+ref+'/'+k)
 position=one(s,'at');need(len(position)==4,'placed pose');x,y,angle=map(D,position[1:]);need(angle in (0,90,180,270),'orthogonal pose');need(not children(s,'mirror'),'unhandled mirrored pin geometry')
 for (u,style,number),p in pins[c['lib_id']].items():
  if u not in (0,unit) or style not in (0,1):continue
  need((ref,number) not in pindefs,'one physical pin placement');pindefs[ref,number]=p
  px,py,_=map(D,one(p,'at')[1:]);dx,dy={D(0):(px,-py),D(90):(-py,-px),D(180):(-px,py),D(270):(py,px)}[angle]
  pinpositions[ref,number]=(x+dx,y+dy)

def terminal(t):return (byid[t['component']]['reference'],str(t['pin']['number']))
expectednets=keyed(intent['nets'],lambda n:'/'+n['name'],'source net');expectednc={terminal(t) for t in intent['no_connects']};need(len(expectednc)==175,'175 source NCs')
assigned=set()
for n in intent['nets']:
 for t in n['terminals']:
  key=terminal(t);need(key in pindefs and key not in assigned,'valid unique source terminal');assigned.add(key)
need(not assigned&expectednc and assigned|expectednc==set(pindefs),'every library pin assigned or declared NC')
ncpositions=Counter(tuple(map(D,one(n,'at')[1:])) for n in children(tree,'no_connect'));need(ncpositions==Counter(pinpositions[t] for t in expectednc),'explicit NC markers match actual declared pin coordinates')
# PWR_FLAG terminals are omitted from XML. Check their emitted wire/label attachment directly.
adjacency={};labels={}
for wire in children(tree,'wire'):
 points=children(one(wire,'pts'),'xy');need(len(points)==2,'two-endpoint emitted wire');a,b=[tuple(map(D,p[1:])) for p in points]
 adjacency.setdefault(a,set()).add(b);adjacency.setdefault(b,set()).add(a)
for label in children(tree,'label')+children(tree,'global_label'):
 labels.setdefault(tuple(map(D,one(label,'at')[1:3])),set()).add(label[1])
for ref in flags:
 start=pinpositions[ref,'1'];pending=[start];visited=set();names=set()
 while pending:
  point=pending.pop()
  if point in visited:continue
  visited.add(point);names|=labels.get(point,set());pending.extend(adjacency.get(point,set())-visited)
 expectedname=next(n['name'] for n in intent['nets'] if any(terminal(t)==(ref,'1') for t in n['terminals']))
 need(names=={expectedname},'power flag wire/label connection '+ref)
xml=ET.parse(candidate/'native.xml');xmlcomponents=keyed(xml.findall('./components/comp'),lambda c:c.attrib['ref'],'native component');need(set(xmlcomponents)==set(components)-flags,'327 XML components')
for ref,n in xmlcomponents.items():
 c=components[ref];need(n.findtext('value')==c['value'] and (n.findtext('footprint') or '')==c.get('footprint',''),'XML value/footprint '+ref)
 fields=keyed(n.findall('./fields/field'),lambda f:f.attrib['name'],'XML field');binding=c.get('part_binding',{})
 need(set(fields)=={'Footprint','Datasheet','Description'}|set(binding),'XML field membership '+ref)
 for k,v in binding.items():need((fields[k].text or '')==v,'XML binding '+ref+'/'+k)
 if 'Datasheet' in binding:need(n.findtext('datasheet')==binding['Datasheet'],'XML datasheet '+ref)
actualnets=keyed(xml.findall('./nets/net'),lambda n:n.attrib['name'],'XML net');need(len(actualnets)==369 and len(expectednets)==194,'194 named plus175NC nets');observed=set();actualnc=set()
for name,n in actualnets.items():
 nodes=n.findall('node');members={(v.attrib['ref'],v.attrib['pin']) for v in nodes};need(len(members)==len(nodes) and not observed&members,'unique XML terminals');observed|=members
 if name in expectednets:
  expectedmembers={terminal(t) for t in expectednets[name]['terminals'] if terminal(t)[0] not in flags};need(members==expectedmembers,'named net mismatch '+name)
 else:
  need(name.startswith('unconnected-') and len(nodes)==1,'unexpected XML net');actualnc|=members
 for node in nodes:
  key=node.attrib['ref'],node.attrib['pin'];p=pindefs[key];kind=p[1];types=node.attrib['pintype'].split('+')
  need(types[0]==kind,'XML electrical type '+str(key));need(('no_connect' in types)==(key in expectednc),'XML explicit NC '+str(key))
  label=one(p,'name')[1];function=node.attrib.get('pinfunction','')
  need(function in ({'', '~'} if label=='~' else {label,label+'_'+key[1]}),'XML pin function '+str(key))
need(actualnc==expectednc,'exact XML NC set')
# Independently contract the sole series subdivision back to prior native connectivity.
def graph(t):return {n.attrib['name']:sorted(tuple(sorted(v.attrib.items())) for v in n.findall('node')) for n in t.findall('./nets/net')}
reduced=copy.deepcopy(xml);nets=reduced.find('./nets');bridge=next(n for n in nets if n.attrib['name']=='/SUP_U18_TOP_SERIES');need({(v.attrib['ref'],v.attrib['pin']) for v in bridge}=={('R60','2'),('R181','1')},'series bridge exact')
nets.remove(bridge);sense=next(n for n in nets if n.attrib['name']=='/SUP_U18_SENSE');endpoint=[v for v in sense if v.attrib['ref']=='R181' and v.attrib['pin']=='2'];need(len(endpoint)==1,'series sense endpoint');endpoint[0].set('ref','R60')
need(graph(reduced)==graph(ET.parse(base/'native.xml')),'series reduction exact prior native graph')
with (candidate/'native-bom.csv').open() as f:bom=keyed(list(csv.DictReader(f)),lambda r:r['Reference'],'BOM row')
include={r:c for r,c in components.items() if r not in flags and r not in {f'TP{i}' for i in range(1,7)} and c.get('in_bom',True)};need(set(bom)==set(include) and len(bom)==316,'exact316 BOM rows')
for ref,c in include.items():need(bom[ref]['Value']==c['value'] and bom[ref]['Footprint']==c['footprint'] and bom[ref]['ExcludeBOM']==bom[ref]['ExcludeBoard']=='','BOM values/exclusions '+ref)
erc=json.loads((candidate/'erc.json').read_text());olderc=json.loads((base/'erc.json').read_text())
for key in ('ignored_checks','included_severities','kicad_version'):need(erc[key]==olderc[key],'ERC policy '+key)
need([{k:v for k,v in s.items() if k!='violations'} for s in erc['sheets']]==[{k:v for k,v in s.items() if k!='violations'} for s in olderc['sheets']],'ERC sheets');need(bool(erc['sheets']) and not any(s['violations'] for s in erc['sheets']),'ERC zero findings')
files={'intent':intent_path,'schematic':schematic_path,**{k:candidate/k for k in ('native.xml','native-bom.csv','erc.json')},'baseline_xml':base/'native.xml','baseline_schematic':base/'captured/project/telemetry-pod.kicad_sch'}
result={'status':'PASS','checks':checks,'source_components':333,'schematic_units':len(placed),'xml_components':327,'named_nets':194,'explicit_nc':175,'bom_components':316,'binding_components':sum(bool(c.get('part_binding')) for c in components.values()),'sha256':{k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in files.items()},'scope':'Exact candidate native source correspondence only; unreleased emitter candidate provenance is separate. Not placement, routing, fabrication, assembly or operating qualification.'}
report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
