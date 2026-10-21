# Independent review: placement candidate iteration 7 (silk-policy board 2c1ac944…54a1, packer board 35f242c8…cba9)

Reviewer: independent review worker, 2026-10-21. Packet:
`/home/halbritt/git/fome-mc/telemetry-pod/expansion/placement-candidate/iteration-7/` at fome-mc
`4ddaf35`. Both boards and the seed gunzipped to
`/tmp/claude-1000/-home-halbritt-git-agent-ee/27167fc2-dedb-47b5-9a97-e1d328bdac8d/scratchpad/iter7/boards/`
(packer `35f242c804038b7ec48740e6f894339e1c152fea95e6a15ddfe77b402030cba9` = README and
`placement-result.json` `board_sha256`; seed `21bbf8ef…ffa6cc` = `placement-result.json`
`source_sha256` and `inputs/input-hashes.txt`; silk-policy `2c1ac944…54a1`; all 46 lines of
`SHA256SUMS` verify). All geometry is my own pcbnew 10.0.7 + shapely code
(`…/scratchpad/iter7/scripts/check7.py`, `j3.py`, `/usr/bin/python3 -B`); DRC via `kicad-cli pcb drc
--severity-all --all-track-errors --schematic-parity` on a same-stem copy beside
`design-rules/board-setup.kicad_pro` (`7c7933bf…`) + `telemetry-pod.kicad_dru` (`ff622083…`)
(`…/scratchpad/iter7/drc/drc.json`); router pre-check via `kicad-route blocked --board`
(`…/scratchpad/iter7/route/`). Nothing under `~/git` was modified.

## Verdict

**Conditional proceed to routing.** The iteration-6 blocker is closed: J3 now sits at the
bottom-left of the board, (9.12, 44.25) rot 0 on B, slot opening toward −y into the board interior,
and the seated card, the full 15 mm insertion/ejection lane and a further 15 mm beyond the lane end
up to the top edge are empty on B; no through-hole pad of any F part is under the J3 courtyard, the
seated card or the lane; the nearest mounting hole (H1) is 9.9 mm from the lane and H4 is 6.3 mm
from the J3 courtyard. Everything the iteration-6 review verified (counts, overhangs, 0.25 mm gaps,
L1/L2 and IMU isolation, obstacles, 26/26 obligations, 17 rigid blocks, GNSS corridor, cited-rules
DRC, silk policy) reproduces.

The condition is a regression the README does not mention: to clear the lane the placer did not
nudge the `adc` block, it moved **ten of the seventeen blocks (140 footprints)**, and the `storage`
block went from under U1 to the opposite corner. J3's contact row is now **73.9–88.3 mm** from U1's
seven SDMMC pins (iteration 6: 1.9–15.4 mm); the SD nets carry 10 k pull-ups at the socket end and no
series termination, and their straight-line paths cross the power entry (Q1, D1), J1's pin field,
and the analog blocks (U4 `adc`, U13 `aux-afe`). This is routable on a 4-layer board with a solid
In1 GND and will work at the SDMMC default 20 MHz, but it costs the 40 MHz high-speed margin, is
exactly the opposite of the "storage under U1 by design" rationale that exempts the block from
`no_block_over_fixed`, and was never decided. Conditions, in order of weight:

1. (Should-fix 1, condition for adoption, not for routing) Decide the SDMMC bus length: either
   record the 74–88 mm bus as accepted with an SD routing constraint (one layer over In1 GND, the
   seven nets routed as a group with CLK matched to the data lines to a stated tolerance, no crossing
   of the `adc`/`aux-afe` courtyards, SDMMC clock capped at 20 MHz until measured), or re-place the
   `storage` block within reach of U1 with the lane pointed into free area (the lane is 15.7 × 15.3
   mm; the top-right B region under U1 at x 48–78, y 0–20 where `adc`/`supervision` now sit is one
   candidate). The routing diagnostic on this board is still useful either way, so routing may start.
2. (Should-fix 2) State in the README that iteration 7 is a different arrangement from iteration 6
   (10 blocks moved, storage relocated), not "everything else as iteration 6"; the inputs are the
   same, the output is not.
