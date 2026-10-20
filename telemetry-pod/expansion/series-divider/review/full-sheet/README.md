# Expanded schematic visual review: findings open

Both parent and independent reviewer inspected all eight retained regions of the
occupied A0 sheet. `review.json` pins the exact schematic, emitter candidate,
gzip-compressed native SVG, crop bounds and raster evidence. Native graph checks and ERC
still pass; they do not detect these presentation defects.

- **VIS-1:** R18 and R128/R129/R140/R144 have vertical net labels superimposed
  on reference/value fields. See `top-middle.png` and `diagnostics.png`.
- **VIS-2:** TP1–TP6 have overlapping net labels and displayed fields. See
  `top-left.png` and `middle-left.png`.
- **VIS-3:** eMMC group titles still say “supplies pending” and “supervisor
  pending.” These circuits exist; the remaining condition is qualification.

No omitted groups or sheet-edge clipping were observed. Crop boundaries are
not sheet boundaries. U31's crowded REF/K/reference presentation also needs
reinspection when the field-placement issue is corrected.

To reproduce, export SVG with KiCad10.0.7 from the pinned native schematic on a
scratch copy. Set each region SVG root's width/height and viewBox to the recorded
millimetre bounds, then render with `rsvg-convert -w 2600`. The retained `telemetry-pod.svgz` (gzip)
preserves the exact review source; generated timestamps can vary on replay.

Do not hand-edit the accepted netlist or captured library geometry to conceal
these defects. Repair the presentation producer, regenerate a separate candidate,
verify unchanged complete connectivity/bindings/NC/BOM/ERC, and repeat visual
review. Update the two group titles as an explicit presentation-input change.
Visual acceptance and overall hardware acceptance remain open.
