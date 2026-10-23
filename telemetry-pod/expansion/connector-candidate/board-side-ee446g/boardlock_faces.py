"""AGENTEE-446 ee446g: board-lock (locator peg) planar faces of the captured TE header STEP (MODEL-ONLY).

Usage (offline, under native-admit; cached CadQuery 2.8.0):
    uv run --offline --no-project --python 3.12 --with cadquery==2.8.0 python -B boardlock_faces.py STEP > boardlock-faces.json

Lists every planar face whose normal is parallel to the model's raw Y axis (the board-normal axis of the captured
footprint pose, rotation (-90, 0, 0)) and whose bounds lie inside the two peg regions around the drawing hole
centres raw (X, Z) = (+/-28.5, -31.3), as in review/section_step.py. The support flats are at raw Y = -11.72
(review/geometry.md). The output is a description of TE's customer view model, not a TE dimension, a retention
force, an insertion force or a fit claim.
"""
import hashlib
import json
import sys

import cadquery as cq

step = sys.argv[1]
solid = cq.importers.importStep(step).val()
faces = []
for face in solid.Faces():
    if face.geomType() != 'PLANE':
        continue
    n = face.normalAt()
    if abs(abs(n.y) - 1) > 1e-6:
        continue
    bb = face.BoundingBox()
    if not (bb.zmin > -34 and bb.zmax < -28.5 and ((bb.xmin > 25 and bb.xmax < 32) or (bb.xmin > -32 and bb.xmax < -25))):
        continue
    verts = [v.toTuple() for v in face.Vertices()]
    radial = max(((abs(x) - 28.5) ** 2 + (z + 31.3) ** 2) ** .5 for x, _, z in verts) if verts else None
    faces.append({'y': round(bb.ymin, 4), 'normal_y': round(n.y, 6), 'area_mm2': round(face.Area(), 4),
                  'x': [round(bb.xmin, 4), round(bb.xmax, 4)], 'z': [round(bb.zmin, 4), round(bb.zmax, 4)],
                  'max_vertex_distance_from_hole_axis_mm': None if radial is None else round(radial, 4)})
faces.sort(key=lambda f: (f['y'], f['x'], f['z']))
json.dump({'schema': 'ee446g.boardlock-faces/1', 'cadquery': cq.__version__,
           'step_sha256': hashlib.sha256(open(step, 'rb').read()).hexdigest(), 'support_flat_y': -11.72,
           'faces': faces}, sys.stdout, indent=1, sort_keys=True)
print()
