import pathlib,json,hashlib,shutil,collections
b=pathlib.Path('/home/halbritt/.cache/route-4-agent507');out=pathlib.Path('/home/halbritt/.cache/agent-worktrees/fome-mc/route-4-local-batch/telemetry-pod/expansion/route-4');out.mkdir(parents=True,exist_ok=True)
for name in ['candidate','checks','targets','recipe','logs']: (out/name).mkdir(exist_ok=True)
inc=b/'target1-attempt1/candidate/project';src=pathlib.Path('/home/halbritt/.cache/route-3-agent507/attempt2/run/candidate/project');assert hashlib.sha256((src/'telemetry-pod.kicad_pcb').read_bytes()).hexdigest()=='0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651';expect=json.loads((b/'target1-attempt1/result.json').read_text())['board_sha256'];assert hashlib.sha256((inc/'telemetry-pod.kicad_pcb').read_bytes()).hexdigest()==expect
for p in inc.iterdir():
 if p.is_file() and p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_dru','.kicad_sch']:shutil.copy2(p,out/'candidate'/p.name)
for label in ['route3','r5']:
 shutil.copytree(b/('final-against-'+label),out/'checks'/('against-'+label),dirs_exist_ok=True);shutil.copy2(b/('final-'+label+'.json'),out/'checks'/('against-'+label+'-result.json'))
for step,files in [('target1-attempt1',['edit.json','result.json','native-reference-context.json']),('target2-attempt1',['edit.json','precheck-result.json']),('target3-attempt1',['command.txt','exit.json']),('target3-attempt2',['edit.json','result.json'])]:
 dest=out/'targets'/step;dest.mkdir()
 for name in files:shutil.copy2(b/step/name,dest/name)
 native=b/step/('precheck' if step=='target2-attempt1' else 'native')
 if native.exists():
  for name in ['new-findings.json','preservation.json']:shutil.copy2(native/name,dest/name)
 if step=='target3-attempt1':
  shutil.copy2(b/step/'run/work/krt.log',dest/'router.log');shutil.copy2(b/step/'run/result.json',dest/'router-result.json');shutil.copy2(b/step/'run/work/krt-out/summary.json',dest/'router-summary.json');shutil.copy2(b/step/'run/validate/new-findings.json',dest/'new-findings.json');shutil.copy2(b/step/'run/validate/preservation.json',dest/'preservation.json')
shutil.copy2(b/'inspection.json',out/'targets/native-terminal-inspection.json');shutil.copy2(b/'STATE.json',out/'batch-state.json')
for name in ['inspect.py','step1.py','step2_precheck.py','target3_route.py','target3_direct.py','final_grade.py','package.py']:shutil.copy2(b/name,out/'recipe'/name)
before=json.loads((b/'target1-attempt1/reference-facts.json').read_text());after=json.loads((b/'final-against-route3/candidate-facts.json').read_text());changes={}
for kind in ['tracks','vias']:
 a={x['uuid']:x for x in before[kind]};c={x['uuid']:x for x in after[kind]};assert all(c.get(u)==v for u,v in a.items());added=[c[u] for u in c.keys()-a.keys()];changes[kind]={'before':len(a),'after':len(c),'added':added,'removed':[],'modified':[]}
assert not changes['tracks']['added'] and len(changes['vias']['added'])==1 and changes['vias']['added'][0]['net']=='/GND';(out/'checks/copper-changes.json').write_text(json.dumps(changes,indent=2))
ref=json.loads((b/'target1-attempt1/native/reference-terminal-components.json').read_text());end=json.loads((b/'final-against-route3/candidate-terminal-components.json').read_text());assert ref['status']=='PASS' and end['status']=='PASS' and ref['inventory']==end['inventory'];splits=[];changed=[]
for n,groups in ref['nets'].items():
 if groups!=end['nets'][n]:changed.append(n)
 for g in groups:
  if not any(set(g)<=set(x) for x in end['nets'][n]):splits.append({'net':n,'group':g})
assert not splits and changed==['/GND'];inspection=json.loads((b/'inspection.json').read_text());junction=next(x for x in inspection['ground_junctions'] if x['point_mm']==[49.4,14.1]);groups={tuple(sorted(p['uuid'] for p in x['terminals'])) for x in junction['tracks']};assert sorted(len(g) for g in groups)==[1,10,48];union=set().union(*(set(g) for g in groups));assert len(union)==59;assert sum(union<=set(g) for g in end['nets']['/GND'])==1
metrics={}
for name,d in [('route3',ref),('route4',end)]:metrics[name]={'nets':len(d['nets']),'complete_nets':sum(len(g)==1 for g in d['nets'].values()),'incomplete_nets':sum(len(g)>1 for g in d['nets'].values()),'component_deficit':sum(len(g)-1 for g in d['nets'].values()),'ground_components':len(d['nets']['/GND'])}
proof={'metrics':metrics,'split_components':splits,'changed_terminal_nets':changed,'joined_native_terminal_groups':[list(g) for g in sorted(groups)],'joined_terminals':59};(out/'checks/native-terminal-comparison.json').write_text(json.dumps(proof,indent=2));print('METRICS',metrics)
ident={}
for name,path,expected in [('route3',src/'telemetry-pod.kicad_pcb','0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651'),('route4',inc/'telemetry-pod.kicad_pcb',expect),('r5',pathlib.Path('/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z/reference/project/telemetry-pod.kicad_pcb'),'8f3bc234305516b91b6e519d3e0a3cd05b69b6dd16006a317c39b6d810ace5fd')]:
 sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==expected;ident[name]={'path':str(path),'sha256':sha,'expected':expected}
(out/'checks/board-identities.json').write_text(json.dumps(ident,indent=2));(out/'targets/scratch-locations.json').write_text(json.dumps({n:str(b/n) for n in ['target1-attempt1','target2-attempt1','target3-attempt1','target3-attempt2']},indent=2));print('CANDIDATE',expect)
