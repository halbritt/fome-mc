# placement-r5: R4 continuation — (A) COMPLETE placed board (309/309), with 63 new silkscreen DRC findings

Assignment: agent-521 brief 81bf1861 (via agent-519); plan agent-ee main `9b381f0d`, revision 5, "Next action (revision 5)" and its acceptance list. These are coordinator records, not owner text.

**Clock:** started 2026-10-23T06:29:33.62Z; board admitted and checked by 06:42:50Z; result written by about 06:45Z. One 60-minute task, used about 16 minutes.

**What this is:**
- a complete placement of all 309 footprints, admitted whole-board by the existing placement gate (patched only for the authorized side transform);
- every placement and preservation check passes;
- native DRC has **63 new silkscreen findings**, listed below. They are open defects, not placement refusals.

**What this is not:** no release qualification is claimed. No routing exists (499 unconnected is expected before routing).

## Saved board and paired project

| File | sha256 |
|---|---|
| `board/telemetry-pod.kicad_pcb` (the admitted candidate) | **`8f3bc234305516b91b6e519d3e0a3cd05b69b6dd16006a317c39b6d810ace5fd`** |
| `board/telemetry-pod.kicad_pro` (original bytes) | `10002b987995765415313fa89da32ba9011160853596f1a78ff8fba24ac9b175` |
| `board/telemetry-pod.kicad_dru` (original bytes) | `ff62208301c38bca2c963a0682e0a2ee843d8a546bace3719340cfcca1b08d0d` |

Input: fome-mc `881f6fc5` board `2f1c9557…` and project `10002b98…`; the emission-7d5b0d4d tree was verified file by file. Starting arrangement: the R2 diagnostic 287 poses, all retained unchanged; `moved_footprints` 300 relative to the emitter layout.

## Runtime: "7d5b0d4d + R5 side-transform patch b4be6263"

- **Image:** `sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7`, `--network none`, no AppArmor or seccomp option.
- **agent-ee:** the R2 step's 7d5b0d4d tool snapshot, with **only** `agent_ee/placer_runner.py` overlaid. Unmodified `76308585…`, patched **`b4be6263656322a337c29c47811951e6be0c6eb9017cd73c4f06d9f491ddd5ba`**.
- **Patch:** `evidence/r5-side-transform.patch`, sha256 **`ac06575d660d0070fe15c4e5d1c0a7d5f8054d2cd3c6f0205b4edaf3b74dbc72`**.
- **agent-ee correction commit:** **`02b6510d1a272dbd72928f2b96ad9dad1fb952e6`** on `wt/r5-side-transform`, based on main `9b381f0d`; not merged or pushed.
- **Admission:** native-admit on proximal; leases in `evidence/native-admit-events.jsonl`.
- **Board run** (lease `456b131269d2`): `~/.local/bin/native-admit run --class suite --weight 4 --label placement-r5 -- bash telemetry-pod/expansion/placement-r5/r5_run.sh <R2 work> <work> <fome-mc> <patched tool>`
  - `r5_place.py`: the 22 poses, then the **whole-board** patched `placer_runner._evaluate_proposal` on the ORIGINAL board under policy r1 plus the `agent-ee.side-changes/1` authorization (`evidence/side-changes.json`, bound to board sha256 `2f1c9557…` and the exact 22 ref/UUIDs);
  - the unchanged `../placement-r1/checks_r1.py`;
  - kicad-cli renders.
- **Extra checks** (lease after it): `r5_extra_checks.py`.
- **An earlier execution of `r5_place.py` is kept, not hidden.** It stopped in 3 s with "R74 unplaceable": my centroid used pads of not-yet-placed parts at their off-board emitter positions. It was a script bug; nothing was admitted or written. The fix (fome-mc commit `6b4ad18`, "on-board peer pads only") preceded the run above.

## The correction (agent-ee, `src/agent_ee/placer_runner.py`)

- **Authorization:** `_side_changes(source, authorization, plan)`. Only the request's `agent-ee.side-changes/1` record grants a flip. It is bound to the original board sha256 and to exact reference+UUID pairs, each named once.
  - The plan must declare the same side for exactly those footprints.
  - Refused: undeclared, wrong-side, same-side, fixed-part and foreign-board flips; a plan's own `side` field; custom or per-layer pad geometry ("unqualified").
