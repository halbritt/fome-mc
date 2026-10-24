"""Native geometry witness only. The single diagnostic run did not emit a schematic/candidate."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import pcbnew
here=Path('telemetry-pod/expansion/production-capture')
spec=importlib.util.spec_from_file_location('verify_j2',here/'verify_j2.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
p=Path('build/ee485-J2b-run/pipe/content/project/telemetry-pod.kicad_pcb')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
before=sha(p); board=pcbnew.LoadBoard(str(p)); j2=next(f for f in board.GetFootprints() if f.GetReference()=='J2')
assert j2.m_Uuid.AsString()=='18c6ebf4-5f6a-5227-b278-be0fa33a91c9'
assert j2.GetFPID().GetUniStringLibId()=='Agentee494:SMA_Amphenol_132134_Manufacturer'
stock=pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty','SMA_Amphenol_132134_Vertical')
pattern=module.pattern(j2); assert pattern==module.pattern(stock)
assert [(r[0],r[1],r[2],r[3],r[4]) for r in pattern]==[('1',0,0,1.5,1.5),*[('2',x,y,1.7,1.7) for x in (-2.54,2.54) for y in (-2.54,2.54)]]
pose=[pcbnew.ToMM(j2.GetPosition().x),pcbnew.ToMM(j2.GetPosition().y)];assert pose==[80,28]
right=pcbnew.ToMM(j2.GetBoundingBox(False,False).GetRight());assert right<=90
binding=json.loads((here/'composition/j2-rf-binding.json').read_text())
areas={z.m_Uuid.AsString():z for z in board.Zones()}; found=[]
for uuid, expected in binding['rule_area_bindings'].items():
    zone=areas[uuid]
    points=[[round(pcbnew.ToMM(zone.Outline().CVertex(i).x),4),round(pcbnew.ToMM(zone.Outline().CVertex(i).y),4)] for i in range(zone.Outline().TotalVertices())]
    assert sorted(points)==sorted(expected['polygon_mm'])
    assert zone.GetDoNotAllowTracks()==expected['tracks_forbidden']
    assert zone.GetDoNotAllowVias()==expected['vias_forbidden']
    found.append({'uuid':uuid,'polygon_mm':points,'tracks_forbidden':zone.GetDoNotAllowTracks(),'vias_forbidden':zone.GetDoNotAllowVias()})
# Reproduce the actual bad UTF8 comparison and verify the corrected guard on the same native object.
assert j2.GetFPID().GetLibItemName()!='SMA_Amphenol_132134_Manufacturer'
assert j2.GetFPID().GetUniStringLibItemName()=='SMA_Amphenol_132134_Manufacturer'
assert sha(p)==before
report={'status':'PASS','scope':'SCAFFOLD GEOMETRY ONLY; native schematic emission NOT_RUN; no placement/assembly acceptance',
        'board_sha256':before,'native_footprints':len(board.GetFootprints()),'j2_uuid':j2.m_Uuid.AsString(),
        'pose_mm':pose,'rightmost_mm':right,'published_pattern_stock_parity':pattern,'rule_areas':found,
        'original_UTF8_guard_rejects':True,'corrected_unicode_guard_accepts':True}
Path('build/ee485-J2b-scaffold-witness.json').write_text(json.dumps(report,indent=1)+'\n')
print(json.dumps(report,indent=1))
