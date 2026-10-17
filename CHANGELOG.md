# Changelog

## 2026-10-16 — `fome-mc`: Integrated Single-PCB Motorcycle ECU (`master` / `fome-mc`)

Integrated the `Atlas-clone` STM32H7 processor core, `Polygonus-Universal-112` carrier circuitry, and two `wideband_controller` Rev C channels onto a single `162.0 mm × 115.0 mm` 4-layer PCB (`fome-mc.kicad_sch` / `fome-mc.kicad_pcb`) targeting the 2007 Suzuki SV650 (K7 dual-plug V-twin).

### Hardware Changes (`halbritt/fome-mc`)
- **Form Factor & Sealed Harness Connectors**:
  - Replaced the 107-pin Polygonus board-to-board headers (`J4..J7`) and the unobtainable Molex CMC 112-pin header with two 35-pin TE Connectivity AMPSEAL right-angle PCB headers: `J1` (`776163-1`, Key 1 Black, LCSC `C412117`) and `J2` (`776163-2`, Key 2 Grey).
  - Resized the 4-layer PCB outline to `162.0 mm × 115.0 mm` with 4× M4 corner mounting holes (`154.0 mm × 107.0 mm` centers) and 474 placed footprints.
- **Dual Onboard Bosch LSU 4.9 Wideband Controllers (`wbo1.kicad_sch`, `wbo2.kicad_sch`)**:
  - Integrated two complete `wideband_controller` Rev C circuits (`U301..U305` for `WBO1`, `U401..U405` for `WBO2`: `STM32F042K6T6`, `MCP6004`, `AD8628`, `REF3033`, `XC6206P332MR`, `VND14NV04` heater FET) and two `TJA1051T/3` CAN transceivers (`U5`, `U200`) onto internal 500 kbps `CAN2` (`PB12/PB13`).
  - Hardware-strapped `WBO1` (`PB1 = GND`, `PA8 = Float` -> `CanIndexOffset = 0`, CAN IDs `0x190/0x191`) and `WBO2` (`PB1 = Float`, `PA8 = +3.3V` -> `CanIndexOffset = 1`, CAN IDs `0x192/0x193`) so broadcast `WB_MSG_SET_INDEX` frames cannot clobber both controllers to the same CAN ID.
  - Removed duplicate 120 Ω termination resistors from the internal `CAN2` transceivers (fixing the Universal 112 triple-termination 40 Ω bus overload).
  - Routed `STM32H753` pins `PE2..PE5` to `WBO1_NRST`, `WBO1_BOOT0`, `WBO2_NRST`, and `WBO2_BOOT0` for sequential single-node OpenBLT firmware updates and reset recovery after potting.
- **Ignition Drivers (`ign_igbt.kicad_sch`, `ign4.kicad_sch`)**:
  - Added 4× `FGD3040G2-F085C` (400 V, 30 A, TO-252, LCSC `C471989`) ignition IGBTs (`Q201..Q204`) on `J1-6..J1-9` (`IGBT1..4`, driven by `PB3, PG15, PG14, PG13` through `MIC4427` `U42/U43` with 10 kΩ MCU reset pull-downs and 20 Ω gate resistors).
  - Routed 4× 5 V push-pull logic coil outputs (`IGN1_LOG..4_LOG` on `J2-23..J2-26`, driven by `PG12..PG9` through `MIC4427` `U44/U45` and 100 Ω series resistors).
- **Injector, Auxiliary Low-Side, Tachometer & Dash Outputs (`lowside_quad.kicad_sch`)**:
  - Dedicated 4× `VNLD5090TR-E` channels with `SK310A` flyback Schottky diodes to `+12V_MR` (`D201..D204`) for `INJ1..4` (`J1-1..J1-4`, `PG5..PG8`).
  - Dedicated 4× `VNLD5090TR-E` channels with `SK310A` diodes (`D205..D208`) for `AUX_LS1..4` (`J1-10..J1-13`, `PC6, PC7, PA15, PD3`), plus a 2.2 kΩ pull-up to `+12V_MR` (`R211`) on `AUX_LS4` (`J1-13`) for the SV650 0–12 V tachometer signal.
  - Added a 2.2 kΩ pull-up to `+12V_MR` (`R212`) on `DASH_TECH` (`J2-27`, `PB9`) for the SV650 K7 7800-baud single-wire instrument cluster serial link.
