# AGENTEE-473: two-level block placement and production side locking — read-only trace

Source: chief coordinator agent-529, brief 65ab387e (via agent-519); parent AGENTEE-472. These are coordinator records, not owner text.

**Clock:** started 2026-10-23T08:35:19.70Z, ended about 08:43Z, within the 45-minute bound.

**Correction, 2026-10-23 (AGENTEE-482, answering agent-510 HOLD fc3488f4).** This report was corrected in place; the prior text stays in git history (writer commit `fa5eb02`, landed as fome-mc `4ff731c`). The changes:
- **H1:** placement groups and electrical locality are now separated in §1 and §2. Groups are enforced; locality is soft. The policy/enforcement discrepancy is recorded.
- **H2:** the congested-underside regression contract in §4 is strengthened. It is a specification, not an executed test.
- **H3:** settled permission questions are removed. An acceptance/dependency map is added (§5).
- **Minor:** the spread metric and the emitted minimum spread are corrected.

No production change, board mutation, test or suite was run for this correction.

**Read-only.** No board was mutated, nothing was routed, and no full suite ran. There was one admitted reproduction container (`native-admit-events.jsonl`). This removes uncertainty; it is not board acceptance.

**Frozen inputs read:**
- **agent-ee** `39924b46196dbd03f283fabece91766a007e94db`, which is current origin/main.
- **The R1–R5 runtime:** the archived 7d5b0d4d step snapshot (`placement-r1/run/work-r2/step/tool`), plus the R5 overlay `placer_runner.py` `b4be6263…`. File hashes are in `runtime-identities.txt`. `blocks.py`, `block_arrangement.py`, `placement_groups.py`, `electrical_locality.py`, `forward_annotation.py` and `placement_probe.py` are **byte-identical** in both. `placer_runner.py` at 39924b46 **is** the R5 patch (`b4be6263`). `placer.py` differs only by the AGENTEE-249 capacity-proof default. So current code explains the old execution, apart from that.
- **fome-mc** `46c7c730141c956cd94970cc130cdea660e23e03`.
- **Boards:**
  - emitted input `2f1c9557…`;
  - R5 `8f3bc234…`;
  - ROUTE-3 `0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651`.

## 1. Stage-by-stage source evidence (agent-ee 39924b46 unless marked; fome-mc 46c7c730)

