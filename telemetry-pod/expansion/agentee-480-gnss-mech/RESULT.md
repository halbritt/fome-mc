# AGENTEE-480 — GNSS binding and mechanical input closure

**Delivered: provisional placement data and executable checks. The board is unchanged and is not mechanically or RF qualified.** Production consumption is proposed for AGENTEE-479; no agent-ee/planner code or existing input was edited. All files are confined to this directory, disjoint from AGENTEE-478 and the block/allocation/relationship data. Agent-449 alone integrates and relays this result through 519.

Clock: **2026-10-23T09:09:14Z** start; end/elapsed in `task-finish.json`, within the 60-minute bound. Source: exact Cairn `5bfc7b7a-9520-4e85-a94f-ee53caa5e630@1`, AGENTEE-480 under owner-authorized AGENTEE-472. Owner answers `fd5bea71` are applied **as relayed in that assignment**, not promoted to owner-authored text. The worktree starts at `fa41e4b9` (AGENTEE-477 evidence), includes the frozen AGENTEE-474 package from `7be86549`, and uses the unchanged ROUTE-3 PCB:

`0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651`.

The current production source remains 449's binding responsibility. This is not a claim that these proposal files have already repaired the producer or a board.

## GNSS: topology and reference definition

The bound RF terminals are **U3.11, D3.1, L3.2 and J2.1**, all on `/POD_GNSS_RF`. **C42.1 → L3.1** is `/ANT_BIAS`; C42.2 and D3.2 are GND. C42 is the bias bypass, not a series RF element. The definition binds footprint UUID/libID, pad UUID/number/net/shape, pose, project hash, four-layer stack and current edges. Missing/duplicate pads, changed nets, wrong face or unsupported launch cases fail loudly.

`gnss-corridor.json` contains a **proposal**, derived from current component/edge geometry. U3's escape follows its local-left RF-pin side to outside its native F courtyard; an elbow follows J2's RF-pad ordinate. D3/L3 RF taps are separate branches. Current main coordinates are:

`U3.11 (49.35,18.7514) → (47.8375,18.7514) → (47.8375,28.0) → J2.1 (86.96,28.0)`.

This finite corridor sketch is not an autorouted path or a feasibility claim. Other blocks may need moving around it. Cardinal U3 rotations are supported; this initial connector binding supports J2's existing **F/180°/right-edge** launch case. A different launch/orientation needs a reviewed source binding, not a guessed datum. The J2 datum is actual pad copper max-X plus D-PCB-4's 0.50 mm; it matches the current right edge exactly.

The inherited engineering RF width is **0.335 mm** (`design-rules/constraints.json:96–98`). The proposal reuses the current project's **0.20 mm Default clearance**, explicitly labelled an existing default, not a new margin or manufacturer RF minimum. The line reservation radius is therefore `0.335/2 + 0.20 = 0.3675 mm`, plus the actual RF terminal pad shapes. This does not prove impedance or define a new universal return-current width.

The final reference exclusion must cover **both the pose-derived proposal and actual saved RF-copper projection**. Its native In1/In2 rule forbids tracks and vias; the separate **In1 whole-outline no-tracks rule allows vias elsewhere**. Neither pads nor ground pour are globally forbidden by D-PCB-6. `legacy-rule-baseline.json` retains the exact old rectangle and flags, unchanged; it is historical evidence, not proof that it follows the new RF path. No old rule was removed, shrunk or re-saved here.

After every placement/route change: extract the actual new board and native terminal receipt, rederive, and invalidate previous masks/check results. Copying old materialized XY fails the binding check. A changed board/project on disk is rejected even if an old observation JSON is supplied. Definition tampering also fails. Height evidence requires separate part-binding requalification before transfer; the baseline mechanical materializer deliberately refuses another board identity.

## What proves F-over-In1, and what the saved board actually shows

`check_constraints.py` requires all of the following; it cannot infer a pass from an airwire picture or a named rule area:

- One connected **F-only** RF copper component containing every terminal's interior witness, with no RF vias/non-F tracks and the inherited minimum physical width.
- Matching same-board native terminal equivalences for RF and all U3/J2/D3/C42 GND returns. The retained native receipt verifies serialized pad/net assignments; the extraction matches its **complete pad inventory**, not just four selected names.
- One **saved GND fill component on In1** covering the actual RF projection and physically touching an In1 pad in that native GND-return group. A GND-named zone, absent fill, or a floating island is insufficient. Net names are exact: `GND` is not silently equated with `/GND`.
- Actual native RF-reference rule coverage over the proposal and actual RF projection; whole-outline In1 no-tracks/vias-elsewhere semantics; no protected-region via/inner-track incursions; correct J2 edge datum.

