"""Check the actual native STEP export of verify.py's connector-only fixture."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane

parser = argparse.ArgumentParser()
parser.add_argument('step', type=Path)
args = parser.parse_args()
solids = cq.importers.importStep(str(args.step)).solids().vals()
models = [s for s in solids if abs(s.Volume() - 20330.606767556506) < 0.01]
assert len(solids) == 2 and len(models) == 1, 'one board and exact connector required'
model = models[0]
axes = set()
tips = []
supports = []
for f in model.Faces():
    surface = BRepAdaptor_Surface(f.wrapped)
    if surface.GetType() == GeomAbs_Cylinder:
        cylinder = surface.Cylinder()
        if abs(cylinder.Axis().Direction().Z()) > .99999 and abs(cylinder.Radius() - .65) < 1e-5:
            p = cylinder.Location()
            axes.add((round(p.X(), 5), round(p.Y(), 5)))
    elif surface.GetType() == GeomAbs_Plane:
        plane = surface.Plane()
        if abs(plane.Axis().Direction().Z()) > .99999:
            if abs(f.Area() - math.pi * .65**2) < 1e-5:
                tips.append(plane.Location().Z())
            if abs(f.Area() - 6.5) < 1e-5:
                supports.append(plane.Location().Z())
expected = {(45 + x0 + 4*i, -55.5-y) for count, x0, y in [(12, -22, -4), (11, -20, 0), (12, -22, 4)] for i in range(count)}
assert axes == expected, 'native model tails must align with all 35 PCB drill axes'
assert len(tips) == 35 and len(supports) == 2, 'tail tips and rear seating flats'
assert all(abs(z - 1.565) < 1e-5 for z in supports), 'fixture-specific native seating datum'
assert all(abs(z + 1.935) < 1e-5 for z in tips), 'tail tips below seating plane'
assert abs(supports[0] - tips[0] - 3.5) < 1e-5, 'tail projection'
b = model.BoundingBox()
bounds = [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]
assert all(abs(a-e) < 1e-4 for a, e in zip(bounds, [6.55, 83.45, -87.3, -49.5, -2.765, 29.335])), 'model envelope'
print(json.dumps({'status': 'PASS', 'cadquery_version': cq.__version__, 'native_step_sha256': hashlib.sha256(args.step.read_bytes()).hexdigest(), 'tail_axes': len(axes), 'tail_projection_mm': 3.5, 'rear_support_z_mm': round(supports[0], 6), 'bounds_mm': [round(x, 6) for x in bounds], 'limits': 'Fixture geometry only; KiCad export offset is not physical stand-off or fit acceptance'}, indent=2))
