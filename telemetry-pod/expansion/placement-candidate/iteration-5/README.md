# Placement candidate, iteration 5 (microSD source; independent review: conditional proceed; not adopted)

First placement of the pod after the owner dropped the eMMC (2026-10-21,
`../../storage-microsd/`). Base seed: `../../placement-seed-microsd/base-seed.kicad_pcb.gz`
(forward-annotated, side-assigned). Method as iteration 3 (cluster-anchored on the released
packer) with these changes:

- no U14 fixed part, no U15 cluster (the storage core buck is gone), no BGA fan-out keep-out;
  38 fixed references, 7 obstacles (IMU exclusion and ring, L1/L2 shadows), 6 groups
  including `j3-microsd-local` (R46–R50, R55, C64, C65 within 12 mm of J3);
- released agent-ee main `f92d71c` packer source (`inputs/source-hashes.txt`);
- **D-PCB-8 silk policy pre-applied to the seed** (`inputs/silk-prepass.json`: 12 more references
  hidden and 13 footprint silk graphics moved to Fab on top of the base seed, which already
  carried 270 hidden references from the migration; the candidate shows 27 references). The first run on the unmodified seed
  (`evidence/iteration-5-silk-gate-refusal/`) planned the same 309 placements in 27,102
  steps, then the released saved-board silk gate refused it with 12 `silk_overlap` + 16
  `silk_over_copper` after its own relocation; two passes of the policy on that board
  cleared them, and this re-run on the pre-treated seed reproduces the placement exactly
  (309 of 309 poses identical) with the gate passing.

## Checks on the candidate (board SHA256 `5bf9e33d…a19648`)

| Check | Result |
| --- | --- |
| Packer (`evidence/placement-*.json`, `packer-execution.json`) | placed, 1673 s, 2 backjumps, judgment pass, 309 of 309, 162 F / 147 B |
| Packer native DRC comparison vs seed | no added findings (the packer's own run carries 18 pre-existing intra-footprint pad-clearance findings at its default 0.20 mm on U2/U16/U18/U19, absent under the cited rules) |
| Pad obligations rev 3 (12 obligations, 26 pairs; `measure.py`, pad centres) | 26 pass, max 8.12 mm (advisory bounds) |
| Native DRC, cited project on the committed board (`evidence/cited-rules-drc-committed-board.json`) | 44 drill (unpatched 0.20 mm thermal vias of the seed's migration footprints, D-PCB-1 pending at the next seed), 199 library, 2 text height + 2 thickness (U16/U19 references at 0.8/0.12 mm; resizing them to 1.0/0.15 clears both, `…-silk-gate-refusal/cited-drc-after-policy-and-text-fix.json`); **clearance 0, courtyard 0, hole 0, edge 0, silk 0** |
| J3 (microSD, B) | (74.46, 19.77) mm, rotation 180: the card slot faces +y into the board interior, not a wall; the card path on B is clear of body-height parts; pull-ups and bypass 8.85–11.99 mm from J3 |

Routing on this placement (planes + `kicad-route campaign`) is reported under
`../../routing-diagnostic/iteration-5/` when it completes.

## Independent review (`review/independent-review.md`)

**Conditional proceed**; every numeric claim above reproduced with the reviewer's own pcbnew
code; 0 same-side overlaps, 0 gaps under 0.25 mm (364 pairs at 0.26–0.30 mm), 0 through-board
stacking with L1/L2/U2, GNSS corridor unchanged from iteration 3, `kicad-route blocked` 489 of
499 unobstructed (the 10 blocked sit against the fixed J1/U12/U6/U5). Conditions before
adoption: (1) test points TP2/TP5 have copper 0.06 mm from the seated card's edge, so a pogo
fixture collides with an inserted card: move them about 1.5 mm at the next seed (add the card
envelope on B as a packer obstacle) or document programming with no card inserted; (2) resize
or hide the U16/U19 reference texts; (3) keep the In1 GND strip under the GNSS corridor
unbroken in plane planning (J3's shield tabs and TP2 now sit under it on B). Bookkeeping: the
declared overhang limits equal the courtyard centreline and the stroked courtyard exceeds
them by 0.045 mm on J1/U1.

Open: the review conditions above; D-PCB-1 thermal-via footprints at the
next migration; enclosure fit of J3; planes and routing; then adoption.
