# AGENTEE-478: data and source prep for the AGENTEE-472 block repair (D1-D5)

Assignment: agent-529 decisions D1-D5 via agent-519 (Plane AGENTEE-478 under AGENTEE-472; the implementation is AGENTEE-479). These are coordinator records, not owner text. This is data and source prep only: **no agent-ee planner, adapter or placer code was touched**, and no board was mutated, routed or saved.

## Run record

**Clock:** started 2026-10-23T09:05:38.47Z, ended 2026-10-23T09:22:24Z (about 17 minutes), within the 60-minute bound.

**Model:** Claude Opus 5.5 (`claude-opus-5-5`), the existing pod-capture-j6b2 writer.

**Host:** proximal.

**Disclosure:** the brief asked for this input record before work began. I wrote it at the end. The values were captured at the start: the main tree export ran at 09:06, and the hashes were taken then and re-verified at 09:21.

**Inputs (frozen, read-only):**
- fome-mc main `fa41e4b93ab03d88c2f0d17320016371325a3726`, exported with `git archive` to a scratch copy.
- Emitted design (emission-7d5b0d4d; the main `telemetry-pod/` copies are byte-identical):
  - schematic `telemetry-pod.kicad_sch` `f5840ecc8a44a2e36cd05da9c3a14d80074919f441c3ef73a107dc98d5aea6a2`;
  - board `telemetry-pod.kicad_pcb` `2f1c955704ab1fb38217c24cbaf5a45f4219a74a6a2309be710452c54db3b673`.
- Allocation `expansion/blocks/allocation.json` `434a9984f52eda3121313171fb69321d22e14ae9ff0679a0e8fabadd20cd8ec9`.
- Evidence directories, by the sha256 of each one's SHA256SUMS. All verify with 0 failures.

  | Directory | SHA256SUMS sha256 |
  |---|---|
  | `agentee-473-trace` | `3e217f72…` |
  | `agentee-473b-rust-trace` | `a6e2e02b…` |
  | `agentee-474-constraints` | `97b221e2…` (`native-geometry.json` `299f1daf…`) |
  | `placement-r5` | `140cf200…`, board `8f3bc234…` |
  | `route-3` | `219ab5e8…`, board `08066170…` |

- Also read:
  - `released-source-migration/emitter-layout.json` `261f1c3b…`, the schematic functional groups;
  - the emission `composition/placement-policy.json` `5fab430a…`, the 12 old obligations;
  - the 13 retained datasheet PDFs, each hashed in `relationship-bounds.json` → `sources`.
- **Not consumed at 478 time; applied in 478b (below):** agent-ee `b7c72f6e` (plan docs) mentions "owner answers to the 474 unknowns". They arrived after the frozen inputs. AGENTEE-478b applies them from agent-529's notice (Cairn `a13a1ba8…` v1).

