# Changelog

## 2026-10-22 — Pod production preparation j6b: bound J1/U3 models, initial candidate, JP1-JP5 copper contract (`AGENTEE-207`, `FOMEMC-34`)

- The prepared scope now carries two project-local 3D models at `${KIPRJMOD}/inputs/models/`, recorded in
  `composition/project-models.json`:
  - the exact-part J1 header STEP (TE 1-776163-1 rev T, `connector-candidate/sources/c-1-776163-1-t-3d.stp`),
    with its sourced native pose;
  - the U3 NEO-M9N datasheet-derived visualization, which the captured `RF_GPS:ublox_NEO` member now references
    with zero transform.

  The j6 candidate's J1 reference did not resolve (`missing`), and U3 had no model at all. The CVM_776164-1
  rev F mating plug is not bound. These are visual/mechanical models only.
- The pipeline records the initial candidate identity of iteration 1. Native checks on the emitted design
  verify agent-509's JP1-JP5 ruling: on-board normally-open copper, not BOM, not DNP. They also rerun the
  J1 drilling audit. `model_check.py` verifies the native STEP export of both models.
- The production emission is regenerated (same agent-ee `81e387ee`, same plan bounds). It is reinstalled as
  the telemetry-pod project, with the models at `telemetry-pod/inputs/models/`. No campaign was launched.

## 2026-10-22 — Telemetry pod production preparation and re-emitted schematic (`AGENTEE-207` j6, `AGENTEE-445`)

- The production capture (`telemetry-pod/expansion/production-capture/`) runs on agent-ee `81e387ee`. The real
  `pod_driver` dry run prepares the bounded plan of record: 2 iterations, routing budget 900 s, placement
  timeout 1500 s and a derived watchdog of 8400 s. The production scope stages the five generic envelope
  obligations under agent-ee's reviewed source contract. No campaign was launched.
- `telemetry-pod/telemetry-pod.kicad_sch` and `.kicad_pcb` are now the production schematic emitted from the
  bound intent (305 components, 235 nets) and its forward-annotated, unplaced generation seed. The emitter
  inputs and stage receipts are retained in `evidence/emission-81e387ee/`. `make check PROJECT=telemetry-pod`
  passes all five steps. The v9 pilot snapshot (`13c0bfb`) stays in history and in its renders.

## 2026-10-18 — Telemetry Pod Document Reconciliation & 12 V Power Source Decision (`FOMEMC-31`)

Reconciled the `fome-mc` telemetry and SV650 harness documentation (`docs/TELEMETRY_AND_RACECHRONO.md` and `docs/WIRING_SV650_K7.md`) against the standalone Rung-3 telemetry pod specification ([`telemetry-pod/REQUIREMENTS.md`](telemetry-pod/REQUIREMENTS.md), revision 2, 2026-10-18, sha256 `09e02c8d9471aabfa5d25935c87f436370cf1be367a96425b35305a53ce93493`) under the owner's third-batch decisions (`2026-10-18`, `FOMEMC-31` / `pod-45`):

- **Owner Decision (`2026-10-18`, verbatim)**:
  - Power source: **"Harness splice on the relay circuit, own 2 A fuse"**
  - Travel ranges: **"130 and 70 mm"**
  - Combined owner choice: **"Harness splice on the relay circuit, own 2 A fuse; 130 and 70 mm"** (`2026-10-18`).
- **Discrepancy 3 — Pod `+12 V` Tap & Zero Draw from the ECU**:
  - `J1-27` (`+12V_MR`) is an ECU power input (`D21` `B340A-13-F` Schottky OR into `12V_RAW`), not an ECU output. Both `docs/TELEMETRY_AND_RACECHRONO.md` and `docs/WIRING_SV650_K7.md` now specify that the telemetry pod taps the switched `+12 V` main relay output (`R/Y` circuit that also feeds `J1-27`) on the harness side via its own `2 A` fuse, never draws power from the ECU (`J1-27` or `J1-30` `5V_SENSOR_2`), and regulates its own local `5.00 V ± 1%` (`200 mA`) ratiometric sensor supply (`J1-30` `5V_SENSOR_2` and `J1-31` `SGND` are not connected to the pod).
- **Discrepancy 5 — Suspension Travel Ranges (`130 mm` Fork / `70 mm` Shock) & `CHASSIS_ECU_GND` (`J1-34`)**:
  - Corrected the `docs/TELEMETRY_AND_RACECHRONO.md` Section 1 topology diagram (`SUSP` node) and prose from `120 mm` / `65 mm` to **`130 mm` front fork** and **`70 mm` rear shock** (**"130 and 70 mm"**), matching the `0x300` CAN frame table (`0..130.00 mm` and `0..70.00 mm`) and `docs/WIRING_SV650_K7.md` Section 7 with one value per quantity across both documents.
  - Replaced `PGND` on `J1-34` in `docs/TELEMETRY_AND_RACECHRONO.md` with **`CHASSIS_ECU_GND`** (matching `docs/WIRING_SV650_K7.md` and `io-map.csv`), documenting that the pod grounds to the chassis ground point (`B/W` circuit) shared with the ECU's `CHASSIS_ECU_GND` (`J1-34`).
- **Discrepancy 4 & Criterion 8 (`POD-AC-8`) Bench Obligation — Lua Ingest of `LeanAngle` (`0x301`)**:
  - Updated the TunerStudio Lua ingest script in `docs/TELEMETRY_AND_RACECHRONO.md` Section 3.3 (`onCanBrakesAndLean`) to decode `LeanAngle` (`0x301` bytes `4..5`, 1-based Lua offset `5`, `0.01 deg/LSB`, `-65..+65°`) into `Sensor.new("LuaGauge1")` and `PitchAngle` (`0x301` bytes `6..7`, offset `7`, `0.01 deg/LSB`, `-45..+45°`) into `Sensor.new("LuaGauge2")`.
  - Recorded the bench obligation for Pod Acceptance Criterion 8 (`POD-AC-8`): load the updated TunerStudio Lua script and verify that the deployed ECU firmware supports the Lua sensors and logs `LuaGauge1` (`LeanAngle`), `AuxLinear1..2` (front/rear brake pressure), and `AuxLinear3..4` (`130 mm` fork / `70 mm` shock travel) in `.mlg`. No C++ firmware change is included here; built-board acceptance and firmware compatibility remain bench obligations.
  - Aligned the topology and overview with revision 2's fixed ESP32-S3-WROOM-1, LSM6DSO32, NEO-M9N, 200 Hz travel and 100 Hz IMU CAN rates.
