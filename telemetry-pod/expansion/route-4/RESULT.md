# ROUTE-4: one retained junction; batch stopped

The best candidate has **75 native unconnected items** and **58 dangling findings against original R5**. It improves the accepted ROUTE-3 working board by two connections and two resolved dangling-track findings. The batch stopped after the next two targets failed. No further target or batch is running.

**Candidate SHA-256:** `5690da57e291dff46f80b239c1c81f164d0622c6d4c0d03b65437e653f025825`.

The whole board remains **INCOMPLETE / NOT RELEASED**. It still has 47 incomplete nets. This finite batch does not redefine the complete telemetry-pod goal. Agent-449 is the sole integrator; this branch contains evidence and the working candidate, without merging, pushing or replacing a production board.

## Compact target ledger

Each target started from the last validated incumbent. Failed trials were discarded. The first retained GND edit is the only change delivered.

| Target | Attempts and changed objects/settings | Native result | Disposition |
|---|---|---|---|
| GND junction at (49.4,14.1) | 1 direct native attempt. Add one 0.6/0.3 mm F.Cu–B.Cu through-via; no existing object or blocker net edited. | Opens **77→75**, DRC **140→138**, parity0; zero new finding or split terminal component; all preservation PASS. | **Retained.** |
| `/SUP_U18_CT` / U18.5 | 1 local precheck. Three short generated GND F.Cu segments transferred to B.Cu, with two standard vias and one endpoint adjustment. Target + one blocker net. No backend search followed the failed precheck. | 4 new findings: 2 tracks_crossing, 1 items_not_allowed, 1 track_dangling; one partial GND component split; opens75→76. | **Rejected; reverted to75.** First consecutive target failure. |
| `/SENSOR_POWER_REAR_UVLO` / U24.2 | 2 attempts. First: target-only protected router, 0.025 mm grid, zero rip-up, 90 s soft budget. Second: direct perpendicular F.Cu escape, one standard via, two short B.Cu segments to existing target copper; no blocker net edited. | Protected route remains open at75. Direct trial gives74 raw opens but **17 new findings: 9 clearance + 8 shorting_items**. | **Both rejected; reverted to75.** Second consecutive target failure; batch stopped. |

These are three targets, within the maximum of five. No target used more than two attempts. A provisional GND split in the U18 trial was resolved by discarding that trial and revalidating the unchanged incumbent; no unresolved regression remains in the delivered board. Candidate copies and larger native intermediates for failed attempts remain at the exact paths in `targets/scratch-locations.json`. Compact changes, native findings, preservation records and the one router log are committed under `targets/`; full duplicate report trees are not committed for every trial.

## Retained GND junction: exact terminal evidence

Native `GetConnectedItems(track, flags=0)` at (49.4,14.1) found **three distinct, disjoint GND terminal groups**: 1 terminal on F.Cu, 10 on B.Cu, and 48 on In2.Cu. A through-via joins these 59 terminals into one component. The complete native GND partition changes from **30 to 28 components**. Every prior terminal equivalence survives, including partial groups on incomplete nets.

Only one via is added at (49.4,14.1), diameter **0.6 mm**, drill **0.3 mm**, F.Cu through B.Cu. There is no track addition, deletion, movement or layer change in the retained candidate. All prior via records survive unchanged. No pad centre lies within 1.2 mm of the new via centre. Native netclass-geometry, keepout, hole/copper-clearance, scope and connectivity checks pass. `checks/copper-changes.json` contains its native UUID and full record; `checks/native-terminal-comparison.json` contains all joined pad UUIDs and the complete partition comparison.

The two resolved findings are the existing GND dangling tracks at the junction:

- `b0648978-c785-4051-b66f-017fd3463622`, F.Cu, 0.8000 mm;
- `638d5b32-d036-42e6-aa35-a98f061f134c`, B.Cu, 2.9698 mm.

## Native acceptance and original R5 baseline

The existing native grade API ran DRC with all severities, schematic parity, refill, native terminal extraction, preservation and pour checks against the exact ROUTE-3 incumbent. The native-only reference context is source-bound by the incumbent board/project hashes, native facts and the existing qualified baseline-cache producer. It makes no routing-run ancestry claim. The exact context and method are recorded in `checks/against-route3-result.json` and `targets/target1-attempt1/native-reference-context.json`.

The final saved board was then independently graded against original R5 through the original ROUTE-1 reference context and its whole-board scope. No inherited finding is laundered into a new baseline.

