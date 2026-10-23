# placement-r3: targeted constructive placement of the 22 missing parts — (B) BLOCKED

Assignment: agent-521 brief 99e8ab55 (via agent-519); plan agent-ee main `e97af81b`, revision 3, "Next action (revision 3)". These are coordinator records, not owner text.

**Clock:** started 2026-10-23T05:56:03.85Z; geometry work ended 06:18:23Z; result written by 06:20Z, inside the 30-minute bound. There was one task with no review, repeat or retry. The release-set v1 → v2 step below is the neighbour selection inside this one task, not a repeat.

**No board is saved and nothing goes to routing.** The PNGs in `inspect-287/` are diagnostic free-space maps of the INCOMPLETE R2 arrangement and are marked INCOMPLETE in their filenames. R1 and R2 evidence is untouched.

## What ran (existing code only; no new placer, scorer or search)

**Runtime:**
- every container ran under native-admit on proximal (leases in `native-admit-events.jsonl`, label `placement-r3`);
- image `sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7`, `--network none`, no AppArmor or seccomp option;
- agent-ee **7d5b0d4d**, the R2 step's own tool snapshot;
- input: the R2 materialized candidate tree (board `2f1c9557…`, project `10002b98…`, unchanged) and R2's bound native netlist, on an isolated copy.

**Command:**
`~/.local/bin/native-admit run --class suite --weight 4 --label placement-r3 -- [env RELEASE=/r3/release.json] bash telemetry-pod/expansion/placement-r3/r3_run.sh <R2 work> <new work> <fome-mc>`
It runs `r3_local.py`, which:
1. applies the 287 R2 diagnostic poses to a copy with `placer_runner._apply_plan`;
2. runs the **existing** `placer_runner.place_candidate` (`ranked-first-fit-backjump/1`, step_budget **200000**, the r1 value) with every part except the 22 (and any explicitly released neighbours) held fixed;
3. would then have re-validated the complete arrangement on the original board under policy r1 with `_evaluate_proposal`, which was **not reached**.

**Stage 1: R2 arrangement held, only the 22 searched** (`run-held287/`, lease `a5de24a0c453`)
- Result: `packing_search_exhausted`, "no candidate for R7 in the finite search; infeasibility unproved".
- 2954 steps, **0 backjumps**: every candidate pose for R7 was refused, and no movable blocker existed.

**Inspection** (`inspect-287/free-space.json`, `r3_inspect.py`; 0.1 mm grid, courtyards inflated by gap 0.25 mm, 0.5 mm edge band, declared obstacles):
- **All 22 are front-only** (F courtyard only): 13 resistors with courtyards of 2.96 × 1.46 mm, 3 (R73, R77, R81) at 3.36 × 1.9 mm, and 6 test points TP1–TP6 at 2.0 × 2.0 mm. Their space need including the gap is **≈ 153.6 mm²**.
- **Front free space: 391.5 mm², split into 69 fragments.** The largest:

  | Area | Region (mm) | Bordering parts |
  |---|---|---|
  | 46.1 mm² | x 38.1–56.8, y 44.4–48.7 | 11 |
  | 30.5 mm² | x 21.5–39.0, y 30.1–44.5 | 40 |
  | 28.7 mm² | x 70.8–82.2, y 26.9–33.1 | 14 |
  | 27.4 mm² | x 0.5–10.4, y 25.4–42.4 | 32 |
  | 23.2 mm² | x 51.6–62.5, y 21.4–25.1 | 7 |

- My grid draws neither native keepouts nor copper reservations. The placer, which applies them, found no legal R7 pose in any fragment.
- **Back side: 4976 mm² free in one region**, which the front-only parts cannot use.

**Stage 2: explicit neighbour repositioning** (`release.json`)
- Release v1 (28 parts bordering the three largest regions with the fewest neighbours: 46.1, 28.7 and 23.2 mm²) was **refused before the search**: "fixed placement C79 in group u20-local-bypass needs a fixed anchor". The group anchors U20, U21 and U3 were in the set. Evidence: `run-release-v1-refused/`.
- Release v2 kept those anchors held, releasing 25 movable neighbours. Each was selected for the same one-line reason: *it borders one of the three largest front free regions, and is released so the existing placer can consolidate that fragmented space*:
  - region 1 (x 38.1–56.8, y 44.4–48.7): C118, C124, C126, C17, D103, D105, JP2, JP3, U30, U6;
  - region 2 (x 70.8–82.2, y 26.9–33.1): C115, C116, C80, C81, JP1, R56, R61, U18, U27, U28, U29, Y1;
  - region 3 (x 51.6–62.5, y 21.4–25.1): C77, C83, U12.
- Result (`run-release-v2/`, lease `0fbc34359d2c`, 06:00:13 → 06:18:23Z): **`packing_search_exhausted`**, "every backjump for C80 revisits a part order; infeasibility unproved". 166009 steps, 219 backjumps. **Peak 26 of the 47 movable parts**; the heartbeat peak was 286/309, below R2's 287. Front free-area utilization for the 47 movable parts: 0.4908.

## The geometric obstruction

- **What blocks it:** with the R2 arrangement, the front side's remaining free area (391.5 mm²) is ≈ 2.5× the 22 parts' need (153.6 mm²). But it is split into 69 fragments, and the existing placer finds **no legal pose** for any of the 22 under the unchanged constraints. Re-packing 25 bordering neighbours locally does not recover a complete arrangement: the search exhausted all orders.
- **No infeasibility proof was produced in any stage.**
- **The constraints that bind the front side, with provenance:**
  - **Sourced (envelope `constraint_provenance`):** J2 pose (D-PCB-4), J3 pose (D-PCB-13 v3), the D-PCB-6 RF keepout (In1/In2 x 76–88, y 26.5–30.6 mm), the D-PCB-7 v2 In1 no-tracks area, the stackup and fab profile.
  - **In the envelope, provenance NOT established:** the outline 90 × 65 mm, the J1/U1/U2 poses, H1–H4 (4 mm insets, ⌀3.2 mm), and the **radio-antenna keepout** (no footprints on any layer near U1's antenna).
  - **Agent-selected (derived policy r1, unchanged):** gap 0.25 mm, edge margin 0.5 mm, the 7 locality groups (3.5–15 mm), the 7 advisory obstacles, and the advisory electrical-locality bounds.
- **What the 22 are:** passives and test points with no group or locality obligation. The parts that compete for the same front space include the locality-bound clusters (U5/U7 input and boot capacitors and others) and the group members.

## ONE concrete best alternative (agent-521 decides; not done)

Place the 22 front-only parts (R7, R70–R84, TP1–TP6) on **B.Cu**: flip them with pcbnew, using an explicit pose script and the existing judge. The back side has **4976 mm² free in one region**; the 22 need ≈ 154 mm².
- This changes their layer, which this brief forbids, so it needs an explicit decision. It also has assembly consequences (double-sided assembly; test-point access).
- No sourced constraint found here requires these parts on the front.
- Second option (not preferred): reduce the agent-selected gap or edge margin. Neither is sourced, but both are numeric constraints this plan keeps unchanged.

## Not run

The complete-arrangement validation (309 refs, ref/net, J1 pose, 4 Cu/1.6 mm, native DRC/parity/unconnected, locality) did not run, because no complete arrangement exists. The input's native baseline stays 21 DRC / 499 unconnected (R2 `run/drc-before.json`).
