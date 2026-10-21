# Placement candidate, iteration 7 (two-level placement, D-PCB-13 v2 card lane; pending independent review; not adopted)

Iteration 6 (`../iteration-6/`) re-packed on the same seed, policy, arrangement and allocation
with one change: J3's courtyard now covers the seated microSD card **and its 15 mm insertion
lane** (D-PCB-13 v2, fome-mc 2a70f7d/eb6b43a), after the iteration-6 review found the ADC U4
in that lane. Two-level placer, released agent-ee 15e92c9, 106.355 s wall in the sandbox.
Everything else as iteration 6: 17 blocks, fixed regulator clusters at their reviewed
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
`../../routing-diagnostic/iteration-7/` when it completes. Open: independent review, routing,
then adoption. Carried should-fix from the iteration-6 review: THT soldering access around
J1's pins and boardlock; U6/U12 LDO spacing.