| Stage | What exists | What production R1–R5 actually did | Evidence |
|---|---|---|---|
| **Block definitions / membership / shared nets** | `blocks.derive` takes blocks only from **top-level child sheets** or a **hashed engineer allocation**. Each footprint is in exactly one block or the residual. Membership is by sheet or reference, so **shared supply/ground nets never merge blocks**; net roles only flag boundaries. Unclaimed root-sheet parts become residual silently (`root-sheet`); explicit membership is not required. | The emitted schematic is **flat** (1 sheet `/`, all 305 parts). No allocation was passed, so **0 blocks** resulted and every part was residual. fome-mc `blocks/allocation.json` (`434a9984…`: 18 blocks, 272 members, all present on the emitted board; C18 and R33 unclaimed) was **never used by production**. | `blocks.py:1-11, 117-200` (root-sheet residual `:186-188`; allocation refs `:167-172`); `blocks.py:280` `net_roles`; `repro.json` `derive_without_allocation` / `derive_with_allocation` |
| **Initial micro-placement** | Stage A `blocks.pack_block`: each block is packed alone by the unchanged placer around its anchor, on its **captured side**: "a member keeps its captured side; a block is not mirrored in stage A". | **None.** Forward annotation stages every non-fixed footprint in an off-board column ordered by reference, front side. `board_build.construct` flips only envelope-fixed B parts (J3). The emitted per-block spread (footprint-origin bounding-box diagonal) is **95.25 mm** (power-entry) to 1160.78 mm. | `blocks.py:478`; `docs/blocks.md:345-351`; `forward_annotation.py:32-34, 264-280`; `board_build.py:336-353`; `repro.json` `boards.emitted` |
| **Macro / global placement** | Stage B `block_arrangement.arrange`: rigid macros, deterministic ranked first fit with conflict backjumping. It tries **rotations 0/90/180/270 only**; `macro['side'] = members[0]['side']`, so the side is the captured side. Opposite-side **shadows** are keepouts, not side choices. | **Bypassed.** The campaign adapter declaration accepts optional `blocks` (`placement_adapter.py:190-226`, identical in 7d5b0d4d), but fome-mc `pipeline.py:975-976` declares none. The placer therefore ran the flat `placer.pack` (`ranked-first-fit-backjump/1`; R1c/R2 `placement-result.json`). | `block_arrangement.py:1-12, 276-305, 324, 785, 1048`; `placer_runner.py:887-897` (`blocks` dispatch); fome-mc `production-capture/pipeline.py:962-963, 975-976` |
| **Side candidates / eligibility vs immutable side** | **No packing path chooses a side.** `placer.transform` = translate + quarter turns only. The capture side is read from the native layer. Plan placements carry `position_nm` and `rotation_deg` only. Stage B uses the captured side. The only side-change capability is the R5 write/admission correction (`_side_changes` / `_flipped_inventory`), which needs an explicit request authorization; **no planner produces one**. | R1–R4: side is immutable, and the front fragments (R3: 391 mm² free in 69 fragments; R4 stopped at the interface). R5: 22 leftovers flipped **by coordinator brief**, with poses chosen by a net-centroid script. | `placer.py:92-118, 322, 2380, 2470`; `placement_probe.py:447, 559`; `block_arrangement.py:324`; `placer_runner.py:678-745` |
| **Legalization / residual** | Stage B packs the residual with `placer.pack` and **every block member fixed**. Flat `placer.pack` = ranked first fit with backjumps. No reshape, re-side or block split. | R1/R2: global flat pack, budget- or time-exhausted, peak 283–287. R3: existing placer on 22 missing parts plus 25 released neighbours; exhausted. | `block_arrangement.py:1259-1280`; `placer.py:2103, 2185, 2366-2434` |
| **Write / admission** | `_apply_plan`, then `_evaluate_proposal`: pad-inventory identity (now with declared flips), native courtyard DRC, judge, groups, locality, block rules (**only when the plan came from a block arrangement**), netlist binding. | R5 admitted 309/309 with judge pass. **No block rules were graded** (the plan had no `block_arrangement`). | `placer_runner.py:733-745, 746-779` (`block_rules` `:767`, hard-rule gate `:832`), `:781` |
| **Routing feedback** | None integrated: the placement context reports `routing_feedback: unavailable, 'no captured AGENTEE-93 routed-attempt receipt is integrated'`. AGENTEE-391 (M6 bounded placement↔routing feedback) is **not completed**. | ROUTE-1/3: router blockers (D-PCB-7v2 keepout, J1, U6, U1 …) never returned to placement. | `placement_adapter.py:1866-1868`; Plane AGENTEE-391 (completed: none) |
| **Final-coordinate validation: placement groups** | Groups (7 anchor radii, all unsourced) are **ENFORCED**, both in search and in the final grade, despite their advisory label. Python: `placer.py:1902-1906` rejects a candidate outside a group region or tie radius; `:1947` builds the search window from them; `:2447-2449` stops the complete proposal when `placement_groups.satisfied` is false. Stage B: `block_arrangement.py:894-907` returns `'group'` conflicts. Rust `groups.rs:227-243`: `satisfied` requires no violation, and an exceeded advisory counts as a violation even at `status=info`. So an exceeded unsourced group bound returns False. | R5: group grading **pass**, **20 measured, 0 exceeded**. Groups held where they were declared; they cover only 7 small clusters. | `placer.py:1902-1906, 1947, 2447-2449`; `block_arrangement.py:894-907`; `placement_groups.py:151`; Rust 6f48b9f2 `groups.rs:227-243`; placement-r5 `evidence/placement-judgment.json` `group_grading` |
| **Final-coordinate validation: electrical locality and block report** | Electrical locality (12 pad-pair obligations) is **SOFT**. It ranks candidates in search (`placer.py:1944-1949`). The final gate rejects only a status other than `pass`/`info` (`placer.py:2451-2454`), so unsourced exceeded pairs are reported, not pruned or failed (AGENTEE-337; `electrical_locality.py:216`). No per-block side/spread/internal-length report exists outside the block path. | R5/ROUTE-3: locality status `info`, with **22 of 26 measured pairs exceeded** (for example U7/C10 27.4 mm, U5/C3 18.4 mm, U5/C5 11.2 mm). Block spreads (footprint-origin bbox diagonal) are **29–106 mm** on a 90 × 65 mm board (diagonal 110 mm). This is not internal connection length, which was not measured. **5 blocks are split across sides:** sensor-power-front/rear/tire 4+4, tire-can 17+3, supplies-5v 10+1. | `placer.py:1944-1949, 2451-2454`; `electrical_locality.py:216`; placement-r5 `evidence/placement-judgment.json` `locality_grading`; `repro.json` `boards.r5` / `boards.route3` |

