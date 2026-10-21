# Routing attempt: builtin on bga-exp

- Backend: builtin 0.23.1 (owned-c6c09054f684)
- Input: `bg3.kicad_pcb` from working tree @ None (fingerprint 619bcf6768cb4f93)
- Scope: all, 369 nets; protect: existing; budget 1800 s
- Candidate: `/home/halbritt/.cache/agent499-cluster-anchored/iter3/route/runs/bga-exp/bg3-in2-open/20261021T033125.778272Z/candidate/bga-exp/bg3.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1190.617 s |
| routing | INCOMPLETE | 116 unconnected in scope, 116 total (input: 499) |
| validation | FAIL | 60 new DRC violations: items_not_allowed 35, track_dangling 23, via_dangling 2; preservation net_completion: 37 of the 303 nets fully connected in the input lost connection: /ADC_AIN2, /ADC_AIN3, /AFE_BUF1, /AFE_BUF5, /AFE_DIV6, /DIAG_I2C_SCL, /DIAG_I2C_SDA, /DIAG_U27_AIN0, /DIAG_U27_AIN1, /DIAG_U28_AIN1; preservation pour_integrity: 4 copper zones, 77 zone-connected pads compared on the refilled boards (min spokes 2); /+3V3@In2.Cu 4470.4 mm2 (-17.351 %), 3 polygons; /EMMC_VCC_3V3@B.Cu 138.2 mm2 (+1144.771 %), 3 polygons, 10.7 mm2 off the main pour; /GND@B.Cu 1.5 mm2 (-99.036 %), 15 polygons, 1.3 mm2 off the main pour; /GND@In1.Cu 5130.8 mm2 (-5.667 %), 1 polygons; 4 isolated_island |

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
 "violations_total": 168,
 "parity_total": 0,
 "new_violations": {
  "count": 60,
  "by_type": {
   "items_not_allowed": 35,
   "track_dangling": 23,
   "via_dangling": 2
  },
  "by_severity": {
   "error": 35,
   "warning": 25
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

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-cluster-anchored/iter3/route/runs/bga-exp/bg3-in2-open/20261021T033125.778272Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| keepout 'D-PCB-7 v2 GND plane layer no tracks' (no tracks) on In1.Cu | keepout | 67 | 116 |
| via /SUP_U19_CT (new, unlocked) cc874f30 | new_copper | 11 | 11 |
| footprint U12 pads 1, 8, 9, 9'''', 9''''', 9'' +8 more (/+5V_CAN, /PRE_6V3, /GND +2 more) | footprint | 4 | 8 |
| via /SENSOR_POWER_FRONT_RTN (new, unlocked) 4bece031 | new_copper | 3 | 6 |
| via /DIAG_U28_AIN3 (new, unlocked) f9d285af | new_copper | 3 | 5 |
| via /GND (new, unlocked) 2b7e796c | new_copper | 3 | 4 |
| via /TIRE_CAN_H (new, unlocked) 5c01f9dc | new_copper | 3 | 4 |
| via /+3V3 (new, unlocked) 61fd2305 | new_copper | 3 | 3 |
| footprint U1 pads 4, 12, 13, 14, 10, 11 +19 more (/TWAI_TX, /POWER_FAIL_N, unconnected-(U1-USB_D--Pad13) +21 more) | footprint | 2 | 17 |
| footprint U3 pads 16, 11, 19, 13, 12, 18 (unconnected-(U3-RESERVED-Pad16), /POD_GNSS_RF, unconnected-(U3-SCL{slash}SPI_CLK-Pad19) +2 more) | footprint | 2 | 7 |

- `/+3V3`: 14 open; best layer In1.Cu with 2 hard blockers (via /GNSS_ANT_FAULT_N 30bee52b, keepout 'D-PCB-7 v2 GND plane layer no tracks', track /ADC_CS In2.Cu ddfde252)
- `/ADC_AIN2`: 1 open; best layer In1.Cu with 5 hard blockers (via /+5V_CAN f1c0465c, via /TIRE_CAN_H 5c01f9dc, via /ADC_AIN1 56f0e120, via /ADC_AIN1 a16f2f72, keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/ADC_AIN3`: 1 open; best layer In1.Cu with 4 hard blockers (via /+5V_CAN f1c0465c, via /TIRE_CAN_H 5c01f9dc, via /ADC_AIN1 56f0e120, keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/AFE_BUF1`: 1 open; best layer In1.Cu with 6 hard blockers (via /+3V3 26e3e0d5, footprint U12, keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/AFE_BUF5`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/AFE_DIV6`: 2 open; best layer In1.Cu with 3 hard blockers (via /POD_5V_AUX 8dc7666a, via /AFE_DIV7 f60a49e7, keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/DIAG_I2C_SCL`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/DIAG_I2C_SDA`: 3 open; best layer In1.Cu with 2 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks', via /ADC_CS 2450ee1f)
- `/DIAG_U27_AIN0`: 2 open; best layer In1.Cu with 4 hard blockers (via /GND 9c82aee8, via /FB_PRE_SERIES f27cf402, via /TIRE_CAN_INT_N 201f6683, keepout 'D-PCB-7 v2 GND plane layer no tracks', via /+3V3 61fd2305)
- `/DIAG_U27_AIN1`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/DIAG_U28_AIN1`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/DIAG_U28_AIN2`: 1 open; best layer In1.Cu with 3 hard blockers (via /GND f67b1430, via /TIRE_CAN_CS afa8d28d, keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/DIAG_U29_AIN0`: 1 open; best layer In1.Cu with 5 hard blockers (via /GND 956a5a50, via /POWER_FAIL_N 8ee49f80, via /EMMC_VCC_3V3 ab386a27, via /ADC_AIN0 7ad26922, keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/DIAG_U29_AIN1`: 1 open; best layer In2.Cu with 0 hard blockers
- `/EMMC_CMD`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/EMMC_DAT1`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/EMMC_DAT3`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/EMMC_DAT4`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/EMMC_DAT5`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- `/EMMC_DAT6`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7 v2 GND plane layer no tracks')
- … 38 more nets in the report
- 33 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 4413,
 "new_vias": 401,
 "new_track_length_mm": 4828.658,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1957.692,
  "F.Cu": 1930.377,
  "In1.Cu": 1.365,
  "In2.Cu": 939.224
 },
 "new_copper_nets": 175,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