3. (Carried, unchanged or slightly worse) THT soldering access around J1: the same eleven
   `afe`/`thermistor` members on B under J1, with R22 0.274 mm from the right boardlock NPTH (was
   0.304), JP5 0.339 and JP3 0.384 mm from pins 3/4 (unchanged), plus a new one: `storage` pull-up
   R50 is 0.309 mm from the left boardlock NPTH at (16.5, 56). U6/U12 are still 0.26 mm apart. Both
   should-fixes from iteration 6 remain open; the README says so.

## Blocking findings

None. The microSD card path is clear (details in Verified claims and Notes 1).

## Should-fix

1. **SDMMC bus length and path (new, undisclosed).** J3's contact row is at y = 51.975, x 3.2–11.9
   (pads 1–9, B); U1's SD pins are at x 76.9–81.25, y 7.6–19.0 (F). Pad-centre spans:
   /SD_DAT3 73.91, /SD_DAT2 82.34, /SD_CMD 82.26, /SD_CLK 83.57, /SD_CD 85.70, /SD_DAT0 86.72,
   /SD_DAT1 88.30 mm. Iteration 6: 1.86–15.43 mm. Net members are exactly U1 pin, J3 pad and one
   10 k pull-up (R46–R50, R55; CLK has none); no series resistor. The straight lines cross courtyards
   of D1 (SMCJ24CA), Q1 (DMP6023LE), R111/R175 (2512), J1, U25, U13 (ADA4096-4, `aux-afe`) and U4
   (MCP3208, `adc`). The pull-ups and bypasses are correctly at the socket end: R46–R50/R55 2.0–4.3 mm
   from their J3 pad by same-net pad, C64 2.39 mm and C65 4.29 mm from J3 pin 4 (+3V3), all B, all
   0.26–2.47 mm from the J3 courtyard. The pull-ups R46/R47/R48/R55 sit in a row at y = 54.8 along
   the bottom edge between J3 and H4 (R48 at (4.0, 54.8) is 3.8 mm from H4's hole edge; an M3 head
   or 6 mm standoff clears it by ~2.4 mm).
2. **README scope.** "Iteration 6 re-packed … with one change" describes the inputs. The output
   moved `afe` (0.03 mm), `adc` ((50.06, 11.45) → (72.60, 21.46)), `can` (0.53 mm), `aux-afe`
   ((26.9, 28.1) → (59.5, 20.1)), `storage` ((69.54, 18.84) rot 90 → (9.12, 44.25) rot 0),
   `supervision` ((47.2, 32.4) → (61.3, 8.3)), `sensor-power-front/rear/tire` and `wheel-input`
   (3.2 mm); `power-entry`, `supplies-5v`, `mcu`, `tire-can`, `diagnostic`, `aux-power`,
   `thermistor` are at their iteration-6 poses. The `no_block_over_fixed` census changed
   accordingly: 50 = U3 22, U1 16, J1 11, R4 1 (iteration 6: 55 = U3 17, J1 11, C15 6, U7 5, C9 4,
   C10 4, C14 4, R5 2, R4 1, C8 1); U1 now has `adc` (U4, C40, R15 …) and `supervision` (U18, U19 …)
   under it in place of `storage`. U1's 12 through-hole (thermal-via) pads are all ≥ 0.5 mm from
   every B courtyard; the only through-hole conflicts anywhere on the board are J1's (item 3).
3. **Carried: J1 THT access.** Members under J1 on B: C34, C36, C39, JP3, JP4, JP5, R19, R20,
   R22, R23, U8 (same eleven as iteration 6). Opposite-side courtyard vs through-hole copper
   < 0.5 mm: R22 0.274 (right boardlock NPTH, 2.85 mm), R50 0.309 (left boardlock NPTH), JP5 0.339
   (pin 3 /POD_12V_IN), JP3 0.384 (pin 4 /GND). The AMPSEAL boardlock pegs press into those NPTH
   holes from F; R50 (new) and R22 sit against the hole edge on B. Verdict: slightly worse (one more
   part, one closer). Still needs the fabricator disposition or a B-side keep-out around J1's pins
   and pegs.
4. **Carried: U6/U12.** Courtyard gap 0.26 mm (unchanged); `supplies-5v` did not move.
   U5–U7 9.61 mm courtyard / 16.55 mm centre (thermal_spread pass on the centre metric). U7–U12
   6.30 mm.