The actual ROUTE-3 result is **FAIL**, with these observations:

| Observation | Result |
| --- | --- |
| F RF copper components | **3**; terminals not all connected on F |
| Native RF terminal groups, all layers | **2**: U3/D3/L3 together, J2 separate |
| RF non-F/via objects | **12** (10 B tracks, 2 vias) |
| F RF tracks below inherited 0.335 mm | **9**, each 0.20 mm |
| Saved In1 GND fill | **Absent**; only the two board-owned rule areas exist. Reference continuity is **UNKNOWN**, not a measured plane-void area. |
| Native GND-return coherence | Required returns do not form one group; full GND has 30 terminal groups |
| Proposed protected region | 8 via and 21 inner-track incursions; new source binding is not applied |
| In1 no-tracks area / J2 datum | Existing rule semantics and current edge datum pass these scoped checks |

The project also has only a Default net class and no RF_50 assignment. Its custom `A.NetClass == 'RF_50'` width rule is therefore ineffective for this net. `consumption-contract.json` requires a direct net selector or explicit RF_50 binding when 479 consumes the inherited width. No project rule or clearance was changed in this task.

`check-controls.json` records **17 passing controls**. They include stale pad/edge data, definition changes, topology poisoning, translated rebinding, split native groups, a missing F bridge, a B-layer bridge, a ground void, absent fill, a foreign-net “GND” fill, a reference via and conflated plane/via semantics. The idealized positive case is **synthetic data only**. It establishes that the predicates can pass; it is not a PCB, route, native result or physical acceptance. The real-source CLI explicitly rejects synthetic observations. The actual native board remains FAIL.

The checker is an artifact verifier, not an installed producer feature. Its polygon operations use native saved shapes and conservative terminal witnesses; final native ERC/DRC/parity/connectivity and independent electrical/RF validation remain required. It does not prove impedance, antenna matching, reception or installed performance.

## Mechanical selections and status of the P constraints

The exact owner quotes, relayed in60ee73db@1, are recorded separately in `owner-quotes.json`: **“Pogo clip on bench”**, **“Once, on the bench”**, **“90mm height, the length and width are quite a bit more than that”**, **“Agents pick M3 hardware”**. `owner-answers.json` contains the engineering interpretation. These answers settle usage and selection only; they supply no geometric clearance PASS. Published/measured dimensions and final collision checks remain required. The selected-tip scoped result below comes from the explicit tip/pad geometry and observed-board collision checks, not the usage quote. Final-coordinate candidate qualification remains separate.

`keepouts.json` has **40 per-face reservations**, anchored to footprint/pad references with source/class/phase/Z fields. Z is outward from each face. No arbitrary edge margin was added, and the prior 0.5 mm courtyard-edge / 0.25 mm courtyard-gap defaults are unchanged. Correction b1987334@1 relays the owner: **“90mm height, the length and width are quite a bit more than that”**. Use **~90 mm as the provisional available vertical envelope**, an owner estimate rather than a measured hard cap; no measurement task. Length/width exceed90mm, so the90×65 outline is not cowl-constrained. No12mm height cap returns. The entire installed vertical stack—including floor/lid, M3 supports, board, both-face parts, J1 body plus harness and J2 SMA plus cable bend—must fit that provisional height. `height-stack-check.json` remains **UNKNOWN** with no stack upper bound/headroom because material terms are absent; the known subset cannot prove fit.

