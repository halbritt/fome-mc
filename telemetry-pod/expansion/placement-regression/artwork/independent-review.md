# Independent review

PASS for diagnostic classification of the rejected placement. Independently verified the source SHA and exact committed 2a05f79 DRC bytes, all 117 selected records/native indexes and description-derived classifications. Counts match: 13 mask bridges (all PTH); 79 silk-over-copper (63 reference-related, 19 PTH-related, including three in both categories); 25 silk overlaps (all reference-related). Thus 88 reference-related findings involve 31 unique references. The 16 non-reference silk-over-copper findings all involve PTH pads. Categories are not disjoint.

Read current silkscreen.py at ca15c923. Its dense-passive preparation is limited to exact 0402/0603 metric R/C/L identities, and it also has overhang artwork handling and dedicated IMU/assembly-mark reservations. It is not a general reference-placement solver. The README is appropriately bounded: item involvement does not establish cause, PTH repair is not promised to remove artwork defects, and references must not be globally hidden to manufacture a pass.

No source, CAD or rules changed. Artwork must be re-evaluated on a newly saved candidate after placement repair; the present packet establishes no acceptance.