- **Write:** `_apply_plan(..., changes)` flips natively (`Flip(pos, FLIP_DIRECTION_LEFT_RIGHT)`), then sets orientation and position. It is called unchanged when there are no side changes.
- **Gate:** the pad-inventory baseline = the original inventory, with the flipped footprints replaced by `_flipped_inventory(source, changes)`: the **original** footprints after the same native flip, on a disposable copy. The baseline is never pre-flipped. Every other footprint keeps the exact original comparison. A new check requires every saved side to equal the original side map plus the declared changes.
- **`place_candidate`** passes `request.get('side_changes')`; this is `None` and the behaviour is unchanged without it.

**Tests** (CI image through admission: `native-admit run --class suite --weight 4 --label r5-tests -- ae-ci-exec <worktree> -- python3 scripts/strict_suite.py --jobs 4 …`):
- **`strict suite passed: 5 modules, 139 tests, no skips`** (`evidence/r5-tests.log`):
  - new `test_placer_side_transform` 4: legal flip survives save and reload; refusals for undeclared, wrong-side, same-side, fixed, foreign-board, malformed and wrong-ref flips; corruption on a declared flip (number, shape, size) and on an unflipped part refused; behaviour without side changes unchanged;
  - `test_placer_native` 18, `test_placer_gate_hardening` 12, `test_placer_pad_keepout` 16, `test_placement_defects` 89.
- **The first test run failed and is kept** (`evidence/r5-tests-first-run-failed.log`):
  - two existing tests patch `_apply_plan` with 3-argument wrappers, which my always-4-argument call broke. Fixed by keeping the unchanged call without side changes;
  - one of my subtests mutated a net on a net-less fixture pad. Replaced with a pad-size mutation.

## The 22 side changes (from → to), with each pose's rationale

The pose rule: no search or scorer; one explicit pose per part. Start at the centroid of the part's **on-board peer pads** on its signal nets (rail-like nets with more than 20 peers only as a fallback; ground excluded). Step outward in 0.5 mm rings, trying rotations 0° and 90°, and take the **first** B pose whose native courtyard is clear of all of these:
- the outline less 0.5 mm, with the courtyard inflated by the 0.25 mm gap;
- every other B courtyard;
- all B copper and PTH/NPTH pads;
- every rule area forbidding footprints on B: 111 blocking items in all, the all-layer antenna keepout among them.