| Constraint | Closed definition/data | Still open or failing |
| --- | --- | --- |
| C01, C18 | Both component faces permitted; no equal-count target; existing margins retained and classified | Final eligibility/whole-block relationships belong to 478/479 |
| C03/C04 hardware | **Chosen:** M3×8 ISO7380-1 A2 button-head screw, ISO7089 A2 washer, Harwin **R30-1611200 Nylon66** M3 female/female 12 mm standoff. Both faces have dimensioned hardware reservations. | Current placement overlaps reservations; exact driver bend/tolerances, enclosure attachment, thread engagement, preload/retention, nylon creep and motorcycle vibration remain unqualified. Selection does not establish IP67. |
| C20 pogo access | **Closed for the selected tip model/workflow:** handheld clip on bare board before enclosure, B pads allowed, BLE OTA afterwards. No fixture/post-seal access. Normal approach uses the full Ø1.5 pad landing locus plus a sourced Ø0.64 tip: radius **1.07 mm**, with no extra allowance. | A different/larger clip or approach requires rebinding. This scoped pass is not full mechanical acceptance. |
| C21 solder jumpers | Owner's one-time bare-board workflow applied. F pad-relative approach polygons use a sourced **1.3×0.4 mm** chisel tip; no post-seal opening. | **OPEN/provisional:** full hot taper/barrel and solder-feed/hand envelope not sourced. Tip-only data must not pass complete iron-access qualification. |
| C19 heights | Per-reference table for all **309** footprints; nine sourced package maxima, two nominal-only entries, 15 no-component-body features | **283 body heights UNKNOWN**; all final assembly heights/tolerances require qualification. Unknown never means zero or PASS. |
| C09–C13 connectors/card/antenna | Existing 474/477 source evidence retained, including six footprint-owned U1/J3 native rule areas and component-relative refresh requirements | Antenna feed/case mapping and installed metal/housing checks remain OPEN. J1 mating/tool, SMA cable/tool, and complete card/hand swept volumes remain provisional where they affect packing. No guessed numeric lane is promoted to MFR. |
| C22 cowl/enclosure | ~90mm provisional vertical envelope;90×65 outline not cowl-constrained; complete installed stack must fit; bench-only service access | Installed fit, sealing, temperature/vibration and RF performance remain release obligations; absent CAD does not prohibit provisional candidate generation |

The selected hardware dimensions are published values, **not owner-chosen dimensions**:

- Screw head maximum **Ø5.7 × 1.65 mm**, 2 mm hex drive; washer maximum **Ø7 × 0.5 mm**, ID3.2–3.38. Their standards and exact Accu technical-table URLs are in `sources/selected-facts.json`.
- Harwin drawing R30-161XX00 issue5, sheet2, gives **12±0.30 mm** and **5.50±0.20 mm across flats** for the chosen standoff. The B body uses max AF5.7, circumscribed over rotation, and max length12.3; washer/body Z intervals are explicit. This is a selected internal mounting arrangement, not fabricated enclosure CAD.
- Driver dimensions use Wiha01393 (2 mm hex, 101/18 mm legs). The thin rotating shaft is separated from the return-arm sweep near the far end; **18 mm is not a PCB-plane clearance radius**. Exact bend datum/tolerance remains explicitly provisional.
- The INGUN probe and Weller tip are engineering-selected **reference envelopes**, not claims about tools the owner owns or authorization to buy them. Manufacturer dimensions, chosen approach and unknown complete-tool geometry are separated.

The B pogo approach check finds no same-face courtyard overlap, selected M3 hardware collision, supported native through-hole pad-bound obstruction or intersection with the conservative J1 below-seat body projection. All 87 drilled pad shapes are supported circle/rectangle bounds. It returns `PASS_SELECTED_TIP_MODEL`, scoped to that physical tip and normal approach only.

The current board has **19 courtyard/reservation overlaps**: H1 with C2/C22/C4/U5 (including the screw-head reservation at U5); H2 with R157/R158/R165/R5/R6; H3 with J1/R156/R159/R163; H4 with J1/R35/R41/R42/R44. These are conservative placement-reservation conflicts, **not claimed physical shorts or native DRC findings**. Another 100 XY intersections need currently unknown heights, mostly for elevated tool volumes; they are not 100 proven collisions. Details are in `mechanical-check.json`. The whole candidate's mechanical acceptance remains **false**.

The A2 hardware near U1 also needs antenna/metal assessment. The retained CAD antenna area alone does not establish Espressif's separate housing-clearance recommendation. No antenna constraint was relaxed to accommodate the hardware.

## Height evidence reused and added

