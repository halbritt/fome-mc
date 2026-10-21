# Independent review: placement candidate ed6ecdb0…93d974

Reviewer: independent adversarial review worker, 2026-10-20. Packet:
`/home/halbritt/git/fome-mc/telemetry-pod/expansion/placement-candidate/`. Board gunzipped to
`/tmp/claude-1000/-home-halbritt-git-agent-ee/27167fc2-dedb-47b5-9a97-e1d328bdac8d/scratchpad/review-work/board/candidate.kicad_pcb`
(SHA256 matches the packet claim ed6ecdb0…93d974; seed matches 7f86282b…). All checks are my own
pcbnew 10.0.7 scripts under `…/scratchpad/scripts/` (check.py, exact.py, v.py, poly.py) run with
`/usr/bin/python3 -I`; none of the packet's scripts were executed.

## Verdict

**Allow to proceed to plane planning and routing as a candidate: NO, not as placed.** The
mechanical and declared-electrical checks hold (items 1–3 below all pass), but the free choice of
the U15 cluster origin put a switching regulator and its inductor directly under the fixed IMU, the
main buck inductor L1 sits 0.56 mm from the IMU and back-to-back with L4, and the packet's DRC
evidence was not produced on this board with the cited rules. Findings 4, 5 and 6 are placement
decisions that routing cannot repair; fix them (move the U15 cluster and re-pick the U5 origin,
re-run the packer) and re-review. Nothing found blocks the *approach*; the specific poses do.

## Findings

1. **[pass / note] Footprint count, sides, outline containment.** 331 footprints, 162 F / 169 B
   (README says 162 F / 169 B: agrees). Outline Edge.Cuts bbox 0..90 x 0..65 mm (4 edges).
   Courtyard polygons outside the outline: exactly J1 F (y to 87.895), J2 F (x to 99.775), U1 F
   (y to -21.295, x to 96.545) — all three in `evidence/placement-judgment.json` declared_overhangs.
   No pad of any footprint lies outside the outline. J2's declared overhang lists side B too; the
   board has J2 with an F-side courtyard only (no B courtyard polygon found) — harmless.
   Command: `check.py` (see `review-work/check-out.txt`).

2. **[pass] Same-side courtyard gaps >= 0.25 mm.** Exact vertex-to-segment distance between KiCad
   `GetCourtyard()` polygons for every same-side pair whose bboxes come within 0.26 mm: **0 pairs
   below 0.25 mm, 0 overlaps** (`exact.py`). Caution for anyone repeating this: `SHAPE_POLY_SET.BBox()`
   pads each side by 0.05 mm, so a bbox-based check reports 425 false "0.16 mm" gaps; use the
   vertices. Tightest real pairs: R113–U26 F, C68–L4 B, C97/C98–U26 F, all >= 0.25 mm. U1's
   courtyard is an 8-vertex notch shape; C127, U3, C47, U22, U10 and H2 sit inside the notch, not
   in the courtyard. Native DRC also reports no courtyard overlap (it does not test the 0.25 gap).

3. **[pass] 33 pad obligations, re-measured from pcbnew pad centres.** All 33 pairs within limit;
   every distance equals `evidence/obligations-measured.json` to 1e-6 mm; pad nets match the
   obligation nets; both pads of every pair on the same side; no ambiguous pad numbers. Tightest
   margins: U15.1→C68.2 4.820/5.0, U5.1/U7.1→C4.2/C11.2 8.123/8.5, U5.6→C4.1 3.089/3.5.
   Fixed anchors J1 (45,55.5,0,F), J2 (85.44,28,180,F), U1 (72.5,6.5,0,F), U2 (12,10,0,F),
   H1–H4 at (4,4),(86,4),(86,61),(4,61) F: identical to `inputs/seed.kicad_pcb` in position,
   rotation and side (J1/J2/U1/U2 are not flagged locked in the file; H1–H4 are). All 33
   anchored cluster footprints match `inputs/anchored-footprints.json` exactly (0 mismatches).
   290 footprints moved relative to the seed, as the README states.

