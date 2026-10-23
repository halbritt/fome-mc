# placement-r4: B.Cu placement of the 22 — STOPPED at the admission interface (before any new tool code)

Assignment: agent-521 brief d7978659 (via agent-519); plan agent-ee main `f7216fb1`, revision 4, "Next action (revision 4)". The owner permission is REQUIREMENTS.md:65 (double-sided placement), with side changes authorized only for R7, R70–R84 and TP1–TP6. These are coordinator records, not owner text.

**Clock:** started 2026-10-23T06:23:53.81Z; result written about 06:26Z. One task.

**Outcome:** the brief's STOP clause applies. **The existing agent-ee 7d5b0d4d admission/write path cannot represent the declared side-change transform.** So nothing was placed or saved, and no partial or relabelled board exists. No gate was bypassed, and no new tool code was written. The R1–R3 evidence is untouched.

## The precise interface refusal

The evidence is `interface-probe.json`, produced by `r4_interface_probe.py` in one admitted container. Lease `7c8b9272b192` (`native-admit-events.jsonl`), image `d96f8e00`, agent-ee 7d5b0d4d R2 step snapshot (`placer_runner.py` sha256 `76308585…`, byte-identical to 7d5b0d4d), run on a disposable copy of the input board `2f1c9557…`.

| # | Existing interface (7d5b0d4d `src/agent_ee/placer_runner.py`) | Observed | Consequence |
|---|---|---|---|
| a | `_apply_plan` (`:671-679`) writes a placement with only `SetOrientationDegrees` and `SetPosition` | Called with `{'ref': 'R7', …, 'side': 'B'}`: the saved R7 has `IsFlipped() == False`, layer `F.Cu`; the declared side is **silently ignored** | The plan/write interface has no side field; it cannot express the 22 authorized flips |
| b | `_evaluate_proposal` (`:717-731`) refuses unless `_pad_inventory(saved) == _pad_inventory(board)`: **"native saved board changed footprint pad geometry"**. `_footprint_pad_inventory` (`:121-141`) includes each pad's `GetLayerSet().FmtHex()` | A legal native `Flip(position, FLIP_DIRECTION_LEFT_RIGHT)` of R7 changes **only `layer_set`** for both pads, `…00002003` → `…0000800c` (the pad's layer set moves to the mirrored side; flipped layer reported `B.Cu`-side). Pad uuid, number, net, shape, size, offset and FP-relative position and orientation are unchanged. Nets are unchanged | The gate compares against the board it is handed and has no notion of a declared transform. It therefore refuses every authorized flip. Pre-flipping the input board to make the gate pass would move the baseline, which is a bypass, so it was not done |
| c | `placement_probe.extract` + `placement.judge` | A flipped R7 is represented: courtyard side `B`, as the sourced-fixed J3 already is in the input; judge runs | The capture and judge **can** represent B-side parts; only the write/admission gate (a, b) cannot |

## Minimum required correction (agent-ee change; agent-521 / integrator decide; not written)

1. **Request authorization.** The request carries an explicit `side_changes` list. Here that is exactly R7, R70–R84 and TP1–TP6, each with its target side. Any flip not on the list is refused.
2. **`_apply_plan`.** For a placement whose declared side differs from the footprint's current side and whose ref is authorized, call `fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)` before the existing orientation/position set. Otherwise behaviour is unchanged.
3. **`_evaluate_proposal` pad-inventory gate, as a declared transform.**
   - For each authorized flipped footprint, compute the expected inventory as `_footprint_pad_inventory` of a disposable copy of the **original** footprint after the same native `Flip`, and require byte-equal equality with the saved one.
   - Every other footprint keeps today's exact-equality check.
   - Nothing is relaxed. The check changes from "unchanged" to "equal to the declared native transform of the original".
4. **`_saved_judgment`.** Also compare the saved side with the declared side for every placement.

With that correction, the rest of the R4 task would be:
- the 287 R2 poses plus 22 explicit B.Cu poses, chosen against the native keepouts and reservations near each part's nets and test-point access;
- the whole-board `_evaluate_proposal` under policy r1 (judge, groups, locality, native courtyard DRC, netlist binding);
- full native DRC, parity and unconnected checks, and the preservation checks.

All of that runs with existing code.

**Side-specific limitations recorded:** none found for the 22 in the probe. Nets and pad numbering survive a flip unchanged. Test-point access from the back is an assembly/test decision that this probe did not assess.

## Not done

No positions were chosen for the 22, no board was saved and no render was produced, because there is no candidate. The native baseline stays 21 DRC / 499 unconnected (R2 `run/drc-before.json`). No release qualification is claimed.
