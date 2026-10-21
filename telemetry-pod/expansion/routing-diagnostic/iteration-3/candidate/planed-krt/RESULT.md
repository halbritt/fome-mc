# Routing attempt: krt on candidate

- Backend: krt 0.23.1 (owned-c6c09054f684)
- Input: `ca.kicad_pcb` from working tree @ None (fingerprint 5ec65f4c5b517040)
- Scope: all, 369 nets; protect: existing; budget 1500 s
- Candidate: `/home/halbritt/.cache/agent499-cluster-anchored/iter3/route/runs/candidate/planed-krt/20261021T015600.197348Z/candidate/candidate/ca.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1113.096 s |
| routing | INCOMPLETE | 100 unconnected in scope, 100 total (input: 499) |
| validation | FAIL | 5 new DRC violations: track_dangling 5; preservation net_completion: 39 of the 305 nets fully connected in the input lost connection: /ADC_AIN0, /AFE_BUF1, /AFE_DIV0, /AFE_DIV1, /AFE_DIV5, /AFE_DIV6, /DIAG_I2C_SCL, /DIAG_I2C_SDA, /DIAG_U27_AIN0, /DIAG_U28_AIN0 |

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
  "count": 5,
  "by_type": {
   "track_dangling": 5
  },
  "by_severity": {
   "warning": 5
  }
 },
 "preexisting_violations": 79,
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

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-cluster-anchored/iter3/route/runs/candidate/planed-krt/20261021T015600.197348Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| track /TIRE_CAN_TX_ENABLE In1.Cu (new, unlocked) 45c7ce36 | new_copper | 11 | 13 |
| track /TWAI_RX In1.Cu (new, unlocked) a2b0f7d3 | new_copper | 8 | 9 |
| track /MCU_BOOT46 In1.Cu (new, unlocked) 83612541 | new_copper | 6 | 10 |
| footprint U12 pads 9', 9''''', 9'''''', 9, 9'', 9''' +5 more (/GND, /+5V_CAN, /PRE_6V3) | footprint | 6 | 10 |
| track /TWAI_TX In1.Cu (new, unlocked) 6ffecd7e | new_copper | 6 | 9 |
| track /DIAG_U29_AIN2_UPPER2 In2.Cu (new, unlocked) f2ce7ad6 | new_copper | 4 | 5 |
| track /TIRE_CAN_H In2.Cu (new, unlocked) ceffa6c5 | new_copper | 4 | 5 |
| track /POD_AUX1_SIGNAL In2.Cu (new, unlocked) 8fdf76f7 | new_copper | 4 | 4 |
| via /DIAG_I2C_SCL (new, unlocked) 45bc4988 | new_copper | 4 | 4 |
| via /IMU_INT1 (new, unlocked) 20e904e8 | new_copper | 4 | 4 |

- `/+3V3`: 10 open; best layer F.Cu with 0 hard blockers
- `/ADC_AIN0`: 1 open; best layer In2.Cu with 12 hard blockers (track /TIRE_CAN_H In2.Cu ceffa6c5, track /POD_5V_SENSOR In2.Cu 21fdffe1, track /POD_5V_SENSOR In2.Cu 27e7a904, track /DIAG_U28_AIN1_UPPER2 In2.Cu 7bbfe97f, track /ADC_AIN5 In2.Cu 4d7a6063)
- `/AFE_BUF1`: 1 open; best layer In1.Cu with 6 hard blockers (track /SETPOINT_5V In1.Cu f4c56e2b, track /SETPOINT_5V In1.Cu f985eb9e, footprint U12)
- `/AFE_DIV0`: 1 open; best layer In2.Cu with 3 hard blockers (track /AFE_BUF3 In2.Cu 83a83c3b, via /TWAI_TX 731eafac, via /AFE_DIV1 807bfe34)
- `/AFE_DIV1`: 1 open; best layer B.Cu with 1 hard blockers (track /AFE_BUF0 B.Cu be5c8eba)
- `/AFE_DIV5`: 1 open; best layer In1.Cu with 2 hard blockers (track /AFE_BUF5 In1.Cu 3ede00ec, via /AFE_BUF5 ef0e1f97)
- `/AFE_DIV6`: 1 open; best layer In2.Cu with 2 hard blockers (track /POD_TIRE_SUPPLY In2.Cu 90bfa0bb, via /DIAG_U28_AIN1_UPPER2 1ba017c4)
- `/DIAG_I2C_SCL`: 2 open; best layer In1.Cu with 0 hard blockers
- `/DIAG_I2C_SDA`: 4 open; best layer In1.Cu with 3 hard blockers (track /MCU_BOOT46 In1.Cu 83612541, track /TIRE_CAN_TX_ENABLE In1.Cu 06a6fcd7, track /TIRE_CAN_TX_ENABLE In1.Cu 45c7ce36, track /GNSS_PPS In2.Cu ef31d5e4, via /GND 1e689cd5)
- `/DIAG_U27_AIN0`: 2 open; best layer In1.Cu with 10 hard blockers (track /+3V3 In1.Cu 0660f226, track /POD_12V_PROTECTED In1.Cu 84874086, track /PRE_6V3 In1.Cu 5ba68118, track /PRE_6V3 In1.Cu d0d9dfee, track /PRE_6V3 In1.Cu d551570f)
- `/DIAG_U28_AIN0`: 1 open; best layer In1.Cu with 0 hard blockers
- `/DIAG_U28_AIN2`: 2 open; best layer In1.Cu with 4 hard blockers (track /TWAI_RX In1.Cu a2b0f7d3, track /MCU_BOOT46 In1.Cu 83612541, track /TIRE_CAN_TX_ENABLE In1.Cu 06a6fcd7, track /DIAG_U28_AIN1 In1.Cu 4463015e)
- `/DIAG_U29_AIN0`: 1 open; best layer In2.Cu with 6 hard blockers (track /TIRE_CAN_RX In2.Cu a89e9d60, track /TIRE_CAN_CS In2.Cu fdfa0cda, track /DIAG_I2C_SCL In2.Cu d0979e4e, track /DIAG_U28_AIN1 In2.Cu c10b1aad, via /TIRE_CAN_CS 160e453a)
- `/DIAG_U29_AIN1`: 1 open; best layer In1.Cu with 8 hard blockers (track /GND In1.Cu e153b959, track /TWAI_TX In1.Cu e504f3b9, track /TWAI_RX In1.Cu 5ae78a45, track /TIRE_CAN_INT_N In1.Cu 389dda85, via /GND 29fd3f4d)
- `/EMMC_CLK`: 1 open; best layer In1.Cu with 0 hard blockers
- `/EMMC_CMD`: 1 open; best layer In1.Cu with 0 hard blockers
- `/EMMC_DAT0`: 1 open; best layer In1.Cu with 2 hard blockers (track /SPI_MOSI In1.Cu 69dc6181, via /EMMC_CMD c5e3aaea)
- `/EMMC_DAT1`: 1 open; best layer In1.Cu with 1 hard blockers (track /SPI_MOSI In1.Cu 69dc6181)
- `/EMMC_DAT2`: 1 open; best layer In1.Cu with 2 hard blockers (track /SPI_MOSI In1.Cu 69dc6181, via /EMMC_DAT1 c2cea301)
- `/EMMC_DAT3`: 1 open; best layer In2.Cu with 1 hard blockers (track /GNSS_PPS In2.Cu ef31d5e4)
- … 38 more nets in the report
- 48 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 3918,
 "new_vias": 390,
 "new_track_length_mm": 4738.189,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1799.294,
  "F.Cu": 1844.853,
  "In1.Cu": 554.197,
  "In2.Cu": 539.846
 },
 "new_copper_nets": 174,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
