# Independent review: placement candidate iteration 2 (board 4c607898…848c51)

Reviewer: independent adversarial review worker, 2026-10-20. Packet:
`/home/halbritt/git/fome-mc/telemetry-pod/expansion/placement-candidate/iteration-2/`. Board and
seed gunzipped to `…/scratchpad/review-work/iter2/{board,seed}/`; candidate SHA256 4c607898…848c51
and seed 83d71463… match the README and `inputs/input-hashes.txt`. No SHA256SUMS file is in the
iteration-2 packet (iteration 1 had one). All checks are my own pcbnew 10.0.7 code
(`…/scratchpad/scripts/check.py, exact.py, eng2.py`) run with `/usr/bin/python3 -I`; DRC via
`kicad-cli pcb drc --severity-all --all-track-errors --schematic-parity` on a same-stem copy beside
`design-rules/board-setup.kicad_pro` + `telemetry-pod.kicad_dru` (`review-work/iter2/drc/drc.json`).
Nothing under `~/git` was modified.

## Verdict

**May proceed to plane planning and routing as a candidate (not adoption): YES, conditionally.**
Iteration-1 blockers 4 and 5 are fixed and verified with numbers (findings 1–2 below). Two
placement items should be corrected before or during the routing experiment, ideally by one more
packer run: the eMMC BGA U14 now sits directly under the locked GNSS module U3 and the RF corridor
(finding 5), and the bias-tee inductor L3 is on the wrong side of U3 for the RF line (finding 4).
Neither makes routing impossible; both make the RF/eMMC routing worse than it needs to be. The
DRC evidence file still does not describe this board under the cited project (finding 6).

## Findings

1. **[fixed, verified] IMU U2 clearance from regulators and inductors.** U2 LSM6DSO32 at
   (12.0, 10.0) F. Exact courtyard-polygon distance from U2 (any side):
   L1 F (32.0, 6.6) 14.56 mm; L2 F (39.0, 21.3) 21.81; L4 B (56.75, 26.25) 42.02; L3 F 50.81;
   U5 F (29, 14) 11.54; U7 F (36, 29) 23.73; U15 B (52, 26) 39.12; U26 F (8, 21) 6.81;
   U6 F 47.18; U12 F 38.58; nearest cluster capacitor C1 F 5.13. The README's figures (14.5 /
   21.1 / 40.1 / 11.4 / 18.4 / 36.7 / 6.7) are slightly smaller than mine for L1/L2/L4/U5/U7/U15
   (different metric, e.g. bbox or body), never larger; the claim holds either way. Nearest
   parts to U2 on any side: R135 B 3.51, R134 B 3.73, R138 B 3.76, C128 B 3.81, R114 F 3.81 mm —
   passive 0.1% divider resistors and a 10 uF cap, no switching parts; nothing is under U2 on B
   within 3.5 mm (obstacle box x 7–17, y 5–15 B honoured).

2. **[fixed, verified] Through-board overlaps involving inductors.** Polygon intersection of
   L1 (F), L2 (F), L4 (B) courtyards with every opposite-side courtyard: **none** (0 mm²). Same-side
   L1–L2 gap 5.51 mm; U5–U7 9.61 mm.

3. **[pass] Full checklist (d).**
   - 331 footprints, 162 F / 169 B. Outline 0..90 x 0..65 mm. Courtyards outside the outline:
     exactly J1 F (y to 87.895), J2 F (x 82.485–99.575), U1 F (y to -21.295, x to 96.545), all in
     `placement-judgment.json` declared_overhangs; no pad outside the outline.
   - Same-side courtyard gaps by exact vertex distance on KiCad `GetCourtyard()` polygons:
     **0 pairs < 0.25 mm, 0 overlaps**. Also 0 on line-centre bboxes.
   - 33 pad pairs re-measured from pad centres: all pass, each equal to
     `evidence/obligations-measured.json` to 1e-6 mm, nets and sides correct, no ambiguous pad
     numbers (the cluster geometry is unchanged from iteration 1; only origins moved).
   - Fixed anchors vs `inputs/seed.kicad_pcb`: J1 (45,55.5,0,F), J2 (85.24,28,180,F, locked),
     U1 (72.5,6.5,0,F), U2 (12,10,0,F), H1–H4 (4,4)/(86,4)/(86,61)/(4,61) F locked — identical.
     All 35 entries of `inputs/anchored-footprints.json` (33 cluster parts + J2 + U3) match
     exactly. 289 footprints moved vs seed.
   - Groups (from `placement-judgment.json`, not re-measured): all 15 members within radius;
     tightest C79/C80/C83 at 4.91–4.99 / 5.0 mm and L3 at 11.84 / 12.0 mm.

