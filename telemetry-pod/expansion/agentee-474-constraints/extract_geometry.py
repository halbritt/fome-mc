#!/usr/bin/python3
"""Read-only native geometry inventory for the exact ROUTE-3 candidate.

Run from the repository root with /usr/bin/python3. No SaveBoard, refill,
routing, geometry edits, or DRC invocation occurs here.
"""
import hashlib
import json
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BOARD = ROOT / "telemetry-pod/expansion/route-3/candidate/telemetry-pod.kicad_pcb"
EXPECTED = "0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xy(p):
    return [p.x / 1e6, p.y / 1e6]


def polygons(poly):
    return [[xy(poly.COutline(i).CPoint(j))
             for j in range(poly.COutline(i).PointCount())]
            for i in range(poly.OutlineCount())]


def bounds(polys):
    points = [p for poly in polys for p in poly]
    if not points:
        return None
    return [min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points)]


assert sha(BOARD) == EXPECTED, "wrong candidate: stop"
board = pcbnew.LoadBoard(str(BOARD))
allocation_path = ROOT / "telemetry-pod/expansion/blocks/allocation.json"
allocation = json.loads(allocation_path.read_text())
membership = {}
for block in allocation["blocks"]:
    for ref in block["references"]:
        assert ref not in membership
        membership[ref] = block["id"]
for ref in allocation["residual"]:
    assert ref not in membership
    membership[ref] = "residual (existing allocation; not a functional-role qualification)"

footprints = []
rule_areas = []
for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
    ref = fp.GetReference()
    courts = {}
    for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        poly = polygons(fp.GetCourtyard(layer))
        courts[board.GetLayerName(layer)] = {"polygons_mm": poly, "bbox_mm": bounds(poly)}
    pads = [{"number": p.GetNumber(), "uuid": p.m_Uuid.AsString(),
             "at_mm": xy(p.GetPosition()), "size_mm": xy(p.GetSize()),
             "drill_mm": xy(p.GetDrillSize()), "net": p.GetNetname(),
             "layers": [board.GetLayerName(l) for l in p.GetLayerSet().Seq()]}
            for p in fp.Pads()]
    props = {f.GetName(): f.GetText() for f in fp.GetFields()}
    height_fields = {k: v for k, v in props.items() if "height" in k.lower()}
    footprints.append({"reference": ref, "uuid": fp.m_Uuid.AsString(),
                       "value": fp.GetValue(), "footprint": fp.GetFPID().GetUniStringLibId(),
                       "at_mm": xy(fp.GetPosition()), "rotation_deg": fp.GetOrientationDegrees(),
                       "face": fp.GetLayerName(), "locked": fp.IsLocked(),
                       "existing_block": membership.get(ref, "UNASSIGNED in existing allocation"),
                       "courtyards": courts, "pads": pads,
                       "height_fields": height_fields,
                       "height_qualification": "UNKNOWN: fields/models are not independently verified height evidence"})
    for zone in fp.Zones():
        if zone.GetIsRuleArea():
            rule_areas.append((ref, zone))
for zone in board.Zones():
    if zone.GetIsRuleArea():
        rule_areas.append(("board", zone))
rules = []
for owner, zone in rule_areas:
    poly = polygons(zone.Outline())
    rules.append({"owner": owner, "name": zone.GetZoneName(), "uuid": zone.m_Uuid.AsString(),
                  "layers": [board.GetLayerName(l) for l in zone.GetLayerSet().Seq()],
                  "polygon_mm": poly, "bbox_mm": bounds(poly),
                  "forbid": {"tracks": zone.GetDoNotAllowTracks(), "vias": zone.GetDoNotAllowVias(),
                             "pads": zone.GetDoNotAllowPads(), "footprints": zone.GetDoNotAllowFootprints(),
                             "copper_pours": zone.GetDoNotAllowZoneFills()}})
rf_tracks = []
for track in board.GetTracks():
    if "RF" in track.GetNetname().upper() or "GNSS" in track.GetNetname().upper():
        is_via = isinstance(track, pcbnew.PCB_VIA)
        rf_tracks.append({"uuid": track.m_Uuid.AsString(), "net": track.GetNetname(),
                          "kind": "via" if is_via else "track",
                          "layer": track.GetLayerName(), "start_mm": xy(track.GetStart()),
                          "end_mm": xy(track.GetEnd()),
                          "width_mm": (track.GetWidth(pcbnew.F_Cu) if is_via else track.GetWidth()) / 1e6})
edge = [{"start_mm": xy(d.GetStart()), "end_mm": xy(d.GetEnd()), "shape": int(d.GetShape())}
        for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
result = {"schema": "agentee-474.native-geometry/1", "board": str(BOARD.relative_to(ROOT)),
          "board_sha256": EXPECTED, "pcbnew_version": pcbnew.Version(),
          "board_thickness_mm": board.GetDesignSettings().GetBoardThickness() / 1e6,
          "copper_layer_count": board.GetCopperLayerCount(), "edges": edge,
          "footprint_count": len(footprints), "allocation": str(allocation_path.relative_to(ROOT)),
          "allocation_sha256": sha(allocation_path), "footprints": footprints,
          "rule_areas": rules, "rf_named_tracks": rf_tracks,
          "read_only_board_hash_after": sha(BOARD)}
assert result["read_only_board_hash_after"] == EXPECTED
(OUT / "native-geometry.json").write_text(json.dumps(result, indent=2) + "\n")
summary = {"board_sha256": EXPECTED, "footprints": len(footprints),
           "face_counts": {face: sum(f["face"] == face for f in footprints) for face in ["F.Cu", "B.Cu"]},
           "rule_areas": rules,
           "anchors": [f for f in footprints if f["reference"] in ["H1", "H2", "H3", "H4", "J1", "J2", "J3", "U1", "U2", "U3"]],
           "test_points": [f for f in footprints if f["reference"].startswith("TP")],
           "height_fields_present": [f["reference"] for f in footprints if f["height_fields"]],
           "unassigned_existing_allocation": [f["reference"] for f in footprints if f["existing_block"].startswith("UNASSIGNED")]}
(OUT / "geometry-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"board_sha256": EXPECTED, "footprints": len(footprints), "rule_areas": len(rules),
                  "face_counts": summary["face_counts"], "unassigned": summary["unassigned_existing_allocation"]}))
