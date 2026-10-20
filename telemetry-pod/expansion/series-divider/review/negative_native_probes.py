"""PACKET CANDIDATE REPORT: checker controls on temporary damaged native evidence."""
import csv,json,shutil,subprocess,sys,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from agent_ee.symbol_library import parse_sexpr
root,source,report=map(Path,sys.argv[1:]);results=[]
def children(n,k):return [x for x in n[1:] if isinstance(x,list) and x and x[0]==k]
def one(n,k):return children(n,k)[0]
def serialize(n):return '('+' '.join(serialize(v) for v in n)+')' if isinstance(n,list) else json.dumps(n)
cases=[('lost_long_binding','XML binding'),('series_wrong_endpoint','unique XML terminals'),('embedded_pin_changed','embedded pin function'),('moved_nc','NC markers'),('missing_flag','component/unit membership'),('dnp_changed','attribute'),('bom_excluded','BOM values/exclusions'),('erc_wrong_sheet','ERC sheets')]
for name,reason in cases:
 with tempfile.TemporaryDirectory(prefix='native-series-negative-') as td:
  p=Path(td)/'candidate';shutil.copytree(source,p)
  if name in {'lost_long_binding','series_wrong_endpoint'}:
   path=p/'native.xml';tree=ET.parse(path)
   if name=='lost_long_binding':tree.find('./components/comp[@ref="U20"]/fields/field[@name="PARAM_Datasheet"]').text='truncated'
   else:
    net=next(n for n in tree.findall('./nets/net') if n.attrib['name']=='/SUP_U18_TOP_SERIES');next(n for n in net if n.attrib['ref']=='R181').set('pin','2')
   tree.write(path)
  elif name in {'embedded_pin_changed','moved_nc','missing_flag','dnp_changed'}:
   path=p/'project/telemetry-pod.kicad_sch';tree=parse_sexpr(path.read_bytes())
   if name=='embedded_pin_changed':
    symbol=next(s for s in children(one(tree,'lib_symbols'),'symbol') if s[1]=='Analog_ADC:MCP3208');pin=next(p for u in children(symbol,'symbol') for p in children(u,'pin') if one(p,'number')[1]=='12');pin[1]='output'
   elif name=='moved_nc':one(children(tree,'no_connect')[0],'at')[1]='9999'
   elif name=='missing_flag':tree.remove(next(s for s in children(tree,'symbol') if one(s,'lib_id')[1]=='power:PWR_FLAG'))
   else:one(next(s for s in children(tree,'symbol') if any(v[1:3]==['Reference','U20'] for v in children(s,'property'))),'dnp')[1]='yes'
   path.write_text(serialize(tree))
  elif name=='bom_excluded':
   path=p/'native-bom.csv';rows=list(csv.DictReader(path.open()));rows[0]['ExcludeBoard']='yes'
   with path.open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
  else:
   path=p/'erc.json';data=json.loads(path.read_text());data['sheets']=[{'path':'/fake','violations':[]}];path.write_text(json.dumps(data))
  run=subprocess.run([sys.executable,str(root/'review/check_native_series.py'),str(root),str(p),str(Path(td)/'result.json')],capture_output=True,text=True)
  if run.returncode==0 or reason not in run.stderr:raise ValueError('Unexpected negative outcome '+name+': '+run.stderr)
  results.append({'probe':name,'status':'REJECTED','evidence':run.stderr.splitlines()[-1]})
report.write_text(json.dumps({'scope':'damaged evidence checker controls; no damaged file is a native candidate','results':results},indent=2)+'\n');print('PASS: eight native negative controls rejected')