4. **[blocking] eMMC buck U15 + inductor L4 placed directly under the fixed IMU U2.**
   U2 LSM6DSO32 LGA-14 at (12.0, 10.0) F, courtyard x 10.26–13.74, y 8.51–11.49. On B, U15
   TPS62162 at (10.0, 10.0) (centre 2.0 mm from U2 centre; courtyard overlap through the board
   1.24 x 2.49 mm) and L4 SRP4020 2.2 uH at (14.75, 10.25) (overlap with U2 1.84 x 2.99 mm).
   `inputs/anchor.py` chose this origin by scanning a grid and testing clearance only against
   same-side boxes (`if s!=s2: continue`), so the IMU was never considered. An IMU's analog
   supply, its reference and its temperature-sensitive gyro bias should not share a footprint
   with a 2.25 MHz converter's switch node, inductor field and heat. Fix: move the U15 cluster
   (nothing requires it on the B side under U2; the obligations are intra-cluster).

5. **[blocking] Main buck inductor L1 (15 uH SRP7050, 7x7 mm) 0.56 mm from U2 on the same side,
   and back-to-back with L4.** L1 at (18.0, 8.6) F, courtyard x 14.31–21.70, y 4.16–13.04; gap
   to U2's courtyard 0.56 mm. L1 overlaps L4 (B) through the board by 3.29 x 4.80 mm — two
   switching inductors from independent converters (U5 LMR36520 and U15 TPS62162) coupled
   through 1.6 mm of FR-4. Also under L1 on B: R140, R141, R142 (499 kohm 0.1%) and R143
   (4.99 kohm 0.1%), a high-impedance precision divider (overlaps 0.45–2.95 mm). The U5 origin
   (15,16) was the first grid cell in `anchor.py` that cleared U2 on the F side; the cluster's
   internal geometry (L1 at +3,-7.4 from U5) then placed the inductor beside the IMU. Fix: pick
   the U5 origin so L1 is >= ~5 mm from U2 (e.g. shift the U5 cluster right/down), or rotate
   the cluster so L1 faces away from U2; keep L4 and L1 from overlapping.

6. **[should-fix] Packet DRC evidence is not the candidate under the cited rules.** My run:
   `kicad-cli pcb drc --severity-all --all-track-errors --schematic-parity` on a copy of the
   candidate named `telemetry-pod.kicad_pcb` beside `design-rules/board-setup.kicad_pro` and
   `telemetry-pod.kicad_dru` (`review-work/drc/drc.json`): **drill_out_of_range 44, silk_overlap
   34, silk_over_copper 39, silk_edge_clearance 2, text_height 4, text_thickness 4,
   lib_footprint_issues 199; copper_edge_clearance 0; clearance 0; courtyard 0; hole 0;
   unconnected 499.** Packet `evidence/cited-rules-drc.json`: copper_edge 5, silk_overlap 22,
   silk_over_copper 39, silk_edge 2, lib 199, drill 0, no text findings, source `ca.kicad_pcb`.
   Two causes, both verifiable from the files:
   - The packet DRC's copper-edge messages read "edge clearance 0.5000 mm; actual 0.3000 mm",
     i.e. it ran with `candidate.kicad_pro` (scaffold defaults: edge 0.5, text 0.8/0.08, silk
     clearance 0.0), not `board-setup.kicad_pro` (edge 0.3, text 1.0/0.15, silk 0.15; `jq` diff
     of `.board.design_settings.rules`). Under the cited 0.30 mm edge rule **J2 has no
     copper-edge finding** — the README's "only copper findings are 5 J2 copper-edge" is a
     default-rule artefact, consistent with D-PCB-2's own statement that the J2 findings
     disappear. D-PCB-4 (anchor 0.20 mm outboard) may still be a seating issue; I could not
     verify it from the board.
   - The 44 drill findings are the 0.20 mm thermal vias on U1 (12), U5 (8), U7 (8), U6 (8),
     U12 (8): the candidate still carries the unpatched footprints, contrary to D-PCB-1's
     "every candidate board must be checked with this rule file and the enlarged vias" and
     "next placement run must use `footprints/`". The packet's 0-drill result came from a
     patched copy (`ca.kicad_pcb`), not this board. Not a placement defect, but the evidence
     table must be regenerated on the real candidate with the cited project, and the migration
     should carry the patched footprints before adoption.
   The extra silk/text findings (U16–U19 reference fields below 1.0 mm / 0.15 mm, 12 more silk
   overlaps) belong to AGENTEE-320.

