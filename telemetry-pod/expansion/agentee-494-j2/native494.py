import json,sys,math,hashlib
from pathlib import Path
import pcbnew as K
c=Path(sys.argv[1]);out=[]
# The superseded conditional variant lives in historical-superseded/ as evidence only.
for name in ['SMA_Amphenol_132134_Manufacturer']:
 f=K.FootprintLoad(str(c/'Agentee494.pretty'),name);assert f
 f.SetPosition(K.VECTOR2I(K.FromMM(103),K.FromMM(40))); f.SetOrientationDegrees(0)
 rows=[]
 for q in f.Pads():
  z=q.GetBoundingBox();d=q.GetDrillSize();s=q.GetSize();v=q.GetPosition()
  rows.append({'number':str(q.GetNumber()),'xy':[v.x/1e6,v.y/1e6],'drill':[d.x/1e6,d.y/1e6],'size':[s.x/1e6,s.y/1e6],'bbox':[z.GetLeft()/1e6,z.GetTop()/1e6,z.GetRight()/1e6,z.GetBottom()/1e6]})
 assert len(rows)==5 and sum(r['number']=='1' for r in rows)==1 and sum(r['number']=='2' for r in rows)==4
 assert all(r['drill'][0]>0 for r in rows)
 for r in rows:
  x0,y0,x1,y1=r['bbox'];r['ideal_110x80_edge_margin']=min(x0,y0,110-x1,80-y1);assert r['ideal_110x80_edge_margin']>0
 out.append({'name':name,'pads':rows,'footprint_sha256':hashlib.sha256((c/'Agentee494.pretty'/f'{name}.kicad_mod').read_bytes()).hexdigest()})
res={'schema':'agentee494.native/1','runtime':K.GetBuildVersion(),'scope':'Footprint load, five pads, actual native sizes/drills/pose/bboxes on ideal 110x80 rectangle only. No canonical board load/save, DRC, net connectivity, saved Edge.Cuts, packing or assembly qualification.','tool_status':'PASS','footprints':out}
(c/'native494.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
