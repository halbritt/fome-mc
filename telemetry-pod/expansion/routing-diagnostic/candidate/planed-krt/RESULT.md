# Routing attempt: krt on candidate

- Backend: krt 0.23.1 (owned-c6c09054f684)
- Input: `ca.kicad_pcb` from working tree @ None (fingerprint 3f45347d883609c0)
- Scope: all, 369 nets; protect: existing; budget 1500 s
- Candidate: `/home/halbritt/.cache/agent499-cluster-anchored/iter2/route/runs/candidate/planed-krt/20261021T013127.040753Z/candidate/candidate/ca.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1370.917 s |
| routing | INCOMPLETE | 92 unconnected in scope, 92 total (input: 499) |
| validation | FAIL | 6 new DRC violations: track_dangling 6; preservation net_completion: 32 of the 305 nets fully connected in the input lost connection: /ADC_AIN1, /ADC_AIN5, /ADC_AIN6, /ADC_CS, /AFE_DIV2, /AFE_DIV7, /DIAG_U27_AIN1, /DIAG_U27_AIN2, /DIAG_U28_AIN3, /DIAG_U29_AIN0 |

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
 "violations_total": 84,
 "parity_total": 0,
 "new_violations": {
  "count": 6,
  "by_type": {
   "track_dangling": 6
  },
  "by_severity": {
   "warning": 6
  }
 },
 "preexisting_violations": 78,
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

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-cluster-anchored/iter2/route/runs/candidate/planed-krt/20261021T013127.040753Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| track /ADC_AIN2 In2.Cu (new, unlocked) 5cb485eb | new_copper | 7 | 10 |
| footprint U1 pads 3, 5, 27, 6, 12, 13 +26 more (/MCU_EN, /TWAI_RX, /MCU_BOOT +17 more) | footprint | 4 | 21 |
| track /ADC_AIN2 In2.Cu (new, unlocked) 83cf7ef8 | new_copper | 4 | 5 |
| via /TIRE_CAN_SILENT (new, unlocked) ec67e8c4 | new_copper | 4 | 4 |
| track /SENSOR_POWER_TIRE_RTN In1.Cu (new, unlocked) 1cde5d99 | new_copper | 3 | 6 |
| track /SPI_MISO In2.Cu (new, unlocked) db06de3f | new_copper | 3 | 5 |
| track /POD_FRONT_BRAKE_SIGNAL In2.Cu (new, unlocked) 432f1cac | new_copper | 3 | 4 |
| track /POWER_FAIL_N In2.Cu (new, unlocked) efa91878 | new_copper | 3 | 4 |
| track /SPI_MISO In2.Cu (new, unlocked) a81db0e7 | new_copper | 3 | 3 |
| via /DIAG_U29_AIN0_UPPER1 (new, unlocked) aed5eb2e | new_copper | 3 | 3 |

- `/+3V3`: 3 open; best layer In2.Cu with 0 hard blockers
- `/ADC_AIN1`: 1 open; best layer In1.Cu with 7 hard blockers (track /TIRE_CAN_TX In1.Cu 04dbcc88, track /TWAI_TX In1.Cu 1c2df701, track /TIRE_CAN_TX_ENABLE In1.Cu 50472aae, track /TIRE_CAN_TX_ENABLE In1.Cu 83a7600f, track /TIRE_CAN_TX_ENABLE In1.Cu 97ea18b3)
- `/ADC_AIN5`: 2 open; best layer In1.Cu with 6 hard blockers (track /GND In1.Cu 0220968f, track /IMU_CS In1.Cu 2c290302, via /ADC_AIN3 04d0b28f, via /AFE_DIV6 96a8f52f, track /MCU_BOOT46 In1.Cu 55af8e5a)
- `/ADC_AIN6`: 1 open; best layer In1.Cu with 0 hard blockers
- `/ADC_CS`: 1 open; best layer B.Cu with 1 hard blockers (footprint U4)
- `/AFE_DIV2`: 1 open; best layer In2.Cu with 0 hard blockers
- `/AFE_DIV7`: 1 open; best layer In1.Cu with 1 hard blockers (track /IMU_CS In1.Cu 2c290302)
- `/ANT_BIAS`: 1 open; best layer In1.Cu with 8 hard blockers (track /POD_12V_PROTECTED In1.Cu 2c1c7650, track /PRE_6V3 In1.Cu 6d47db27, track /TIRE_CAN_OSC1 In1.Cu 79c3a517, track /IMU_CS In1.Cu 259931f2, track /AFE_BUF2 In1.Cu fbc17a3a)
- `/DIAG_U27_AIN1`: 2 open; best layer In2.Cu with 18 hard blockers (track /+3V3 In2.Cu 50b0a4ed, track /TIRE_CAN_INT_N In2.Cu 2dc929cb, track /TIRE_CAN_INT_N In2.Cu 5aaa7376, track /TIRE_CAN_INT_N In2.Cu ef3d202f, track /SPI_MISO In2.Cu a81db0e7)
- `/DIAG_U27_AIN2`: 1 open; best layer In1.Cu with 1 hard blockers (track /TIRE_CAN_TX_ENABLE In1.Cu b995449c)
- `/DIAG_U28_AIN2`: 2 open; best layer In1.Cu with 19 hard blockers (track /GND In1.Cu 1bf4ebbe, track /TWAI_TX In1.Cu c334c917, track /MCU_BOOT46 In1.Cu a2667fda, track /TIRE_CAN_GPIO1 In1.Cu f0f1450c, track /ADC_AIN4 In1.Cu c844911d)
- `/DIAG_U28_AIN3`: 1 open; best layer In2.Cu with 24 hard blockers (track /+3V3 In2.Cu eef4c368, track /TIRE_CAN_INT_N In2.Cu ef3d202f, track /SPI_MISO In2.Cu 6bc1c2f7, track /SPI_MISO In2.Cu a81db0e7, track /SPI_MISO In2.Cu c45f5f4d)
- `/DIAG_U29_AIN0`: 2 open; best layer In2.Cu with 20 hard blockers (track /GND In2.Cu da4b698b, track /SETPOINT_5V In2.Cu a610fe78, track /SENSOR_FAULT_N In2.Cu 0feb84af, track /SENSOR_FAULT_N In2.Cu 1b20d3af, track /DIAG_U28_AIN1 In2.Cu bc04bcc9)
- `/DIAG_U29_AIN1`: 1 open; best layer In2.Cu with 19 hard blockers (track /GND In2.Cu ad028dec, track /TIRE_CAN_RX In2.Cu aa812eb7, track /POWER_FAIL_N In2.Cu efa91878, track /REF_DIV In2.Cu 19573e5e, track /REF_DIV In2.Cu 2856fbe6)
- `/DIAG_U29_AIN2`: 1 open; best layer In2.Cu with 11 hard blockers (track /SPI_MISO In2.Cu db06de3f, track /ADC_AIN2 In2.Cu 5cb485eb, track /ADC_AIN2 In2.Cu 83cf7ef8, via /+3V3 5372676c, via /GND 9232d7b1)
- `/EMMC_CLK`: 1 open; best layer In1.Cu with 4 hard blockers (track /EMMC_DAT1 In1.Cu c9488de1, track /EMMC_DS In1.Cu f75d06dd, via /+3V3 f9461177, via /DIAG_U28_AIN0 d7538a9a)
- `/EMMC_CMD`: 1 open; best layer In2.Cu with 4 hard blockers (track /ADC_AIN3 In2.Cu 5981bfc4, track /ADC_AIN3 In2.Cu f549b4c9, via /GND 95f4a97e, via /DIAG_I2C_SDA 1d6b0dd0)
- `/EMMC_DAT0`: 1 open; best layer In1.Cu with 3 hard blockers (track /GND In1.Cu bc900b0d, track /EMMC_DAT1 In1.Cu c9488de1, via /MCU_BOOT b56b37a8)
- `/EMMC_DAT3`: 2 open; best layer In1.Cu with 0 hard blockers
- `/EMMC_DAT4`: 1 open; best layer In2.Cu with 0 hard blockers
- … 31 more nets in the report
- 40 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 3875,
 "new_vias": 407,
 "new_track_length_mm": 4858.325,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1895.281,
  "F.Cu": 1840.388,
  "In1.Cu": 636.658,
  "In2.Cu": 485.998
 },
 "new_copper_nets": 173,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
