import json,hashlib
from pathlib import Path
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Plane
p=Path(__file__).parent;source=p.parent/'sources/c-1-776163-1-t-3d.stp';shape=cq.importers.importStep(str(source)).val();planes=[];cyl=[]
def bounds(s):
 b=s.BoundingBox();return [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]
for f in shape.Faces():
 a=BRepAdaptor_Surface(f.wrapped)
 if a.GetType()==GeomAbs_Cylinder:
  c=a.Cylinder();v=c.Axis().Direction();loc=c.Location()
  if abs(v.Y())>.999999:cyl.append({'radius':c.Radius(),'axis_origin':[loc.X(),loc.Y(),loc.Z()],'bounds':bounds(f)})
 elif a.GetType()==GeomAbs_Plane:
  n=a.Plane().Axis().Direction()
  if abs(n.Y())>.999999:planes.append({'area':f.Area(),'bounds':bounds(f),'normal':[n.X(),n.Y(),n.Z()]})
tails=[c for c in cyl if abs(c['radius']-.65)<1e-5 and abs(c['bounds'][2]+14.97)<1e-4]
# Deduplicate split cylindrical surfaces by their axis, selecting all tail barrels near underside.
barrels={}
for c in cyl:
 if abs(c['radius']-.65)<1e-5 and c['bounds'][2]<-12:
  x,_,z=c['axis_origin'];barrels[(round(x,5),round(z,5))]=c
expected={(float(x),float(z)) for z,x0,count in [(-35.8,-22,12),(-31.8,-20,11),(-27.8,-22,12)] for x in [x0+4*i for i in range(count)]}
actual=set(barrels);transformed=shape.rotate((0,0,0),(1,0,0),90).translate((0,-31.8,11.72))
tail_tips=[f for f in planes if abs(f['bounds'][2]+15.22)<1e-6 and abs(f['area']-1.32732289614)<1e-6]
seating=[f for f in planes if abs(f['bounds'][2]+11.72)<1e-6 and abs(f['area']-6.5)<1e-6]
result={'tail_tip_count':len(tail_tips),'seating_support_flats':seating,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cadquery_version':cq.__version__,'solid_count':len(shape.Solids()),'raw_bounds':bounds(shape),'physical_transformed_bounds':bounds(transformed),'tail_axes_count':len(actual),'tail_axes_exact_match':actual==expected,'tail_axes_raw_XZ':sorted(actual),'parallel_Y_cylinders':cyl,'parallel_Y_planes':sorted(planes,key=lambda f:-f['area']),'transform':'physical=(X,-Z-31.8,Y+11.72); screen=(X,Z+31.8)'}
(p/'step-independent.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['parallel_Y_cylinders','parallel_Y_planes','tail_axes_raw_XZ']}));print('Planes',json.dumps(result['parallel_Y_planes'][:10]));print('Non-tail Y cylinders',json.dumps([c for c in cyl if abs(c['radius']-.65)>1e-5]))
