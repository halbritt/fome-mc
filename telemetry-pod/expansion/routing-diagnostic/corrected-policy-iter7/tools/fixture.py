"""Make one DRC fixture: a copy of BOARD with a single /GND track or via added.

usage: fixture.py BOARD OUT KIND LAYER X1 Y1 [X2 Y2]
KIND is track or via (through via F.Cu-B.Cu, Default net-class size 0.6/0.3 mm; LAYER is ignored); track width 0.2 mm.
Also: fixture.py BOARD --free X Y R  prints whether any pad lies within R mm of (X, Y).
"""
import sys, uuid, pcbnew

MM = pcbnew.FromMM
b = pcbnew.LoadBoard(sys.argv[1])

if sys.argv[2] == "--free":
    x, y, r = map(float, sys.argv[3:6])
    p = pcbnew.VECTOR2I(MM(x), MM(y))
    near = [f"{pad.GetParentFootprint().GetReference()}.{pad.GetNumber()}"
            for pad in b.GetPads() if (pad.GetPosition() - p).EuclideanNorm() < MM(r)
            or pad.HitTest(p, MM(r))]
    print("near:", near)
    sys.exit(0)

out, kind, layer = sys.argv[2:5]
xy = list(map(float, sys.argv[5:]))
gnd = b.FindNet("/GND")
assert gnd is not None
if kind == "track":
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(MM(xy[0]), MM(xy[1])))
    t.SetEnd(pcbnew.VECTOR2I(MM(xy[2]), MM(xy[3])))
    t.SetWidth(MM(0.2))
    t.SetLayer(b.GetLayerID(layer))
else:
    t = pcbnew.PCB_VIA(b)
    t.SetViaType(pcbnew.VIATYPE_THROUGH)
    t.SetPosition(pcbnew.VECTOR2I(MM(xy[0]), MM(xy[1])))
    t.SetWidth(MM(0.6))
    t.SetDrill(MM(0.3))
    t.SetLayerPair(b.GetLayerID("F.Cu"), b.GetLayerID("B.Cu"))
t.SetNet(gnd)
t.SetUuid(pcbnew.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL, "fixture:" + " ".join(sys.argv[3:])))))  # reproducible
b.Add(t)
assert pcbnew.SaveBoard(out, b)
