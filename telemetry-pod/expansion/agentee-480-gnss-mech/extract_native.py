#!/usr/bin/python3
"""Read one saved PCB through pcbnew; write observations, never a PCB.

Use native-admit. The JSON is an observation transport for check_constraints.py,
not a replacement for native ERC/DRC or an electrical/physical qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pcbnew as k


def xy(point):
    return [point.x / 1e6, point.y / 1e6]


def polyset(poly):
    def ring(chain):
        return [xy(chain.CPoint(i)) for i in range(chain.PointCount())]
    return [{"shell": ring(poly.COutline(i)),
             "holes": [ring(poly.CHole(i, h)) for h in range(poly.HoleCount(i))]}
            for i in range(poly.OutlineCount())]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(board_path, terminal_path):
    before = digest(board_path)
    board = k.LoadBoard(str(board_path))
    if not board.BuildConnectivity():
        raise ValueError("native connectivity build failed")
    terminal = json.loads(terminal_path.read_text())
    if terminal["status"] != "PASS" or terminal["board_sha256_before"] != before or terminal["board_sha256_after"] != before:
        raise ValueError("verified native terminal receipt does not match this saved board")
    footprints = []
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        pads = []
        for p in fp.Pads():
            pad = {"number": p.GetNumber(), "uuid": p.m_Uuid.AsString(),
                   "net": p.GetNetname(), "at_mm": xy(p.GetPosition()),
                   "size_mm": xy(p.GetSize()), "drill_mm": xy(p.GetDrillSize()),
                   "orientation_deg": p.GetOrientationDegrees(),
                   "shape": int(p.GetShape()), "attribute": int(p.GetAttribute()),
                   "layers": [board.GetLayerName(l) for l in p.GetLayerSet().Seq()]}
            if fp.GetReference() in {"U3", "L3", "D3", "C42", "J2"}:
                pad["copper_polygons"] = {board.GetLayerName(l): polyset(p.GetEffectivePolygon(l))
                                          for l in [k.F_Cu, k.In1_Cu, k.In2_Cu, k.B_Cu]
                                          if p.IsOnLayer(l)}
            pads.append(pad)
        footprints.append({"reference": fp.GetReference(), "uuid": fp.m_Uuid.AsString(),
                           "lib_id": fp.GetFPID().GetUniStringLibId(), "value": fp.GetValue(),
                           "face": fp.GetLayerName(), "at_mm": xy(fp.GetPosition()),
                           "rotation_deg": fp.GetOrientationDegrees(), "pads": pads,
                           "courtyards": {board.GetLayerName(l): polyset(fp.GetCourtyard(l))
                                          for l in [k.F_CrtYd, k.B_CrtYd]}})
    tracks = []
    for t in board.GetTracks():
        via = isinstance(t, k.PCB_VIA)
        record = {"uuid": t.m_Uuid.AsString(), "net": t.GetNetname(),
                  "kind": "via" if via else "track", "layer": t.GetLayerName(),
                  "layers": [board.GetLayerName(l) for l in t.GetLayerSet().Seq()],
                  "start_mm": xy(t.GetStart()), "end_mm": xy(t.GetEnd()),
                  "width_mm": (t.GetWidth(k.F_Cu) if via else t.GetWidth()) / 1e6}
        if t.GetNetname() == "/POD_GNSS_RF" or t.GetLayer() == k.In1_Cu:
            shape = k.SHAPE_POLY_SET()
            # 1 nm polygonization error is a numerical representation bound,
            # not a physical clearance or a fit allowance.
            t.TransformShapeToPolygon(shape, k.F_Cu if via else t.GetLayer(),
                                      0, 1, k.ERROR_INSIDE)
            record["copper_polygons"] = polyset(shape)
        tracks.append(record)
    zones = []
    for z in board.Zones():
        zones.append({"uuid": z.m_Uuid.AsString(), "name": z.GetZoneName(),
                      "net": z.GetNetname(), "layers": [board.GetLayerName(l) for l in z.GetLayerSet().Seq()],
                      "rule_area": z.GetIsRuleArea(), "outline": polyset(z.Outline()),
                      "forbid": {"tracks": z.GetDoNotAllowTracks(), "vias": z.GetDoNotAllowVias(),
                                 "pads": z.GetDoNotAllowPads(), "footprints": z.GetDoNotAllowFootprints(),
                                 "copper_pours": z.GetDoNotAllowZoneFills()},
                      "saved_in1_fill": polyset(z.GetFilledPolysList(k.In1_Cu))
                      if z.IsOnLayer(k.In1_Cu) and not z.GetIsRuleArea() else []})
    project = board_path.with_suffix(".kicad_pro")
    result = {"schema": "agentee-480.native-observation/1", "pcbnew_version": k.Version(),
              "board_path": str(board_path), "board_sha256": before,
              "project_sha256": digest(project), "project": json.loads(project.read_text()),
              "copper_layers": board.GetCopperLayerCount(),
              "board_thickness_mm": board.GetDesignSettings().GetBoardThickness() / 1e6,
              "edges": [{"start_mm": xy(e.GetStart()), "end_mm": xy(e.GetEnd()),
                         "shape": int(e.GetShape())}
                        for e in board.GetDrawings() if e.GetLayer() == k.Edge_Cuts],
              "footprints": footprints, "tracks": tracks, "zones": zones}
    after = digest(board_path)
    if before != after:
        raise RuntimeError("source PCB changed during extraction")
    result["unchanged_board_sha256"] = after
    native_inventory = {p["uuid"]: {"net": p["net"], "number": p["number"], "footprint": f["uuid"]}
                        for f in footprints for p in f["pads"]}
    if native_inventory != terminal["inventory"]:
        raise ValueError("native pad/net inventory differs from the independently serialized-verified receipt")
    result["native_terminals"] = {"status": terminal["status"], "board_sha256": before,
                                  "source_path": str(terminal_path), "source_sha256": digest(terminal_path),
                                  "method": terminal["method"], "identity": terminal["identity"],
                                  "nets": {n: terminal["nets"][n] for n in ["/POD_GNSS_RF", "/GND"]}}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("terminal_receipt", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(extract(args.board, args.terminal_receipt), indent=2) + "\n")
