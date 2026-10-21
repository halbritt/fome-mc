# Independent review: placement candidate iteration 3 (board fc28ba79…a3660e)

Reviewer: independent adversarial review worker, 2026-10-20. Packet:
`/home/halbritt/git/fome-mc/telemetry-pod/expansion/placement-candidate/iteration-3/`. Board and
seed gunzipped to `…/scratchpad/review-work/iter3/{board,seed}/`; candidate SHA256
fc28ba79ac7e87a92bbfa3be712248868d02aaee004025789982a43f69a3660e matches the README; seed
6507431735…85ad. All checks are my own pcbnew 10.0.7 code (`…/scratchpad/scripts/check.py,
exact.py, eng3.py`) under `/usr/bin/python3 -I`; DRC via `kicad-cli pcb drc --severity-all
--all-track-errors --schematic-parity` on a same-stem copy beside `design-rules/board-setup.kicad_pro`
+ `telemetry-pod.kicad_dru` (`review-work/iter3/drc/drc.json`). Nothing under `~/git` modified.

## Verdict

**May proceed to plane planning and routing as a candidate: YES.** No blocking and no
should-fix placement findings remain. Both iteration-2 should-fix items are fixed and verified
with exact polygons (findings 1–2). All first-review checks pass (finding 3). The DRC evidence
now describes the committed board under the cited project and matches my run item for item.

**Fit for adoption review after routing: yes, provided** the routed board is re-checked against
the same cited project with (i) the D-PCB-1 patched thermal-via footprints applied (the 44 drill
findings are the only non-silk native findings), (ii) the eMMC interior fan-out decided per
D-PCB-3 (via-in-pad or BGA net class) and shown to route, (iii) the GNSS line routed as a
continuous 50-ohm trace over an unbroken In1.Cu GND reference with L3/D3 tapped at the line, and
(iv) silk relocation (AGENTEE-320). None of these is a placement defect; the placement does not
need to change for them. Notes 6–9 are engineering observations for the plane/routing stage.

## Findings

1. **[fixed, verified] L3 bias tee in the RF corridor.** U3 NEO-M9N at (71.5, 35.0) F rot 180,
   locked; RF pad 11 `/POD_GNSS_RF` at (77.5, 29.1); J2 pin 1 at (86.96, 28.0); span 9.52 mm.
   L3 LQW18AN56N at (80.6, 28.6) F rot 90, locked: pad 2 (`/POD_GNSS_RF`) at (80.6, 27.812) is
   3.36 mm from U3 pad 11 and 6.36 mm from the J2 pin, 0.92 mm off the straight pad-to-pin line;
   pad 1 (`/ANT_BIAS`) at (80.6, 29.387). C42 100 nF (`/ANT_BIAS`/GND) at (80.6, 31.81) F sits
   right behind it — correct bias-tee decoupling placement. D3 PESD5V0C1BLS at (80.47, 25.97) F,
   0.26 mm from L3, on the line. RF net members are exactly U3, L3, D3, J2 (all F). The RF
   trace will need a <1 mm jog or stub to L3 pad 2, negligible at 1.575 GHz (λ/4 ≈ 27 mm in
   FR-4). Corridor box (±1.5 mm around the pad-to-pin span, x 76.0–88.46, y 26.5–30.6)
   intersects on F only L3, D3, C42 (all RF-line parts); on B: C75, U18, R181, U9, U4 — see
   note 7.

2. **[fixed, verified] U14 under the ESP32 body.** U14 LFBGA-153 at (72.5, 19.0) B rot 0,
   locked; courtyard x 65.75–79.25, y 11.51–26.50. Exact polygon intersection with F-side
   courtyards: **U1 only, 113.86 mm²**; U3 (F, courtyard y >= 26.75) 0 mm². U1's twelve thermal
   PTH pads (0.20 mm drill, 0.60 mm pad, through to B.Cu) at x 69.6–72.4, y 7.56–10.36: none
   inside U14's courtyard; nearest is 1.145 mm outside it (the y = 10.36 row); hole edge to the
   nearest U14 ball copper >= 5.17 mm; via pad copper to ball copper >= 4.97 mm (nearest balls
   P2/P3/P4/P6/P7 on the module-side row). Hole-to-hole minimum 0.25 mm and hole clearance
   0.25 mm are met by >4 mm. Same-side (B) neighbours at 0.26 mm from U14's courtyard: C63,
   C64, C65, C66 (bypass group, 0.26–0.63 mm, group radius 7.87–8.98 / 9.0 mm), R52, C75,
   U18, U4, R51 — see note 8.