- **Onboard `DRV8825PWPR` Stepper + Dual `TLE9201SG` H-Bridges (`stepper_etb.kicad_sch`, `etb-9201.kicad_sch`)**:
  - Replaced Universal 112's through-hole Pololu stepper module with an onboard SMD `DRV8825PWPR` (`U202`, LCSC `C81582`, `STEP = PB4`, `DIR = PB7`, `~EN = PB8`, 0.20 Ω sense resistors, `0.75 A` chopper limit) on `J1-19..J1-22` (`STEP_1A/1B/2A/2B`) for the SV650 4-wire `ISC` idle valve.
  - Retained two `TLE9201SG` / `IFX9201SG` 6 A H-bridges (`U201`, `U203`, LCSC `C112633`) on `J1-15..J1-18` (`ETB1_OUT+/-`, `ETB2_OUT+/-`) for the SV650 4-wire `STVA` secondary throttle stepper or dual DBW throttles.
- **Soldered SD NAND Logging Storage (`mcu.kicad_sch`)**:
  - Added soldered `XTSD04GLGEAG` (`U25`, LCSC `C558840`, 4 Gbit / 512 MB SLC SD NAND in `6 × 8 mm` LGA-8; footprint-compatible with `MKDV4GIL-AST` `C726727` and `MKDV1GIL-AS` `C726726`) on 4-bit `SDMMC1` (`PC8..PC12, PD2`), retaining `J10` microSD as DNP for bench boards.
- **Barometric Sensor Chimney Pocket & Analog Inputs (`mcu.kicad_sch`, `quad_analog.kicad_sch`)**:
  - Placed `LPS25HBTR` (`U24`, LCSC `C87898`, `I2C2` on `PB10/PB11`) at `(121.62, 100.61 mm)` inside an `ID 8.0 mm × OD 11.0 mm` potting keep-out ring for an ePTFE membrane enclosure vent (`Amphenol LTW VE80410` / `Gore PMF100321`).
  - Added a 1.5 kΩ 1% pull-up (`R210`) to `5V_SENSOR_1` on `AV6_GEAR` (`J2-8`, `PA5`) for the SV650 6-speed gear position resistor ladder.
- **Potted USB DFU Recovery (`mcu.kicad_sch`)**:
  - Added dual-threshold circuit on `J1-35` (`USB_VBUS_DFU`): applying `+5 V` supplies normal `USB_VBUS` (`BOOT0 = 0`), while applying `+12 V` conducts through `6.8 V` Zener `D19` + `R209` (`4.7 kΩ`) to pull `U26` `BOOT0` high (`3.1 V`) for STM32 ROM USB DFU recovery after potting.

### Firmware Changes (`halbritt/fome-fw`, branch `fome-mc`, commit `773074f3d2`)
- Created board target `firmware/config/boards/fome-mc/` with SV650 K7 defaults (`board_configuration.cpp`, `connectors/mapping.yaml`, `efifeatures.h`, `halconf.h`, `mcuconf.h`, `knock_config.h`, `compile_fome-mc.sh`).
- Fixed trailing spark overdwell (`ctx.isOverdwellProtect`) and engine-stop (`isnan(dwell)`) coil-stuck-HIGH bug in `firmware/controllers/engine_cycle/spark_logic.cpp`, with unit tests `trailingSparkTwoCylinderOddFireSV650` and `trailingSparkOverdwellProtection`.
- Fixed hardcoded `if (true)` in `firmware/controllers/actuators/idle_hardware.cpp` (`if (engineConfiguration->useHbridgesToDriveIdleStepper)`) so `DRV8825` STEP/DIR initializes when `useHbridgesToDriveIdleStepper = false`.
- Implemented single-owner `FatFs` -> `USBMSD1` engine-stopped handoff (`pollUsbHandOffRequested()`, `handOffSdToUsbMassStorage()`, `tryHandOffActiveLogToUsb()`) in `firmware/hw_layer/mmc_card_mount.cpp` and `firmware/console/binary_log/sd_file_log.cpp`.

