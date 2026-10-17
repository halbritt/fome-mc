# Changelog

## 2026-10-16 (Rev 2) — Power Remediation & Plane Milestones `FOMEMC-1` .. `FOMEMC-4`

Completed the 6-step power/ERC remediation and all four follow-on architecture & firmware enhancements (`FOMEMC-1`, `FOMEMC-2`, `FOMEMC-3`, `FOMEMC-4`):

### 1. Power Architecture, Keep-Alive & Zero-ERC Remediation (`7c3806c`)
- **Ignition & Main Relay Diode-OR Keep-Alive (`sheets/Keep_Alive.kicad_sch`, `sheets/lowside_quad.kicad_sch`, `sheets/stepper_etb.kicad_sch`)**:
  - Added `D20` and `D21` (`B340A-13-F` 40 V 3 A Schottky, LCSC `C8598`) diode-OR combining `+12V_IGN_SW` (`J1-26`) and `+12V_MR` (`J1-27`) onto `12V_RAW`.
  - Connected `12V_SENSE` (`R96 = 82 kΩ / R97 = 10 kΩ` -> `U26.45` `PC5` `12V_DIVIDED`) upstream of `D20` on `/12V_IGN_SW` so key-off is immediately detected while `/12V_MR` keeps `12V_RAW` alive.
  - Routed `PE0` (`U26.141` `MAIN_RLY`) through `RN9/RN10` into `U1202` (`VNLD5090` channel 2, `U1202.6`) with `D209` (`B340A-13-F`) flyback clamp to `/12V_MR` on `J1-14` (`MAIN_RLY`), enabling deterministic post-key-off `.mlg` `f_sync()` flush and stepper parking before main relay release.
  - Retained `Perm_Live` (`J1-28`) -> `D16` (`B5819W`) -> `U41` (`MIC5205-3.3YM5` 3.3 V backup LDO, LCSC `C5370979`) -> `D17`/`D15` into `U26.6` (`VBAT`).
- **Load-Dump, Reverse-Battery & Regulator Hardening (`sheets/psu.kicad_sch`)**:
  - Removed the orphaned `U46` (`LM2733XMFX` boost on an LDO symbol) + `L3, D18, C107`, orphaned `BD3571` regulators, and `U28` (`S3225SMD32.768KOSC` 32.768 kHz oscillator).
  - Upgraded `D1` (`12V_RAW`) and added `D22` (`12V_MR`) as unidirectional **`SMCJ24A`** (`C224045`, `24 V` standoff / `38.9 V` max clamping sacrificial crowbar TVS diodes) ahead of **`Q1` (`AO4485` P-MOSFET reverse-polarity block, `C51499`)** + `D19` (`BZT52C12` `C43491` 12 V gate Zener) + `R124` (`47 kΩ` `C25819`), eliminating the `~0.45 V` / `0.7 W` series Schottky (`D2` `SS34`) drop.
  - Routed `12V_PROT` through the `L1` (`2.2 µH`) + `C6` (`47 µF` Panasonic `EEHZC1H470P` hybrid polymer, `C454346`) LC filter into **`U3` (`LMR16020PDDAR` 60 V 2 A step-down buck, `C190006`)**, **`U1, U2` (`2× TLS115D0E` tracked 5 V sensor LDOs, `C3747428`)**, and **`U6` (`TLV75733PDBVR` 3.3 V 1 A low-dropout LDO, `C485517`, `0.25 V` typ dropout)**, achieving a **`~4.0–4.2 V` connector cranking brownout floor**.
  - Upgraded 12 V rail MLCCs (`C2, C4, C5, C7, C8, C10, C108, C1201`) to Murata `GCJ` soft-terminated 50 V X7R parts and resolved all 60 schematic ERC errors down to **`0` ERC errors** across all 21 sheets (including isolating `/knock/FILTERED_1` `U26.14` and `/knock/FILTERED_2` `U26.15`, separating `VDDA_WBO1` / `VDDA_WBO2`, and fixing `U4/U5` `MCP2551-I-SN` Pin 5 `Vref`).