5. **Packet bookkeeping (as iteration 6).** `placement-result.json` `verdict: defect` / `outcome:
   defect` (the 3 `silk_over_copper` on U20's reference over U22's pads) while the README says
   "judgment pass" (judgment pass, candidate defect; both true, the silk policy closes it).
   `evidence/cited-rules-drc-silk-policy-board.json` was again produced on `ca2.kicad_pcb` (pass-1
   on `ca.kicad_pcb`), not under the project stem; result identical to mine. `obligations-measured.json`
   `board_sha256: null` again.

## Notes (no action for placement)

1. **The microSD card path.** J3 (Hirose DM3AT-SF-PEJM5, D-PCB-13 v2 footprint: courtyard
   −7.82…7.88 × −8.82…29.0 local) at (9.12, 44.25) rot 0, B. Board courtyard x 1.305–16.995,
   y 15.255–53.065 (15.69 × 37.81 mm, 593 mm²). Contacts (pads 1–9) are the row at y = 51.975; the
   shell drawn on B.Fab spans x 2.145–16.095, y 36.075–52.125; the seated card is drawn to its tip at
   y = 30.525 over x 3.195–14.195 (11.0 mm wide). The card therefore slides along −y to enter, i.e.
   from the board interior toward the socket at the bottom-left; the 15 mm travel lane is
   x 3.2–14.2, y 15.5–30.5 and the courtyard covers it to y 15.255 (0.27 mm margin).
   Census on B (courtyards): seated region 0 parts, 15 mm lane 0, courtyard-width lane 0, 5 mm
   beyond the lane end 0, and the whole strip from the lane end to the top edge (y 0–15.5) 0. The
   nearest B parts to the card path are the storage passives at 7.8 mm (C64, R46–R48, R50, R55,
   all beyond the contact row) and C129/R177 at 12.4 mm; so no B part of any height is anywhere the
   card or the holding fingers go. Through-hole pads intersecting the seated card, lane, 5 mm
   extension or the J3 courtyard: none (the nearest is J1's left boardlock NPTH at (16.5, 56), 1.51 mm
   from the courtyard and 2.47 mm from the shell). Mounting holes (3.2 mm NPTH, F): H1 (4, 4) is
   9.9 mm from the lane and 9.7 mm from the courtyard; H4 (4, 61) is 6.3 mm from the courtyard and
   13.9 mm from the seated card; H2/H3 are > 67 mm away. The ejected card: the lane is a full card
   length, so a push-push over-travel of any stroke leaves the card inside the lane (the Hirose
   stroke is still uncaptured per the storage README). Loading: the slot faces the board interior
   15.5 mm from the top edge and 2.1 mm (shell) from the left edge; the card is loaded with the board
   out of the enclosure, pressed from the B side; REQUIREMENTS already states the socket needs no
   card access in service. On F, the lane lies under U24 (TPS26625, `sensor-power-rear`, 18.4 mm²),
   C89, R77, R120 and the `sensor-power-rear` passives; the seated card lies under R119/R120 (620 Ω
   2512, `wheel-input`), U26 (LM2903), D102 and `wheel-input` passives. No cross-board collision
   is possible; the plane stage should know the card sits under two 2512 resistors.
2. **IMU.** U2 (F, courtyard 10.255–13.745 × 8.505–11.495) unchanged from the seed. No courtyard
   intersects U2's or any of the seven obstacle polygons. The only courtyard within 4 mm of U2 is
   J3's at 3.76 mm, and it is the lane extension (the card strip is 4.03 mm from U2, the socket shell
   24.6 mm); the B-side IMU obstacle (7–17 × 5–15) ends 0.255 mm short of the J3 courtyard. Nothing
   heavy or tall is near U2: next are C1 5.13, H1 5.49, C2 5.82 (fixed), then C86 8.06; L1 14.56,
   L2 21.81, U5 11.54, U7 23.73, J1 37.46, J2 69.57, U1 35.85, U3 52.86 mm. L1/L2 (+0.5 mm): no
   opposite-side courtyard (nearest J3 12.07 mm from L1, D105 8.61 mm from L2).
