# Independent AMPSEAL geometry review

Both pages of retained J8 and newly captured current TE drawing776163 revisionK1 were rendered and visually inspected. The current TE endpoint was also opened independently; its revision block identifies K1,16SEP2024. Parent subsequently captured the PDF and exact-part STEP archive, so the earlier current-source-unavailable hold is withdrawn. This report does not claim native PCB acceptance or physical fit.

Source URL: https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=776163&DocType=Customer+Drawing&PartCntxt=1-776163-1

## Dimensions directly shown

K1 sheet2, upper-right recommended P.C. board layout, for1.57mm board:

-35 signal holes, finished after plating Ø1.75±0.10mm. Position tolerance Ø0.1 at RFS relative to datumA at RFS.
-Three rows,4mm apart;4mm pitch within each row; middle row shifted2mm. Outer rows contain12 holes each, middle11.
-Two locator holes Ø2.85±0.08mm,57mm center spacing. Left locator defines datumA; right locator position Ø0.1 at RFS relative toA.
-Left locator to first outer-row hole6.5mm horizontal offset.
-Locator centerline is0.5mm toward the dashed board-edge line from the middle row. Dashed edge is9mm beyond the locator centerline. It is a recommended edge reference, not a requirement to embed an Edge.Cuts segment into a reusable footprint.

K1 sheet2 upper-left is an entirely separate panel layout: four mounting holesØ3.00–3.30mm, top horizontal span63.4mm, bottom66.4mm, vertical18.1mm. These are not PCB locators. Panel opening is60.0–60.5mm wide and24.2–25.2mm high, corner radius6.60–6.80mm. J8 showed24.2–24.7mm height; do not carry its obsolete maximum into enclosure design.

K1 sheet1 front view: overall flange width(76.9), overall height(32.1), mating housing width(59.4), reference dimensions in parentheses.63.4mm is a screw-hole spacing, not total body width. The black gold-plated exact part is1-776163-1; black tin-plated is776163-1. Identical nominal board pattern does not interchange finish/BOM identity.

## Proposed coordinate convention and numbering

Choose middle-row center pad18 as(0,0),+X to the right in a component-side PCB view,+Y toward the connector's mating face and board edge. Front-face numbering on sheet1 and the bent-contact paths in sectionA-A support the following component-side mapping. The sheet2 PCB diagram itself has no pin numbers, so this mapping is a derived transform, not a directly printed numbering table.

| Pins | X coordinates | Y |
|---|---|---:|
|1–12|−22,−18,…,+22|−4|
|13–23|−20,−16,…,+20|0|
|24–35|−22,−18,…,+22|+4|
|Two locators|−28.5,+28.5|+0.5|
|Recommended mating-side board edge|line parallel toX|+9.5|

The upper row of the mating face (pins1–12) bends to the tail row farthest behind the panel; lower face row24–35 bends to the nearest row. Looking at the mating face from outside with its top up, numbering increases left-to-right. With mating side+Y in the component-side view, this produces the table above. Rotating a footprint180° must rotate pads, locators, edge and body together; do not separately mirror pin labels. This convention agrees with the existing signal-pad numbering, but not its locator geometry.

`coordinates.json` contains all35 proposed coordinates and the datum values. Copper diameter is a separate fabrication choice: the existing2.4mm pad diameter gives0.325mm nominal radial annulus with a1.75mm drill, or0.275mm at a1.85mm finished-hole diameter before registration allowances. TE does not prescribe2.4mm copper here. Preserve fabrication/drill tolerance and solderability checks.

## Existing footprint defects and body association

Inspected `/home/halbritt/git/fome-mc/libs/footprints/ampseal.pretty/ampseal-35.kicad_mod`:

- Four Ø2mm NPTHs at(±31.7,−10.8)/(±33.2,+7.3) reproduce panel-hole spacing in the board plane. Remove these from the PCB footprint and replace with the two correct locator holes above. They are neither the right hole count nor diameter nor location for PCB seating.
- Its Fab rectanglex±36,y−12.5..+10 is not the drawing's complete body envelope. Width72mm is smaller than reference flange76.9mm, and the rectangle projects onto the wrong portion of the mating-side overhang.
- The35 existing pad coordinates match the proposed convention; no evidence here calls for renumbering those pads merely to fix the locators.

