"""For each starved_thermal pad: its other GND connections (tracks, vias, chain to a
via/plane), what crowds the relief, and whether the parent board had it too."""
import json, sys, re, math, collections
import pcbnew
D = sys.argv[1]
board = pcbnew.LoadBoard(f"{D}/new-oldrules/fome-mc.kicad_pcb")
new = json.load(open(f"{D}/drc-oldrules/new-oldrules-drc.json"))
old = json.load(open(f"{D}/old/drc/old-drc.json"))
def starved(rep):
    out = {}
    for v in rep["violations"]:
        if v["type"] != "starved_thermal":
            continue
        pad = v["items"][1]["description"]
        m = re.search(r"actual (\d+)", v["description"])
        out[pad] = int(m.group(1)) if m else None
    return out
s_new, s_old = starved(new), starved(old)
MM = 1e6
gnd = board.FindNet("GND").GetNetCode()
zones = [(z.GetNetname(), [board.GetLayerName(l) for l in z.GetLayerSet().Seq()], z.GetAssignedPriority()) for z in board.Zones() if not z.GetIsRuleArea()]
tracks = [t for t in board.GetTracks()]
gtracks = [t for t in tracks if t.GetNetCode() == gnd and not isinstance(t, pcbnew.PCB_VIA)]
gvias = [t for t in tracks if t.GetNetCode() == gnd and isinstance(t, pcbnew.PCB_VIA)]

def seg_dist(p, a, b):
    ax, ay, bx, by, px, py = a.x, a.y, b.x, b.y, p.x, p.y
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)

def chain(pad, layer):
    """BFS over GND tracks/vias from the pad, ignoring zones: vias and pads reached."""
    start = [t for t in gtracks if t.GetLayer() == layer and (pad.HitTest(t.GetStart()) or pad.HitTest(t.GetEnd()))]
    vias_in_pad = [v for v in gvias if pad.HitTest(v.GetPosition())]
    seen, frontier, vias, pads = set(), list(start), set(v.m_Uuid.AsString() for v in vias_in_pad), set()
    pts = []
    while frontier:
        t = frontier.pop()
        if t.m_Uuid.AsString() in seen:
            continue
        seen.add(t.m_Uuid.AsString())
        for p in (t.GetStart(), t.GetEnd()):
            for v in gvias:
                if v.GetPosition() == p or seg_dist(v.GetPosition(), p, p) < v.GetWidth(pcbnew.F_Cu) / 2:
                    if v.m_Uuid.AsString() not in vias:
                        vias.add(v.m_Uuid.AsString())
                        # continue on every layer the via reaches
                        frontier += [u for u in gtracks if (u.GetStart() == v.GetPosition() or u.GetEnd() == v.GetPosition())]
            frontier += [u for u in gtracks if u.GetLayer() == t.GetLayer() and (u.GetStart() == p or u.GetEnd() == p)]
            for fp in board.GetFootprints():
                for q in fp.Pads():
                    if q.GetNetCode() == gnd and q is not pad and q.IsOnLayer(t.GetLayer()) and q.HitTest(p):
                        pads.add(f"{fp.GetReference()}.{q.GetNumber()}")
    return len(start), len(vias_in_pad), len(vias), sorted(pads), len(seen)

rows = []
for desc, spokes in sorted(s_new.items()):
    m = re.match(r"Pad (\S+) \[GND\] of (\S+) on (\S+)", desc)
    num, ref, lname = m.groups()
    fp = board.FindFootprintByReference(ref)
    pad = next(p for p in fp.Pads() if p.GetNumber() == num)
    layer = board.GetLayerID(lname)
    n_tr, n_vip, n_vias, pads, n_seen = chain(pad, layer)
    c = pad.GetPosition()
    sz = pad.GetSize(layer) if hasattr(pad, "GetSize") else None
    half = max(sz.x, sz.y) / 2 if sz else 0
    near = []
    for t in tracks:
        if isinstance(t, pcbnew.PCB_VIA):
            if t.GetNetCode() != gnd and t.IsOnLayer(layer):
                d = math.hypot(t.GetPosition().x - c.x, t.GetPosition().y - c.y) - t.GetWidth(layer) / 2 - half
                if d < 0.8 * MM:
                    near.append((round(d / MM, 2), "via " + t.GetNetname()))
        elif t.GetLayer() == layer and t.GetNetCode() != gnd:
            d = seg_dist(c, t.GetStart(), t.GetEnd()) - t.GetWidth() / 2 - half
            if d < 0.8 * MM:
                near.append((round(d / MM, 2), t.GetNetname()))
    near = sorted(set(near))[:3]
    zc = {0: "inherited", 1: "none", 2: "thermal", 3: "solid", 4: "thermal_tht"}.get(int(pad.GetLocalZoneConnection()), str(pad.GetLocalZoneConnection()))
    rows.append({"pad": f"{ref}.{num}", "value": fp.GetValue(), "footprint": fp.GetFPIDAsString().split(":")[-1],
                 "layer": lname, "spokes": spokes, "in_parent": desc in s_old,
                 "gnd_tracks_on_pad": n_tr, "via_in_pad": n_vip, "gnd_vias_reached": n_vias,
                 "gnd_pads_reached": pads[:6], "pad_zone_connection": zc,
                 "crowding": near})
json.dump({"zones": zones, "pads": rows, "parent_only": sorted(set(s_old) - set(s_new))}, open(f"{D}/thermal-pads.json", "w"), indent=1)
print("zones:", zones)
for r in rows:
    print(json.dumps(r))
print("parent-only starved:", sorted(set(s_old) - set(s_new)))