**Runtime:** pcbnew 10.0.7 read-only extraction (`extract_pins.py`, `LoadBoard` with no save; each board's hash is re-checked after loading). The `kicad-cli sch export netlist` run on a scratch copy of the emitted schematic used native-admit leases `4c3b99deaa3c` and `a3ee1e0d909b` (`logs/native-admit-events.jsonl`). Everything else is stdlib Python over the extracts. No docker, AppArmor, cloud, upload or review.

## D1: allocation v2 (`allocation-v2.json`)

**Coverage:** **309 of 309 captured exactly once**: 293 members of 24 blocks, 10 fixed and 6 shared. There is no residual, root-sheet or implicit bucket.

The 37 former residual parts:
- **Fixed, with 474 entry IDs:** J1 (C05–C08), J2 (C09), J3 (C10/C11), U1 (C12/C13), U2 (C14), U3 (C15), H1–H4 (C03/C04).
- **Shared (test):** TP1–TP6.
- **New small blocks:**
  - `gnss-antenna-supply`: U10, R24, R25, R26, C42. The DC active-antenna bias chain.
  - `gnss-rf-feed`: L3, D3. These sit on the RF line itself.
  - `storage-support`: R46–R50, R55, C64, C65, anchored on the fixed J3.
- **C18** goes to `pre-6v3`. It is on /PRE_6V3, the U5/L1 output node; U7 is not on that net.
- **R33** goes to `mcu`. It is the IO46 strap of the fixed U1; `mcu` is U1's support block, anchored on the fixed U1.
- **C38, C41, C43, C44** go to `buck-3v3`. The emitted schematic draws them in the "3V3 regulator (U7) and 3V3 bulk" group, on /+3V3 with no per-load binding. The old fifth fix removed them because of where an earlier placement put them, not because of what they do.

**Corrections to the existing 18 blocks**, from the actual emitted netlist (evidence is in `corrections[]` and in `d1-verification.json`, the non-rail connected components):
1. **`supervision` split into three independent blocks:** `supervisor-3v3` (U16), `supervisor-5v-sensor` (U18) and `supervisor-12v` (U19). They watch different rails and share only rails; U18 and U19 are unreachable from U16 on non-rail nets.
2. **`afe` loses U9, R22, R23, C39 to a new `sensor-ref` block.** U9 buffers the 2.5 V ADC reference into U4 Vref. On non-rail nets it is unreachable from U8.
3. **`aux-afe` loses the ADC CH4–7 input RC to `adc`:** R36, R39, R42, R45 and C55, C57, C59, C61. These have the same topology as the CH0–3 RC, which is already in `adc`; the 100 pF capacitor is the sampling reservoir at the U4 pin.

**Every member is justified** (`d1-verification.json`, 0 unjustified). Each one is either connected to its block's core on non-rail nets, bound to a device pin by a D3 relationship, or linked to its block's fixed anchor.

**Validator:** `validate_coverage.py` checks coverage and cross-file references; `coverage-report.json` is its output.
- Result: **PASS**: 309 footprints, **0 unassigned, 0 duplicates**, 0 unknown references.
- The other checks also pass:
  - the board-only parts are exactly H1–H4, all fixed;
  - every schematic symbol is on the board;
  - the anchors are valid;
  - there is no implicit bucket;
  - eligibility covers every block, fixed and shared part, and cites only C01–C23;
  - all 219 relationships bind real pins and nets;
  - every template instance and fixed rule resolves.
- **Negative test:** a copy with U5 duplicated and C30 removed exits 1 and fails on duplicates, unassigned and coverage.

## D2: side eligibility (`side-eligibility.json`)

- **Default:** every block may use either face (C01; no count balance and no quota).
- **Face restriction:** `gnss-rf-feed` is **F only** (C15). The RF line must run on F.Cu over In1 (R:65), and U3 and J2 are on F. Recheck this once C15 is reconciled.
- **Region restrictions** apply to a face and region, not to a whole face:
  - C12, all layers: the U1 antenna area, for `mcu`.
  - C10/C11, B: the J3 card lane and rule areas, for `storage-support`.
  - C06, B: the J1 PTH pin field, for the 11 blocks around J1.
- **Material unknowns carried per block:**
  - C19: heights, both faces. The owner cowl estimate (C22) is context only, not a per-face budget (478b).
  - C22: enclosure. The owner estimate is about 90 mm of provisional available HEIGHT for the full stack (enclosure floor and lid, standoffs, board, both-face parts, connector bodies, cable/harness). It is not a measured rigid cap. Length and width are substantially larger, and the outline has no numeric cowl constraint (478b, corrected per a13a1ba8 v2).
  - C04: H1–H4 hardware is M3, selected by agents (owner answer). The envelope radius stays UNKNOWN on both faces, pending AGENTEE-480 (478b).
  - C23: thermal, for the regulator, MCU and switch blocks.
  - The opposite-face area under the U5/U7 exposed pad is reserved for thermal vias (LMR36520 p28 item 7); its size is UNKNOWN.
- **Fixed parts:** ~~each keeps a single face~~ (superseded by 478c): a fixed role is not side authority. Each part separates sourced restrictions, an AGENT engineering anchor and the captured starting pose; U2's face is OPEN for 529.
- **Test and assembly access plan (`test_assembly_access_plan`):**
  - TP1–TP6 (corrected in 478b): hand-held pogo clip or probes on the bare board before enclosure (owner: "Pogo clip on bench"). Either face, bottom allowed. No fixed fixture pattern, no common-face or grouping requirement, no post-seal access. A common face or grouping is at most a labelled, optional engineering convenience. The earlier "one fixture head / 25 mm grouping" assumption is withdrawn.
  - Probe-tip approach clearance only (no tall part or screw hardware over or around each pad). Its size is UNKNOWN (C20); never PASS.
  - JP1–JP5 follow their blocks. One-time soldering-iron access on the bare board before enclosure (owner: "Once, on the bench"); the access-zone size is UNKNOWN (C21).
  - **No owner-reserved fixture constraint.** The owner decided usage (bench clip, before sealing); clearance geometry is engineering and still UNKNOWN.

## D3: relationship bounds (`relationship-bounds.json`)

**Scope:** 219 relationships, each giving the exact device pin and the support part's pad on the same net. The relationships cover:
- decoupling, including input and bulk capacitors, hot loops, VCC and LDO capacitors;
- feedback, bootstrap and the switch-node inductor;
- crystal and load capacitors;
- ESD (measured both at the transceiver and at the J1 pin) and termination;
- input and sampling filters, and sense and timing networks;
- reference capacitors;
- strap, enable and RC pulls on critical lines.

I2C, chip-select, interrupt and SD pull-ups are treated as non-critical and left unbounded.

**Metric:** 3D pad-centre distance, adding dz = 1.6 mm when the two pads are on opposite faces. The return leg runs from the support's GND pad to the nearest device GND pad. Pad-centre distance is a lower bound on trace length; routed length can only be measured after routing.

**Provenance, per relationship:**
- **MFR**, with retained file, sha256, page and wording. This covers 13 datasheets, for example:
  - LMR36520 p27–28, items 1–4 and 8;
  - TPS7B4253 p19, which requires the same side;
  - ADS1119 p37–38: no vias, same layer;
  - TPS2662 p35, TPS2553 p25, LSM6DSO32 p53;
  - NEO-M9N integration manual p80–81, ESP32 hardware guide p11/p17;
  - MCP3208 p23, OPA320 p28, LM2903B p18, SN74LVC1G132 p14, TL431 p31.
- **TOPOLOGY** reasoning.
- An explicitly labelled **ENGINEERING-JUDGEMENT** entry for every numeric value. **No manufacturer source gives a numeric radius**; they all say "as close as possible".
- The bound classes and their values are in `bound_classes`.
- The numeric bounds have **not been feasibility-tested** in stage A. A bound that proves infeasible is to be reported, not quietly relaxed.

**The 12 old advisory obligations were not hardened** (`old_obligations_disposition`). Each was mapped to its re-derived relationship. Four old supply legs used **U5/U7 pin 3 (EN, tied to VIN)**; the new relationships use **VIN pin 2**.

**UNRESOLVED (13), which block acceptance of those relationships:**
- **RF line (3):** U3.11–L3, U3.11–D3, and J2.1. 474 C15 (RF path and corridor) has not been reconciled.
- **Schematic decoupling gaps (10).** The emitted schematic has **no decoupler dedicated to** any of these pins:
  - U2.8 VDD and U2.5 VDDIO (LSM6DSO32 wants C1 and C2 = 100 nF);
  - U3.23 VCC and U3.22 V_BCKP;
  - U10.1 IN;
  - U4.16 Vdd, U8.4 V+, U9.5 V+;
  - U100.5 VIO;
  - U11.2 Vin.

  Placement cannot satisfy a relationship that the design does not contain. **Proposed alternative, NOT applied; it needs a 529/owner decision via 519:**
  - rebind C38 → U2.8, C41 → U2.5, C44 (1 µF) → U3.23 and C43 → U10.1, instead of the U7 output bank;
  - or add decouplers in a design change.

**Baseline, identical on R5 and ROUTE-3** (routing moved no parts): **43 within, 163 exceeding and 13 UNRESOLVED.** Per relationship, `baseline` records the supply and return legs, the faces and the verdict. Some examples:

| Relationship | R5 measurement | Bound |
|---|---|---|
| U5.2–C3 hot loop | 10.32 / 10.65 mm | 3.0 / 3.0 mm |
| U7.5–R5 feedback | 83.6 mm | 4.0 mm |
| U1.3–R29/C47 EN RC | 40.5 / 37.0 mm | 10 mm |
| Y1 to U20 OSC pins | 4.1 / 5.8 mm | 6 mm (within) |

Opposite-face relationships in R5: 19, from the J3 caps and the R70–R84 side flips.

## D4: cross-face templates (`cross-face-templates.json`)

There are three templates:
- **`decoupler-under-device`:** applies to decouplers and to bias, reference, filter, sense and strap supports. The pin locality is the 3D bound, giving an XY allowance of √(bound² − 1.6²) per instance.
  - Excluded: TPS7B4253 (U6, U12) and ADS1119 (U27–U29), whose manufacturers require the same side.
  - Per-face limits: no overlap with the U5/U7 exposed-pad via field, no part in a native rule area (C11, C12, C16), no part in the J1 B pin field (C06) or the hole hardware zones (C04), and heights UNKNOWN.
- **`same-face-only`:** applies to hot loop, bulk input, bootstrap, switch-node inductor, LDO capacitors and crystal.
- **`whole-block-flip`:** flipping a whole block is not a split.

**Deliberate split versus lost cohesion:** a member on the opposite face counts as deliberate only if all four hold:
- a template instance covers it;
- the device is not excluded;
- its 3D metric is within the bound;
- its XY position is inside the device courtyard expanded by the allowance.

Anything else on the opposite face is lost cohesion. The regression contract is to fail before AGENTEE-479 and pass after it. There are 206 instances.

## D5: fixed and shared rules (`fixed-shared-rules.json`)

- **Fixed parts (corrected in 478c):** each records its sourced restrictions (474 entry and class), its AGENT engineering anchor (reconsiderable, chosen before packing) and its R5/emitted starting poses (start state only), plus adjacent blocks, support relationships and access rules.
  - U3 is **staged off-board in the emitted board**. Its anchor pose is placement-derived (MECH-DERIVED, C15), not sourced.
  - J1, J2, J3, U1, U2 and H1–H4 match between the emitted board and R5.
- **Shared parts:** the TP bench pogo-clip approach rules (either face per pad; a common face is only an optional convenience, 478b); JP parts follow their blocks.
- **Rails:** these are nets, not memberships; they never merge blocks.
- **No flat fallback:** an unlisted footprint is a refusal.

## Proposed schemas (`proposed-schemas.json`; proposed only, AGENTEE-479 consumes them)

**Schemas:** `agent-ee.block-allocation/2`, `fome-mc.side-eligibility/1`, `relationship-bounds/1`, `cross-face-templates/1` and `fixed-shared-rules/1`, each with its intended consumer.

**Stage-A side-variant format: `agent-ee.block-candidate-set/1`, "proposed, pending agreement with agent-524".** 449 routes that agreement through 519.
- It wraps **unchanged** `block-candidate/2` documents, one per eligible face.
- Rust `validate_candidate` (blocks.rs:769) checks an exact key set. Each variant therefore still validates with the existing function.
- The B variant's member geometry comes from the native pcbnew `Flip(LEFT_RIGHT)`.
- Admission checks four things:
  - each variant's face is eligible;
  - the pad inventory equals the native flip of the captured footprint;
  - the member set is the same in every variant;
  - the frame anchor is the same in every variant.
- A plain `/2` document reads as a one-variant set.

**The actual hybrid pipeline:**
- Python does stage-A packing.
- Once AGENTEE-476 ships, Rust is the default for stage B, admission and the residual pack.
- Python stage B and admission are an explicit parity reference only, never a silent fallback.
- Saved-board validation stays in Python.

**Not all Rust.**

## Files

The sha256 of every file is in `SHA256SUMS`.
- **Data:** `allocation-v2.json`, `side-eligibility.json`, `relationship-bounds.json`, `cross-face-templates.json`, `fixed-shared-rules.json`, `proposed-schemas.json`.
- **Reports:** `coverage-report.json` (validator output) and `d1-verification.json`.
- **Scripts:** `extract_pins.py`, `build_prep.py`, `validate_coverage.py`, `d1_verify.py`.
- **Extracts:** in `extract/`: the emitted board, R5, ROUTE-3 and the emitted schematic netlist.
- **Logs:** `logs/native-admit-events.jsonl`.

**Reproduce:**
```
python3 -I build_prep.py <telemetry-pod> extract/emitted-schematic-netlist.json .
python3 -I d1_verify.py . d1-verification.json
python3 -I validate_coverage.py . coverage-report.json
```

## Remaining and open items, none of which are deferred acceptance

1. A 529/owner decision on the 10 decoupling gaps: rebind the bank capacitors as proposed, or change the design.
2. Reconcile 474 C15 (the RF path), which unblocks the three RF relationships and the `gnss-rf-feed` face.
3. Done in 478b: the owner answers are applied to the usage and selection entries. Their geometry (probe/iron clearance, M3 envelope via AGENTEE-480, cowl fit) stays UNKNOWN.
4. Agreement with agent-524 on `block-candidate-set/1`.
5. The numeric bounds are labelled engineering judgement and untested for feasibility; AGENTEE-479 stage A will test them.

## AGENTEE-484: rebinding to the decoupling-repaired design

The 10 decoupling-gap entries are replaced by sourced per-pin dispositions (`../agentee-484-decoupling/dispositions.json`).
- **Inventory:** the regenerated emission, board `0b68a0ac…` with 313 footprints (`extract/emitted-0b68a0ac.json`) and schematic `cef8e4c7…` (`extract/emitted-schematic-netlist-cef8e4c7.json`). The 2f1c9557 extract stays for the R5/ROUTE-3 baselines.
- **Coverage:** PASS. 313 footprints: 297 block members in 26 blocks, 10 fixed, 6 shared; 0 unassigned, 0 duplicates.
- **Relationships:** 214, of which 3 are UNRESOLVED (the RF line, C15).
- **Allocation changes:**
  - new blocks `imu-support` (C38, C41) and `gnss-receiver-support` (C44);
  - C43 moves to `gnss-antenna-supply`, C18 to `supplies-5v`;
  - C130–C133 join `adc`, `afe`, `sensor-ref` and `can`;
  - the U7 output bank keeps C13–C15.
- **Tooling:** `validate_coverage.py` and `d1_verify.py` now read the board extract and netlist declared in `allocation-v2.json` → `inventory`. Schematic-only parts are allowed only when declared.
## AGENTEE-478b: owner physical answers applied (data only)

**Run:** 2026-10-23T09:29:32.43Z to 2026-10-23T09:31:31Z, within the 15-minute bound, directed by 449.

**Single reference:** agent-529's consolidated owner-directions notice, Cairn `a13a1ba8-2838-4044-a40c-fe875b4e83f1` v1 (owner relay fd5bea71@1).

**Rule:** these answers resolve usage and selection only. No geometric clearance is marked PASS; unsupplied dimensions stay UNKNOWN.

**Owner quotes, verbatim** (recorded separately as `owner_answer.quote` in the data):

| Entry | Quote |
|---|---|
| C20 | "Pogo clip on bench" |
| C21 | "Once, on the bench" |
| C22 / C19 | "I'm sure it's ~90mm or more." (fd5bea71@1); correction: "90mm height, the length and width are quite a bit more than that" (27c51f73@1) |
| C04 | "Agents pick M3 hardware" |

**Engineering interpretation** (`owner_answer.interpretation`):
- **C20:** a hand-held pogo clip or probes on the bare board before enclosure. Bottom-side TPs are allowed, BLE OTA is used after sealing, and there is no fixed fixture pattern and no post-seal access. Only probe-tip approach clearance is reserved: no tall part or screw hardware over or around the pads. Its size is UNKNOWN.
- **C21:** one-time soldering-iron access on the bare board before enclosure.
- **C22 / C19 (per a13a1ba8 v2, which supersedes the v1 cowl paragraph):** about 90 mm is the provisional available **HEIGHT**, an owner estimate and not a measured rigid cap. It covers the full vertical stack: enclosure floor and lid, standoffs, board, both-face parts, connector bodies, and cable/harness. Length and width are substantially larger, with no numeric outline constraint. Final fit stays with bench/install verification. The per-face height budget remains UNKNOWN; no clearance PASS.
  - The earlier v1 "unspecified dimension" reading, and the discrepancy note about it, are superseded; they remain in git history (`93adc6c`).
- **C04:** M3 hardware, selected and sourced by agent-507 in AGENTEE-480 (pending). The selection is not duplicated here; the head/washer/standoff/driver envelope stays UNKNOWN on both faces until AGENTEE-480 supplies it.

**Changed entries (before → after):**

| File / entry | Before | After |
|---|---|---|
| side-eligibility `shared.TP1-TP6.constraint` | all six on ONE common face (single-sided programming fixture), chosen by the planner | either face per pad (bottom allowed); probe-tip approach clearance reserved on the probed face; no fixed fixture pattern, no common-face requirement |
| side-eligibility `shared.TP1-TP6.material_unknowns[C20]` | probe tip / approach travel / fixture pin height / support force / tool clearance | probe-tip / pogo-clip approach clearance dimensions (no tall part or screw hardware over or around each pad); size not supplied |
| side-eligibility `test_assembly_access_plan.rules` | one common face; "pad within 25 mm (EJ) … one fixture head"; probe keep-clear UNKNOWN; "fixture support area UNKNOWN" | REQUIRED: hand-probe/clip reach on the bare board, either face. REQUIRED: approach clearance, no tall part or screw hardware, size UNKNOWN, never PASS. NOT required: fixture pattern, common face, grouping, post-seal access. Labelled optional ENGINEERING CONVENIENCE: one face and nearby pads, as a tie-break only. The U1 antenna / J3 card-path rule is kept |
| side-eligibility `test_assembly_access_plan.purpose` / `.JP1-JP5` | factory programming before sealing / during assembly before sealing | bench pogo clip before enclosure, BLE OTA after, no post-seal access / once, on the bench, bare board before enclosure |
| side-eligibility `shared.JP1-JP5` | solder-iron access before sealing; unknown: tool angle / access footprint / timing | one-time soldering-iron access on the bare board before enclosure; unknown: access-zone size (timing decided) |
| side-eligibility `blocks.*.material_unknowns` C04 ×4 | radius UNKNOWN; envelope UNKNOWN | M3 hardware (owner); radius and envelope UNKNOWN pending AGENTEE-480; no clearance PASS |
| side-eligibility `blocks.*.material_unknowns` C19 / C22 | heights / "enclosure / cowl / harness envelope" | the same UNKNOWN, plus the owner estimate as context (about 90 mm provisional available HEIGHT for the full stack, not a measured cap; length/width substantially larger; outline not cowl-constrained) |
| fixed-shared-rules `fixed.H1-H4.access` | hardware envelope UNKNOWN F/B (C04) | M3 hardware (owner: "Agents pick M3 hardware"); envelope UNKNOWN F/B pending AGENTEE-480 (C04) |
| fixed-shared-rules `shared.TP1-TP6` | side_rule: one common face, either | adds `access` (hand clip/probes, approach clearance only, no fixture pattern, no post-seal access) and `owner_answer`; side_rule: either face per pad, common face only an optional labelled convenience |
| fixed-shared-rules `shared.JP1-JP5` | role / membership / side_rule only | adds `access` (one-time iron access on the bare board before enclosure, zone size UNKNOWN) and `owner_answer` |
| RESULT.md:35, 82-84, 89-92, 218 | as written in 478 | corrected to the above; the earlier text stays in git history (`2ee1e63`) |

**Not changed:** `allocation-v2.json`, `relationship-bounds.json`, `cross-face-templates.json` and `proposed-schemas.json` (content identical). `d1-verification.json` was restored to the committed file: a rerun differs only in set iteration order and is semantically equal.

**Generator:** `build_prep.py` now holds the `OWNER` table and the patched entries, so the data stays reproducible. The validator `validate_coverage.py` was rerun: **PASS**, 309 footprints, 0 unassigned, 0 duplicates, 0 failed checks.

## AGENTEE-478c: role coverage is not side or pose authority (agent-529, AGENTEE-479 comment 5dbeb677, Cairn c228b69f)

`side-eligibility.json` → `fixed.*` and `fixed-shared-rules.json` → `fixed.*` now separate, per part:
- **`sourced_restrictions`:** each cites its 474 entry and class.
- **`engineering_anchor`:** labelled AGENT and `reconsiderable`. It is chosen before packing, and a reconsidered anchor needs final transformed keepout and axis checks (an AGENTEE-479 acceptance item).
- **`starting_poses`:** R5 and emitted poses, labelled "captured start state only, never a constraint".
- **`face_decision`:** stated explicitly per part.

| Part | Sourced restriction (474) | Engineering anchor (AGENT) | Face decision |
|---|---|---|---|
| J1 | right angle (C05 OWNER); +Y mating to the edge (C05 MFR); PTH pattern (C06 MFR) | XY (45, 55.5) rot 0 | F, AGENT, reconsiderable |
| J2 | F.Cu-over-In1 RF launch (C15, R:65); edge launch (C09 MECH-DERIVED) | XY (85.24, 28) rot 180; corridor per AGENTEE-480 | F, sourced via the RF path |
| J3 | card off the left edge (C10 OWNER); socket areas (C11 MFR) | XY (8.9, 32) rot 90 B, lane | B, AGENT, reconsiderable |
| U1 | antenna case and overhang (C12 OWNER); land pattern (C12 MFR) | XY (72.5, 6.5) rot 0 | F, AGENT, reconsiderable |
| **U2** | **REQUIRED axes X fwd / Y left / Z up, no software rotation (C14, R:69)** | XY (12, 10), historical; no source for XY or F-only | **OPEN for 529:** U2 must be on the face that points up when installed; the installed orientation is UNKNOWN (C14/C22); F is only a labelled AGENT start |
| U3 | F.Cu over In1 REQUIRED (C15, R:65) | corridor and anchor per AGENTEE-480 (agent-507), not duplicated | F, sourced |
| H1–H4 | corner holes (C03 OWNER); M3, agents pick (C04) | XY at the 4 mm corners, AGENT | n/a (NPTH, both faces) |

The 478b owner answers (commits `93adc6c` and `6e0aea2` on the j6b2 branch) were carried onto this branch so the data is coherent. Validator: PASS, 313 footprints, 0 unassigned, 0 duplicates.
