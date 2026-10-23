# AGENTEE-473b: Rust planner trace against the AGENTEE-473 findings (read-only)

Source: agent-529 sequencing addendum (via agent-519); owner relay 863a378d, "bring in the rust planner". These are coordinator records, not owner text.

**Clock:** started 2026-10-23T08:47:40.69Z, ended about 08:51Z, within the 20-minute bound. Read-only: no code, run, board or test.

**Revisions read:**
- **Rust candidate:** agent-ee `6f48b9f2653ff2d3b5a10c1a9c2a5a0b3f9b061c`, branch wt/rust-planner-greenfield-agent524 ("Record matched greenfield Rust planner benchmark results"), via `git archive`.
- **Comparison:** `39924b46196dbd03f283fabece91766a007e94db`.
- `merge-base(6f48b9f2, 39924b46)` = `b6bb621c`.

File hashes are in `source-identities.txt`. **`blocks.py` and `block_arrangement.py` are byte-identical in 7d5b0d4d, 39924b46 and 6f48b9f2**, so every 473 line reference for them holds at both revisions.

## 3 first (the direct questions)

- **Does Rust implement two-level blocks?** It implements **stage B (block arrangement of supplied candidates) plus residual packing**, and **candidate admission**, not just the flat pack. It does **not** implement stage A, the packing of each block into a `block-candidate/2`.
  - `lib.rs:22-60` dispatches `blocks` to `arrangement::plan`, `targeted`/`targeted_plans` to `targeted`, and otherwise `packing::pack`.
  - `blocks.rs` has `derive` (`:179`), `isolate` (`:404`) and `admit` (`:1913`), with candidate validation (`:769`) and compaction/recovery validation (`:1302, :1362`). It has **no stage-A packer**.
  - README: "supplied block admission and arrangement".
  - Stage A stays Python: `blocks.pack_block`, `blocks.py:478`.
- **Any side concept?** **Only the captured side**, as in Python:
  - `side: String` is a captured field (`footprint.rs:61, 129`);
  - `transform_value(fp, position, rotation_degrees)` has **no side parameter** (`footprint.rs:702`);
  - a block macro takes `side: first.side.clone()` (`macro_fp`, `arrangement.rs:210` → `footprint.rs:413`);
  - stage B loops `for rotation in [0, 90, 180, 270]` (`arrangement.rs:743`);
  - `opposite()` builds shadow keepouts only (`arrangement.rs:165-200`);
  - plan poses are `{ref, uuid, position_nm, rotation_deg}` (`packing.rs:854`), and block poses `{block, position_nm, rotation_deg}` (`arrangement.rs:357`).
- **Is the Python block path still reachable after Rust ships?** **Yes.**
  - `placer_runner._plan` (6f48b9f2 `:816-821`) delegates to an *active* runtime and otherwise runs Python `_plan_local` (`:824-845`), whose `blocks` branch calls `block_arrangement.plan_from_request`.
  - At 6f48b9f2, Rust is **opt-in** (`placement_rust_runtime.experimental`, `:16-25`; README "Opt in through…"), with no Python fallback inside a Rust session.
  - Python remains the parity oracle (`scripts/placement_engine_parity.py`, block suite).
- **Integration fact:** **6f48b9f2 does not contain the R5 side-transform correction** (`e76659d5`/`0e78994e`).
  - Its `placer_runner.py` (`aa9cd1a8…`) still has the 3-argument `_apply_plan` (`:671`) and the plain `_evaluate_proposal` (`:717`).
  - At 39924b46 these are `_side_changes` `:678`, `_flipped_inventory` `:721`, `_apply_plan` `:733` and `_evaluate_proposal` `:781` (`b4be6263…`).
  - The Rust landing must rebase over it. The changes are in different functions of the same file.

## 1–2. Map of each 473 finding onto Rust, with classification bound to both revisions

Classes: **(a)** shared input; **(b)** adapter/admission/final validation; **(c)** planner implementation.