| Ref(s) | Sourced package/body limit | Exact provenance |
| --- | --- | --- |
| L1 / L2 | 4.8±0.2 → **5.0 max** / 5.2±0.2 → **5.4 max** | Reused 477 `RESULT.md:89–90`, `sources.txt` Bourns capture hashes5a7926dd/3f16305b. No reacquisition. |
| U3 | **2.6 max** | Reused 477 `RESULT.md:91`, UBX-19014285 R08. Visualization-only STEP is not a tolerance source. |
| U1 | 3.1±0.15 → **3.25 max** | Retained Espressif datasheetv1.8 p42 Fig10-1, visually checked. The 3.2 mm WROOM-1U dimension is a different variant. |
| U2 | **0.86 max** | Retained ST LSM6DSO32 DocID032891 Rev1 p149 Fig22, visually checked |
| U5/U7 | **1.7 max** | Retained TI LMR36520 DDA0008B package outline, PDFp38 |
| U6/U12 | **1.7 max** | Retained TI TPS7B4253-Q1 SLVSCP3D, DDA0008J-C02, PDFp24 |
| J3 / J1 | 1.68 catalog nominal / 27.77 STEP nominal above support | Upper tolerances UNKNOWN; no maximum inferred |

The 15 bare holes/test pads/jumpers have no component body under 477's classification. Their solder, installed hardware and probe/iron access are separate; a zero body does not certify zero assembled protrusion. Every row binds UUID, value, footprint and source. `build_mechanical_data.py` is deliberately baseline-only: transferring heights to another candidate requires verifying MPN/LCSC and source bindings, not matching reference names alone.

## Consumption by 479 and final-coordinate requirements

`consumption-contract.json` and its proposed JSON schema describe the initial integration surface. 479 must verify the bundle hashes, actual part bindings, selected source classes and pose identities, then consume these as **provisional inputs**. No schema or planner integration has been performed. Existing native footprint rule areas must be freshly read after side/rotation changes; the frozen U1/J3 world polygons are context, not transferable constraints.

At the final saved coordinates, re-extract the same board/project/rules and same-board native terminal evidence. Recompute the RF mask and all hardware/probe/iron reservations, with correct faces and phase. Check actual bodies, copper/contact, drilled features, heights and approach volumes, not just footprint centres or a hole courtyard. Report the named unresolved refs, material UNKNOWNs and actual conflicts. Preserve owner-required RF/antenna/interface behaviour; move/reshape/re-side eligible blocks rather than modifying sources or inventing a margin to make a report pass. Full block/relationship and native electrical/manufacturing checks remain additional gates.

Reproduction from repository root (`P` abbreviates this directory):

```sh
P=telemetry-pod/expansion/agentee-480-gnss-mech
native-admit run --class suite --weight 4 --label agentee-480-read --max-wait 60 -- \
  /usr/bin/python3 "$P/extract_native.py" \
  telemetry-pod/expansion/route-3/candidate/telemetry-pod.kicad_pcb \
  telemetry-pod/expansion/route-3/attempts/2/validate/candidate-terminal-components.json \
  "$P/native-observation.json"
/usr/bin/python3 "$P/check_constraints.py" derive "$P/native-observation.json" "$P/gnss-corridor.json"
/usr/bin/python3 "$P/check_constraints.py" check "$P/native-observation.json" "$P/gnss-corridor.json" "$P/rf-check.json"
```

The final command exits **2 for this documented design failure**; malformed/stale source evidence raises an error rather than a pass. `check_controls.py` exits0 for its predicate controls. These do not replace native DRC. The initial inspection reservation timed out after60 s; the later native reads were admitted at weight4, with no budget increase (`native-operations.json`). There are no live compute handles, new agents, routing, purchases, uploads or cloud operations from this task.

C08 remains OPEN: the later agent-449 coordination note e360ae17@1 reports a J1 mating-plug model/drawings forwarded for transform/harness work. That queued follow-up is not performed or claimed closed in this bounded package; the mated transform, full plug/tool sweep and harness bend envelope remain provisional. No STEP bytes are committed.

No new owner question is needed. Material OPEN items are engineer/source/consumer work listed above; any concrete future owner-reserved change goes through 449→519. Unknowns are retained only in provisional output and cannot receive placement/mechanical/release acceptance. Source hashes, doctrine provenance, task clock and `SHA256SUMS` accompany the package.

Post-delivery source correction: notice b1987334-6363-413b-b1a4-d2666284142b@1 was delivered after the initial25283560 package had been integrated by449. This correction updates only provisional envelope data/prose and the mechanical data materializer; original checks remain scoped to the same unchanged PCB. No second Cairn response is sent. The correction is retained as an unmerged follow-up for449.
