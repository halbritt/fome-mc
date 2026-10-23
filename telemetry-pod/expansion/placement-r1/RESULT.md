# placement-r1: ONE bounded placement attempt on the complete emitted pod board

Assignment: agent-521 brief b8a43a9c v1, relayed by agent-519, under delivery plan revision 1 (agent-ee main `1b0637c7`, `docs/telemetry-pod-delivery-plan.md`, "Next artifact and causal action"). These are coordinator records, not owner text.

## Outcome: NOT PLACED (`packing_budget_exhausted`). Partial stays partial.

**The search really ran.** The existing placer ran on the complete 305 + 4 board for **316.9 s**:
- strategy `ranked-first-fit-backjump/1`, 260 backjumps;
- it **exhausted the policy's deterministic `step_budget` of 200000 candidates**;
- the peak was **283 of 309** footprints placed: the 9 sourced-fixed parts plus 274 of the 300 movable;
- the first part left unplaced was **R19**.

**No board was saved.** The placer publishes no board on a typed failure (`placer_runner.place_candidate`). Its partial plan exists only as a diagnostic, labelled `diagnostic-only-unvalidated-partial-placement` (283 poses, in `runs/attempt-1c/placement-result.json`). **No placed board or project exists to hand to routing.**

**Why it stopped.** The stop came from the step budget, not the 1500 s time bound: about 1183 s of that bound were unused. `step_budget` 200000 is an **agent-selected packing heuristic** in the derived policy, not an owner or manufacturer limit. Raising it is a different bound, so per the brief I **stopped and report it here, rather than starting an extended run.**

## Inputs (verified before anything else)

| | |
|---|---|
| fome-mc | main `881f6fc5b10e81e3a9b99fd542df991742ed68f0` (`git show` copies in `input/`) |
| Board | `input/telemetry-pod.kicad_pcb`, sha256 **`2f1c955704ab1fb38217c24cbaf5a45f4219a74a6a2309be710452c54db3b673`** (unchanged) |
| Project | `input/telemetry-pod.kicad_pro`, sha256 **`10002b987995765415313fa89da32ba9011160853596f1a78ff8fba24ac9b175`** (unchanged) |
| Candidate tree | The retained emission design tree (`production-capture/evidence/emission-7d5b0d4d/MANIFEST.json` `design`, 559 files, every sha256 verified) was materialized as the placement inputs. Its board and project are the bytes above. The schematic is `f5840ecc…`. |
| Identity note | `identity({scope, files})` of that tree with the prepared `scope.json` is `683e4af1…` for attempt 1/1b and `32682efb…` with the repaired policy. Neither equals the emission's recorded `candidate_id` `5504a022…`, so the emission's scope object evidently differs from the prepared `scope.json`. The board bytes are verified directly, so this does not affect the attempt. It is recorded, not resolved. |

## Runtime, command and run directory

- **Image:** the qualified runtime `sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7` (tini entrypoint), `--network none`.
- **Security options:** none given (no AppArmor or seccomp option; nothing AppArmor-related inspected, loaded or tested).
- **Visuals:** `AGENT_EE_SKIP_VISUALS=1`, so no bwrap.
- **Admission:** every container ran in a native-admit lease on proximal (label `placement-r1`; `runs/native-admit-events.jsonl`). Queued 0 s each time.
- **Run directory:** `/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/placement-r1/run/` (`work-1c/` is the placement run). Evidence copies are in `runs/attempt-1`, `runs/attempt-1b` and `runs/attempt-1c`.
- **Host command (attempt 1c):**
  `~/.local/bin/native-admit run --class suite --weight 4 --label placement-r1 -- env WORK_NAME=work-1c AE_SRC=/opt/agent-ee/src POLICY_OVERRIDE=/r1/repair/placement-policy.r1.json bash telemetry-pod/expansion/placement-r1/run_r1.sh RUN FOME`
  at fome-mc `fd9cba6a`, lease `f0ed850b85d8` (suite/4, 12 cpus).
