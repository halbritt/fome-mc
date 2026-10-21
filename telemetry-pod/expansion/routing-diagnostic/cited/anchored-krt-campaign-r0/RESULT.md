# Routing attempt: krt on cited

- Backend: krt 0.23.1 (owned-c6c09054f684)
- Input: `ca.kicad_pcb` from working tree @ None (fingerprint 3d5ceaac81f0bdad)
- Scope: all, 369 nets; protect: existing; budget 900 s
- Candidate: `/home/halbritt/.cache/agent499-cluster-anchored/route/runs/cited/anchored-krt-campaign-r0/20261021T004744.523709Z/candidate/cited/ca.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 330.576 s |
| routing | INCOMPLETE | 89 unconnected in scope, 89 total (input: 499) |
| validation | FAIL | 1 new DRC violations: track_dangling 1; preservation net_completion: 31 of the 312 nets fully connected in the input lost connection: /ADC_AIN3, /ADC_AIN5, /ADC_AIN6, /AFE_DIV3, /AFE_DIV4, /DIAG_I2C_SCL, /DIAG_I2C_SDA, /DIAG_U29_AIN0, /DIAG_U29_AIN1, /EMMC_CLK |

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
 "violations_total": 90,
 "parity_total": 0,
 "new_violations": {
  "count": 1,
  "by_type": {
   "track_dangling": 1
  },
  "by_severity": {
   "warning": 1
  }
 },
 "preexisting_violations": 89,
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

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-cluster-anchored/route/runs/cited/anchored-krt-campaign-r0/20261021T004744.523709Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| track /DIAG_U28_AIN2 In2.Cu (new, unlocked) 562503ab | new_copper | 7 | 10 |
| track /SENSOR_POWER_FRONT_RTN In2.Cu (new, unlocked) aa6234a1 | new_copper | 5 | 6 |
| track /TWAI_RX In2.Cu (new, unlocked) caffd41a | new_copper | 4 | 9 |
| track /EMMC_DAT1 In1.Cu (new, unlocked) 3f3e47a8 | new_copper | 4 | 6 |
| track /SETPOINT_5V In2.Cu (new, unlocked) d5edf96b | new_copper | 4 | 5 |
| track /TIRE_CAN_TX_ENABLE In2.Cu (new, unlocked) e8dd58e7 | new_copper | 3 | 6 |
| track /AFE_BUF3 In1.Cu (new, unlocked) 18c210b4 | new_copper | 3 | 5 |
| track /DIAG_U28_AIN0 In1.Cu (new, unlocked) d2264b62 | new_copper | 3 | 5 |
| track /TIRE_CAN_INT_N In2.Cu (new, unlocked) 8ca82de0 | new_copper | 3 | 5 |
| track /EMMC_DS In2.Cu (new, unlocked) f199c6fd | new_copper | 3 | 4 |

- `/+3V3`: 9 open; best layer F.Cu with 1 hard blockers (track /TIRE_CAN_TX_ENABLE F.Cu 7c1be652)
- `/ADC_AIN3`: 1 open; best layer In1.Cu with 9 hard blockers (track /+3V3 In1.Cu f119e6e4, track /TWAI_TX In1.Cu df876a48, track /DIAG_I2C_SDA In1.Cu 1f428dad, track /EMMC_DAT1 In1.Cu 1923e148, track /REF_DIV In1.Cu 6650a8c9)
- `/ADC_AIN5`: 1 open; best layer In1.Cu with 2 hard blockers (track /TWAI_TX In1.Cu 3bc5c57b, via /ADC_AIN7 04b0429c)
- `/ADC_AIN6`: 1 open; best layer In2.Cu with 17 hard blockers (track /GND In2.Cu 329eee55, track /GND In2.Cu 3de24d0b, track /POD_GNSS_RF In2.Cu b311de89, track /POD_GNSS_RF In2.Cu d775b882, track /DIAG_U28_AIN2 In2.Cu 4c06f50e)
- `/AFE_DIV3`: 1 open; best layer In2.Cu with 10 hard blockers (track /+3V3 In2.Cu 1d5d85a6, track /+3V3 In2.Cu 6d71ec58, track /+3V3 In2.Cu ac47e9ec, track /EMMC_DAT1 In2.Cu fe2943e3, track /EMMC_DS In2.Cu f199c6fd)
- `/AFE_DIV4`: 1 open; best layer B.Cu with 1 hard blockers (track /AFE_BUF5 B.Cu 8c967396)
- `/DIAG_I2C_SCL`: 1 open; best layer In1.Cu with 3 hard blockers (track /MCU_BOOT46 In1.Cu 768955fb, track /ADC_CS In1.Cu 3581df85, track /SENSOR_FAULT_N In1.Cu c70b798c)
- `/DIAG_I2C_SDA`: 1 open; best layer F.Cu with 6 hard blockers (track /+3V3 F.Cu 2aa6ffcb, track /ADC_CS F.Cu 4e2d5434, track /TIRE_CAN_GPIO1 F.Cu 4a202ec0, footprint R29, footprint R32)
- `/DIAG_U28_AIN2`: 1 open; best layer F.Cu with 2 hard blockers (track /GNSS_LNA_EN F.Cu 826e793d, track /POD_REAR_SHOCK_SIGNAL F.Cu a80b912d)
- `/DIAG_U29_AIN0`: 2 open; best layer In2.Cu with 13 hard blockers (track /DIAG_U27_AIN2 In1.Cu 977905cd, track /+5V_CAN In2.Cu 40c4967b, track /POD_GNSS_RF In2.Cu b311de89, track /POD_GNSS_RF In2.Cu ff9b4bfa, track /SETPOINT_5V In2.Cu 5fc7d37f)
- `/DIAG_U29_AIN1`: 1 open; best layer B.Cu with 2 hard blockers (via /GND 1afe5576, footprint U29)
- `/EMMC_CLK`: 1 open; best layer In2.Cu with 20 hard blockers (track /+3V3 In2.Cu 4100082f, track /+3V3 In2.Cu 4fb3a21c, track /+3V3 In2.Cu 6d71ec58, track /+3V3 In2.Cu db0dc374, track /TWAI_RX In2.Cu 5a489e35)
- `/EMMC_CMD`: 2 open; best layer In1.Cu with 19 hard blockers (via /+3V3 c2068228, track /GND In1.Cu 4103b30e, track /GND In1.Cu ecfc6355, track /GND In1.Cu f9ffd86b, track /TWAI_TX In1.Cu d217589c)
- `/EMMC_DAT3`: 1 open; best layer In1.Cu with 16 hard blockers (track /GNSS_RX_IN In1.Cu b8262475, track /POWER_FAIL_N In1.Cu f99979a2, track /EMMC_DAT0 In1.Cu 0249e4f1, track /EMMC_DAT0 In1.Cu 8fc1f800, track /EMMC_DAT1 In1.Cu 3f3e47a8)
- `/EMMC_DAT4`: 1 open; best layer In1.Cu with 3 hard blockers (track /EMMC_DAT0 In1.Cu 0249e4f1, via /EMMC_DAT0 0d2fc9c5, via /AFE_DIV0 53cbda65)
- `/EMMC_DAT5`: 1 open; best layer In2.Cu with 7 hard blockers (track /SETPOINT_5V In2.Cu 5a56e37b, track /SETPOINT_5V In2.Cu d5edf96b, track /DIAG_U28_AIN3 In2.Cu 612f170b, track /AFE_DIV2 In2.Cu c2d4945d, via /GND 8846ce83)
- `/EMMC_DAT6`: 1 open; best layer In1.Cu with 5 hard blockers (track /POD_GNSS_RF In1.Cu 3e67c8c0, track /DIAG_U27_AIN1 In1.Cu 5bd3df2a, track /AFE_DIV2 In1.Cu 075e1d9c, via /DIAG_U28_AIN3 0276b940, via /AFE_DIV2 6e615666)
- `/EMMC_DAT7`: 1 open; best layer In2.Cu with 3 hard blockers (track /EMMC_DS In2.Cu f199c6fd, via /GND 7815e14f, via /EMMC_DS 7de99629)
- `/EMMC_VCC_3V3`: 3 open; best layer In1.Cu with 1 hard blockers (track /WHEEL_REAR_CAPTURE In1.Cu aaff117c)
- `/EMMC_VDDi`: 1 open; best layer In2.Cu with 3 hard blockers (track /SETPOINT_5V In2.Cu 5a56e37b, track /DIAG_U28_AIN3 In2.Cu 612f170b, via /SETPOINT_5V 5a87a6f0)
- … 29 more nets in the report
- 32 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 4352,
 "new_vias": 381,
 "new_track_length_mm": 5310.41,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1637.553,
  "F.Cu": 1724.02,
  "In1.Cu": 1160.222,
  "In2.Cu": 788.615
 },
 "new_copper_nets": 173,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
