# placement R2: ONE placement with a raised computational allowance (delivery plan rev 2, corrected)

Assignment: agent-521 decision update (via agent-519), agent-ee main `b8760cfd` `docs/telemetry-pod-delivery-plan.md` "Next action (revision 2)". These are coordinator records, not owner text. The superseded search-order brief was stopped before any run; its uncommitted analysis script is held in scratch (`held-r2-order-analysis/`) and is not part of this result.

## Outcome: NOT COMPLETE (`packing_budget_exhausted`: "wall-time search budget exhausted")

| | R2 | R1 / 1c (preserved, `../placement-r1/`) |
|---|---|---|
| Terminal reason | **`search_timeout_s` 1400 reached** | `step_budget` 200000 reached |
| Steps used | **567014** of 1000000 (≈ 405 steps/s) | 200000 of 200000 (≈ 631 steps/s) |
| Backjumps | **595** | 260 |
| Peak placed | **287 / 309** (9 fixed + 278 of 300 movable) | 283 / 309 (9 + 274) |
| Part being placed at termination | **R37** | R19 |
| Unplaced at peak | **22**: R7, R70–R84, TP1–TP6 | 26: R66–R69 plus the same 22 |
| Placement elapsed | **1405.0 s** (05:26:26.47Z → 05:49:51.50Z) | 316.9 s |
| Front free-area utilization (diagnostic) | 0.857740 | 0.857740 |

**No board was saved.** The placer publishes no board on a typed failure. The 287-pose plan is `diagnostic-only-unvalidated-partial-placement` (`run/placement-result.json`). Nothing is ready for routing.

**Facts about the frontier (no hypothesis drawn):**
- R2's 22 unplaced parts are a strict subset of 1c's 26. With 2.8× the steps, R2 additionally placed R66–R69 and nothing new became unplaced.
- The frontier is the tail of the reference-sorted run R66…R84 plus TP1–TP6.
- No capacity-infeasibility proof was produced, and the step budget was not the binding bound.
- Per instruction: **no further increase, retry or second run.** agent-521 decides.

## The only change: policy r2

`../placement-r1/repair/placement-policy.r2.json`, sha256 `ed9af8d7a8dc3d502f135d4be65a49ce172dc600ecbffc06e840734ac7cd1f8c`. It is r1 (`b4503695…`, with C42/D3/L3/U3 unfixed) with exactly two keys changed; the exact diff is `../placement-r1/repair/policy-r1-to-r2.diff`:

```
- "step_budget": 200000
+ "search_timeout_s": 1400,
+ "step_budget": 1000000
```

`priority_refs` is unchanged (J1, U1, J2, U3), so the search order is identical. The bound request carries step_budget 1000000, search_timeout_s 1400, 9 fixed refs and the same priority_refs (`run/request.json`).

**Runtime support, verified in agent-ee 7d5b0d4d `src/agent_ee/placer.py`** (sha256 `9b026056…`, byte-identical to the 1c step snapshot):
- `_validate_policy` accepts `step_budget` 1..1000000 (`:188`) and `search_timeout_s` in (0, 86400] (`:193-196`), with no key whitelist;
- `_Search` sets `deadline = started + search_timeout_s` (`:1775-1777`) and raises `_SearchTimedOut` at the deadline (`:1815-1816`);
- `_pack` maps that to `packing_budget_exhausted` / "wall-time search budget exhausted" (`:2373-2374`), which is the observed reason.

## Runtime, command, run directory

- **Same as 1c:**
  - image `sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7`, `--network none`, no AppArmor or seccomp option;
  - agent-ee **7d5b0d4d** (`/opt/agent-ee/src`) tool snapshot;
  - the campaign's own `placement_adapter` declaration (helper `agent-ee.placer/1`, `timeout_s` 1500);
  - the same unchanged `../placement-r1/run_r1.sh`, `setup_r1.py` and `checks_r1.py`.
- **Host command:** `~/.local/bin/native-admit run --class suite --weight 4 --label placement-r2 -- env WORK_NAME=work-r2 AE_SRC=/opt/agent-ee/src POLICY_OVERRIDE=/r1/repair/placement-policy.r2.json bash telemetry-pod/expansion/placement-r1/run_r1.sh RUN FOME`, at fome-mc `bcb84018`.
- **Lease:** `446d824359fd` (suite/4, 12 cpus; queued 0 s; `run/native-admit-events.jsonl`).
- **Step:** `timeout 1500 /usr/bin/python3 -B -I /placement-tool/launch.py /candidate/project/telemetry-pod.kicad_pcb /candidate/project/telemetry-pod.kicad_sch --request /placement-request/request.json --root /work/placement`. Exit 1, `not_placed`; the outer 1500 s bound was not reached.
- **Run directory:** `/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/placement-r1/run/work-r2/`. Evidence copies are in `run/`.
- **Time:** setup 2.4 s and checks 0.6 s; the lease ran from 05:26:24Z to 05:49:52Z.

## Input and native checks (input board; there is no output board)

- **Inputs unchanged:** board `2f1c955704ab1fb38217c24cbaf5a45f4219a74a6a2309be710452c54db3b673` and project `10002b987995765415313fa89da32ba9011160853596f1a78ff8fba24ac9b175` (fome-mc `881f6fc5`), re-hashed after the run.
- **Native check of the input:** 309 footprints (305 electrical plus H1–H4), 235 nets, 4 Cu, 1.6 mm, 0 tracks/vias, 2 zones.
- **Native DRC of the input:** 21 violations (courtyards_overlap 4, lib_footprint_mismatch 3, text_height 7, text_thickness 7), 499 unconnected, 0 schematic parity (`run/drc-before.json`, `run/checks.json`).
- **Not applicable:** the ref/net, J1-pose and after-DRC checks need a placed board.
- **Unchanged constraints:** geometry, clearances, constraints, the fixed sourced set (H1–H4, J1, J2, J3, U1, U2), rules, outline, stackup, electrical locality, parts and code. The provenance gaps recorded in `../placement-r1/RESULT.md` still apply.