- **Pinned Planning Document Identities (`2026-10-18` Decision)**:
  - `docs/TELEMETRY_AND_RACECHRONO.md`: git blob `3dafed620a10f8fba209c2707b8f832eec6f6303`, sha256 `acaeab4504761c5ae1776eff185d1481d52a2637b501c7c29381a57547a41624`.
  - `docs/WIRING_SV650_K7.md`: git blob `bb0ff8c1a32faef6e7cc8fe1e67538829544b106`, sha256 `52920d87d8bc396aa702f4dd8d7ea96751cfcec7a9ed013575857104c96c03bf` (after merging the 2026-10-18 documentation audit 643245f; the pod section is Section 7).
  - Downstream `agent-ee` pod `spec-record.json` / requirement-map (`pod-01`, `pod-02`, `pod-44`) must cite the final corrected `FOMEMC-31` commit and these blob identities. Updating that external record remains with the coordinator; it is not verified here.

## 2026-10-18 — Telemetry pod project

The tail-cowl CAN1 telemetry pod gets its own KiCad project in this repository
(`FOMEMC-28`; agent-ee epic `AGENTEE-157`, item pod-42). Its requirements are the owner's
"Telemetry pod requirements" (2026-10-17, @Heath; captured markdown sha256
`c5128ef9391e2114e7a399b352a957472ad26b93ca76e3179cc04b2b51194572`), which take their
fome-mc facts from commit `c582b29`. Only the skeleton is added; agent-ee generates the
design into it later, and open owner gates (e.g. `FOMEMC-31`, the 12 V tap and travel
ranges) are not decided here.

- `telemetry-pod/`: empty KiCad 10 placeholders `telemetry-pod.kicad_{pro,sch,pcb}`, an
  empty `sym-lib-table`, an `fp-lib-table` with `ampseal` →
  `${KIPRJMOD}/../libs/footprints/ampseal.pretty`, and empty `sheets/`, `contracts/`,
  `export/`.
- `toolchain/versions.toml`: `[projects.telemetry-pod]`, so `make doctor` checks its files
  and `make erc|drc|check PROJECT=telemetry-pod` run on its snapshots.
- `.gitignore`: `telemetry-pod/export/*.net`, `BOM-telemetry-pod.csv` and
  `CPL-telemetry-pod.csv` are tracked like fome-mc's `export/` files.

## 2026-10-17 — Generator direction

Owner decisions for the AI-driven PCB generator (agent-ee, kicad-route, fome-mc), as
they bear on this repository:

1. Generation is a repair campaign from an empty candidate; fome-mc is the target product and the last benchmark rung (rung 4: 15 sheets, 4 layers, 514 footprints — 494 populated + 16 DNP + 4× M4 mounting holes H1..H4). Rung 2 is one fome-mc sheet (PSU or one wideband channel).
2. Boards are composed from verified reference blocks, then adapted. fome-mc's sheets, built from Polygonus, Universal-112 and wideband Rev C, are the reference library; capture plan in `docs/BLOCK_LIBRARY.md`.
3. Stages are requirements, parts, schematic, placement, routing, verification and fab package. Routing already uses kicad-route (`toolchain/ROUTING.md`, KRT default).
4. Placement is a new agent-ee stage; it does not change this repository.
5. Every stage keeps the evidence model: hashed inputs, recorded tool versions, sandboxed runs, independent review. FOMEMC-1..27 findings seed agent-ee's benchmark (`docs/SEEDED_DEFECT_BENCHMARK.md`).
6. Tools stay upstream with versions and hashes recorded per run. `scripts/generate_fab_package.py` exports and normalizes `export/gerbers/` and `reports/toolchain/fab-manifest.json` from a pinned commit (`FOMEMC-21`), and `scripts/export_bom_cpl.py` generates `export/BOM-fome-mc.csv` and `export/CPL-fome-mc.csv` (`FOMEMC-24`).

## 2026-10-16 (Rev 2) — Power Remediation & Plane Milestones `FOMEMC-1` .. `FOMEMC-4`

Completed the 6-step power/ERC remediation and all four follow-on architecture & firmware enhancements (`FOMEMC-1`, `FOMEMC-2`, `FOMEMC-3`, `FOMEMC-4`):

### 1. Power Architecture, Keep-Alive & Zero-ERC Remediation (`7c3806c`)
- **Ignition & Main Relay Diode-OR Keep-Alive (`sheets/Keep_Alive.kicad_sch`, `sheets/lowside_quad.kicad_sch`, `sheets/stepper_etb.kicad_sch`)**:
  - Added `D20` and `D21` (`B340A-13-F` 40 V 3 A Schottky, LCSC `C64982`) diode-OR combining `+12V_IGN_SW` (`J1-26`) and `+12V_MR` (`J1-27`) onto `12V_RAW`.
  - Connected `12V_SENSE` (`R96 = 82 kΩ / R97 = 10 kΩ` -> `U26.45` `PC5` `12V_DIVIDED`) upstream of `D20` on `/12V_IGN_SW` so key-off is immediately detected while `/12V_MR` keeps `12V_RAW` alive.
  - Routed `PE0` (`U26.141` `MAIN_RLY`) through `RN9/RN10` into `U1202` (`VNLD5090` channel 2, `U1202.6`) with `D209` (`B340A-13-F`, `C64982`) flyback clamp to `/12V_MR` on `J1-14` (`MAIN_RLY`), enabling deterministic post-key-off `.mlg` `f_sync()` flush and stepper parking before main relay release.
  - Retained `Perm_Live` (`J1-28`) -> `D16` (`B5819W` `C8598`) -> `U41` (`MIC5205-3.3YM5` 3.3 V backup LDO, LCSC `C5370979`) -> `D17` (`Keep_Alive.kicad_sch`) -> `D7` (`B5819W` `C8598` in `mcu.kicad_sch`, diode-ORed with `D6` from `BT1` and `D8` from `+3V3`) into `U26.6` (`VBAT`).
