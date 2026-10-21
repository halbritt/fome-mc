# Routing attempt: builtin on bga-exp

- Backend: builtin 0.23.1 (owned-c6c09054f684)
- Input: `bg2.kicad_pcb` from working tree @ None (fingerprint 84717eabe7786f42)
- Scope: all, 369 nets; protect: existing; budget 1800 s
- Candidate: `/home/halbritt/.cache/agent499-cluster-anchored/iter3/route/runs/bga-exp/bg2-full-nofinalize/20261021T025837.918103Z/candidate/bga-exp/bg2.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1801.358 s |
| routing | INCOMPLETE | 168 unconnected in scope, 168 total (input: 499) |
| validation | FAIL | 77 new DRC violations: items_not_allowed 64, track_dangling 12, via_dangling 1; preservation net_completion: 46 of the 303 nets fully connected in the input lost connection: /ADC_AIN1, /ADC_AIN2, /ADC_AIN3, /ADC_AIN7, /AFE_BUF3, /AFE_BUF4, /AFE_DIV1, /AFE_DIV5, /AFE_DIV6, /DIAG_I2C_SCL; preservation pour_integrity: 4 copper zones, 77 zone-connected pads compared on the refilled boards (min spokes 2); /+3V3@In2.Cu 5109.7 mm2 (-5.532 %), 1 polygons; /EMMC_VCC_3V3@B.Cu 108.7 mm2 (+879.531 %), 3 polygons, 13.7 mm2 off the main pour; /GND@B.Cu 1.9 mm2 (-98.799 %), 15 polygons, 1.3 mm2 off the main pour; /GND@In1.Cu 5186.2 mm2 (-4.648 %), 1 polygons; 4 isolated_island |

| Preservation check | Status |
|---|---|
| project_files | PASS |
| board_outline | PASS |
| layers | PASS |
| stackup | PASS |
| board_setup | PASS |
| nets_and_netclasses | PASS |
| pad_connectivity | PASS |
| footprints | PASS |
| zones | PASS |
| keepouts | PASS |
| copper_graphics | PASS |
| protected_copper | PASS |
| new_copper_netclass_geometry | PASS |
| routing_scope | PASS |
| net_completion | FAIL |
| pour_integrity | FAIL |

Native DRC (original rules and severities):

```json
{
 "violations_total": 185,
 "parity_total": 0,
 "new_violations": {
  "count": 77,
  "by_type": {
   "items_not_allowed": 64,
   "track_dangling": 12,
   "via_dangling": 1
  },
  "by_severity": {
   "error": 64,
   "warning": 13
  }
 },
 "preexisting_violations": 108,
 "resolved_violations": 13,
 "new_parity": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
 },
 "resolved_parity": 0
}
```

Unsupported or approximated by this backend:

- KRT reads only a subset of .kicad_dru custom rules; every rule is still graded by KiCad DRC
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class
- backend reported: .kicad_dru: rule 'fine-pitch intra-footprint pad clearance (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U16 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U17 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U18 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U19 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-cluster-anchored/iter3/route/runs/bga-exp/bg2-full-nofinalize/20261021T025837.918103Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| keepout 'D-PCB-7 plane layers no tracks' (no tracks) on In1.Cu, In2.Cu | keepout | 120 | 168 |
| via /+3V3 (new, unlocked) 3f6df146 | new_copper | 5 | 7 |
| footprint U5 pads 1, 8, 9, 9'''', 9''''', 7 +7 more (/GND, /SW_PRE, /BOOT_PRE +1 more) | footprint | 5 | 6 |
| footprint U12 pads 2, 3, 9''', 9'''', 9'''''''', 9 +11 more (unconnected-(U12-NC-Pad2), /GND, unconnected-(U12-NC-Pad7) +3 more) | footprint | 4 | 15 |
| footprint J1 pads 11, 23, 22, 6, 10, 9 +5 more (/POD_5V_SENSOR, /POD_WHEEL_FRONT_SUPPLY, /GND +5 more) | footprint | 3 | 6 |
| via /AFE_BUF1 (new, unlocked) 0db9a02a | new_copper | 3 | 5 |
| via /TIRE_CAN_CS (new, unlocked) 16cdb930 | new_copper | 3 | 3 |
| footprint U3 pads 11, 22, 21, 18, 7, 15 +8 more (/POD_GNSS_RF, /+3V3, /GNSS_RX_IN +7 more) | footprint | 2 | 12 |
| via /POD_FRONT_BRAKE_SIGNAL (new, unlocked) 6fa3e594 | new_copper | 2 | 4 |
| via /GND (new, unlocked) 426c82ab | new_copper | 2 | 3 |

- `/+3V3`: 24 open; best layer In2.Cu with 1 hard blockers (keepout 'D-PCB-7 plane layers no tracks', track /TIRE_CAN_TX F.Cu 2e245d98, footprint U20, track /GNSS_ANT_FAULT_N F.Cu 0a5ebe66)
- `/+5V_CAN`: 2 open; best layer B.Cu with 1 hard blockers (track /AFE_BUF1 B.Cu 34c6953c, track /TIRE_CAN_RX F.Cu 962fef7e)
- `/ADC_AIN1`: 1 open; best layer In2.Cu with 3 hard blockers (via /GND 96a31bf2, via /REF_DIV 7e862736, keepout 'D-PCB-7 plane layers no tracks')
- `/ADC_AIN2`: 2 open; best layer In1.Cu with 2 hard blockers (via /GND 5b32ff1e, keepout 'D-PCB-7 plane layers no tracks')
- `/ADC_AIN3`: 2 open; best layer In1.Cu with 2 hard blockers (via /GND 5b32ff1e, keepout 'D-PCB-7 plane layers no tracks')
- `/ADC_AIN7`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 plane layers no tracks')
- `/AFE_BUF3`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 plane layers no tracks')
- `/AFE_BUF4`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 plane layers no tracks')
- `/AFE_DIV1`: 2 open; best layer B.Cu with 1 hard blockers (track /AFE_BUF0 B.Cu c8f4892c, track /AFE_DIV2 B.Cu da6cf58a)
- `/AFE_DIV5`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 plane layers no tracks')
- `/AFE_DIV6`: 2 open; best layer B.Cu with 1 hard blockers (track /AFE_DIV5 B.Cu 61fb0bf4, track /AFE_BUF7 B.Cu 8b49e53e)
- `/DIAG_I2C_SCL`: 3 open; best layer In1.Cu with 2 hard blockers (via /+3V3 3f6df146, keepout 'D-PCB-7 plane layers no tracks', via /ADC_CS 4756b614)
- `/DIAG_I2C_SDA`: 3 open; best layer In1.Cu with 2 hard blockers (via /+3V3 3f6df146, keepout 'D-PCB-7 plane layers no tracks', via /GNSS_TX_OUT a531d8dd)
- `/DIAG_U27_AIN0`: 2 open; best layer In1.Cu with 3 hard blockers (via /GND a6cce617, via /MCU_BOOT46 be340755, keepout 'D-PCB-7 plane layers no tracks', via /+3V3 3f6df146)
- `/DIAG_U27_AIN1`: 2 open; best layer In1.Cu with 4 hard blockers (via /TIRE_CAN_TX 4bea2533, via /SETPOINT_5V 6951eb3e, via /FB_PRE_SERIES 42ef1ebe, keepout 'D-PCB-7 plane layers no tracks', via /+3V3 3f6df146)
- `/DIAG_U27_AIN2`: 1 open; best layer In1.Cu with 5 hard blockers (via /GND 2c76e8de, via /GND fd5d152c, footprint U5, keepout 'D-PCB-7 plane layers no tracks')
- `/DIAG_U28_AIN0`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 plane layers no tracks')
- `/DIAG_U28_AIN2`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 plane layers no tracks')
- `/DIAG_U29_AIN0`: 2 open; best layer In1.Cu with 6 hard blockers (via /TIRE_CAN_CS 16cdb930, via /GNSS_RX_IN 272e6eeb, via /GNSS_TX_OUT 864fe407, via /DIAG_U28_AIN1_UPPER2 a323a653, via /DIAG_U27_AIN1 0ca285d7)
- `/DIAG_U29_AIN1`: 1 open; best layer In2.Cu with 6 hard blockers (via /GND 2c76e8de, via /GND fd5d152c, via /TIRE_CAN_CS 16cdb930, via /DIAG_U27_AIN1 0ca285d7, via /DIAG_U27_AIN2 12f59325)
- … 60 more nets in the report
- 26 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 4335,
 "new_vias": 344,
 "new_track_length_mm": 4362.666,
 "new_track_length_mm_by_layer": {
  "B.Cu": 2117.575,
  "F.Cu": 2241.268,
  "In1.Cu": 1.976,
  "In2.Cu": 1.847
 },
 "new_copper_nets": 177,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
