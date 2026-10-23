# ROUTE-1: one isolated all-net builtin route of the R5 board — routed candidate saved; routing INCOMPLETE; validation FAIL

Assignment: agent-521 brief b9e0f217 (via agent-519). Input: R5 board `8f3bc234…` (FOME writer commit `9d5aefdd`), accepted. These are coordinator records, not owner text.

**Clock:** task started 2026-10-23T06:52:18.73Z, route 06:53:08 → 07:00:16Z, result written by about 07:03Z. Total about 11 min of the 40 min bound. One run; no retry, no optimization.

**This candidate is INCOMPLETE and INVALID for release.** It has 78 open connections on 48 nets, and native validation fails on 61 new dangling-copper warnings. It is retained as inspectable evidence. It is not a finished routed board.

## The three outcomes, separately

| | Result |
|---|---|
| **Process outcome** | **PASS**: the builtin backend exited 0 (`process.status` PASS); kicad-route overall exit **3** because routing is incomplete and validation failed |
| **Routing scope and completeness** | Scope **all: 235 of 235 nets** (no `--nets`/`--netclass`). **INCOMPLETE**: unconnected **499 → 78** (`unconnected_in_scope` = `unconnected_total` = 78). 48 nets remain incomplete (native terminal evidence: incomplete nets 182 → 48, component deficit 701 → 78). Net completion PASS: none of the 53 nets connected in the input was lost or split |
| **Native validation** | **FAIL**: 61 new DRC violations (via_dangling 34, track_dangling 27; all severity warning). Schematic parity 0 (0 new). Refill did not modify the board. Preservation: **all 16 checks PASS** |

**Copper:** 5889 new tracks and **686 new vias**; new track length 7523.4 mm (F.Cu 2891.4, In2.Cu 2355.0, B.Cu 2277.0); 181 nets received new copper; **0** existing tracks/vias removed. The input had 0 tracks and 0 vias.

**The 48 incomplete nets** (`result.json` `routing.unrouted_nets`): /+3V3, /ADC_AIN4, /ADC_AIN7, /AFE_BUF3, /AFE_BUF7, /AFE_DIV0, /AFE_DIV5, /AFE_DIV6, /AFE_DIV7, /DIAG_I2C_SCL, /DIAG_U27_AIN2, /DIAG_U28_AIN1, /DIAG_U28_AIN2_UPPER1, /DIAG_U28_AIN2_UPPER2, /DIAG_U29_AIN1, /GND, /IMU_CS, /POD_5V_SENSOR, /POD_AUX3_SIGNAL, /POD_AUX4_SIGNAL, /POD_FRONT_BRAKE_SIGNAL, /POD_GNSS_RF, /POD_WHEEL_FRONT_SUPPLY, /PRE_6V3, /SD_DAT0, /SD_DAT1, /SD_DAT2, /SD_DAT3, /SENSOR_POWER_AUX_DVDT, /SENSOR_POWER_AUX_ILIM, /SENSOR_POWER_FRONT_DVDT, /SENSOR_POWER_FRONT_ILIM, /SENSOR_POWER_FRONT_OVP, /SENSOR_POWER_FRONT_UVLO, /SENSOR_POWER_REAR_ILIM, /SENSOR_POWER_REAR_UVLO, /SENSOR_POWER_TIRE_DVDT, /SENSOR_POWER_TIRE_ILIM, /SENSOR_POWER_TIRE_OVP, /SENSOR_POWER_TIRE_UVLO, /SETPOINT_5V, /SPI_MOSI, /SPI_SCK, /SUP_U18_CT, /SUP_U19_SENSE, /THERM_BIAS_MID, /THERM_EXC_2V495, /TIRE_CAN_OSC2

**What blocks them** (kicad-route `blocked-by.json`, heuristic corridors; 22 of the 78 open connections have no obstruction on their best layer):
- the sourced **D-PCB-7v2 In1.Cu no-tracks keepout** lies across 51 connections on their best layer (In1.Cu) and 78 on any layer;
- then J1 (7), U6 (5), the router's own new vias (for example /SD_CLK 5, /TIRE_CAN_INT_N 4, /PRE_6V3 4), U1 (4), the sourced **D-PCB-6 RF reference keepout** (4) and U12 (3);
- **/GND** has 29 open connections.

The keepouts were preserved (preservation `keepouts` PASS), not relaxed.

## Saved routed candidate (`candidate/`, written by kicad-route)

| File | sha256 |
|---|---|
| `candidate/telemetry-pod.kicad_pcb` (routed; equals `validated_board_sha256` and `delivered_board_sha256`) | **`19ed7954ab305b39f29d19f08fb619b4399cb6522869fba21b7712a52a310bdf`** |
| `candidate/telemetry-pod.kicad_pro` (original bytes) | `10002b987995765415313fa89da32ba9011160853596f1a78ff8fba24ac9b175` |
| `candidate/telemetry-pod.kicad_dru` (original bytes) | `ff62208301c38bca2c963a0682e0a2ee843d8a546bace3719340cfcca1b08d0d` |
| `candidate/telemetry-pod.kicad_sch` (original bytes) | `f5840ecc8a44a2e36cd05da9c3a14d80074919f441c3ef73a107dc98d5aea6a2` |

