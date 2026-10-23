#!/usr/bin/python3
"""Materialize task-scoped mechanical data from the immutable native observation.

Engineering selections are labelled. This neither edits a board nor declares
the current candidate mechanically accepted.
"""
import json
import math
from pathlib import Path

from shapely import affinity
from shapely.geometry import Point, box, mapping

from check_constraints import footprints, geometry, verify_saved_source

OUT = Path(__file__).resolve().parent


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def materialize(obs):
    if obs["board_sha256"] != "0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651":
        raise ValueError("baseline height sources require part-binding requalification before transfer to a new candidate")
    fps = footprints(obs)
    source477 = "telemetry-pod/expansion/agentee-477-3d-models/RESULT.md#sourced-geometry-for-agentee-474--472"
    sources = [
        {"id": "screw", "class": "manufacturer table / ISO7380-1", "url": "https://www.accu.co.uk/socket-button-screws/8102-SSB-M3-8-A2",
         "locator": "Technical Specification; web read2026-10-23; direct HTTP403 retained separately",
         "facts": {"part": "SSB-M3-8-A2", "thread": "M3x0.5", "length_mm": 8,
                   "head_diameter_max_mm": 5.7, "head_height_max_mm": 1.65, "drive_AF_mm": 2,
                   "socket_depth_min_mm": 1.04, "material": "A2 stainless"}},
        {"id": "washer", "class": "manufacturer table / ISO7089", "url": "https://www.accu.co.uk/metric-flat-washers/404025-HPW-M3-V1-A2-BL",
         "locator": "Technical Specification; web read2026-10-23; direct HTTP403 retained separately",
         "facts": {"part": "HPW-M3-V1-A2-BL", "OD_max_mm": 7, "ID_min_mm": 3.2, "ID_max_mm": 3.38,
                   "thickness_max_mm": 0.5, "thickness_min_mm": 0.4, "material": "A2 stainless"}},
        {"id": "standoff", "class": "manufacturer drawing", "url": "https://content.harwin.com/asset/01366872-70cb-4c3a-b07f-f37dd1fbb2c1/DRG-01996-Technical-Drawing-Datasheet-R30-161-pdf.pdf",
         "locator": "R30-161XX00 issue5,24.02.10,sheet2of2; visually read; PDF SHA35dd465b26949b006ff38bae89c74fdf30b218679dc49af1fb6d24f4ffc4fc01",
         "facts": {"part": "R30-1611200", "thread": "M3x0.5-6H female/female through-threaded",
                   "body_length_nominal_mm": 12, "body_length_max_mm": 12.3, "body_length_min_mm": 11.7,
                   "AF_nominal_mm": 5.5, "AF_max_mm": 5.7, "AF_min_mm": 5.3, "material": "Nylon66 UL94V-2"}},
        {"id": "driver", "class": "manufacturer product data / ISO2936L", "url": "https://wiha.com/pl/pl/narzedzia/klucze-szesciokatne/pojedyncze-klucze-z-glowka-kulowa-wiha/gniazdo-szesciokatne/klucze-szesciokatne/01393",
         "facts": {"part": "Wiha01393", "AF_mm": 2, "overall_long_mm": 101, "short_mm": 18},
         "locator": "Product dimensions and01393 table row; long leg used axially; 25deg ball-end use not assumed"},
        {"id": "probe", "class": "manufacturer reference probe, engineering selection for envelope only",
         "url": "https://ingun.com/media/30/5f/08/1752236032/INGUN_GKS-075_305_064_A_1500_GKS-075-0084_EN_Datasheet.pdf?ts=1763083368",
         "facts": {"part": "GKS-075-0084", "tip_diameter_mm": 0.64, "barrel_diameter_mm": 1.02,
                   "working_stroke_mm": 4.3, "maximum_stroke_mm": 6.35}, "locator": "PDFp1; no fixture or full clip envelope is adopted"},
        {"id": "iron", "class": "manufacturer tip data, engineering selection for envelope only",
         "url": "https://www.weller-tools.com/mea/gb/industrial-soldering/products/soldering-tips/rtm-013-s",
         "facts": {"part": "RTM013S", "chisel_width_mm": 1.3, "chisel_thickness_mm": 0.4},
         "locator": "Product description; full hot taper/barrel dimensions UNKNOWN"}]
    save("sources/selected-facts.json", {"schema": "agentee-480.sourced-dimensions/1", "items": sources,
                                         "note": "Paraphrased dimensions, not a redistributed standard/drawing. Sources do not authorize purchases."})
    save("owner-answers.json", {"schema": "agentee-480.owner-answers/1", "source": "owner answers fd5bea71 as relayed in exact Cairn5bfc7b7a-9520-4e85-a94f-ee53caa5e630@1",
                                "class": "owner-relayed; assignment is not owner-authored text",
                                "TP": "handheld pogo clip, bare board before enclosure; bottom TPs allowed; BLE OTA after",
                                "JP": "set once with soldering iron on bare board before enclosure",
                                "hardware": "agents choose standard M3 hardware; no purchase",
                                "cowl": {'estimate_mm': 90, 'dimension': 'available vertical height under rear cowl', 'axis': 'Z', 'measured': False, 'hard_cap': False, 'provisional_envelope_height_mm': 90, 'length_width': 'well over90mm;90x65mm board outline is not cowl-constrained', 'measurement_task': False, 'source': 'b1987334-6363-413b-b1a4-d2666284142b@1 relays owner to519 via27c51f73', 'assembly_requirement': 'Entire installed vertical stack must fit provisional90mm height: enclosure floor/lid, M3 stack, board, both-face components, J1 body plus harness, J2 SMA plus cable bend. Unknown terms cannot pass.'}})
    body_limits = {
        "L1": (4.8, 5.0, "BournsSRP7050TA-150M", source477, "4.8+0.2; reused477 capture5a7926dd, not reacquired"),
        "L2": (5.2, 5.4, "BournsSRP7050WA-6R8M", source477, "5.2+0.2; reused477 capture3f16305b, not reacquired"),
        "U3": (2.4, 2.6, "NEO-M9N-00B", source477, "UBX-19014285R08; sourced dimensions; visualization STEP is not authority"),
        "U1": (3.1, 3.25, "ESP32-S3-WROOM-1-N8", "telemetry-pod/expansion/parts-closure/recovered-pilot/core/datasheets-core/bcd526f54b8de686cec4db67219e36ea7ace50cddb0c92f3dfdac49cf99ffd2e.pdf:p42,Fig10-1", "3.1+0.15; WROOM-1U3.2 dimension does not apply"),
        "U2": (None, 0.86, "LSM6DSO32TR", "telemetry-pod/expansion/parts-closure/recovered-pilot/core/datasheets-current/fce1bf36cb460a31e2d1f3ede054b5d2e68f07b8f9039cb09062522e9bcf4e2c.pdf:p149,Fig22", "0.86MAX; visually checked"),
        "U5": (None, 1.7, "LMR36520ADDAR", "telemetry-pod/expansion/parts-closure/recovered-pilot/power-source/acquisition/cb8ebe03bcc7860306c5e291bd6d892cb951f20cf5f21f15ecbcd8efd3029dd1.pdf:p38,DDA0008B", "seating-plane package maximum"),
        "U7": (None, 1.7, "LMR36520ADDAR", "telemetry-pod/expansion/parts-closure/recovered-pilot/power-source/acquisition/cb8ebe03bcc7860306c5e291bd6d892cb951f20cf5f21f15ecbcd8efd3029dd1.pdf:p38,DDA0008B", "same bound exact package"),
        "U6": (None, 1.7, "TPS7B4253QDDARQ1", "telemetry-pod/expansion/parts-closure/recovered-pilot/power-source/acquisition-tracker/f0068c8d96247b629703e6eacc46990097dff6779f4204d95b88ed3118e22827.pdf:p24,DDA0008J-C02", "seating-plane package maximum; source identity from477sources.txt"),
        "U12": (None, 1.7, "TPS7B4253QDDARQ1", "telemetry-pod/expansion/parts-closure/recovered-pilot/power-source/acquisition-tracker/f0068c8d96247b629703e6eacc46990097dff6779f4204d95b88ed3118e22827.pdf:p24,DDA0008J-C02", "same bound exact package")}
    heights = []
    for ref, f in fps.items():
        row = {"reference": ref, "uuid": f["uuid"], "face": f["face"], "value": f["value"],
               "footprint": f["lib_id"], "body_nominal_mm": None, "body_max_mm": None,
               "assembled_height_qualification": "UNKNOWN; numeric package limits do not qualify this assembly",
               "source": None, "status": "UNKNOWN"}
        if ref in body_limits:
            nominal, maximum, part, source, note = body_limits[ref]
            row.update(body_nominal_mm=nominal, body_max_mm=maximum, selected_part=part, source=source,
                       status="SOURCED_PACKAGE_LIMIT", note=note)
        elif ref == "J3":
            row.update(body_nominal_mm=1.68, status="SOURCED_NOMINAL_ONLY",
                       source="telemetry-pod/expansion/production-capture/sources/j3-datasheet/acquisition-digikey/7059663a2a7162b7315ebf55be1a1d3dcffa2066e159a59e5c75b234466d1207.pdf:p3",
                       note="catalog dimension, no maximum tolerance asserted")
        elif ref == "J1":
            row.update(body_nominal_mm=27.77, status="MODEL_NOMINAL_ONLY", source="telemetry-pod/expansion/connector-candidate/README.md:83-108",
                       note="nominal STEP top relative to support plane; tail projection3.50 before owner-described trimming; upper tolerance UNKNOWN")
        elif ref.startswith(("H", "TP", "JP")):
            row.update(body_nominal_mm=0, body_max_mm=0, status="COPPER_OR_HOLE_NO_COMPONENT_BODY",
                       source=source477, note="no component body; installed hardware, probe and solder bridge/fillet are separate, not zero-height assumptions")
        heights.append(row)
    save("heights.json", {"schema": "agentee-480.part-heights/1", "status": "PROVISIONAL_HEIGHT_TABLE", "board_sha256": obs["board_sha256"],
                          "parts": heights, "unknown_never_passes": True,
                          "model_coverage_is_not_height_qualification": True})
    reservations = []
    def add(ref, face, part, radius, z, phase, source, note):
        f = fps[ref]
        reservations.append({"id": ref + "/" + part, "reference": ref, "uuid": f["uuid"], "face": face,
                             "relative": {"origin": "footprint centre", "offset_mm": [0, 0], "follows_pose": True},
                             "at_mm": f["at_mm"], "geometry": {"kind": "axial_cylinder", "radius_mm": radius,
                                                                      "z_outward_from_face_mm": z},
                             "phase": phase, "source": source, "class": "sourced dimensions; engineering-selected assembly/approach",
                             "note": note})
    for ref in ["H1", "H2", "H3", "H4"]:
        add(ref, "F.Cu", "ISO7089-washer", 3.5, [0, 0.5], "installed", "washer", "OD7.0 maximum; no extra margin")
        add(ref, "F.Cu", "ISO7380-head", 2.85, [0.4, 2.15], "installed", "screw", "head above washer; includes washer thickness interval")
        add(ref, "B.Cu", "ISO7089-washer", 3.5, [0, 0.5], "installed", "washer", "selected washer between PCB and insulating standoff")
        add(ref, "B.Cu", "Harwin-standoff", (5.7 / math.cos(math.pi / 6)) / 2, [0.4, 12.8], "installed", "standoff",
            "rotation-independent circumscribed hex at maxAF5.7; max12.3 body + washer0.5; no added radius")
        add(ref, "F.Cu", "driver-shaft", (2 / math.cos(math.pi / 6)) / 2, [0.4, 102.11], "bench-fastening-before-lid", "driver+screw",
            "nominal rotating2mm hex; long leg axially; z from washer contact to101+2.15-1.04; exact key dimensional tolerance UNKNOWN")
        add(ref, "F.Cu", "driver-return-arm", 18, [101 - 2 / math.cos(math.pi / 6) + 0.4, 102.11], "bench-fastening-before-lid", "driver+screw",
            "nominal outer18mm short-leg sweep at far end; z lower=101-hexAcrossCorners+washerMin, upper=101+headWasherMax-socketMin; exact bend/tolerance UNKNOWN; no PCB-plane18mm rule")
    for ref in ["TP" + str(i) for i in range(1, 7)]:
        p = fps[ref]["pads"][0]
        # Any landing point on the1.5mm pad + a0.64mm physical tip; not a new margin.
        add(ref, fps[ref]["face"], "pogo-tip-approach", max(p["size_mm"]) / 2 + 0.64 / 2, [0, None],
            "bare-board-bench-only", "owner-answers+probe", "normal approach ray; pad landing locus plus tip radius; no fixture/post-seal or full clip envelope")
    for ref in ["JP" + str(i) for i in range(1, 6)]:
        f = fps[ref]
        for p in f["pads"]:
            # Native pad box plus the physical1.3x0.4 chisel at selected normal approach.
            shape = box(-p["size_mm"][0] / 2 - 1.3 / 2, -p["size_mm"][1] / 2 - 0.4 / 2,
                        p["size_mm"][0] / 2 + 1.3 / 2, p["size_mm"][1] / 2 + 0.4 / 2)
            shape = affinity.rotate(shape, p["orientation_deg"], origin=(0, 0))
            shape = affinity.translate(shape, *p["at_mm"])
            reservations.append({"id": ref + "/iron-pad" + p["number"], "reference": ref, "uuid": f["uuid"],
                                 "face": f["face"], "relative": {"origin": "pad", "number": p["number"], "follows_pose": True},
                                 "geometry": {"kind": "extruded_polygon", "polygon": mapping(shape), "z_outward_from_face_mm": [0, None]},
                                 "class": "sourced chisel+engineering-selected normal approach", "source": "owner-answers+iron",
                                 "phase": "bare-board-one-time-soldering", "status": "PROVISIONAL_TIP_ONLY",
                                 "unknown": "full hot-taper/barrel/solder-feed-hand envelope not sourced; cannot pass complete iron-access qualification"})
    save("keepouts.json", {"schema": "agentee-480.per-face-keepouts/1", "board_sha256": obs["board_sha256"],
                           "status": "PROVISIONAL_UNTIL_CONSUMED_AND_FINAL_COORDINATES_CHECKED", "items": reservations,
                           "notes": ["Z is outward from each face; B therefore opposes F in worldZ.",
                                     "Do not turn bench-only reservations into enclosure openings.",
                                     "Hardware selection does not prove nylon creep, thread retention, torque or motorcycle vibration performance.",
                                     "Choose enclosure attachment using internal bosses; seal/fastener engagement remain future engineering deliverables.",
                                     "A2 screw/washer near U1 requires installed antenna/metal assessment; IP67 is not established by component selection."]})
    conflicts = []
    unknown_height = []
    for item in reservations:
        from shapely.geometry import shape as read_shape
        geo = item["geometry"]
        footprint = (Point(item["at_mm"]).buffer(geo["radius_mm"]) if geo["kind"] == "axial_cylinder"
                     else read_shape(geo["polygon"]))
        layer = "F.Courtyard" if item["face"] == "F.Cu" else "B.Courtyard"
        for ref, fp in fps.items():
            if ref == item["reference"]:
                continue
            court = geometry(fp["courtyards"][layer])
            if court.is_empty or not footprint.intersects(court):
                continue
            part_height = next(h for h in heights if h["reference"] == ref)["body_max_mm"]
            zmin, zmax = geo["z_outward_from_face_mm"]
            if part_height is not None and part_height <= zmin:
                continue
            record = {"reservation": item["id"], "face": item["face"], "reference": ref,
                      "intersection_area_mm2": footprint.intersection(court).area,
                      "meaning": "courtyard/reservation intersection, not a measured physical short or native DRC finding"}
            if zmin > 0 and part_height is None:
                unknown_height.append(record)
            else:
                conflicts.append(record)
    pogo_obstructions = []
    unsupported_pth_shapes = []
    for probe in [r for r in reservations if r["id"].endswith("pogo-tip-approach")]:
        swept = Point(probe["at_mm"]).buffer(probe["geometry"]["radius_mm"])
        for hardware in [r for r in reservations if r["face"] == "B.Cu" and r["phase"] == "installed"]:
            if swept.intersects(Point(hardware["at_mm"]).buffer(hardware["geometry"]["radius_mm"])):
                pogo_obstructions.append({"probe": probe["id"], "object": hardware["id"]})
        for ref, fp in fps.items():
            for p in fp["pads"]:
                if not any(p["drill_mm"]):
                    continue
                if p["shape"] not in [0, 1]:
                    unsupported_pth_shapes.append({"reference": ref, "pad_uuid": p["uuid"], "shape": p["shape"]})
                    continue
                # Rotated native size box contains a circular/rectangular pad;
                # a clear result is conservative without guessing solder-tail height.
                bound = box(-p["size_mm"][0] / 2, -p["size_mm"][1] / 2,
                            p["size_mm"][0] / 2, p["size_mm"][1] / 2)
                bound = affinity.translate(affinity.rotate(bound, p["orientation_deg"], origin=(0, 0)), *p["at_mm"])
                if swept.intersects(bound):
                    pogo_obstructions.append({"probe": probe["id"], "object": ref + "/" + p["uuid"]})
        if swept.intersects(geometry(fps["J1"]["courtyards"]["F.Courtyard"])):
            pogo_obstructions.append({"probe": probe["id"], "object": "J1 conservative projection of its below-seat body"})
    pogo_court_conflicts = [r for r in conflicts + unknown_height if r["reservation"].endswith("pogo-tip-approach")]
    save("mechanical-check.json", {"schema": "agentee-480.mechanical-check/1", "status": "PROVISIONAL_FAIL_OR_UNKNOWN",
                                   "reservation_conflicts": conflicts, "height_unknown_intersections": unknown_height,
                                   "pogo_tip_approach": {"status": "PASS_SELECTED_TIP_MODEL" if not pogo_obstructions and not pogo_court_conflicts and not unsupported_pth_shapes else "FAIL_OR_UNKNOWN",
                                                         "obstructions": pogo_obstructions, "courtyard_conflicts": pogo_court_conflicts,
                                                         "unsupported_pth_shapes": unsupported_pth_shapes,
                                                         "scope": "normal B approach with chosen0.64mm tip and full pad landing locus; future larger/different clip requires rebind; no fixture or post-seal access"},
                                   "cross_face_through_hole_body_check": "OPEN; native courtyard intersection is not full3D/tool/solder-tail validation",
                                   "candidate_mechanical_acceptance": False})
    return {"height_rows": len(heights), "sourced_package_maxima": len(body_limits),
            "reservations": len(reservations), "conflicts": len(conflicts), "height_unknown_intersections": len(unknown_height)}


if __name__ == "__main__":
    observation = json.loads((OUT / "native-observation.json").read_text())
    verify_saved_source(observation)
    print(json.dumps(materialize(observation)))
