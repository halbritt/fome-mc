# Placement candidate, iteration 6 (two-level placement on released agent-ee 15e92c9; pending independent review; not adopted)

First pod placement by the released two-level placer (AGENTEE-339/340/355): 17 engineer
blocks packed in isolation (stage A, `inputs/candidates/`), arranged as rigid macros and
completed by residual packing (stage B), in 168.846 s wall inside the sandbox
(`evidence/packer-execution.json`). Source: `../../storage-microsd/` (microSD, eMMC gone).

## Seed and fixed parts (`inputs/seed.kicad_pcb.gz`)

`../../placement-seed-microsd/base-seed-viapatched.kicad_pcb.gz` (D-PCB-1 thermal vias) with
the D-PCB-13 card envelope in J3's courtyard, plus these locked parts:
- the historical anchors J1, U1, U2 and H1–H4, J2 at the D-PCB-4 edge pose;
- the reviewed GNSS RF corridor of iterations 3–5: U3 (71.5, 35.0) rot 180, L3 (80.6, 28.6),
  D3 (80.485, 25.97), C42 (80.6, 31.81);
- the two buck regulator clusters at their reviewed iteration-5 poses (U5 at 29, 14 and U7 at
  36, 29 with C1–C7, L1, R2, R3, R27 and C8–C15, L2, R4, R5, R28). They were meant to come
  from the block library (`inputs/library/`: entries imported from the iteration-5 board),
  but `materialize` refuses them because the courtyard identity hash is not canonical under
  rotation (AGENTEE-370, fix in progress); carrying them fixed is the interim path.

## Policy and arrangement (`inputs/policy.json`, `inputs/arrangement.json`)

Packing policy: gap 0.25 mm, the 12 pad obligations of `../../electrical-locality/pad-obligations/`
(advisory, AGENTEE-337), groups u20/u21/u22 local, gnss-antenna-power (U10 within 15 mm of U3),
gnss-local (R24–R26 within 12 mm of U3), obstacles = IMU exclusion (B) and ring (F) plus the
L1/L2 inductor shadows on B (courtyard + 0.5 mm, as in iterations 2–5). Arrangement: step
budget 200 000, priority blocks power-entry and supplies-5v, objective pad-locality /
inter-block-wire / thermal-spread, thermal U5–U7 15 mm (advisory), no_stacking L1/L2 (advisory;
the obstacles make it hold), no_block_over_fixed (advisory, storage exempt).
Allocation: `../../blocks/allocation.json` at fome-mc 3fe6e68 (17 blocks; gnss, pre-6v3 and
buck-3v3 dissolved because their members are fixed; C18/R33/C38/C41/C43/C44 residual).

## Checks on the candidate (packer board SHA256 `172d3d4e…`)

| Check | Result |
| --- | --- |
| Two-level placer (`evidence/placement-*.json`, `block-provenance.json`) | placed, judgment pass, 309 of 309, 162 F / 147 B; 17 blocks arranged |
| Packer native DRC comparison vs seed | 3 `silk_over_copper` added (closed below) |
| Arrangement rules | no_stacking pass, thermal_spread pass; no_block_over_fixed 55 advisory findings (block members over fixed parts on the other side, including the fixed regulator capacitors and J1/U1; cross-side only) |
| Pad obligations (12 obligations, 26 pairs; `measure.py`) | **26 pass** (the fixed clusters carry iteration 5's values) |
| D-PCB-8 silk policy (`evidence/silk-policy-pass-*.json`) | two passes: 2 references hidden, 8 graphics to Fab, 3 references resized; `candidate-silk-policy.kicad_pcb.gz` |
| Native DRC, cited project, on the silk-policy board (`evidence/cited-rules-drc-silk-policy-board.json`) | **199 library findings only**: clearance 0, courtyard 0, hole 0, edge 0, drill 0 (D-PCB-1 vias), silk 0, text 0 |
| J3 (microSD, B) | (69.54, 18.84); TP2/TP5 at x ≥ 81 mm, clear of the card envelope (D-PCB-13) |

Compared with iteration 5 (cluster-anchored, released packer): same obligation result, 1673 s → 168.846 s,
the 44 drill findings gone, no stacking under the inductors, and the storage, AFE, ADC, CAN,
sensor-power, supervision and diagnostic groups now placed as rigid blocks.

Routing on the silk-policy board (planes + `kicad-route campaign`) is reported under
`../../routing-diagnostic/iteration-6/` when it completes. Open: independent review, routing,
then adoption.
