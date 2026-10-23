#!/usr/bin/python3
"""Artifact-only data rebinding and conservative checks, with explicit failures.

derive OBS OUT: materialize component/edge-relative GNSS and access definitions.
check OBS DEF OUT: reject stale definitions; assess the saved RF copper/fill.
No production imports, planner integration, board editing or routing occurs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, mapping
from shapely.ops import polygonize, unary_union

RF_PADS = [("U3", "11"), ("L3", "2"), ("D3", "1"), ("J2", "1")]
BOUND_PADS = RF_PADS + [("L3", "1"), ("D3", "2"), ("C42", "1"), ("C42", "2")]
NETS = {"U3.11": "/POD_GNSS_RF", "L3.2": "/POD_GNSS_RF", "D3.1": "/POD_GNSS_RF",
        "J2.1": "/POD_GNSS_RF", "L3.1": "/ANT_BIAS", "D3.2": "/GND",
        "C42.1": "/ANT_BIAS", "C42.2": "/GND"}


def hashed(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify_saved_source(obs):
    if obs.get("synthetic_control_only"):
        raise ValueError("SYNTHETIC_CONTROL_IS_NOT_SAVED_BOARD_EVIDENCE")
    board = Path(obs["board_path"])
    if not board.is_absolute():
        board = Path(__file__).resolve().parents[3] / board
    if hashlib.sha256(board.read_bytes()).hexdigest() != obs["board_sha256"]:
        raise ValueError("STALE_NATIVE_OBSERVATION_REEXTRACT_REQUIRED")
    if hashlib.sha256(board.with_suffix(".kicad_pro").read_bytes()).hexdigest() != obs["project_sha256"]:
        raise ValueError("STALE_PROJECT_REEXTRACT_REQUIRED")
    receipt = Path(obs["native_terminals"]["source_path"])
    if not receipt.is_absolute():
        receipt = Path(__file__).resolve().parents[3] / receipt
    receipt_bytes = receipt.read_bytes()
    if hashlib.sha256(receipt_bytes).hexdigest() != obs["native_terminals"]["source_sha256"]:
        raise ValueError("NATIVE_TERMINAL_RECEIPT_IDENTITY_CHANGED")
    original = json.loads(receipt_bytes)
    if obs["native_terminals"]["nets"] != {n: original["nets"][n] for n in ["/POD_GNSS_RF", "/GND"]}:
        raise ValueError("NATIVE_TERMINAL_GROUPS_CHANGED")


def geometry(polys):
    shapes = [Polygon(p["shell"], p["holes"]) for p in polys]
    if any(not p.is_valid for p in shapes):
        raise ValueError("invalid native polygon; no automatic repair")
    return unary_union(shapes)


def footprints(obs):
    result = {f["reference"]: f for f in obs["footprints"]}
    if len(result) != len(obs["footprints"]):
        raise ValueError("duplicate footprint references")
    return result


def pad(fps, ref, number):
    matches = [p for p in fps[ref]["pads"] if p["number"] == number]
    if len(matches) != 1:
        raise ValueError(f"expected one bound pad {ref}.{number}; got {len(matches)}")
    return matches[0]


def binding(obs):
    fps = footprints(obs)
    selected = []
    for ref, number in BOUND_PADS:
        f, p = fps[ref], pad(fps, ref, number)
        if p["net"] != NETS[ref + "." + number]:
            raise ValueError(f"topology mismatch on {ref}.{number}: {p['net']}")
        if f["face"] != "F.Cu":
            raise ValueError(f"F-over-In1 topology requires {ref} on F; found {f['face']}")
        selected.append({"reference": ref, "number": number, "fp_uuid": f["uuid"],
                         "lib_id": f["lib_id"], "pose_mm_deg": [*f["at_mm"], f["rotation_deg"]],
                         "pad": p})
    return {"pads": selected, "edges": obs["edges"], "project_sha256": obs["project_sha256"],
            "copper_layers": obs["copper_layers"], "thickness_mm": obs["board_thickness_mm"]}


def derive(obs):
    fps = footprints(obs)
    bound = binding(obs)
    points = {r + "." + n: pad(fps, r, n)["at_mm"] for r, n in BOUND_PADS}
    if obs["copper_layers"] != 4:
        raise ValueError("this reference definition binds the four-layer F/In1/In2/B stack")
    # Inherited engineering RF width, not a new margin or an impedance proof.
    width = 0.335
    default_class = next(c for c in obs["project"]["net_settings"]["classes"] if c["name"] == "Default")
    clearance = default_class["clearance"]
    radius = width / 2 + clearance
    u3 = fps["U3"]
    theta = math.radians(u3["rotation_deg"])
    # U3's RF pin is on its local left edge. Cardinal rotations are explicit;
    # non-cardinal poses are unsupported by this initial L-corridor proposal.
    normal = [-round(math.cos(theta)), -round(math.sin(theta))]
    if abs(u3["rotation_deg"] / 90 - round(u3["rotation_deg"] / 90)) > 1e-9:
        raise ValueError("non-cardinal U3 rotation needs a reviewed corridor definition")
    court = geometry(u3["courtyards"]["F.Courtyard"])
    xmin, ymin, xmax, ymax = court.bounds
    rf, sma = points["U3.11"], points["J2.1"]
    if fps["J2"]["rotation_deg"] % 360 != 180:
        raise ValueError("this right-edge J2 datum binds rotation180; a different launch case needs a reviewed source binding")
    if normal[0]:
        escape = [(xmin - radius) if normal[0] < 0 else (xmax + radius), rf[1]]
        elbow = [escape[0], sma[1]]
    else:
        escape = [rf[0], (ymin - radius) if normal[1] < 0 else (ymax + radius)]
        elbow = [sma[0], escape[1]]
    main = [rf, escape, elbow, sma]
    # D3 and L3 are shunt/bias taps, not series RF elements; C42 is bias bypass.
    branches = [[points["D3.1"], escape], [points["L3.2"], escape]]
    lines = [LineString(main)] + [LineString(p) for p in branches]
    reserved = unary_union([line.buffer(radius, cap_style=2, join_style=2) for line in lines])
    reserved = reserved.union(unary_union([geometry(pad(fps, r, n)["copper_polygons"]["F.Cu"])
                                         for r, n in RF_PADS]))
    edge_x = max(p[0] for e in obs["edges"] for p in [e["start_mm"], e["end_mm"]])
    # J2 pin copper ends 0.50 mm inboard of the footprint's edge datum (D-PCB-4).
    j2 = pad(fps, "J2", "1")
    datum = geometry(j2["copper_polygons"]["F.Cu"]).bounds[2] + 0.50
    return {"schema": "agentee-480.gnss-reference/1", "status": "PROVISIONAL_PROPOSAL",
            "observed_board_sha256": obs["board_sha256"], "binding": bound,
            "binding_sha256": hashed(bound),
            "relative_recipe": {"main": "U3.11 -> outside U3 F courtyard along local-left -> elbow at J2.1 ordinate -> J2.1",
                                "shunt_taps": ["D3.1", "L3.2"],
                                "bias_branch": "C42.1 ANT_BIAS -> L3.1; C42.2 and D3.2 GND",
                                "j2_edge": "pin1 copper max-x + D-PCB-4 datum0.50 = right Edge.Cuts",
                                "regenerate": "derive from the new saved-board observation; never copy materialized XY"},
            "rf_width_mm": width, "rf_width_class": "inherited engineering calculation; design-rules/constraints.json:96-98",
            "existing_clearance_mm": clearance, "clearance_class": "existing Default class; no new margin",
            "main_polyline_mm": main, "tap_polylines_mm": branches,
            "reference_exclusion": mapping(reserved),
            "final_reference_mask_recipe": "union this pose-derived proposal with the actual saved RF-copper projection; final native rule must cover both",
            "reference_layers": ["In1.Cu", "In2.Cu"], "forbid": ["tracks", "vias"],
            "signal_layer": "F.Cu", "ground_reference_layer": "In1.Cu", "ground_net": "/GND",
            "j2_edge_datum_error_mm": datum - edge_x,
            "legacy_baseline": {"polygon_mm": [[76, 26.5], [88, 26.5], [88, 30.6], [76, 30.6]],
                                "source_pad_mm": [77.5, 29.1], "status": "historical only; not deleted or changed"},
            "plane_rule": {"region": "current Edge.Cuts", "layer": "In1.Cu", "forbid_tracks": True,
                           "vias_elsewhere": "allowed subject to local/native rules; RF mask separately forbids vias"}}


def assess_rf(obs, definition):
    current = binding(obs)
    if hashed(current) != definition["binding_sha256"] or current != definition["binding"]:
        return {"status": "FAIL", "code": "STALE_BINDING", "geometry_check": "NOT_RUN"}
    if obs["board_sha256"] != definition["observed_board_sha256"]:
        return {"status": "FAIL", "code": "BOARD_IDENTITY_CHANGED_REDERIVE_REQUIRED", "geometry_check": "NOT_RUN"}
    if hashed(derive(obs)) != hashed(definition):
        return {"status": "FAIL", "code": "DEFINITION_CHANGED_REDERIVE_REQUIRED", "geometry_check": "NOT_RUN"}
    fps = footprints(obs)
    tracks = [t for t in obs["tracks"] if t["net"] == "/POD_GNSS_RF"]
    rf_pads = [geometry(pad(fps, r, n)["copper_polygons"]["F.Cu"]) for r, n in RF_PADS]
    if any(p.geom_type != "Polygon" or p.is_empty for p in rf_pads):
        raise ValueError("each bound RF terminal must be one nonempty copper polygon")
    f_tracks = [t for t in tracks if t["kind"] == "track" and t["layer"] == "F.Cu"]
    copper = unary_union(rf_pads + [geometry(t["copper_polygons"]) for t in f_tracks])
    components = list(copper.geoms) if copper.geom_type == "MultiPolygon" else [copper]
    # Electrical terminal membership uses an interior witness in each connected
    # pad. Requiring exact boundary containment after GEOS union creates false
    # failures at floating-point noding vertices even for a single component.
    connected = any(all(component.covers(p.representative_point()) for p in rf_pads)
                    for component in components)
    wrong_layers = [t["uuid"] for t in tracks if t["kind"] == "via" or t["layer"] != "F.Cu"]
    narrow = [t["uuid"] for t in f_tracks if t["width_mm"] < definition["rf_width_mm"]]
    ground = unary_union([geometry(z["saved_in1_fill"]) for z in obs["zones"]
                          if not z["rule_area"] and z["net"] == definition["ground_net"]])
    ground_components = list(ground.geoms) if ground.geom_type == "MultiPolygon" else [ground]
    continuous_reference = not ground.is_empty and any(g.covers(copper) for g in ground_components)
    terminal = obs["native_terminals"]
    if terminal["status"] != "PASS" or terminal["board_sha256"] != obs["board_sha256"]:
        raise ValueError("native terminal evidence is not bound to the observed board")
    required_returns = {p["uuid"] for ref in ["U3", "J2", "D3", "C42"] for p in fps[ref]["pads"]
                        if p["net"] == "/GND"}
    return_group = next((set(g) for g in terminal["nets"]["/GND"] if required_returns.issubset(g)), None)
    required_rf = {pad(fps, r, n)["uuid"] for r, n in RF_PADS}
    native_rf_connected = any(required_rf.issubset(g) for g in map(set, terminal["nets"]["/POD_GNSS_RF"]))
    reference_witness = False
    if return_group:
        witness_pads = [p for ref in ["U3", "J2", "D3", "C42"] for p in fps[ref]["pads"]
                        if p["uuid"] in return_group and "In1.Cu" in p.get("copper_polygons", {})]
        reference_witness = any(g.covers(copper) and any(g.intersects(geometry(p["copper_polygons"]["In1.Cu"]))
                                                      for p in witness_pads) for g in ground_components)
    from shapely.geometry import shape
    mask = shape(definition["reference_exclusion"])
    rf_rules = [z for z in obs["zones"] if z["rule_area"] and
                {"In1.Cu", "In2.Cu"}.issubset(z["layers"]) and z["forbid"]["tracks"] and z["forbid"]["vias"]]
    rule_bound = bool(rf_rules) and unary_union([geometry(z["outline"]) for z in rf_rules]).covers(mask.union(copper))
    in1_tracks = [t["uuid"] for t in obs["tracks"] if t["kind"] == "track" and t["layer"] == "In1.Cu"]
    outline_polygons = list(polygonize([LineString([e["start_mm"], e["end_mm"]]) for e in obs["edges"]]))
    if len(outline_polygons) != 1 or any(e["shape"] != 0 for e in obs["edges"]):
        raise ValueError("outline check requires one closed line-segment outline; arcs/cutouts need native extension")
    outline = outline_polygons[0]
    plane_rules = [z for z in obs["zones"] if z["rule_area"] and set(z["layers"]) == {"In1.Cu"}
                   and z["forbid"]["tracks"] and not z["forbid"]["vias"]]
    plane_bound = bool(plane_rules) and unary_union([geometry(z["outline"]) for z in plane_rules]).covers(outline)
    # Check both the reserved future corridor and the actual RF projection.
    protected = mask.union(copper)
    incursion_vias = [t["uuid"] for t in obs["tracks"] if t["kind"] == "via" and
                     {"In1.Cu", "In2.Cu"}.intersection(t["layers"]) and
                     protected.intersects(Point(t["start_mm"]).buffer(t["width_mm"] / 2))]
    inner_tracks = [t["uuid"] for t in obs["tracks"] if t["kind"] == "track" and
                    t["layer"] in ["In1.Cu", "In2.Cu"] and
                    protected.intersects(LineString([t["start_mm"], t["end_mm"]]).buffer(t["width_mm"] / 2))]
    flags = {"F_only_RF_connectivity": connected, "RF_net_has_no_vias_or_non_F_tracks": not wrong_layers,
             "native_RF_terminal_equivalence": native_rf_connected,
             "native_U3_J2_D3_C42_returns_one_group": return_group is not None,
             "In1_reference_touches_that_native_return_group": reference_witness,
             "inherited_RF_min_width": not narrow, "one_saved_GND_In1_component_covers_actual_RF": continuous_reference,
             "pose_bound_reference_rule_covers_proposal": rule_bound,
             "In1_no_tracks_vias_allowed_rule_covers_outline": plane_bound,
             "In1_has_no_tracks": not in1_tracks, "protected_region_has_no_vias": not incursion_vias,
             "protected_region_has_no_inner_tracks": not inner_tracks,
             "J2_edge_datum_matches": definition["j2_edge_datum_error_mm"] == 0}
    return {"status": "PASS" if all(flags.values()) else "FAIL", "checks": flags,
            "wrong_layer_objects": wrong_layers, "narrow_F_tracks": narrow,
            "reference_uncovered_area_mm2": copper.difference(ground).area if not ground.is_empty else None,
            "unknowns": ["NO_SAVED_GND_IN1_FILL: reference continuity cannot be proven"] if ground.is_empty else [],
            "via_incursions": incursion_vias, "inner_track_incursions": inner_tracks,
            "F_copper_component_count": len(components),
            "scope": "saved geometry/continuity only; not impedance, RF performance, native DRC or release qualification"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("operation", choices=["derive", "check"])
    p.add_argument("observation", type=Path)
    p.add_argument("definition", type=Path)
    p.add_argument("output", nargs="?", type=Path)
    a = p.parse_args()
    obs = json.loads(a.observation.read_text())
    verify_saved_source(obs)
    if a.operation == "derive":
        result = derive(obs)
        a.definition.write_text(json.dumps(result, indent=2) + "\n")
    else:
        if a.output is None:
            p.error("check needs an output JSON path")
        result = assess_rf(obs, json.loads(a.definition.read_text()))
        a.output.write_text(json.dumps(result, indent=2) + "\n")
        raise SystemExit(0 if result["status"] == "PASS" else 2)