3. **GNSS RF corridor.** U3 pad 11 (77.5, 29.1) → J2 pin 1 (86.96, 28.0), 9.524 mm; net members
   exactly U3.11, L3.2, D3.1, J2.1, all F; L3 pad 2 0.921 mm off the line; U3 (71.5, 35.0) rot 180,
   L3 (80.6, 28.6) rot 90, D3 (80.485, 25.97) rot 90, C42 (80.6, 31.81) rot −90, J2 (85.24, 28.0)
   rot 180 (iteration 3/5/6 poses). ±1.5 mm corridor intersects J2, L3, U3 on F and nothing on B:
   no courtyard, no pad, no through-hole. Unchanged from iteration 6.
4. **Router pre-check** (`kicad-route blocked --board`, heuristic): 499 connections analysed,
   **487 unobstructed**, 12 hard-blocked on their best layer: J1 8 (/TIRE_CAN_H ×2, /TIRE_CAN_L ×2,
   /POD_5V_SENSOR ×2, /POD_TIRE_SUPPLY, /POD_WHEEL_REAR_SIGNAL), U7 2 (/POD_12V_PROTECTED,
   /POD_CAN_P), U5 1 (/POD_CAN_N), U12 1 (/+5V_CAN). All fixed parts or J1's own pins. Iteration 6:
   486/499.
5. **Crowding.** 458 same-side pairs at 0.26–0.30 mm (iteration 6: 448), minimum 0.26 mm, none
   below 0.25, no overlap. Block spreads 4.3–13.5 mm. Policy groups 12/12; C80 4.99 of 5, C79 4.91
   of 5, C83 4.68 of 5, C82 8.61 of 9, R24 11.68 of 12 at the limit. Courtyards < 1 mm from the
   edge (policy floor 0.5): only TP3 at 0.505 mm (fixed pogo pad, from the seed).
6. **TP2/TP5.** (81.25, 7.28) and (81.25, 17.85), B, under U1, 63.3–63.8 mm from J3's courtyard;
   the iteration-5 conflict cannot recur in this arrangement.

## Verified claims

| Claim (README / evidence) | My result | Status |
| --- | --- | --- |
| Packer board SHA256 `35f242c8…`; SHA256SUMS | match; 46/46 OK; seed `21bbf8ef…` = result `source_sha256`; silk board `2c1ac944…` | verified |
| 309 footprints, 162 F / 147 B | 309, 162 F / 147 B on both boards; 272 moved vs seed; 37 locked seed refs unmoved | verified |
| Two boards differ only in silk/text | packer vs silk: 0 pose/rotation/side differences; U20, JP4 references hidden; U16/U18/U19 0.8/0.12 → 1.0/0.15; JP4 ×3, U8 ×2, U9 ×3 graphics to Fab (= `silk-policy-pass-1/2.json`) | verified |
| Outline 90 × 65; courtyards inside except J1/J2/U1 | exactly J1 bottom 22.845, J2 right 9.525, U1 top 21.245 / right 6.495 mm; no pad centre outside | verified |
| Same-side gap ≥ 0.25 mm | 0 overlaps, 0 pairs < 0.25, min 0.26, 458 pairs 0.26–0.30 | verified |
| no_stacking pass; obstacles; IMU | 0 opposite-side courtyards in L1/L2 + 0.5 mm; 0 courtyards in the 7 obstacles; 0 part bodies within 4 mm of U2 (J3 lane courtyard at 3.76) | verified |
| 12 obligations / 26 pairs pass | 26/26 by pad centre (12 supply, 12 return, 2 switch), nets and sides correct, max 8.1234 (u5-vcc-C4, u7-vcc-C11 return, limit 8.5), switch legs 2.786 / 2.811 of 5.5; row-for-row equal to `obligations-measured.json` | verified |
| 17 blocks arranged as rigid macros | all 17: every member at the candidate's anchor-relative pose under one quarter-turn, sides unchanged, member sets = allocation. Rotations: power-entry 180, supplies-5v 90, afe −90, adc 90, mcu 0, can −90, aux-afe −90, storage 0, supervision 180, tire-can 0, sensor-power-front −90, -rear −90, -tire 180, wheel-input −90, diagnostic 90, aux-power −90, thermistor 0 | verified |
| thermal_spread pass | U5–U7 16.55 mm centre, 9.61 mm courtyard | verified (centre metric) |
| no_block_over_fixed 50 advisory, cross-side only | 50 (U3 22, U1 16, J1 11, R4 1), none same-side; only J1 has pins; 4 members < 0.5 mm from its pad/peg copper (R22, R50, JP5, JP3), none overlapping | verified, physical content added |
| J3 (9.12, 44.25) rot 0 B; lane courtyard x 1.26–17.05, y 15.2–53.1; no B part intersects; slot toward −y | (9.12, 44.25) rot 0 B; courtyard 1.305–16.995 × 15.255–53.065; 0 B courtyards intersect; contact row at y 51.975, card tip at y 30.525, travel along −y; lane and 15 mm beyond it empty on B; no through-hole under it | verified |
| Cited-rules DRC on the silk-policy board: 199 library findings only | identical: 199 `lib_footprint_issues` (warning), 0 other types, 0 mine-only / 0 packet-only; unconnected 499 identical; parity 0 | verified |
| Packer native DRC vs seed: 3 `silk_over_copper` added, closed by the policy | packer board under the cited rules: 3 silk_over_copper + 8 silk_overlap + 3 text_height + 3 text_thickness (U20/U22, JP4, U8/U9, U16/U18/U19), all absent on the silk-policy board | verified |
| 106.355 s wall | `packer-execution.json` says so; not re-run | read only |
| "Everything else as iteration 6" | inputs yes; arrangement no: 10 blocks / 140 footprints moved, storage from under U1 to the bottom-left corner, SD spans 1.9–15.4 → 73.9–88.3 mm | overstated (should-fix 1, 2) |
| Routing diagnostic under `../../routing-diagnostic/iteration-7/` | not checked | not verified |

