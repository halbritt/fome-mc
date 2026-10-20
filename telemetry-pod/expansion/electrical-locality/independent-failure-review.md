# Independent combined-group failure review

Confirmed packing_search_exhausted/outcome unknown at C66, 7039 steps, six backjumps, placed_peak four. Source placer.py stops on exhausted finite candidates or repeated backjump orders; neither proves continuous geometric infeasibility. The peak counts movable placed parts, not the eight fixed anchors.

Capture dimensions: U14 courtyard 13.5 x 15 mm; C63/C65/C67 2.96 x 1.46 mm; C64/C66 3.4 x 1.96 mm, all B-side. The 8 mm origin radius is intrinsically tight. Beside unrotated U14's short-axis edge, a rotated 0805 needs center X at least 6.75+0.25+0.98=7.98 mm, leaving only 0.565 mm Y offset within the disk. A 0603 needs 7.73 mm, allowing approximately 2.061 mm Y offset. Above/below the long edge, even a narrow 0603 needs 7.5+0.25+0.73=8.48 mm. These are necessary rectangle conditions, not a completed packing proof.

Smallest next diagnostic: isolate U14 plus its five capacitors, fix an abstract anchor, enumerate allowed quarter-turn courtyard orientations, and derive exact feasible center intervals within the unchanged 8 mm disk and 0.25 mm gap. Check pairwise occupancy with exhaustive local geometry. Initially omit external obstacles to test the group itself. If a legal witness exists, independently verify it and then test against actual fixed/PTH obstacles. This distinguishes internal group geometry, external obstacles and greedy ordering without another full-board run or constraint relaxation. Heuristic failure remains unknown; an impossibility claim requires a complete exact argument.

No packing, board edits, radius changes or adoption performed.

## Completed local-policy proof review

Independently verified all six native courtyards are axis-aligned rectangles centered at their footprint origins with the stated dimensions and B-side ownership. Quarter-turning U14 merely exchanges axes. Horizontal cap orientations cannot clear either U14 axis inside radius8; vertical orientations can only occupy the left/right strips. Their Y bounds are0.565332mm for0805 and2.060849mm for0603. Same-side horizontal center separation is at most0.27mm, insufficient even for nonoverlap, so cap pairs must separate inY. Two large caps need3.65mm Y separation but can achieve at most1.130664mm; hence they require opposite sides. A large and small need3.43mm but can achieve at most2.626181mm. Each large therefore excludes every small on its side. Since two large occupy both sides, the five-cap group cannot satisfy this exact8mm origin-radius/.25mm gap/quarter-turn/same-side rectangular policy. The inequalities have substantial margin and do not depend on finite greedy search or board dimensions.

This establishes local policy impossibility only, not electrical infeasibility, board-size infeasibility or authority to change the engineering radius. A revised group must be explicitly proposed and independently checked; no new packing was performed.

## Proposed9mm local witness

Verified independent coordinate rotations from the captured, origin-centered native courtyards against placer.transform/boxes and every retained pairwise separation. All15pairs have separating-axis gap at least0.25mm; large-small same-side gaps are0.32mm. Largest capacitor-origin distance is8.485452mm, below proposed9mm. This is a constructive isolated-group witness, so9mm removes the demonstrated internal8mm policy contradiction.

Terminology boundary: native-extracted footprint geometry is transformed mathematically here; no KiCad saved six-part board or nativeDRC was produced by local-witness.py. It is not a native writer roundtrip, full-board placement, routing or electrical acceptance. Correcting this explicitly engineer-selected radius8→9 is a defensible next diagnostic proposal with all other gaps/rules unchanged. Actual fixed/PTH obstacles, decoupling pin/return loops and saved-board checks remain mandatory. No packing was launched by this review.
