"""inspect_rule_areas.py BOARD [RESAVE]: reload BOARD with pcbnew and print its rule areas as JSON.
With RESAVE, also save the reloaded board there (for a byte-identity round-trip check)."""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
ras = []
for z in b.Zones():
    if not z.GetIsRuleArea():
        continue
    o = z.Outline()
    ch = o.Outline(0)
    ras.append({
        "name": z.GetZoneName(), "uuid": z.m_Uuid.AsString(),
        "layers": [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
        "tracks_not_allowed": z.GetDoNotAllowTracks(), "vias_not_allowed": z.GetDoNotAllowVias(),
        "pads_not_allowed": z.GetDoNotAllowPads(), "copperpour_not_allowed": z.GetDoNotAllowZoneFills(),
        "footprints_not_allowed": z.GetDoNotAllowFootprints(),
        "outlines": o.OutlineCount(), "holes": o.HoleCount(0),
        "polygon_mm": [[pcbnew.ToMM(ch.CPoint(i).x), pcbnew.ToMM(ch.CPoint(i).y)] for i in range(ch.PointCount())],
        "area_mm2": round(o.Area() / 1e12, 6),
    })
print(json.dumps({"rule_areas": ras,
                  "zones_total": len(list(b.Zones())),
                  "copper_zones": [[z.GetNetname(), [b.GetLayerName(l) for l in z.GetLayerSet().Seq()]] for z in b.Zones() if not z.GetIsRuleArea()]}, indent=1))
if len(sys.argv) > 2:
    assert pcbnew.SaveBoard(sys.argv[2], b)
