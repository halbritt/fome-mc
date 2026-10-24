# 485-A3 single-leg source-template adoption

**All 143 single-leg source relationships are adopted. Eleven routing requirements remain pending. The full native contract still has explicit geometry and coverage findings.** This source change uses the sealed consumer `8ab3b0b95dd3ece043e67fff6bd226c36427ff22` and frozen A2 parent `a1678bdf6583263b4c0917de77a950f21c6748d6`.

The effective policy now has **201 obligations / 261 physical pairs**: the unchanged 58 A2 obligations / 118 pairs plus 143 explicit single legs. Each added obligation has exactly `id`, `kind: "single-leg"`, `metric: "pad-centre-to-centre"`, and one `leg` containing the exact source physical endpoints, original engineering target and advisory provenance. Templates use `role: "leg"` and retain each source template. No return is fabricated. All original A2 endpoint corrections, VIO-to-VCC returns, PGND/SW selectors and numeric targets are unchanged.

`coverage-ledger.json` preserves all **214 source rows**: 211 historical cross-face rows now have placement bindings, and three RF records have pending routing obligations. The full original source record and disposition history remain in each row. This source adoption does not declare complete support-pin coverage for every native footprint; the consumer's remaining coverage findings are retained below.

## Explicit guard migration

`guard-migrations.json` records every one of the 154 A2 material guards and its replacement:

- 143 G1 guards become exact single-leg placement bindings.
- Eight G2 guards become `contract.routing_obligations` of kind `no-via`: six ADS1119 bypass clauses and two crystal clauses.
- Three G3 guards become routing obligations of kind `controlled-impedance`, preserving their RF path, F-over-In1 reference corridor and 50-ohm requirements.

No routing clause is discharged. Each routing declaration has an explicit ID, `stage: "routing"`, physical terminal pairs, full source requirement and source path/hash/locator/quote. The source bytes are captured in `relationships.source_records`; the consumer verifies the hash, quote and native terminals. The consumer reports all 11 as **pending**, with native connectivity/via-count or RF-geometry/impedance evidence still required. An input claim of `status: pass` refuses. Both placement and saved reports preserve these obligations.

The generator removes only guards whose exact identities have a recorded placement binding or routing migration. Unrelated guards would remain. For the frozen A2 input there are **zero remaining material guards** after those 154 migrations; this does not remove the native findings or pending routing stage. `routing-obligations.json` is the source declaration; the consumer adds pending status and required evidence to its report.

## Actual consumer result and remaining findings

The declaration positive passes against the sealed consumer with the genuine native board capture. The standalone all-143 single-leg grade measures all 143, with **0 unknowns, 0 defects and 143 advisories**, status `info`. Of the 143 single legs, 142 exceed their retained engineering targets; those measured overruns remain visible advisories. All 261 targets remain advisory; no manufacturer or owner numeric authority is invented. Every policy endpoint resolves.

The full native report is **defect**, with three `cross_face_template_outside` findings:

| Relationship / role | Native 3D pad distance | Finding |
|---|---:|---|
| J3.4-C65-hf-decoupler / supply | 228.784 mm | C65 supply pad is outside J3's qualitative under-device courtyard projection. |
| J3.4-C65-hf-decoupler / return | 227.253 mm | C65 return pad is outside the same projection. |
| J3.4-C64-bulk-decoupler / leg | 225.144 mm | The newly represented C64 source leg also lies outside the projection. |

These are qualitative template failures, not advisory-radius failures. Advisory radii cannot enlarge the permitted under-device region. The board and templates are unchanged; the findings are neither waived nor repaired in this source slice.

The full report also retains **17 block-pin coverage groups / 72 references**, and **six internal-net geometry unknowns**. `NATIVE-FINDINGS.json` contains the complete reference lists, net names and reasons. The six internal nets are `/THERM_AUX1_SELECT` through `/THERM_AUX4_SELECT`, `/TIRE_CAN_L`, and `/TIRE_CAN_TERM`; their captured custom-copper centroids remain unqualified. RF feed footprints D3/L3 remain in placement pin-coverage findings while their source requirements are carried at the routing stage. Pending routing is not placement evidence.

## Controls and reproducibility

The actual consumer refuses an omitted leg, an omitted source relationship against the complete effective policy, a wrong native pin, stale A2 policy, changed routing source hash, wrong routing terminal, and a claimed routing pass. An opposite-side fault for the retained same-face crystal-load leg produces `same_face_required`. Source template permissions are preserved, including U6/U12 and U27–29 same-side requirements.

From a checkout containing the frozen A2 git objects:

```sh
python3 telemetry-pod/expansion/agentee-485-blocks/build_packet.py /path/to/native-probe.json
PYTHONDONTWRITEBYTECODE=1 python3 telemetry-pod/expansion/agentee-485-blocks/verify_packet.py \
  --agent-ee-src /path/to/8ab3b0b9/src --probe /path/to/native-probe.json \
  --report /path/to/validation.json
```

The generator reads immutable A2 git objects rather than its previous output. It verifies native board bytes and preserves the full source scope. `verify_packet.py` uses the real frozen consumer, validates exact A2 obligation preservation and explicit migration coverage, measures the single legs, and retains the full native residuals. `VALIDATION.json` records its controls. The evidence packet also includes a fresh pcbnew extraction/control run through `ae-ci-exec` on the sealed consumer worktree; the native board is only copied to temporary analysis storage and never resaved.

The policy bytes equal `relationships-effective.json` and are embedded byte-for-byte in the contract. Strict allocation/2 and eligibility remain null-bound for the producing stage; all 313 native footprints retain their full logical roles and the existing allocation/1 bridge. Board, schematic, power topology, reservations, pipeline and build files are untouched. `POLICY-HASHES.json` and `SHA256SUMS` seal the source artifacts. Review, runtime composition and landing remain with the integrator in the one combined 485 review.