## 2. What was ignored, weakened or lost, and why production took its path

| Relationship | Fate | Class |
|---|---|---|
| Functional blocks (18-block allocation exists) | Not declared to the campaign placer (`pipeline.py:975-976`); the repack candidates are bound to the **iter8n seed** (`0365485e…`) and feed only scope limitations (`pipeline.py:17-24, 355-384`: "a real placement repacks this block against its own emitted board") | **Bypassed path** + **missing inputs** (no stage-A candidates packed from the emitted board; the flat schematic yields no sheet blocks) |
| Whole-block side choice | Specified by AGENTEE-340 ("four rotations, **both sides**"); implemented as captured side only (`block_arrangement.py:5, 324, 785`) | **Missing capability** (weakened from spec) |
| Per-part side choice | Not in `placer.transform` or plans | **Missing capability** |
| The seed's double-sided layout | The AGENTEE-355 microSD seed had **162 F / 147 B**; forward annotation stages everything on F, and the emitted board is 308 F / 1 B | **Lost** (emission discards side; nothing carries it) |
| Device-support pin relationships (decoupling, feedback, boot, input caps): electrical locality | 12 pad obligations, **soft**: they rank and report but never fail (22 of 26 exceeded at R5) | **Weakened by policy** (AGENTEE-337 advisory rule) + **missing inputs** (no sourced or owner bounds; most support parts uncovered) |
| Local clusters: placement groups | 7 unsourced anchor-radius groups, **enforced** in search and in the final grade; held at R5 (20 measured, 0 exceeded) | **Not lost**, but **coverage is incomplete** (7 small clusters only). This is an **existing policy/enforcement discrepancy**: unsourced group bounds are enforced, contrary to the AGENTEE-337 advisory policy. It is recorded as an input to AGENTEE-479; nothing is hardened or relaxed here |
| Explicit membership for every footprint | `derive` defaults to implicit `root-sheet` residual | **Missing capability** (no strict-coverage mode) |
| Router feedback | Not integrated (AGENTEE-391 open) | **Missing capability** |
| R5 shape | Retained 287 R2 poses and flipped only the 22 leftovers | **Coordinator restriction** (briefs R3–R5); **superseded** by AGENTEE-472 |

**Why the path:** a flat emitted schematic, a production declaration without `blocks`, and side immutability in every packing path. Together they forced a flat front-side pack of 300 movable parts. That pack fragmented the front (R1–R3), and the coordinator then restricted R5 to keeping R2's poses and flipping leftovers. The result is front-heavy and has no block locality, which is what the owner observed.

**Not every loss of cohesion comes from advisory-only enforcement.** The enforced groups held (20 measured, 0 exceeded); only the soft locality pairs drifted (22 of 26 exceeded). The dominant causes are the bypassed block path, the missing membership and missing obligations for most support parts, and side immutability.

## 3. Leads (Plane state and source) and the original two-pass behaviour

| Lead | What it is | State | Bearing |
|---|---|---|---|
| AGENTEE-339 | Stage A: blocks from hierarchy or allocation, packed alone into rigid `block-candidate/2` | completed | Works; captured side; needs an allocation for a flat schematic |
| AGENTEE-340 | Stage B: arrange macros, then residual pack | completed | **Spec said both sides; code is captured side** |
| AGENTEE-355 | Complete the real pod (compact stage A, member-aligned axes, incremental ranking) on the microSD source | completed | **Two-pass completed the pod** on the microSD seed (`docs/blocks.md` around 794-850) |
| AGENTEE-439 | Campaign blocks-request support, snapshot data, netlist semantic identity | **not completed** in Plane; code present (`placement_adapter.py:190-226, 267-273, 1541`; `test_placement_blocks_request.py`) | Capability present, production never used it |
| AGENTEE-341 | Electrical locality: disjoint supply/return nets, switch-leg binding | completed (docs only: `placer.md:1541, 1790`; `check-reference.md:2120-2124`) | Locality semantics only; no placement-side effect |
| AGENTEE-391 | M6 bounded placement↔routing feedback | **not completed**; not in source | Missing routing feedback |

