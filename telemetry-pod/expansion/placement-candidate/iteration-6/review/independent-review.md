# Independent review: placement candidate iteration 6 (silk-policy board 43fb72fc…625c5, packer board 172d3d4e…3be6)

Reviewer: independent review worker, 2026-10-21. Packet:
`/home/halbritt/git/fome-mc/telemetry-pod/expansion/placement-candidate/iteration-6/` at fome-mc
`866122b`. Both boards and the seed gunzipped to
`/tmp/claude-1000/-home-halbritt-git-agent-ee/27167fc2-dedb-47b5-9a97-e1d328bdac8d/scratchpad/iter6/boards/`.
Packer board SHA256 `172d3d4e8739eaf19e4ef03a194c336abbdab3a23b7c325ad7c0ec51073f3be6` matches the README
and `placement-result.json`; seed `8605b07c…` matches `placement-result.json` `source_sha256`; all 50
lines of `SHA256SUMS` verify. All geometry is my own pcbnew 10.0.7 + shapely 2.2 code
(`…/scratchpad/iter6/scripts/check.py`, `/usr/bin/python3 -B`); DRC via `kicad-cli pcb drc
--severity-all --all-track-errors --schematic-parity` on a same-stem copy beside
`design-rules/board-setup.kicad_pro` + `telemetry-pod.kicad_dru` (`…/scratchpad/iter6/drc/drc.json`);
router pre-check via `kicad-route blocked --board` (`…/scratchpad/iter6/route/`). Nothing under `~/git`
was modified.

## Verdict

**Reject as the board to route; re-run with one placement change.** The packing, block rigidity,
obligations, clearances, IMU/inductor isolation, the GNSS corridor and the cited-rules DRC all
reproduce and are better than iteration 5 on every axis the previous review conditioned. But the
microSD card cannot be inserted into J3 on this board: the ADC U4 (SOIC-16, 1.75 mm body, side B)
sits 0.52 mm beyond the seated card's tip, inside the card's insertion lane. D-PCB-13 keeps the
*seated* card clear; it says nothing about the lane the card travels through, and the packer filled
that lane to the 0.25 mm gap. The fix is a placement change (move the `adc` block, or extend the
J3 envelope along the slot axis and re-pack), so routing this board would be wasted work.

Conditions for the next candidate, in order of weight:

1. (Blocking 1) Keep a clear lane along J3's slot axis on side B for the card's full travel:
   at least the card length (15 mm) beyond the socket mouth, over the card width (11 mm), free of
   any body taller than the socket's card floor. Either add it to the D-PCB-13 courtyard / an
   obstacle polygon on B, or move the `adc` block. Record the Hirose push-push ejection stroke
   from the DM3AT drawing while doing it (the datasheet capture is still pending per the
   storage README).
2. (Should-fix 1) Decide on the eleven `afe`/`thermistor` members on B under J1 within 0.30–0.70 mm
   of J1's through-hole pad copper and boardlock hole: keep them with an explicit THT-soldering
   disposition, or add a B-side keep-out around J1's pins and pegs.
3. (Should-fix 2) Record that J3's slot faces the board interior 55 mm from the nearest edge,
   so the card is loaded with the board out of the enclosure, and that the card lane crosses the
   `mcu` block and U20 on F (no conflict, but the plane stage should know).

Everything else below is a note or bookkeeping.

## Blocking findings