- **Load-Dump, Reverse-Battery & Regulator Hardening (`sheets/psu.kicad_sch`)**:
  - Removed the orphaned `U46` (`LM2733XMFX` boost on an LDO symbol) + `L3, D18, C107`, orphaned `BD3571` regulators, and `U28` (`S3225SMD32.768KOSC` 32.768 kHz oscillator).
  - Upgraded `D1` (`12V_RAW`) and added `D22` (`12V_MR`) as unidirectional **`SMCJ24A`** (`C224045`, `24 V` standoff / `38.9 V` max clamping sacrificial crowbar TVS diodes) ahead of **`Q1` (`AO4485` P-MOSFET reverse-polarity block, `C51499`)** + `D19` (`BZT52C12` `C43491` 12 V gate Zener) + `R124` (`47 kΩ` `C25819`), eliminating the `~0.45 V` / `0.7 W` series Schottky (`D2` `SS34`) drop.
  - Routed `12V_PROT` through the `L1` (`2.2 µH`, `C75646`) + `C6` (`47 µF` Panasonic `EEHZC1H470P` hybrid polymer, `C454346`) LC filter into **`U3` (`LMR16020PDDAR` 60 V 2 A step-down buck, `C190006`)**, **`U1, U2` (`2× TLS115D0E` tracked 5 V sensor LDOs, `C3747428`)**, and **`U6` (`TLV75733PDBVR` 3.3 V 1 A low-dropout LDO, `C485517`, `0.25 V` typ dropout)**, achieving a **`V_BATT ≈ 4.8 V` steady-state guaranteed floor** (`U3` `4.30 V` minimum operating `VIN`, with `C1/C6` riding through sub-ms cranking dips).
  - Upgraded 12 V rail MLCCs (`C2, C4, C5, C7, C8, C10, C108, C1201`) to Murata `GCJ` soft-terminated 50 V X7R parts and resolved all 60 schematic ERC errors down to **`0` ERC errors** across all 21 sheets (including isolating `/knock/FILTERED_1` `U26.14` and `/knock/FILTERED_2` `U26.15`, separating `VDDA_WBO1` / `VDDA_WBO2`, and fixing `U4/U5` `MCP2551-I-SN` Pin 5 `Vref`).

### 2. `FOMEMC-1` — External 1-Bar Barometer Default & Single-Pour Flood Potting (`c29fde6`)
- Configured `J2-6` (`AV3_BARO_MAP2` / `PA2` / `EFI_ADC_2`) in `fome-fw/firmware/config/boards/fome-mc/board_configuration.cpp` to default to an external automotive **GM `12614970` / Delphi `PS10150` 1-bar absolute pressure sensor** (`MT_GM_1_BAR`, `10–105 kPa` across `0–5 V`, powered by `J1-29` `5V_SENSOR_1` and `J1-31` `GND`).
- Marked onboard `U24` (`LPS25HBTR`) as `DNP` for potted builds (`lps25BaroSensorScl/Sda = Gpio::Unassigned` by default) and removed the cylindrical `U24` potting dam keep-out rings (`baro.dam.id` / `baro.dam.od`) from `fome-mc.kicad_pcb`, enabling **uniform single-pour flood potting** in an unvented aluminum enclosure with zero lid penetration or capillary wicking risk.

### 3. `FOMEMC-2` — Onboard `ATWINC1500-MR210UB` U.FL Wi-Fi (`SPI4`) & Remapped WBO1/2 Reset/Boot Pins (`f3b0f47`)
- Integrated **`U29` (`ATWINC1500-MR210UB`, LCSC `C1558703`)** 2.4 GHz 802.11b/g/n Wi-Fi module with integral U.FL external antenna receptacle (`R122 = 10 kΩ` pull-up on `SPI_CFG/WAKE/CHIP_EN`, `C106 = 100 nF` `C161115` decoupling) on `SPI4` (`PE2 = SCK`, `PE5 = MISO`, `PE6 = MOSI`, `PE4 = CS`, `PE3 = IRQ`, `PC13 = RESETN`) in `sheets/mcu.kicad_sch` and `fome-mc.kicad_pcb` (initially placed at `(40.0, 134.0 mm)`; relocated to `(166.0, 131.5 mm, rotated 90°)` in `FOMEMC-27` for `H3`/`H4` `M4` corner hole clearance).
- Remapped `WBO1_NRST`, `WBO1_BOOT0`, `WBO2_NRST`, and `WBO2_BOOT0` from `PE2..PE5` to **`PD4..PD7` (`U26.118, 119, 122, 123`)**.
- Enabled `USE_WIFI = yes` in `fome-fw/firmware/config/boards/fome-mc/board.mk` and configured `SPI4` Wi-Fi hooks in `board_configuration.cpp` for wireless TunerStudio (`TCP :29000`, `wifi_console.cpp`) and the built-in HTTP SDNAND `.mlg`/`.zip` log web server (`HTTP :80`, `http_file_server.cpp`) via an O-ring-sealed U.FL-to-RP-SMA bulkhead pigtail.

### 4. `FOMEMC-3` — 4 GB Soldered LGA-8 SDNAND & Automatic Ring-Buffer Log Pruning (`8bee1ee`)
- Upgraded `U25` from 4 Gbit / 512 MB (`XTSD04GLGEAG` / `CSNP4GCR01-AMW`) to **32 Gbit / 4 GB (`CSNP32GCR01-AOW`, LCSC `C2841139`, 394 in stock; pin-compatible with `MKDV32GCL-STH` `C5199868`)** in the same `6 × 8 mm` LGA-8 footprint on 4-bit `SDMMC1` (`PC8..PC12, PD2`), expanding onboard `.mlg` logging capacity by `8×` to **`~160.5 hours` at `50 Hz`** (`~80.2 hours` at `100 Hz`, `~32.1 hours` at `250 Hz`).
- Added automatic oldest-`.mlg`/`.teeth` ring-buffer pruning (`ensureSdFreeSpace()`, `deleteOldestLogFile()`, `sd_log_ring_buffer.h`) in `fome-fw/firmware/console/binary_log/sd_file_log.cpp` whenever free space drops below `64 MiB` (`25%` on smaller volumes), `.mlg` file count reaches `480`, or `f_write()` hits disk-full, covered by `SdLogRingBuffer.*` GTest unit tests.

### 5. `FOMEMC-4` — `CAN1` Motorsport Telemetry Pod, RaceChrono Pro & Action Camera Integration (`232daec`)
- Configured `CAN1` (`J2-28` `CAN1_H` / `J2-29` `CAN1_L`, 500 kbps via `U4` `MCP2551-I-SN`) in `board_configuration.cpp` to broadcast `FOME_CAN_verbose.dbc` (`0x200..0x207`: RPM, TPS1, STPS, Gear, MAP, CLT, IAT, VBatt, InjPW, Knock, WBO1/2 Lambda) at **50 Hz (`20 ms`, `canSleepPeriodMs = 20`)** and receive incoming Bosch Motorsport MM5.10 6-axis IMU frames (`0x174`, `0x178`, `0x17C`; RaceChrono Pro decodes all 6 axes while FOME `can_imu.cpp` decodes `YawRate`, `AccelLat`, `AccelLon`, `AccelVert`) by default (`imuType = IMU_MM5_10`), with `can_imu_test.cpp` unit test coverage and full integration documentation in [`docs/TELEMETRY_AND_RACECHRONO.md`](docs/TELEMETRY_AND_RACECHRONO.md).

