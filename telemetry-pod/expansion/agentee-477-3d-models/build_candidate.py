"""AGENTEE-477 candidate builder (isolated copy; visualization metadata only). Adds the declared 3D model entries of
MAPPING_JSON to the named footprints of BOARD and saves OUT. Refuses if any footprint's FPID, position, orientation,
side, pad inventory (number, net, local position, size, shape, layers) or any other footprint's model list changed.
Usage: build_candidate.py BOARD MAPPING_JSON OUT
"""
import json, sys
import pcbnew
board, mapping, out = sys.argv[1:4]
m = json.load(open(mapping))['models']
def inv(b):
    d = {}
    for fp in b.GetFootprints():
        pads = sorted((p.GetNumber(), p.GetNetname(), p.GetFPRelativePosition().x, p.GetFPRelativePosition().y, p.GetSizeX(), p.GetSizeY(),
                       int(p.GetShape(pcbnew.PADSTACK.ALL_LAYERS)), p.GetLayerSet().FmtHex()) for p in fp.Pads())
        d[fp.GetReference()] = (fp.GetFPIDAsString(), fp.GetPosition().x, fp.GetPosition().y, fp.GetOrientationDegrees(), fp.IsFlipped(), tuple(pads),
                                tuple((x.m_Filename, x.m_Offset.x, x.m_Offset.y, x.m_Offset.z, x.m_Rotation.x, x.m_Rotation.y, x.m_Rotation.z) for x in fp.Models()))
    return d
b = pcbnew.LoadBoard(board)
before = inv(b)
for fp in b.GetFootprints():
    spec = m.get(fp.GetReference())
    if not spec:
        continue
    if list(fp.Models()):
        raise SystemExit(f'{fp.GetReference()} already declares a model')
    x = pcbnew.FP_3DMODEL()
    x.m_Filename = spec['filename']
    x.m_Offset = pcbnew.VECTOR3D(*spec['offset_mm']); x.m_Rotation = pcbnew.VECTOR3D(*spec['rotation_deg']); x.m_Scale = pcbnew.VECTOR3D(1, 1, 1)
    x.m_Show = True
    fp.Models().push_back(x)
pcbnew.SaveBoard(out, b)
after = inv(pcbnew.LoadBoard(out))
problems = []
for ref, a in after.items():
    o = before[ref]
    if a[:6] != o[:6]:
        problems.append(f'{ref}: footprint identity/pose/pads changed')
    if ref not in m and a[6] != o[6]:
        problems.append(f'{ref}: model list changed without a mapping')
    if ref in m and len(a[6]) != 1:
        problems.append(f'{ref}: expected exactly one model')
if set(after) != set(before):
    problems.append('footprint set changed')
print(json.dumps({'out': out, 'footprints': len(after), 'models_added': sorted(set(m) & set(after)), 'problems': problems}))
sys.exit(1 if problems else 0)
