# Routing attempt: freerouting on patched2

- Backend: freerouting v2.5.0 (freerouting-2.5.0.jar b647a2f824cfbc54bc4dcaee71b03b7cd945eb76)
- Input: `p2.kicad_pcb` from working tree @ None (fingerprint e15d64bc1cdc39f8)
- Scope: all, 369 nets; protect: existing; budget 1500 s
- Candidate: `/home/halbritt/.cache/agent499-route-diag/runs/patched2/cited-freerouting-nostall/20261021T000615.283801Z/candidate/patched2/p2.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1512.998 s |
| routing | INCOMPLETE | 191 unconnected in scope, 191 total (input: 499) |
| validation | FAIL | 309 new DRC violations: via_diameter 154, annular_width 154, track_dangling 1; preservation net_completion: 54 of the 312 nets fully connected in the input lost connection: /ADC_AIN0, /ADC_AIN2, /ADC_AIN5, /ADC_AIN7, /ADC_CS, /AFE_BUF3, /AFE_BUF4, /AFE_BUF5, /AFE_DIV2, /AFE_DIV4 |

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
 "violations_total": 425,
 "parity_total": 0,
 "new_violations": {
  "count": 309,
  "by_type": {
   "via_diameter": 154,
   "annular_width": 154,
   "track_dangling": 1
  },
  "by_severity": {
   "error": 308,
   "warning": 1
  }
 },
 "preexisting_violations": 116,
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
- p2.kicad_dru: net-class-to-net-class clearance rules are translated to Specctra class_class rules; any other custom rule is listed as untranslated below
- custom rule 'agent_ee_netclass_RF_50' not given to the backend: only a single clearance constraint without layer clauses is translatable
- custom rule 'fine-pitch intra-footprint pad clearance (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U2') && B.memberOfFootprint('U2')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U16 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U16') && B.memberOfFootprint('U16')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U17 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U17') && B.memberOfFootprint('U17')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U18 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U18') && B.memberOfFootprint('U18')" is not purely net-class based
- custom rule 'supervisor intra-footprint pad clearance U19 (D-PCB-1)' not given to the backend: condition "A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('U19') && B.memberOfFootprint('U19')" is not purely net-class based

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-route-diag/runs/patched2/cited-freerouting-nostall/20261021T000615.283801Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| track /EMMC_VCC_3V3 In2.Cu (new, unlocked) ad235e03 | new_copper | 5 | 19 |
| track /POD_AUX1_SIGNAL In1.Cu (new, unlocked) e6412c8c | new_copper | 5 | 14 |
| track /TIRE_CAN_CS In1.Cu (new, unlocked) b40eb9b1 | new_copper | 5 | 9 |
| track /TWAI_TX In1.Cu (new, unlocked) 00b3c24a | new_copper | 4 | 29 |
| track /POD_AUX2_SIGNAL In1.Cu (new, unlocked) a045d565 | new_copper | 4 | 14 |
| track /POD_AUX4_SIGNAL In1.Cu (new, unlocked) 0145650f | new_copper | 4 | 13 |
| track /TWAI_RX In1.Cu (new, unlocked) 84d573fd | new_copper | 3 | 26 |
| track /AFE_DIV3 In1.Cu (new, unlocked) c3e8603f | new_copper | 3 | 16 |
| track /TIRE_CAN_TX In1.Cu (new, unlocked) 9d054061 | new_copper | 3 | 14 |
| track /TIRE_CAN_INT_N In1.Cu (new, unlocked) e611d9d3 | new_copper | 3 | 10 |

- `/+3V3`: 24 open; best layer In1.Cu with 4 hard blockers (track /ADC_AIN2 In2.Cu c6372d50, track /IMU_CS In1.Cu a4595a57, track /DIAG_U27_AIN0_UPPER2 In1.Cu 8dfb4e14, via /IMU_CS 6ce8a5e9, via /DIAG_U27_AIN0 8e4647f1)
- `/+5V_CAN`: 1 open; best layer In2.Cu with 0 hard blockers
- `/ADC_AIN0`: 1 open; best layer In1.Cu with 11 hard blockers (track /SETPOINT_5V In1.Cu 755413a0, track /IMU_CS In1.Cu a4595a57, track /WHEEL_REAR_OUT In1.Cu aca71e2d, track /POD_AUX1_SIGNAL In1.Cu e6412c8c, track /POD_AUX2_SIGNAL In1.Cu a045d565)
- `/ADC_AIN2`: 1 open; best layer In1.Cu with 1 hard blockers (via /ADC_AIN1 a34917f3)
- `/ADC_AIN5`: 1 open; best layer In1.Cu with 0 hard blockers
- `/ADC_AIN7`: 1 open; best layer In1.Cu with 0 hard blockers
- `/ADC_CS`: 1 open; best layer In1.Cu with 3 hard blockers (track /TIRE_CAN_TX In1.Cu 9d054061, track /TWAI_TX In1.Cu 00b3c24a, track /TWAI_RX In1.Cu 84d573fd)
- `/AFE_BUF3`: 1 open; best layer In2.Cu with 0 hard blockers
- `/AFE_BUF4`: 1 open; best layer In1.Cu with 2 hard blockers (track /TIRE_CAN_CS In1.Cu b40eb9b1, track /TIRE_CAN_INT_N In1.Cu e611d9d3)
- `/AFE_BUF5`: 1 open; best layer In1.Cu with 2 hard blockers (track /TIRE_CAN_CS In1.Cu b40eb9b1, track /TIRE_CAN_INT_N In1.Cu e611d9d3)
- `/AFE_DIV2`: 1 open; best layer In1.Cu with 0 hard blockers
- `/AFE_DIV4`: 2 open; best layer In1.Cu with 0 hard blockers
- `/AFE_DIV7`: 1 open; best layer In1.Cu with 1 hard blockers (track /TIRE_CAN_CS In1.Cu b40eb9b1)
- `/ANT_BIAS`: 2 open; best layer In2.Cu with 1 hard blockers (track /ADC_AIN1 In2.Cu 2d4e7ddd)
- `/ANT_LIMITED`: 1 open; best layer In2.Cu with 1 hard blockers (track /EMMC_VCC_3V3 In2.Cu ad235e03)
- `/DIAG_I2C_SCL`: 1 open; best layer In1.Cu with 1 hard blockers (track /EMMC_VCC_3V3 In1.Cu 6061ae3a)
- `/DIAG_I2C_SDA`: 2 open; best layer In1.Cu with 0 hard blockers
- `/DIAG_U27_AIN1`: 1 open; best layer In2.Cu with 11 hard blockers (track /FB_PRE_SERIES In2.Cu 8a7ac7f9, track /IMU_CS In2.Cu 0f430f7f, track /ADC_AIN3 In2.Cu a8621e06, track /ADC_AIN3 In2.Cu b4a2e051, track /ADC_AIN3 In2.Cu c9889744)
- `/DIAG_U27_AIN2`: 2 open; best layer In2.Cu with 4 hard blockers (track /ADC_AIN1 In2.Cu 5d50c871, track /ADC_AIN1 In2.Cu 2d4e7ddd, track /ADC_AIN1 In2.Cu ea0c12ba, via /WHEEL_FRONT_OUT a394080e)
- `/DIAG_U28_AIN2`: 2 open; best layer F.Cu with 0 hard blockers
- … 64 more nets in the report
- 126 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 1976,
 "new_vias": 154,
 "new_track_length_mm": 4308.856,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1147.533,
  "F.Cu": 1154.165,
  "In1.Cu": 703.75,
  "In2.Cu": 1303.408
 },
 "new_copper_nets": 168,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