4. **[should-fix] L3 bias-tee inductor is 12 mm from the RF pad, on the far side of U3.**
   RF net `/POD_GNSS_RF` members: U3 pad 11 at (77.5, 25.1) F, D3, L3, J2 pad 1 at (86.96, 28.0).
   L3 LQW18AN56N (F) at (65.28, 20.93), its RF-side pad 2 at (66.07, 20.93): 12.17 mm from U3
   pad 11 and 12.17 mm from the straight RF line, on the opposite (left) side of the module
   (U3 courtyard x 64.36–78.64, y 22.75–39.24; L3 1.10 mm from the U3 courtyard, 12.35 mm from
   D3). The bias tee must tap the 50-ohm line right at the pad; here it would need a ~12 mm
   stub around/over the module. The `gnss-rf-bias-tee` radius (12 mm to U3's origin) is met at
   11.84 mm but the constraint is to the wrong reference point: anchor it to U3 pad 11 (or the
   D3 pad) with ~3 mm, or fix L3 next to the pad. U10 TPS2553 (antenna power switch) at
   (62.05, 28.65) F, 0.61 mm from U3's courtyard, is on the `/ANT_LIMITED` side and fine there.

5. **[should-fix] eMMC BGA U14 now sits under the GNSS module and the RF corridor.**
   U14 LFBGA-153 0.5 mm at (75.53, 25.44) B rot 180, courtyard x 68.78–82.28, y 17.95–32.94.
   Polygon intersection with F-side courtyards (mm²): **U3 100.37 (locked)**, U1 26.92, C44 4.28,
   C48 4.28, R31 4.28, C53 3.92, D3 2.13, R24 1.71. The RF corridor box (U3 pad 11 to J2 pin,
   ±1.5 mm) intersects exactly two courtyards: D3 (F) and U14 (B). The iteration-1 concern (F-side
   parts over the BGA block through-via fan-out, D-PCB-3) is now worse: the fan-out field would
   emerge on F under the LCC module and under the GNSS RF trace, and the 8-bit eMMC bus with
   its return vias runs under the one line on the board that needs a clean reference. U14 is
   not fixed; add an F-side obstacle under U3 and the corridor (or fix U14 elsewhere, e.g. the
   left half of the B side) and re-pack. Same-side spacing is fine: L4–U14 9.19 mm,
   U15–U14 15.29 mm, L2–U14 25.74 mm.

6. **[should-fix, evidence] Cited-rules DRC on the real candidate differs from
   `evidence/cited-rules-drc-via-patched-copy.json`.** My run on this board with
   `board-setup.kicad_pro` + `.kicad_dru`: drill_out_of_range 44 (U1 12, U5 8, U7 8, U6 8,
   U12 8 — the unpatched 0.20 mm thermal vias, as the README admits), silk_overlap 29,
   silk_over_copper 40, text_height 4, text_thickness 4 (reference fields of U16–U19),
   lib_footprint_issues 199; **clearance 0, courtyard 0, hole 0, copper_edge 0**; unconnected
   499; parity 0. Packet file: silk_overlap 17, silk_over_copper 40, lib 199, nothing else,
   source `ca.kicad_pcb`. Set-diff of silk/text findings by item: 19 present in mine and absent
   from the packet (11 silk overlaps incl. U14/C63, U15, U20/U22, Y1/R67, J1/C94, and all 8
   text findings); 0 the other way. The packet's silk descriptions do carry "silk clearance
   0.1500 mm", but the text findings only arise with the cited 1.0 / 0.15 mm minimums, so the
   copy was not checked with the full `board-setup.kicad_pro`, or the copy differs from this
   board in more than the vias. I could not inspect the copy or its project. The README's
   "no clearance, drill, courtyard, hole or copper-edge finding" is true of this board for
   clearance/courtyard/hole/copper-edge; drill is 44 until the migration carries the patched
   footprints. Not a placement defect; the evidence table should be regenerated from the
   committed board (drill findings included, annotated) rather than from an undisclosed copy.

7. **[pass] J2 anchor correction (D-PCB-4).** J2 Molex 73251-1153 at (85.24, 28.0) F rot 180
   locked (seed identical). Pin 1 `/POD_GNSS_RF` centre (86.96, 28.0) = anchor + 1.72 mm; GND
   pads at (86.96, 23.62/32.38), (83.97, …), (83.52, …). Outboard pad copper extends to
   x = 89.50, i.e. **0.500 mm from the right edge**; body/courtyard overhangs to x = 99.525. No
   copper-edge finding under the 0.30 mm cited rule. Orientation unchanged from iteration 1
   (180; only x moved by -0.20).

8. **[note] RF corridor occupants.** Between U3 pad 11 (77.5, 25.1) and J2 pin 1 (86.96, 28.0)
   (9.90 mm): D3 PESD5V0C1BLS at (79.5, 24.75) F, pads `/POD_GNSS_RF` and `/GND` — an ESD
   diode on the antenna line belongs there if the schematic keeps it (low-capacitance part;
   whether it stays is the schematic owner's call), and U14 (B) per finding 5. Nothing else on
   either side; the ESP32 antenna wing (y < -0.25) is clear of the corridor. U3 rot 180 does
   put pad 11 on the J2-facing edge.

9. **[note] Regulator/thermal layout.** U5 (29, 14) F with L1 (32, 6.6) F; U7 (36, 29) F with
   L2 (39, 21.3) F; U15 (52, 26) B with L4 (56.75, 26.25) B; LDOs U12 (50.44, 33.45) F and U6
   (53.05, 44.98) F (4.08 mm apart). U15/L4 on B sit 2.49 / 1.33 mm (opposite sides) from the
   U12 LDO thermal pad on F — three heat sources stacked within ~3 mm; acceptable for these
   power levels but plane planning should give U12/U15 separate copper. Cluster internals are
   unchanged and sound (hot-loop pairs 2.45–2.79 mm). U26 cluster at (8, 21) F is 6.8 mm from
   U2, no switching.

10. **[note] Packet hygiene.** No `SHA256SUMS` in iteration-2; `input-hashes.txt` lists
    `run.py` and `inputs/native.xml` that are not in the packet. `placement-judgment.json`
    declares a J2 overhang on side B although J2 has only an F courtyard (same as iteration 1).

## Not verified

- The via-patched copy and its project file (not in the packet); hence the cause of the
  19-finding DRC difference.
- `evidence/blocked-by.json` heuristic; no router run.
- D-PCB-4 seating beyond the 0.50 mm pad-to-edge and pin-offset numbers above.
- Thermal/EMC quantitatively; findings 4, 5 and 9 are geometric engineering judgment.
