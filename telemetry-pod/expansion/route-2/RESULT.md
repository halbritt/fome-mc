# ROUTE-2: repair rejected; ROUTE-1 preserved

**No repair candidate was accepted.** One bounded experiment ran with the qualified runtime. Its own improvement gate rejected the trial and restored its exact ROUTE-1 input. The returned board is still **INCOMPLETE: 78 native unconnected items across 48 nets**. Final grading against original R5 is **FAIL: 61 new dangling findings**. The pass against ROUTE-1 is only preservation of the existing defective board.

The returned board SHA-256 is `19ed7954ab305b39f29d19f08fb619b4399cb6522869fba21b7712a52a310bdf`, exactly the ROUTE-1 candidate. Both source boards remain unchanged: ROUTE-1 at that SHA and R5 at `8f3bc234305516b91b6e519d3e0a3cd05b69b6dd16006a317c39b6d810ace5fd`. `diagnosis/board-identities.json` records the paths and final rehashes. The durable original boards are also on fome-mc main `0fc9b543`, in `telemetry-pod/expansion/route-1/candidate/` and `telemetry-pod/expansion/placement-r5/board/`.

## Diagnosis and experiment

See `diagnosis/DIAGNOSIS.md` for final ROUTE-1 `failed_single` **and** `open_single`, pad deficits, blockers, `boxed_in`, native finding UUIDs, and measured pad escapes. Two precise sampled escapes, U30.8 and U18.5, pass the existing local reachability diagnostic on copper-free R5 at the unchanged 0.2 mm track / 0.2 mm clearance / 0.6 mm via geometry, but report caged after ROUTE-1. That supports investigating generated-copper congestion. U2.12's ROUTE-1 field auto-coarsened and is advisory only. No whole-board feasibility or immutable placement blocker is established; no footprint correction is justified by these samples.

The single attempt selected the 48 open nets plus their recorded blocker-net union, 119 nets total (`diagnosis/scope.json`). `--protect locked` allowed the router to move its generated unlocked copper; R5 contains no tracks/vias and ROUTE-1 contains no locked copper. The existing `--rip-existing-nets` capability received the explicit blocker list. The grid changed from 0.1 to 0.05 mm. Explicit layer costs `1 -1 3 3` kept In1.Cu obstacle-only. The In1 track keepout and the RF reference keepout remained unchanged. No geometry/rule/severity relaxation, footprint movement, new routing capability, model invocation, review, extra agent, or second routing attempt occurred. No additional dangling-object cleanup was performed.

## Rejected trial versus returned board

The engine's `JSON_IMPROVEMENT_GATE` reports **34 previously complete nets lost**, 13 gained, and worsened deficits on /+3V3 (2 to 35) and /POD_WHEEL_FRONT_SUPPLY (1 to 2). Its verdict is `reject`.

`kicad-route/router-summary.json` explicitly says `shipped: "input board"`: **every tally in that summary describes the rejected trial, not the returned board**. The runtime did not retain a separate rejected-trial PCB. Its pre-revert counts are engine reports, and the discarded trial has no native DRC qualification. The returned incumbent is saved in `candidate/`; exact geometry comparison shows **zero added/removed tracks or vias and zero changed nets** (`diagnosis/copper-changes.json`). No distinct improved board is delivered.

## Native grading

The wrapper ran full KiCad DRC with all severities, schematic parity, refill and preservation against both baselines. The final command was `kicad-route --json validate <route-2-run> --against <original-route-1-run>`; the original run's input is R5. Exact argv is in `logs/validation-command.json`.

| Measure | Original R5 | ROUTE-1 | Returned ROUTE-2 |
|---|---:|---:|---:|
| Native DRC unconnected items | 499 | 78 | 78 |
| Native DRC violations | 80 | 141 | 141 |
| Schematic parity findings | 0 | 0 | 0 |
| Native terminal graph complete nets (of 235) | 53 | 187 | 187 |
| Native terminal graph incomplete nets | 182 | 48 | 48 |
| Native terminal graph component deficit | 701 | 78 | 78 |