### 2. `FOMEMC-1` — External 1-Bar Barometer Default & Single-Pour Flood Potting (`c29fde6`)
- Configured `J2-6` (`AV3_BARO_MAP2` / `PA2` / `EFI_ADC_2`) in `fome-fw/firmware/config/boards/fome-mc/board_configuration.cpp` to default to an external automotive **GM `12614970` / Delphi `PS10150` 1-bar absolute pressure sensor** (`MT_GM_1_BAR`, `10–105 kPa` across `0–5 V`, powered by `J1-29` `5V_SENSOR_1` and `J1-31` `SGND`).
- Marked onboard `U24` (`LPS25HBTR`) as `DNP` for potted builds (`lps25BaroSensorScl/Sda = Gpio::Unassigned` by default) and removed the cylindrical `U24` potting dam keep-out rings (`baro.dam.id` / `baro.dam.od`) from `fome-mc.kicad_pcb`, enabling **uniform single-pour flood potting** in an unvented aluminum enclosure with zero lid penetration or capillary wicking risk.

### 3. `FOMEMC-2` — Onboard `ATWINC1500-MR210UB` U.FL Wi-Fi (`SPI4`) & Remapped WBO1/2 Reset/Boot Pins (`f3b0f47`)
- Integrated **`U29` (`ATWINC1500-MR210UB`, LCSC `C1558703`)** 2.4 GHz 802.11b/g/n Wi-Fi module with integral U.FL external antenna receptacle (`R122 = 10 kΩ` pull-up on `SPI_CFG/WAKE/CHIP_EN`, `C106 = 100 nF` decoupling) on `SPI4` (`PE2 = SCK`, `PE5 = MISO`, `PE6 = MOSI`, `PE4 = CS`, `PE3 = IRQ`, `PC13 = RESETN`) in `sheets/mcu.kicad_sch` and `fome-mc.kicad_pcb` (`40.0, 134.0 mm`).
- Remapped `WBO1_NRST`, `WBO1_BOOT0`, `WBO2_NRST`, and `WBO2_BOOT0` from `PE2..PE5` to **`PD4..PD7` (`U26.118, 119, 122, 123`)**.
- Enabled `USE_WIFI = yes` in `fome-fw/firmware/config/boards/fome-mc/board.mk` and configured `SPI4` Wi-Fi hooks in `board_configuration.cpp` for wireless TunerStudio (`TCP :29000`, `wifi_console.cpp`) and the built-in HTTP SDNAND `.mlg`/`.zip` log web server (`HTTP :80`, `http_file_server.cpp`) via an O-ring-sealed U.FL-to-RP-SMA bulkhead pigtail.

### 4. `FOMEMC-3` — 4 GB Soldered LGA-8 SDNAND & Automatic Ring-Buffer Log Pruning (`8bee1ee`)
- Upgraded `U25` from 4 Gbit / 512 MB (`XTSD04GLGEAG` / `CSNP4GCR01-AMW`) to **32 Gbit / 4 GB (`CSNP32GCR01-AOW`, LCSC `C2841139`, 394 in stock; pin-compatible with `MKDV32GCL-STH` `C5199868`)** in the same `6 × 8 mm` LGA-8 footprint on 4-bit `SDMMC1` (`PC8..PC12, PD2`), expanding onboard `.mlg` logging capacity by `8×` to **`~160.5 hours` at `50 Hz`** (`~80.2 hours` at `100 Hz`, `~32.1 hours` at `250 Hz`).
- Added automatic oldest-`.mlg`/`.teeth` ring-buffer pruning (`ensureSdFreeSpace()`, `deleteOldestLogFile()`, `sd_log_ring_buffer.h`) in `fome-fw/firmware/console/binary_log/sd_file_log.cpp` whenever free space drops below `64 MiB` (`25%` on smaller volumes), `.mlg` file count reaches `480`, or `f_write()` hits disk-full, covered by `SdLogRingBuffer.*` GTest unit tests.

### 5. `FOMEMC-4` — `CAN1` Motorsport Telemetry Pod, RaceChrono Pro & Action Camera Integration (`232daec`)
- Configured `CAN1` (`J2-28` `CAN1_H` / `J2-29` `CAN1_L`, 500 kbps via `U4` `MCP2551-I-SN`) in `board_configuration.cpp` to broadcast `FOME_CAN_verbose.dbc` (`0x200..0x207`: RPM, TPS1, STPS, Gear, MAP, CLT, IAT, VBatt, InjPW, Knock, WBO1/2 Lambda) at **50 Hz (`20 ms`)** and decode incoming Bosch Motorsport MM5.10 6-axis IMU frames (`0x174`, `0x178`, `0x17C`: `YawRate`, `AccelLat`, `RollRate`, `AccelLon`, `PitchRate`, `AccelVert`) by default (`imuType = IMU_MM5_10`), with `can_imu_test.cpp` unit test coverage and full integration documentation in [`docs/TELEMETRY_AND_RACECHRONO.md`](docs/TELEMETRY_AND_RACECHRONO.md).