### 6. `FOMEMC-5` .. `FOMEMC-27` — Adversarial Hardware Remediation, 100% PCB Parity, Full Copper Routing, Thermal/HV Hardening, Mode A2 VR Conditioning, Wide WBO Heater Buses, M4 Mounting Holes, Per-Sheet Contracts, Fab Package & Zero-ERC / Zero-DRC Closure
- **`FOMEMC-5` .. `FOMEMC-8`**: Remediated all adversarial hardware review findings across power/keep-alive (`U41` `MIC5205-3.3YM5` `EN` strap, `C6` `47 µF` hybrid polymer bulk capacitor, `D1/D22` `SMCJ24A` crowbar TVS, `Q1` `AO4485` reverse-battery PMOS), analog/ADC (`U23` `REF3333AIDBZR` fixed `3.30 V` `VREF+` reference with `5V_SENSE_DIVIDED` `U26.50` / `PF12` ratiometric sensor compensation, `3.3 nF` `C472819` knock filters), ignition/low-side/H-bridge (`R213/R214` `0.20 Ω` `1206` `C25335` stepper sense resistors with `VREF = 0.767 V` via `R215 = 33 kΩ / R216 = 10 kΩ` -> `0.77 A` limit), and CAN/USB/Wi-Fi (`U4/U5` `MCP2551` `RS` `10 Ω` `C22859` slope control, `U29` `ATWINC1500-MR210UB` `CHIP_EN` / `RESETN` / `WAKE` biasing).
- **`FOMEMC-9` (`6af7bf4`)**: Synchronized all footprints and nets between `fome-mc.kicad_sch` and `fome-mc.kicad_pcb` (`0` schematic parity errors) and added `Package_SO:MSOP-10_3x3mm_P0.5mm` for `U13` and `U14` (`MAX9924UAUB+`, `LCSC C143633`).
- **`FOMEMC-10`**: Completed 100% 4-layer copper trace routing, power/ground plane fill, and thermal/via stitching in `fome-mc.kicad_pcb` (`0` `unconnected_items`, `0` DRC errors, `0` `track_dangling`, `0` `via_dangling`, `routing_complete: true` in `make analyze`).
- **`FOMEMC-11`**: Restored `"min_resolved_spokes": 2` in `fome-mc.kicad_pro` and eliminated all 24 single-spoke GND thermals in `fome-mc.kicad_pcb` via 19 dedicated GND stitching vias + `0.254 mm` `F.Cu` tie tracks and `ZONE_CONNECTION_FULL` pad settings (`0` `starved_thermal` warnings).
- **`FOMEMC-12`**: Enabled teardrops (`"td_enabled": true` in `fome-mc.kicad_pro` and `1,642` pad/via teardrop definitions in `fome-mc.kicad_pcb`), upsized `7` `0.45/0.20 mm` vias to `0.5994/0.2997 mm` where clearance permits, and widened `392` `0.127 mm` track segments to `0.200–0.254 mm`.
- **`FOMEMC-13`**: Added `3× 74HCT125D` (`U1003, U1103, U1203`, LCSC `C5947` + `100 nF` decoupling `C1003, C1103, C1203` `C161115`) `+5V` CMOS level-translating buffers between `3.3 V` MCU outputs (`10 kΩ` pull-downs `RN5, RN7, RN9` `4D03WGJ0103T5E` `C29718`) and `1 kΩ` series arrays (`RN6, RN8, RN10` `4D03WGJ0102T5E` `C20197`) in `sheets/lowside_quad.kicad_sch` so all `VNLD5090TR-E` low-side channels (`U1001..U1202`) receive `4.9 V` gate drive (`> 3.25 V` `V_IH(max)`).
- **`FOMEMC-14`**: Populated `R219 = 1.5 kΩ` `1%` (`0603`, LCSC `C22843`) pull-up to `/5V_SENSOR_1` on `/AV6` (`J2-8`, `PA5`) on root sheet `fome-mc.kicad_sch` and `fome-mc.kicad_pcb` (`(152.75, 93.85)`) to bias the passive SV650 K7 6-speed gear-position resistor ladder, and populated `R212 = 2.2 kΩ` (`0603`, LCSC `C22976`) pull-up to `/12V_MR` on `/LS8` (`J1-13` Tachometer) in `sheets/stepper_etb.kicad_sch`.
- **`FOMEMC-15`**: Upgraded `C12` (`+5V` buck output capacitor on `sheets/psu.kicad_sch`) from `6.3 V` X5R (`C19666`) to Samsung **`CL10A106MA8NRNC` (`10 µF 25 V X5R 0603`, LCSC `C96446`)** and added `PWR_FLAG` on `5V_SENSOR_SUPPLY` in `sheets/triggers.kicad_sch`.
- **`FOMEMC-16`**: Placed and routed `U1003, C1003, U1103, C1103, U1203, C1203, R219` (`0` parity errors, `0` unconnected items), added `>= 1.20 mm` `F.Cu` rule-area collector keepouts around `Q201..Q204` (`400 V` peak IGBT tabs), widened `/IGN1_COIL../IGN4_COIL` traces to `1.20 mm` nominal (`0.60–1.50 mm`), added filled `F.Cu` and `B.Cu` copper heat-spreader zones on `/WBO1_H-` (`Q301.2`) and `/WBO2_H-` (`Q401.2`), and refreshed `export/BOM-fome-mc.csv` and `export/CPL-fome-mc.csv`.
- **`FOMEMC-17` (PSU 50 V X7R Capacitor Upgrades, Injector `42 V` Active Clamp DNP & `LMR16020` Brownout Margin)**:
  - Upgraded `C4` (`4.7 µF` input RC damper on `/12V_PROT` via `R2 = 1 Ω` `C25086`) from `16 V X5R 0603` (`C19666`) to **`4.7 µF 50 V X7R 1210` Murata `GCJ32ER71H475KA12L` (`LCSC C417122`, soft-terminated AEC-Q200)** to withstand up to `38.9 V` `SMCJ24A` clamping transients without voltage overstress or severe Class-II DC-bias derating.
  - Upgraded `C2, C5` (`/12V_PROT` input caps on `U1/U2` `TLS115D0EJ`) and `C7` (`/VBOOST` input cap on `U3` `LMR16020PDDAR`) from `0603` (`C15849`) to **`1 µF 50 V X7R 0805` Murata `GCJ21BR71H105KA01L` (`LCSC C354368`, soft-terminated AEC-Q200)**; upgraded `C8` (`10 nF` soft-start cap) to **`50 V X7R 0603` `GCJ188R71H103KA01D` (`LCSC C344025`)**; and upgraded `C10` (`100 nF` bootstrap cap) to **`50 V X7R 0603` `GCJ188R71H104KA12D` (`LCSC C161115`)**.
  - Marked `D201..D204` (`B340A-13-F` `C64982` on `INJ1..4` `/LS1../LS4`) as **DNP** (`exclude_from_bom`, `dnp`) so `U1001/U1002` (`VNLD5090TR-E`) demagnetize high-Z fuel injectors via their internal **`42 V` active Zener clamps** (`~0.83 ms` turn-off vs `~4.8 ms` with a `14 V` Schottky clamp to `+12 V`, preventing nonlinear fuel delivery and cylinder-to-cylinder AFR skew at `10,500 RPM`), while `D205..D209` remain populated for inductive solenoids/relays (`/LS5../LS8`, `/MAIN_RLY`).
  - Reconciled `U3` (`LMR16020PDDAR`) brownout margin across all documentation: TI `LMR16020` has a **`4.30 V` minimum operating `VIN`** (internal `VIN` UVLO rising threshold `4.0 V` typ / `4.3 V` max and falling threshold `3.8 V` typ), with `Pin 2 (VIN)` and `Pin 3 (EN)` tied to `/VBOOST`, `R3 = 10 kΩ` (`C25744`) on `Pin 4 (RT)`, and `R5 = 12 kΩ / R6 = 68 kΩ` on `Pin 5 (FB)` setting `+5V = 5.00 V`. With `D20/D21 + Q1 + L1` series drop (`~0.50 V`), `U3` operates in low-dropout pass-through as `VIN` approaches `5.0 V`, while `+3V3` (`U6` `TLV75733PDBVR`, dropout `0.25 V` max) stays fully regulated (`3.30 V`) until `U3` reaches its `4.30 V` minimum operating `VIN` (`V_BATT ≈ 4.8 V` steady-state guaranteed floor, with `C1 + C6 = 2 × 47 µF` riding through sub-millisecond cranking dips).
