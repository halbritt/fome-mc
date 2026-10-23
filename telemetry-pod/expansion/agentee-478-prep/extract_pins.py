"""Read-only pcbnew extraction (no save): per footprint ref/value/fpid/side/pose,
per pad number/net/pin function/type/centre. Usage: extract_pins.py <board> <out.json>"""
import hashlib, json, sys
import pcbnew

board_path, out = sys.argv[1], sys.argv[2]
sha = hashlib.sha256(open(board_path, 'rb').read()).hexdigest()
b = pcbnew.LoadBoard(board_path)
mm = lambda v: round(pcbnew.ToMM(v), 4)
fps = {}
for fp in b.GetFootprints():
    ref = fp.GetReference()
    pads = []
    for p in fp.Pads():
        c = p.GetPosition()
        pads.append({'number': p.GetNumber(), 'net': p.GetNetname(),
                     'pin_function': p.GetPinFunction(), 'pin_type': p.GetPinType(),
                     'x': mm(c.x), 'y': mm(c.y), 'pth': p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH})
    bb = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd).BBox()
    fps[ref] = {'value': fp.GetValue(), 'fpid': fp.GetFPIDAsString(),
                'side': 'B' if fp.IsFlipped() else 'F',
                'x': mm(fp.GetPosition().x), 'y': mm(fp.GetPosition().y),
                'rot': round(fp.GetOrientationDegrees(), 3),
                'courtyard_bbox': [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())],
                'pads': pads}
json.dump({'board': board_path, 'sha256': sha, 'footprints': fps}, open(out, 'w'), indent=1, sort_keys=True)
assert hashlib.sha256(open(board_path, 'rb').read()).hexdigest() == sha
print(len(fps), sha)
