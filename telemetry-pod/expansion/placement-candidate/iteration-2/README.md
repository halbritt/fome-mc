# Placement candidate, iteration 2 (pending independent review; not adopted)

Same method as iteration 1 (regulator clusters placed by construction, the rest by the
released origin-group packer, agent-ee main `39a6b626…`), with the review's defects fixed in
`inputs/anchor2.py`:

- cluster placement checks clearance on **both** sides: no cluster part within 4 mm of the
  IMU U2 on either side, no cluster stacked through the board on a fixed part, another
  cluster or an inductor;
- packer obstacles: a through-board exclusion under U2 on B, a 4 mm ring around U2 on F
  (four separate strips; touching contours are refused by the policy validator), and the
  opposite-side shadow of each inductor L1, L2, L4 (+0.5 mm);
- J2 anchor moved 0.20 mm inboard to x = 85.24 (D-PCB-4): the edge-launch SMA's fab datum
  now coincides with the board edge and its pads sit 0.50 mm from it;
- GNSS module U3 fixed at (71.5, 31.0) F, rotation 180, so its RF pad faces J2 across a
  4.7 mm corridor (RF pad to connector pin 9.9 mm) with the ESP32 antenna keep-out above;
  groups `gnss-rf-bias-tee` (L3 within 12 mm of U3) and `gnss-antenna-power` (U10 within
  15 mm).

Cluster origins (mm): U5 (29, 14) F, U7 (36, 29) F, U15 (52, 26) B, U26 (8, 21) F. The seed
(`inputs/seed.kicad_pcb.gz`) re-measured with pcbnew: 33 pairs, 0 failures. Two refused
attempts preceded this run (touching obstacle contours; C1 0.22 mm from an obstacle) and
one search exhaustion (U10 could not fit within 9 mm of U3 against the SMA and the
antenna keep-out), which is why U3 moved and the GNSS radii widened.

## Checks on the candidate (board SHA256 `4c607898…848c51`)

| Check | Result |
| --- | --- |
| Packer (`evidence/placement-*.json`) | placed, 1429 s, 25 440 steps, 2 backjumps, judgment pass, groups pass, 331 of 331, 162 F / 169 B |
| Pad obligations rev 2, independent `measure.py` | 33 pass, 0 exceed, 0 unknown |
| Native DRC, scaffold project (`evidence/native-drc.json`) | 320: 44 drill + 20 clearance (default-rule findings closed by D-PCB-1), 57 silk, 199 library |
| Native DRC, cited project, on a copy with thermal vias patched to 0.30/0.70 (`evidence/cited-rules-drc-via-patched-copy.json`) | 256: 199 library, 57 silk; **no clearance, drill, courtyard, hole or copper-edge finding** |
| Distance of L1/L2/L4/U5/U7/U15 to the IMU courtyard (pcbnew) | 14.5 / 21.1 / 40.1 / 11.4 / 18.4 / 36.7 mm; U26 6.7 mm |
| Inductor through-board overlaps (pcbnew courtyards) | none |
| Routing readiness (`evidence/blocked-by.json`, heuristic) | 486 of 499 unobstructed |

Open: silkscreen fields (AGENTEE-320), the committed candidate still carries the unpatched
0.20 mm thermal vias of the migration footprints (patched copies live in `../../design-rules/
footprints/`), eMMC interior fan-out (D-PCB-3), planes (D-PCB-5) and routing. The RF
corridor box between U3's RF pad and J2 contains the ESD diode D3 on F and U14 below on B;
whether D3 belongs on the antenna line is for the reviewer and the schematic owner.
