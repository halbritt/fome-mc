# Routing attempt: freerouting on candidate

- Backend: freerouting v2.5.0 (freerouting-2.5.0.jar b647a2f824cfbc54bc4dcaee71b03b7cd945eb76)
- Input: `ca2.kicad_pcb` from working tree @ None (fingerprint bf10798c3725a18b)
- Scope: all, 235 nets; protect: existing; budget 1500 s
- Candidate: `/home/halbritt/.cache/agent499-microsd/iter8d/route/runs/candidate/iter8d-fr-leftovers/20261021T152620.088475Z/candidate/candidate/ca2.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1566.23 s |
| routing | INCOMPLETE | 51 unconnected in scope, 51 total (input: 55) |
| validation | PASS | no new findings |

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
 "violations_total": 24,
 "parity_total": 0,
 "new_violations": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
 },
 "preexisting_violations": 24,
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

- Freerouting never rips up pre-existing copper (KiCad exports it as fixed/protected); --protect locked behaves like --protect existing
- Specctra carries per-class width/clearance/via only: custom .kicad_dru rules, diff pairs and length tuning are not exported; KiCad DRC grades them
- rule areas export only their no-tracks/no-vias restrictions; zones export as plane outlines
- ca2.kicad_dru: net-class-to-net-class clearance rules are translated to Specctra class_class rules; any other custom rule is listed as untranslated below
- custom rule 'agent_ee_netclass_RF_50' not given to the backend: only a single clearance constraint without layer clauses is translatable
- custom rule 'fine-pitch intra-footprint pad clearance (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U2') && B.memberOfFootprint('U2')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U16 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U16') && B.memberOfFootprint('U16')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U17 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U17') && B.memberOfFootprint('U17')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U18 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U18') && B.memberOfFootprint('U18')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U19 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U19') && B.memberOfFootprint('U19')" is not purely net-class based

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-microsd/iter8d/route/runs/candidate/iter8d-fr-leftovers/20261021T152620.088475Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| via /TIRE_CAN_TX (input, unlocked) 4514d48b | input_copper | 3 | 3 |
| track /POD_AUX2_SIGNAL In1.Cu (input, unlocked) f74a23f0 | input_copper | 2 | 4 |
| track /GNSS_RX_IN In1.Cu (input, unlocked) 69d51fcc | input_copper | 2 | 3 |
| track /SPI_MISO In2.Cu (input, unlocked) dacb6bc4 | input_copper | 2 | 3 |
| track /DIAG_U28_AIN1_UPPER2 In1.Cu (input, unlocked) 61512e74 | input_copper | 2 | 2 |
| via /DIAG_U29_AIN2_UPPER2 (input, unlocked) ef936836 | input_copper | 2 | 2 |
| via /SPI_MISO (input, unlocked) 44567c7f | input_copper | 2 | 2 |
| via /SPI_MOSI (input, unlocked) b66b4296 | input_copper | 2 | 2 |
| footprint U1 pads 3, 17, 18, 8, 9, 41 +17 more (/MCU_EN, /ADC_CS, /IMU_CS +15 more) | footprint | 1 | 11 |
| track /SUP_U19_CT In2.Cu (input, unlocked) 30556dd6 | input_copper | 1 | 7 |

- `/+3V3`: 4 open; best layer In2.Cu with 1 hard blockers (via /GND 8273d977)
- `/AFE_BUF1`: 1 open; best layer In2.Cu with 1 hard blockers (via /GND 93895e5b)
- `/AFE_DIV1`: 1 open; best layer In1.Cu with 0 hard blockers
- `/DIAG_U28_AIN2`: 1 open; best layer In2.Cu with 6 hard blockers (via /+3V3 5732e2f9, via /GND 24a3ee37, via /GND 4d843ac7, via /GND b01b85d8, via /ANT_LIMITED 475d2222)
- `/DIAG_U28_AIN3`: 1 open; best layer In1.Cu with 13 hard blockers (track /TIRE_CAN_L In1.Cu 4def16cc, track /TIRE_CAN_L In1.Cu b2346d9f, track /TIRE_CAN_H In1.Cu c39ee8e2, track /POD_TIRE_SUPPLY In1.Cu fb8b7f30, track /SD_DAT0 In1.Cu 34ab89e4)
- `/GND`: 14 open; best layer F.Cu with 2 hard blockers (via /+3V3 6c541906, footprint C80)
- `/GNSS_PPS`: 1 open; best layer In1.Cu with 6 hard blockers (track /IMU_INT1 In1.Cu 9996666a, track /SENSOR_REF_2V5 In1.Cu eca76af7, track /ADC_AIN4 In1.Cu adb5178d, track /DIAG_U29_AIN2_UPPER2 In1.Cu 020d13b7, via /DIAG_U29_AIN2_UPPER2 ef936836)
- `/MCU_EN`: 3 open; best layer In1.Cu with 1 hard blockers (via /SUP_U19_CT 1de3bd57)
- `/POD_5V_AUX`: 1 open; best layer In1.Cu with 0 hard blockers
- `/POD_AUX3_SIGNAL`: 1 open; best layer In1.Cu with 5 hard blockers (track /TIRE_CAN_H In1.Cu 041b703b, track /POD_TIRE_SUPPLY In1.Cu d966121a, track /DIAG_U28_AIN1_UPPER2 In1.Cu 61512e74, footprint U6)
- `/POWER_FAIL_N`: 1 open; best layer In1.Cu with 0 hard blockers
- `/SD_CD`: 1 open; best layer In1.Cu with 19 hard blockers (track /GND In1.Cu f3774e66, track /PRE_6V3 In1.Cu 6acb734e, track /MCU_EN In1.Cu f4b0487a, track /GNSS_RX_IN In1.Cu 69d51fcc, track /POD_AUX1_SIGNAL In1.Cu 629bafd1)
- `/SD_CMD`: 1 open; best layer In2.Cu with 18 hard blockers (track /+3V3 In2.Cu a401adc2, track /+5V_CAN In2.Cu 2c6ff269, track /POD_5V_SENSOR In2.Cu 5db7622d, track /POD_5V_SENSOR In2.Cu 8164194a, track /POD_CAN_P In2.Cu 6b0f33b8)
- `/SD_DAT1`: 1 open; best layer In2.Cu with 10 hard blockers (track /SUP_U19_CT In2.Cu 0a43fa04, track /SUP_U19_CT In2.Cu 30556dd6, track /SUP_U19_CT In2.Cu f3ff8ea6, via /TIRE_CAN_TX 4514d48b, via /SUP_U19_CT 76c0e13c)
- `/SD_DAT2`: 1 open; best layer In1.Cu with 13 hard blockers (track /+3V3 In1.Cu 00ee79a0, track /+3V3 In1.Cu 8af80b89, track /GND In1.Cu 6d1b7751, track /TWAI_RX In1.Cu 1ce37649, track /WHEEL_FRONT_OUT In1.Cu cf833659)
- `/SENSOR_FAULT_N`: 2 open; best layer In1.Cu with 3 hard blockers (track /MCU_BOOT In1.Cu 0e1b558b, via /IMU_INT1 dcba173e, via /SPI_MISO d11fbdb8)
- `/SENSOR_POWER_FRONT_ILIM`: 1 open; best layer B.Cu with 0 hard blockers
- `/SENSOR_POWER_FRONT_OVP`: 1 open; best layer B.Cu with 0 hard blockers
- `/SENSOR_POWER_FRONT_UVLO`: 2 open; best layer B.Cu with 0 hard blockers
- `/SENSOR_POWER_REAR_DVDT`: 1 open; best layer B.Cu with 0 hard blockers
- … 10 more nets in the report
- 32 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 794,
 "new_vias": 5,
 "new_track_length_mm": 173.309,
 "new_track_length_mm_by_layer": {
  "B.Cu": 40.216,
  "F.Cu": 92.508,
  "In1.Cu": 36.88,
  "In2.Cu": 3.704
 },
 "new_copper_nets": 149,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