---

## 2026-10-16 (Rev 1) — `fome-mc`: Initial Single-PCB Motorcycle ECU Integration (`f5abd10`)

Integrated the `fome-mc` STM32H7 processor core, `Polygonus-Universal-112` carrier circuitry, and two `wideband_controller` Rev C channels onto a single `162.0 mm × 115.0 mm` 4-layer PCB (`fome-mc.kicad_sch` / `fome-mc.kicad_pcb`) targeting the 2007 Suzuki SV650 (K7 dual-plug V-twin). *(Note: Where superseded by Rev 2 above—such as `D20/D21` + `PE0` `MAIN_RLY` keep-alive, `LMR16020PDDAR` + `AO4485` + `TLV75733PDBVR`, `FOMEMC-1` external baro default, `FOMEMC-2` `ATWINC1500-MR210UB` Wi-Fi + `PD4..PD7` WBO reset/boot, and `FOMEMC-3` 4 GB `CSNP32GCR01-AOW` SDNAND—the Rev 2 specification governs.)*

### Hardware Changes (`halbritt/fome-mc`)
- **Form Factor & Sealed Harness Connectors**:
  - Replaced the 107-pin Polygonus board-to-board headers (`J4..J7`) and the unobtainable Molex CMC 112-pin header with two 35-pin TE Connectivity AMPSEAL right-angle PCB headers: `J1` (`776163-1`, Key 1 Black, LCSC `C722761` / `C412117`) and `J2` (`776163-2`, Key 2 Grey, LCSC `C722762`).
  - Resized the 4-layer PCB outline to `162.0 mm × 115.0 mm` with 4× M4 corner mounting holes (`154.0 mm × 107.0 mm` centers) and 475 schematic components (`106` BOM lines).
- **Dual Onboard Bosch LSU 4.9 Wideband Controllers (`wbo1.kicad_sch`, `wbo2.kicad_sch`)**:
  - Integrated two complete `wideband_controller` Rev C circuits (`U301..U309` for `WBO1`, `U401..U409` for `WBO2`: `STM32F042K6T6`, `MCP6004`, `AD8628`, `REF3033`, `XC6206P332MR`, `VND14NV04` heater FET) and two `TJA1051T/3` CAN transceivers (`U307`, `U407`) onto internal 500 kbps `CAN2` (`PB12/PB13` via `U5` `MCP2551-I-SN`).
  - Hardware-strapped `WBO1` (`PB1 = GND`, `PA8 = Float` -> `CanIndexOffset = 0`, CAN IDs `0x190/0x191`) and `WBO2` (`PB1 = Float`, `PA8 = +3.3V` -> `CanIndexOffset = 1`, CAN IDs `0x192/0x193`) so broadcast `WB_MSG_SET_INDEX` frames cannot clobber both controllers to the same CAN ID.
  - Removed duplicate 120 Ω termination resistors from the internal `CAN2` transceivers (fixing the Universal 112 triple-termination 40 Ω bus overload).
  - Routed `STM32H753` pins `PD4..PD7` (remapped from `PE2..PE5` in `FOMEMC-2`) to `WBO1_NRST`, `WBO1_BOOT0`, `WBO2_NRST`, and `WBO2_BOOT0` for sequential single-node OpenBLT firmware updates and reset recovery after potting.
- **Ignition Drivers (`ign_igbt.kicad_sch`, `ign4.kicad_sch`)**:
  - Added 4× `FGD3040G2-F085` (400 V, 30 A, TO-252, LCSC `C606124` / `C471989`) ignition IGBTs (`Q201..Q204`) on `J1-6..J1-9` (`IGBT1..4`, driven by `PB3, PG15, PG14, PG13` through `MIC4427` `U42/U43` with 10 kΩ MCU reset pull-downs and 15 Ω gate resistors).
  - Routed 4× 5 V push-pull logic coil outputs (`IGN1_LOG..4_LOG` on `J2-23..J2-26`, driven by `PG12..PG9` through `MIC4427` `U44/U45` and 100 Ω series resistors).