---

## 2026-10-16 — `Atlas-clone`: STM32H7 Brain Module Checkpoint (branch `atlas-brain-module-checkpoint`, commit `c43ad7b`)

Initial adaptation of [FOME-Tech/Polygonus](https://github.com/FOME-Tech/Polygonus) V1.6.1 (`b3176cb1de7d0f5b9380ecebc1d007e2f365a6de`) to run the `ARCH_STM32H7` (`atlas`) pinout while resolving JLCPCB component shortages.

### Hardware Changes vs. Polygonus V1.6.1
1. **MCU (`U26`)**: Upgraded from `STM32F767ZIT6` (`C90235`) to `STM32H753ZIT6` (`C730207`) / `STM32H743ZIT6` (`C114408`) in LQFP-144.
2. **4-Bit `SDMMC1` & MCU Pin Remap (`Polygonus` -> `Atlas-clone` / `fome-mc`)**:
   - On Polygonus (`proteus_f7`), `PC8` and `PC9` drove `IGN4` and `IGN3`, while the SD card used 1-bit `SPI3` (`PC10..PC12`). To free `PC8..PC12` + `PD2` for hardware 4-bit `SDMMC1` (`SD_D0..D3, SD_CLK, SD_CMD`) and align with the FOME `atlas` H7 peripheral map, the `U26` I/O banks were remapped:

| Function | Polygonus V1.6.1 (`proteus_f7`) | `Atlas-clone` & `fome-mc` (`STM32H753`) |
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
| `VR_1, VR_2` (`MAX9924` `U3, U4`) | `PE7, PE8` | `PE14, PE15` (Pins 67, 68) |
| `LED1..LED4` (`D10..D13`) | `PE3, PE4, PE5, PE6` | `PF0, PF2, PD14, PF1` (Pins 10, 12, 85, 11) |

3. **`VBoost` Pre-Regulator (`psu.kicad_sch`)**: Added `U46` (`LM2733XMFX/NOPB`, `C80169`), `L3` (`10 µH`, `C408412`), `D18` (`C8678`), `C107` (`4.7 µF`, `C19666`), and `R122/R123` (`68 kΩ / 10 kΩ`) setting a `9.59 V` pre-regulator floor during starter cranking sags.
4. **32.768 kHz CMOS Active Oscillator (`mcu.kicad_sch`)**: Added `U28` (`S3225SMD32.768KOSC`, `C7431189`) driving `PC14` (`OSC32_IN`, `-DSTM32_LSE_BYPASS`).
5. **JLCPCB Component Shortage Substitutions**:
   - `U24`: `C87898` (`LPS25HBTR`, 2.5×2.5 mm HLGA-10L) replacing mismatched `C94049` (`LPS22HBTR`).
   - `C1, C6`: SMD `47 µF 50 V` hybrid polymer (`C454346` / `C134739`) replacing OOS THT `C1518237`.
   - `D4, D5`: `C907839` (`PESD1CAN`) replacing OOS `C152727`.
   - `C16, C17`: `C472819` (`3.3 nF 50 V X7R 0805`) replacing OOS `C53175`.
   - `D9, D11, D12, D13`: KENTO `0603` LEDs (`C12624` Green, `C2288` Blue, `C2287` Yellow) replacing OOS Everlight LEDs.
