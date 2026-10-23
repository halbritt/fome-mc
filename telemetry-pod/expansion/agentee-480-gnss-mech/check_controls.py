#!/usr/bin/python3
"""Adversarial DATA controls, never synthetic PCB or acceptance evidence.

Synthetic observations exercise individual predicates. The real native board
is separately checked and fails. No synthetic result can stand in for it.
"""
import copy
import json
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, box, mapping, shape

from check_constraints import assess_rf, derive, verify_saved_source

OUT = Path(__file__).resolve().parent


def polyrecord(polygon):
    return [{"shell": list(polygon.exterior.coords),
             "holes": [list(h.coords) for h in polygon.interiors]}]


def run():
    observed = json.loads((OUT / "native-observation.json").read_text())
    definition = json.loads((OUT / "gnss-corridor.json").read_text())
    results = []

    def record(name, result, expect, scope="synthetic data control only"):
        assert expect(result), (name, result)
        results.append({"case": name, "result": result, "control_expectation": "PASS", "scope": scope})

    native = assess_rf(observed, definition)
    record("actual_ROUTE3_is_not_RF_qualified", native,
           lambda r: r["status"] == "FAIL" and not r["checks"]["F_only_RF_connectivity"], "actual saved-board observation")
    moved = copy.deepcopy(observed)
    next(f for f in moved["footprints"] if f["reference"] == "U3")["pads"][10]["at_mm"][0] += 1
    record("one_bound_pad_moved", assess_rf(moved, definition), lambda r: r.get("code") == "STALE_BINDING")
    edge = copy.deepcopy(observed)
    edge["edges"][0]["start_mm"][0] += 1
    record("edge_moved", assess_rf(edge, definition), lambda r: r.get("code") == "STALE_BINDING")
    bad = copy.deepcopy(definition)
    bad["rf_width_mm"] = 0.01
    record("definition_width_tamper", assess_rf(observed, bad),
           lambda r: r.get("code") == "DEFINITION_CHANGED_REDERIVE_REQUIRED")
    bad = copy.deepcopy(observed)
    next(p for f in bad["footprints"] if f["reference"] == "C42" for p in f["pads"] if p["number"] == "1")["net"] = "/POD_GNSS_RF"
    try:
        derive(bad)
    except ValueError as error:
        record("bias_bypass_relabelled_as_RF", {"exception": str(error)}, lambda r: "topology mismatch" in r["exception"])
    else:
        raise AssertionError("topology poison accepted")
    # Common translation of the relevant geometry and edges must regenerate a
    # translated corridor. This does not assert that a real translated PCB fits.
    translated = copy.deepcopy(observed)
    for f in translated["footprints"]:
        if f["reference"] not in {"U3", "L3", "D3", "C42", "J2"}:
            continue
        f["at_mm"][0] += 1
        for p in f["pads"]:
            p["at_mm"][0] += 1
            for polys in p.get("copper_polygons", {}).values():
                for polygon in polys:
                    for ring in [polygon["shell"], *polygon["holes"]]:
                        for point in ring:
                            point[0] += 1
        for polygons in f["courtyards"].values():
            for polygon in polygons:
                for ring in [polygon["shell"], *polygon["holes"]]:
                    for point in ring:
                        point[0] += 1
    for e in translated["edges"]:
        e["start_mm"][0] += 1
        e["end_mm"][0] += 1
    regenerated = derive(translated)
    same = shape(regenerated["reference_exclusion"]).equals_exact(
        affinity.translate(shape(definition["reference_exclusion"]), xoff=1), tolerance=1e-12)
    record("explicit_rebind_follows_common_translation", {"translated_geometry_matches": same,
           "j2_edge_error_mm": regenerated["j2_edge_datum_error_mm"]},
           lambda r: r["translated_geometry_matches"] and r["j2_edge_error_mm"] == 0)

    # A deliberately idealized geometry data control supplies a connected F
    # tree, unperforated GND fill and the correctly rebound native-rule shape.
    # These are NOT board objects, native checks, or evidence of route feasibility.
    synthetic = copy.deepcopy(observed)
    synthetic["synthetic_control_only"] = True
    for net in ["/POD_GNSS_RF", "/GND"]:
        synthetic["native_terminals"]["nets"][net] = [sorted({p for group in synthetic["native_terminals"]["nets"][net] for p in group})]
    synthetic["tracks"] = []
    for index, path in enumerate([definition["main_polyline_mm"], *definition["tap_polylines_mm"]]):
        for segment, (a, b) in enumerate(zip(path, path[1:])):
            copper = LineString([a, b]).buffer(definition["rf_width_mm"] / 2, cap_style=1)
            synthetic["tracks"].append({"uuid": f"SYNTHETIC-{index}-{segment}", "net": "/POD_GNSS_RF", "kind": "track",
                                        "layer": "F.Cu", "layers": ["F.Cu"], "start_mm": a, "end_mm": b,
                                        "width_mm": definition["rf_width_mm"], "copper_polygons": polyrecord(copper)})
    rf_rule = next(z for z in synthetic["zones"] if z["name"] == "D-PCB-6-RF-reference")
    mask = shape(definition["reference_exclusion"])
    pieces = list(mask.geoms) if mask.geom_type == "MultiPolygon" else [mask]
    rf_rule["outline"] = [p for piece in pieces for p in polyrecord(piece)]
    synthetic["zones"].append({"uuid": "SYNTHETIC-GND", "name": "SYNTHETIC", "net": "/GND",
                                "rule_area": False, "layers": ["In1.Cu"], "outline": polyrecord(box(0, 0, 90, 65)),
                                "saved_in1_fill": polyrecord(box(0, 0, 90, 65))})
    record("idealized_predicates_can_pass", assess_rf(synthetic, definition), lambda r: r["status"] == "PASS")
    native_split = copy.deepcopy(synthetic)
    native_split["native_terminals"]["nets"]["/POD_GNSS_RF"] = observed["native_terminals"]["nets"]["/POD_GNSS_RF"]
    record("native_RF_split_overrides_geometric_picture", assess_rf(native_split, definition),
           lambda r: not r["checks"]["native_RF_terminal_equivalence"])
    ground_split = copy.deepcopy(synthetic)
    ground_split["native_terminals"]["nets"]["/GND"] = observed["native_terminals"]["nets"]["/GND"]
    record("floating_reference_return_group_rejected", assess_rf(ground_split, definition),
           lambda r: not r["checks"]["native_U3_J2_D3_C42_returns_one_group"])
    removed = copy.deepcopy(synthetic)
    removed["tracks"].pop(1)
    record("missing_F_bridge_rejected", assess_rf(removed, definition), lambda r: not r["checks"]["F_only_RF_connectivity"])
    wrong = copy.deepcopy(synthetic)
    wrong["tracks"][1]["layer"] = "B.Cu"
    record("B_layer_bridge_rejected", assess_rf(wrong, definition), lambda r: not r["checks"]["RF_net_has_no_vias_or_non_F_tracks"])
    hole = copy.deepcopy(synthetic)
    ground = box(0, 0, 90, 65).difference(box(59.9, 27.9, 60.1, 28.1))
    hole["zones"][-1]["saved_in1_fill"] = polyrecord(ground)
    record("reference_void_rejected", assess_rf(hole, definition),
           lambda r: not r["checks"]["one_saved_GND_In1_component_covers_actual_RF"])
    missing_fill = copy.deepcopy(synthetic)
    missing_fill["zones"][-1]["saved_in1_fill"] = []
    record("unknown_reference_never_passes", assess_rf(missing_fill, definition),
           lambda r: r["status"] == "FAIL" and bool(r["unknowns"]))
    foreign_ground = copy.deepcopy(synthetic)
    foreign_ground["zones"][-1]["net"] = "GND"
    record("distinct_net_name_not_silently_normalized", assess_rf(foreign_ground, definition),
           lambda r: not r["checks"]["one_saved_GND_In1_component_covers_actual_RF"])
    try:
        verify_saved_source(synthetic)
    except ValueError as error:
        record("synthetic_control_refused_by_real_source_gate", {"exception": str(error)},
               lambda r: r["exception"] == "SYNTHETIC_CONTROL_IS_NOT_SAVED_BOARD_EVIDENCE")
    else:
        raise AssertionError("synthetic observation accepted as native evidence")
    via = copy.deepcopy(synthetic)
    via["tracks"].append({"uuid": "SYNTHETIC-FOREIGN-VIA", "net": "/+3V3", "kind": "via", "layer": "F.Cu",
                          "layers": ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"], "start_mm": [60, 28], "end_mm": [60, 28], "width_mm": 0.6})
    record("foreign_reference_via_rejected", assess_rf(via, definition),
           lambda r: not r["checks"]["protected_region_has_no_vias"])
    policy = copy.deepcopy(synthetic)
    next(z for z in policy["zones"] if z["name"] == "D-PCB-7v2-In1-no-tracks")["forbid"]["vias"] = True
    record("plane_rule_via_semantics_not_conflated", assess_rf(policy, definition),
           lambda r: not r["checks"]["In1_no_tracks_vias_allowed_rule_covers_outline"])
    output = {"schema": "agentee-480.check-controls/1", "status": "PASS", "cases": results,
              "physical_acceptance": False, "warning": "Synthetic controls are predicate tests only, never routed/native/physical candidate evidence."}
    (OUT / "check-controls.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"controls_passed": len(results), "native_board_status": native["status"], "physical_acceptance": False}))


if __name__ == "__main__":
    run()
