# AGENTEE-484r: RF width-rule binding in the design source, and production_run.sh unconfined

Decision: agent-529 39bfdc72 (comment 9c8f6770 on AGENTEE-484), relayed via 519.

## Run record

**Clock:** started 2026-10-23T10:16:58Z, ended 2026-10-23T10:39:54Z, within the 40-minute bound.

**Model and host:** Claude Opus 5.5 on proximal.

**Worktree:** `wt/agentee-484r` (git-wt), base fome-mc `07ed909`.

**Runtime:** native-admit only. No AppArmor profile was loaded or tested; no cloud or upload.

## Part 1: production_run.sh

- **`production-capture/production_run.sh`:** the host-dependent selection (`profile=agent-ee-container` when AppArmor is enabled) is replaced by an explicit `--security-opt apparmor=unconfined`, per the owner ruling "remove the apparmor profiles like I asked".
- **`production-capture/runtime_receipt.py`:** the recorded (not executed) campaign launch command also used `apparmor=agent-ee-container`; it now uses `apparmor=unconfined`.
- **Not changed:** the sealed copies under `evidence/production-runtime-j6b/`.
- **Re-run:** the committed script itself ran under native-admit (`--class suite --weight 4`) from commit `9de12bd`: build-out exit 0, build-check exit 0 ("reproduces byte for byte"), pipeline exit 0 (**28/28 stages accepted**), observe exit 0, `exit=0`. See `logs/production-run-summary.txt`.

## Part 2: RF width-rule binding

**Where the fix lives.** `pipeline.py:189` copies `design-rules/telemetry-pod.kicad_dru` into the project byte for byte. `board-setup.kicad_pro` is rewritten by the agent-ee scaffold, so a net-class assignment there would depend on agent-ee preserving it. The binding is therefore a **source-declared direct net selector** in the fome-mc rules source. **No agent-ee code was needed or touched.**

The rule changes from:
```
(condition "A.NetClass == 'RF_50'")
```
to:
```
(condition "A.NetClass == 'RF_50' || A.NetName == '/POD_GNSS_RF'")
```
- The constraint is unchanged: `track_width (min 0.335mm)`.
- No other rule or clearance changed.
- The F.Cu-over-In1 requirement is unchanged.
- `constraints.json` is not edited, because the J1 hand-fit chain pins its bytes; `design-rules/README.md` records the selector.

**Regenerated through the existing production path,** then retained (`retain.py` → `evidence/emission-7d5b0d4d-agentee484r/`, `--check` OK) and installed.
- The schematic, board and `.kicad_pro` are **byte-identical** to 07ed909.
- Only the installed `.kicad_dru` changed.

**Native proofs** (`drc_proof.py`, under native-admit, on DISPOSABLE copies of the installed project). Three test tracks were added on F.Cu: T1 0.20 mm on /POD_GNSS_RF, T2 0.335 mm on /POD_GNSS_RF, and T3 0.20 mm on /GNSS_PPS as a control.

| Rules file | T1 (0.20 mm RF) | T2 (0.335 mm RF) | T3 (0.20 mm control) | Total violations |
|---|---|---|---|---|
| new, bound (`drc-proof-bound.json`) | **"Track width (rule 'agent_ee_netclass_RF_50' min width 0.3350 mm; actual 0.2000 mm)"** | none | none | 221 |
| old, unbound (`drc-proof-unbound.json`) | **none** (narrow RF copper passes silently) | none | none | 220 |

- **(a) The net is selected.** Native DRC resolves rule `agent_ee_netclass_RF_50` for /POD_GNSS_RF copper, and does not resolve it for another net.
- **(b) Too-narrow copper is rejected.** It is flagged with the binding and not flagged without it.
- The other 220 violations are identical in both copies. They are inherited findings of the unrouted board, not part of this change.

**Limits:**
- The binding enforces a minimum width only. It does **not** prove 50-ohm impedance; that needs the fabricator stackup and the reference-plane check (AGENTEE-480).
- The existing ROUTE-3/4 copper was not re-checked here.

## Files changed (sha256)

| File | sha256 |
|---|---|
| `telemetry-pod/expansion/production-capture/production_run.sh` | `59061128d7c83e5a45c0ef6a2cd66b1a659d29d4c6e40df1b9e2356a0b6734d4` |
| `telemetry-pod/expansion/production-capture/runtime_receipt.py` | `6ad2399870223ff247ee3f05597c2ef123202898cad8f93691a44f9946069b92` |
| `telemetry-pod/expansion/production-capture/retain.py` | `ef6c20a2a389f4da25e9805f5c65a37d0e586a58464618a54bac9fc59f920062` |
| `telemetry-pod/expansion/design-rules/telemetry-pod.kicad_dru` | `2769902a266944f8f9a5a47785e65beec19be74804d3776cd8007b6b7f288271` |
| `telemetry-pod/expansion/design-rules/README.md` | `8bce72ce242a44fc1ae1f9b307038dc17a030f7fb89690c75b0a27f1c5eefb02` |
| `telemetry-pod/telemetry-pod.kicad_dru` | `2769902a266944f8f9a5a47785e65beec19be74804d3776cd8007b6b7f288271` |
| `telemetry-pod/telemetry-pod.kicad_pro` | `33ab13e734fb424cfbc77f113d46a877c8f1cc6fb180e00086617f4fd491b3f7` |
| `telemetry-pod/telemetry-pod.kicad_sch` | `cef8e4c7f3b60e1afd434da171a0e431cead68f6df465d987a1e7118035a6d9c` |
| `telemetry-pod/telemetry-pod.kicad_pcb` | `0b68a0ac4b3978b77faa497fd208b35a376c89d576f1b4e08b276966db997eac` |

Regenerated project: schematic `cef8e4c7…` and board `0b68a0ac…` (both unchanged), `.kicad_pro` `33ab13e7…` (unchanged), `.kicad_dru` **`2769902a…`**.
