# Verification of 216eb9a (FOMEMC-10 routing) against its parent 6af7bf4

Independent check, 2026-10-17, KiCad 10.0.7 `kicad-cli`, same grading as `route.py`:
snapshot of each commit, zones refilled, JSON DRC with `--severity-all
--schematic-parity`, and the `route.py` preservation checks of 216eb9a against 6af7bf4.
Reproduce with `verify_routing.py 6af7bf4 216eb9a` (raw numbers in `verify.json`).

## Claim: routing complete, DRC closed

| | 6af7bf4 (parent) | 216eb9a, its own rules | 216eb9a, parent's rules |
|---|---|---|---|
| Unconnected items | 322 | **0** | 0 |
| DRC errors | 0 | **0** | 0 |
| Schematic parity issues | 0 | **0** | 0 |
| Warnings | 484 | 471 | 495 |
| `starved_thermal` | 27 | 0 | **24** |
| `lib_footprint_mismatch` / silk | 199 / 256 | 199 / 272 | 199 / 272 |
| DRC exclusions | 0 | 0 | 0 |

Connectivity and the error-severity rules hold: every net is connected and no
clearance, width, hole or short rule fails. The claim holds in that sense.

## What else changed (not a pure routing change)

- **Rule relaxed:** `.kicad_pro` `min_resolved_spokes` 2 -> 1. That is the only rule
  change, and it hides the 24 `starved_thermal` warnings (GND pads of C7, C40, C67, C68,
  C96, C99, C100, C109, R48, R63, R71, R94, U26 pads 48/51/120, ...). Ignored severities
  are unchanged and no exclusions were added.
- **Narrow conductors:** 1646 of 6846 new tracks are below the net-class width (0.254 mm,
  Default): 1550 at 0.127 mm (the board minimum), about 1.19 m in total, spread over
  signal nets (`/ETB1_PWM`, `/ign1/IN4`, `/ign2/IN3`, `/mcu/VBOOST_DIVIDED`, SD lines) and
  32 segments on `+3V3`. KiCad DRC accepts them (`min_track_width` 0.127); the net class
  says 0.254.
- **Placement moved:** 15 placed footprints relocated (C203-C206, R127-R132, R211,
  R213-R216; for example R127 from (158, 91.5) to (61, 128.5) mm).
- **Zones / keepouts:** the `+3V3` In2.Cu zone outline was redrawn; one new F.Cu no-fill
  rule area (100.65-102.05 x 125.6-127.1 mm).
- **Existing copper:** 1016 tracks and 88 vias of the parent removed or rerouted (none
  were locked), 6842 tracks and 820 vias added (13.3 m).
- Nets, net classes, pad-to-net assignments, outline, layers and board setup unchanged.
