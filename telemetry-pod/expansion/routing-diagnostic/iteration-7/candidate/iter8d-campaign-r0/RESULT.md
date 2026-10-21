# Routing attempt: builtin on candidate

- Backend: builtin 0.23.1 (owned-89a2efbf5305)
- Input: `ca2.kicad_pcb` from working tree @ None (fingerprint d75d2e1d150742d3)
- Scope: all, 235 nets; protect: existing; budget 900 s
- Candidate: `/home/halbritt/.cache/agent499-microsd/iter8d/route/runs/candidate/iter8d-campaign-r0/20261021T135939.841838Z/candidate/candidate/ca2.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 318.089 s |
| routing | INCOMPLETE | 55 unconnected in scope, 55 total (input: 499) |
| validation | FAIL | 1 new DRC violations: via_dangling 1; preservation net_completion: 10 of the 155 nets fully connected in the input lost connection: /AFE_BUF1, /AFE_DIV1, /DIAG_U28_AIN3, /POD_AUX3_SIGNAL, /SD_DAT1, /SD_DAT2, /SENSOR_POWER_FRONT_DVDT, /SENSOR_POWER_FRONT_ILIM, /SENSOR_POWER_REAR_ILIM, /SUP_U18_SENSE |

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
| pour_integrity | PASS |

Native DRC (original rules and severities):

```json
{
 "violations_total": 24,
 "parity_total": 0,
 "new_violations": {
  "count": 1,
  "by_type": {
   "via_dangling": 1
  },
  "by_severity": {
   "warning": 1
  }
 },
 "preexisting_violations": 23,
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

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-microsd/iter8d/route/runs/candidate/iter8d-campaign-r0/20261021T135939.841838Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| via /TIRE_CAN_TX (new, unlocked) 4514d48b | new_copper | 3 | 3 |
| track /SUP_U19_CT In2.Cu (new, unlocked) 30556dd6 | new_copper | 2 | 8 |
| track /POD_AUX2_SIGNAL In1.Cu (new, unlocked) f74a23f0 | new_copper | 2 | 5 |
| track /SPI_MISO In2.Cu (new, unlocked) 14f5cb65 | new_copper | 2 | 5 |
| track /SPI_MISO In2.Cu (new, unlocked) d971e460 | new_copper | 2 | 3 |
| track /SPI_MISO In2.Cu (new, unlocked) dacb6bc4 | new_copper | 2 | 3 |
| track /DIAG_U28_AIN1_UPPER2 In1.Cu (new, unlocked) 61512e74 | new_copper | 2 | 2 |
| track /GNSS_RX_IN In1.Cu (new, unlocked) 69d51fcc | new_copper | 2 | 2 |
| via /SPI_MOSI (new, unlocked) b66b4296 | new_copper | 2 | 2 |
| footprint U1 pads 3, 4, 17, 18, 8, 9 +17 more (/MCU_EN, /TWAI_TX, /ADC_CS +15 more) | footprint | 1 | 12 |

- `/+3V3`: 4 open; best layer In2.Cu with 1 hard blockers (via /GND 8273d977)
- `/AFE_BUF1`: 1 open; best layer In2.Cu with 1 hard blockers (via /GND 93895e5b)
- `/AFE_DIV1`: 1 open; best layer In1.Cu with 0 hard blockers
- `/DIAG_U28_AIN2`: 1 open; best layer In2.Cu with 6 hard blockers (track /DIAG_I2C_SDA In2.Cu 33fb5cc0, track /DIAG_I2C_SDA In2.Cu 58c22b11, track /ANT_LIMITED In2.Cu 1fa15a9f, via /DIAG_I2C_SDA 03fa1901, via /DIAG_I2C_SCL 0fc7e71a)
- `/DIAG_U28_AIN3`: 1 open; best layer In1.Cu with 13 hard blockers (track /TIRE_CAN_L In1.Cu 4def16cc, track /TIRE_CAN_L In1.Cu b2346d9f, track /TIRE_CAN_H In1.Cu c39ee8e2, track /POD_TIRE_SUPPLY In1.Cu fb8b7f30, track /SD_DAT0 In1.Cu 34ab89e4)
- `/GND`: 14 open; best layer F.Cu with 2 hard blockers (via /+3V3 6c541906, footprint C80)
- `/GNSS_PPS`: 1 open; best layer In1.Cu with 6 hard blockers (track /IMU_INT1 In1.Cu 9996666a, track /SENSOR_REF_2V5 In1.Cu eca76af7, track /ADC_AIN4 In1.Cu adb5178d, track /DIAG_U29_AIN2_UPPER2 In1.Cu 020d13b7, via /DIAG_U29_AIN2_UPPER2 ef936836)
- `/MCU_EN`: 4 open; best layer In2.Cu with 5 hard blockers (via /SUP_U19_CT 1de3bd57, track /SPI_MOSI In2.Cu 0636041f, track /SPI_MISO In2.Cu 29040aec, track /SUP_U19_CT In2.Cu 30556dd6, via /GND 1d8d8ca2)
- `/POD_5V_AUX`: 1 open; best layer In1.Cu with 0 hard blockers
- `/POD_AUX3_SIGNAL`: 1 open; best layer In1.Cu with 6 hard blockers (track /TIRE_CAN_H In1.Cu 041b703b, track /POD_TIRE_SUPPLY In1.Cu d966121a, track /DIAG_U28_AIN1_UPPER2 In1.Cu 61512e74, via /GND c347b52e, via /DIAG_U29_AIN0_UPPER2 d77e8ef0)
- `/POWER_FAIL_N`: 1 open; best layer In1.Cu with 0 hard blockers
- `/SD_CD`: 1 open; best layer In1.Cu with 18 hard blockers (track /GND In1.Cu f3774e66, track /PRE_6V3 In1.Cu 6acb734e, track /GNSS_RX_IN In1.Cu 69d51fcc, track /POD_AUX1_SIGNAL In1.Cu 629bafd1, track /POD_AUX2_SIGNAL In1.Cu f74a23f0)
- `/SD_CMD`: 1 open; best layer In2.Cu with 15 hard blockers (track /+3V3 In2.Cu b5df756e, track /SPI_MISO In2.Cu 14f5cb65, track /SPI_MISO In2.Cu 4ffd5811, track /SPI_MISO In2.Cu d971e460, track /WHEEL_FRONT_PULLUP In2.Cu 2af3015f)
- `/SD_DAT1`: 1 open; best layer In2.Cu with 9 hard blockers (track /SUP_U19_CT In2.Cu 30556dd6, track /SUP_U19_CT In2.Cu f3ff8ea6, via /TIRE_CAN_TX 4514d48b, via /SUP_U19_CT 76c0e13c, footprint U1)
- `/SD_DAT2`: 1 open; best layer In1.Cu with 11 hard blockers (track /+3V3 In1.Cu 6ac684be, track /GND In1.Cu 15a6c941, track /GND In1.Cu 4687083f, track /TWAI_RX In1.Cu 1ce37649, track /SD_DAT0 In1.Cu 706dc71d)
- `/SENSOR_FAULT_N`: 2 open; best layer In1.Cu with 3 hard blockers (track /MCU_BOOT In1.Cu 0e1b558b, via /IMU_INT1 dcba173e, via /SPI_MISO d11fbdb8)
- `/SENSOR_POWER_FRONT_DVDT`: 1 open; best layer B.Cu with 0 hard blockers
- `/SENSOR_POWER_FRONT_ILIM`: 1 open; best layer B.Cu with 0 hard blockers
- `/SENSOR_POWER_FRONT_OVP`: 1 open; best layer B.Cu with 0 hard blockers
- `/SENSOR_POWER_FRONT_UVLO`: 2 open; best layer B.Cu with 0 hard blockers
- … 12 more nets in the report
- 35 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 3532,
 "new_vias": 412,
 "new_track_length_mm": 4497.724,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1640.772,
  "F.Cu": 1970.922,
  "In1.Cu": 481.68,
  "In2.Cu": 404.35
 },
 "new_copper_nets": 173,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