| 473 finding | Python (39924b46 = 7d5b0d4d for these files) | Rust (6f48b9f2) | Class |
|---|---|---|---|
| Flat emitted schematic gives 0 sheet blocks; implicit `root-sheet` residual | `blocks.py:117-200` (`:186-188`) | `blocks.rs:179` `derive`, `root-sheet` `:345`, `allocated-residual` `:312`, `board-only` `:209`: **ported** | **(a)** membership/allocation input; strict coverage would touch **both** derives (parity) |
| Allocation (`blocks/allocation.json`, 18 blocks) never supplied | fome-mc `pipeline.py:975-976`; adapter accepts `blocks` `placement_adapter.py:190-226` (39924b46 `e9bb41b6…`; 6f48b9f2 `90662c74…`, the same `validate_declaration`) | Consumes `request.blocks` the same way (`lib.rs:43-55`) | **(a)** production declaration |
| Stage A (per-block candidate packing) | `blocks.py:478` `pack_block` | **Absent**: candidates supplied, `blocks.rs:1913` `admit` | **(c)** stage A stays Python-only; it is the producer of a shared input |
| Stage B whole-block side: captured only (spec said both sides) | `block_arrangement.py:324, 785` | `arrangement.rs:210` + `footprint.rs:413`, `:743` | **(c)** both planners |
| Per-part side immutable | `placer.py:92-118` (6f48b9f2 `transform` `:92`) | `footprint.rs:702` `transform_value`; poses without side `packing.rs:854` | **(c)** both |
| Opposite-side shadows as keepouts only | `block_arrangement.py:276-305` | `arrangement.rs:165-200` | **(c)** (already a rule input; keep) |
| Side-change write/admission (R5) | `placer_runner.py:678-745, 781` (39924b46) | **Not in 6f48b9f2** (`:671, :717`); Rust emits no `side` | **(b)** must be carried over by rebase; the authorization source must become an eligibility record |
| Device-support / locality bounds unsourced → advisory | `electrical_locality.py:216`; AGENTEE-337 | `locality.rs:283, 308` (advisory default; downgrade test `:1005-1011`) | **(a)** sourcing input; enforcement semantics already identical |
| Groups (anchor radii) unsourced → advisory in grading but rejected in search | `placement_groups.py:151` | `groups.rs:271-275`; test `:401` | **(a)** sourcing; **(c)** parity already holds |
| Final-coordinate validation: block rules graded only for block plans; no per-block side/spread/internal-length report | `placer_runner.py:746-779` (`block_rules` `:767`, hard gate `:832`) | Plan grading in Rust (`arrangement.rs:1374` `grade_rules`, `grading.rs:73` `judge`); **saved-board validation stays Python** (6f48b9f2 `placer_runner.py:682` `_saved_judgment`, `:717`) | **(b)** a per-block final report belongs in Python saved-board validation, planner-independent |
| Routing feedback absent (AGENTEE-391 open) | `placement_adapter.py:1866-1868` | No feedback input in `rust-planning-input/1` (`lib.rs:22-35`: facts, request, policy, netlist only) | **(b)** adapter, later |
| Emission stages all parts on F (seed sides lost) | `forward_annotation.py:264-280` | n/a (before planning) | **(a)** input; side becomes a placement decision, not an emission one |

## 4. Where side-aware block arrangement changes in the Rust path, and what can proceed now

**Must change in the planner, in BOTH Rust and the Python reference (parity), and so should wait for, or land with, the Rust branch:**
- Rust `footprint.rs:702` (`transform_value` + side, with native-flip geometry supplied in the capture, **not** a synthetic mirror) and `:413` (macro side);
- Rust `arrangement.rs:210, 580` (rotated cache keyed by side), `:743` (search over rotation × eligible side) and `:357` (block pose + side);
- Rust `packing.rs:854` (pose + side);
- Rust `blocks.rs:769, 1913` (admit per-side candidates);
- Python `block_arrangement.py:324, 785`, `placer.py:92`, `blocks.py:478` (stage A per eligible side);
- the parity suite's block cases.

Doing this in Python first and then porting doubles the work, and breaks parity on the Rust branch meanwhile.

**Disjoint shared-boundary work that can proceed alongside the Rust landing** (no planner file touched):
1. **Membership input (a):** finalize the emitted-board allocation in fome-mc (`blocks/allocation.json`: C18, R33 and the residual roles) plus a stand-alone strict-coverage **validator** run before planning. That avoids editing both `derive`s now.
2. **Side-eligibility record (a/b):** schema plus coordinator binding in `placement_adapter.binding` (Python only), with sourced per-block restrictions. The planner still ignores it until step 4.
3. **Admission (b):** derive the `agent-ee.side-changes/1` authorization from the bound eligibility record in `placer_runner._side_changes` (39924b46 `:678`). This is the rebase point with 6f48b9f2's `placer_runner.py`; coordinate with agent-524.
4. **Final validation (b):** the per-block final-coordinate report (membership, side, spread, internal connection length, violations) in Python saved-board validation (`_saved_judgment`). It is independent of which planner produced the plan. 473's `a473_repro.py` is a prototype of the metrics.
5. **Production declaration (a):** fome-mc `pipeline.py` declares `blocks` (allocation, arrangement policy, stage-A candidates packed from the emitted board), so both planners receive real block input.
6. **Stage-A candidates (a, Python producer):** per-side candidate generation in `blocks.pack_block` is shared input for both planners. Its **schema change** (side variants) touches Rust admission (`blocks.rs:769`), though, so agree on the schema with agent-524 first.

## 5. Rust boundaries not traced in 20 minutes

- `rank.rs` objective terms and whether any cost depends on side.
- `targeted.rs` side handling.
- `search.rs:382` rotation loop internals.
- Rust `arrangement.rs:1374` `grade_rules` versus Python `block_arrangement.saved_rules` (`:1015`) equivalence.
- The `--events` protocol.
- `placement_scoring.py` / `data/placement_score.rs` (the scalar scorer) and its interaction with blocks.
- Parity-suite coverage of block cases (`scripts/placement_engine_parity.py --suite block`) and `tests/test_placement_rust_runtime.py` contents.
- Whether 6f48b9f2's benchmark included a pod `blocks` request.
- Why 6f48b9f2's `placement_adapter.py` equals the older 7d5b0d4d version (`90662c74…`).
- Whether the rebased branch changes any of the above.
