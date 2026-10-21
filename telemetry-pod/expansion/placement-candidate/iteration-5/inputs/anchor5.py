import json, sys
sys.path.insert(0,'/home/halbritt/.cache/agent499-cluster-anchored'); sys.path.insert(0,'/home/halbritt/git/agent-ee/src')
from agent_ee.placer import transform, boxes
from clusters import fps
sol=json.load(open('cluster-poses.json'))
M=1000000
# fixed parts: historical anchors, J2 moved inboard (D-PCB-4), U3 fixed adjacent to J2 (short RF path)
fixed_pose={'J1':(45*M,55.5*M,0),'J2':(85.24*M,28*M,180),'U1':(72.5*M,6.5*M,0),'U2':(12*M,10*M,0),'H1':(4*M,4*M,0),'H2':(86*M,4*M,0),'H3':(86*M,61*M,0),'H4':(4*M,61*M,0),'U3':(71.5*M,35*M,180),'L3':(80.6*M,28.6*M,90)}
fixed_boxes=[]
for r,(x,y,rot) in fixed_pose.items():
    for side,b in boxes(transform(fps[r],[x,y],rot)).items(): fixed_boxes.append((r,side,b))
IMU=('U2',); INDUCTORS={'L1','L2'}
OUT=(500000,500000,89500000,64500000)
def cluster_boxes(anchor,origin):
    out=[]
    for ref,(x,y,rot) in sol[anchor].items():
        for side,b in boxes(transform(fps[ref],[origin[0]+x,origin[1]+y],rot)).items(): out.append((ref,side,b))
    return out
def gap(b,b2): return max(b2[0]-b[2],b[0]-b2[2],b2[1]-b[3],b[1]-b2[3])
def ok(bs, others):
    for ref,s,b in bs:
        if b[0]<OUT[0] or b[1]<OUT[1] or b[2]>OUT[2] or b[3]>OUT[3]: return False
        for ref2,s2,b2 in others:
            g=gap(b,b2)
            if s==s2 and g<500000: return False                      # same side: 0.5 mm
            if ref2 in IMU and g<4*M: return False                   # IMU isolation, either side
            if s!=s2 and g<0 and (ref2 in fixed_pose or ref in INDUCTORS or ref2 in INDUCTORS): return False  # no through-board stacking with fixed parts or inductors
            if s!=s2 and g<0 and ref2 not in fixed_pose: return False  # clusters never stack on each other
    return True
prefs={'U5':[(x,y) for y in range(14,36) for x in range(27,52)],
       'U7':[(x,y) for y in range(14,42) for x in range(27,70)],
       'U15':[(x,y) for y in range(8,42) for x in range(20,62)],
       'U26':[(x,y) for y in range(20,46) for x in range(8,46)]}
M_=1000000
imu_obs=[('OBS','B',(7*M_,5*M_,17*M_,15*M_)),('OBS','F',(7.5*M_,4.5*M_,9.9*M_,15.5*M_)),('OBS','F',(14.1*M_,4.5*M_,17.75*M_,15.5*M_)),('OBS','F',(10.1*M_,4.5*M_,13.9*M_,8.15*M_)),('OBS','F',(10.1*M_,11.85*M_,13.9*M_,15.5*M_))]
placed=list(fixed_boxes)+imu_obs; origins={}
for anchor in ('U5','U7','U26'):
    for (x,y) in prefs[anchor]:
        o=(x*M,y*M); bs=cluster_boxes(anchor,o)
        if ok(bs,placed): origins[anchor]=o; placed+=bs; break
    print(anchor, origins.get(anchor) and (origins[anchor][0]/M,origins[anchor][1]/M))
abs_poses={}
for anchor,o in origins.items():
    for ref,(x,y,rot) in sol[anchor].items(): abs_poses[ref]=[o[0]+x,o[1]+y,rot,fps[ref]['side']]
for r,(x,y,rot) in fixed_pose.items():
    if r in ('J2','U3','L3'): abs_poses[r]=[x,y,rot,fps[r]['side']]
# obstacles: IMU zone on B and F ring; inductor shadows on the opposite side
def rect(x0,y0,x1,y1): return [[int(x0),int(y0)],[int(x1),int(y0)],[int(x1),int(y1)],[int(x0),int(y1)]]
obs=[{'side':'B','polygons':[rect(7*M,5*M,17*M,15*M)],'name':'IMU U2 exclusion (through-board)'}]+[{'side':'F','polygons':[rect(*[v for v in b])],'name':'IMU ring'} for _,sd,b in imu_obs if sd=='F']
for L in INDUCTORS:
    x,y,rot,side=abs_poses[L]
    for s,b in boxes(transform(fps[L],[x,y],rot)).items():
        obs.append({'side':'B' if s=='F' else 'F','polygons':[rect(b[0]-0.5*M,b[1]-0.5*M,b[2]+0.5*M,b[3]+0.5*M)],'name':f'{L} shadow'})
json.dump({'origins_nm':origins,'fixed':fixed_pose,'poses':abs_poses,'obstacles':obs},open('iter5/absolute-poses.json','w'),indent=1)
print(len(abs_poses),'anchored (33 cluster + J2 + U3);',len(obs),'obstacles')
