# Independent review: placement candidate iteration 5 (board 5bf9e33d…a19648)

Reviewer: independent review worker, 2026-10-21. Packet:
`/home/halbritt/git/fome-mc/telemetry-pod/expansion/placement-candidate/iteration-5/` at fome-mc
`b87cfb6`. Board, seed and base seed gunzipped to `…/scratchpad/{board,seed,baseseed}/`;
candidate SHA256 `5bf9e33da72bb1d4eab29aea967800860f139caabc5a8e33ce77d0c519a19648` matches the
README; `inputs/seed.kicad_pcb` SHA256 `044b9f7c…` matches `request.json` `source_sha256`; all 32
lines of `SHA256SUMS` verify. All geometry is my own pcbnew 10.0.7 code
(`…/scratchpad/scripts/check.py, check2.py, check3.py`, `/usr/bin/python3 -B`); DRC via
`kicad-cli pcb drc --severity-all --all-track-errors --schematic-parity` on a same-stem copy beside
`design-rules/board-setup.kicad_pro` + `telemetry-pod.kicad_dru` (`…/scratchpad/drc/drc.json`);
router pre-check via `kicad-route blocked --board` (`…/scratchpad/route/`). Nothing under `~/git`
was modified.

## Verdict

**Conditional proceed** to plane planning and routing. No blocking placement finding. The README's
numeric claims all reproduce (table below). Conditions, in order of weight:

1. Before the routed board is adopted, decide the TP2/TP5 pogo-pad vs. microSD-card conflict
   (should-fix 1): either move the two pads or record that the programming fixture is used with no
   card inserted.
2. Resize or hide the U16/U19 reference texts (should-fix 2); the packet's own
   `cited-drc-after-policy-and-text-fix.json` already shows the board is clean with that done.
3. Carry the J3 enclosure-fit and thermal notes (should-fix 3, note 5) into the plane stage and
   the enclosure drawing, as the README itself lists.

The placement does not need to change for any of these.

## Blocking findings

None.

## Should-fix

1. **TP2/TP5 pogo pads sit against the inserted card's edge.** J3 (Hirose DM3AT, B side) at
   (74.46, 19.775) rot 180: contacts at y = 12.05 (board-top side), card inserted from +y (the board
   interior). The footprint's B.Fab card drawing spans x 69.33–80.44, y 28.05–33.55, i.e. the card
   tip protrudes ~4.9 mm past the courtyard (y 28.70) when seated, further during push-push eject.
   TP2 (81.25, 29.91) and TP5 (81.28, 32.16), `PogoPad_D1.5mm` on B, have copper from x = 80.50,
   0.06 mm beside the card's drawn edge; their courtyards overlap the card region (0.15 / 0.11 mm²).
   The pads themselves are flat and the card cannot hit them, but a 1.3–1.5 mm pogo barrel on the
   pad centre would land within ~0.1 mm of a seated card, and a card half-ejected during
   programming would be under the pin. REQUIREMENTS: factory firmware load is over UART pogo-pin
   test pads before sealing, which is also when the card is loaded. Fix: ≥ 1 mm between any
   pogo target and the card outline (move TP2/TP5 ~1.5 mm in +x or south of y 34), or document
   "program with no card inserted". The packer cannot see this: J3's courtyard excludes the card.
2. **U16 and U19 reference fields at 0.8 mm / 0.12 mm** (B.Silkscreen, visible): the only
   `text_height` (2) and `text_thickness` (2) findings under the cited project (min 1.0 / 0.15).
   U18's reference has the same size but is hidden by the pre-pass, so it does not fire. Resize to
   1.0 / 0.15 or add them to the D-PCB-8 hidden set.
