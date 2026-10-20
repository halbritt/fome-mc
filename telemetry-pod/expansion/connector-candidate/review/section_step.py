import cadquery as cq,json
from pathlib import Path
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
p=Path(__file__).parent;s=cq.importers.importStep(str(p.parent/'sources/c-1-776163-1-t-3d.stp')).val();result={}
for y in [-11.72,-12,-13,-13.29,-13.5,-14]:
 plane=cq.Face.makePlane(200,200,(0,y,0),(0,1,0));op=BRepAlgoAPI_Section(s.wrapped,plane.wrapped);op.Build();sec=cq.Shape.cast(op.Shape());edges=[]
 for e in sec.Edges():
  bb=e.BoundingBox()
  if bb.zmin< -29 and bb.zmax> -33 and ((bb.xmin>26 and bb.xmax<32) or (bb.xmin>-32 and bb.xmax<-26)):
   points=[e.positionAt(k/100) for k in range(101)];edges.append({'bounds':[bb.xmin,bb.xmax,bb.zmin,bb.zmax],'max_distance_from_hole_axis':max(((abs(v.x)-28.5)**2+(v.z+31.3)**2)**.5 for v in points)})
 result[str(y)]=edges
(p/'boardlock-sections.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
