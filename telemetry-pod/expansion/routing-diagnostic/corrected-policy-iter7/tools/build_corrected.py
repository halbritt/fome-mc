"""Add the D-PCB-7 v2 and D-PCB-6 native rule areas to a copy of the iteration-7 input.

usage: build.py SRC.kicad_pcb OUT.kicad_pcb
Nothing else on the board is touched; the result is saved once with pcbnew.
"""
import sys, uuid, pcbnew

src, out = sys.argv[1:3]
b = pcbnew.LoadBoard(src)
MM = pcbnew.FromMM
NS = uuid.UUID("6f1c6c1e-7d0a-4a51-9a52-2c1b0d7f0091")  # fixed namespace -> reproducible UUIDs


def rule_area(name, layers, pts, tracks, vias):
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(b.GetLayerID(l))
    z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(tracks)
    z.SetDoNotAllowVias(vias)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowZoneFills(False)
    z.SetDoNotAllowFootprints(False)
    o = z.Outline()
    o.NewOutline()
    for x, y in pts:
        o.Append(MM(x), MM(y))
    z.SetUuid(pcbnew.KIID(str(uuid.uuid5(NS, name))))
    b.Add(z)
    return z


# D-PCB-7 v2: In1.Cu no tracks over the actual board outline (vias allowed).
outline = pcbnew.SHAPE_POLY_SET()
assert b.GetBoardPolygonOutlines(outline, False)
assert outline.OutlineCount() == 1 and outline.HoleCount(0) == 0
ch = outline.Outline(0)
edge = [(pcbnew.ToMM(ch.CPoint(i).x), pcbnew.ToMM(ch.CPoint(i).y)) for i in range(ch.PointCount())]
rule_area("D-PCB-7v2 In1.Cu no tracks (board outline)", ["In1.Cu"], edge, True, False)

# D-PCB-6: In1.Cu + In2.Cu no tracks, no vias, x 76..88, y 26.5..30.6 mm.
rule_area("D-PCB-6 RF reference keep-out", ["In1.Cu", "In2.Cu"],
          [(76, 26.5), (88, 26.5), (88, 30.6), (76, 30.6)], True, True)

assert pcbnew.SaveBoard(out, b)
print("outline", edge)