1. **U4 blocks the microSD card lane.** J3 (Hirose DM3AT, side B) at (69.54, 18.842) rot 90 with the
   D-PCB-13 footprint (courtyard x 55.565–78.355, y 10.967–26.657, 22.8 × 15.7 mm, i.e. the
   footprint's −8.82…+13.98 extension is in the board). Contacts (pads 1–9) are the row at
   x = 77.265; the card enters from −x (the board interior) and its seated tip is drawn on B.Fab at
   x = 55.765 over y 13.717–24.817 (card width 11.1 mm). U4 (`SOIC-16_3.9x9.9mm`, MCP3208, side B,
   `adc` block anchor at (50.055, 11.452) rot −90) has courtyard x 44.86–55.25, y 7.757–15.147: it
   is 0.52 mm from the seated card tip and overlaps the card's lane (y 13.717–15.147, a 1.43 mm
   strip of the card's width) over 10.4 mm of U4's length (14.3 mm² of lane). A 15 × 11 × 1 mm card
   slides in parallel to the board at the socket's card-floor height (socket 1.83 mm tall, card
   1.0 mm thick, so the card's underside is well below U4's 1.75 mm body top); it cannot pass over
   U4's corner flat, and the slot's 1.1 mm mouth and 11 mm width leave no roll or yaw room to go
   around it. On a push-push socket the ejected card travels further out than seated, into U4.
   Consequence: the card cannot be loaded at the factory, and REQUIREMENTS makes standalone
   logging depend on it. Nothing else is in the lane: C40 at 7.95 mm and R15 at 11.16 mm beyond
   the tip are clear if the lane is 15 mm. The packer could not see this: J3's courtyard stops
   0.25 mm past the seated card, and the `adc` block was placed with a 0.25 mm gap to it (U4 is
   0.315 mm from J3's courtyard, the third-nearest B part). TP2/TP5, the iteration-5 conflict, are
   now 3.68 / 4.18 mm from the J3 courtyard and off the lane: that condition is met.

## Should-fix

1. **Back-side parts against J1's through-hole pins and pegs.** J1 (AMPSEAL 35, F, right-angle,
   35 PTH pins 1.75 mm drill / 2.4 mm pad plus two 2.85 mm NPTH boardlock holes at (16.5, 56) and
   (73.5, 56)) has eleven block members under its courtyard on B: C34, C36, C39, R19, R20, R22,
   R23, U8 (TSSOP-14 op-amp, `afe`) and the solder jumpers JP3, JP4, JP5 (`thermistor`). Their
   courtyards do not touch the pad copper (native DRC clearance 0), but R22 is 0.304 mm from the
   left boardlock hole, JP5 0.339 mm from pin 3 (/POD_12V_IN) and JP3 0.384 / 0.704 mm from pins
   4 (/GND) and 5. The pins are soldered from B after SMT, with a fillet on a 2.4 mm pad and an
   iron or selective nozzle that needs access; the AMPSEAL boardlock peg sits in that NPTH hole.
   This is the physical content of the README's 55 `no_block_over_fixed` advisories: the other 44
   (17 under U3, 15 under the fixed capacitors C8/C9/C10/C14/C15 and R4/R5, 5 under U7) are
   SMD-over-SMD through the board, which is harmless, and U7's 0.30 mm thermal vias are 0.85 mm
   from the nearest `aux-afe` courtyard (R40, R44). Only J1 has through-hole pins and only these
   three members are closer than 1 mm to them. Decide with a fabricator rule, or give J1's pin
   field a B-side keep-out.