**Original two-pass behaviour** (AGENTEE-339/340/355; `docs/blocks.md` around 794-850): stage A packed **20 blocks** of `blocks/allocation.json` (`1fb4ecde…`, 293 members, 16 residual). Members kept their seed sides: **2607 mm² F plus 1701 mm² B** outline boxes. Stage B arranged them as rigid macros, and the residual was packed with members fixed. The complete pod came out `placed` in about 41 s through `placer_runner`: judge pass, groups pass, hard `no_stacking`/`no_block_over_fixed` pass, locality `info`. **Its side diversity came from the hand-built seed** (`base-seed.kicad_pcb`: 162 F / 147 B), not from the placer. The production emission had no such seed.

**Current tests that bear on this:**
- `test_blocks` (54; side only as identity: `:1146, 1209, 1221`);
- `test_block_arrangement` (27; opposite-side shadows `:319`);
- `test_block_provenance` (7);
- `test_block_library` (49);
- `test_placement_blocks_request` (14);
- `test_placer_side_transform` (4);
- `test_electrical_locality` (55).

**No test selects or changes a block's side or exercises a congested underside.**

## 4. Reproduction, repair boundary, regression, decisions

**Minimal reproduction** (ran once, read-only): `repro-run.sh` runs `a473_repro.py` in image d96f8e00 with agent-ee 39924b46. The output is `repro.json`:
- derive without allocation: 0 blocks, 305 root-sheet;
- with allocation: 18 blocks, 272 members;
- per-board, final-coordinate block side and spread for emitted, R5 and ROUTE-3, as quoted above.

