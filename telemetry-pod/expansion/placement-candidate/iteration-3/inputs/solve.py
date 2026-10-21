import json, sys, math, itertools
sys.path.insert(0, "/home/halbritt/.cache/agent499-cluster-anchored")
sys.path.insert(0,'/home/halbritt/git/agent-ee/src')
from agent_ee.placer import transform, boxes
from clusters import fps, doc, clusters, place, measure, gaps
O=(45000000,30000000)
def pairs_for(ref):
    out=[]
    for o in doc['obligations']:
        for role in ('supply','return','switch'):
            if role in o:
                pr=o[role]
                if ref in (pr['from']['reference'],pr['to']['reference']): out.append(pr)
    return out
def pad(placed,e): return [p for p in placed[e['reference']]['pads'] if p['number']==e['pad']][0]['position_nm']
def solve(anchor, order, span=9000000, step=250000, rots=(0,90,180,270)):
    placed={anchor:transform(fps[anchor],list(O),0)}
    poses={anchor:(0,0,0)}
    for ref in order:
        prs=pairs_for(ref); best=None
        for rot in rots:
            for dx in range(-span,span+1,step):
                for dy in range(-span,span+1,step):
                    cand=transform(fps[ref],[O[0]+dx,O[1]+dy],rot)
                    trial=dict(placed); trial[ref]=cand
                    ok=True; cost=0
                    for pr in prs:
                        a,b=pr['from'],pr['to']
                        if a['reference'] not in trial or b['reference'] not in trial: continue
                        d2=sum((p-q)**2 for p,q in zip(pad(trial,a),pad(trial,b)))
                        if d2>pr['max_distance_nm']**2: ok=False; break
                        cost+=d2/pr['max_distance_nm']**2
                    if not ok: continue
                    if gaps(trial): continue
                    cost+= (dx*dx+dy*dy)/1e14*0.01
                    if best is None or cost<best[0]: best=(cost,dx,dy,rot)
        if best is None: print('NO POSE for',ref); return None
        _,dx,dy,rot=best; poses[ref]=(dx,dy,rot); placed[ref]=transform(fps[ref],[O[0]+dx,O[1]+dy],rot)
        print(anchor,ref,'->',(dx/1e6,dy/1e6,rot))
    return poses
sol={}
sol['U15']=solve('U15',['C70','L4','C68','C69'])
sol['U26']=solve('U26',['C97','C98'],span=7000000)
sol['U5']=clusters['U5']; sol['U7']=clusters['U7']
json.dump({k:{r:list(v) for r,v in p.items()} for k,p in sol.items() if p},open('cluster-poses.json','w'),indent=1)
for k,p in sol.items():
    if not p: continue
    pl=place(p); rows=measure(pl); g=gaps(pl)
    print('==',k,'fails',[r for r in rows if not r[4]],'gaps',g)
    for r in rows: print('   ',r)