- **`FOMEMC-18` (`U29` `ATWINC1500-MR210UB` Footprint Land Pattern & `1P3V_TP` Bypass Capacitors)**:
  - Corrected `U29` (`ATWINC1500-MR210UB`) footprint in `libs/footprints/ampseal.pretty/ATWINC1500-MR210UB.kicad_mod` and `fome-mc.kicad_pcb` to match Microchip `DS70005304F` `Figure 2-2` & `Figure 10-1` (`14.73 × 21.72 mm`, `1.9 × 0.8 mm` / `0.8 × 1.9 mm` pads at `1.016 mm` pitch with exact physical pin-group gaps around the RF shield/keep-out and `3.7 × 3.7 mm` ground paddle `Pad 29` with 2×2 thermal/ground via array).
  - Added required **`C111` (`10 µF` 25 V X5R `0603`, `LCSC C96446`)** and **`C112` (`10 nF` 50 V X7R `0603`, `LCSC C344025`)** bypass capacitors on `U29` Pin 24 (`1P3V_TP`, net `/mcu/WIFI_1P3V`) placed `< 2 mm` from Pin 24 per `DS70005304F` Table 3-1 / Section 5.1.
- **`FOMEMC-19` (`/IGN1_COIL../IGN4_COIL` `HV_IGN` `0.50 mm` Clearance & `U25` SDNAND Local Decoupling)**:
  - Added dedicated `HV_IGN` netclass (`0.50 mm` minimum copper clearance, `1.2 mm` track width) for `/IGN1_COIL../IGN4_COIL` in `fome-mc.kicad_pro` across all 4 copper layers (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`), providing `> 0.50 mm` separation everywhere for the `380–400 V` `FGD3040G2-F085` IGBT collector clamp pulses.
  - Added dedicated **`C113` (`4.7 µF` `0603`, `LCSC C19666`)** and **`C114` (`100 nF` `0603`, `LCSC C161115`)** local decoupling capacitors `< 2.0 mm` from `U25` (`CSNP32GCR01-AOW` 4 GB SDNAND) Pin 4 (`VDD`).
- **`FOMEMC-20` (Zero Schematic ERC Violations)**:
  - Cleaned up all `unconnected_wire_endpoint`, `isolated_pin_label`, `multiple_net_names`, `same_local_global_label`, `similar_labels`, and `pin_to_pin` warnings across all sheets so `kicad-cli sch erc` reports **`0` violations (`0` errors, `0` warnings)**. Total schematic components = **`510`** (**`494`** populated in BOM/CPL with 100% LCSC coverage after excluding `16` DNP footprints: `BT1`, `D201..D204`, `J8`, `J9`, `J11..J16`, `JP1`, `JP2`, `U24`; plus `4× M4` mounting holes `H1..H4` = **`514`** total board footprints).
- **`FOMEMC-21` (Reproducible Fabrication Package & Manifest)**:
  - Added `scripts/generate_fab_package.py` to export and normalize `export/gerbers/` (`14` Gerber/Excellon/job files with deterministic commit timestamps) and write `reports/toolchain/fab-manifest.json` (`22` verified artifacts) recording sha256 hashes of the source schematic/board, Gerbers, drills, netlist, and BOM/CPL. Tracked `export/fome-mc.net` in git (`!export/fome-mc.net`).
- **`FOMEMC-22` (Per-Sheet Boundary Contracts)**:
  - Added machine-checked per-sheet boundary contracts in `contracts/*.interface.json` (`633` invariants) and `docs/SHEET_CONTRACTS.md` covering all 15 schematic sheet files (21 instances) and verified them in `scripts/verify_io_map.py`.
- **`FOMEMC-23` (Documentation, Netlist & BOM Claim Reconciliation)**:
  - Reconciled all component references, LCSC part numbers, sheet instance counts, MCU pin assignments (`PF12` `5V_SENSE_DIVIDED`, `PD12/10/11` & `PD13/9/8` `ETB1/2`, `PC1, PC2, PA1..PA5` `J2-1..8`), `DRV8825` `0.77 A` current limit (`0.20 Ω` `R213/R214` `C25335`, `VREF = 0.767 V` via `R215 = 33 kΩ / R216 = 10 kΩ`), `D201..D204` DNP status, and Plane issue IDs (`FOMEMC-13..27`) across `io-map.csv`, `README.md`, `docs/DESIGN.md`, `docs/VALIDATION.md`, `CHANGELOG.md`, `docs/POTTING_AND_ENCLOSURE.md`, `docs/BLOCK_LIBRARY.md`, and `scripts/render_docs.py`.
- **`FOMEMC-24` (100% BOM & CPL Parity and LCSC Normalization)**:
  - Added `scripts/export_bom_cpl.py` and regenerated `export/BOM-fome-mc.csv` and `export/CPL-fome-mc.csv` (`494` populated components across `102` BOM lines, `16` DNP footprints and `4` `H1..H4` mounting holes excluded, `C1` and `C6` included in CPL, `100%` LCSC coverage, and 1-to-1 `(value, package) -> LCSC` mapping including `R7/R8 = 10 Ω` `C22859` vs `R9/R10 = 120 Ω` `C22787`, `10 nF 0603` `C344025`, and `100 nF 0603` `C161115`).
- **`FOMEMC-25` (`MAX9924UAUB+` Mode A2 Adaptive Peak Threshold & `VBAT` `4 KB BKPSRAM` Keep-Alive Without LSE Crystal)**:
  - **`circuit-001` (`U13, U14` `MAX9924UAUB+` Mode A2)**: Wired both `U13` and `U14` (`MAX9924UAUB+`, `LCSC C143633` in `sheets/triggers.kicad_sch`) in **Mode A2 (Internal Adaptive Peak Threshold + Internal Bias + Zero-Crossing Watchdog Enabled)** per `MAX9924` datasheet Table 1 (page 12), Bias Reference (page 13), and Figure 3 (page 15): Pin 6 (`ZERO_EN`) = `GND` (enables the internal `85 ms` zero-crossing watchdog timer), Pin 9 (`INT_THRS`) = `GND` (enables the internal adaptive peak threshold generator), Pin 4 (`BIAS`) = `GND` (switches in the internal `2.5 V` `VCC / 2` bias reference to bias `IN+`/`IN-` via `R35..R38 = 10 kΩ`), and Pin 8 (`EXT`) = `no_connect` (`NC` in Mode A2). Placed `C38` and `C39` (`100 nF` `0603` `C161115`) `< 2 mm` from `U13`/`U14` Pin 10 (`VCC = /5V_SENSOR_1`) in parallel with `C109` and `C110`.
  - **`circuit-002` (`VBAT` Backup SRAM `4 KB BKPSRAM` & Backup Register Keep-Alive)**: Documented that `PC14/OSC32_IN` and `PC15/OSC32_OUT` on `U26` (`STM32H753ZIT6`) are `no_connect` (no 32.768 kHz LSE crystal is populated, and `U28` was removed), so `VBAT` (`U41` `MIC5205-3.3YM5` via `D16/D17` + `D6/D7/D8` `B5819W` `C8598` + `BT1` `CR2032` DNP) powers the **`4 KB BKPSRAM` and 32 backup registers (`RTC_BKPxR`)** for fast-reboot state, knock/LTFT adaptation tables, and fault-code retention across battery disconnects rather than key-off wall-clock RTC timekeeping (active-run timestamps use the `8 MHz` HSE `Y1`, GPS, or Wi-Fi NTP).
- **`FOMEMC-26` (Wide Low-Resistance Copper Buses for `/WBO1_H-` and `/WBO2_H-`)**:
  - Routed `/WBO1_H-` (`Q301` Pad 2 -> `J1-23`) and `/WBO2_H-` (`Q401` Pad 2 -> `J1-25`) in `fome-mc.kicad_pcb` with wide (`>= 1.50 mm`) low-resistance copper buses (`<= 0.05 Ω` end-to-end trace resistance per channel, `< 0.13 W` trace loss at `1.6 A RMS` and `< 0.45 W` at `3.0 A` cold-start peak), eliminating the `1.56 W` trace heating and `0.65 V` voltage drop of the previous `0.254 mm` tracks.
- **`FOMEMC-27` (4× `M4` Corner Mounting Holes `H1..H4` & Zero-Warning DRC)**:
  - Added the 4× `M4` (`Ø 4.3 mm` NPTH) corner mounting holes `H1..H4` in `fome-mc.kicad_pcb` at `(30.0, 29.0)`, `(184.0, 29.0)`, `(30.0, 136.0)`, and `(184.0, 136.0)` (`154.0 × 107.0 mm` centers on the `162.0 × 115.0 mm` board), relocated `U29` (`ATWINC1500-MR210UB`) to `(166.0, 131.5 mm, rotated 90°)` with `C106, C111, C112` at `X = 178.5 mm` for `H4` corner clearance, and resolved all silkscreen overlaps (`C1203`/`U1203` and custom field visibility on `F.SilkS`) for a clean **`0`-error, `0`-warning** DRC and ERC pass.

---

## 2026-10-16 (Rev 1) — `fome-mc`: Initial Single-PCB Motorcycle ECU Integration (`f5abd10`)

Integrated the `fome-mc` STM32H7 processor core, `Polygonus-Universal-112` carrier circuitry, and two `wideband_controller` Rev C channels onto a single `162.0 mm × 115.0 mm` 4-layer PCB (`fome-mc.kicad_sch` / `fome-mc.kicad_pcb`) targeting the 2007 Suzuki SV650 (K7 dual-plug V-twin). *(Note: Where superseded by Rev 2 above—such as `D20/D21` + `PE0` `MAIN_RLY` keep-alive, `LMR16020PDDAR` + `AO4485` + `TLV75733PDBVR`, `FOMEMC-1` external baro default, `FOMEMC-2` `ATWINC1500-MR210UB` Wi-Fi + `PD4..PD7` WBO reset/boot, and `FOMEMC-3` 4 GB `CSNP32GCR01-AOW` SDNAND—the Rev 2 specification governs.)*

### Hardware Changes (`halbritt/fome-mc`)
- **Form Factor & Sealed Harness Connectors**:
  - Replaced the 107-pin Polygonus board-to-board headers (`J4..J7`) and the unobtainable Molex CMC 112-pin header with two 35-pin TE Connectivity AMPSEAL right-angle PCB headers: `J1` (`776163-1`, Key 1 Black, LCSC `C722761`) and `J2` (`776163-2`, Key 2 Grey, LCSC `C722762`).
  - Resized the 4-layer PCB outline to `162.0 mm × 115.0 mm` with 4× M4 corner mounting holes (`154.0 mm × 107.0 mm` centers).
- **Dual Onboard Bosch LSU 4.9 Wideband Controllers (`wbo1.kicad_sch`, `wbo2.kicad_sch`)**:
  - Integrated two complete `wideband_controller` Rev C circuits (`U301..U309` for `WBO1`, `U401..U409` for `WBO2`: `STM32F042K6T6` `C69216`, `MCP6004` `C50282`, `AD8628` `C29309`, `REF3033` `C36658`, `XC6206P332MR` `C5446`, `VND14NV04` `C2649436` heater FET) and two `TJA1051T/3` CAN transceivers (`U307`, `U407`, `C38695`) onto internal 500 kbps `CAN2` (`PB12/PB13` via `U5` `MCP2551-I-SN`).
  - Hardware-strapped `WBO1` (`PB1 = GND`, `PA8 = Float` -> `CanIndexOffset = 0`, CAN IDs `0x190/0x191`) and `WBO2` (`PB1 = Float`, `PA8 = +3.3V` -> `CanIndexOffset = 1`, CAN IDs `0x192/0x193`) so broadcast `WB_MSG_SET_INDEX` frames cannot clobber both controllers to the same CAN ID.
  - Removed duplicate 120 Ω termination resistors from the internal `CAN2` transceivers (fixing the Universal 112 triple-termination 40 Ω bus overload).
  - Routed `STM32H753` pins `PD4..PD7` (remapped from `PE2..PE5` in `FOMEMC-2`) to `WBO1_NRST`, `WBO1_BOOT0`, `WBO2_NRST`, and `WBO2_BOOT0` for sequential single-node OpenBLT firmware updates and reset recovery after potting.
- **Ignition Drivers (`ign_igbt.kicad_sch`, `ign4.kicad_sch`)**:
  - Added 4× `FGD3040G2-F085` (400 V, 30 A, TO-252, LCSC `C606124`) ignition IGBTs (`Q201..Q204`) on `J1-6..J1-9` (`IGBT1..4`, driven by `PB3, PG15, PG14, PG13` through `MIC4427` `U42/U43` in `/ign1/` with 10 kΩ gate-emitter bleeders `R205..R208` and 15 Ω gate resistors `R201..R204`).
  - Routed 4× 5 V push-pull logic coil outputs (`IGN1_LOG..4_LOG` on `J2-23..J2-26`, driven by `PG12..PG9` through `MIC4427` `U44/U45` in `/ign2/` and 100 Ω series resistors `R112..R115`).
- **Injector, Auxiliary Low-Side, Main Relay, Tachometer & Dash Outputs (`lowside_quad.kicad_sch`, `stepper_etb.kicad_sch`)**:
  - Dedicated 4× `VNLD5090TR-E` channels (`U1001, U1002`, `C222209`) with `B340A-13-F` (`C64982`, marked DNP in `FOMEMC-17`) on `INJ1..4` (`J1-1..J1-4`, `PG5..PG8`).
  - Dedicated 4× `VNLD5090TR-E` channels (`U1101, U1102`) with `B340A-13-F` diodes (`D205..D208`, `C64982`) for `AUX_LS1..4` (`J1-10..J1-13`, `PC6, PC7, PA15, PD3`), plus `R212 = 2.2 kΩ` (`C22976`) pull-up to `+12V_MR` on `AUX_LS4` (`J1-13`) for the SV650 0–12 V tachometer signal.
  - Dedicated `MAIN_RLY` (`PE0` -> `U1202.6` + `D209` `B340A-13-F` `C64982` on `J1-14`) and `DASH_TECH` (`PB9` -> `U1201.8` open-drain low-side on `J2-27`) for the SV650 K7 7800-baud single-wire instrument cluster serial link.
- **Onboard `DRV8825PWPR` Stepper + Dual `TLE9201SG` H-Bridges (`stepper_etb.kicad_sch`, `etb-9201.kicad_sch`)**:
  - Replaced Universal 112's through-hole Pololu stepper module with an onboard SMD `DRV8825PWPR` (`U202`, LCSC `C50506`, `STEP = PB4`, `DIR = PB7`, `~EN = PB8`, `0.20 Ω` sense resistors `R213/R214` `C25335`, `VREF = 0.767 V` via `R215 = 33 kΩ / R216 = 10 kΩ` -> `0.77 A` chopper limit) on `J1-19..J1-22` (`STEP_1A/1B/2A/2B`) for the SV650 4-wire `ISC` idle valve.
  - Retained two `TLE9201SG` / `IFX9201SG` 6 A H-bridges (`U201` in `/etb1/`, `U203` inline in `/stepper_etb/`, LCSC `C112633`) on `J1-15..J1-18` (`ETB1_OUT+/-`, `ETB2_OUT+/-`) for the SV650 4-wire `STVA` secondary throttle stepper or dual DBW throttles.
- **Soldered SD NAND Logging Storage (`mcu.kicad_sch`)**:
  - Added soldered `CSNP32GCR01-AOW` (`U25`, LCSC `C2841139`, 32 Gbit / 4 GB SD NAND in `6 × 8 mm` LGA-8; upgraded in `FOMEMC-3` from 4 Gbit / 512 MB `XTSD04GLGEAG` `C558840`) on 4-bit `SDMMC1` (`PC8..PC12, PD2`).
- **Barometric Sensor & Analog Inputs (`mcu.kicad_sch`, `quad_analog.kicad_sch`, `fome-mc.kicad_sch`)**:
  - Defaulted `J2-6` (`PA2` / `EFI_ADC_2`) to an external GM `12614970` / Delphi `PS10150` 1-bar sensor (`MT_GM_1_BAR`) for single-pour flood potting (`FOMEMC-1`), keeping `U24` (`LPS25HBTR`, `C87898`, `I2C2` `PB10/PB11`) as DNP for unpotted bench boards.
  - Added `R219 = 1.5 kΩ` 1% (`C22843`) pull-up to `5V_SENSOR_1` on `AV6_GEAR` (`J2-8`, `PA5`) for the SV650 6-speed gear position resistor ladder.
- **Potted USB DFU Recovery (`mcu.kicad_sch`, `stepper_etb.kicad_sch`)**:
  - Added dual-threshold circuit on `J1-35` (`USB_VBUS_BOOT0`): applying `+5 V` supplies normal `USB_VBUS` (`BOOT0 = 0`), while applying `+12 V` conducts `D210` (`BZT52C6V8` `C173404`) + `R209` (`12 kΩ` `C25752`) to pull `U26` `BOOT0` high (`3.3 V`) for STM32 ROM USB DFU recovery after potting.

### Firmware Changes (`halbritt/fome-fw`, branch `master`)
- Created board target `firmware/config/boards/fome-mc/` with SV650 K7 defaults (`board_configuration.cpp`, `connectors/*.yaml`, `board.mk`, `knock_config.h`, `compile_fome-mc.sh`), `USE_WIFI = yes` (`ATWINC1500-MR210UB` on `SPI4`), external `MT_GM_1_BAR` baro on `EFI_ADC_2`, and `CAN1` 50 Hz `FOME_CAN_verbose.dbc` broadcast + Bosch MM5.10 IMU receive (`IMU_MM5_10`).
- Fixed trailing spark overdwell (`ctx.isOverdwellProtect`) and engine-stop (`isnan(dwell)`) coil-stuck-HIGH bug in `firmware/controllers/engine_cycle/spark_logic.cpp`, with unit tests `trailingSparkTwoCylinderOddFireSV650` and `trailingSparkOverdwellProtection`.
- Fixed hardcoded `if (true)` in `firmware/controllers/actuators/idle_hardware.cpp` (`if (engineConfiguration->useHbridgesToDriveIdleStepper)`) so `DRV8825` STEP/DIR initializes when `useHbridgesToDriveIdleStepper = false`.
- Implemented single-owner `FatFs` -> `USBMSD1` engine-stopped handoff (`pollUsbHandOffRequested()`, `handOffSdToUsbMassStorage()`, `tryHandOffActiveLogToUsb()`) in `firmware/hw_layer/mmc_card_mount.cpp` and `firmware/console/binary_log/sd_file_log.cpp`, plus automatic oldest-`.mlg` ring-buffer pruning (`sd_log_ring_buffer.h`).

---

## 2026-10-16 — `fome-mc`: STM32H7 Brain Module Checkpoint (branch `atlas-brain-module-checkpoint`, commit `c43ad7b`)

Initial adaptation of [FOME-Tech/Polygonus](https://github.com/FOME-Tech/Polygonus) V1.6.1 (`b3176cb1de7d0f5b9380ecebc1d007e2f365a6de`) to run the `ARCH_STM32H7` (`atlas`) pinout while resolving JLCPCB component shortages.

### Hardware Changes vs. Polygonus V1.6.1
1. **MCU (`U26`)**: Upgraded from `STM32F767ZIT6` (`C90235`) to `STM32H753ZIT6` (`C730207`) / `STM32H743ZIT6` (`C114408`) in LQFP-144.
2. **4-Bit `SDMMC1` & MCU Pin Remap (`Polygonus` -> `atlas` / `fome-mc`)**:
   - On Polygonus (`proteus_f7`), `PC8` and `PC9` drove `IGN4` and `IGN3`, while the SD card used 1-bit `SPI3` (`PC10..PC12`). To free `PC8..PC12` + `PD2` for hardware 4-bit `SDMMC1` (`SD_D0..D3, SD_CLK, SD_CMD`) and align with the FOME `atlas` H7 peripheral map, the `U26` I/O banks were remapped:

| Function | Polygonus V1.6.1 (`proteus_f7`) | `atlas` & `fome-mc` (`STM32H753`) |
| :--- | :--- | :--- |
| `LS1..LS4` (`VNLD5090` `U1001, U1002`) | `PD7, PG9, PG10, PG11` | `PG5, PG6, PG7, PG8` (Pins 90–93) |
| `LS5..LS8` (`VNLD5090` `U1101, U1102`) | `PG12, PG13, PG14, PB4` | `PC6, PC7, PA15, PD3` (Pins 96, 97, 110, 117) |
| `LS9..LS12` (Passthrough / Stepper) | `PB5, PB6, PB7, PB8` | `PB4, PB5, PB6, PB7` (Pins 134–137) |
| `LS13..LS16` (`VNLD5090` `U1201, U1202`) | `PB9, PE0, PE1, PE2` | `PB8, PB9, PE0, PE1` (Pins 139–142) |
| `IGN1..IGN4` (`MIC4427` `U42, U43`) | `PD4, PD3, PC9, PC8` | `PB3, PG15, PG14, PG13` (Pins 133, 132, 129, 128) |
| `IGN5..IGN8` (`MIC4427` `U44, U45`) | `PC7, PG8, PG7, PG6` | `PG12, PG11, PG10, PG9` (Pins 127, 126, 125, 124) |
| `IGN9..IGN12` (Passthrough / UART2) | `PG5, PG4, PG3, PG2` | `PD7, PD6, PD5, PD4` (Pins 123, 122, 119, 118) |
| `HS1..HS4` (`VNQ7140AJ` `U40`) | `PA9, PA8, PD15, PD14` | `PG4, PG3, PG2, PD15` (Pins 89, 88, 87, 86) |
| `AV1..AV8` (`MCP6004` `U17, U19`) | `PC0..PC3, PA0..PA3` | `PA0..PA7` (Pins 34–37, 40–43) |
| `AV9..AV11` (`MCP6004` `U21`) | `PA4..PA6` | `PB0, PB1, PC0` (Pins 46, 47, 26) |
| `AT1..AT4` (`MCP6004` `U15`) | `PC4, PC5, PB0, PB1` | `PC1, PC2, PC3, PC4` (Pins 27–29, 44) |
| `12V_DIVIDED` (`BatteryVoltage`) | `PA7` (Pin 43) | `PC5` (Pin 45, `EFI_ADC_15`) |
| `MR_DIVIDED` (`MainRelayVoltage`) | — | `PF11` (Pin 49, `EFI_ADC_16`) |
| `5V_SENSE_DIVIDED` (`Sensor5vVoltage`) | — | `PF12` (Pin 50, `EFI_ADC_17`) |
| `VBOOST_DIVIDED` (`VboostVoltage`) | — | `PF13` (Pin 53, `EFI_ADC_18`) |
| `DIGITAL1..DIGITAL6` | `PC6, PE11..PE15` | `PG0, PG1, PE10..PE13` (Pins 56, 57, 63–66) |
| `VR_1, VR_2` (`MAX9924UAUB+` `U13, U14`) | `PE7, PE8` | `PE14, PE15` (Pins 67, 68) |
| `LED1..LED4` (`D10..D13`) | `PE3, PE4, PE5, PE6` | `PF0, PF2, PD14, PF1` (Pins 10, 12, 85, 11) |

3. **`VBoost` Pre-Regulator (`psu.kicad_sch`)**: Added `U46` (`LM2733XMFX/NOPB`, `C80169`), `L3` (`10 µH`, `C408412`), `D18` (`C8678`), `C107` (`4.7 µF`, `C19666`), and `R122/R123` (`68 kΩ / 10 kΩ`) setting a `9.59 V` pre-regulator floor during starter cranking sags.
4. **32.768 kHz CMOS Active Oscillator (`mcu.kicad_sch`)**: Added `U28` (`S3225SMD32.768KOSC`, `C7431189`) driving `PC14` (`OSC32_IN`, `-DSTM32_LSE_BYPASS`).
5. **JLCPCB Component Shortage Substitutions**:
   - `U24`: `C87898` (`LPS25HBTR`, 2.5×2.5 mm HLGA-10L) replacing mismatched `C94049` (`LPS22HBTR`).
   - `C1, C6`: SMD `47 µF 50 V` hybrid polymer (`C454346` / `C134739`) replacing OOS THT `C1518237`.
   - `D4, D5`: `C907839` (`PESD1CAN`) replacing OOS `C152727`.
   - `C16, C17`: `C472819` (`3.3 nF 50 V X7R 0805`) replacing OOS `C53175`.
   - `D9, D11, D12, D13`: KENTO `0603` LEDs (`C12624` Green, `C2288` Blue, `C2287` Yellow) replacing OOS Everlight LEDs.
