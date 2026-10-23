import pathlib,json,shutil,hashlib,collections,datetime
b=pathlib.Path('/home/halbritt/.cache/route-3-agent507');out=pathlib.Path('/home/halbritt/.cache/agent-worktrees/fome-mc/route-3-local/telemetry-pod/expansion/route-3');out.mkdir(parents=True,exist_ok=True);(out/'candidate').mkdir(exist_ok=True);(out/'checks').mkdir(exist_ok=True);(out/'diagnosis').mkdir(exist_ok=True);(out/'recipe').mkdir(exist_ok=True);(out/'logs').mkdir(exist_ok=True)
final=b/'attempt2/run/candidate/project';original=pathlib.Path('/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z');before=json.loads((original/'validate/candidate-facts.json').read_text());after=json.loads((b/'native-final-route1/candidate-facts.json').read_text())
for p in final.iterdir():
 if p.is_file() and p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_dru','.kicad_sch']:shutil.copy2(p,out/'candidate'/p.name)
for name in ['route1','r5']:
 shutil.copytree(b/('native-final-'+name),out/'checks'/('against-'+name),dirs_exist_ok=True);shutil.copy2(b/('grade-'+name+'.json'),out/'checks'/('against-'+name+'-result.json'))
for number in [1,2]:
 src=b/f'attempt{number}';dest=out/'attempts'/str(number);dest.mkdir(parents=True,exist_ok=True)
 for f in ['command.txt','start.json','exit.json','stdout.json','stderr.log','edit.json','precheck-result.json','reachability.json']:
  if (src/f).exists():shutil.copy2(src/f,dest/f)
 for f in ['result.json','attempt.json','snapshot.json']:shutil.copy2(src/'run'/f,dest/f)
 shutil.copy2(src/'run/work/krt.log',dest/'router.log');shutil.copy2(src/'run/work/krt-out/summary.json',dest/'router-summary.json');shutil.copytree(src/'run/validate',dest/'validate',dirs_exist_ok=True)
 if number==1:shutil.copytree(src/'precheck',dest/'precheck',dirs_exist_ok=True);shutil.copy2(src/'run/candidate/project/telemetry-pod.kicad_pcb',dest/'NOT-RETAINED.kicad_pcb')
for f in ['prepare.py','route.py','route2.py','final_grade.py']:shutil.copy2(b/f,out/'recipe'/f)
for src,label in [(pathlib.Path('/home/halbritt/.cache/route-2-agent507/r5-U30.8.json'),'r5-U30.8.json'),(pathlib.Path('/home/halbritt/.cache/route-2-agent507/route1-U30.8.json'),'route1-U30.8.json'),(pathlib.Path('/home/halbritt/.cache/route-2-agent507/route1-U30.8-defect.json'),'route1-U30.8-defect.json')]:shutil.copy2(src,out/'diagnosis'/label)
changes={};nets=set();positions=[]
for typ in ['tracks','vias']:
 a={t['uuid']:t for t in before[typ]};c={t['uuid']:t for t in after[typ]};added=[c[u] for u in c.keys()-a.keys()];removed=[a[u] for u in a.keys()-c.keys()];modified=[{'before':a[u],'after':c[u]} for u in a.keys()&c.keys() if a[u]!=c[u]];changes[typ]={'added':added,'removed':removed,'modified':modified}
 for x in added+removed+[x[y] for x in modified for y in ['before','after']]:
  nets.add(x['net']);positions.extend([x['start'],x['end']] if typ=='tracks' else [x['position']])
assert nets=={'/SENSOR_POWER_AUX_DVDT','/GND'};assert len(changes['tracks']['modified'])==2 and len(changes['vias']['modified'])==1;assert not changes['tracks']['removed'] and not changes['vias']['removed'];assert len(changes['tracks']['added'])==4 and len(changes['vias']['added'])==1
bounds=[min(p[0] for p in positions)/1e6,min(p[1] for p in positions)/1e6,max(p[0] for p in positions)/1e6,max(p[1] for p in positions)/1e6];assert 55.9<=bounds[0] and bounds[2]<=58.0 and 42.5<=bounds[1] and bounds[3]<=47
changes['changed_nets']=sorted(nets);changes['changed_object_centerline_bounds_mm']=bounds;changes['accepted_region_mm']=[55.5,42.5,58.5,47.0];(out/'checks/copper-changes.json').write_text(json.dumps(changes,indent=2))
parts={'route1':json.loads((original/'validate/candidate-terminal-components.json').read_text()),'route3':json.loads((b/'native-final-route1/candidate-terminal-components.json').read_text())};comp={}
for k,d in parts.items():assert d['status']=='PASS';comp[k]={'complete_nets':sum(len(g)==1 for g in d['nets'].values()),'incomplete_nets':sum(len(g)>1 for g in d['nets'].values()),'component_deficit':sum(len(g)-1 for g in d['nets'].values())}
assert parts['route1']['inventory']==parts['route3']['inventory'];splits=[]
for net,groups in parts['route1']['nets'].items():
 for group in groups:
  if not any(set(group)<=set(g) for g in parts['route3']['nets'][net]):splits.append({'net':net,'group':group})
assert not splits;root='/SENSOR_POWER_AUX_DVDT';assert len(parts['route1']['nets'][root])==2 and len(parts['route3']['nets'][root])==1;comp['target']={'before_components':2,'after_components':1};comp['split_components']=splits;(out/'checks/native-connectivity-comparison.json').write_text(json.dumps(comp,indent=2))
ident={}
for name,p,expect in [('route1',original/'candidate/project/telemetry-pod.kicad_pcb','19ed7954ab305b39f29d19f08fb619b4399cb6522869fba21b7712a52a310bdf'),('r5',original/'reference/project/telemetry-pod.kicad_pcb','8f3bc234305516b91b6e519d3e0a3cd05b69b6dd16006a317c39b6d810ace5fd'),('route3',final/'telemetry-pod.kicad_pcb',None)]:
 sha=hashlib.sha256(p.read_bytes()).hexdigest();assert not expect or sha==expect;ident[name]={'path':str(p),'sha256':sha,'expected':expect}
(out/'checks/board-identities.json').write_text(json.dumps(ident,indent=2));print('identities',ident);print('metrics',comp,'bounds',bounds)