7. **[should-fix] GNSS RF corridor U3 → J2 is filled.** U3 NEO-M9N at (55.35, 9.9) F, J2 SMA at
   (85.44, 28.0) F, ~35 mm apart, with U1's on-board body (x 62.75–82.25, y < 19.95) between
   them, so the 50-ohm line must detour below U1 at y ≈ 20–28. That strip now holds the CAN
   cluster: U22 (60.8, 20.45) F, U20 MCP2518FD (67.33, 23.9) F, Y1 20 MHz crystal (69.43,
   31.31) F, U21 TJA1051 (61.17, 31.55) F, plus R29/R68/R32/R30 on the straight line, and on B
   U29/U28 ADS1119, U4 MCP3208, C57/C59/C61 100 pF analog filters, R51. D3 (PESD, GNSS ESD) at
   (81.58, 28.05) F next to J2 is correct. `inputs/request.json` has `obstacles: []` — no RF
   keep-out was requested. Routing is not impossible, but a 35 mm RF line threaded through the
   CAN/crystal cluster is poor; reserve a corridor (obstacle) for U3→J2 before re-packing, or
   revisit the U3/J2 anchors (both fixed, so out of this packet's scope).

8. **[should-fix] Parts opposite the eMMC BGA U14 obstruct fan-out.** U14 LFBGA-153 0.5 mm at
   (48.475, 9.73) B, courtyard x 40.98–55.97, y 2.98–16.47. On F over it: C13 (22 uF, U7
   output) 3.19 x 4.59 mm overlap, C14 3.19 x 3.67, C12, C49, C51, R24, L2 (3.07 x 9.49), and
   U3 (7.77 x 13.49) and U1 (7.47 x 13.49). D-PCB-3 already says the interior balls need
   via-in-pad or a BGA net class; through-vias on a 4-layer board exit on F, where these parts
   sit. C13/C14 are locked U7-cluster parts (U7 origin 37,16 with C13–C15 at +9 mm), so the U7
   cluster abuts the BGA. Move the BGA (not fixed) or the U7 origin so U14's F side is clear.

9. **[note] Regulator clusters U5/U7/U26 internally are sound.** Input HF caps C3/C10 2.45–2.76
   mm from PGND/VIN, bootstrap caps 2.0 mm, SW-to-inductor 2.79/2.81 mm, bulk input C1/C2,
   C8/C9 6.1–6.7 mm, VCC caps 3.09 mm; output caps C6/C7, C13–C15 on the inductor side. U5 and
   U7 are 22 mm apart, U15 is 7 mm from U5, LDOs U6 (53.3, 40.9) F and U12 (55.3, 24.1) F are
   mid-board, 17 mm apart; no thermal pile-up. U26 (LM2903, 8,26 F) with C97/C98 is fine.
   U5's own B side has C68 (U15 output cap) 0.31 x 2.99 mm under it — minor.

10. **[note] ESP32 antenna.** U1's antenna courtyard wing (x 48.5–96.5, y -21.25 to -0.25) is
    entirely off-board; on-board parts nearest the top edge under that wing are C65, C73, U17,
    U16, C71, R56, R57 at y = 1.5–2.0 on B. Acceptable for an edge-overhanging antenna; keep
    copper pours off that top strip at plane planning.

11. **[note] Side split and routability.** 169 B / 162 F; 499 unconnected; parity 0. I did not
    run a router. Beyond findings 7 and 8 I saw nothing that makes routing impossible.

## Not verified

- D-PCB-4 (J2 seating 0.20 mm outboard): not measurable from the board alone.
- The packer's own courtyard-box source (line-centre vs. KiCad polygon): irrelevant to the
  verdict because the KiCad polygon gap already holds >= 0.25 mm.
- `evidence/blocked-by.json` routing-readiness heuristic: not re-run.
- Thermal and EMC quantitatively; the IMU/inductor findings are engineering judgment on
  geometry, not simulation.