| Whole-board measure | Accepted ROUTE-3 | Retained ROUTE-4 |
|---|---:|---:|
| Native unconnected items / component deficit | 77 | **75** |
| Incomplete nets (of 235) | 47 | **47** |
| Complete nets | 188 | **188** |
| GND native terminal components | 30 | **28** |
| Native DRC findings | 140 | **138** |
| Schematic parity findings | 0 | **0** |
| Split prior terminal components | — | **0** |
| New native DRC findings vs ROUTE-3 | — | **0** |
| Dangling findings above original R5 | 60 | **58** |

All preservation checks PASS against both references: project/rules files, outline, layers, stackup, setup, netclasses/nets, pad connectivity, footprints, zones, keepouts, copper graphics, protected copper, conductor geometry, routing scope, net completion and pour integrity. Refill changes no candidate board bytes. Rules, clearances, widths, via geometry, severities and fixed geometry were not relaxed.

**R5 grading remains FAIL:** 80 inherited findings plus **58 outstanding dangling findings (33 via_dangling, 25 track_dangling)**, 138 total, parity0. ROUTE-1 originally introduced 61; ROUTE-3 resolved one and this batch resolves two more. Those remaining 58 must clear before release. Exact UUIDs, positions and full reports are in `checks/against-r5/`.

The ROUTE-3 incumbent SHA `0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651` and original R5 SHA `8f3bc234305516b91b6e519d3e0a3cd05b69b6dd16006a317c39b6d810ace5fd` remain unchanged. Their final rehashes are in `checks/board-identities.json`.

## Exact residual obstruction

**U18.5 / SUP_U18_CT:** the F.Cu escape is constrained beside generated GND copper and a fixed signal-pad region. The tested local layer transfer cannot be retained: the proposed GND via at **(82.7,26.6)** violates the preserved **D-PCB-6-RF-reference** keepout. The B.Cu transfer also crosses `/SENSOR_POWER_AUX_RTN` objects `50a81cf7-bd50-43fb-a074-86d50417f949` and `c97b2ea5-e534-4990-852e-757a7b1db626`. No keepout or footprint change is justified by that rejected trial; it does not establish immutable placement infeasibility. The exact native counterexample is in `targets/target2-attempt1/new-findings.json`.

**U24.2 / SENSOR_POWER_REAR_UVLO:** native pad centre **(31.205763,29.6836)** remains disconnected from nearby B.Cu target copper at **(32.1,29.7)**. The protected router exhausted this attempt's search. The direct trial's via at **(31.205763,28.7)** and its escape conflict with `/SENSOR_POWER_REAR_OVP`, `/WHEEL_FRONT_OUT`, `/SUP_U19_SENSE` and `/PRE_6V3`, including C18.1. Its proposed connection is invalid despite a lower raw-open count. All 17 native findings, UUIDs and positions are in `targets/target3-attempt2/new-findings.json`. No legal bounded correction was established within this target's two attempts; no broad rip or additional trial is authorized in this batch.

## Execution and handoff

- Task started **2026-10-23 08:05:42 UTC**, with a **08:50:42 UTC** deadline. `logs/task-finish.json` records sealing within 45 minutes.
- The qualified router was invoked once: **33.518 s actual backend command time**, **35.009 s** including wrapper backend preparation/restoration, below the **1200 s** total backend cap. Direct native edits used no routing backend. The command used a 90-second soft budget and did not stop on budget.
- Protected routing used `--protect existing`, `--max-ripup 0`, grid 0.025, explicit In1.Cu track prohibition, and disabled rescue, plane finalization, global planning and automatic reconciliation rip escalation. There was no global rip or budget increase.
- Runtime remains clean **b5774496d8466b67ffa0362b6665fee2108155a3**, installed builtin generation **84b30dc286f44df6b465ae8d40aa1363**, router/grid-router 0.23.1, KiCad/pcbnew 10.0.7, Python 3.12.3. No production routing software was added or changed; `recipe/` only records calls to existing native/edit/grade APIs.
- All native work used sequential proximal `native-admit` suite/weight4 leases. No capacity refusal, parallel native run, new agent, model call/review or cloud job occurred.
- Best candidate and full final checks are committed once under `telemetry-pod/expansion/route-4/`, with `SHA256SUMS`. Large scratch evidence remains at `/home/halbritt/.cache/route-4-agent507/`.
- Gallery/integration label for agent-449's existing job: **75 open / 58 dangling / INCOMPLETE / NOT RELEASED**. The four-hour gallery cadence and integration remain with 449; agent-507 has not published a gallery or adopted a board.
