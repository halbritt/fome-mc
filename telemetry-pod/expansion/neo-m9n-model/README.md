# NEO-M9N-00B visualization model

This package makes the existing iter8t U3 model reproducible and durable. It does
not change a schematic, footprint, PCB, rule or placement. The STEP and both
authoring scripts are copied byte-for-byte from the agent-449 iter8t delivery.
No official downloadable u-blox STEP was located in the bounded source search;
this asset is an explicitly **datasheet-derived visualization, not manufacturer
CAD or mechanical qualification**.

## Source and approximations

The retained original is u-blox `NEO-M9N-00B_DataSheet_UBX-19014285.pdf`, R08,
09-Oct-2025, section 6, Figure 5 and Table 20, pp. 16–17. `provenance.json`
records its official URL and SHA-256. The model uses nominal body dimensions
16.0 × 12.2 × 2.4 mm, substrate thickness 0.82 mm, and nominal contact dimensions
0.8 × 0.9 mm. Published body maxima are 16.1 × 12.3 × 2.6 mm. Residual tabs may
project up to 0.5 mm on either short side, not both; their exact shape is variable.

The nominal model is not a maximum-tolerance collision solid. Its full-width
shield, box-shaped castellations, pin-1 dot and colors are visual approximations.
The contact boxes extend 0.01 mm below the nominal mounting plane and beyond the
nominal body; the dot adds 0.05 mm above it. These are visibility embellishments,
not manufacturer dimensions. Two translucent red tab strips indicate possible
locations, not two physical tabs or a qualified keep-out. Transparency may be
rendered differently by different viewers. Do not use the overall STEP bounding
box as a dimensional requirement. No enclosure or harness CAD is required for
this bare-board visualization; those are being designed separately.

## Coordinate and candidate evidence

Model units are mm. X follows footprint X; model Y is opposite KiCad's screen Y.
Zero model rotation/offset and unit scale place it on `RF_GPS:ublox_NEO`.
`evidence/native-pose.json` binds the reviewed iter8t board by SHA-256: U3 on
F.Cu at (71.5,35) mm, 180 degrees; board thickness is the standard 1.6 mm.
The 24 world pad centers were read from that exact board with native pcbnew.

`evidence/native-u3.step` is a fresh native KiCad 10.0.7 export of U3 alone,
without the board body. `verify.py` independently reads both STEP artifacts with
CadQuery 2.8.0, verifies all 29 solids, the nominal core, every pad/contact
alignment, the full placement transform and the pin-1 corner. The generated
model must reproduce byte-for-byte. The native mounting Z=1.6012 mm is an
exporter datum, not a physical solder stand-off specification.

`evidence/native-u3-closeup.png` is a fresh native render of the same unchanged
board, visually inspected: U3 is visible with its shield, contacts and pin-1 cue
next to the SMA and AMPSEAL. Background board geometry is historical iter8t,
not proof of current routing or release readiness.

## Reproduce and integrate

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python 3.12 --with cadquery==2.8.0 \
  python -B telemetry-pod/expansion/neo-m9n-model/verify.py
```

`evidence/commands.json` records native export/render arguments against the
hash-bound source board. No ERC/DRC rerun is claimed: this addition changes only
a standalone visual-asset package, and exports do not alter the candidate.

Agent-449 is the integrator. Copy the long-named STEP into the target candidate's
`inputs/models/` and retain its provenance/classification in `project-models.json`.
Bind U3 to `${KIPRJMOD}/inputs/models/<same STEP filename>` with zero transform,
then recapture model inventory and publish fresh candidate-bound renders. Never
carry this historical candidate's acceptance or placement receipt to a different
board hash. Apply the model to later candidates through their normal derivation
pipeline; do not replay the complete old iter8t board.
