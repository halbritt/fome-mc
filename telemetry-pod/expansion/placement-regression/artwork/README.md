# Rejected placement: artwork follow-up

This diagnostic classifies the committed rejected placement's native DRC records. It does not change CAD, rules, or acceptance. Run `python3 classify.py` to regenerate classification.json from the parent directory’s retained native report (introduced in fome-mc commit 2a05f79).

All 13 solder-mask bridges involve PTH pads. Of 79 silk-over-copper findings, 63 involve reference fields; the other 16 involve PTH pads. Three reference-related cases also involve PTH pads, so these categories are not disjoint. All 25 silk-overlap findings involve reference fields. The 88 reference-related findings identify 31 unique component references.

Cross-side PTH reservation repair may remove PTH-related findings, but that is unproven until a new saved candidate receives full native DRC. Reference-field artwork needs its own evaluation after the final placement. Do not hide all references or suppress categories to obtain a pass. Preserve identifying marks on assembly layers and required board markings; assess readable silkscreen positions on both faces against actual exposed pads and other graphics.

Existing agent-ee silkscreen preparation at ca15c92 contains a narrow dense-passive policy, rather than a general reference label placement solver. This classification alone does not prove a defect in that policy. The next candidate must be checked for silk-over-copper, silk-overlap, and solder-mask bridges separately from electrical shorts, clearance, and courtyard checks.