3. **J3's slot faces the board interior, not an enclosure wall; thermal and fixture context
   should be recorded.** The README calls the slot orientation "unverified against the enclosure
   wall". Verified: the card enters from y ≈ 33.5 toward y = 12, the socket body is 7.67 mm from
   the right edge and 10.91 mm from the top edge, and the card tip is 36 mm from the bottom edge,
   so the slot never meets a wall; it needs back-side access with the board out of (or open in)
   the enclosure. Nothing body-height is on B in the card's travel or ejection path (the nearest B
   parts beyond the card tip are C122 0805 at y 40.8 and R38 0603 at x 68.9, 7 mm and 0.4 mm
   outside the corridor respectively). Cross-side, J3's courtyard lies under U1 (140.7 mm² of the
   ESP32 module body), U3 (22.9 mm²), L3, D3, R30 and R33 on F; no physical collision is possible
   across the board, and U1's twelve 0.20 mm thermal PTH vias (y ≤ 10.36) stay 0.55 mm outside
   J3's courtyard and ≥ 1.69 mm from its nearest pad. J3 is a −25…+85 °C part (D-PCB-12
   exception) sitting under the module's heat dump; the plane stage should keep In1.Cu solid
   under J3 and tie U1's via field to it, as iteration 3 said for U14.
4. **Declared overhang limits equal the courtyard centreline, not the stroked courtyard.**
   `fixed_overhangs` `max_nm`: J1 bottom 22.85, U1 top 21.25 / right 6.50, J2 right 9.73 mm. Raw
   courtyard vertices give exactly 22.85 / 21.25 / 6.50 (and 9.53 for J2), but KiCad's
   `GetCourtyard()` (0.05 mm stroke) extends 0.045 mm further: J1 22.895, U1 21.295 / 6.545, J2
   9.575. The judgment passes because the packer uses the same centreline convention; the
   envelope should state that, or carry the stroked figure, so a stricter checker does not refuse
   the same board. Bookkeeping, not geometry.

## Notes (engineering observations, no action required for placement)

5. **GNSS RF corridor, B side now holds J3 and TP2.** The F-side path is unchanged from
   iteration 3: U3 pad 11 (77.5, 29.1) → J2 pin 1 (86.96, 28.0), 9.52 mm; L3 pad 2 (80.6, 27.812)
   3.36 mm from the U3 pad, 6.36 mm from the pin, 0.92 mm off the line; D3 (80.485, 25.97), C42
   (80.6, 31.81); RF net members exactly U3.11, L3.2, D3.1, J2.1, all F; corridor ±1.5 mm
   intersects on F only C42, D3, J2, L3, U3. On B the corridor now intersects J3 (its GND shield
   tabs, (81.285, 26.7) and (81.285, 16.35)) and TP2 instead of iteration 3's C75/U18/R181/U9/U4.
   With In1.Cu solid GND under the F.Cu microstrip this is fine; the plane planner must keep the
   strip x 76–88, y 26.5–30.6 on In1 unbroken and must not fan J3's shield tabs into it with a
   via row that slots the reference.
6. **IMU isolation.** U2 (F, courtyard 10.21–13.79 × 8.46–11.54): L1 14.56, L2 21.81, U5 11.54,
   U7 23.73, U26 6.81, J1 37.46, J2 69.57, U1 35.85, J3 52.84, U3 52.86 mm (exact polygons, any
   side) — identical to iteration 3 for the fixed cluster. No courtyard on either side intersects
   L1, L2 or U2 through the board, and none intersects the request's seven obstacle polygons.
   Nearest parts of any kind: R114/R31 (F) and R136/R138 (B), 0603 resistors at 3.51 mm from the
   courtyard — outside the request's F ring (which is 2.71 mm wide on the left, 3.96 mm on the
   right) and the B exclusion (3.21/3.46 mm), but inside a literal 4 mm figure. They are not tall
   or heavy; the nearest larger packages are the fixed 1210 bulk caps C1/C2 at 5.0/5.7 mm, then
   H1 and C128 (1206, B) at 6.1 mm. No electrolytic or tall part is near U2.