- **The placement step**, exactly as agent-ee `placement_adapter.prepare_step` declared it (the campaign's own `placement_adapter` declaration: helper `agent-ee.placer/1`, policy `composition/placement-policy.json`, `timeout_s` 1500):
  `timeout 1500 /usr/bin/python3 -B -I /placement-tool/launch.py /candidate/project/telemetry-pod.kicad_pcb /candidate/project/telemetry-pod.kicad_sch --request /placement-request/request.json --root /work/placement`
  This is `placement_adapter.sandbox_main`, which does a fresh native netlist export and then the existing `placer_runner`. It ran directly in the container, not inside bwrap.
- **agent-ee:** the step's tool snapshot is the image's own **7d5b0d4d** (`/opt/agent-ee/src`), via `tool_snapshot`. See attempt 1 for why it is not `1b0637c7`.
- **Elapsed:** placement **316.9 s** (05:14:31.82Z → 05:19:48.69Z). Setup, diagnostics and checks over all leases took about 290 s admitted. One search ran.

## Attempts in this one execution (each failed attempt is evidence)

| # | What ran | Result | Defect → smallest repair |
|---|---|---|---|
| 1 | Production path with agent-ee **1b0637c7** (lease `d1c03e7fd189`) | Refused in 1.3 s, before packing: `constraint provenance geometry inventory differs from saved project/rules` (`design_rule_provenance._verify_geometry`) | **Input-compatibility defect.** The project's `agent_ee_constraint_provenance` witness was emitted by producer 7d5b0d4d. AGENTEE-348 (`4bc90803`, `c9101642`, `daf3fce2`) later changed `geometry_defaults`. Diagnostic lease `fcbb6b9aae4c`: 7d5b0d4d accepts the record, 1b0637c7 refuses it (`runs/diag-provenance.log`). **Repair:** use the qualified runtime's 7d5b0d4d ("or the qualified runtime where compatible"). Input bytes unchanged. |
| 1b | The same with **7d5b0d4d** (lease `a140c83f893e`) | `fixed_conflict` in 2.8 s, 0 steps: `fixed placement C42 conflicts with outline, obstacle, keepout or reserved gap` | **Input defect in the derived request policy.** The diagnostic (lease `cc8c10875031`, `runs/attempt-1b/diag-fixed.json`) checked all 13 fixed refs. The **9 sourced envelope refs (H1–H4, J1, J2, J3, U1, U2) all fit**. The 4 policy-only refs **C42, D3, L3, U3 are outside the board outline** at their emitted positions, and nothing sources fixing them. **Repair:** `repair/placement-policy.r1.json` (`b4503695…`) = the original (`5fab430a…`) with ONLY those four removed from `fixed_refs`; the packer places them. Nothing else changed (diff in `repair/`). |
| 1c | **The placement run** | `packing_budget_exhausted` after 316.9 s; peak 283/309; first unplaced R19 | The stopping bound is the agent-selected `step_budget` 200000. See "Smallest next correction". |

## Preservation checks (native pcbnew on the input; there is no output board)

- **309 footprints**: 305 electrical plus 4 mounting holes (H1–H4, no nets); **235 nets**.
- **4 copper layers, 1.6 mm** (1600000 nm); 0 tracks, 0 vias, 2 zones (`runs/attempt-1c/checks.json`).
- **Nothing was written to any design:** the run's input board and project, hashed after the run, still equal the hashes above; no output board exists.
- **Not run:** ref/net mapping and J1 pose comparisons need a placed board. The checks code is in `checks_r1.py`.
- **J1:** the right-angle AMPSEAL `1-776163-1` is held fixed by the sourced envelope (bottom edge, position 45 mm, inset 9.5 mm, front, rotation 0).
- **Stackup:** the accepted four-layer/1.6 mm stackup (envelope `stackup`, JLC `jlc04161h-7628`) was not touched.

## Native diagnostic delta (kicad-cli `pcb drc --severity-all --schematic-parity`)

| | Before (input board) | After |
|---|---|---|
| DRC violations | **21**: courtyards_overlap 4, lib_footprint_mismatch 3, text_height 7, text_thickness 7 | **none: no board was placed** |
| Unconnected | **499** | n/a |
| Schematic parity | 0 | n/a |

The before report is `runs/attempt-1c/drc-before.json` (`fa1beef2…`). It reproduces the historical 21 / 499.

## Constraints and provenance

**Sourced** (captured envelope `composition/envelope.json`, with `constraint_provenance`):
- J2 fixed pose (D-PCB-4);
- J3 fixed pose (D-PCB-13 v3);
- the In1.Cu no-tracks rule area (D-PCB-7 v2);
- the In1/In2 RF reference keepout x 76–88 / y 26.5–30.6 mm (D-PCB-6);
- the stackup (JLC source quote) and fab profile `jlc04161h-7628`.

**Provenance NOT established here:** these are in the envelope, but it carries no `constraint_provenance` row for them, and I found no citation:
- **J1** pose (bottom, position 45 mm, inset 9.5 mm, courtyard overhang ≤ 22.85 mm);
- **U1** pose (top, 72.5 mm, inset 6.5 mm);
- **U2** pose (top, 12 mm, inset 10 mm);
- **H1–H4** at 4 mm insets, ⌀3.2 mm NPTH;
- the **90 × 65 mm outline**;
- the **radio-antenna keepout** (forbid footprints/tracks/vias/pads/pours on all layers around U1's antenna). The README says this keepout "stays unknown by design".

They were applied, not weakened.

**Agent-selected (derived request policy `placement-policy.json`, README: "the derived request policy"; not owner or manufacturer requirements)**, applied as given:
- `gap_nm` 250000 and `min_courtyard_edge_mm` 0.5;
- `step_budget` 200000;
- `priority_refs`;
- the 7 locality `groups` (max distances 3.5–15 mm);
- the 7 declared `obstacles` (plus reservations the placer adds at run time), which the placer marks "unsourced obstacle … is advisory";
- the `electrical_locality` bounds, which their own citations mark "agent-derived bound … class ADVISORY: not owner-chosen";
- the four extra fixed refs C42, D3, L3 and U3, removed (repair above).

## Smallest next correction (agent-521 decides; nothing was run)

The search used its whole 200000-candidate budget in 317 s, with about 1183 s of the 1500 s step bound left. It reached 274/300 movable parts.

The smallest change is to the **agent-selected `step_budget`**: for example, set it so that the 1500 s step timeout becomes the binding bound. That is roughly 4.7× at the observed rate of about 630 steps/s; the placer also supports `search_timeout_s`. The packing constraints stay unchanged.

It is a different bound, so it needs agent-521's decision. It is **not** a sourced constraint, and nothing sourced would be weakened. Front-side free-area utilization is 0.858 (diagnostic only); there is no capacity-infeasibility proof.

Also open for the plan:
- the 7d5b0d4d/1b0637c7 provenance incompatibility. Future placement on main `1b0637c7` needs a re-emitted project provenance record, or the qualified 7d5b0d4d runtime.
- the four off-board policy-fixed parts. Their intended positions are not established by any source.