**ONE proposed reusable repair boundary:** a **side-aware block arrangement**, with side as a decision variable of stage B under bound eligibility. Dependency order:
1. **Membership input:** a strict-coverage mode in `blocks.derive`, where every footprint is a block member, declared residual with a role (shared/fixed/edge), or refused. Plus the emitted-board allocation (fome-mc `blocks/allocation.json`, with C18/R33 and the 31 residual roles resolved).
2. **Side eligibility record:** per block or part, eligible sides with **sourced** restrictions (antenna, RF F.Cu-over-In1 path, connector or mechanical access, thermal, assembly), bound by the coordinator like envelopes. The default is settled: either face, by owner requirement (REQUIREMENTS.md:65), as decided by agent-529 in 407cd406. Only part-specific restrictions remain open.
3. **Stage A, mirrored candidates:** each block packed once per eligible side. Member geometry comes from the **native flip** of the captured footprints (as `placer_runner._flipped_inventory` does), never a synthetic mirror.
4. **Stage B search over rotation × eligible side**, with the existing per-side keepouts, shadows and fixed reservations. The objective stays connectivity and congestion; **no side-balance term**.
5. **Plan → write:** placements carry `side`. The `agent-ee.side-changes/1` authorization is **derived from the bound eligibility record** (extend `_side_changes`' source), never self-authorized by the plan.
6. **Hard device-support:** obligations become hard only with a sourced or owner-ratified bound (decision D3); otherwise they are reported per block.
7. **Production:** fome-mc `pipeline.py` declares `blocks` (allocation, arrangement, candidates packed from the emitted board).
8. **Later:** AGENTEE-391 routing feedback.

**Congested-underside regression CONTRACT** (a specification for AGENTEE-479; not executed here). Before-fail/after-pass execution is an AGENTEE-479 acceptance gate; nothing here demands running an unbuilt feature.

1. **Deterministic fixture.** Synthetic geometry with no pod data. The outline, every courtyard, the fixed parts, keepouts and shadows are given as literal coordinates. The seed, part order and finite step budget/timeout are fixed and identical across every arm.
   - Two faces. The front cannot hold all the blocks plus the residual.
   - Block A is connector-adjacent and **ineligible** for B by a sourced access record. Block B is eligible.
   - The underside is partly blocked by a fixed B part and an opposite-side shadow.
2. **Known feasible underside witness.** The fixture ships a hand-constructed complete legal arrangement, with block B whole on B, verified by the independent judge and native courtyard DRC. Feasibility is therefore proven by construction, not inferred from a search result.
3. **A real residual/global/legalization conflict that forces an actual block move.** The current `block_arrangement.py:1259-1287` fixes every arranged member during residual packing. A naive fixture could therefore pass with blocks never moving.
   - The fixture places a residual part whose only legal positions (proved by the witness) lie inside block B's first-arranged footprint.
   - Completion **requires** block B to be moved, re-sided or reshaped during global placement or legalization.
   - The test asserts that block B's final pose **differs** from its first stage-B pose. It also asserts the move was made by the adjustment step, which the search trace must show.
4. **Obligations checked after the adjustment AND after native save/reload.** Recompute from the reloaded board bytes:
   - membership, with every member present and the block whole;
   - each member's side against the bound eligibility record;
   - spread and internal connection length;
   - every pin-level relationship bound;
   - whether each cross-face member is deliberate or lost cohesion.

   All must hold on the reloaded board, not only in the plan.
5. **Negative mutations, which final admission must REJECT:**
   - (i) move one block-B member out of its block, breaking cohesion or a pin bound;
   - (ii) flip a member or block to a face its eligibility forbids, an unauthorized side change.

   Each mutated saved board must be refused with a typed reason.
6. **Matched side-disabled comparison.** The same inputs, order, seed and budget, with side choice disabled. The expected outcome is `arrangement_*_exhausted` or a capacity proof.
   - The witness proves the instance is feasible, so exhaustion here shows only **search exhaustion under that configuration**, never physical infeasibility.
   - The report must keep the two apart.
7. **No side balance.** A variant with spare front capacity keeps block B on F when that lowers the inter-block wire cost.
8. **Write path.** The write path refuses any flip outside the bound eligibility record.

**Decisions.** agent-529 decided D1–D5 in 407cd406; the data was prepared in AGENTEE-478.
- **Settled, removed as questions:**
  - the generic double-sided permission (REQUIREMENTS.md:65);
  - deliberate cross-face adjacency (required by AGENTEE-472 and docs/functional-block-placement-request.md).
- **Still open (part-specific, sourced restrictions):**
  - U1 antenna and housing applicability (474 C12/C13);
  - the U3/J2 RF path and F-over-In1 corridor (C15);
  - J1/J3 connector and card access (C05–C11);
  - H1–H4 hardware (C04);
  - regulator thermal (C23);
  - test-point fixture geometry (C20).

**Residual unknowns:**
- The stage-A/B runtime on the emitted board with the 18-block allocation is unmeasured; nothing was run.
- Whether the 434a9984 allocation's stage-A candidates fit the current outline and keepouts.
- How AGENTEE-439's code differs from its Plane acceptance; not audited.

## 5. Acceptance / dependency map (all six AGENTEE-472 owner requirements)

**Whole-block F/B flips alone are INSUFFICIENT.** They are a first capability only. Acceptance also needs deliberate cross-face adjacency within one membership, and post-global member refinement and legalization that keep the block constraints.

| # | AGENTEE-472 owner requirement | Needs (data → code → check) | Depends on | Acceptance evidence |
|---|---|---|---|---|
| 1 | Every footprint has explicit block membership or a shared/fixed role; shared rails do not merge blocks | Allocation v2 (AGENTEE-478 D1) → strict-coverage derive or pre-planning validator, with Python/Rust parity → fome-mc production declares `blocks` | none | validator 0 unassigned / 0 duplicates on the emitted board; production request carries the allocation |
| 2 | Sourced fixed mechanical/interface anchors first; place blocks across the allowed area and sides; then refine members while keeping locality | D5 fixed/shared rules + 474 register → fixed refs/obstacles bound before packing → stage B, then **post-global member refinement** | 1 | final report lists every fixed pose and its authority; members refined after global placement still meet their bounds |
| 3 | Eligible whole-block side changes **and deliberate cross-face adjacency**; sourced restrictions; optimize connectivity/congestion, not side counts | D2 eligibility + D4 templates → stage-A per-side variants (native flip; the side-variant format needs agent-524 agreement) → stage B over rotation × eligible side → side-changes authorization derived from eligibility | 1, 2 | regression contract items 1–8; underside evaluated and selected where it helps; no balance term |
| 4 | Device-to-support relationships enforced with pin/interface measurement (bounding boxes insufficient) | D3 relationship bounds (pin-level, provenance, UNRESOLVED blocks acceptance) → hard locality in search and final grading, in both planners | 1 | per-relationship pin measurements in the final report; 0 violations or explicit UNRESOLVED |
| 5 | Global placement, legalization **and routing feedback** keep all block constraints; move, reshape or re-side blocks, or report infeasibility; relaxations are explicit | residual/legalization able to move blocks (today members are fixed: `block_arrangement.py:1259-1287`) → AGENTEE-391 routing feedback, or an explicit missing-requirement record | 1–4 | regression contract item 3 (forced move) and item 4 (after save/reload); routing-feedback status reported |
| 6 | Sourced mechanical keepouts (hardware, connector/access, antenna, enclosure/thermal, courtyards, heights) applied on the relevant faces before packing | 474 register → per-face obstacles/rule areas before packing; UNKNOWN entries carried with region and face | 2 | final mechanical validation per face; every unknown reported as UNKNOWN, never PASS |