The complete structured result is `kicad-route/result.json`; the `--json` stdout object is `logs/stdout.json`. kicad-route's `RESULT.md`, `attempt.json`, `snapshot.json` and the validate artifacts (`candidate-drc.json`, `new-findings.json`, `preservation.json`, `blocked-by.json`, `pour-integrity.json`, `candidate-refill.json`, the terminal-component records) are under `kicad-route/`.

## Native DRC delta (kicad-cli `pcb drc --format json --severity-all --schematic-parity --units mm`, after `--refill-zones`)

| Type | Before: R5 board `8f3bc234…` | After: candidate `19ed7954…` | |
|---|---|---|---|
| lib_footprint_mismatch | 3 | 3 | inherited (17 total), unchanged |
| text_height / text_thickness | 7 / 7 | 7 / 7 | inherited, unchanged |
| silk_overlap / silk_over_copper / silk_edge_clearance | 35 / 27 / 1 | 35 / 27 / 1 | the 63 R5 silkscreen findings, unchanged; severities untouched |
| **via_dangling** | 0 | **34** | **new** |
| **track_dangling** | 0 | **27** | **new** |
| **Violations total** | **80** | **141** | +61 new, 0 resolved |
| Schematic parity | 0 | 0 | 0 new |
| Unconnected | 499 | **78** | −421 |

The before state matches kicad-route's own refilled baseline of the untouched input (80 pre-existing) and `kicad-route/before-drc-r5-board.json` (the R5 native DRC of the same bytes).

**Rule checks:** kicad-route loaded both rules files (`telemetry-pod.kicad_pro` and `telemetry-pod.kicad_dru`; `not_loaded` empty). The backend reads only a subset of custom `.kicad_dru` rules; the skipped ones (for example the D-PCB-1 0.15 mm intra-footprint clearances) are listed in `result.json` `unsupported`. **Every rule is still graded by KiCad DRC,** and `new_copper_netclass_geometry` PASS.

**Refill:** `refill_modified_board` false; `pour_integrity` PASS.

**Preservation** (`kicad-route/preservation.json`): project_files, board_outline, layers, stackup, board_setup, nets_and_netclasses, pad_connectivity, footprints, zones, keepouts, copper_graphics, protected_copper, new_copper_netclass_geometry, routing_scope, net_completion and pour_integrity are **all PASS**. This covers the fixed placement and pad/net identities, the 4-layer/1.6 mm stackup, and the RF/layer keepouts.

## Command and runtime

- **Runtime:** `~/git/kicad-route` at **`b5774496d8466b67ffa0362b6665fee2108155a3`** (= origin/main, clean tree; `tool_identity.kicad_route.dirty` false), run through `~/.local/bin/kicad-route` on the host's `/usr/bin/python3`:
  - Python **3.12.3**;
  - pcbnew **10.0.7-10.0.7~ubuntu24.04.1**;
  - kicad-cli **10.0.7** (sha256 `0dd2a47a…`);
  - builtin backend 0.23.1, build `owned-89a2efbf5305`, source sha256 `89a2efbf…`, Rust grid_router 0.23.1.
- **`kicad-route doctor`:** **PASS (25 checks)**; full output in `logs/doctor.txt`. It ran in a native-admit lease. The doctor reported `state read-only` as NOT_RUN: the STATE checkout is writable, so the optional read-only-state requirement does not hold.
- **Command** (`logs/command.txt`):

  `~/.local/bin/native-admit run --class suite --weight 4 --label route-1 -- ~/.local/bin/kicad-route --out <scratch>/route-1/out --json run --backend builtin --dir <isolated tree>/project --board telemetry-pod.kicad_pcb --schematic telemetry-pod.kicad_sch --budget 1500 --label route-1`

- **Flags:**
  - `--backend builtin` (qualified engine);
  - `--dir`/`--board`/`--schematic` explicitly select telemetry-pod;
  - `--budget 1500` (as assigned);
  - `--out` and `--label` set only output locations;
  - `--json` gives one structured stdout object.
- **Defaults kept, nothing copied from other boards:** protect `existing`, no net subset, no clearance overrides, no backend args or env, plane/pour handling default (not disabled).
- **Backend flags kicad-route chose itself:** `--escalation off --fab-tier standard --strict-sizes …` (see `process.commands`).
- **Isolated project:** a copy of the verified emission-7d5b0d4d design tree (558 files) with only `project/telemetry-pod.kicad_pcb` replaced by the R5 board. Project, rules and schematic are the original bytes. kicad-route snapshots the `${KIPRJMOD}/../` library directories itself.
- **Leases** (`logs/native-admit-events.jsonl`): doctor (test/1); route (suite/4); renders (test/1, admitted after a 10 s CPU-pressure wait).
- **Elapsed:** `runtime_s` 427.7 (backend and validation); wall 06:53:08.36 → 07:00:16.84Z.
- **Logs:** `logs/stdout.json`, `logs/stderr.log`, `logs/times.txt`.

## Renders (candidate-bound, kicad-cli pcb render)

`render/candidate-19ed7954ab30-front.png` and `render/candidate-19ed7954ab30-back.png`. **They show the INCOMPLETE routed candidate.**

## Not claimed

No release qualification is claimed. The carried items are unchanged, including BLE, the 29 unknown rows, J1 plug and sourced-none. Also unchanged: the electrical, thermal, RF and mechanical qualification, and the provenance gaps for the J1/U1/U2 poses, the holes, the outline and the antenna keepout. agent-521 decides the next action.
