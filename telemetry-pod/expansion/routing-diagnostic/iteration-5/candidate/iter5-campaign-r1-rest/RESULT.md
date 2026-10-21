# Routing attempt: builtin on candidate

- Backend: builtin 0.23.1 (owned-c6c09054f684)
- Input: `ca2.kicad_pcb` from working tree @ None (fingerprint aeb17aa302c84e6b)
- Scope: selected, 189 nets; protect: existing; budget 900 s
- Candidate: `/home/halbritt/.cache/agent499-cluster-anchored/iter5/route/runs/candidate/iter5-campaign-r1-rest/20261021T085828.019416Z/candidate/candidate/ca2.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 499.696 s |
| routing | INCOMPLETE | 39 unconnected in scope, 68 total (input: 335) |
| validation | FAIL | preservation pour_integrity: 2 copper zones, 55 zone-connected pads compared on the refilled boards (min spokes 2); /+3V3@In2.Cu 4802.7 mm2 (-7.974 %), 1 polygons; /GND@In1.Cu 4812.8 mm2 (-8.932 %), 1 polygons; 1 spokes_below_minimum |

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
| pour_integrity | FAIL |

Native DRC (original rules and severities):

```json
{
 "violations_total": 75,
 "parity_total": 0,
 "new_violations": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
 },
 "preexisting_violations": 75,
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

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-cluster-anchored/iter5/route/runs/candidate/iter5-campaign-r1-rest/20261021T085828.019416Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| track /MCU_EN In1.Cu (input, unlocked) 307a0cd4 | input_copper | 4 | 4 |
| track /ADC_AIN5 In2.Cu (input, unlocked) 6a5cd648 | input_copper | 2 | 5 |
| track /AFE_BUF7 In1.Cu (new, unlocked) 8995e2df | new_copper | 2 | 3 |
| track /TWAI_TX In1.Cu (new, unlocked) 8954b573 | new_copper | 2 | 3 |
| via /ADC_AIN7 (input, unlocked) 631ee055 | input_copper | 2 | 2 |
| via /MCU_EN (input, unlocked) 1d12cd20 | input_copper | 2 | 2 |
| track /TIRE_CAN_GPIO1 In1.Cu (new, unlocked) 3cda1ac1 | new_copper | 2 | 2 |
| via /AFE_BUF7 (new, unlocked) 65f04d83 | new_copper | 2 | 2 |
| via /DIAG_U28_AIN1_UPPER2 (new, unlocked) 6fcfa42b | new_copper | 2 | 2 |
| via /TIRE_CAN_GPIO1 (new, unlocked) 7c92cf03 | new_copper | 2 | 2 |

