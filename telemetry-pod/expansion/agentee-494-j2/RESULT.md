# AGENTEE-494 J2 joint and sealed interface

The selected Amphenol 132134 supports a concrete sealed interface: keep it inside the enclosure and connect it to an Amphenol 095-902-570-006 IP67 SMA bulkhead cable assembly. The stock holes do not establish a worst-case insertion guarantee. This packet supplies the original pattern, a conditional enlarged-hole footprint and writer recipes. Complete joint, packing, RF and enclosure acceptance remain open for the specific evidence listed below.

The frozen base is `f6c7ec25e4f1bcd5411c376f3db970bbd2d31650`. REQUIREMENTS.md hashes to `dd6555f706d163709bccb3417d8c366c38de7d603fca8894d0c4a95a58928208`. Agent-449 integrates and arranges the single 15-minute Fable review; this branch is not merged.

## Joint budget and footprint

`joint-budget.json` contains all assumptions and equations. The retained [132134 rev C drawing](https://www.amphenolrf.com/en-us/assets/file/4065789557/) controls the part dimensions; its retained PDF hash is `1ec1d365bf5bf9e1598cf7cf2c90747ba11f06607f4c6a28ca6d30a0aab56034`. [JLCPCB's capability](https://jlcpcb.com/capabilities/pcb-capabilities/) gives finished holes +0.13/−0.08 mm, position ±0.075 mm and board thickness 1.44–1.76 mm. The budget conservatively treats position as ±0.075 per axis.

The signal pin maximum is 1.37 mm. A conservative square ground-pin side is 1.17 mm, inferred from the independently toleranced outer and inner spans, giving a 1.6546 mm circumscribed diameter. Applying ±0.10 mm per axis from the mounting pattern as a **physical pin-location bound is conditional**: the drawing does not separately specify true position about the signal pin. The combined radial displacement is 0.24749 mm.

| Pattern | Signal hole / pad OD | Ground hole / pad OD | Signal insertion margin | Ground insertion margin |
|---|---:|---:|---:|---:|
| Manufacturer holes / KiCad pads | 1.5 / 2.05 | 1.7 / 2.25 | −0.22249 | −0.26480 |
| Conditional proposal | 2.0 / 2.8 | 2.4 / 3.2 | +0.02751 | +0.08520 |

All values are mm. Both files are in `Agentee494.pretty`. Hole centres remain (0,0) for pad 1 and (±2.54,±2.54) for four pad 2 objects. `pad-map.json` binds pad 1 to `/POD_GNSS_RF`, all pad 2 objects to `/GND`, and preserves canonical J2 UUID `18c6ebf4-5f6a-5227-b278-be0fa33a91c9`. F(103,40,0) is a candidate only.

The proposal has nominal 0.40 mm annuli; maximum-hole arithmetic leaves 0.335 mm, or 0.22893 mm after conservatively subtracting radial hole position again. Actual drill-to-copper registration and pad etch are not independently guaranteed by that general position figure. Larger holes also need a qualified solder-fill and retention process. Positive insertion arithmetic does not close those questions.

With zero seating lift, bare pins project 1.78–2.90 mm below B. Let seating lift be `sF` and B-side solder-filleting depth be `fB`: the soldered B reservation is `max(2.90−sF,fB)`. The F body is bounded by 7.2 mm square and `9.73+sF` mm above F. Neither maximum `sF` nor `fB` is published here; a finite soldered maximum is not claimed.

## Sealed SMA and assembly

The exact [095-902-570-006 part page](https://www.amphenolrf.com/en-us/part/095-902-570-006/9372/) and [95-902-570-XXX rev A drawing](https://www.amphenolrf.com/en-us/assets/file/4068761521/) identify a standard SMA right-angle plug, RG-316 and IP67 bulkhead female jack with O-ring hardware. That plug mates to 132134. Only the bulkhead jack crosses the wall; the only penetrations remain AMPSEAL and SMA. The family brochure reverses 569/570 orientation descriptions relative to the exact drawing and product page; use the latter for 570.

The 6-inch assembly has 152.4 mm nominal length and ±6.35 mm tolerance, maximum 158.75 mm. Retain the owner's ≤500 mm external antenna cable limit. A conservative **combined** cable allocation leaves 341.25 mm maximum externally; this is an advisory allocation, not a newly attributed owner requirement. Bind the exact antenna/cable before claiming both limits. An existing 457 mm external cable does not satisfy the combined allocation.

`sealed-interface.json` and `reservations.json` give the wall, both-face body, insertion, cable, wrench and soldering recipes. The mounting-hole figure is nominally Ø6.60 with a 6.10 flat dimension; the 5.85 D-flat labels the connector. The PDF text was available, but direct download returned HTTP403 and its distributor mirror timed out. The figure/tolerance interpretation therefore remains to be visually checked before panel manufacture. No panel thickness, seal compression, torque or complete installed ingress qualification is invented.

`manual-fit.json` proposes the REQUIREMENTS criterion 5 `not_assembled` deviation: J2 from DigiKey **ACX1230-ND / 132134** and cable assembly from Newark **25AK8098 / 095-902-570-006**. Exclude J2 from JLC assembly BOM/CPL while preserving its electrical membership; hand-fit before case installation. This names purchase sources without claiming JLC stock absence, current availability or placing an order. The canonical writer must implement and verify export handling.

## Verification and remaining evidence

`native494.json` records PASS for footprint loading and all five native pad sizes, drills and candidate pad bounds, through peecee-wsl `native-admit`, KiCad 10.0.7. It uses an ideal 110×80 rectangle. It proves no final saved Edge.Cuts clearance, DRC, connectivity, packing or joint qualification. No canonical board was loaded or saved. The 490 RESULT.md and verification record now explicitly disclose the same ideal-outline limitation for J3.

`RF-deltas.json` invalidates the old (106.96,40) endpoint and end launch, PTH antipads, ground transitions and affected support/cable cutouts. Regenerate board areas `460352a8-dace-51a2-842b-c1e4ef7ad212` and `93d1ddf1-382d-5ed8-abfa-2bf617ad0cae` after dependent geometry changes. Preserve ordinary 0.293/0.2032 pending 492; no net-wide waiver or new stackup is introduced.

Material evidence still needed: physical pin-axis datum, actual hole/copper registration and etch, solder fill/retention and fillet maxima, complete mating-plane and tool solids, panel/O-ring stack and torque, strain relief and exact antenna length, then final saved-board launch/reference/packing checks and installed enclosure IP67 verification. These are concrete qualification gaps; the proposal is not ready for fabrication acceptance.

Doctrine packet `pkt-86b8048d49bc089c`, hash `86b8048d49bc089c4ac5ff0c89b821562f5e6a1dbedd5a48e2db5f0f6e094d0f`, used authority boundaries, evidence before intervention, explicit invariants and repository precedence. `analysis/decision-receipt.json` abstains from complete admission. The validated corpus is `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`; unmet obligations retain their materiality classifications.