3. **[pass] Full checklist.**
   - 331 footprints, 162 F / 169 B; outline 0..90 x 0..65 mm; courtyards outside the outline
     exactly J1 F, J2 F (x 82.485–99.575), U1 F — all declared; no pad outside the outline.
   - Same-side courtyard gaps by exact vertex distance on `GetCourtyard()` polygons: **0 pairs
     < 0.25 mm, 0 overlaps.** (Line-centre bbox shows C89–U26 0.01 and R113–U26 0.19, both
     inside the SOIC-8 courtyard notches; exact polygon distance >= 0.25.)
   - 33 pad pairs from pad centres: all pass, each equal to `evidence/obligations-measured.json`
     to 1e-6 mm, nets and sides correct; cluster geometry unchanged since iteration 1.
   - Fixed anchors vs `inputs/seed.kicad_pcb`: J1 (45,55.5,0,F), J2 (85.24,28,180,F locked),
     U1 (72.5,6.5,0,F), U2 (12,10,0,F), H1–H4 locked — identical. All 37 entries of
     `anchored-footprints.json` (33 cluster + J2, U3, U14, L3) match exactly; 287 moved vs seed.
   - IMU: U2 to L1/L2/L4/U5/U7/U15/U26 = 14.56 / 21.81 / 42.02 / 11.54 / 23.73 / 39.12 /
     6.81 mm (exact polygons, any side), same as iteration 2; no inductor through-board
     courtyard overlap. J2 pin 1 at anchor + 1.72, pad copper 0.50 mm from the right edge.
   - Groups (judgment file): all within radius; tightest C79 4.98/5.0, C84 4.98/5.0, C85
     2.71/3.5, U10 12.60/15.0.

4. **[pass] Cited-rules DRC on the committed board.** Mine: drill_out_of_range 44 (U1 12,
   U5 8, U7 8, U6 8, U12 8 — unpatched 0.20 mm thermal vias, D-PCB-1), silk_overlap 33,
   silk_over_copper 44, silk_edge_clearance 1, text_height 4, text_thickness 4 (U16–U19
   reference fields), lib_footprint_issues 199 = 329; **clearance 0, courtyard 0, hole 0,
   copper-edge 0**; unconnected 499; parity 0. `evidence/cited-rules-drc-committed-board.json`
   has the same 329 findings — identical item sets (0 mine-only, 0 packet-only). The
   via-patched copy's 257 (0 drill) is consistent with mine minus the 44 drills and minus
   silk/text differences attributable to the patched footprints' silk; I did not inspect the
   copy. This closes iteration-1/2 finding 6.

5. **[note] eMMC bus lengths.** Straight pad-to-ball distances U1 → U14: CLK 10.34 mm
   (U1.31 → M6), CMD 11.34 (U1.32 → M5), DAT0 16.37 (U1.33 → A3), DAT1 17.02, DAT2 17.75,
   DAT3 7.70 (U1.24 → B2). DAT4–7 and DS have no U1 end (4-bit SDMMC; DAT4–7 are U14-only
   nets — pull-ups or NC per schematic). 8–18 mm at <= 52 MHz SDMMC needs no length matching;
   the CLK/CMD/DAT0–2 pins are on U1's right edge (x = 81.25) and must pass under the module
   body on F or via In2 to reach the BGA on B — short and unobstructed on F (only U1's own
   courtyard), fine.

6. **[note] Thermal coupling ESP32 ↔ eMMC.** U14 sits under U1's body with U1's 12 ground
   vias 1.1–3.9 mm outside U14's courtyard, so the module's heat is dumped into the GND plane
   next to, not through, the BGA. WROOM TX bursts (~0.5–1 W) over a 4-layer board with a
   solid In1 GND will raise the eMMC a few °C; FEMDME008G is rated for this. Plane planning:
   keep In1.Cu solid under U14 and give U1's via field a continuous GND tie; do not slot it for
   the eMMC fan-out.

7. **[note] B side under the RF corridor.** C75 22 nF (U18 timing cap, `/SUP_U18_CT`), U18
   TPS3890 supervisor, R181 1.2 k 0.1% sense divider, U9 OPA320 reference buffer, U4 MCP3208
   ADC (U4 and U13 also lie under U3's body: U4 75.6 mm², U13 16.6 mm²). All are DC /
   low-frequency analog; with In1.Cu a solid GND plane directly under the F.Cu microstrip
   they are fully shielded from the 1.575 GHz line and do not matter. What would matter is a
   plane cut or a via fence gap under the trace, so the plane planner should treat the strip
   x 76–88, y 26.5–30.6 on In1 as untouchable, and route the supervisor/ADC signals on B.Cu
   only (no In2 traces under the line).

8. **[note] BGA escape room on B.** Nine parts sit 0.26 mm from U14's courtyard on the same
   side (C63–C66, R52, C75, U18, U4, R51); the courtyard leaves ~1 mm beyond the 11.5x13 mm
   body. The outer two ball rows escape on B.Cu between those parts; with a 0.5 mm pitch and
   0.15/0.15 rules this is routable but tight. If routing stalls on U14's edges, a 1.5 mm
   B-side moat obstacle around U14 (C63–C67 can stay within their 9 mm radius) is the first
   lever; not a defect now.

9. **[note] Packet hygiene.** No SHA256SUMS in iteration 3 (as in 2). `placement-judgment.json`
   again declares a J2 overhang on side B although J2 has only an F courtyard. `request.json`
   `gnss-rf-bias-tee` group is gone because L3 is fixed; `gnss-antenna-power` (U10 within
   15 mm of U3) is met at 12.60 mm with U10 at (64.11, 45.2) F.

## Not verified

- The via-patched copy and its project (not in the packet); only the committed-board DRC was
  reproduced.
- `evidence/blocked-by.json` heuristic; no router run; D-PCB-3 fan-out feasibility.
- Thermal and EMC quantitatively; notes 6–8 are geometric engineering judgment.
- Schematic intent for DAT4–7/DS and for D3 on the antenna line.
