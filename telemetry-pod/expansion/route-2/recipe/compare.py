import pathlib,json,collections,hashlib
b=pathlib.Path('/home/halbritt/.cache/route-2-agent507');out=pathlib.Path('/home/halbritt/.cache/agent-worktrees/fome-mc/route-2-repair/telemetry-pod/expansion/route-2');r=b/'run';v=pathlib.Path(json.loads((b/'grade-dirs.json').read_text())['against_route1'])
assert (v/'candidate-facts.json').exists()
old=json.loads((r/'facts/reference-facts.json').read_text());new=json.loads((v/'candidate-facts.json').read_text());changes={};counts=collections.Counter()
for typ in ['tracks','vias']:
 def k(x):return json.dumps({n:v for n,v in x.items() if n!='uuid'},sort_keys=True)
 a=collections.Counter(k(x) for x in old[typ]);c=collections.Counter(k(x) for x in new[typ]);added=list((c-a).elements());removed=list((a-c).elements())
 changes[typ]={'before':len(old[typ]),'after':len(new[typ]),'added_geometry':[json.loads(x) for x in added],'removed_geometry':[json.loads(x) for x in removed]}
 for x in added:counts[(json.loads(x)['net'],'added_'+typ)]+=1
 for x in removed:counts[(json.loads(x)['net'],'removed_'+typ)]+=1
changes['by_net']={n:{key:counts[(n,key)] for key in ['added_tracks','removed_tracks','added_vias','removed_vias']} for n in sorted({n for n,k in counts})}
(out/'diagnosis'/'copper-changes.json').write_text(json.dumps(changes,indent=1))
# Compare all pad components, not just complete nets.
orig=pathlib.Path('/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z/validate')
parts={'r5':json.loads((orig/'reference-terminal-components.json').read_text()),'route1':json.loads((orig/'candidate-terminal-components.json').read_text()),'route2':json.loads((v/'candidate-terminal-components.json').read_text())}
res={'metrics':{},'comparisons':{}}
for name,d in parts.items():
 assert d['status']=='PASS',name
 g=d['nets'];res['metrics'][name]={'nets':len(g),'complete_nets':sum(len(x)==1 for x in g.values()),'incomplete_nets':sum(len(x)>1 for x in g.values()),'open_pad_pairs':sum(len(x)-1 for x in g.values())}
for name in ['r5','route1']:
 prior=parts[name];after=parts['route2'];assert prior['inventory']==after['inventory'];splits=[];closed=[]
 for net,groups in prior['nets'].items():
  end=[set(x) for x in after['nets'][net]]
  for g in groups:
   if not any(set(g)<=x for x in end):splits.append({'net':net,'original_pad_uuids':g,'candidate_groups':[sorted(x) for x in end if x&set(g)]})
  if len(groups)>1 and len(end)==1:closed.append(net)
 res['comparisons'][name]={'split_components':splits,'newly_complete_nets':closed}
(out/'diagnosis'/'native-connectivity-comparison.json').write_text(json.dumps(res,indent=2));print(json.dumps({k:v for k,v in res['metrics'].items()},indent=2));print('splits',[(k,len(v['split_components'])) for k,v in res['comparisons'].items()]);print('changednets',len(changes['by_net']))
