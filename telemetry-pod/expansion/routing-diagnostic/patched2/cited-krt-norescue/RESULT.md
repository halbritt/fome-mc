# Routing attempt: krt on patched2

- Backend: krt 0.23.1 (owned-c6c09054f684)
- Input: `p2.kicad_pcb` from working tree @ None (fingerprint e15d64bc1cdc39f8)
- Scope: all, 369 nets; protect: existing; budget 1800 s
- Candidate: `/home/halbritt/.cache/agent499-route-diag/runs/patched2/cited-krt-norescue/20261021T000015.332333Z/candidate/patched2/p2.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 3, 964.373 s; KRT --strict-sizes: it reports delivering geometry below a requirement (candidate kept for grading) |
| routing | INCOMPLETE | 101 unconnected in scope, 101 total (input: 499) |
| validation | FAIL | 430 new DRC violations: via_diameter 199, annular_width 199, track_dangling 32; preservation net_completion: 34 of the 312 nets fully connected in the input lost connection: /ADC_AIN1, /ADC_AIN3, /ADC_AIN6, /AFE_BUF6, /AFE_BUF7, /AFE_DIV2, /ANT_LIMITED, /DIAG_I2C_SCL, /EMMC_CLK, /EMMC_CMD |

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
 "violations_total": 546,
 "parity_total": 0,
 "new_violations": {
  "count": 430,
  "by_type": {
   "via_diameter": 199,
   "annular_width": 199,
   "track_dangling": 32
  },
  "by_severity": {
   "error": 398,
   "warning": 32
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

- KRT reads only a subset of .kicad_dru custom rules; every rule is still graded by KiCad DRC
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class
- backend reported: .kicad_dru: rule 'fine-pitch intra-footprint pad clearance (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U16 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U17 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U18 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U19 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it

Blocked by (heuristic straight/L corridors, not a proof; details `/home/halbritt/.cache/agent499-route-diag/runs/patched2/cited-krt-norescue/20261021T000015.332333Z/validate/blocked-by.json`):

| Blocker | Category | Blocks (best layer) | Blocks (any layer) |
|---|---|---|---|
| track /DIAG_U29_AIN1 In1.Cu (new, unlocked) 469afdb0 | new_copper | 5 | 10 |
| track /DIAG_U29_AIN2 In2.Cu (new, unlocked) 3e3d0817 | new_copper | 4 | 7 |
| track /EMMC_DAT2 In1.Cu (new, unlocked) 232d456a | new_copper | 3 | 13 |
| track /DIAG_U27_AIN2 In2.Cu (new, unlocked) 4eda00f3 | new_copper | 3 | 9 |
| track /DIAG_U28_AIN3 In1.Cu (new, unlocked) 25ebb539 | new_copper | 3 | 8 |
| track /POD_AUX1_SIGNAL In2.Cu (new, unlocked) ee71d57f | new_copper | 3 | 5 |
| track /TIRE_CAN_RX In2.Cu (new, unlocked) 7d9a970b | new_copper | 3 | 4 |
| track /PRE_6V3 In2.Cu (new, unlocked) db7443cc | new_copper | 3 | 3 |
| track /ADC_AIN1 In1.Cu (new, unlocked) 5a38d05b | new_copper | 2 | 3 |
| track /DIAG_U27_AIN2 In1.Cu (new, unlocked) 62afa8d1 | new_copper | 2 | 3 |

- `/+3V3`: 8 open; best layer F.Cu with 1 hard blockers (footprint U21, track /TIRE_CAN_TX F.Cu 60694e68, footprint U22)
- `/ADC_AIN1`: 1 open; best layer In1.Cu with 2 hard blockers (track /DIAG_U28_AIN1 In1.Cu dc014bfe, track /DIAG_U29_AIN1 In1.Cu 469afdb0)
- `/ADC_AIN3`: 1 open; best layer In2.Cu with 16 hard blockers (track /TIRE_CAN_RX In2.Cu 2dc04461, track /TIRE_CAN_RX In2.Cu 7d9a970b, track /PRE_6V3 In2.Cu 7c0218ce, track /TWAI_TX In2.Cu feef065e, track /POD_AUX1_SIGNAL In2.Cu ee71d57f)
- `/ADC_AIN6`: 1 open; best layer B.Cu with 2 hard blockers (track /ADC_AIN5 B.Cu 370cba83, footprint C59)
- `/AFE_BUF6`: 1 open; best layer F.Cu with 5 hard blockers (track /GNSS_PPS F.Cu 15758762, track /TIRE_CAN_CS F.Cu 883cf605, track /GNSS_RX_IN F.Cu c0991761, via /AFE_DIV6 411764e7, footprint U1)
- `/AFE_BUF7`: 1 open; best layer In2.Cu with 1 hard blockers (track /SPI_MOSI In2.Cu c3113807)
- `/AFE_DIV2`: 1 open; best layer In1.Cu with 12 hard blockers (track /ANT_BIAS In1.Cu 81558bdd, track /PRE_6V3 In1.Cu 166788f7, track /PRE_6V3 In1.Cu 85991f21, track /PRE_6V3 In1.Cu 8832ea6a, track /PRE_6V3 In1.Cu dcfcd2df)
- `/ANT_LIMITED`: 1 open; best layer In1.Cu with 19 hard blockers (track /GND In1.Cu 0384e0b8, track /GND In1.Cu 25789186, track /GND In1.Cu 48c21369, track /GND In1.Cu 580134ee, track /GND In1.Cu 70d0510a)
- `/DIAG_I2C_SCL`: 1 open; best layer In1.Cu with 1 hard blockers (track /GND In1.Cu 44bc4103)
- `/EMMC_CLK`: 1 open; best layer In1.Cu with 0 hard blockers
- `/EMMC_CMD`: 1 open; best layer In2.Cu with 0 hard blockers
- `/EMMC_DAT1`: 1 open; best layer In1.Cu with 1 hard blockers (track /EMMC_DAT2 In1.Cu 232d456a)
- `/EMMC_DAT3`: 2 open; best layer In1.Cu with 2 hard blockers (track /MCU_EN In1.Cu cb829738, via /GND 706de1c8)
- `/EMMC_DAT4`: 1 open; best layer In1.Cu with 5 hard blockers (track /+3V3 In1.Cu 2946b8e9, track /MCU_EN In1.Cu 52df340a, track /SPI_MISO In1.Cu 367db080, track /GNSS_LNA_EN In1.Cu 8aee6e18, via /DIAG_U27_AIN0 b7130013)
- `/EMMC_DAT5`: 1 open; best layer In2.Cu with 6 hard blockers (track /EMMC_VCC_3V3 In2.Cu 02b4e1f0, track /EMMC_VCC_3V3 In2.Cu 3e282d98, track /EMMC_VCC_3V3 In2.Cu 554e05fb, track /EMMC_VCC_3V3 In2.Cu af957027, track /EMMC_VCC_3V3 In2.Cu e97e49e8)
- `/EMMC_DAT6`: 1 open; best layer In1.Cu with 1 hard blockers (track /EMMC_DAT2 In1.Cu 232d456a)
- `/EMMC_DAT7`: 1 open; best layer In2.Cu with 2 hard blockers (track /SPI_MOSI In2.Cu 5c647f51, via /SPI_MOSI 5fd33767)
- `/EMMC_DS`: 1 open; best layer In2.Cu with 0 hard blockers
- `/EMMC_VCC_3V3`: 1 open; best layer In1.Cu with 1 hard blockers (via /MCU_BOOT 8793a49f)
- `/EMMC_VDDi`: 1 open; best layer In2.Cu with 0 hard blockers
- … 32 more nets in the report
- 45 connection(s) have an unobstructed corridor: the obstacle is elsewhere (congestion, detours, the backend's search or budget)

Route statistics:

```json
{
 "new_tracks": 4656,
 "new_vias": 404,
 "new_track_length_mm": 5992.81,
 "new_track_length_mm_by_layer": {
  "B.Cu": 2022.6,
  "F.Cu": 1775.785,
  "In1.Cu": 1193.382,
  "In2.Cu": 1001.043
 },
 "new_copper_nets": 169,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
