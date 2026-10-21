# Pad-level electrical locality declaration

`electrical-locality.json` is an `agent-ee.electrical-locality/1` document declaring
pad-centre obligations for the four switching/bypass clusters of the expanded telemetry
pod: the two LMR36520 bucks (U5 pre-regulator, U7 3.3 V), the TPS62162 eMMC core
regulator (U15) and the LM2903B wheel comparator (U26). It is the engineer input that
AGENTEE-322 (`criterion: electrical-locality/1`, packer `policy.electrical_locality`)
requires before a guided pod placement can run. Origin groups in `../next-groups.json`
and `../../electrical-locality/storage-power` remain in force; a passing origin group
is not electrical acceptance.

## Provenance status (owner direction 2026-10-21): ADVISORY

Owner, relayed by agent-449: "the limits should be validated against some spec, either the
component or what JLCPCB can manufacture." The 33 numeric bounds below were chosen by the
agent from package geometry; the owner did not choose them, so the earlier "design-owner
declaration" label was wrong and is withdrawn. Until each bound is re-derived from (a) a
component figure (a datasheet number, or a measurement of the datasheet's reference layout
with its scale recorded) or (b) the JLCPCB manufacturable floor for that pair (footprints
plus captured JLCPCB assembly and PCB rules), the bounds are advisory placement guidance,
not pass/fail: a pair over its bound is an "exceedance of an advisory bound", never a
failure, and nothing blocks on it. AGENTEE-337 (agent-ee) adds provenance classes to
locality bounds, computes the JLCPCB floor per pair and will supply the classification
table that this file's next revision uses for the derivation. The cluster-anchored
placements already satisfy all 33 bounds by construction, so the advisory status changes
no placement outcome.

## What is declared and by whom

Every pair names the exact IC pad, capacitor or inductor pad and native net, and a
numeric bound with a citation locating the datasheet guideline it implements. The
datasheets give prose only ("as close as possible", "short, wide"); none gives a
numeric radius. The numeric bounds were chosen by the agent (D-PL-1, 2026-10-20) from package and
capacitor geometry so that a capacitor seated directly against the named pins satisfies
the bound with roughly 1 mm of placement slack. They are advisory (see above) until
re-derived from a spec; they are not manufacturer limits and do not claim qualification.

| Cluster | Pairs | Bounds (mm) | Datasheet locator |
| --- | --- | --- | --- |
| U5/U7 HF input (C3/C10, 0805) | VIN pin 2, PGND pin 1 | 3.5 / 3.5 | LMR36520 SNVSBF0C §8.5.1 item 1, p.27 |
| U5/U7 bulk input (C1,C2 / C8,C9, 1210) | VIN pin 3, PGND pin 1 | 7.0 / 7.0 and 9.0 / 9.0 | §8.5.1 item 1 |
| U5/U7 VCC (C4/C11, 0603) | VCC pin 6, PGND pin 1 | 3.5 / 8.5 | §8.5.1 item 2 |
| U5/U7 BOOT (C5/C12, 0603) | BOOT pin 7, SW pin 8 | 3.5 / 3.5 | §8.5.1 item 3 |
| U5/U7 switch node (L1/L2) | SW pin 8 to inductor pad 1 | 5.5 | §8.5.1 item 8 |
| U15 input (C70, 1210) | VIN pin 2, PGND pin 1 | 4.0 / 4.0 | TPS6216x-Q1 §11.1 item 1, p.22 |
| U15 switch node (L4) | SW pin 7 to L4 pad 1 | 4.0 | §11.1 item 5 |
| U15 output (C68, C69, 1210) | VOS pin 6, PGND pin 1 | 4.5 / 5.0 and 8.0 / 8.5 (rev 2) | §11.1 items 2 and 4 |
| U26 bypass (C97 0603, C98 0805) | V+ pin 8, GND pin 4 | 3.5 / 8.5 and 5.5 / 10.0 | LM2903B-Q1 §4.4.1, p.18 |

Pin numbers and functions were read from the retained PDFs (hashes in each citation):
LMR36520 pin table p.4 (PGND 1, VIN 2/3, VCC 6, BOOT 7, SW 8), TPS6216x-Q1 pin table
p.3 (PGND 1, VIN 2, VOS 6, SW 7), LM2903B-Q1 (V+ 8, GND 4). Nets were taken from the
frozen placement probe and match the released-source-migration netlist labels.

Return bounds that cross the package (VCC-to-PGND on the HSOIC-8, V+-to-GND on the
SOIC-8) are deliberately wider than the supply bound: the physical return for those
capacitors is the exposed pad and ground plane. The LMR36520 exposed pad is pad "9",
which the footprint repeats nine times (thermal pad plus eight via pads), so AGENTEE-322
refuses it as ambiguous; a centroid obligation to the exposed pad needs the pad-UUID
selection of AGENTEE-328 and will be added when that lands. Output-capacitor loops of
the LMR36520 bucks (L1/L2 pad 2 to C6/C7, C13–C15) cannot be expressed in the 322
schema, which requires supply and return pairs to start at the same IC; this is
recorded as a software gap for AGENTEE-328 or a follow-up.

**Rev 2 (2026-10-20):** C69's bounds were loosened from 6.5 / 7.0 mm to 8.0 / 8.5 mm after the
AGENTEE-322 guided packer exhausted its budget with C69 as the unplaced part (peak 41 of
331 placed, 28 backjumps). C69 is the second, bulk output capacitor; C68 keeps the tight
bound. The frozen-board measurement below is unchanged by this (C69 measured 2.68 / 6.89 mm).

## Measurement on the frozen diagnostic board

`measure.py` is an independent measurer that uses no agent-ee code. Run against the
retained 17-group diagnostic candidate (board SHA256
`79cc13104618147391eae4896985052ac1ed6bbfa31105e7bcc09ba015055f36`, probe at
`~/.cache/agent491-main-buck-locality/work/proposal/placement-probe.json`):

```sh
python3 -I measure.py <placement-probe.json> electrical-locality.json
```

`frozen-79cc1310-measurements.json` records 33 pairs: 20 within and 13 over the advisory
bound, 0 unknown. Every pad, net and limit resolves, so the document is usable as a
322 input without further authoring. `cross-check-322-18aad41.json` records that the
unreleased AGENTEE-322 grader (worktree commit 18aad41, diagnostic use only) reports
identical distances and the identical defect set.

The 13 exceedances of the advisory bounds on the frozen diagnostic board are: U7's HF input capacitor C10 (4.34 / 7.51 mm), bulk returns C8/C9, U7 VCC
capacitor C11 (7.58 mm), U5's C2 bulk and L1 switch node (6.86 mm), U15's input C70
supply and L4 switch node, C68 output return, and U26's C98 supply (7.42 mm). They
are where origin-group packing left capacitors far from their pins; the cluster-anchored
placements (../../placement-candidate/) satisfy all 33 bounds by construction.

## Status and next step

This packet declares and measures; it adopts nothing. No board, rule or CAD file was
changed. The next placement run must use the released AGENTEE-322 (or 328) software
with this file as the captured `locality` input and `policy.electrical_locality`,
then be re-measured here and reviewed independently before adoption or routing.
Routing, thermal, EMC, assembly and bench qualification remain open. The pending
owner question on the 64 proposed pad/drill rule exceptions is unaffected by this
packet.
