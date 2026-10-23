# ROUTE-2 diagnosis and selected experiment

The ROUTE-1 written-board regrade reports 34 `failed_single`, four `open_single`, 14 entries in `failed_multipoint` (some overlap), and 691/769 connected pad pairs. Native KiCad independently reports 78 unconnected items across 48 nets. The complete final summary, blockers and boxed-in records are retained beside this document. `boxed_in_static` describes this routed search state; it does not establish an immutable placement defect.

ROUTE-1 introduced 61 native dangling findings: 27 `track_dangling` and 34 `via_dangling`. `route-1-new-findings.json` preserves every native object UUID and position. These findings remain defects when grading a later candidate; R5 is the final DRC baseline.

## Discriminating pad measurements

The existing `check_reachability.py` tool examined the exact R5 and ROUTE-1 boards. Geometry stayed at 0.2 mm tracks, 0.2 mm clearance and 0.6 mm vias. Its layer list was F.Cu, In2.Cu, B.Cu; the In1.Cu track prohibition remained intact. These are local raster diagnostics, not native DRC or whole-board routing proofs.

| Terminal | Net | Pad centre (mm) | R5 bottleneck / margin | ROUTE-1 result |
|---|---|---|---|---|
| U30.8 | /SENSOR_POWER_AUX_DVDT | 57.735, 46.550 | 0.32028 mm / +120.28 um | CAGED, margin approximately zero; nearby generated /GND via at 56.3,45.7 and /SENSOR_POWER_TIRE_RTN segment |
| U18.5 | /SUP_U18_CT | 81.160, 24.770 | 0.34027 mm / +140.27 um | CAGED; no numeric connected throat |
| U2.12 | /IMU_CS | 12.500, 9.0875 | 0.52957 mm / +329.57 um | CAGED but auto-widened to 0.05403 mm raster; advisory locator only |

The first two checks retain the 0.01 mm raster. Their R5 fields show passable escapes with the immutable placement. Generated copper, which R5 does not contain, constrains those same escapes after ROUTE-1. The U2 result does not support a precise congestion or impossibility claim because of its coarsening. No footprint correction is established by these measurements.

`D-PCB-7v2-In1-no-tracks` (UUID 460352a8-dace-51a2-842b-c1e4ef7ad212) forbids tracks, permits vias, and stays unchanged. `D-PCB-6-RF-reference` (UUID 93d1ddf1-382d-5ed8-abfa-2bf617ad0cae) forbids tracks and vias on In1.Cu and In2.Cu in its polygon. The wrapper's straight/L-corridor heuristic selecting In1.Cu for 51/78 connections grants no routing authority there. Exact polygons and layer flags are retained in `named-rule-areas.json`.

## One selected repair

The experiment retains ROUTE-1 as its source and uses the qualified b5774496 runtime. It selects the 48 native-open nets and the union of their final recorded blocker nets, 119 nets total. The exact lists are in `scope.json`; already connected blockers are eligible to move only when blocking a selected connection. The router may reroute generated unlocked copper with `--protect locked` and an explicit `--rip-existing-nets` list. R5 has zero tracks/vias and ROUTE-1 has zero locked objects, so this does not authorize removing human or locked copper.

The search grid is 0.05 mm instead of 0.1 mm. The explicit four-layer cost vector is 1,-1,3,3: In1.Cu stays obstacle-only while through-vias can span it. Track/via geometry, clearances, netclasses, rules, severities, footprints, pad/net identities, outline, stackup and keepouts are preserved. No force-reroute or second routing attempt is scheduled. The backend has 1,000 seconds, below the task's 1,200-second cap; the entire task is bounded by 07:06:55–07:46:55 UTC.

The alternatives were to retain ROUTE-1, assert an immutable blocker, or test a constrained repair. The local R5 measurements do not justify an immutable blocker. This single experiment tests whether removing the router's own congestion helps; its outcome is determined by the saved-board native checks. No additional object deletion is performed to suppress dangling findings.
