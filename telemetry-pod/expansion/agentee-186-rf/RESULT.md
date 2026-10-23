# AGENTEE-186: stackup metadata (HOLD) and RF source consumption

Decisions from agent-529: 8900b0a9, 7526f49d, and 4cf9d43d v2 (ADOPTED 0.293 mm).

## Run record

**Clock:** started 2026-10-23T12:22:10Z, ended 2026-10-23T12:42:43Z.

**Branches:** fome-mc `wt/agentee-186` (from 488 c98e1135); agent-ee `wt/agentee-186-rf` (from a085fbfa).

**Runtime:** native-admit on proximal.

## Stackup metadata: HOLD (source is agent-ee scaffold.py, a protected path)

- **Native (installed board):** every dielectric is `(type "core")`, `(material "FR4") (epsilon_r 4.5) (loss_tangent 0.02)`.
  - Thicknesses are correct: 0.2104 / 1.065 / 0.2104 mm.
  - The fab profile JLC04161H-7628 has outer prepreg 7628 at 0.2104 mm, Er 4.4, and a core of 1.065 mm at Er 4.6.
- **Source trace:**
  - The fome-mc envelope (`composition/envelope.json` stackup, quoting `sources/jlcpcb-stackup.txt`) declares only `kind: dielectric` with thickness; it carries no prepreg/core type, Er or loss tangent.
  - agent-ee `src/agent_ee/scaffold.py:149` (a085fbfa) writes `['type', 'core']` for EVERY dielectric and no Er/tan. pcbnew's save then fills in its FR4 defaults (Er 4.5, tan 0.02).