| Ref | From (side, pos mm, rot) | To (side, pos mm, rot) | Rationale |
|---|---|---|---|
| R7 | F, (95.25, 553.72), 0° | **B**, (37.81, 26.31), 0° | first clear B pose 0 mm from the centroid (37.81, 26.31) of its 4 on-board peer pads on /REF_CAP_NODE, /SETPOINT_5V |
| R70 | F, (95.25, 765.81), 0° | **B**, (59.88, 43.56), 0° | first clear B pose 0 mm from the centroid (59.88, 43.56) of its 5 on-board peer pads on /TIRE_CAN_H, /TIRE_CAN_TERM |
| R71 | F, (95.25, 769.62), 0° | **B**, (61.53, 32.67), 0° | first clear B pose 0 mm from the centroid (61.53, 32.67) of its 2 on-board peer pads on /TIRE_CAN_SILENT |
| R72 | F, (95.25, 773.43), 0° | **B**, (71.14, 21.43), 0° | first clear B pose 0 mm from the centroid (71.14, 21.43) of its 1 on-board peer pads on /TIRE_CAN_GPIO1 |
| R73 | F, (95.25, 777.24), 0° | **B**, (35.03, 25.62), 90° | first clear B pose 1 mm from the centroid (35.90, 25.12) of its 21 on-board peer pads on /PRE_6V3, /SENSOR_POWER_FRONT_UVLO |
| R74 | F, (95.25, 781.05), 0° | **B**, (65.29, 63.68), 0° | first clear B pose 1 mm from the centroid (65.79, 64.55) of its 3 on-board peer pads on /SENSOR_POWER_FRONT_OVP, /SENSOR_POWER_FRONT_UVLO |
| R75 | F, (95.25, 784.86), 0° | **B**, (54.48, 63.68), 0° | first clear B pose 1 mm from the centroid (54.98, 64.55) of its 9 on-board peer pads on /SENSOR_POWER_FRONT_OVP, /SENSOR_POWER_FRONT_RTN |
| R76 | F, (95.25, 788.67), 0° | **B**, (53.58, 61.87), 0° | first clear B pose 3 mm from the centroid (54.93, 64.55) of its 9 on-board peer pads on /SENSOR_POWER_FRONT_ILIM, /SENSOR_POWER_FRONT_RTN |
| R77 | F, (95.25, 792.48), 0° | **B**, (31.21, 29.68), 0° | first clear B pose 0 mm from the centroid (31.21, 29.68) of its 1 on-board peer pads on /SENSOR_POWER_REAR_UVLO |
| R78 | F, (95.25, 796.29), 0° | **B**, (50.79, 62.92), 90° | first clear B pose 2.5 mm from the centroid (52.69, 64.55) of its 3 on-board peer pads on /SENSOR_POWER_REAR_OVP, /SENSOR_POWER_REAR_UVLO |
| R79 | F, (95.25, 800.10), 0° | **B**, (37.01, 63.68), 0° | first clear B pose 1 mm from the centroid (37.51, 64.55) of its 9 on-board peer pads on /SENSOR_POWER_REAR_OVP, /SENSOR_POWER_REAR_RTN |
| R80 | F, (95.25, 803.91), 0° | **B**, (36.10, 61.87), 0° | first clear B pose 3 mm from the centroid (37.45, 64.55) of its 9 on-board peer pads on /SENSOR_POWER_REAR_ILIM, /SENSOR_POWER_REAR_RTN |
| R81 | F, (95.25, 807.72), 0° | **B**, (50.85, 34.23), 0° | first clear B pose 0 mm from the centroid (50.85, 34.23) of its 1 on-board peer pads on /SENSOR_POWER_TIRE_UVLO |
| R82 | F, (95.25, 811.53), 0° | **B**, (64.44, 61.87), 0° | first clear B pose 3 mm from the centroid (65.79, 64.55) of its 3 on-board peer pads on /SENSOR_POWER_TIRE_OVP, /SENSOR_POWER_TIRE_UVLO |
| R83 | F, (95.25, 815.34), 0° | **B**, (57.27, 62.62), 90° | first clear B pose 3.5 mm from the centroid (54.35, 64.55) of its 9 on-board peer pads on /SENSOR_POWER_TIRE_OVP, /SENSOR_POWER_TIRE_RTN |
| R84 | F, (95.25, 819.15), 0° | **B**, (59.43, 62.59), 90° | first clear B pose 5.5 mm from the centroid (54.29, 64.55) of its 9 on-board peer pads on /SENSOR_POWER_TIRE_ILIM, /SENSOR_POWER_TIRE_RTN |
| TP1 | F, (95.25, 1101.09), 0° | **B**, (81.25, 5.05), 0° | first clear B pose 0 mm from the centroid (81.25, 5.05) of its 1 on-board peer pads on /POD_UART_TX |
| TP2 | F, (95.25, 1106.17), 0° | **B**, (82.00, 7.62), 0° | first clear B pose 1.5 mm from the centroid (81.25, 6.32) of its 1 on-board peer pads on /POD_UART_RX |
| TP3 | F, (95.25, 1111.25), 0° | **B**, (45.00, 32.50), 0° | first clear B pose 0 mm from the centroid (45.00, 32.50) of its 0 on-board peer pads on  |
| TP4 | F, (95.25, 1116.33), 0° | **B**, (71.48, 30.17), 0° | first clear B pose 0 mm from the centroid (71.48, 30.17) of its 5 on-board peer pads on /MCU_EN |
| TP5 | F, (95.25, 1121.41), 0° | **B**, (83.06, 17.60), 0° | first clear B pose 0 mm from the centroid (83.06, 17.60) of its 2 on-board peer pads on /MCU_BOOT |
| TP6 | F, (95.25, 1126.49), 0° | **B**, (45.12, 35.74), 0° | first clear B pose 0 mm from the centroid (45.12, 35.74) of its 92 on-board peer pads on /+3V3 |