## Method

- `check7.py` (the iteration-6 script re-pointed at iteration 7): `GetBoardPolygonOutlines` for the
  outline; `fp.GetCourtyard(F/B_CrtYd)`; overhang = courtyard minus outline per edge; same-side pairs
  with a 0.6 mm bbox prefilter and exact polygon distance/intersection; opposite-side intersections
  with L1/L2 (+0.5 mm, mitred) and U2 (intersection and 4 mm, any side); obstacle polygons from
  `inputs/policy.json`; obligations by pad centre over `electrical-locality.json` (all three legs,
  net and side checks; the switch legs measured in a second pass); policy groups by footprint
  centre; block rigidity by fitting one quarter-turn about the candidate anchor to every member of
  `inputs/candidates/<id>.candidate.json` (1 µm, exact rotation, equal side); RF net membership and
  ±1.5 mm corridor on both sides including pads and through-holes; `no_block_over_fixed` findings
  from `placement-result.json` with each fixed part's through-hole pads (`GetEffectivePolygon` on the
  member's copper layer) against the member courtyard; every opposite-side courtyard vs every
  through-hole pad < 0.5 mm; silk vs packer vs seed pose/text/graphic comparison.
- `j3.py`: card geometry from J3's B.Fab drawing (shell, seated card to y 30.525, width 11.0);
  regions seated / 15 mm lane / 5 mm and 15 mm extensions / courtyard-width lane; B and F courtyard
  census per region; nearest B parts; through-hole pads (PTH/NPTH, pad-size circle) intersecting each
  region; mounting-hole positions and distances; shell vs U2/J1; J1 through-hole copper vs R50, R22,
  JP3, JP5; SD-net spans U1 pin to J3 pad and large courtyards crossed by the straight line;
  pull-up/bypass distances; iteration-6 silk board loaded beside iteration 7 to list moved blocks.
- DRC: `cp silk.kicad_pcb drc/telemetry-pod.kicad_pcb; cp board-setup.kicad_pro
  drc/telemetry-pod.kicad_pro; cp telemetry-pod.kicad_dru drc/; kicad-cli pcb drc --severity-all
  --all-track-errors --schematic-parity --format json`; set comparison on (type, severity,
  description, item descriptions) and on unconnected items against
  `evidence/cited-rules-drc-silk-policy-board.json`; the same on the packer board
  (`…/iter7/drc-packer/`).
- Router: `kicad-route blocked --board silk.kicad_pcb --out route/out --top 15` and `--json`;
  hard-blocked = `best_layer_hard_count > 0`, blockers from `layers[best_layer].hard[].footprint`.
- Footprint source: `design-rules/footprints/Connector_Card.pretty` (courtyard −7.82…7.88 ×
  −8.82…29.0; card drawn to 13.725) compared with the board's J3 courtyard and B.Fab items.