- **Why it stops:** `scaffold.py` is on the forbidden-path list (agent-524's scaffold fix a8fece00).
- **Change needed (for 449 to sequence with 524):**
  - (1) In the fome-mc envelope source, declare per dielectric `dielectric_type` (prepreg / core / prepreg) and `epsilon_r` (4.4 / 4.6 / 4.4) with the jlcpcb-stackup citation. Leave loss tangent explicitly unknown, because no source exists.
  - (2) agent-ee `scaffold.py:149` emits `type` and `epsilon_r` from the envelope. It also needs a decision on how to represent an unknown `loss_tangent`, because KiCad otherwise writes its 0.02 default. That default must be recorded as a default, not a source value.
  - (3) agent-ee `board_envelope.py:2041` already accepts the `('core','prepreg')` types. Check that `envelope_check.compare_stackup` still passes, since `layer_thickness_tolerance_mm` is an exact metadata comparison.
- **Unchanged:** board layer thicknesses and the 1.6 mm board thickness. Calculator T1 0.04064 mm is NOT a fab copper thickness.

## RF: fome-mc `design-rules/telemetry-pod.kicad_dru` (commit 575f0463)

The 484r exact-net selector `A.NetName == '/POD_GNSS_RF'` is KEPT, and it is active.
- **`agent_ee_netclass_RF_50`:** track_width min = opt = max **0.293 mm**, replacing min 0.335 mm.
- **`agent_ee_RF_50_cpw_gap`:** on F.Cu, clearance min **0.2032 mm** to any other net (both flanks).
- **`agent_ee_RF_50_launch_transition_REVIEW`:** an explicit SCOPE for segments intersecting the U3/J2 courtyards. Its values equal nominal until a reviewed relaxation exists; it is never a net-wide waiver.
- **Basis** (recorded in `design-rules/README.md` and the agent-ee binding):
  - Z 50.0087997251 ohm, eff Er 3.1696914377, at T1 0.04064 mm (JLC calculator 1.6 mil basis);
  - H1 0.2104 mm, Er1 4.4, mask C1 1.2 / C2 0.6 mil, CEr 3.8;
  - taper 0.5 mil (client config); the JLC guide's 0.7 mil is recorded as a difference, not merged.
  - The historical forward point 47.394 ohm @ 0.335 mm, T1 0.035 mm, is kept with its own inputs.
  - Guide: https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator (529-read; no new capture).
- **Not claimed:** no tolerance band and no impedance verification.
- **Regenerated** via `production_run.sh` from 575f0463: 28/28 stages, build reproduces, observe exit 0.
  - Retention: `evidence/emission-7d5b0d4d-agentee186/` (408 files, `retain.py --check` OK).
  - Installed: `.kicad_dru` **d4ce8f95ea3cf80a7de7d0bed33c3867377c48dea20f68664cb84b0af3806433**. The schematic (78637c6e), board (cbfea9be) and pro (85c517aa) are unchanged from 488.

**Native controls** (`rf_controls.py`, on DISPOSABLE copies; `rf-controls-new.json`, `rf-controls-installed.json`, and `rf-controls-484r-rules.json` for comparison):

| Control | Result |
|---|---|
| nominal 0.293 | no finding |
| too narrow 0.25 | `agent_ee_netclass_RF_50` min 0.2930 |
| too wide 0.34 | `agent_ee_netclass_RF_50` max 0.2930 |
| gap 0.201 (below 0.2032, above the 0.2 default) | `agent_ee_RF_50_cpw_gap` 0.2032 |
| gap 0.30 (above nominal) | **no finding** (see the missing capability below) |
| wrong net (/GNSS_PPS 0.25) | no RF finding |
| launch inside U3 courtyard 0.25 / 0.34 | REVIEW rule min/max 0.2930 |
| selector still active | yes: the too-narrow finding names the rule |

## RF: agent-ee (`wt/agentee-186-rf` commit 6678bb12, not merged)

- **`fixtures/telemetry-pod/rf-net-constraints.json`:** track_width_mm 0.334416796875 → 0.29286522460874 (clearance 0.2032).
- **`fixtures/telemetry-pod/rf-inverse-50ohm-result.json`:** NEW, byte-for-byte agent-510 `inverse-result.json` (046d421b…).
- **`fixtures/telemetry-pod/rf-source-capture.json`:** `w2_continuation.dimension_mapping`:
  - W1/W2 are now from the inverse (11.5301269531 / 11.0301269531 mil);
  - constraint_sha256 d0d03633…;
  - emitted_min_track_width_mm 0.293;
  - `adopted_inverse` binding: path, sha, dErEff pointer `/impedance_calc_result/dErEff`, basis, packet hashes including RESULT-inverse 00fe444c…, the historical point, and not-claimed.
- **Docs:** `docs/gnss-rf-path.md`, `docs/routing-policy-contract.json` / `.md` (RF_50 is now active via the 484r selector; values 0.293 and 0.2032).
- **`tests/test_gnss_rf_path.py`:** the 0.335 / 335000 / 334999 probes become 0.293 / 293000 / 292999. The width-mapping test now verifies the adopted inverse binding (sha, dResultValid, Z, Er_eff, jBackCalc).
- **Tests (CI image, native-admit + ae-ci-exec):** `tests.test_gnss_rf_path` plus `tests.test_routing_policy_contract` 18/18 OK; `tests.test_rf_geometry` 57/57 OK (run with PYTHONPATH=.:src:tests, because the default harness path fails to import `toolchain`).

## Missing capability: measured two-flank gap and connected In1 reference

KiCad DRC can only bound the gap from below. A gap above nominal, and In1 reference continuity, need the routed-geometry consumer.
- **The consumer exists:** agent-ee `src/agent_ee/rf_geometry.py` measures the `cpw` section (width, gap to coplanar ground on BOTH flanks, and reference-layer ground under trace plus gaps) and the `guard` section, from an `agent-ee.rf-geometry/1` declaration.
- **It is NOT consumed for this pod.** The compiled scope (`requirements/rev3-microsd/compiled/scope.json`) has only `routing-geometry` with empty params, and fome-mc declares no `agent-ee.rf-geometry/1` for /POD_GNSS_RF.
- **What is needed (bounded delta, fome-mc requirement-map + one declaration file):**
  - an `rf-geometry` routing-stage check in `requirements/rev3-microsd/requirement-map.json`;
  - an `agent-ee.rf-geometry/1` declaration: net /POD_GNSS_RF, ground /GND, signal F.Cu, reference In1.Cu, `cpw` with its source bound to `rf-net-constraints.json` / `rf-inverse-50ohm-result.json`. The tolerances must come from the coordinator: no tolerance band is invented here, so `width_tolerance_mm` / `gap_tolerance_mm` are an OPEN decision.
  - Then recompile the scope.
- It applies only after routing.

## Deltas for 449 to forward

- **479/524:** the stackup change in `scaffold.py:149` (above).
- **486:** none from this slice.