The "from" poses are the input board's off-board emitter positions; R2 never placed these 22. **Side-specific limits recorded:** none for the packages, whose pads, nets and shapes are preserved under the flip. The test points TP1–TP6 are B-side SMD pads; the back render shows them exposed. Assembly/test-fixture access from the back is a downstream decision.

## Whole-board placement checks (309 refs, policy r1 + the authorization)

**Patched `_evaluate_proposal`:** status **`placed`** (`evidence/evaluate-proposal.json`, `placement-judgment.json`). It passed every gate:
- pad inventory equals the declared-transform expectation (unflipped: exact);
- saved sides equal the declaration;
- native courtyard DRC overlaps: **none**;
- polygon judge **pass**;
- placement groups satisfied;
- electrical locality **info** (no failure);
- netlist binding;
- reserved area;
- custom-pad geometry.

**`r5_extra_checks.py`** (`evidence/extra-checks.json`):
- all 9 sourced-fixed poses (H1–H4, J1, J2, J3, U1, U2) are **unchanged**, including side;
- the placer's own `_fits` edge test finds **0 movable parts** within 0.5 mm of the outline;
- exactly the 22 authorized refs changed side; J3 was already on B.

## Preservation (`evidence/checks.json`, native pcbnew, input vs saved)

**309 footprints** (305 electrical + H1–H4), **235 nets**. All of these are **true**:
- same reference set;
- same FPID and value for every ref;
- same pad→net mapping for every pad;
- same net set;
- J1 `PodConnector:AMPSEAL_35_1-776163-1` (1-776163-1) pose unchanged;
- mounting holes unchanged;
- **4 Cu, 1.6 mm**;
- `(stackup …)` block byte-equal;
- `(setup …)` block byte-equal (`aa04823b…`);
- tracks/vias 0 and zones 2, as in the input.

The project and rules files are the original bytes. Pad UUIDs, numbers, nets and shapes are enforced by the admission gate.

## Native DRC, schematic parity, unconnected (kicad-cli `--severity-all --schematic-parity`)

| | Input (`evidence/drc-before-input.json`) | Saved board (`evidence/drc-after.json`) | Delta |
|---|---|---|---|
| Violations | **21** | **80** | +59 |
| courtyards_overlap | 4 | **0** | **−4 (resolved)** |
| lib_footprint_mismatch | 3 | 3 | 0 (inherited) |
| text_height / text_thickness | 7 / 7 | 7 / 7 | 0 (inherited) |
| **silk_overlap** | 0 | **35** | **+35 new** |
| **silk_over_copper** | 0 | **27** | **+27 new** |
| **silk_edge_clearance** | 0 | **1** | **+1 new** |
| Schematic parity | 0 | **0** | 0 |
| Unconnected | 499 | 499 | 0 (no routing yet) |

The admission's item-level comparison (`evidence/native-drc-comparison.json`) agrees: **63 open defects, all `placement_silkscreen_conflict`; 0 blocking findings.** The 17 inherited findings are unchanged, and the 4 input courtyard overlaps are gone. The 63 silkscreen conflicts are reference/value text and silk outlines against copper and each other in the denser layout. They do not affect copper, clearances or courtyards, but they remain open findings to fix (for example by relocating silk text) before fabrication.

## Renders (candidate-bound: board sha256 prefix 8f3bc2343055)

`render/candidate-8f3bc2343055-front.png` and `render/candidate-8f3bc2343055-back.png` (kicad-cli `pcb render`, quality basic).

## Carried

These remain open: BLE, the 29 unknown rows, J1 plug, sourced-none, all electrical/thermal/RF/mechanical qualification, and the 20 open staged envelope items. The provenance gaps recorded in R1 also remain open: the J1/U1/U2 poses, H1–H4, the outline and the antenna keepout have no recorded source. Next per the plan: one bounded routing attempt, agent-521's decision.
