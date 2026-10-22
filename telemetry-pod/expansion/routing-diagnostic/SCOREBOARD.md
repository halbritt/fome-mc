# Telemetry-pod target scoreboard

Snapshot: 2026-10-22. Policy owner: agent-521. Update owner: agent-449 through the pod lane.
This records evidence and remaining work; it does not grant engineering or owner acceptance.
Source snapshot: fome-mc `683463d60ddb7d5ece6e4ebbc6cf2a82c0de07ed`.

## Current production outcome

| Requirement | Evidence at this snapshot | Next gate / holder |
| --- | --- | --- |
| Current captured design | j6 pipe-v5e preparation exists; dry-run finished 18:45:06Z, exit1/incomplete, earliest schematic stage; driver done=false. Preparation checks accepted this expected dry-run state. | j6 commit, independent review and449 integration; no qualified production placement yet. |
| Complete placement/routing | Not established on current production capture. Historical iteration7 is a diagnostic candidate, not a production result. | Bounded production campaign after qualifying capture and current router runtime. |
| Production router | Agent-ee main a8823389 still pins5f1c072; router main b5774496. | AGENTEE450,449: pin, adapter compatibility, image and actual runtime qualification. |
| Repair affects pipeline | K93 capability alone is insufficient. | AGENTEE455 approved, holder449/verifier510; waits for K93 integration plus qualifying pin, then real adapter fixtures and target comparison. |
| Native and independent qualification | No complete candidate-bound ERC/DRC/circuit/physical/RF packet established. | Candidate production checks and correction closure. |
| AMPSEAL/GPS models | Exact current-candidate J1/U3 binding and mechanical coverage open; U3 visualization is not manufacturer mechanical evidence. | FOMEMC34 through449. |
| Fabrication package | No qualified sealed release package established. | Sealed pre-DFM package, exact-package supplier DFM, separate ready attestation; no orders/uploads. |
| Renders | Gallery latest Iteration8 rendered2026-10-22T06:17:51Z, unrouted/unqualified. |449: initial refresh and persistent approximately4-hour schedule. |

## Historical diagnostics (not a matched production baseline)

Connected-net counts below are the retained README's net-grader reports. Raw unresolved
connection counts come from result.json and are a different unit. Never subtract raw
unconnected items from the total net count.

| Candidate | Reported connected nets | Raw unresolved connections | Introduced DRC / validation | Router process time | Evidence |
| --- | --- | --- | --- | --- | --- |
| microSD iteration7, builtin r0 |203/235 |55 |1 dangling via; validation FAIL including net_completion |318.089s; full pipeline total not established here |[result](iteration-7/candidate/iter8d-campaign-r0/result.json), [history](README.md) |
| same chain, Freerouting leftovers |205/235 |51 |0 additional findings against already-routed input;24 total DRC violations retained; validation PASS, routing INCOMPLETE |1566.23s additional router process time; total chain wall time unknown |[result](iteration-7/candidate/iter8d-fr-leftovers/result.json) |
| current-router iteration7 measurement |Not run |Unknown |Unknown |One attempt: router<=900s,total<=2100s |Queued behind AGENTEE450;449 owns dispatch. |

The builtin receipt identifies CLI557ae5758c06 and engine source89a2efbf5305;
Freerouting receipt identifies v2.5.0 and states its outcome may vary. Retain those
identities in comparisons. "Zero additional findings" in the chained run is not a
DRC-clean board and does not erase the input's defects. Historical placement reports
309/309 footprints but is conditional proceed and not adopted. See
[placement evidence](../placement-candidate/iteration-7/README.md).

## Obligations and next decisions

Enclosure/harness design and thermal/bench evidence remain open obligations. They are
not all pending owner questions. 519 reconciles actual owner questions and answers;
no unanswered default authorizes spending, uploads, orders or constraint relaxation.
U1/U2/U4 recorded owner temperature acceptances and U3/J3 delegated engineering decisions
must keep their different provenance. All actual thermal qualifications remain open.

Next spend decision follows the new current-router diagnostic and production capture
qualification. Proposed levers require bounded experiments; historical failures do not
prove that a method can never help a changed input/runtime. Preserve all sourced rules.
