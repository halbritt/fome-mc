# 485-A2 incremental source-backed policy correction

**Supported increment implemented; full item-4 acceptance remains UNRESOLVED because the frozen consumer cannot express every required relationship.** This branch changes the effective locality policy and its contract sources. It retains all 12 original obligation IDs and every existing ADVISORY numeric limit, corrects the four bulk-input VIN selectors, and adds 46 supported obligations. It does not switch to an unrelated policy or claim production acceptance.

The corrected policy has **58 obligations / 118 physical pairs**. The source ledger accounts for **all 211 historical cross-face relationships plus three RF records**. Sixty-eight source rows have supported physical bindings; eight of those also retain a no-via gap. The 143 unpaired single-leg rows, three RF rows and eight no-via subrequirements remain **154 explicitly UNRESOLVED source rows**, each recorded as a required unknown in the contract. No unsupported requirement is accepted by omission.

## What changed

- C1/C2 now measure to **U5.2 VIN** and C8/C9 to **U7.2 VIN**, replacing EN pin 3. TI LMR36520 pin table p.4 identifies VIN2/EN3; layout p.27 requires input-capacitor locality to VIN/PGND. Sharing a net never makes the physical pins interchangeable. Existing bounds remain unchanged and advisory.
- U5/U7 input and VCC returns explicitly use **PGND pin 1**, excluding thermal PAD9 as an electrical selector. Primary p.4 says the pad is thermal rather than an electrical interconnect. Bootstrap returns remain **SW pin 8 → C5/C12 pin 2**, as specified by BOOT/SW evidence on p.4 and p.27. C98's existing U26.4→C98.2 return remains intact.
- All 47 historical relationships that declared supply and return legs have supported counterparts. Generic nearest-any-GND measurements are explicitly superseded by functional power-ground designations; grounded address, USB, card-detect, strap and thermal pins are not chosen merely because they share `/GND`. `selected-return-pins.json`, the native netlist pin functions and retained primary pin tables record each engineering designation. Numeric radii remain engineering defaults, never manufacturer values.
- Adopted 488 VIO returns are active pairs: **U21.3→C84.2** and **U100.3→C133.2**, both on `/+5V_CAN`. They are never replaced by a generic GND return.
- Eighteen existing single-leg source rows can be expressed using ten paired obligations. Each pair joins **two already-declared physical relationships** to distinct pins of the same support part: crystal, protection, termination or a two-leg sense network. No electrical edge or power topology is invented. The consumer field names `supply` and `return` are serialization roles here; the source ledger retains each leg's actual electrical kind.
- U6/U12's four regulator-capacitor relationships retain `same-face-only` on both roles. U27–29's six bypass relationships retain that template and explicit AGND/DGND designations from ADS1119 p.3. Their source no-via requirement remains a required unknown, because the frozen consumer cannot grade it from footprint-only geometry. The two crystal no-via source requirements are preserved in the same way.

## Full source disposition and acceptance boundary

`coverage-ledger.json` contains every original record, exact native primary pair, supported obligation/role bindings, disposition, source reason and unresolved subrequirements. `MAPPING.md` and `CROSS_FACE_MAPPING.md` render all 214 rows. `EXPLICITLY_SUPERSEDE` identifies an actual endpoint-selector or advisory-default correction; `DEDUPLICATE` points to an exact supported physical counterpart; `CARRY_FORWARD` preserves the existing source requirement. A disposition with `status: UNRESOLVED` does not claim successful implementation.

The full source ledger is captured verbatim in the policy's existing `source_records` text surface. The frozen consumer does **not** interpret that ledger. Enforcement of its unresolved requirements uses the existing contract mechanism: each required gap appears in the appropriate block's `material_unknowns`. `block_contract.check_complete` returns `unknown` and carries every guard forward. Deleting metadata from a report does not authorize resolving a requirement.

`block-contract-template.json` embeds byte-equal corrected locality and the updated eligibility document. The strict allocation/2 and eligibility source hashes remain **null** until the authenticated producer binds its own native board. Allocation still covers all **313 native footprints** exactly once in 26 full logical blocks, ten fixed roles and six shared TP roles. The /1 bridge is unchanged. Historical board-bound allocation-v2 is never used. Current mechanical reservations, board/schematic, pipeline and build files are unchanged.

## Smallest exact consumer gaps

1. **Single physical leg:** `electrical_locality._validated` requires both `supply` and `return` pairs, with distinct physical pads on the same support footprint. It cannot represent the remaining 143 declared single-leg relationships. The smallest schema extension must permit a nonempty explicit leg set without fabricating a second edge, while preserving legacy paired validation. Pair-specific templates and grading must consume that representation. Actual feedback-only input refuses with `locality obligation needs id, metric, supply and return; optional switch`.
2. **No vias:** `block_contract.judge` grades mounting side and pad-centre geometry; its capture contains footprints, not authenticated routed connectivity. Same-side placement does not prove a via-free connection. A source-backed no-via predicate needs explicit representation and authenticated routed evidence. Adding a `no_vias_required` field currently refuses as an unsupported obligation shape. Six ADS bypass and two crystal requirements stay unresolved.
3. **RF path:** the three RF records require path topology, F-over-In1 reference corridor and 50-ohm evidence. The source records have no resolved pad-centre radius, and the consumer supports only `pad-centre-to-centre`. Do not invent a distance or treat RF endpoints as proof of impedance. These rows remain explicit required unknowns.
4. **Advisory numbers:** `block_contract.judge` emits `required_numeric_authority_missing` for every advisory maximum. Full acceptance therefore remains unknown even where native endpoint geometry is known. Qualitative/source coverage and numeric enforcement authority must be separated; no hard radius is fabricated to obtain a pass.

These are implementation gaps for the integrator, not owner clarification requests. `unresolved-decisions.json` gives exact affected rows. The frozen consumer's declaration admission and endpoint-resolution positive passes. Its complete placement check correctly stays unknown; the packet does not claim an all-policy acceptance positive that the implementation cannot provide.

## Controls and reproduction

From the frozen fome input, use the genuine retained writer-C native probe and the frozen agent-ee source directory:

```sh
python3 telemetry-pod/expansion/agentee-485-blocks/build_packet.py /path/to/native-probe.json
PYTHONDONTWRITEBYTECODE=1 python3 telemetry-pod/expansion/agentee-485-blocks/verify_packet.py \
  --agent-ee-src /path/to/frozen-agent-ee/src \
  --probe /path/to/native-probe.json --report /path/to/validation.json
```

The generator verifies the probe against native board bytes and the reservations hash. The verifier uses the **unmodified consumer at 8e3b382b0f48525742cfd520e3f306b12e78a468**. It resolves all 236 policy endpoints and all 428 source primary endpoints, confirms complete source accounting, preserves every original radius, and exercises the real consumer's refusals for an omitted adopted relationship, wrong physical selector, stale policy, unauthorized VIO return and forbidden side. Policy-equality controls compare with the authenticated corrected effective policy; they do not claim the consumer reads manufacturer pin tables. Side faults mutate in-memory capture copies only. No board edits, native placement or routed-via qualification are performed.

`VALIDATION.json` records the results. `policy-before-cA2.json` and `eligibility-before-cA2.json` preserve the cA baseline, making the increment and required-unknown guards reproducible. `SHA256SUMS` seals the packet files. Full-project design-rule provenance and manufacturing acceptance are outside this source correction.