7. **SD bus geometry is short.** J3 contact row on B at y = 12.05 ↔ U1 pins on F at x = 81.25:
   DAT0 3.53, DAT1 3.70, CD 4.52, CLK 5.20, CMD 7.39, DAT3 8.10, DAT2 10.55 mm pad-centre spans,
   one via each. Pull-ups 4.8–13.3 mm from their J3 pad (uncritical), C64 2.14 mm and C65 3.17 mm
   from J3 pin 4 (+3V3). Group `j3-microsd-local` (R46–R50, R55, C64, C65 within 12 mm of J3):
   8.85–11.985 mm centre-to-centre, all pass; R46 (11.985) and R49 (11.982) are at the limit.
8. **Router pre-check** (`kicad-route blocked --board`, heuristic straight/L corridors): 499
   connections analysed, **489 unobstructed**, 10 with a hard blocker on their best layer:
   /TIRE_CAN_H and /TIRE_CAN_L (U20 ↔ U21 pairs, 16–21 mm), /POD_12V_PROTECTED U5.1↔U5.3 (4.7 mm,
   blocked by U5's own exposed pad — a plane net), /PRE_6V3 (7.4 mm), /POD_CAN_N (30.6 mm),
   /SENSOR_POWER_TIRE_OVP (18.6 mm), /POD_TIRE_SUPPLY and /POD_WHEEL_REAR_SIGNAL from J1 (12 mm).
   Top blockers by best layer: J1 (6), U12 (2), U6 (1), U5 (1). All are fixed or large parts;
   nothing suggests a placement change before a real routing run.
9. **Silk state, as it actually is.** The board has **282 hidden references and 27 visible**
   (all 1.0/0.15 except U16/U19); values are all on Fab. The README's "12 references hidden,
   13 graphics moved" is the pre-pass delta from `placement-seed-microsd/base-seed` (verified:
   exactly D101, D103, D104, R162, U18, U20, U22, U23, U24, U25, U28, U29 flipped, and 13 silk graphics
   moved to Fab on U21, U25, D102, C47, U22, U24, U28, U29); the other 270 hidden references were
   inherited by the base seed from iteration 3's D-PCB-8 pass. The candidate changes no text or
   silk relative to `inputs/seed` (0 visibility or graphic-count changes). Cited-project DRC:
   silk 0, silk-text 4 (should-fix 2).
