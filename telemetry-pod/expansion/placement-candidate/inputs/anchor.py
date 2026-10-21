import json, sys, itertools
sys.path.insert(0,'/home/halbritt/.cache/agent499-cluster-anchored'); sys.path.insert(0,'/home/halbritt/git/agent-ee/src')
from agent_ee.placer import transform, boxes
from clusters import fps
sol=json.load(open('cluster-poses.json'))
FIXED=['J1','J2','U1','U2','H1','H2','H3','H4']
fixed_boxes=[(r,side,boxes(fps[r]).get(side)) for r in FIXED for side in ('F','B') if boxes(fps[r]).get(side)]
OUT=(500000,500000,89500000,64500000)  # 0.5 mm inside outline
def cluster_boxes(anchor,origin):
    out=[]
    for ref,(x,y,rot) in sol[anchor].items():
        fp=transform(fps[ref],[origin[0]+x,origin[1]+y],rot)
        for side,b in boxes(fp).items(): out.append((ref,side,b))
    return out
def clear(bs, others):
    for _,s,b in bs:
        if b[0]<OUT[0] or b[1]<OUT[1] or b[2]>OUT[2] or b[3]>OUT[3]: return False
        for _,s2,b2 in others:
            if s!=s2: continue
            gap=max(b2[0]-b[2],b[0]-b2[2],b2[1]-b[3],b[1]-b2[3])
            if gap<500000: return False
    return True
# preferred regions (mm): power bucks top-left/left-centre on F, U15 on B left, U26 F lower-left
prefs={'U5':[(x,y) for y in range(16,34,1) for x in range(12,40,1)],
       'U7':[(x,y) for y in range(16,34,1) for x in range(12,60,1)],
       'U15':[(x,y) for y in range(10,40,1) for x in range(8,40,1)],
       'U26':[(x,y) for y in range(20,44,1) for x in range(8,45,1)]}
placed=list(fixed_boxes); origins={}
for anchor in ('U5','U7','U15','U26'):
    for (x,y) in prefs[anchor]:
        o=(x*1000000,y*1000000); bs=cluster_boxes(anchor,o)
        if clear(bs,placed): origins[anchor]=o; placed+=bs; break
    print(anchor, origins.get(anchor))
abs_poses={}
for anchor,o in origins.items():
    for ref,(x,y,rot) in sol[anchor].items(): abs_poses[ref]=[o[0]+x,o[1]+y,rot,fps[ref]['side']]
json.dump({'origins_nm':origins,'poses':abs_poses},open('absolute-poses.json','w'),indent=1)
print(len(abs_poses),'footprints anchored')
