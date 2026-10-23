"""AGENTEE-477 3D model inventory (read-only): every footprint's FPID, value, side, MPN/LCSC fields and declared 3D
models with offset/rotation/scale/visibility, and whether each model path resolves (KIPRJMOD = the board's dir;
KICAD*_3DMODEL_DIR = /usr/share/kicad/3dmodels). Usage: inventory.py BOARD OUT_JSON
"""
import json, os, re, sys
from pathlib import Path
import pcbnew
board, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
b = pcbnew.LoadBoard(str(board))
def resolve(name):
    s = name
    s = s.replace('${KIPRJMOD}', str(board.parent))
    s = re.sub(r'\$\{KICAD\d*_3DMODEL_DIR\}', '/usr/share/kicad/3dmodels', s)
    return s
rows = []
for fp in b.GetFootprints():
    fields = {f.GetName(): f.GetText() for f in fp.GetFields()}
    models = []
    for m in fp.Models():
        r = resolve(m.m_Filename)
        models.append({'filename': m.m_Filename, 'resolved': r, 'exists': os.path.isfile(r), 'show': bool(m.m_Show),
                       'offset_mm': [m.m_Offset.x, m.m_Offset.y, m.m_Offset.z], 'rotation_deg': [m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z],
                       'scale': [m.m_Scale.x, m.m_Scale.y, m.m_Scale.z]})
    rows.append({'ref': fp.GetReference(), 'fpid': fp.GetFPIDAsString(), 'value': fp.GetValue(), 'side': 'B' if fp.IsFlipped() else 'F', 'position_mm': [fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6], 'orientation_deg': fp.GetOrientationDegrees(),
                 'pads': fp.GetPadCount(), 'mpn': fields.get('MPN') or fields.get('Manufacturer_Part_Number') or fields.get('MFR_PN'),
                 'lcsc': fields.get('LCSC') or fields.get('LCSC_Part'), 'fields': {k: v for k, v in fields.items() if k not in ('Reference', 'Value', 'Footprint') and v and len(v) < 200},
                 'models': models, 'has_loadable_model': any(m['exists'] and m['show'] for m in models)})
doc = {'board': str(board), 'footprints': len(rows), 'with_loadable_model': sum(r['has_loadable_model'] for r in rows),
       'without': sorted((r['ref'] for r in rows if not r['has_loadable_model']), key=lambda s: (re.sub(r'\d', '', s), int(re.sub(r'\D', '', s) or 0))),
       'rows': rows}
out.write_text(json.dumps(doc, indent=1, sort_keys=True) + '\n')
print(json.dumps({k: doc[k] for k in ('footprints', 'with_loadable_model', 'without')}))