10. **Packer-native DRC row.** `evidence/native-drc.json` (the packer's own run, default rules)
    carries 18 `clearance` findings that the README row "no added findings" does not name: all
    are intra-footprint pad gaps of 0.15–0.175 mm on U2 (LGA-14), U16, U18, U19 (SOT-23-5) under
    the packer's default 0.20 mm. They are footprint geometry, present in the seed, and absent
    under the cited 0.09 mm project. Not a placement matter, but the row would be clearer naming
    them.
11. **Packet hygiene.** `placement-judgment.json` again lists a J2 overhang on side B although J2's
    B courtyard is only its NPTH/edge-mount outline; harmless. `native-drc-comparison.json` is
    empty by construction. The iteration-5 packet has no `blocked-by.json` (iteration 3 had one);
    note 8 fills that gap. The routing-diagnostic directory the README points to was not checked.

## Verified claims

| Claim (README / evidence) | My result | Status |
| --- | --- | --- |
| Board SHA256 `5bf9e33d…a19648`; seed `044b9f7c…` | match; all 32 SHA256SUMS lines OK | verified |
| 309 footprints, 162 F / 147 B; 309 of 309 poses from the seed | 309, 162 F / 147 B; 271 moved vs `inputs/seed`, 0 fixed refs moved; 38 fixed refs at seed poses; H1–H4, J2, U3, L3 locked | verified |
| Outline 90 × 65; courtyards inside except J1, J2, U1 | outline 0..90 × 0..65; exactly J1 (F, bottom), J2 (F, right), U1 (F, top+right) outside; no pad copper outside the outline | verified (see should-fix 4 on the 0.045 mm) |
| Same-side courtyard gap ≥ 0.25 mm (`gap_nm` 250000) | 424 bbox-near same-side pairs checked with exact polygon distance: 0 overlaps, 0 pairs < 0.25 mm; 364 pairs at 0.26–0.30 mm (packed to the limit) | verified |
| No through-board stacking with L1/L2/U2; obstacles respected | 0 opposite-side courtyard intersections with L1, L2, U2; 0 courtyards in any of the 7 obstacle polygons | verified |
| 12 obligations / 26 pairs pass, max 8.12 mm | 12 / 26 pass by pad centre, nets and sides correct, every distance equal to `obligations-measured.json` to 1e-6 mm; max 8.1234 mm (u5-vcc-C4 and u7-vcc-C11 return, limit 8.5) | verified |
| Groups (judgment): all within radius | all 18 measured distances reproduce to 1e-4 mm; tightest C80 4.99/5.0, C79 4.91/5.0, R46 11.985/12, R49 11.982/12 | verified |
| J3 at (74.46, 19.77) B | (74.46, 19.775) B rot 180, `Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5`; courtyard 66.535–82.325 × 10.91–28.70 | verified; slot faces +y (board interior), see should-fix 1, 3 |
| Cited-rules DRC: 44 drill, 199 library, 2 text height, 2 text thickness; clearance/courtyard/hole/edge/silk 0 | identical: 247 findings, 0 mine-only, 0 packet-only; drill = U1 12, U5 8, U6 8, U7 8, U12 8 (0.20 mm thermal vias); unconnected 499; parity 0 | verified |
| Silk pre-pass: 12 refs hidden, 13 graphics to Fab | exactly those 12 refs and 13 graphics, base-seed → inputs/seed | verified (note 9 on the 282 total) |
| Silk gate refusal: 12 silk_overlap + 16 silk_over_copper | `failure.json` says so; not re-run | read only |
| GNSS RF path unchanged from iteration 3 | numbers identical to iteration-3 review finding 1 | verified |
| "Packer native DRC vs seed: no added findings" | comparison file empty; native run carries 18 pre-existing intra-footprint clearance findings (note 10) | verified, incomplete wording |
| Routing diagnostic under `../../routing-diagnostic/iteration-5/` | not checked | not verified |

## Method

- `check.py`: `pcbnew.LoadBoard`; `GetBoardPolygonOutlines(poly, False)` for the outline;
  `fp.GetCourtyard(F_CrtYd/B_CrtYd)` for courtyards; exact polygon distance by
  `BooleanIntersection` area test plus vertex-to-segment minimum over both outlines; bbox prefilter
  at 0.25 and 0.60 mm; opposite-side and obstacle intersections by `BooleanIntersection` area;
  obligations by pad centre over `electrical-locality.json` with net and side check; J3 pad,
  Fab-graphic and corridor inventory; RF net membership and corridor; seed comparison; text and
  silk census; judgment-group replication.
- `check2.py`: raw courtyard vertex extents and stroke width vs declared overhangs; base/seed/
  candidate text visibility and silk-graphic counts; card-region and approach-region footprint
  intersections; U1 PTH vs J3 courtyard.
- `check3.py`: base-seed → inputs/seed delta (visibility, silk/fab counts, poses, locks); SD
  net pad spans U1 ↔ J3 and pull-up/bypass spans; IMU neighbour list by package.
- DRC: `cp candidate.kicad_pcb drc/telemetry-pod.kicad_pcb; cp board-setup.kicad_pro
  drc/telemetry-pod.kicad_pro; cp telemetry-pod.kicad_dru drc/; kicad-cli pcb drc --severity-all
  --all-track-errors --schematic-parity --format json`; set comparison on (type, description,
  item uuids/descriptions) against `evidence/cited-rules-drc-committed-board.json`.
- Router: `kicad-route blocked --board candidate.kicad_pcb --out route/out --top 15` and `--json`;
  hard-blocked connections filtered on `best_layer_hard_count > 0`.
