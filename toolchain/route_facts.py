#!/usr/bin/env python3
"""Extract the engineering content of a KiCad board as JSON, for preservation checks.

    route_facts.py BOARD.kicad_pcb OUT.json

Runs with a Python that can import KiCad's `pcbnew` (the toolchain venv or
/usr/bin/python3). Everything is read through KiCad's own loader, so two boards
that serialise differently but mean the same thing produce the same facts. All
lengths are integer nanometres (KiCad internal units); angles are degrees.

The project rules (.kicad_pro, .kicad_dru) are compared as files by route.py;
this script covers what lives in the board: outline, layers, stackup, setup,
footprints and pads, nets and their resolved net classes, zones and rule areas,
tracks/arcs/vias (with lock state) and other copper graphics.
"""
import hashlib
import json
import re
import sys
from pathlib import Path


def sexpr(text):
    """Minimal s-expression reader: nested lists of atoms (strings keep quotes off)."""
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()"]+', text)
    stack, cur = [], []
    for t in tokens:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    return cur


def find(node, key):
    for child in node:
        if isinstance(child, list) and child and child[0] == key:
            return child
    return None


def setup_block(text):
    """The board's (setup ...) section as a tree, minus volatile/non-engineering keys."""
    start = text.find("\n\t(setup")
    if start < 0:
        return None
    depth, i = 0, start + 1
    for j in range(i, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                tree = sexpr(text[i:j + 1])[0]
                # plot parameters are output settings, not engineering constraints
                return [c for c in tree if not (isinstance(c, list) and c and c[0] == "pcbplotparams")]
    return None


def main(board_path, out_path):
    import pcbnew

    board_path = Path(board_path)
    board = pcbnew.LoadBoard(str(board_path))
    text = board_path.read_text()

    def xy(v):
        return [int(v.x), int(v.y)]

    def layer_name(layer):
        return board.GetLayerName(layer)

    def layer_names(lset):
        return sorted(board.GetLayerName(l) for l in lset.Seq())

    facts = {"kicad_version": pcbnew.GetBuildVersion(), "board": board_path.name}
    VIA_TYPES = {pcbnew.VIATYPE_THROUGH: "through", pcbnew.VIATYPE_BLIND: "blind",
                 pcbnew.VIATYPE_BURIED: "buried", pcbnew.VIATYPE_MICROVIA: "micro"}

    enabled = board.GetEnabledLayers()
    facts["copper_layer_count"] = board.GetCopperLayerCount()
    facts["enabled_layers"] = layer_names(enabled)
    facts["copper_layers"] = [{"name": board.GetLayerName(l), "type": int(board.GetLayerType(l))}
                              for l in enabled.CuStack()]
    setup = setup_block(text)
    facts["stackup"] = find(setup, "stackup") if setup else None
    facts["setup"] = [c for c in setup if not (isinstance(c, list) and c and c[0] == "stackup")] if setup else None

    # Board outline: every Edge.Cuts shape, board-level and footprint-owned.
    outline = []

    def shape_record(s):
        rec = {"shape": s.ShowShape(), "layer": layer_name(s.GetLayer()), "width": int(s.GetWidth())}
        st = s.GetShape()
        if st == pcbnew.SHAPE_T_POLY:
            poly = s.GetPolyShape()
            rec["points"] = [[int(poly.CVertex(i).x), int(poly.CVertex(i).y)] for i in range(poly.TotalVertices())]
        elif st == pcbnew.SHAPE_T_CIRCLE:
            rec.update(center=xy(s.GetCenter()), radius=int(s.GetRadius()))
        elif st == pcbnew.SHAPE_T_ARC:
            rec.update(start=xy(s.GetStart()), mid=xy(s.GetArcMid()), end=xy(s.GetEnd()))
        else:
            ends = sorted([xy(s.GetStart()), xy(s.GetEnd())])
            rec.update(start=ends[0], end=ends[1])
        return rec

    copper_graphics = []
    for d in board.GetDrawings():
        if not isinstance(d, pcbnew.PCB_SHAPE):
            if d.IsOnCopperLayer():
                copper_graphics.append({"class": d.GetClass(), "layer": layer_name(d.GetLayer())})
            continue
        if d.GetLayer() == pcbnew.Edge_Cuts:
            outline.append(shape_record(d))
        elif d.IsOnCopperLayer():
            rec = shape_record(d)
            rec["net"] = d.GetNetname()
            copper_graphics.append(rec)
    footprints = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for item in fp.GraphicalItems():
            if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.Edge_Cuts:
                rec = shape_record(item)
                rec["footprint"] = ref
                outline.append(rec)
        pads = {}
        for pad in fp.Pads():
            key = pad.GetNumber() or f"<unnumbered@{pad.GetPosition().x},{pad.GetPosition().y}>"
            while key in pads:
                key += "'"
            pads[key] = {
                "position": xy(pad.GetPosition()), "net": pad.GetNetname(),
                "size": xy(pad.GetSize(pcbnew.F_Cu)) if hasattr(pad, "GetSize") else None,
                "drill": xy(pad.GetDrillSize()), "attribute": int(pad.GetAttribute()),
                "layers": layer_names(pad.GetLayerSet()),
            }
        footprints[ref] = {
            "fpid": fp.GetFPIDAsString(), "value": fp.GetValue(),
            "position": xy(fp.GetPosition()), "orientation": round(fp.GetOrientationDegrees(), 6),
            "layer": layer_name(fp.GetLayer()), "locked": bool(fp.IsLocked()),
            "path": fp.GetPath().AsString(), "pads": dict(sorted(pads.items())),
        }
    facts["outline"] = sorted(outline, key=lambda r: json.dumps(r, sort_keys=True))
    facts["copper_graphics"] = sorted(copper_graphics, key=lambda r: json.dumps(r, sort_keys=True))
    facts["footprints"] = dict(sorted(footprints.items()))

    nets = {}
    net_settings = board.GetDesignSettings().m_NetSettings
    for name, net in board.GetNetsByName().items():
        name = str(name)
        if not name:
            continue
        nc = net_settings.GetEffectiveNetClass(name)
        nets[name] = {"netclass": nc.GetName(),
                      "track_width": int(nc.GetTrackWidth()) if nc.HasTrackWidth() else None,
                      "clearance": int(nc.GetClearance()) if nc.HasClearance() else None,
                      "via_diameter": int(nc.GetViaDiameter()) if nc.HasViaDiameter() else None,
                      "via_drill": int(nc.GetViaDrill()) if nc.HasViaDrill() else None}
    facts["nets"] = dict(sorted(nets.items()))

    zones, rule_areas = [], []
    for z in board.Zones():
        poly = z.Outline()
        outline_pts = [[int(poly.CVertex(i).x), int(poly.CVertex(i).y)] for i in range(poly.TotalVertices())]
        rec = {"name": z.GetZoneName(), "layers": layer_names(z.GetLayerSet()), "outline": outline_pts}
        if z.GetIsRuleArea():
            rec.update(no_tracks=z.GetDoNotAllowTracks(), no_vias=z.GetDoNotAllowVias(),
                       no_pads=z.GetDoNotAllowPads(), no_footprints=z.GetDoNotAllowFootprints(),
                       no_zone_fills=z.GetDoNotAllowZoneFills())
            rule_areas.append(rec)
        else:
            rec.update(net=z.GetNetname(), priority=int(z.GetAssignedPriority()),
                       clearance=int(z.GetLocalClearance()) if z.GetLocalClearance() is not None else None,
                       min_thickness=int(z.GetMinThickness()), pad_connection=int(z.GetPadConnection()),
                       thermal_gap=int(z.GetThermalReliefGap()),
                       thermal_spoke=int(z.GetThermalReliefSpokeWidth()),
                       fill_mode=int(z.GetFillMode()), island_removal=int(z.GetIslandRemovalMode()),
                       locked=bool(z.IsLocked()), filled=bool(z.IsFilled()))
            zones.append(rec)
    facts["zones"] = sorted(zones, key=lambda r: json.dumps(r, sort_keys=True))
    facts["rule_areas"] = sorted(rule_areas, key=lambda r: json.dumps(r, sort_keys=True))

    tracks, vias = [], []
    for t in board.GetTracks():
        locked = bool(t.IsLocked())
        if isinstance(t, pcbnew.PCB_VIA):
            vias.append({"position": xy(t.GetPosition()), "diameter": int(t.GetWidth(pcbnew.F_Cu)),
                         "drill": int(t.GetDrillValue()), "via_type": VIA_TYPES.get(int(t.GetViaType()), "unknown"),
                         "layers": [layer_name(t.TopLayer()), layer_name(t.BottomLayer())],
                         "net": t.GetNetname(), "locked": locked, "uuid": t.m_Uuid.AsString()})
        else:
            a, b = xy(t.GetStart()), xy(t.GetEnd())
            rec = {"kind": "arc" if isinstance(t, pcbnew.PCB_ARC) else "segment",
                   "layer": layer_name(t.GetLayer()), "width": int(t.GetWidth()), "net": t.GetNetname(),
                   "locked": locked, "uuid": t.m_Uuid.AsString()}
            if rec["kind"] == "arc":
                rec.update(start=a, mid=xy(t.GetMid()), end=b)
            else:
                a, b = sorted([a, b])
                rec.update(start=a, end=b)
            tracks.append(rec)
    facts["tracks"] = tracks
    facts["vias"] = vias
    facts["netclass_count"] = len({n["netclass"] for n in nets.values()})
    facts["sha256"] = hashlib.sha256(board_path.read_bytes()).hexdigest()
    Path(out_path).write_text(json.dumps(facts, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