2. **J3 orientation and card lane across the MCU block.** The slot opens toward the board
   interior; the socket body is 11.6 mm from the right edge and 11.0 mm from the top edge, and the
   seated card tip is 55.6 mm from the left edge. As in iteration 5, the card is loaded with the
   board out of (or open in) the enclosure; the enclosure drawing must not assume a slot. On F,
   the seated card region lies under U1 (140 mm² of the courtyard), U20 (21.8 mm²), C45 and the
   `mcu` passives; no cross-board collision is possible, and no through-hole pad is under the J3
   courtyard (U1's thermal-via pad 41 is 0.26 mm outside it). Thermal context unchanged: J3 is an
   85 °C part under the module's heat dump; keep In1.Cu solid there.
3. **U6 and U12 (both TPS7B4253 DDA, `supplies-5v`) are 0.26 mm apart.** Two LDOs with exposed
   pads at the packing gap share one thermal footprint on F; the thermal rule only separates U5
   from U7 (9.61 mm courtyard gap, 16.55 mm centre; the arrangement's 15 mm figure is centre-to-
   centre). The plane stage should give the pair a joint copper area, or the next block pack
   should spread them.
4. **Packet bookkeeping.** `placement-result.json` has `verdict: defect` / `outcome: defect`
   (the 3 `silk_over_copper` on U20's reference over U22's pads) while the README row says
   "judgment pass"; both are true (judgment pass, candidate defect) and the silk policy closes it,
   but the row should say so. `evidence/cited-rules-drc-silk-policy-board.json` was produced on a
   file named `ca2.kicad_pcb`, not under the project stem; the result is identical to mine on the
   properly named copy, so no harm. `obligations-measured.json` has `board_sha256: null`.

## Notes (no action for placement)

5. **IMU isolation is better than iteration 5.** U2 (F, courtyard 10.255–13.745 × 8.505–11.495):
   nothing on either side within 4 mm of its courtyard (iteration 5 had four 0603s at 3.51 mm).
   Nearest: C1 5.13, H1 5.49, C2 5.82 (fixed 1210 bulk caps and the mounting hole), then U25 7.87,
   U24 8.11; L1 14.56, L2 21.81, U5 11.54, U7 23.73, J1 37.46, J2 69.57, U1 35.85, J3 41.82 mm.
   No courtyard intersects the seven obstacle polygons. U2 rot 0, unchanged from the seed.
6. **GNSS RF corridor, B side now empty.** U3 pad 11 (77.5, 29.1) → J2 pin 1 (86.96, 28.0),
   9.524 mm; L3 pad 2 0.921 mm off the line; D3 (80.485, 25.97), C42 (80.6, 31.81), L3 (80.6, 28.6)
   rot 90, U3 (71.5, 35.0) rot 180, all at the iteration 3/5 poses; net members exactly U3.11,
   L3.2, D3.1, J2.1, all F. The ±1.5 mm corridor intersects J2, L3, U3 on F and **nothing on B**
   (no courtyard, no pad, no through-hole); iteration 5 had J3's shield tabs and TP2 there. The
   In1 GND condition is now trivially satisfiable.
7. **SD bus.** J3 contact row (x 77.265) ↔ U1 pins: DAT3 1.86, CMD 7.94, CLK 8.76, CD 9.15,
   DAT2 9.37, DAT0 13.16, DAT1 15.43 mm pad-centre spans. Pull-ups R46–R50, R55 are 11.6–12.9 mm
   centre-to-centre from J3 (2.5–4.5 mm from their J3 pad by same-net pad); C64 2.39 mm and C65
   2.82 mm from J3 pin 4 (+3V3). All B, all inside the storage block.
8. **Crowding.** In-board courtyard density F 0.620, B 0.229. 448 same-side pairs sit at
   0.26–0.30 mm (iteration 5: 364), minimum 0.2596 mm; nothing below 0.25, no overlap. Block
   spreads (max member distance from anchor) 4.3–13.5 mm (diagnostic 13.49 with 46 members,
   storage 12.88). Policy groups: 12/12 pass; R24 at 11.68 of 12 mm and C80 at 4.99 of 5 mm are
   at the limit.
9. **Router pre-check** (`kicad-route blocked --board`, heuristic): 499 connections analysed,
   **486 unobstructed**, 13 with a hard blocker on their best layer: J1 (8: /TIRE_CAN_H, /TIRE_CAN_L
   ×2 each, /POD_5V_SENSOR ×2, /POD_TIRE_SUPPLY, /POD_WHEEL_REAR_SIGNAL), U7 (2: /POD_12V_PROTECTED,
   /POD_WHEEL_FRONT_SUPPLY), U5 (2: /POD_CAN_P, /POD_CAN_N), U12 (1: /+5V_CAN). All fixed parts or
   their own pins (J1-to-J1 same-net pairs). Iteration 5: 489/499.
10. **Silk state.** 272 references hidden, 37 visible (all 1.0 / 0.15 mm); values all on Fab.
    The silk-policy board differs from the packer board only in: U20 and JP4 references hidden,
    U16/U18/U19 references 0.8/0.12 → 1.0/0.15, and 8 silk graphics moved to Fab (JP4 ×3, U8 ×2,
    U9 ×3) — exactly `silk-policy-pass-1/2.json`; 0 pose, rotation or side differences across the
    309 footprints. The iteration-5 U16/U19 text condition is met.
11. **Declared overhangs** (bookkeeping as in iteration 5): J1 bottom 22.845, U1 top 21.245 /
    right 6.495, J2 right 9.525 mm by `GetCourtyard()` against declared 22.85 / 21.25 / 6.50 / 9.73.
    No pad centre outside the outline. 37 policy `fixed_refs` all at their seed poses; 272 of 309
    footprints moved vs the seed.

## Verified claims

| Claim (README / evidence) | My result | Status |
| --- | --- | --- |
| Packer board SHA256 `172d3d4e…`; SHA256SUMS | match; 50/50 lines OK; silk board `43fb72fc…`, seed `8605b07c…` = result `source_sha256` | verified |
| 309 footprints, 162 F / 147 B, 309 of 309 placed | 309, 162 F / 147 B on both boards; 272 moved vs seed, 0 fixed refs moved | verified |
| Outline 90 × 65; courtyards inside except J1, J2, U1 | exactly J1 (bottom), J2 (right), U1 (top+right) outside, within the declared `fixed_overhangs`; no pad outside | verified |
| Same-side gap ≥ 0.25 mm (`gap_nm` 250000) | 0 overlaps, 0 pairs < 0.25 mm, min 0.2596 mm, 448 pairs at 0.26–0.30 | verified |
| no_stacking under L1/L2 pass; obstacles | 0 opposite-side courtyards in L1/L2 courtyard + 0.5 mm (nearest C59/R40 at 0.805 mm from L2); 0 courtyards in the 7 obstacle polygons; 0 within 4 mm of U2 | verified |
| 12 obligations / 26 pairs pass | 26/26 by pad centre (12 supply, 12 return, 2 switch), nets and sides correct, max 8.1234 mm (u5-vcc-C4, u7-vcc-C11 return, limit 8.5), identical to `obligations-measured.json` and to iteration 5 (fixed clusters) | verified |
| 17 blocks arranged as rigid macros | all 17 blocks: every member at the candidate's anchor-relative pose under one quarter-turn (0/90/180/270) about the anchor, sides unchanged, member sets = allocation; 0 re-packed members. Rotations: power-entry 180, supplies-5v 90, afe −90, adc −90, mcu 0 (anchor C45), can −90, aux-afe 0, storage 90, supervision 90, tire-can 0, sensor-power-front/rear/tire 180, wheel-input −90, diagnostic 90, aux-power −90, thermistor 0 | verified |
| thermal_spread pass (U5–U7 ≥ 15 mm) | 16.55 mm centre, 9.61 mm courtyard gap | verified (centre metric) |
| no_block_over_fixed: 55 advisory findings, cross-side only | 55 (U3 17, J1 11, C15 6, U7 5, C9 4, C10 4, C14 4, R5 2, R4 1, C8 1), none same-side; only J1 has through-hole pins; 3 members within 0.40 mm of its pad/peg copper, none overlapping (should-fix 1) | verified, physical content added |
| Cited-rules DRC on the silk-policy board: 199 library findings only, all other types 0 | identical: 199 `lib_footprint_issues` (warning), 0 mine-only / 0 packet-only; unconnected 499 identical; parity 0 (no schematic) | verified |
| Silk policy: 2 refs hidden, 8 graphics to Fab, 3 refs resized; no pose change | exactly U20, JP4 hidden; JP4/U8/U9 8 graphics; U16/U18/U19 resized; 0 pose/side diffs | verified |
| Packer native DRC vs seed: 3 `silk_over_copper` added, closed by the policy | `native_drc_comparison.added_by_type` = 3 silk_over_copper (U20 ref over U22 pads); absent on the silk-policy board | verified |
| J3 at (69.54, 18.84) B; TP2/TP5 at x ≥ 81 clear of the card envelope | (69.54, 18.842) rot 90 B; TP2 (81.25, 7.29) 3.68 mm and TP5 (83.53, 17.85) 4.18 mm from the D-PCB-13 courtyard, off the lane | verified; but U4 is in the lane (blocking 1) |
| GNSS corridor as iterations 3/5 | identical F-side numbers; B side now empty | verified |
| 168.846 s wall, 17 candidates packed | `packer-execution.json` and `pack-log.txt` say so; not re-run | read only |
| Routing diagnostic under `../../routing-diagnostic/iteration-6/` | not checked | not verified |

## Method

- `check.py` (pcbnew + shapely): `GetBoardPolygonOutlines(poly, False)` for the outline;
  `fp.GetCourtyard(F/B_CrtYd)` for courtyards; overhang = courtyard minus outline per edge;
  same-side pairs with a 0.6 mm bbox prefilter and exact polygon distance / intersection area;
  opposite-side intersections with L1/L2 (+0.5 mm, mitred buffer) and U2 (intersection and
  4 mm distance, any side); obstacle polygons from `inputs/policy.json`; obligations by pad
  centre over `electrical-locality.json` with net and side checks (all three legs); policy groups
  by footprint centre; block rigidity by fitting one quarter-turn about the candidate anchor to
  every member of `inputs/candidates/<id>.candidate.json` (position tolerance 1 µm, rotation
  exact, side equal); J3 pads, B.Fab card drawing, courtyard, B/F neighbours, lane census, pull-up
  and bypass same-net pad spans, SD spans to U1, through-hole pads under the courtyard; RF net
  membership, ±1.5 mm corridor on both sides including pads and through-holes;
  `no_block_over_fixed` findings re-derived from `placement-result.json` with each fixed part's
  through-hole pads (`GetEffectivePolygon` on the member's copper layer) against the member
  courtyard; every opposite-side courtyard vs every through-hole pad < 0.5 mm; density, residual
  parts, thermal neighbours, text census; silk vs raw vs seed pose/text/graphic comparison.
- DRC: `cp silk.kicad_pcb drc/telemetry-pod.kicad_pcb; cp board-setup.kicad_pro
  drc/telemetry-pod.kicad_pro; cp telemetry-pod.kicad_dru drc/; kicad-cli pcb drc --severity-all
  --all-track-errors --schematic-parity --format json`; set comparison on (type, description,
  item descriptions) and on unconnected items against
  `evidence/cited-rules-drc-silk-policy-board.json`.
- Router: `kicad-route blocked --board silk.kicad_pcb --out route/out --top 15` and `--json`;
  hard-blocked connections filtered on `best_layer_hard_count > 0`, blockers taken from
  `layers[best_layer].hard[].footprint`.
- Footprint source: `design-rules/footprints/Connector_Card.pretty/*.kicad_mod` courtyard
  (−7.82…7.88 × −8.82…13.98) compared with the board's J3 courtyard graphics (22.85 × 15.75 mm).
