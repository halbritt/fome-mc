# Placement candidate, iteration 3 (independent review: proceed; fit for adoption review after routing; not adopted)

Iteration 2 plus the review's two should-fix items:

- **U14 (eMMC, BGA-153) is now a fixed part** at (72.5, 19.0) on B, under the ESP32 module
  body, offset so that none of U1's twelve thermal vias falls inside its courtyard. The
  module's courtyard is the only front-side copper over it, so its fan-out area is clear
  by construction; its five bypass capacitors C63–C67 sit 0.26–0.63 mm from its courtyard
  edge (group `u14-local-storage-bypass`). A front keep-out covers the strip of U14 below
  the module (x 65.75–79.25, y 20.4–26.0).
- **U3 at (71.5, 35.0) F, rotation 180** so its RF pad (77.5, 29.1) faces the J2 pin
  (86.96, 28.0) across 9.5 mm; **L3 (bias tee) is fixed in that corridor** at (80.6, 28.6),
  3.36 mm from the module's RF pad and 6.36 mm from the connector pin.

Everything else as iteration 2 (cross-side clearance, IMU isolation, inductor shadows,
J2 0.20 mm inboard). 44 fixed references, 9 obstacles. Two refusals preceded the run (the
keep-out 0.10 mm from U1's courtyard, inside the 0.25 mm reserved gap; moved to 0.40 mm).

## Independent review (`review/independent-review.md`)

No blocking or should-fix placement findings. Verified with the reviewer's own pcbnew code:
L3 pad 3.36 mm from the U3 RF pad and 0.92 mm off the straight line to J2, C42 behind it,
D3 0.26 mm from the line, RF net members U3/L3/D3/J2 only; U14 under U1 only, U1's thermal
PTH pads at least 1.145 mm outside U14's courtyard (hole edge to ball copper >= 5.17 mm);
the full checklist (331 parts, overhangs, same-side gaps, 33 pairs, anchors, IMU distances,
J2 0.50 mm edge) and the cited-rules DRC identical item-for-item to
`evidence/cited-rules-drc-committed-board.json`. Fit for adoption review after routing,
conditional on: the D-PCB-1 patched thermal-via footprints on the routed board, D-PCB-3
(eMMC fan-out) decided and shown to route, the GNSS line routed over an unbroken In1 GND
with L3/D3 tapped at the line and no In2 traces under it (D-PCB-6 keep-out), and silk
relocation (AGENTEE-320). Reviewer notes: eMMC CLK/CMD/DAT0-3 straight lengths 7.7-17.8 mm
(4-bit mode, DAT4-7/DS are U14-only nets); nine B parts sit 0.26 mm from U14's courtyard,
so a 1.5 mm B-side moat is the first lever if BGA escape stalls.

## Checks on the candidate (board SHA256 `fc28ba79…a3660e`)

| Check | Result |
| --- | --- |
| Packer (`evidence/placement-*.json`) | placed, 866 s, 16 511 steps, 2 backjumps, judgment pass, groups pass, 331 of 331, 162 F / 169 B |
| Pad obligations rev 2 (`measure.py`) | 33 pass, 0 exceed, 0 unknown |
| Native DRC, **cited project on the committed board** (`evidence/cited-rules-drc-committed-board.json`) | 329: 44 drill (unpatched 0.20 mm thermal vias of the migration footprints), 199 library, 86 silk/text; **clearance 0, courtyard 0, hole 0, copper-edge 0** |
| Same on a copy with 0.30/0.70 mm thermal vias (`…-via-patched-copy.json`) | 257: 199 library, 58 silk; 0 drill |
| IMU courtyard distances, exact polygons (L1/L2/L4/U5/U7/U15/U26) | 14.56 / 21.81 / 42.02 / 11.54 / 23.73 / 39.12 / 6.81 mm |
| Through-board courtyard intersections with L1, L2, L4 | none |
| Front parts over U14 | U1 only (113.9 mm², by design) |
| Routing readiness (`evidence/blocked-by.json`, heuristic) | 489 of 499 unobstructed |

Parts whose courtyards intersect a 3 mm band between the U3 RF pad and the J2 pin: L3 (F,
the bias tee, intended) and C75, U18, R181, U9 on B, behind the two inner planes.
Open: silkscreen (AGENTEE-320), thermal-via patch at the next migration (D-PCB-1), eMMC
interior fan-out detail (D-PCB-3), planes (D-PCB-5) and routing, then review and adoption.