The R5 raw DRC count (499) and terminal-graph deficit (701) are different baseline observations and have not been reconciled here. They are reported separately, not substituted for each other. The returned board and ROUTE-1 agree exactly in bytes, copper geometry, and complete native terminal partitions. Neither baseline loses any prior terminal equivalence, including partially connected net groups; both comparisons have zero split components.

- **Against ROUTE-1:** routing INCOMPLETE, validation PASS, exit 2. It inherits all 61 dangling findings.
- **Against R5:** routing INCOMPLETE, validation FAIL, exit 3: **34 via_dangling + 27 track_dangling** new, zero new parity, 80 pre-existing violations, zero resolved violations.
- Refill changed no board bytes. All 16 preservation checks PASS against both inputs: project files, outline, layers, stackup, setup, netclasses/nets, pad connectivity, footprints, zones, keepouts, copper graphics, protected copper, new-copper geometry, scope, terminal connectivity and pour integrity.
- Full reports, all native finding UUIDs and positions, native terminal partitions, refill and preservation receipts are under `kicad-route/against-route-1/` and `kicad-route/against-r5/`.

## Runtime and limits

- kicad-route **b5774496d8466b67ffa0362b6665fee2108155a3**, clean runtime tree; builtin generation **84b30dc286f44df6b465ae8d40aa1363**, owned source **89a2efbf5305**, router/grid-router **0.23.1**. Full executed identity is in `kicad-route/result.json`.
- Native KiCad/pcbnew **10.0.7**, Python **3.12.3**. No switch to the old private development branch.
- One proximal `native-admit` suite, weight **4**, routing lease **3f6131eae193**. Diagnostics, validation and renders were sequential admitted work. There was no capacity refusal. Lease, PID/child, configuration, selected admission environment and cgroup receipts are in `logs/`. This was an admitted host command; advertised CPU/PID allowances are not presented as separate cgroup-enforced limits.
- Backend command duration **1161.726 s**, wrapper backend envelope **1161.984 s**, below the assigned **1200 s** maximum. The selected `--budget 1000` requested a soft stop at **1000.219 s**; the runtime completed during its built-in grace, **161.507 s** later. A 1190-second hard-stop watcher was armed to protect the owner's maximum but did not fire. The wrapper's total routing/validation runtime was **1183.089 s**.
- `measurement: false`: the budget stop disqualifies this as a reproducible measurement, even though the executed build has repeat evidence. The original run exit is 2 and process status PASS; neither means the repair succeeded.
- The task started **07:06:55 UTC** with a **07:46:55 UTC** wall deadline. The completion timestamp and elapsed task wall time are in `logs/task-finish.json`.
- Exact command, start/finish times, stdout/stderr and complete router log are under `logs/`. `recipe/` records the scripts used; they are evidence, not changes to routing software. Large intermediates remain at `/home/halbritt/.cache/route-2-agent507/run`.

## Artifact status

The front/back PNGs in `render/` were produced natively from the exact returned board and visually inspected. Their added header says **ROUTE-2 INCOMPLETE / NOT ACCEPTED**, with the candidate hash. They show the preserved ROUTE-1 board, not the discarded trial.

This commit contains evidence only, for agent-449 to integrate. It does not merge or push the branch and does not adopt a board or claim release qualification. The experiment is closed without another attempt. The local escape measurements do not support calling placement immutable; the available whole-net rip/retry experiment did not yield a connectivity-preserving repair.

Protocol provenance: Pincite release d3e0c0d4 passed its retrieval-state gate. Final packet `pkt-1cc08e4e7029b78b` (content SHA-256 `1cc08e4e7029b78bfaf5c4e982aa6a225caffe69af0635e5d1d5c0a7488a40f5`) records authority and observed evidence. `provenance/doctrine-disposition.json` classifies its unmet obligations and withholds repair/feasibility conclusions. Native KiCad and exact saved-board comparisons determine the reported outcome.
