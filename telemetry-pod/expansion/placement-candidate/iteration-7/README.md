# Placement candidate, iteration 7 (two-level placement, D-PCB-13 v2 card lane; independent review: conditional proceed; not adopted)

Iteration 6 (`../iteration-6/`) re-packed on the same seed, policy, arrangement and allocation
with one change: J3's courtyard now covers the seated microSD card **and its 15 mm insertion
lane** (D-PCB-13 v2, fome-mc 2a70f7d/eb6b43a), after the iteration-6 review found the ADC U4
in that lane. Two-level placer, released agent-ee 15e92c9, 106.355 s wall in the sandbox.
The inputs are iteration 6's, but the arrangement is new: 10 of the 17 blocks (140 footprints)
moved, and `storage` went from under U1 to the bottom-left corner, so the SDMMC pad spans
U1 to J3 are 73.9–88.3 mm (iteration 6: 1.9–15.4 mm); see D-PCB-14. Otherwise: 17 blocks, fixed regulator clusters at their reviewed
iteration-5 poses, fixed GNSS corridor (U3, L3, D3, C42), IMU keep-outs and L1/L2 shadows as
obstacles, the 12 pad obligations in the policy (advisory).

## Checks on the candidate (packer board SHA256 `35f242c8…`)

| Check | Result |
| --- | --- |
| Two-level placer (`evidence/placement-*.json`, `block-provenance.json`) | placed, judgment pass, 309 of 309, 162 F / 147 B; 17 blocks arranged |
| Packer native DRC comparison vs seed | 3 `silk_over_copper` added (closed below) |
| Arrangement rules | no_stacking pass, thermal_spread pass; no_block_over_fixed 50 advisory (cross-side only) |
| Pad obligations (12 obligations, 26 pairs) | **26 pass** |
| D-PCB-8 silk policy (two passes) | 2 references hidden, 8 graphics to Fab, 3 references resized; `candidate-silk-policy.kicad_pcb.gz` |
| Native DRC, cited project, silk-policy board | **199 library findings only** (clearance, courtyard, hole, edge, drill, silk, text all 0) |
| J3 (microSD, B) | (9.12, 44.25) rot 0; lane courtyard x 1.26–17.05, y 15.2–53.1 mm; **no back-side part intersects it**; slot opens toward −y into the board interior |

Routing (planes + `kicad-route campaign`) on the silk-policy board is reported under
`../../routing-diagnostic/iteration-7/` when it completes. ## Independent review (`review/independent-review.md`): conditional proceed to routing

All claims reproduced (0 gaps under 0.25 mm, nothing under L1/L2 or within 4 mm of U2,
26/26 obligations, 17 blocks rigid, DRC identical, GNSS corridor intact, 487 of 499
connections unobstructed). Card path: seated region, 15 mm lane, 5 mm beyond and the strip
to the top edge all empty on B; no through-hole pad under it; the lane ends 15.5 mm from
the top edge and 4.0 mm from U2's courtyard; the card loads with the board out of the
enclosure. **Condition:** decide the SD bus length before adoption (D-PCB-14 accepts it at
the 20 MHz SDR target). Should-fix carried: J1 THT soldering access (R22 0.27, R50 0.31,
JP5 0.34, JP3 0.38 mm from pins/boardlock, slightly worse than iteration 6); U6/U12 0.26 mm.

Open: routing, then adoption. Carried should-fix from the iteration-6 review: THT soldering access around
J1's pins and boardlock; U6/U12 LDO spacing.