- `/+5V_CAN`: 1 open; best layer In1.Cu with 0 hard blockers
- `/ADC_AIN1`: 2 open; best layer In2.Cu with 2 hard blockers (track /+3V3 In2.Cu 4d66d63d, track /DIAG_U29_AIN0 In2.Cu cc61997b)
- `/ADC_AIN3`: 2 open; best layer In2.Cu with 5 hard blockers (track /TWAI_RX In2.Cu fe3baf7b, track /IMU_INT1 In2.Cu 8337a0e3, via /AFE_BUF1 47d3f2ee, via /SENSOR_REF_2V5 1c6ae7d2, via /DIAG_U27_AIN1 08b30637)
- `/ADC_AIN6`: 2 open; best layer In1.Cu with 3 hard blockers (track /GND In1.Cu 0227f371, track /GND In1.Cu 26a984bf, track /ADC_AIN7 In1.Cu d6851564, via /SPI_MISO 56a82632, via /DIAG_U28_AIN1 76aa7c51)
- `/ADC_CS`: 2 open; best layer In2.Cu with 2 hard blockers (track /ADC_AIN5 In2.Cu 48cfa857, track /ADC_AIN5 In2.Cu 6a5cd648)
- `/AFE_BUF4`: 1 open; best layer In1.Cu with 6 hard blockers (track /TWAI_TX In1.Cu 8954b573, track /ANT_LIMITED In1.Cu 8eff5843, track /ADC_AIN7 In1.Cu 0d4789af, via /GND e39c345d, via /GNSS_LNA_EN 99ae57c8)
- `/AFE_DIV2`: 1 open; best layer F.Cu with 1 hard blockers (footprint R164)
- `/AFE_DIV4`: 1 open; best layer In1.Cu with 3 hard blockers (track /TIRE_CAN_H In1.Cu b513decc, track /SENSOR_POWER_TIRE_RTN In1.Cu 6d56535a, via /TIRE_CAN_RX 08de3c3e)
- `/AFE_DIV5`: 1 open; best layer In1.Cu with 6 hard blockers (track /SENSOR_POWER_TIRE_RTN In1.Cu 3035bba6, track /AFE_BUF7 In1.Cu 8995e2df, via /+3V3 91cdcb77, via /PRE_6V3 e5ea8388, via /SENSOR_POWER_TIRE_RTN 0e4366f9)
- `/AFE_DIV7`: 1 open; best layer B.Cu with 1 hard blockers (track /GND B.Cu 4cf46699)
- `/DIAG_I2C_SCL`: 1 open; best layer In2.Cu with 0 hard blockers
- `/DIAG_I2C_SDA`: 1 open; best layer F.Cu with 1 hard blockers (track /DIAG_U28_AIN1 F.Cu 469f3243)
- `/DIAG_U29_AIN1`: 1 open; best layer In1.Cu with 2 hard blockers (via /TIRE_CAN_SILENT 3c0fcc00, via /DIAG_U29_AIN0 04680a69)
- `/DIAG_U29_AIN2`: 1 open; best layer In2.Cu with 0 hard blockers
- `/DIAG_U29_AIN2_UPPER2`: 1 open; best layer In1.Cu with 12 hard blockers (track /TIRE_CAN_TX In1.Cu ed2abfe0, track /+5V_CAN In1.Cu 105ec3c4, track /+5V_CAN In1.Cu de07bab7, track /+5V_CAN In1.Cu f42a3dcf, track /TIRE_CAN_RX In1.Cu d0628dc1)
- `/GNSS_PPS`: 1 open; best layer In2.Cu with 6 hard blockers (track /SD_CMD In2.Cu e6d30a17, track /SUP_U18_TOP_SERIES In2.Cu 32385fbd, via /SD_DAT3 0f350a6a, via /ADC_AIN7 f429ab8a, footprint U1)
- `/GNSS_RX_IN`: 1 open; best layer In1.Cu with 7 hard blockers (track /TWAI_TX In1.Cu 8954b573, track /AFE_BUF7 In1.Cu 8995e2df, track /ADC_AIN7 In1.Cu 4b57ccb1, track /ADC_AIN7 In1.Cu 8cd86410, via /AFE_BUF7 65f04d83)
- `/GNSS_TX_OUT`: 1 open; best layer In2.Cu with 6 hard blockers (track /TIRE_CAN_SILENT In2.Cu 733f6a7c, track /GNSS_LNA_EN In2.Cu b94ca46f, track /ADC_AIN5 In2.Cu 6a5cd648, via /AFE_BUF7 65f04d83, via /ADC_AIN7 631ee055)
- `/POWER_FAIL_N`: 2 open; best layer In1.Cu with 1 hard blockers (track /MCU_EN In1.Cu 307a0cd4)
- `/PRE_6V3`: 1 open; best layer In1.Cu with 0 hard blockers
- … 12 more nets in the report
- 10 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 1602,
 "new_vias": 251,
 "new_track_length_mm": 3010.928,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1231.639,
  "F.Cu": 1131.65,
  "In1.Cu": 383.712,
  "In2.Cu": 263.927
 },
 "new_copper_nets": 122,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