Tentative drawing-to-body datum association in this convention: sectionA-A middle tail is9.8mm behind the rear flange surface, locating that surface atY=+9.8. The2.0mm flange thickness gives its mating face+11.8; the0.75mm gasket reference moves to+12.55. The19.3/18.6mm reference extents then imply a nominal full envelopeY=−6.05..+31.85 andX=±38.45. This chain depends on correctly associating those extension lines and is explicitly an inference to compare with the exact-part STEP. The STEP transform, seating plane, modeled locator axes, pin1 correspondence and actual clearance envelope still require independent numerical/native verification. These reference dimensions are not worst-case mechanical tolerances.

Do not restore a12mm height acceptance criterion: that earlier limit was agent-drafted and the owner withdrew it. The drawing's32.1mm flange height is a real envelope consideration, but its location relative to PCB seating and the enclosure still needs model/physical confirmation. A connector may overhang the PCB;76.9mm body width does not by itself mandate76.9mm PCB width. PCB outline, enclosure panel, screws, cable exit and mating/service clearance must be resolved together.

## Remaining acceptance

Current-source capture is now available. Compare exact captured STEP geometry with the K1 drawing and the authored footprint, establish its rotation/translation and seating plane, then check native pads, drills and board edge. Archive capture hashes, native render/DRC evidence and connector-specific assembly/clearance results. The STEP archive member is dated2023 whereas K1 drawing is2024; do not assume every enclosure detail is synchronized without comparison. No repository files were modified by this review.

## Independent STEP follow-up: seating correction

The exact captured STEP was independently imported using CadQuery2.8.0 in an isolated `uv run --no-project --python3.12 --with cadquery` execution. See `check_step.py`, `step-independent.json`, `section_step.py` and `boardlock-sections.json`.

The model contains one solid. Raw bounds areX±38.45,Y±16.05,Z−37.8..0. All35 radius0.65mm tail axes were extracted independently and exactly match these rawX,Z locations:

- Z−35.8:X−22..22 at4mm pitch (12 tails).
- Z−31.8:X−20..20 at4mm pitch (11 tails).
- Z−27.8:X−22..22 at4mm pitch (12 tails).

All35 tip faces are at rawY−15.22. This confirms the proposed screen-plane mapping `(x,y)=(X,Z+31.8)` and the footprint hole-row pattern. The STEP geometry has no pin labels; electrical numbering still comes from the drawing's front view and section, not cylinder extraction alone.

**Reject the original seating argument based on the916.5mm² plane at rawY−11.8.** Its rawZ extent is−20..−0.5, corresponding to screenY11.8..31.3, entirely outside the board edgeY9.5. It is the mating-housing underside, not a PCB support surface.

Two rear support flats are instead at rawY−11.72, each6.5mm², spanning rawX24.47..25.77 and its mirror, rawZ−37.8..−32.8. These are within the PCB region and give exactly3.50mm tail projection to−15.22, consistent with the drawing's3.0–4.0mm reference. They provide stronger model evidence for the seating datum.

Recommended corrected Cartesian model transform:

`physical (x,y,z)=(X,-Z-31.8,Y+11.72)`.

That is a proper+90° rotation aboutX followed by translation(0,−31.8,+11.72), not a reflection. ScreenY is the negative of physicalY. Independent transformed bounds areX±38.45,physicalY−31.8..6.0,Z−4.33..27.77. The drawing-inferredY bounds−6.05..31.85 differ by0.05mm from the nominal STEP projection−6..31.8; use model-derived nominal geometry while retaining dimension/tolerance checks. Parts of the flange extend below the PCB seating plane outside the board edge.

The two board-lock shafts were independently sectioned at rawY−11.72,−12,−13 and−13.29. Their shapes fit around drawing hole centers raw(X,Z)=(±28.5,−31.3), corresponding to screen(±28.5,+0.5). Sampled cross-section radial extent from those centers is at most1.299231mm, below even minimum hole radius1.385mm. The cylinders used to construct these asymmetric/truncated shafts have axesX±28.9; that is not a reason to move the hole centers. The snap-latch flare starts at rawY−13.5,0.21mm below a1.57mm board seated at−11.72, with radial extent about1.90mm. This is consistent with a compliant snap lock; it does not establish insertion force, tolerance-stack fit or retention strength.

Accept the corrected transform as a model-placement candidate. Native KiCad model rotation/offset interpretation, pin1 orientation and actual rendered seating must still be checked before attachment is considered verified. Physical board-thickness tolerance, model/drawing synchronization, mating enclosure, fabrication and hardware acceptance remain open.
