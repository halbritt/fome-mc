import json, sys, itertools, math
sys.path.insert(0,'/home/halbritt/git/agent-ee/src')
from agent_ee.placer import transform, boxes
probe=json.load(open('/home/halbritt/.cache/agent491-main-buck-locality/work/proposal/placement-probe.json'))
fps={f['ref']:f for f in probe['footprints']}
doc=json.load(open('/home/halbritt/git/fome-mc/telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json'))
W=json.load(open('/home/halbritt/.cache/agent491-main-buck-locality/isolated-witnesses.json'))
clusters={w['anchor']:{k:tuple(v) for k,v in w['poses_nm'].items()} for w in W['witnesses']}
# designed clusters (relative to anchor origin, nm, rotation deg)
clusters['U15']={'U15':(0,0,0),'C70':(-3200000,500000,90),'L4':(3300000,1700000,90),'C68':(1000000,-3300000,0),'C69':(1000000,-6600000,0)}
clusters['U26']={'U26':(0,0,0),'C97':(4300000,-1900000,180),'C98':(4600000,400000,180)}
def place(cluster, origin=(45000000,30000000), variants=None):
    placed={}
    for ref,(x,y,rot) in cluster.items():
        if variants and ref in variants: rot=variants[ref]
        placed[ref]=transform(fps[ref],[origin[0]+x,origin[1]+y],rot)
    return placed
def measure(placed):
    rows=[]
    for o in doc['obligations']:
        for role in ('supply','return','switch'):
            if role not in o: continue
            pr=o[role]; a,b=pr['from'],pr['to']
            if a['reference'] not in placed or b['reference'] not in placed: continue
            pa=[p for p in placed[a['reference']]['pads'] if p['number']==a['pad']][0]['position_nm']
            pb=[p for p in placed[b['reference']]['pads'] if p['number']==b['pad']][0]['position_nm']
            d=math.dist(pa,pb)/1e6; rows.append((o['id'],role,round(d,3),pr['max_distance_nm']/1e6,d*1e6<=pr['max_distance_nm']))
    return rows
def gaps(placed):
    bad=[]
    for a,b in itertools.combinations(placed.values(),2):
        for side in ('F','B'):
            ba,bb=boxes(a).get(side),boxes(b).get(side)
            if not ba or not bb: continue
            gap=max(bb[0]-ba[2],ba[0]-bb[2],bb[1]-ba[3],ba[1]-bb[3])
            if gap<250000: bad.append((a['ref'],b['ref'],side,gap))
    return bad
if __name__=='__main__':
    for anchor,cl in clusters.items():
        pl=place(cl); rows=measure(pl); g=gaps(pl)
        fails=[r for r in rows if not r[4]]
        print(f"== {anchor}: {len(rows)} pairs, {len(fails)} fail, gaps<0.25mm: {g}")
        for r in rows: print('   ', 'OK ' if r[4] else 'BAD', r)
