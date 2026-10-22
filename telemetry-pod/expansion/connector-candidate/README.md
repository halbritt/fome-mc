# AMPSEAL connector footprint candidate

This package replaces the erroneous panel-hole pattern in a project-local
footprint for TE **1-776163-1**. It captures the current manufacturer drawing,
776163 revision K1 (16 September 2024), and the exact-part revision T STEP model.
The shared ECU library and actual telemetry-pod project are unchanged. The
expanded native schematic must adopt this footprint after its generation gate
is released; a standalone footprint check does not qualify the complete pod.

## Sources and coordinate convention

`sources.json` binds the downloaded PDF and ZIP to their primary TE URLs and
SHA-256 digests. The STEP is extracted verbatim from that ZIP. Its internal
export date is 13 June 2023; it is the model currently linked by TE for this
exact part, not evidence that every later drawing change was incorporated.
The older J8 drawing remains in `../sources` as historical evidence.

The footprint origin is the center of the middle contact row. Viewed from the
component side, the connector mates toward +Y. Pin numbering follows the front
view and bent contacts on K1 sheet 1; sheet 2's board pattern is unnumbered.
The independent derivation is in `review/geometry.md` and `coordinates.json`.

| Feature | Footprint coordinates / dimension |
| --- | --- |
| Pins 1–12 | X = -22 to +22 in 4 mm steps; Y = -4 |
| Pins 13–23 | X = -20 to +20 in 4 mm steps; Y = 0 |
| Pins 24–35 | X = -22 to +22 in 4 mm steps; Y = +4 |
| 35 plated holes | 1.75 mm finished diameter; drawing tolerance ±0.10 mm |
| Two unplated board locators | (−28.5, +0.5), (+28.5, +0.5); diameter 2.85 mm ±0.08 |
| Recommended PCB edge | Y = +9.5 mm, for the drawing's 1.57 mm board |
| Reference overall flange width | 76.9 mm |

The four enclosure mounting screws are not PCB holes. In particular, 63.4 mm
is a screw-spacing dimension, not the total connector width. K1 also changes
the panel opening height maximum from J8's 24.7 mm to 25.2 mm; any enclosure
cutout must use K1 sheet 2 and its surface/tolerance requirements.

The 2.4 mm contact lands preserve the earlier land diameter and yield a nominal
0.325 mm radial annulus. Final fabrication capabilities must include finished
hole and registration tolerances. KiCad's nominal drill file does not encode or
prove those tolerances. No paste aperture is generated for these through holes.

The F.Fab rectangle uses drawing reference bounds X ±38.45, Y −6.05..31.85;
it is a conservative nominal projection, not a toleranced collision solid.
The courtyard adds a provisional 0.5 mm placement allowance. It does not include
the mating plug, harness bend radius, tools or enclosure access. The edge guide
is on Dwgs.User, never Edge.Cuts inside the footprint.

For a 90 × 65 mm board, placing this footprint at (45, 55.5), rotation 0,
aligns its guide with the board's Y=65 edge and leaves 6.55 mm nominal flange
width margin per side. The connector projects about 22.35 mm beyond that edge.
This illustrates an orientation that preserves the candidate board width; it
is not a placement solution for the other components or a cowl-fit claim.

## Verification and adoption

```sh
python3 prepare.py
/usr/bin/python3 verify.py
```

The verifier checks source hashes, exact ZIP extraction, generated footprint
reproduction, native KiCad pad loading against independently derived coordinates,
and the positions/counts/diameters in native Excellon output. Three negative
controls must reject a panel-hole diameter, wrong locator offset and reversed
contact placement. The temporary board is a connector-only 90 × 65 mm fixture.
This is not complete-board DRC, routing or manufacturing acceptance.

Before adoption: bind the exact connector to the expanded intent and verify all
board/enclosure clearances. Board thickness is owner-accepted as relayed by agent-509 (agent-drafted record, not owner-confirmed) as relayed by agent-509 (agent-drafted record, not owner-confirmed)
([decision, 2026-10-22](mating-interface/sources/owner-decision-2026-10-22-board-thickness.txt)): J1 fits by the owner's component-side through-hole rule (at least ±10%
of TE's recommended 1.57 mm, band 1.413–1.727 mm; the 1.6 mm board is inside,
AGENTEE-448), and the standard JLCPCB four-layer 1.6 mm board is accepted
(its published ±10% finished tolerance is a separate board-side fact, not
the J1 fit basis), and TE's 1.57 mm layout title
is not a thickness gate. The normal footprint, finished-hole/pad, retention and
solder-joint checks remain. Panel seal, screw selection/torque and installed cowl
clearance are verified once the team-designed enclosure exists. The prior
arbitrary 12 mm height limit is not reinstated.

## Model placement and native convention

Independent STEP sections locate two rear PCB support flats at raw Y=-11.72 mm.
The larger raw Y=-11.8 face belongs to the mating housing outside the PCB; using
it as the seating datum would shift the model by 0.08 mm. All 35 tail tips are
at raw Y=-15.22, giving 3.50 mm projection below the actual support flats.
The physical transform relative to the PCB top is `(X, -Z-31.8, Y+11.72)`.
KiCad stores the corresponding model rotation as **(-90, 0, 0)** degrees and
offset **(0, -31.8, 11.72)** mm; its stored rotation sign differs from the
mathematical positive X rotation. Native export caught and rejected the opposite
sign before adoption.

`check_model.py` independently reads the native exported STEP with CadQuery2.8.0.
It requires all35 tail axes to align with the fixture's drilled coordinates,
35 tip faces below two support flats, 3.50 mm projection, and the expected full
model envelope. The raw model's nominal projection is X±38.45, screenY−6..31.8,
and height −4.33..27.77 relative to its rear support plane. The slightly larger
Fab reference rectangle intentionally retains the drawing-derived bounds.

The KiCad10.0.7 fixture exports its board body at Z0..1.48 and the rear support
flats at Z1.565. That exporter datum includes its copper/nominal offset behavior;
it is not a physical stand-off specification. KiCad documents a0.05mm model
board offset in its [STEP exporter source](https://docs.kicad.org/doxygen/step__pcb__model_8cpp.html).
Do not silently subtract it from the source model or use the nominal exported
gap to certify mechanical seating. Board thickness is owner-accepted as relayed by agent-509 (agent-drafted record, not owner-confirmed) as relayed by agent-509 (agent-drafted record, not owner-confirmed)
([decision](mating-interface/sources/owner-decision-2026-10-22-board-thickness.txt)); physical seating, retention and solder joints are checked as
normal board-side checks. The model path assumes it is copied to
`${KIPRJMOD}/inputs/models/c-1-776163-1-t-3d.stp` during project generation.

Run both native drilling and exported-model checks with `bash verify-all.sh`.
This uses the system KiCad Python bindings and a separate pinned CadQuery2.8.0
environment; it creates no environment or lockfile in the project.
