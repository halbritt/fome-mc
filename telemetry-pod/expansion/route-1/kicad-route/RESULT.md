# Routing attempt: builtin on project

- Backend: builtin 0.23.1 (owned-89a2efbf5305)
- Input: `telemetry-pod.kicad_pcb` from working tree @ None (fingerprint e65e8d96a835407c)
- Scope: all, 235 nets; protect: existing; budget 1500 s
- Candidate: `out/runs/project/route-1/20261023T065308.671261Z/candidate/project/telemetry-pod.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 407.572 s |
| routing | INCOMPLETE | 78 unconnected in scope, 78 total (input: 499) |
| validation | FAIL | 61 new DRC violations: via_dangling 34, track_dangling 27 |

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
| net_completion | PASS |
| pour_integrity | PASS |

Native DRC (original rules and severities):

```json
{
 "violations_total": 141,
 "parity_total": 0,
 "new_violations": {
  "count": 61,
  "by_type": {
   "via_dangling": 34,
   "track_dangling": 27
  },
  "by_severity": {
   "warning": 61
  }
 },
 "preexisting_violations": 80,
 "resolved_violations": 0,
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

Blocked by (heuristic straight/L corridors, not a proof; details `out/runs/project/route-1/20261023T065308.671261Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| keepout 'D-PCB-7v2-In1-no-tracks' (no tracks) on In1.Cu | keepout | 51 | 78 |
| footprint J1 pads 19, 20, 21, 22, 10, 11 +11 more (/POD_AUX3_SIGNAL, /POD_AUX4_SIGNAL, /POD_5V_AUX +9 more) | footprint | 7 | 7 |
| footprint U6 pads 9, 9''''', 9'''''', 9''''''', 9'''''''', 6 +10 more (/GND, unconnected-(U6-NC-Pad7), /PRE_6V3 +2 more) | footprint | 5 | 10 |
| via /SD_CLK (new, unlocked) c96d0d9e | new_copper | 5 | 5 |
| footprint U1 pads 41', 41'''', 41'''''', 41''''''', 41'''''''''', 41'''''''''''' +30 more (/GND, /TIRE_CAN_CS, /IMU_INT1 +21 more) | footprint | 4 | 18 |
| keepout 'D-PCB-6-RF-reference' (no tracks, no vias) on In1.Cu, In2.Cu | keepout | 4 | 6 |
| via /TIRE_CAN_INT_N (new, unlocked) 4cb26db9 | new_copper | 4 | 6 |
| via /PRE_6V3 (new, unlocked) 87fe860f | new_copper | 4 | 5 |
| via /ADC_AIN7 (new, unlocked) 8eb41072 | new_copper | 3 | 5 |
| footprint U12 pads 9'', 9''', 9''''''', 9, 9''''', 9' +2 more (/GND) | footprint | 3 | 5 |

- `/+3V3`: 1 open; best layer F.Cu with 0 hard blockers
- `/ADC_AIN4`: 1 open; best layer In1.Cu with 8 hard blockers (via /+3V3 5a7b3a9b, via /+3V3 e034c21f, via /GND 52fca7fc, via /MCU_EN 41d2ab00, via /SPI_MOSI a2678ba8)
- `/ADC_AIN7`: 1 open; best layer In1.Cu with 8 hard blockers (via /+3V3 fca18a4b, via /GND 2ba981db, via /GND fd4faa72, via /SD_CLK c96d0d9e, via /DIAG_U27_AIN2 8c1fcf00)
- `/AFE_BUF3`: 1 open; best layer In1.Cu with 14 hard blockers (via /+3V3 2da996ce, via /GND 5ed74b9c, via /GND aa1c3b5a, via /PRE_6V3 6e0c7eed, via /PRE_6V3 f0711e35)
- `/AFE_BUF7`: 1 open; best layer In1.Cu with 17 hard blockers (via /GND 0181102a, via /PRE_6V3 6f64066f, via /PRE_6V3 86af45db, via /SUP_U19_SENSE e303eaa0, via /SETPOINT_5V a94cca75)
- `/AFE_DIV0`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7v2-In1-no-tracks')
- `/AFE_DIV5`: 1 open; best layer In1.Cu with 1 hard blockers (keepout 'D-PCB-7v2-In1-no-tracks')
- `/AFE_DIV6`: 1 open; best layer In1.Cu with 4 hard blockers (via /GND b2e5b46d, via /SD_CLK c96d0d9e, via /SD_DAT1 976ac82a, keepout 'D-PCB-7v2-In1-no-tracks')
- `/AFE_DIV7`: 1 open; best layer In1.Cu with 5 hard blockers (via /GND bed42dd7, via /AFE_DIV4 823ef923, via /AFE_BUF5 1c7c079c, via /SD_CLK c96d0d9e, keepout 'D-PCB-7v2-In1-no-tracks')
- `/DIAG_I2C_SCL`: 1 open; best layer B.Cu with 0 hard blockers
- `/DIAG_U27_AIN2`: 1 open; best layer In1.Cu with 15 hard blockers (via /+3V3 2405ba57, via /GND 58efd7cb, via /TIRE_CAN_TX c67fc1c6, via /TIRE_CAN_TX eb9eee48, via /TIRE_CAN_RX 014ac080)
- `/DIAG_U28_AIN1`: 1 open; best layer In1.Cu with 11 hard blockers (via /GND a7636e79, via /ADC_AIN1 34387625, via /THERM_BIAS_IN 240d9a77, via /POD_5V_SENSOR 4ab20ffb, via /POD_AUX2_SIGNAL 605310d8)
- `/DIAG_U28_AIN2_UPPER1`: 1 open; best layer In1.Cu with 21 hard blockers (via /+3V3 0f18e895, via /+3V3 5e5738d7, via /GND 1335568d, via /GND cc8f3f15, via /SD_DAT0 5177aafa)
- `/DIAG_U28_AIN2_UPPER2`: 1 open; best layer In1.Cu with 15 hard blockers (via /+3V3 56cda127, via /+3V3 76fc2d4a, via /GND 227988e6, via /GND 3e4f203d, via /GND cc8f3f15)
- `/DIAG_U29_AIN1`: 1 open; best layer In1.Cu with 9 hard blockers (via /DIAG_I2C_SCL 9a4295d2, via /DIAG_U27_AIN1 e6d6ab61, via /TIRE_CAN_OSC1 045618ed, via /MCU_EN 5e0191f3, via /MCU_EN 92d0fad5)
- `/GND`: 29 open; best layer In1.Cu with 2 hard blockers (via /POD_12V_PROTECTED 44e65acd, via /PRE_6V3 4505d775, keepout 'D-PCB-7v2-In1-no-tracks', via /WHEEL_FRONT_OUT caf036e5, via /POD_CAN_P cc0d9153)
- `/IMU_CS`: 2 open; best layer In1.Cu with 6 hard blockers (via /TWAI_RX f08c1b70, via /DIAG_U27_AIN1_UPPER2 49eef282, via /GNSS_PPS 424fdc3f, via /GNSS_LNA_EN 48cab06e, footprint U1)
- `/POD_5V_SENSOR`: 1 open; best layer In1.Cu with 13 hard blockers (via /GND 0b263272, via /SUP_U16_SENSE 5ce5c539, via /THERM_EXC_2V495 be976b0b, via /SUP_U16_CT 8aed29a3, via /SENSOR_POWER_AUX_ILIM 872b06ed)
- `/POD_AUX3_SIGNAL`: 1 open; best layer In1.Cu with 14 hard blockers (via /GND 453982e2, via /GND cea19363, via /TIRE_CAN_TX c67fc1c6, via /POD_WHEEL_FRONT_SUPPLY 6c14441f, via /DIAG_I2C_SDA da9beb13)
- `/POD_AUX4_SIGNAL`: 1 open; best layer In1.Cu with 7 hard blockers (via /GND 0b263272, via /GND 8b83bf9d, via /DIAG_U29_AIN1 3e0490ca, via /SUP_U18_SENSE eeb93f48, footprint J2)
- … 28 more nets in the report
- 22 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 5889,
 "new_vias": 686,
 "new_track_length_mm": 7523.41,
 "new_track_length_mm_by_layer": {
  "B.Cu": 2276.996,
  "F.Cu": 2891.397,
  "In2.Cu": 2355.017
 },
 "new_copper_nets": 181,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