- **Injector, Auxiliary Low-Side, Main Relay, Tachometer & Dash Outputs (`lowside_quad.kicad_sch`, `stepper_etb.kicad_sch`)**:
  - Dedicated 4× `VNLD5090TR-E` channels (`U1001, U1002`) with `B340A-13-F` flyback Schottky diodes to `+12V_MR` (`D201..D204`) for `INJ1..4` (`J1-1..J1-4`, `PG5..PG8`).
  - Dedicated 4× `VNLD5090TR-E` channels (`U1101, U1102`) with `B340A-13-F` diodes (`D205..D208`) for `AUX_LS1..4` (`J1-10..J1-13`, `PC6, PC7, PA15, PD3`), plus a 2.2 kΩ pull-up to `+12V_MR` on `AUX_LS4` (`J1-13`) for the SV650 0–12 V tachometer signal.
  - Dedicated `MAIN_RLY` (`PE0` -> `U1202.6` + `D209` `B340A-13-F` on `J1-14`) and `DASH_TECH` (`PB9` -> `U1201.8` + `R212` `2.2 kΩ` pull-up to `+12V_MR` on `J2-27`) for the SV650 K7 7800-baud single-wire instrument cluster serial link.
- **Onboard `DRV8825PWPR` Stepper + Dual `TLE9201SG` H-Bridges (`stepper_etb.kicad_sch`, `etb-9201.kicad_sch`)**:
  - Replaced Universal 112's through-hole Pololu stepper module with an onboard SMD `DRV8825PWPR` (`U202`, LCSC `C50506` / `C81582`, `STEP = PB4`, `DIR = PB7`, `~EN = PB8`, 0.20 Ω sense resistors, `0.75 A` chopper limit) on `J1-19..J1-22` (`STEP_1A/1B/2A/2B`) for the SV650 4-wire `ISC` idle valve.
  - Retained two `TLE9201SG` / `IFX9201SG` 6 A H-bridges (`U201`, `U203`, LCSC `C112633`) on `J1-15..J1-18` (`ETB1_OUT+/-`, `ETB2_OUT+/-`) for the SV650 4-wire `STVA` secondary throttle stepper or dual DBW throttles.
- **Soldered SD NAND Logging Storage (`mcu.kicad_sch`)**:
  - Added soldered `CSNP32GCR01-AOW` (`U25`, LCSC `C2841139`, 32 Gbit / 4 GB SD NAND in `6 × 8 mm` LGA-8; upgraded in `FOMEMC-3` from 4 Gbit / 512 MB `XTSD04GLGEAG` `C558840`) on 4-bit `SDMMC1` (`PC8..PC12, PD2`).
- **Barometric Sensor & Analog Inputs (`mcu.kicad_sch`, `quad_analog.kicad_sch`)**:
  - Defaulted `J2-6` (`PA2` / `EFI_ADC_2`) to an external GM `12614970` / Delphi `PS10150` 1-bar sensor (`MT_GM_1_BAR`) for single-pour flood potting (`FOMEMC-1`), keeping `U24` (`LPS25HBTR`, `C87898`, `I2C2` `PB10/PB11`) as DNP for unpotted bench boards.
  - Added a 1.5 kΩ 1% pull-up to `5V_SENSOR_1` on `AV6_GEAR` (`J2-8`, `PA5`) for the SV650 6-speed gear position resistor ladder.
- **Potted USB DFU Recovery (`mcu.kicad_sch`, `stepper_etb.kicad_sch`)**:
  - Added dual-threshold circuit on `J1-35` (`USB_VBUS_DFU` / `/RC2`): applying `+5 V` supplies normal `USB_VBUS` (`BOOT0 = 0`), while applying `+12 V` biases `R209` (`10 kΩ`) to pull `U26` `BOOT0` high (`3.3 V`) for STM32 ROM USB DFU recovery after potting.

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
2. **4-Bit `SDMMC1` & MCU Pin Remap (`Polygonus` -> `fome-mc` / `fome-mc`)**:
   - On Polygonus (`proteus_f7`), `PC8` and `PC9` drove `IGN4` and `IGN3`, while the SD card used 1-bit `SPI3` (`PC10..PC12`). To free `PC8..PC12` + `PD2` for hardware 4-bit `SDMMC1` (`SD_D0..D3, SD_CLK, SD_CMD`) and align with the FOME `atlas` H7 peripheral map, the `U26` I/O banks were remapped:

| Function | Polygonus V1.6.1 (`proteus_f7`) | `fome-mc` & `fome-mc` (`STM32H753`) |
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
