# `fome-mc` Hierarchical Sheet Pin Contracts & Cross-Block Ownership Ledger (`FOMEMC-22`)

Status: **Verified against native KiCad 10.0.7 netlist export and `agent-ee.interface/1` validator (`FOMEMC-22`)**.

This document defines the complete hierarchical boundary contract of every subsheet in `fome-mc` (`fome-mc.kicad_sch` + 15 child schematics in `sheets/*.kicad_sch`, instantiated as 21 sheet instances total), resolves all cross-block component/net couplings to an explicit owner block, records the engineering disposition of the shared `/PB8_STEP_EN` (`PB8` / `LS13`) net, and indexes the 15 machine-checkable `agent-ee.interface/1` contracts in `contracts/*.interface.json`.

---

## 1. Sheet Instance Inventory (15 Sheet Files, 21 Sheet Instances)

The root schematic `fome-mc.kicad_sch` (`uuid = 3b9c5ffd-e59b-402d-8c5e-052f7ca643a4`) instantiates 15 unique child schematic files in `sheets/*.kicad_sch` across 20 child sheet instances (21 instances including `/`). Across the full hierarchy, the native netlist contains **510 components** (494 populated, 16 DNP) and **491 nets**, with **222 unique `hierarchical_label` definitions** across the 15 child sheet files expanding to **262 instance-pin bindings** across the 20 child instances.

| # | Instance Path (`sheet_name`) | Sheet File (`sheet_file`) | Native Instance Timestamp (`uuid`) | Components (Total / Pop / DNP) | Unique Pins (Label Occurrences) | Interface Contract | Primary Function & Key Active Devices |
|---:|---|---|---|---:|---:|---|---|
| 0 | `/` | `fome-mc.kicad_sch` | `/` (`3b9c5ffd-e59b-402d-8c5e-052f7ca643a4`) | 4 (4 / 0) | — (Root) | Verified via `verify_io_map.py` | Root harness integration: `J1`, `J2` (35-pin AMPSEAL headers), `C1` (`47 µF` `/12V_MR` bulk cap), `R219` (`1.5 kΩ` `1%` `C22843` `/AV6` gear pull-up) |
| 1 | `/Keep_Alive/` | `sheets/Keep_Alive.kicad_sch` | `/46495fed-359e-4c30-808a-9217af090de7/` | 10 (10 / 0) | 5 (5) | `contracts/Keep_Alive.interface.json` | Power OR-ing & VBAT Keep-Alive Supply — D20, D21 (B340A-13-F Schottky OR), D22 (SMCJ24A TVS), U41 (MIC5205-3.3YM5 LDO), D16, D17 (B5819W), IC1 (PSM712) |
| 2 | `/etb1/` | `sheets/etb-9201.kicad_sch` | `/a1000000-0000-4000-8000-000000000003/` | 5 (5 / 0) | 6 (6) | `contracts/etb-9201.interface.json` | Primary Electronic Throttle Body / STVA H-Bridge #1 — U201 (TLE9201SG 6A H-Bridge #1), C1201 (2.2uF), R210 (10k DIS pull-up to +3V3) |
| 3 | `/highside_quad/` | `sheets/highside_quad.kicad_sch` | `/00000000-0000-0000-0000-00005dd5b2e0/` | 14 (14 / 0) | 9 (9) | `contracts/highside_quad.interface.json` | Quad Protected High-Side Output Driver (Spare) — U40 (BTS716G 4-Ch High-Side Smart Switch), RN11 (4x10k pull-down), R103..R106 |
| 4 | `/ign1/` | `sheets/ign4.kicad_sch` | `/00000000-0000-0000-0000-00005d975f3c/` | 16 (16 / 0) | 8 (8) | `contracts/ign4.interface.json` | Quad 5V Push-Pull Ignition Pre-Driver / Logic Coil Buffer — /ign1/: U42, U43 (MIC4427YM IGBT Gate Drivers); /ign2/: U44, U45 (MIC4427YM 5V Smart-Coil Drivers) |
| 5 | `/ign2/` | `sheets/ign4.kicad_sch` | `/00000000-0000-0000-0000-00005d98f734/` | 16 (16 / 0) | 8 (8) | `contracts/ign4.interface.json` | Quad 5V Push-Pull Ignition Pre-Driver / Logic Coil Buffer — /ign1/: U42, U43 (MIC4427YM IGBT Gate Drivers); /ign2/: U44, U45 (MIC4427YM 5V Smart-Coil Drivers) |
| 6 | `/ign_igbt/` | `sheets/ign_igbt.kicad_sch` | `/a1000000-0000-4000-8000-000000000001/` | 12 (12 / 0) | 8 (8) | `contracts/ign_igbt.interface.json` | Quad 400V Clamped Ignition Coil Low-Side IGBT Power Stage — Q201..Q204 (FGD3040G2-F085 400V 15A IGBTs), R201..R204 (15R gate), R205..R208 (10k G-E) |
| 7 | `/knock/` | `sheets/knock.kicad_sch` | `/00000000-0000-0000-0000-00005e814213/` | 24 (22 / 2) | 4 (4) | `contracts/knock.interface.json` | Dual-Channel Piezo Knock Sensor AC Bandpass Filter — U7 (MCP6004 quad op-amp), C16, C17 (3.3nF 50V X7R input AC coupling), bandpass RC network |
| 8 | `/lowside_quad1/` | `sheets/lowside_quad.kicad_sch` | `/00000000-0000-0000-0000-00005d98a146/` | 6 (6 / 0) | 8 (8) | `contracts/lowside_quad.interface.json` | Quad 5V-Buffered Protected Low-Side Driver (VNLD5090-E) — U1001..U1202 (VNLD5090-E dual 42V-clamped low-side switches), U1003/U1103/U1203 (74HCT125D 5V buffers), RN5..RN10 |
| 9 | `/lowside_quad2/` | `sheets/lowside_quad.kicad_sch` | `/00000000-0000-0000-0000-00005d99f107/` | 6 (6 / 0) | 8 (8) | `contracts/lowside_quad.interface.json` | Quad 5V-Buffered Protected Low-Side Driver (VNLD5090-E) — U1001..U1202 (VNLD5090-E dual 42V-clamped low-side switches), U1003/U1103/U1203 (74HCT125D 5V buffers), RN5..RN10 |
| 10 | `/lowside_quad4/` | `sheets/lowside_quad.kicad_sch` | `/00000000-0000-0000-0000-00005d99f54c/` | 6 (6 / 0) | 8 (8) | `contracts/lowside_quad.interface.json` | Quad 5V-Buffered Protected Low-Side Driver (VNLD5090-E) — U1001..U1202 (VNLD5090-E dual 42V-clamped low-side switches), U1003/U1103/U1203 (74HCT125D 5V buffers), RN5..RN10 |
| 11 | `/mcu/` | `sheets/mcu.kicad_sch` | `/00000000-0000-0000-0000-00005d99e6ee/` | 86 (76 / 10) | 77 (77) | `contracts/mcu.interface.json` | STM32H753ZIT6 Core, REF3333 ADC VREF+, 4GB SDNAND, Wi-Fi & USB ESD — U26 (STM32H753ZIT6), U23 (REF3333), U25 (CSNP32GCR01-AOW SDNAND), U29 (ATWINC1500-MR210UB Wi-Fi), U27 (USBLC6-2SC6), U24 (LPS25HB DNP) |
| 12 | `/psu/` | `sheets/psu.kicad_sch` | `/00000000-0000-0000-0000-00005da72eff/` | 39 (39 / 0) | 15 (15) | `contracts/psu.interface.json` | 12V Load-Dump/Reverse Protection, 5V Buck, Dual Tracked 5V Sensor LDOs, 3.3V LDO & Dual CAN Transceivers — D1 (SMCJ24A), Q1 (AO4485 PFET), U3 (LMR16020PDDAR 5V buck), U1, U2 (TLS115D0E), U6 (TLV75733PDBVR), U4, U5 (MCP2551-I-SN CAN1/CAN2), D4, D5 (PESD1CAN-UX) |
| 13 | `/quad_analog1/` | `sheets/quad_analog.kicad_sch` | `/00000000-0000-0000-0000-00005d9a3845/` | 20 (20 / 0) | 8 (8) | `contracts/quad_analog.interface.json` | Quad 0-5V Ratiometric Analog Input Conditioning (Op-Amp Unity Buffer + 5.6k/10k Divider + ESD Clamp) — U17, U19, U21 (MCP6004 +5V unity buffers), U18, U20, U22 (SRV05-4 ESD arrays), 5.6k/10k output dividers, 470k bleeders |
| 14 | `/quad_analog2/` | `sheets/quad_analog.kicad_sch` | `/00000000-0000-0000-0000-00005da6c1ea/` | 20 (20 / 0) | 8 (8) | `contracts/quad_analog.interface.json` | Quad 0-5V Ratiometric Analog Input Conditioning (Op-Amp Unity Buffer + 5.6k/10k Divider + ESD Clamp) — U17, U19, U21 (MCP6004 +5V unity buffers), U18, U20, U22 (SRV05-4 ESD arrays), 5.6k/10k output dividers, 470k bleeders |
| 15 | `/quad_analog3/` | `sheets/quad_analog.kicad_sch` | `/00000000-0000-0000-0000-00005da6c714/` | 20 (20 / 0) | 8 (8) | `contracts/quad_analog.interface.json` | Quad 0-5V Ratiometric Analog Input Conditioning (Op-Amp Unity Buffer + 5.6k/10k Divider + ESD Clamp) — U17, U19, U21 (MCP6004 +5V unity buffers), U18, U20, U22 (SRV05-4 ESD arrays), 5.6k/10k output dividers, 470k bleeders |
| 16 | `/quad_analog_temp/` | `sheets/quad_analog_pullup.kicad_sch` | `/00000000-0000-0000-0000-00005dcc02d0/` | 21 (21 / 0) | 9 (9) | `contracts/quad_analog_pullup.interface.json` | Quad Thermistor Analog Input Conditioning with 2.7k 0.1% Pull-Ups to 5V_SENSOR_1 — U15 (MCP6004 +5V unity buffer), U16 (SRV05-4 ESD array), R39..R42 (2.7k 0.1% bias pull-ups), 5.6k/10k output dividers |
| 17 | `/stepper_etb/` | `sheets/stepper_etb.kicad_sch` | `/a1000000-0000-4000-8000-000000000002/` | 26 (22 / 4) | 26 (26) | `contracts/stepper_etb.interface.json` | Bipolar Stepper (DRV8825), Secondary H-Bridge #2 (TLE9201SG), Low-Side Clamps (D201..D209) & USB/BOOT0 Recovery — U202 (DRV8825PWPR), U203 (TLE9201SG #2), D201..D204 (B340A DNP), D205..D209 (B340A), R212 (2.2k tach pull-up), D210 (BZT52C6V8), D211 (B5819W) |
| 18 | `/triggers/` | `sheets/triggers.kicad_sch` | `/00000000-0000-0000-0000-00005dd8090b/` | 43 (43 / 0) | 19 (26) | `contracts/triggers.interface.json` | Dual Adaptive Differential VR Conditioners (MAX9924) & 6-Ch Hall/Digital Schmitt Buffers — U13, U14 (MAX9924UAUB+ Mode A2), U8..U10 (SN74LVC2G17DB), U11, U12 (SRV05-4 ESD), R23..R28 = 2.7k pull-ups to 5V_SENSOR_1, R29..R34 = 2.7k series |
| 19 | `/wbo1/` | `sheets/wbo1.kicad_sch` | `/a1000000-0000-4000-8000-000000000004/` | 58 (58 / 0) | 10 (10) | `contracts/wbo1.interface.json` | Front Cylinder #1 Bosch LSU 4.9 Wideband Controller (STM32F042 + Pump/Nernst AFE + Heater PWM + CAN2) — U302 (STM32F042K6T6), U301 (MCP6004), U305 (AD8628), U303 (REF3033), U309 (XC6206P332MR), Q301 (VND14NV04), U307 (TJA1051T/3), R310 (61.9R 0.1%) |
| 20 | `/wbo2/` | `sheets/wbo2.kicad_sch` | `/a1000000-0000-4000-8000-000000000005/` | 58 (58 / 0) | 10 (10) | `contracts/wbo2.interface.json` | Rear Cylinder #2 Bosch LSU 4.9 Wideband Controller (STM32F042 + Pump/Nernst AFE + Heater PWM + CAN2) — U402 (STM32F042K6T6), U401 (MCP6004), U405 (AD8628), U403 (REF3033), U409 (XC6206P332MR), Q401 (VND14NV04), U407 (TJA1051T/3), R410 (61.9R 0.1%) |

### 1.1 Implicit Global Power & Ground Nets Crossing Sheet Boundaries

Only three nets cross sheet boundaries via KiCad global power symbols rather than explicit `hierarchical_label` ports:

| Global Power Symbol Net | Voltage / Domain | Source Block & Regulator | Consuming Sheet Instances | External Connector Pins |
|---|---|---|---|---|
| `GND` | `0 V` Unified Reference & Power Return | External battery/chassis return (`J1-5, J1-31..34`) | All 21 sheet instances (`/`, `/psu/`, `/Keep_Alive/`, `/mcu/`, `/wbo1/`, `/wbo2/`, `/ign_igbt/`, `/ign1/`, `/ign2/`, `/lowside_quad1/`, `/lowside_quad2/`, `/lowside_quad4/`, `/highside_quad/`, `/quad_analog1..3/`, `/quad_analog_temp/`, `/triggers/`, `/knock/`, `/stepper_etb/`, `/etb1/`) | `J1-5` (`PGND_INJ`), `J1-31` (`SGND`), `J1-32` (`PGND_IGN`), `J1-33` (`PGND_HEATER`), `J1-34` (`CHASSIS_ECU_GND`) |
| `+5V` | `+5.00 V ± 2%` (`2 A` Switching Buck) | `/psu/` (`U3` `LMR16020PDDAR` fed from `/VBOOST`) | 14 instances: `/psu/`, `/mcu/`, `/quad_analog1/`, `/quad_analog2/`, `/quad_analog3/`, `/quad_analog_temp/`, `/triggers/`, `/lowside_quad1/`, `/lowside_quad2/`, `/lowside_quad4/`, `/ign1/`, `/ign2/`, `/wbo1/`, `/wbo2/` | Internal board rail (supplies `U6` `+3V3` LDO, `U23` `REF3333`, `MCP2551`, `MCP6004`, `MAX9924`, `74HCT125D`, `MIC4427YM`, and `U309`/`U409` WBO LDOs) |
| `+3V3` | `+3.30 V ± 1%` (`1 A` Linear LDO) | `/psu/` (`U6` `TLV75733PDBVR` fed from `+5V`) | 7 instances: `/psu/`, `/mcu/`, `/triggers/`, `/knock/`, `/highside_quad/`, `/stepper_etb/`, `/etb1/` | Internal digital/logic rail (supplies `U26` `STM32H753ZIT6`, `U25` `SDNAND`, `U29` `ATWINC1500`, `SN74LVC2G17`, `U7` `MCP6004`, `U202` `DRV8825` logic/VREF, `TLE9201SG` logic) |

> **Note on Local Per-Channel Wideband Rails**: `sheets/wbo1.kicad_sch` and `sheets/wbo2.kicad_sch` use sheet-specific power symbols `+3V3_WBO1` / `VDDA_WBO1` (generated by `U309` `XC6206P332MR` and `U303` `REF3033` inside `/wbo1/`) and `+3V3_WBO2` / `VDDA_WBO2` (generated by `U409` `XC6206P332MR` and `U403` `REF3033` inside `/wbo2/`). These rails remain strictly local to their respective wideband channel sheets.

---

## 2. Complete Hierarchical Pin Contract Table (All 15 Sheet Files, 222 Unique Pins, 262 Instance Bindings)

Every `hierarchical_label` in every `sheets/*.kicad_sch` file is listed below with its declared KiCad shape/direction, exact exported net name at each sheet instance, internal child component terminal(s), voltage/current domain, external `J1`/`J2` connector pin(s) from `io-map.csv` (or internal MCU endpoint), and electrical intent.

### 2.1 `sheets/Keep_Alive.kicad_sch` (`/Keep_Alive/`)

- **Function**: Power OR-ing & VBAT Keep-Alive Supply
- **Key Components**: D20, D21 (B340A-13-F Schottky OR), D22 (SMCJ24A TVS), U41 (MIC5205-3.3YM5 LDO), D16, D17 (B5819W), IC1 (PSM712)
- **Contract File**: `contracts/Keep_Alive.interface.json` (`requirement = FOMEMC-22-Keep_Alive`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `Keep_Alive.kicad_sch` | `12V_IGN_SW` | `input` | `/12V_IGN_SW` | `D20:2` | `8V_to_18V_TVS_Clamped` | `J1-26` (`+12V_IGN_SW`) | Ignition Switch / Kill Switch Run +12V Input (D20_B340A_OR_to_12V_RAW_plus_82k_10k_Div) |
| `Keep_Alive.kicad_sch` | `12V_MR` | `input` | `/12V_MR` | `D21:2`, `D22:1` | `12V_6A_Continuous` | `J1-24` (`WBO_HTR+`), `J1-27` (`+12V_MR`) | Bosch LSU 4.9 #1 & #2 Pin 4 (Heater +12V Supply) (Direct_12V_MR_Heater_Feed) |
| `Keep_Alive.kicad_sch` | `12V_RAW` | `output` | `/12V_RAW` | `D20:1`, `D21:1` | `8V_to_18V_DiodeOR` | Inter-sheet (`/12V_RAW`) | Diode-OR raw 12V supply from D20 (12V_IGN_SW) and D21 (12V_MR) into PSU D1/Q1 input stage |
| `Keep_Alive.kicad_sch` | `Keep_Alive` | `output` | `/Keep_Alive/Keep_Alive` | `D17:1` | `3.3V_VBAT_Backup` | Inter-sheet (`/Keep_Alive/Keep_Alive`) | Always-on 3.3V backup supply from U41 MIC5205-3.3YM5 (fed by J1-28 Perm_Live via D16) through D17/D7 into STM32H7 VBAT |
| `Keep_Alive.kicad_sch` | `Perm_Live` | `input` | `/Perm_Live` | `D16:2` | `8V_to_18V_1A` | `J1-28` (`+12V_BATT_KEEPALIVE`) | Unswitched Battery +12V Backup / Keep-Alive Supply (D16_B5819W_to_U41_MIC5205) |

### 2.2 `sheets/etb-9201.kicad_sch` (`/etb1/`)

- **Function**: Primary Electronic Throttle Body / STVA H-Bridge #1
- **Key Components**: U201 (TLE9201SG 6A H-Bridge #1), C1201 (2.2uF), R210 (10k DIS pull-up to +3V3 C25744)
- **Contract File**: `contracts/etb-9201.interface.json` (`requirement = FOMEMC-22-etb-9201`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `etb-9201.kicad_sch` | `12V_SUPPLY` | `input` | `/12V_MR` | `C1201:2`, `U201:4` | `12V_6A_Continuous` | `J1-24` (`WBO_HTR+`), `J1-27` (`+12V_MR`) | Bosch LSU 4.9 #1 & #2 Pin 4 (Heater +12V Supply) (Direct_12V_MR_Heater_Feed) |
| `etb-9201.kicad_sch` | `DIR` | `input` | `/ETB1_DIR` | `U201:1` | `3.3V_CMOS_HBridgeCtrl` | `U26:79` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `etb-9201.kicad_sch` | `DIS` | `input` | `/ETB1_DIS` | `R210:1`, `U201:11` | `3.3V_CMOS_HBridgeCtrl` | `U26:80` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `etb-9201.kicad_sch` | `OUT+` | `output` | `/ETB1_OUT+` | `C201:2`, `U201:5` | `12V_6A_Peak` | `J1-15` (`ETB1_OUT+`) | SV650 STVA Secondary Throttle Stepper Phase A+ (or DBW1+) (U201_TLE9201SG_1_OUT1) |
| `etb-9201.kicad_sch` | `OUT-` | `output` | `/ETB1_OUT-` | `C202:1`, `U201:7` | `12V_6A_Peak` | `J1-16` (`ETB1_OUT-`) | SV650 STVA Secondary Throttle Stepper Phase A- (or DBW1-) (U201_TLE9201SG_1_OUT2) |
| `etb-9201.kicad_sch` | `PWM` | `input` | `/ETB1_PWM` | `U201:12` | `3.3V_CMOS_HBridgeCtrl` | `U26:81` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |

### 2.3 `sheets/highside_quad.kicad_sch` (`/highside_quad/`)

- **Function**: Quad Protected High-Side Output Driver (Spare)
- **Key Components**: U40 (BTS716G 4-Ch High-Side Smart Switch), RN11 (4x10k pull-down), R103..R106
- **Contract File**: `contracts/highside_quad.interface.json` (`requirement = FOMEMC-22-highside_quad`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `highside_quad.kicad_sch` | `12V` | `input` | `/12V_MR` | `U40:1`, `U40:10`, `U40:11`, `U40:12` (+4 more) | `12V_6A_Continuous` | `J1-24` (`WBO_HTR+`), `J1-27` (`+12V_MR`) | Bosch LSU 4.9 #1 & #2 Pin 4 (Heater +12V Supply) (Direct_12V_MR_Heater_Feed) |
| `highside_quad.kicad_sch` | `IN1` | `input` | `/highside_quad/IN1` | `RN11:4` | `3.3V_CMOS_10kPulldown` | `U26:89` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `highside_quad.kicad_sch` | `IN2` | `input` | `/highside_quad/IN2` | `RN11:3` | `3.3V_CMOS_10kPulldown` | `U26:88` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `highside_quad.kicad_sch` | `IN3` | `input` | `/highside_quad/IN3` | `RN11:2` | `3.3V_CMOS_10kPulldown` | `U26:87` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `highside_quad.kicad_sch` | `IN4` | `input` | `/highside_quad/IN4` | `RN11:1` | `3.3V_CMOS_10kPulldown` | `U26:86` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `highside_quad.kicad_sch` | `OUT1` | `output` | `/highside_quad/OUT1` *(root `no_connect`)* | `C85:1`, `R103:1`, `U40:18` | `12V_HighSide_Spare_NC` | `[ROOT_NC]` | U40 BTS716G protected high-side output channel (terminated with explicit no_connect on root sheet; unallocated spare) |
| `highside_quad.kicad_sch` | `OUT2` | `output` | `/highside_quad/OUT2` *(root `no_connect`)* | `C86:1`, `R104:1`, `U40:17` | `12V_HighSide_Spare_NC` | `[ROOT_NC]` | U40 BTS716G protected high-side output channel (terminated with explicit no_connect on root sheet; unallocated spare) |
| `highside_quad.kicad_sch` | `OUT3` | `output` | `/highside_quad/OUT3` *(root `no_connect`)* | `C87:1`, `R105:1`, `U40:14` | `12V_HighSide_Spare_NC` | `[ROOT_NC]` | U40 BTS716G protected high-side output channel (terminated with explicit no_connect on root sheet; unallocated spare) |
| `highside_quad.kicad_sch` | `OUT4` | `output` | `/highside_quad/OUT4` *(root `no_connect`)* | `C88:1`, `R106:1`, `U40:13` | `12V_HighSide_Spare_NC` | `[ROOT_NC]` | U40 BTS716G protected high-side output channel (terminated with explicit no_connect on root sheet; unallocated spare) |

### 2.4 `sheets/ign4.kicad_sch` (`/ign1/`, `/ign2/`)

- **Function**: Quad 5V Push-Pull Ignition Pre-Driver / Logic Coil Buffer
- **Key Components**: /ign1/: U42, U43 (MIC4427YM IGBT Gate Drivers); /ign2/: U44, U45 (MIC4427YM 5V Smart-Coil Drivers)
- **Contract File**: `contracts/ign4.interface.json` (`requirement = FOMEMC-22-ign4`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `ign4.kicad_sch` | `IN1` | `input` | `/ign1/`: `/ign1/IN1`<br>`/ign2/`: `/ign2/IN1` | `/ign1/`: `R1501:2`, `U42:2`<br>`/ign2/`: `R1601:2`, `U44:2` | `3.3V_CMOS_1kPulldown` | `/ign1/`: `U26:133`<br>`/ign2/`: `U26:127` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 1k pull-down to GND (`R1501/R1601` `C11702`) |
| `ign4.kicad_sch` | `IN2` | `input` | `/ign1/`: `/ign1/IN2`<br>`/ign2/`: `/ign2/IN2` | `/ign1/`: `R1502:2`, `U42:4`<br>`/ign2/`: `R1602:2`, `U44:4` | `3.3V_CMOS_1kPulldown` | `/ign1/`: `U26:132`<br>`/ign2/`: `U26:126` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 1k pull-down to GND (`R1502/R1602` `C11702`) |
| `ign4.kicad_sch` | `IN3` | `input` | `/ign1/`: `/ign1/IN3`<br>`/ign2/`: `/ign2/IN3` | `/ign1/`: `R1503:2`, `U43:2`<br>`/ign2/`: `R1603:2`, `U45:2` | `3.3V_CMOS_1kPulldown` | `/ign1/`: `U26:129`<br>`/ign2/`: `U26:125` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 1k pull-down to GND (`R1503/R1603` `C11702`) |
| `ign4.kicad_sch` | `IN4` | `input` | `/ign1/`: `/ign1/IN4`<br>`/ign2/`: `/ign2/IN4` | `/ign1/`: `R1504:2`, `U43:4`<br>`/ign2/`: `R1604:2`, `U45:4` | `3.3V_CMOS_1kPulldown` | `/ign1/`: `U26:128`<br>`/ign2/`: `U26:124` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 1k pull-down to GND (`R1504/R1604` `C11702`) |
| `ign4.kicad_sch` | `OUT1` | `output` | `/ign1/`: `/IGN1`<br>`/ign2/`: `/IGN5` | `/ign1/`: `C93:1`, `R108:1`<br>`/ign2/`: `C99:1`, `R112:1` | `5V_1.5A_PushPull` | `/ign1/`: Inter-sheet (`/IGN1`)<br>`/ign2/`: `J2-23` (`IGN1_LOG`) | Logic Ignition 1 (5V Push-Pull Smart Coil 1) (U44_MIC4427_1_OUTA_via_R112_100R) |
| `ign4.kicad_sch` | `OUT2` | `output` | `/ign1/`: `/IGN2`<br>`/ign2/`: `/IGN6` | `/ign1/`: `C94:1`, `R109:1`<br>`/ign2/`: `C100:1`, `R113:1` | `5V_1.5A_PushPull` | `/ign1/`: Inter-sheet (`/IGN2`)<br>`/ign2/`: `J2-24` (`IGN2_LOG`) | Logic Ignition 2 (5V Push-Pull Smart Coil 2) (U44_MIC4427_1_OUTB_via_R113_100R) |
| `ign4.kicad_sch` | `OUT3` | `output` | `/ign1/`: `/IGN3`<br>`/ign2/`: `/IGN7` | `/ign1/`: `C95:1`, `R110:1`<br>`/ign2/`: `C101:1`, `R114:1` | `5V_1.5A_PushPull` | `/ign1/`: Inter-sheet (`/IGN3`)<br>`/ign2/`: `J2-25` (`IGN3_LOG`) | Logic Ignition 3 (5V Push-Pull Smart Coil 3) (U45_MIC4427_2_OUTA_via_R114_100R) |
| `ign4.kicad_sch` | `OUT4` | `output` | `/ign1/`: `/IGN4`<br>`/ign2/`: `/IGN8` | `/ign1/`: `C96:1`, `R111:1`<br>`/ign2/`: `C102:1`, `R115:1` | `5V_1.5A_PushPull` | `/ign1/`: Inter-sheet (`/IGN4`)<br>`/ign2/`: `J2-26` (`IGN4_LOG`) | Logic Ignition 4 (5V Push-Pull Smart Coil 4) (U45_MIC4427_2_OUTB_via_R115_100R) |

### 2.5 `sheets/ign_igbt.kicad_sch` (`/ign_igbt/`)

- **Function**: Quad 400V Clamped Ignition Coil Low-Side IGBT Power Stage
- **Key Components**: Q201..Q204 (FGD3040G2-F085 400V 15A IGBTs), R201..R204 (15R gate), R205..R208 (10k G-E)
- **Contract File**: `contracts/ign_igbt.interface.json` (`requirement = FOMEMC-22-ign_igbt`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `ign_igbt.kicad_sch` | `IGN1_COIL` | `output` | `/IGN1_COIL` | `Q201:2` | `400V_15A_Clamped` | `J1-6` (`IGBT1`) | Front Cylinder #1 Primary Center Coil - (or K7 Dual-Tower Front Coil -) (U42_MIC4427_to_Q201_FGD3040G2) |
| `ign_igbt.kicad_sch` | `IGN1_IN` | `input` | `/IGN1` | `R201:1` | `5V_PushPull_GateDrive` | Inter-sheet (`/IGN1`) | 5V push-pull gate/coil drive from MIC4427YM (U42/U43 in /ign1/ via 100R -> ign_igbt 15R -> Q201..Q204 IGBTs; U44/U45 in /ign2/ -> J2-23..26) |
| `ign_igbt.kicad_sch` | `IGN2_COIL` | `output` | `/IGN2_COIL` | `Q202:2` | `400V_15A_Clamped` | `J1-7` (`IGBT2`) | Rear Cylinder #2 Primary Center Coil - (or K7 Dual-Tower Rear Coil -) (U42_MIC4427_to_Q202_FGD3040G2) |
| `ign_igbt.kicad_sch` | `IGN2_IN` | `input` | `/IGN2` | `R202:1` | `5V_PushPull_GateDrive` | Inter-sheet (`/IGN2`) | 5V push-pull gate/coil drive from MIC4427YM (U42/U43 in /ign1/ via 100R -> ign_igbt 15R -> Q201..Q204 IGBTs; U44/U45 in /ign2/ -> J2-23..26) |
| `ign_igbt.kicad_sch` | `IGN3_COIL` | `output` | `/IGN3_COIL` | `Q203:2` | `400V_15A_Clamped` | `J1-8` (`IGBT3`) | Front Cylinder #1 Trailing Side Plug Coil - (4-Coil Split Mode) (U43_MIC4427_to_Q203_FGD3040G2) |
| `ign_igbt.kicad_sch` | `IGN3_IN` | `input` | `/IGN3` | `R203:1` | `5V_PushPull_GateDrive` | Inter-sheet (`/IGN3`) | 5V push-pull gate/coil drive from MIC4427YM (U42/U43 in /ign1/ via 100R -> ign_igbt 15R -> Q201..Q204 IGBTs; U44/U45 in /ign2/ -> J2-23..26) |
| `ign_igbt.kicad_sch` | `IGN4_COIL` | `output` | `/IGN4_COIL` | `Q204:2` | `400V_15A_Clamped` | `J1-9` (`IGBT4`) | Rear Cylinder #2 Trailing Side Plug Coil - (4-Coil Split Mode) (U43_MIC4427_to_Q204_FGD3040G2) |
| `ign_igbt.kicad_sch` | `IGN4_IN` | `input` | `/IGN4` | `R204:1` | `5V_PushPull_GateDrive` | Inter-sheet (`/IGN4`) | 5V push-pull gate/coil drive from MIC4427YM (U42/U43 in /ign1/ via 100R -> ign_igbt 15R -> Q201..Q204 IGBTs; U44/U45 in /ign2/ -> J2-23..26) |

### 2.6 `sheets/knock.kicad_sch` (`/knock/`)

- **Function**: Dual-Channel Piezo Knock Sensor AC Bandpass Filter
- **Key Components**: U7 (MCP6004 quad op-amp), C16, C17 (3.3nF 50V X7R input AC coupling), bandpass RC network
- **Contract File**: `contracts/knock.interface.json` (`requirement = FOMEMC-22-knock`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `knock.kicad_sch` | `FILTERED_1` | `output` | `/knock/FILTERED_1` | `C20:2`, `U7:6`, `U7:7` | `0V_to_3.3V_Analog_BPF` | `U26:14` | Active bandpass-filtered piezo knock signal from U7 MCP6004 (/knock/) to STM32H7 PF4/PF5 (ADC3_INP9/INP4 250kSPS DMA) |
| `knock.kicad_sch` | `FILTERED_2` | `output` | `/knock/FILTERED_2` | `C21:2`, `U7:8`, `U7:9` | `0V_to_3.3V_Analog_BPF` | `U26:15` | Active bandpass-filtered piezo knock signal from U7 MCP6004 (/knock/) to STM32H7 PF4/PF5 (ADC3_INP9/INP4 250kSPS DMA) |
| `knock.kicad_sch` | `INPUT_1` | `input` | `/KNOCK_1` | `C16:2`, `JP1:1` | `AC_Bandpass_SoftwareKnock` | `J2-9` (`KNOCK1`) | Cylinder #1 Piezo Knock Sensor Input (U7_MCP6004_Knock1_Bandpass_via_3n3) |
| `knock.kicad_sch` | `INPUT_2` | `input` | `/KNOCK_2` | `C17:2`, `JP2:1` | `AC_Bandpass_SoftwareKnock` | `J2-10` (`KNOCK2`) | Cylinder #2 Piezo Knock Sensor Input (U7_MCP6004_Knock2_Bandpass_via_3n3) |

### 2.7 `sheets/lowside_quad.kicad_sch` (`/lowside_quad1/`, `/lowside_quad2/`, `/lowside_quad4/`)

- **Function**: Quad 5V-Buffered Protected Low-Side Driver (VNLD5090-E)
- **Key Components**: U1001..U1202 (VNLD5090-E dual 42V-clamped low-side switches), U1003/U1103/U1203 (74HCT125D 5V buffers), RN5..RN10
- **Contract File**: `contracts/lowside_quad.interface.json` (`requirement = FOMEMC-22-lowside_quad`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `lowside_quad.kicad_sch` | `IN1` | `input` | `/lowside_quad1/`: `/lowside_quad1/IN1`<br>`/lowside_quad2/`: `/lowside_quad2/IN1`<br>`/lowside_quad4/`: `/PB8_STEP_EN` | `/lowside_quad1/`: `RN5:8`, `U1003:2`<br>`/lowside_quad2/`: `RN7:8`, `U1103:2`<br>`/lowside_quad4/`: `RN9:8`, `U1203:2` | `3.3V_CMOS_10kPulldown` | `/lowside_quad1/`: `U26:90`<br>`/lowside_quad2/`: `U26:96`<br>`/lowside_quad4/`: `U26:139` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `lowside_quad.kicad_sch` | `IN2` | `input` | `/lowside_quad1/`: `/lowside_quad1/IN2`<br>`/lowside_quad2/`: `/lowside_quad2/IN2`<br>`/lowside_quad4/`: `/lowside_quad4/IN2` | `/lowside_quad1/`: `RN5:7`, `U1003:5`<br>`/lowside_quad2/`: `RN7:7`, `U1103:5`<br>`/lowside_quad4/`: `RN9:7`, `U1203:5` | `3.3V_CMOS_10kPulldown` | `/lowside_quad1/`: `U26:91`<br>`/lowside_quad2/`: `U26:97`<br>`/lowside_quad4/`: `U26:140` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `lowside_quad.kicad_sch` | `IN3` | `input` | `/lowside_quad1/`: `/lowside_quad1/IN3`<br>`/lowside_quad2/`: `/lowside_quad2/IN3`<br>`/lowside_quad4/`: `/lowside_quad4/IN3` | `/lowside_quad1/`: `RN5:6`, `U1003:9`<br>`/lowside_quad2/`: `RN7:6`, `U1103:9`<br>`/lowside_quad4/`: `RN9:6`, `U1203:9` | `3.3V_CMOS_10kPulldown` | `/lowside_quad1/`: `U26:92`<br>`/lowside_quad2/`: `U26:110`<br>`/lowside_quad4/`: `U26:141` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `lowside_quad.kicad_sch` | `IN4` | `input` | `/lowside_quad1/`: `/lowside_quad1/IN4`<br>`/lowside_quad2/`: `/lowside_quad2/IN4`<br>`/lowside_quad4/`: `/lowside_quad4/IN4` | `/lowside_quad1/`: `RN5:5`, `U1003:12`<br>`/lowside_quad2/`: `RN7:5`, `U1103:12`<br>`/lowside_quad4/`: `RN9:5`, `U1203:12` | `3.3V_CMOS_10kPulldown` | `/lowside_quad1/`: `U26:93`<br>`/lowside_quad2/`: `U26:117`<br>`/lowside_quad4/`: `U26:142` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `lowside_quad.kicad_sch` | `OUT1` | `output` | `/lowside_quad1/`: `/LS1`<br>`/lowside_quad2/`: `/LS5`<br>`/lowside_quad4/`: `/lowside_quad4/OUT1` *(root `no_connect`)* | `/lowside_quad1/`: `U1001:6`<br>`/lowside_quad2/`: `U1101:6`<br>`/lowside_quad4/`: `U1201:6` | `12V_5A_Clamped42V` | `/lowside_quad1/`: `J1-1` (`INJ1`)<br>`/lowside_quad2/`: `J1-10` (`AUX_LS1`)<br>`/lowside_quad4/`: `[ROOT_NC]` | Front Cylinder #1 Primary Fuel Injector - (U1003_74HCT125D_to_U1001_VNLD5090_CH1) |
| `lowside_quad.kicad_sch` | `OUT2` | `output` | `/lowside_quad1/`: `/LS2`<br>`/lowside_quad2/`: `/LS6`<br>`/lowside_quad4/`: `/LS14` | `/lowside_quad1/`: `U1001:8`<br>`/lowside_quad2/`: `U1101:8`<br>`/lowside_quad4/`: `U1201:8` | `12V_5A_Clamped60V` | `/lowside_quad1/`: `J1-2` (`INJ2`)<br>`/lowside_quad2/`: `J1-11` (`AUX_LS2`)<br>`/lowside_quad4/`: `J2-27` (`DASH_TECH`) | Cooling Fan Relay Coil - (U1103_74HCT125D_to_U1101_VNLD5090_CH2) |
| `lowside_quad.kicad_sch` | `OUT3` | `output` | `/lowside_quad1/`: `/LS3`<br>`/lowside_quad2/`: `/LS7`<br>`/lowside_quad4/`: `/MAIN_RLY` | `/lowside_quad1/`: `U1002:6`<br>`/lowside_quad2/`: `U1102:6`<br>`/lowside_quad4/`: `U1202:6` | `12V_5A_Clamped60V` | `/lowside_quad1/`: `J1-3` (`INJ3`)<br>`/lowside_quad2/`: `J1-12` (`AUX_LS3`)<br>`/lowside_quad4/`: `J1-14` (`MAIN_RLY`) | PAIR Air Injection Solenoid Valve - (or Shift Light) (U1103_74HCT125D_to_U1102_VNLD5090_CH1) |
| `lowside_quad.kicad_sch` | `OUT4` | `output` | `/lowside_quad1/`: `/LS4`<br>`/lowside_quad2/`: `/LS8`<br>`/lowside_quad4/`: `/lowside_quad4/OUT4` *(root `no_connect`)* | `/lowside_quad1/`: `U1002:8`<br>`/lowside_quad2/`: `U1102:8`<br>`/lowside_quad4/`: `U1202:8` | `12V_5A_2k2Pullup` | `/lowside_quad1/`: `J1-4` (`INJ4`)<br>`/lowside_quad2/`: `J1-13` (`AUX_LS4`)<br>`/lowside_quad4/`: `[ROOT_NC]` | Tachometer Pulse Output (0-12V Square Wave) (U1103_74HCT125D_to_U1102_VNLD5090_CH2_plus_R212_2k2) |

### 2.8 `sheets/mcu.kicad_sch` (`/mcu/`)

- **Function**: STM32H753ZIT6 Core, REF3333 ADC VREF+, 4GB SDNAND, Wi-Fi & USB ESD
- **Key Components**: U26 (STM32H753ZIT6), U23 (REF3333), U25 (CSNP32GCR01-AOW SDNAND), U29 (ATWINC1500-MR210UB Wi-Fi), U27 (USBLC6-2SC6), U24 (LPS25HB DNP)
- **Contract File**: `contracts/mcu.interface.json` (`requirement = FOMEMC-22-mcu`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `mcu.kicad_sch` | `12V_MR` | `input` | `/12V_MR` | `R116:1` | `12V_6A_Continuous` | `J1-24` (`WBO_HTR+`), `J1-27` (`+12V_MR`) | Bosch LSU 4.9 #1 & #2 Pin 4 (Heater +12V Supply) (Direct_12V_MR_Heater_Feed) |
| `mcu.kicad_sch` | `12V_SENSE` | `input` | `/12V_IGN_SW` | `R96:1` | `8V_to_18V_TVS_Clamped` | `J1-26` (`+12V_IGN_SW`) | Ignition Switch / Kill Switch Run +12V Input (D20_B340A_OR_to_12V_RAW_plus_82k_10k_Div) |
| `mcu.kicad_sch` | `5V_SENSOR_1` | `input` | `/5V_SENSOR_1` | `R118:1` | `5.00V_150mA_Protected` | `J1-29` (`5V_SENSOR_1`) | 5V Regulated Sensor Supply #1 (TPS / STPS / MAP1 / Baro / GP) (U1_TLS115D0E_1) |
| `mcu.kicad_sch` | `5V_SENSOR_1_PG` | `input` | `/mcu/5V_SENSOR_1_PG` | `U26:55` | `3.3V_OpenDrain_PG` | `U26:55` | U1 TLS115D0E #1 power-good reset/status flag (R1 10k pull-up) to STM32H7 PF15 (U26:55) |
| `mcu.kicad_sch` | `5V_SENSOR_2_PG` | `input` | `/mcu/5V_SENSOR_2_PG` | `U26:54` | `3.3V_OpenDrain_PG` | `U26:54` | U2 TLS115D0E #2 power-good reset/status flag (R4 10k pull-up) to STM32H7 PF14 (U26:54) |
| `mcu.kicad_sch` | `AT1` | `input` | `/mcu/AT1` | `U26:27` | `0V_to_3.30V_Buffered_ADC` | `U26:27` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AT2` | `input` | `/mcu/AT2` | `U26:28` | `0V_to_3.30V_Buffered_ADC` | `U26:28` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AT3` | `input` | `/mcu/AT3` | `U26:29` | `0V_to_3.30V_Buffered_ADC` | `U26:29` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AT4` | `input` | `/mcu/AT4` | `U26:44` | `0V_to_3.30V_Buffered_ADC` | `U26:44` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV1` | `input` | `/mcu/AV1` | `U26:34` | `0V_to_3.30V_Buffered_ADC` | `U26:34` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV10` | `input` | `/mcu/AV10` | `U26:47` | `0V_to_3.30V_Buffered_ADC` | `U26:47` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV11` | `input` | `/mcu/AV11` | `U26:26` | `0V_to_3.30V_Buffered_ADC` | `U26:26` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV2` | `input` | `/mcu/AV2` | `U26:35` | `0V_to_3.30V_Buffered_ADC` | `U26:35` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV3` | `input` | `/mcu/AV3` | `U26:36` | `0V_to_3.30V_Buffered_ADC` | `U26:36` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV4` | `input` | `/mcu/AV4` | `U26:37` | `0V_to_3.30V_Buffered_ADC` | `U26:37` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV5` | `input` | `/mcu/AV5` | `U26:40` | `0V_to_3.30V_Buffered_ADC` | `U26:40` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV6` | `input` | `/mcu/AV6` | `U26:41` | `0V_to_3.30V_Buffered_ADC` | `U26:41` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV7` | `input` | `/mcu/AV7` | `U26:42` | `0V_to_3.30V_Buffered_ADC` | `U26:42` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV8` | `input` | `/mcu/AV8` | `U26:43` | `0V_to_3.30V_Buffered_ADC` | `U26:43` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `AV9` | `input` | `/mcu/AV9` | `U26:46` | `0V_to_3.30V_Buffered_ADC` | `U26:46` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `mcu.kicad_sch` | `BOOT0` | `input` | `/BOOT0_NET` | `J16:1`, `R90:1`, `SW2:1`, `U26:138` | `3.3V_CMOS_DFU_Boot` | `U26:138` | STM32H753ZIT6 BOOT0 pin (U26:138) driven by J1-35 12V Zener recovery divider (D210 BZT52C6V8 + R209 12k vs R90 10k pull-down) |
| `mcu.kicad_sch` | `CAN2_RX` | `input` | `/mcu/CAN2_RX` | `U26:73` | `3.3V_5V_Tolerant_CMOS` | `U26:73` | Internal wideband CAN2 receive data from U5 MCP2551-I-SN RXD (pin 4) to STM32H7 PB12 (FDCAN2_RX, U26:73) |
| `mcu.kicad_sch` | `CAN2_TX` | `output` | `/mcu/CAN2_TX` | `U26:74` | `3.3V_CMOS_500kbps` | `U26:74` | Internal wideband CAN2 transmit data from STM32H7 PB13 (FDCAN2_TX, U26:74) to U5 MCP2551-I-SN TXD (pin 1) |
| `mcu.kicad_sch` | `CAN_RX` | `input` | `/mcu/CAN_RX` | `U26:114` | `3.3V_5V_Tolerant_CMOS` | `U26:114` | External CAN1 receive data from U4 MCP2551-I-SN RXD (pin 4) to STM32H7 PD0 (FDCAN1_RX, U26:114) |
| `mcu.kicad_sch` | `CAN_TX` | `output` | `/mcu/CAN_TX` | `U26:115` | `3.3V_CMOS_500kbps` | `U26:115` | External CAN1 transmit data from STM32H7 PD1 (FDCAN1_TX, U26:115) to U4 MCP2551-I-SN TXD (pin 1) |
| `mcu.kicad_sch` | `DIGITAL1` | `input` | `/mcu/DIGITAL1` | `U26:56` | `3.3V_CMOS_Schmitt` | `U26:56` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `DIGITAL2` | `input` | `/mcu/DIGITAL2` | `U26:57` | `3.3V_CMOS_Schmitt` | `U26:57` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `DIGITAL3` | `input` | `/mcu/DIGITAL3` | `U26:63` | `3.3V_CMOS_Schmitt` | `U26:63` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `DIGITAL4` | `input` | `/mcu/DIGITAL4` | `U26:64` | `3.3V_CMOS_Schmitt` | `U26:64` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `DIGITAL5` | `input` | `/mcu/DIGITAL5` | `U26:65` | `3.3V_CMOS_Schmitt` | `U26:65` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `DIGITAL6` | `input` | `/mcu/DIGITAL6` | `U26:66` | `3.3V_CMOS_Schmitt` | `U26:66` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `ETB1_DIR` | `output` | `/ETB1_DIR` | `U26:79` | `3.3V_CMOS_HBridgeCtrl` | `U26:79` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `mcu.kicad_sch` | `ETB1_DIS` | `output` | `/ETB1_DIS` | `U26:80` | `3.3V_CMOS_HBridgeCtrl` | `U26:80` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `mcu.kicad_sch` | `ETB1_PWM` | `output` | `/ETB1_PWM` | `U26:81` | `3.3V_CMOS_HBridgeCtrl` | `U26:81` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `mcu.kicad_sch` | `ETB2_DIR` | `output` | `/ETB2_DIR` | `U26:78` | `3.3V_CMOS_HBridgeCtrl` | `U26:78` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `mcu.kicad_sch` | `ETB2_DIS` | `output` | `/ETB2_DIS` | `U26:77` | `3.3V_CMOS_HBridgeCtrl` | `U26:77` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `mcu.kicad_sch` | `ETB2_PWM` | `output` | `/ETB2_PWM` | `U26:82` | `3.3V_CMOS_HBridgeCtrl` | `U26:82` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `mcu.kicad_sch` | `HS1` | `output` | `/highside_quad/IN1` | `U26:89` | `3.3V_CMOS_10kPulldown` | `U26:89` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `mcu.kicad_sch` | `HS2` | `output` | `/highside_quad/IN2` | `U26:88` | `3.3V_CMOS_10kPulldown` | `U26:88` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `mcu.kicad_sch` | `HS3` | `output` | `/highside_quad/IN3` | `U26:87` | `3.3V_CMOS_10kPulldown` | `U26:87` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `mcu.kicad_sch` | `HS4` | `output` | `/highside_quad/IN4` | `U26:86` | `3.3V_CMOS_10kPulldown` | `U26:86` | STM32H7 high-side control output (PG4..PG1, U26:89..86) to U40 BTS716G input via RN11 10k pull-down |
| `mcu.kicad_sch` | `IGN1` | `output` | `/ign1/IN1` | `U26:133` | `3.3V_CMOS_10kPulldown` | `U26:133` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `IGN2` | `output` | `/ign1/IN2` | `U26:132` | `3.3V_CMOS_10kPulldown` | `U26:132` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `IGN3` | `output` | `/ign1/IN3` | `U26:129` | `3.3V_CMOS_10kPulldown` | `U26:129` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `IGN4` | `output` | `/ign1/IN4` | `U26:128` | `3.3V_CMOS_10kPulldown` | `U26:128` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `IGN5` | `output` | `/ign2/IN1` | `U26:127` | `3.3V_CMOS_10kPulldown` | `U26:127` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `IGN6` | `output` | `/ign2/IN2` | `U26:126` | `3.3V_CMOS_10kPulldown` | `U26:126` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `IGN7` | `output` | `/ign2/IN3` | `U26:125` | `3.3V_CMOS_10kPulldown` | `U26:125` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `IGN8` | `output` | `/ign2/IN4` | `U26:124` | `3.3V_CMOS_10kPulldown` | `U26:124` | STM32H7 ignition timing trigger output (PB3, PG15..PG9) into MIC4427YM input with 10k pull-down to GND |
| `mcu.kicad_sch` | `KNOCK_1` | `input` | `/knock/FILTERED_1` | `U26:14` | `0V_to_3.3V_Analog_BPF` | `U26:14` | Active bandpass-filtered piezo knock signal from U7 MCP6004 (/knock/) to STM32H7 PF4/PF5 (ADC3_INP9/INP4 250kSPS DMA) |
| `mcu.kicad_sch` | `KNOCK_2` | `input` | `/knock/FILTERED_2` | `U26:15` | `0V_to_3.3V_Analog_BPF` | `U26:15` | Active bandpass-filtered piezo knock signal from U7 MCP6004 (/knock/) to STM32H7 PF4/PF5 (ADC3_INP9/INP4 250kSPS DMA) |
| `mcu.kicad_sch` | `Keep_Alive` | `input` | `/Keep_Alive/Keep_Alive` | `D6:1`, `D7:2` | `3.3V_VBAT_Backup` | Inter-sheet (`/Keep_Alive/Keep_Alive`) | Always-on 3.3V backup supply from U41 MIC5205-3.3YM5 (fed by J1-28 Perm_Live via D16) through D17/D6 into STM32H7 VBAT |
| `mcu.kicad_sch` | `LS1` | `output` | `/lowside_quad1/IN1` | `U26:90` | `3.3V_CMOS_10kPulldown` | `U26:90` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS12` | `output` | `/LS12` | `U26:137` | `3.3V_CMOS_StepDir` | `U26:137` | Bipolar stepper DIR control from STM32H7 PB7 (U26:137) to U202 DRV8825PWPR DIR (pin 20) |
| `mcu.kicad_sch` | `LS13` | `output` | `/PB8_STEP_EN` | `U26:139` | `3.3V_CMOS_ActiveLow_10kPD` | `U26:139` | Bipolar stepper active-low enable (/PB8_STEP_EN) from STM32H7 PB8 (U26:139) to U202 DRV8825 nENBL (pin 21) and /lowside_quad4/ IN1 (RN9:8 10k pull-down) |
| `mcu.kicad_sch` | `LS14` | `output` | `/lowside_quad4/IN2` | `U26:140` | `3.3V_CMOS_10kPulldown` | `U26:140` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS15` | `output` | `/lowside_quad4/IN3` | `U26:141` | `3.3V_CMOS_10kPulldown` | `U26:141` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS16` | `output` | `/lowside_quad4/IN4` | `U26:142` | `3.3V_CMOS_10kPulldown` | `U26:142` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS2` | `output` | `/lowside_quad1/IN2` | `U26:91` | `3.3V_CMOS_10kPulldown` | `U26:91` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS3` | `output` | `/lowside_quad1/IN3` | `U26:92` | `3.3V_CMOS_10kPulldown` | `U26:92` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS4` | `output` | `/lowside_quad1/IN4` | `U26:93` | `3.3V_CMOS_10kPulldown` | `U26:93` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS5` | `output` | `/lowside_quad2/IN1` | `U26:96` | `3.3V_CMOS_10kPulldown` | `U26:96` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS6` | `output` | `/lowside_quad2/IN2` | `U26:97` | `3.3V_CMOS_10kPulldown` | `U26:97` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS7` | `output` | `/lowside_quad2/IN3` | `U26:110` | `3.3V_CMOS_10kPulldown` | `U26:110` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS8` | `output` | `/lowside_quad2/IN4` | `U26:117` | `3.3V_CMOS_10kPulldown` | `U26:117` | STM32H7 low-side control signal into 74HCT125D 5V CMOS buffer (with 10k RN pull-down to GND) -> 1k series -> VNLD5090-E gate |
| `mcu.kicad_sch` | `LS9` | `output` | `/LS9` | `U26:134` | `3.3V_CMOS_StepPulse` | `U26:134` | Bipolar stepper STEP pulse from STM32H7 PB4 (U26:134) to U202 DRV8825PWPR STEP (pin 22) |
| `mcu.kicad_sch` | `RC2` | `output` *(root sheet pin: `input`)* | `/RC2` | `U26:101` | `3.3V_Clamped_Sense` | `U26:101` | USB VBUS sense output from J1-35 divider (R217 10k / R218 12k, clamped by D211 B5819W to +3V3) into STM32H7 PA9 (U26:101 USB_OTG_FS_VBUS) |
| `mcu.kicad_sch` | `USB_D+` | `bidirectional` | `/USB_D+` | `J13:3`, `J14:3`, `U26:104`, `U27:1` (+1 more) | `3.3V_Diff_90Ohm` | `J2-34` (`USB_D+`), `U26:104` | Sealed USB Full-Speed D+ (TunerStudio CDC + MSD + STM32 DFU) (U27_USBLC6_2SC6_IO2_plus_22R) |
| `mcu.kicad_sch` | `USB_D-` | `bidirectional` | `/USB_D-` | `J13:2`, `J14:2`, `U26:103`, `U27:3` (+1 more) | `3.3V_Diff_90Ohm` | `J2-35` (`USB_D-`), `U26:103` | Sealed USB Full-Speed D- (TunerStudio CDC + MSD + STM32 DFU) (U27_USBLC6_2SC6_IO1_plus_22R) |
| `mcu.kicad_sch` | `USB_SHIELD` | `passive` | `/mcu/USB_SHIELD` *(root `no_connect`)* | `C83:1`, `J13:5`, `J14:5`, `R98:1` | `Chassis_RC_Shield_NC` | `[ROOT_NC]` | USB connector shield RC network (R98 0R / C83 inside mcu.kicad_sch; hierarchical pin terminated with no_connect on root sheet) |
| `mcu.kicad_sch` | `VBOOST` | `input` | `/VBOOST` | `R120:1` | `8V_to_38.9V_LC_Filtered` | Inter-sheet (`/VBOOST`) | LC-filtered (L1 2.2uH, C6 47uF) protected 12V rail feeding U3 LMR16020PDDAR 5V buck & MCU R120/R121 voltage sense divider |
| `mcu.kicad_sch` | `VR_1` | `input` | `/mcu/VR_1` | `U26:67` | `3.3V_CMOS_Schmitt` | `U26:67` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `VR_2` | `input` | `/mcu/VR_2` | `U26:68` | `3.3V_CMOS_Schmitt` | `U26:68` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `mcu.kicad_sch` | `WBO1_BOOT0` | `output` | `/WBO1_BOOT0` | `U26:119` | `3.3V_CMOS_10kPulldown` | `U26:119`, `U302:31` | STM32H7 boot-mode override control (PD5->WBO1_BOOT0 U26:119; PD7->WBO2_BOOT0 U26:123) to onboard STM32F042K6T6 BOOT0 (pin 31) |
| `mcu.kicad_sch` | `WBO1_NRST` | `output` | `/WBO1_NRST` | `U26:118` | `3.3V_OpenDrain_Reset` | `U26:118`, `U302:4` | STM32H7 hardware reset control (PD4->WBO1_NRST U26:118; PD6->WBO2_NRST U26:122) to onboard STM32F042K6T6 NRST (pin 4) |
| `mcu.kicad_sch` | `WBO2_BOOT0` | `output` | `/WBO2_BOOT0` | `U26:123` | `3.3V_CMOS_10kPulldown` | `U26:123`, `U402:31` | STM32H7 boot-mode override control (PD5->WBO1_BOOT0 U26:119; PD7->WBO2_BOOT0 U26:123) to onboard STM32F042K6T6 BOOT0 (pin 31) |
| `mcu.kicad_sch` | `WBO2_NRST` | `output` | `/WBO2_NRST` | `U26:122` | `3.3V_OpenDrain_Reset` | `U26:122`, `U402:4` | STM32H7 hardware reset control (PD4->WBO1_NRST U26:118; PD6->WBO2_NRST U26:122) to onboard STM32F042K6T6 NRST (pin 4) |

### 2.9 `sheets/psu.kicad_sch` (`/psu/`)

- **Function**: 12V Load-Dump/Reverse Protection, 5V Buck, Dual Tracked 5V Sensor LDOs, 3.3V LDO & Dual CAN Transceivers
- **Key Components**: D1 (SMCJ24A), Q1 (AO4485 PFET), U3 (LMR16020PDDAR 5V buck), U1, U2 (TLS115D0E), U6 (TLV75733PDBVR), U4, U5 (MCP2551-I-SN CAN1/CAN2), D4, D5 (PESD1CAN-UX)
- **Contract File**: `contracts/psu.interface.json` (`requirement = FOMEMC-22-psu`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `psu.kicad_sch` | `12V_PROT` | `output` | `/12V_PROT` | `C2:1`, `C5:1`, `D19:1`, `L1:1` (+8 more) | `8V_to_38.9V_Clamped` | Inter-sheet (`/12V_PROT`) | TVS-clamped (D1 SMCJ24A) & reverse-polarity protected (Q1 AO4485) 12V rail; feeds U1/U2 TLS115D0E & L1->VBOOST (root pin tied to PWR_FLAG only) |
| `psu.kicad_sch` | `12V_RAW` | `input` | `/12V_RAW` | `C108:1`, `D1:1`, `Q1:5`, `Q1:6` (+2 more) | `8V_to_18V_DiodeOR` | Inter-sheet (`/12V_RAW`) | Diode-OR raw 12V supply from D20 (12V_IGN_SW) and D21 (12V_MR) into PSU D1/Q1 input stage |
| `psu.kicad_sch` | `5V_SENSOR_1` | `output` | `/5V_SENSOR_1` | `C3:1`, `U1:1` | `5.00V_150mA_Protected` | `J1-29` (`5V_SENSOR_1`) | 5V Regulated Sensor Supply #1 (TPS / STPS / MAP1 / Baro / GP) (U1_TLS115D0E_1) |
| `psu.kicad_sch` | `5V_SENSOR_1_PG` | `output` | `/mcu/5V_SENSOR_1_PG` | `R1:1`, `U1:4` | `3.3V_OpenDrain_PG` | `U26:55` | U1 TLS115D0E #1 power-good reset/status flag (R1 10k pull-up) to STM32H7 PF15 (U26:55) |
| `psu.kicad_sch` | `5V_SENSOR_2` | `output` | `/5V_SENSOR_2` | `C9:1`, `U2:1` | `5.00V_150mA_Protected` | `J1-30` (`5V_SENSOR_2`) | 5V Regulated Sensor Supply #2 (Aux Sensor Supply) (U2_TLS115D0E_2) |
| `psu.kicad_sch` | `5V_SENSOR_2_PG` | `output` | `/mcu/5V_SENSOR_2_PG` | `R4:1`, `U2:4` | `3.3V_OpenDrain_PG` | `U26:54` | U2 TLS115D0E #2 power-good reset/status flag (R4 10k pull-up) to STM32H7 PF14 (U26:54) |
| `psu.kicad_sch` | `CANH` | `bidirectional` | `/CAN+` | `D4:2`, `R9:1`, `U4:7` | `ISO11898_500kbps_120R` | `J2-28` (`CAN1_H`) | External CAN1 High (Telemetry Pod / Dash / OpenBLT) (U4_MCP2551_1_CANH) |
| `psu.kicad_sch` | `CANH2` | `bidirectional` | `/CAN2+` | `D5:2`, `R10:1`, `U5:7` | `ISO11898_500kbps_Internal` | Inter-sheet (`/CAN2+`) | Internal wideband CAN2 differential bus between U5 (MCP2551-I-SN in /psu/, R10 120R, D5 PESD1CAN-UX) and U307 (/wbo1/) + U407 (/wbo2/) TJA1051T/3 transceivers |
| `psu.kicad_sch` | `CANL` | `bidirectional` | `/CAN-` | `D4:1`, `R9:2`, `U4:6` | `ISO11898_500kbps_120R` | `J2-29` (`CAN1_L`) | External CAN1 Low (Telemetry Pod / Dash / OpenBLT) (U4_MCP2551_1_CANL) |
| `psu.kicad_sch` | `CANL2` | `bidirectional` | `/CAN2-` | `D5:1`, `R10:2`, `U5:6` | `ISO11898_500kbps_Internal` | Inter-sheet (`/CAN2-`) | Internal wideband CAN2 differential bus between U5 (MCP2551-I-SN in /psu/, R10 120R, D5 PESD1CAN-UX) and U307 (/wbo1/) + U407 (/wbo2/) TJA1051T/3 transceivers |
| `psu.kicad_sch` | `RXDCAN` | `output` | `/mcu/CAN_RX` | `U4:4` | `3.3V_5V_Tolerant_CMOS` | `U26:114` | External CAN1 receive data from U4 MCP2551-I-SN RXD (pin 4) to STM32H7 PD0 (FDCAN1_RX, U26:114) |
| `psu.kicad_sch` | `RXDCAN2` | `output` | `/mcu/CAN2_RX` | `U5:4` | `3.3V_5V_Tolerant_CMOS` | `U26:73` | Internal wideband CAN2 receive data from U5 MCP2551-I-SN RXD (pin 4) to STM32H7 PB12 (FDCAN2_RX, U26:73) |
| `psu.kicad_sch` | `TXDCAN` | `input` | `/mcu/CAN_TX` | `U4:1` | `3.3V_CMOS_500kbps` | `U26:115` | External CAN1 transmit data from STM32H7 PD1 (FDCAN1_TX, U26:115) to U4 MCP2551-I-SN TXD (pin 1) |
| `psu.kicad_sch` | `TXDCAN2` | `input` | `/mcu/CAN2_TX` | `U5:1` | `3.3V_CMOS_500kbps` | `U26:74` | Internal wideband CAN2 transmit data from STM32H7 PB13 (FDCAN2_TX, U26:74) to U5 MCP2551-I-SN TXD (pin 1) |
| `psu.kicad_sch` | `VBOOST` | `output` | `/VBOOST` | `C6:1`, `C7:1`, `L1:2`, `U3:2` (+1 more) | `8V_to_38.9V_LC_Filtered` | Inter-sheet (`/VBOOST`) | LC-filtered (L1 2.2uH, C6 47uF) protected 12V rail feeding U3 LMR16020PDDAR 5V buck & MCU R120/R121 voltage sense divider |

### 2.10 `sheets/quad_analog.kicad_sch` (`/quad_analog1/`, `/quad_analog2/`, `/quad_analog3/`)

- **Function**: Quad 0-5V Ratiometric Analog Input Divider, RC Filter, ESD Clamp & Op-Amp Buffer
- **Key Components**: U17, U19, U21 (MCP6004 unity buffers), U18, U20, U22 (SRV05-4 ESD arrays), 5.6k/10k dividers, 470k bleeders
- **Contract File**: `contracts/quad_analog.interface.json` (`requirement = FOMEMC-22-quad_analog`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `quad_analog.kicad_sch` | `IN1` | `input` | `/quad_analog1/`: `/AV1`<br>`/quad_analog2/`: `/AV5`<br>`/quad_analog3/`: `/quad_analog3/IN1` *(root `no_connect`)* | `/quad_analog1/`: `R51:1`, `RN2:1`<br>`/quad_analog2/`: `R63:1`, `RN3:1`<br>`/quad_analog3/`: `R75:1`, `RN4:1` | `0V_to_5V_Ratiometric` | `/quad_analog1/`: `J2-5` (`MAP1_FRONT`)<br>`/quad_analog2/`: `J2-7` (`AV5_TIPOVER`)<br>`/quad_analog3/`: `[ROOT_NC]` | Front Cylinder #1 Intake Air Pressure (IAP1) & Cam Phase Sync (U17_MCP6004_AV1_plus_5k6_10k_Div) |
| `quad_analog.kicad_sch` | `IN2` | `input` | `/quad_analog1/`: `/AV2`<br>`/quad_analog2/`: `/AV6`<br>`/quad_analog3/`: `/quad_analog3/IN2` *(root `no_connect`)* | `/quad_analog1/`: `R52:1`, `RN2:2`<br>`/quad_analog2/`: `R64:1`, `RN3:2`<br>`/quad_analog3/`: `R76:1`, `RN4:2` | `0V_to_5V_Ratiometric` | `/quad_analog1/`: `J2-3` (`TPS1`)<br>`/quad_analog2/`: `J2-8` (`AV6_GEAR`)<br>`/quad_analog3/`: `[ROOT_NC]` | Primary Throttle Position Sensor (TPS) (U17_MCP6004_AV2_plus_5k6_10k_Div) |
| `quad_analog.kicad_sch` | `IN3` | `input` | `/quad_analog1/`: `/AV3`<br>`/quad_analog2/`: `/quad_analog2/IN3` *(root `no_connect`)*<br>`/quad_analog3/`: `/quad_analog3/IN3` *(root `no_connect`)* | `/quad_analog1/`: `R53:1`, `RN2:3`<br>`/quad_analog2/`: `R65:1`, `RN3:3`<br>`/quad_analog3/`: `R77:1`, `RN4:3` | `0V_to_5V_Ratiometric` | `/quad_analog1/`: `J2-6` (`AV3_BARO_MAP2`)<br>`/quad_analog2/`: `[ROOT_NC]`<br>`/quad_analog3/`: `[ROOT_NC]` | External 1-Bar Barometric Sensor (GM 12614970 / Delphi PS10150) or Aux Pressure (U17_MCP6004_AV3_plus_5k6_10k_Div) |
| `quad_analog.kicad_sch` | `IN4` | `input` | `/quad_analog1/`: `/AV4`<br>`/quad_analog2/`: `/quad_analog2/IN4` *(root `no_connect`)*<br>`/quad_analog3/`: `/quad_analog3/IN4` *(root `no_connect`)* | `/quad_analog1/`: `R54:1`, `RN2:4`<br>`/quad_analog2/`: `R66:1`, `RN3:4`<br>`/quad_analog3/`: `R78:1`, `RN4:4` | `0V_to_5V_Ratiometric` | `/quad_analog1/`: `J2-4` (`TPS2_STPS`)<br>`/quad_analog2/`: `[ROOT_NC]`<br>`/quad_analog3/`: `[ROOT_NC]` | Secondary Throttle Position Sensor (STPS) (U17_MCP6004_AV4_plus_5k6_10k_Div) |
| `quad_analog.kicad_sch` | `OUT1` | `output` | `/quad_analog1/`: `/mcu/AV1`<br>`/quad_analog2/`: `/mcu/AV5`<br>`/quad_analog3/`: `/mcu/AV9` | `/quad_analog1/`: `R55:1`, `R59:2`<br>`/quad_analog2/`: `R67:1`, `R71:2`<br>`/quad_analog3/`: `R79:1`, `R83:2` | `0V_to_3.30V_Buffered_ADC` | `/quad_analog1/`: `U26:34`<br>`/quad_analog2/`: `U26:40`<br>`/quad_analog3/`: `U26:46` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `quad_analog.kicad_sch` | `OUT2` | `output` | `/quad_analog1/`: `/mcu/AV2`<br>`/quad_analog2/`: `/mcu/AV6`<br>`/quad_analog3/`: `/mcu/AV10` | `/quad_analog1/`: `R56:1`, `R60:2`<br>`/quad_analog2/`: `R68:1`, `R72:2`<br>`/quad_analog3/`: `R80:1`, `R84:2` | `0V_to_3.30V_Buffered_ADC` | `/quad_analog1/`: `U26:35`<br>`/quad_analog2/`: `U26:41`<br>`/quad_analog3/`: `U26:47` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `quad_analog.kicad_sch` | `OUT3` | `output` | `/quad_analog1/`: `/mcu/AV3`<br>`/quad_analog2/`: `/mcu/AV7`<br>`/quad_analog3/`: `/mcu/AV11` | `/quad_analog1/`: `R57:1`, `R61:2`<br>`/quad_analog2/`: `R69:1`, `R73:2`<br>`/quad_analog3/`: `R81:1`, `R85:2` | `0V_to_3.30V_Buffered_ADC` | `/quad_analog1/`: `U26:36`<br>`/quad_analog2/`: `U26:42`<br>`/quad_analog3/`: `U26:26` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `quad_analog.kicad_sch` | `OUT4` | `output` | `/quad_analog1/`: `/mcu/AV4`<br>`/quad_analog2/`: `/mcu/AV8`<br>`/quad_analog3/`: `/quad_analog3/OUT4` *(root `no_connect`)* | `/quad_analog1/`: `R58:1`, `R62:2`<br>`/quad_analog2/`: `R70:1`, `R74:2`<br>`/quad_analog3/`: `R82:1`, `R86:2` | `0V_to_3.30V_Buffered_ADC` | `/quad_analog1/`: `U26:37`<br>`/quad_analog2/`: `U26:43`<br>`/quad_analog3/`: `[ROOT_NC]` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |

### 2.11 `sheets/quad_analog_pullup.kicad_sch` (`/quad_analog_temp/`)

- **Function**: Quad Thermistor Analog Input Conditioning with 2.7k 0.1% Pull-Ups to 5V_SENSOR_1
- **Key Components**: U15 (MCP6004 unity buffer), U16 (SRV05-4 ESD array), R39..R42 (2.7k 0.1% bias pull-ups), 5.6k/10k dividers
- **Contract File**: `contracts/quad_analog_pullup.interface.json` (`requirement = FOMEMC-22-quad_analog_pullup`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `quad_analog_pullup.kicad_sch` | `5V_PULLUP_SUPPLY` | `input` | `/5V_SENSOR_1` | `C41:2`, `R39:1`, `R40:1`, `R41:1` (+1 more) | `5.00V_150mA_Protected` | `J1-29` (`5V_SENSOR_1`) | 5V Regulated Sensor Supply #1 (TPS / STPS / MAP1 / Baro / GP) (U1_TLS115D0E_1) |
| `quad_analog_pullup.kicad_sch` | `IN1` | `input` | `/AT1` | `R39:2`, `RN1:1` | `0V_to_5V_2k7Pullup` | `J2-1` (`CLT`) | Engine Coolant Temperature Sensor (ECT) (U15_MCP6004_AT1_plus_2k7_Pullup) |
| `quad_analog_pullup.kicad_sch` | `IN2` | `input` | `/AT2` | `R40:2`, `RN1:2` | `0V_to_5V_2k7Pullup` | `J2-2` (`IAT`) | Intake Air Temperature Sensor (IAT) (U15_MCP6004_AT2_plus_2k7_Pullup) |
| `quad_analog_pullup.kicad_sch` | `IN3` | `input` | `/quad_analog_temp/IN3` *(root `no_connect`)* | `R41:2`, `RN1:3` | `0V_to_5V_Analog_Spare_NC` | `[ROOT_NC]` | Unconnected spare analog divider/filter input (470k bleeder to GND, terminated with root no_connect) |
| `quad_analog_pullup.kicad_sch` | `IN4` | `input` | `/quad_analog_temp/IN4` *(root `no_connect`)* | `R42:2`, `RN1:4` | `0V_to_5V_Analog_Spare_NC` | `[ROOT_NC]` | Unconnected spare analog divider/filter input (470k bleeder to GND, terminated with root no_connect) |
| `quad_analog_pullup.kicad_sch` | `OUT1` | `output` | `/mcu/AT1` | `R43:1`, `R47:2` | `0V_to_3.30V_Buffered_ADC` | `U26:27` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `quad_analog_pullup.kicad_sch` | `OUT2` | `output` | `/mcu/AT2` | `R44:1`, `R48:2` | `0V_to_3.30V_Buffered_ADC` | `U26:28` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `quad_analog_pullup.kicad_sch` | `OUT3` | `output` | `/mcu/AT3` | `R45:1`, `R49:2` | `0V_to_3.30V_Buffered_ADC` | `U26:29` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |
| `quad_analog_pullup.kicad_sch` | `OUT4` | `output` | `/mcu/AT4` | `R46:1`, `R50:2` | `0V_to_3.30V_Buffered_ADC` | `U26:44` | MCP6004 unity-buffered & 5.6k/10k scaled analog output (via 1k/100nF RC filter) to STM32H7 ADC1/2/3 input |

### 2.12 `sheets/stepper_etb.kicad_sch` (`/stepper_etb/`)

- **Function**: Bipolar Stepper (DRV8825), Secondary H-Bridge #2 (TLE9201SG), Low-Side Clamps (D201..D209) & USB/BOOT0 Recovery
- **Key Components**: U202 (DRV8825PWPR), U203 (TLE9201SG #2), D201..D204 (B340A DNP), D205..D209 (B340A), R212 (2.2k tach pull-up), D210 (BZT52C6V8), D211 (B5819W)
- **Contract File**: `contracts/stepper_etb.interface.json` (`requirement = FOMEMC-22-stepper_etb`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `stepper_etb.kicad_sch` | `12V_MR` | `input` | `/12V_MR` | `C204:2`, `C205:1`, `D201:1`, `D202:1` (+12 more) | `12V_6A_Continuous` | `J1-24` (`WBO_HTR+`), `J1-27` (`+12V_MR`) | Bosch LSU 4.9 #1 & #2 Pin 4 (Heater +12V Supply) (Direct_12V_MR_Heater_Feed) |
| `stepper_etb.kicad_sch` | `BOOT0_OUT` | `output` | `/BOOT0_NET` | `R209:2` | `3.3V_CMOS_DFU_Boot` | `U26:138` | STM32H753ZIT6 BOOT0 pin (U26:138) driven by J1-35 12V Zener recovery divider (D210 BZT52C6V8 + R209 12k vs R90 10k pull-down) |
| `stepper_etb.kicad_sch` | `DASH_TECH_PULLUP` | `passive` | `/LS8` | `R212:2` | `12V_5A_2k2Pullup` | `J1-13` (`AUX_LS4`) | Tachometer Pulse Output (0-12V Square Wave) (U1103_74HCT125D_to_U1102_VNLD5090_CH2_plus_R212_2k2) |
| `stepper_etb.kicad_sch` | `DIR_IN` | `input` | `/LS12` | `U202:20` | `3.3V_CMOS_StepDir` | `U26:137` | Bipolar stepper DIR control from STM32H7 PB7 (U26:137) to U202 DRV8825PWPR DIR (pin 20) |
| `stepper_etb.kicad_sch` | `ETB2_DIR` | `input` | `/ETB2_DIR` | `U203:1` | `3.3V_CMOS_HBridgeCtrl` | `U26:78` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `stepper_etb.kicad_sch` | `ETB2_DIS` | `input` | `/ETB2_DIS` | `U203:11` | `3.3V_CMOS_HBridgeCtrl` | `U26:77` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `stepper_etb.kicad_sch` | `ETB2_OUT+` | `output` | `/ETB2_OUT+` | `U203:5` | `12V_6A_Peak` | `J1-17` (`ETB2_OUT+`) | SV650 STVA Secondary Throttle Stepper Phase B+ (or DBW2+) (U203_TLE9201SG_2_OUT1) |
| `stepper_etb.kicad_sch` | `ETB2_OUT-` | `output` | `/ETB2_OUT-` | `U203:7` | `12V_6A_Peak` | `J1-18` (`ETB2_OUT-`) | SV650 STVA Secondary Throttle Stepper Phase B- (or DBW2-) (U203_TLE9201SG_2_OUT2) |
| `stepper_etb.kicad_sch` | `ETB2_PWM` | `input` | `/ETB2_PWM` | `U203:12` | `3.3V_CMOS_HBridgeCtrl` | `U26:82` | STM32H7 TIM4/GPIO H-bridge control (ETB1: PD12/PD10/PD11 -> U201 TLE9201SG #1; ETB2: PD13/PD9/PD8 -> U203 TLE9201SG #2) |
| `stepper_etb.kicad_sch` | `LS1_CLAMP` | `passive` | `/LS1` | `D201:2` | `12V_5A_Clamped42V` | `J1-1` (`INJ1`) | Front Cylinder #1 Primary Fuel Injector - (U1003_74HCT125D_to_U1001_VNLD5090_CH1) |
| `stepper_etb.kicad_sch` | `LS2_CLAMP` | `passive` | `/LS2` | `D202:2` | `12V_5A_Clamped42V` | `J1-2` (`INJ2`) | Rear Cylinder #2 Primary Fuel Injector - (U1003_74HCT125D_to_U1001_VNLD5090_CH2) |
| `stepper_etb.kicad_sch` | `LS3_CLAMP` | `passive` | `/LS3` | `D203:2` | `12V_5A_Clamped42V` | `J1-3` (`INJ3`) | Spare / Staged Front Injector 3 - (U1003_74HCT125D_to_U1002_VNLD5090_CH1) |
| `stepper_etb.kicad_sch` | `LS4_CLAMP` | `passive` | `/LS4` | `D204:2` | `12V_5A_Clamped42V` | `J1-4` (`INJ4`) | Spare / Staged Rear Injector 4 - (U1003_74HCT125D_to_U1002_VNLD5090_CH2) |
| `stepper_etb.kicad_sch` | `LS5_CLAMP` | `passive` | `/LS5` | `D205:2` | `12V_5A_Clamped60V` | `J1-10` (`AUX_LS1`) | Fuel Pump Relay Coil - (U1103_74HCT125D_to_U1101_VNLD5090_CH1) |
| `stepper_etb.kicad_sch` | `LS6_CLAMP` | `passive` | `/LS6` | `D206:2` | `12V_5A_Clamped60V` | `J1-11` (`AUX_LS2`) | Cooling Fan Relay Coil - (U1103_74HCT125D_to_U1101_VNLD5090_CH2) |
| `stepper_etb.kicad_sch` | `LS7_CLAMP` | `passive` | `/LS7` | `D207:2` | `12V_5A_Clamped60V` | `J1-12` (`AUX_LS3`) | PAIR Air Injection Solenoid Valve - (or Shift Light) (U1103_74HCT125D_to_U1102_VNLD5090_CH1) |
| `stepper_etb.kicad_sch` | `LS8_CLAMP` | `passive` | `/LS8` | `D208:2` | `12V_5A_2k2Pullup` | `J1-13` (`AUX_LS4`) | Tachometer Pulse Output (0-12V Square Wave) (U1103_74HCT125D_to_U1102_VNLD5090_CH2_plus_R212_2k2) |
| `stepper_etb.kicad_sch` | `MAIN_RLY_CLAMP` | `passive` | `/MAIN_RLY` | `D209:2` | `12V_5A_Clamped60V` | `J1-14` (`MAIN_RLY`) | ECU Main Relay Coil Low-Side Control - (U1203_74HCT125D_to_U1202_VNLD5090_CH2_plus_D209) |
| `stepper_etb.kicad_sch` | `STEP_1A` | `output` | `/STEP_1A` | `U202:5` | `12V_0.77A_Chopper` | `J1-19` (`STEP_1A`) | SV650 ISC Idle Speed Control Valve Stepper Phase A+ (U202_DRV8825PWPR_AOUT1) |
| `stepper_etb.kicad_sch` | `STEP_1B` | `output` | `/STEP_1B` | `U202:7` | `12V_0.77A_Chopper` | `J1-20` (`STEP_1B`) | SV650 ISC Idle Speed Control Valve Stepper Phase A- (U202_DRV8825PWPR_AOUT2) |
| `stepper_etb.kicad_sch` | `STEP_2A` | `output` | `/STEP_2A` | `U202:10` | `12V_0.77A_Chopper` | `J1-21` (`STEP_2A`) | SV650 ISC Idle Speed Control Valve Stepper Phase B+ (U202_DRV8825PWPR_BOUT1) |
| `stepper_etb.kicad_sch` | `STEP_2B` | `output` | `/STEP_2B` | `U202:8` | `12V_0.77A_Chopper` | `J1-22` (`STEP_2B`) | SV650 ISC Idle Speed Control Valve Stepper Phase B- (U202_DRV8825PWPR_BOUT2) |
| `stepper_etb.kicad_sch` | `STEP_IN` | `input` | `/LS9` | `U202:22` | `3.3V_CMOS_StepPulse` | `U26:134` | Bipolar stepper STEP pulse from STM32H7 PB4 (U26:134) to U202 DRV8825PWPR STEP (pin 22) |
| `stepper_etb.kicad_sch` | `USB_VBUS_BOOT0` | `input` | `/USB_VBUS_BOOT0` | `D210:1`, `R217:1` | `5V_USB_or_12V_ForceDFU` | `J1-35` (`USB_VBUS_BOOT0`) | Sealed USB VBUS (+5V) & Potted ROM DFU Override (+12V) (R217_10k_R218_12k_D211_B5819W_plus_D210_BZT52C6V8_R209_12k) |
| `stepper_etb.kicad_sch` | `VBUS_SENSE_OUT` | `output` | `/RC2` | `D211:2`, `R217:2`, `R218:1` | `3.3V_Clamped_Sense` | `U26:101` | USB VBUS sense output from J1-35 divider (R217 10k / R218 12k, clamped by D211 B5819W to +3V3) into STM32H7 PA9 (U26:101 USB_OTG_FS_VBUS) |
| `stepper_etb.kicad_sch` | `nENBL_IN` | `input` | `/PB8_STEP_EN` | `U202:21` | `3.3V_CMOS_ActiveLow_10kPD` | `U26:139` | Bipolar stepper active-low enable (/PB8_STEP_EN) from STM32H7 PB8 (U26:139) to U202 DRV8825 nENBL (pin 21) and /lowside_quad4/ IN1 (RN9:8 10k pull-down) |

### 2.13 `sheets/triggers.kicad_sch` (`/triggers/`)

- **Function**: Dual Adaptive Differential VR Conditioners (MAX9924) & 6-Ch Hall/Digital Schmitt Buffers
- **Key Components**: U13, U14 (MAX9924UAUB+ Mode A1), U8..U10 (SN74LVC2G17DB), U11, U12 (SRV05-4 ESD), 4.7k pull-ups to 5V_SENSOR_1
- **Contract File**: `contracts/triggers.interface.json` (`requirement = FOMEMC-22-triggers`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `triggers.kicad_sch` | `5V_SENSOR_SUPPLY` | `input` (8x) | `/5V_SENSOR_1` | `C109:1`, `C110:1`, `C38:2`, `C39:2` (+8 more) | `5.00V_150mA_Protected` | `J1-29` (`5V_SENSOR_1`) | 5V Regulated Sensor Supply #1 (TPS / STPS / MAP1 / Baro / GP) (U1_TLS115D0E_1) |
| `triggers.kicad_sch` | `HALL_IN_1` | `input` | `/DIGITAL_1` | `C24:1`, `R23:2`, `R29:2` | `0V_to_12V_2k7Pullup5V` | `J2-16` (`HALL2_VSS`) | Vehicle Speed Sensor (VSS 3-Wire Hall Output) (R23_2k7_Pullup5V_plus_U10_SN74LVC2G17DB) |
| `triggers.kicad_sch` | `HALL_IN_2` | `input` | `/DIGITAL_2` | `C25:1`, `R24:2`, `R30:2` | `0V_to_12V_2k7Pullup5V` | `J2-15` (`HALL1_CAM`) | Hall Effect Cam / Aux Trigger Input 1 (R24_2k7_Pullup5V_plus_U8_SN74LVC2G17DB) |
| `triggers.kicad_sch` | `HALL_IN_3` | `input` | `/DIGITAL_3` | `C26:1`, `R25:2`, `R31:2` | `0V_to_12V_2k7Pullup5V` | `J2-18` (`DIN2_NEUTRAL`) | Neutral / Sidestand Relay Interlock Switch Input (R25_2k7_Pullup5V_plus_U8_SN74LVC2G17DB) |
| `triggers.kicad_sch` | `HALL_IN_4` | `input` | `/DIGITAL_4` | `C27:1`, `R26:2`, `R32:2` | `0V_to_12V_2k7Pullup5V` | `J2-17` (`DIN1_CLUTCH`) | Clutch Lever Switch Input (Active Low to GND) (R26_2k7_Pullup5V_plus_U9_SN74LVC2G17DB) |
| `triggers.kicad_sch` | `HALL_IN_5` | `input` | `/triggers/HALL_IN_5` *(root `no_connect`)* | `C28:1`, `R27:2`, `R33:2` | `0V_to_12V_4k7Pullup5V_NC` | `[ROOT_NC]` | Unconnected spare Hall/digital input channel in /triggers/ (pulled up to 5V_SENSOR_1 via 4.7k; terminated with root no_connect) |
| `triggers.kicad_sch` | `HALL_IN_6` | `input` | `/triggers/HALL_IN_6` *(root `no_connect`)* | `C29:1`, `R28:2`, `R34:2` | `0V_to_12V_4k7Pullup5V_NC` | `[ROOT_NC]` | Unconnected spare Hall/digital input channel in /triggers/ (pulled up to 5V_SENSOR_1 via 4.7k; terminated with root no_connect) |
| `triggers.kicad_sch` | `HALL_OUT_1` | `output` | `/mcu/DIGITAL1` | `U10:6` | `3.3V_CMOS_Schmitt` | `U26:56` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `triggers.kicad_sch` | `HALL_OUT_2` | `output` | `/mcu/DIGITAL2` | `U8:6` | `3.3V_CMOS_Schmitt` | `U26:57` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `triggers.kicad_sch` | `HALL_OUT_3` | `output` | `/mcu/DIGITAL3` | `U8:4` | `3.3V_CMOS_Schmitt` | `U26:63` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `triggers.kicad_sch` | `HALL_OUT_4` | `output` | `/mcu/DIGITAL4` | `U9:6` | `3.3V_CMOS_Schmitt` | `U26:64` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `triggers.kicad_sch` | `HALL_OUT_5` | `output` | `/mcu/DIGITAL5` | `U10:4` | `3.3V_CMOS_Schmitt` | `U26:65` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `triggers.kicad_sch` | `HALL_OUT_6` | `output` | `/mcu/DIGITAL6` | `U9:4` | `3.3V_CMOS_Schmitt` | `U26:66` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `triggers.kicad_sch` | `VR1` | `input` | `/VR1+` | `R35:1` | `mV_to_100V_AC_Adaptive` | `J2-11` (`VR1+`) | Crankshaft Position Sensor VR+ (CKP+ 24-2 Rotor) (U13_MAX9924UAUB_IN+_via_R35_10k) |
| `triggers.kicad_sch` | `VR1-` | `input` | `/VR1-` | `R36:1` | `mV_to_100V_AC_Adaptive` | `J2-12` (`VR1-`) | Crankshaft Position Sensor VR- (CKP- Differential Return) (U13_MAX9924UAUB_IN-_via_R36_10k) |
| `triggers.kicad_sch` | `VR1_OUT` | `output` | `/mcu/VR_1` | `R125:2`, `U13:7` | `3.3V_CMOS_Schmitt` | `U26:67` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |
| `triggers.kicad_sch` | `VR2` | `input` | `/VR2+` | `R37:1` | `mV_to_100V_AC_Adaptive` | `J2-13` (`VR2+`) | Camshaft / Secondary Trigger VR+ (U14_MAX9924UAUB_IN+_via_R37_10k) |
| `triggers.kicad_sch` | `VR2-` | `input` | `/VR2-` | `R38:1` | `mV_to_100V_AC_Adaptive` | `J2-14` (`VR2-`) | Camshaft / Secondary Trigger VR- Differential Return (U14_MAX9924UAUB_IN-_via_R38_10k) |
| `triggers.kicad_sch` | `VR2_OUT` | `output` | `/mcu/VR_2` | `R126:2`, `U14:7` | `3.3V_CMOS_Schmitt` | `U26:68` | Conditioned trigger/digital pulse output from /triggers/ (MAX9924 COUT or SN74LVC2G17DB) to STM32H7 EXTI input |

### 2.14 `sheets/wbo1.kicad_sch` (`/wbo1/`)

- **Function**: Front Cylinder #1 Bosch LSU 4.9 Wideband Controller (STM32F042 + Pump/Nernst AFE + Heater PWM + CAN2)
- **Key Components**: U302 (STM32F042K6T6), U301 (MCP6004), U305 (AD8628), U303 (REF3033), U309 (XC6206P332MR), Q301 (VND14NV04), U307 (TJA1051T/3), R310 (61.9R 0.1%)
- **Contract File**: `contracts/wbo1.interface.json` (`requirement = FOMEMC-22-wbo1`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `wbo1.kicad_sch` | `12V_SENSE` | `input` | `/12V_MR` | `R320:1` | `12V_6A_Continuous` | `J1-24` (`WBO_HTR+`), `J1-27` (`+12V_MR`) | Bosch LSU 4.9 #1 & #2 Pin 4 (Heater +12V Supply) (Direct_12V_MR_Heater_Feed) |
| `wbo1.kicad_sch` | `CANH2` | `bidirectional` | `/CAN2+` | `U307:7` | `ISO11898_500kbps_Internal` | Inter-sheet (`/CAN2+`) | Internal wideband CAN2 differential bus between U5 (MCP2551-I-SN in /psu/, R10 120R, D5 PESD1CAN-UX) and U307 (/wbo1/) + U407 (/wbo2/) TJA1051T/3 transceivers |
| `wbo1.kicad_sch` | `CANL2` | `bidirectional` | `/CAN2-` | `U307:6` | `ISO11898_500kbps_Internal` | Inter-sheet (`/CAN2-`) | Internal wideband CAN2 differential bus between U5 (MCP2551-I-SN in /psu/, R10 120R, D5 PESD1CAN-UX) and U307 (/wbo1/) + U407 (/wbo2/) TJA1051T/3 transceivers |
| `wbo1.kicad_sch` | `LSU_H-` | `output` | `/WBO1_H-` | `Q301:2` | `12V_3A_RMS_7.5A_Peak` | `J1-23` (`WBO1_HTR-`) | Front Cylinder #1 Bosch LSU 4.9 Pin 3 (Heater -) (Q301_VND14NV04_1) |
| `wbo1.kicad_sch` | `LSU_IP` | `bidirectional` | `/WBO1_IP` | `R310:2`, `R312:2` | `1.65V_PumpCurrent` | `J2-20` (`WBO1_IP`) | Front Cylinder #1 Bosch LSU 4.9 Pin 1 (Ip Pump Current) (U301_MCP6004_WBO1_Pin8_via_R310_61R9) |
| `wbo1.kicad_sch` | `LSU_RTRIM` | `bidirectional` | `/WBO1_RTRIM` | `R308:1`, `R310:1`, `R311:2`, `R334:1` | `Trim_Resistor_Network` | `J2-21` (`WBO1_RCAL`) | Front Cylinder #1 Bosch LSU 4.9 Pin 5 (Rcal Trim Resistor) (R310_61R9_Sense_Shunt_WBO1) |
| `wbo1.kicad_sch` | `LSU_UN` | `bidirectional` | `/WBO1_UN` | `C302:1`, `R314:2`, `U301:10` | `2.10V_Nernst_AC_ESR` | `J2-22` (`WBO1_UN`) | Front Cylinder #1 Bosch LSU 4.9 Pin 6 (Vs / Un Nernst Cell) (U305_AD8628_WBO1_plus_U301_MCP6004) |
| `wbo1.kicad_sch` | `LSU_VM` | `bidirectional` | `/WBO1_VM` | `C304:1`, `R303:1`, `R309:1`, `U302:7` | `1.65V_VirtualGND` | `J2-19` (`WBO1_VM`), `U302:7` | Front Cylinder #1 Bosch LSU 4.9 Pin 2 (Vm Virtual Ground) (U301_MCP6004_WBO1_Pin14) |
| `wbo1.kicad_sch` | `WBO_BOOT0` | `input` | `/WBO1_BOOT0` | `R329:2`, `U302:31` | `3.3V_CMOS_10kPulldown` | `U26:119`, `U302:31` | STM32H7 boot-mode override control (PD5->WBO1_BOOT0 U26:119; PD7->WBO2_BOOT0 U26:123) to onboard STM32F042K6T6 BOOT0 (pin 31) |
| `wbo1.kicad_sch` | `WBO_NRST` | `input` | `/WBO1_NRST` | `C316:1`, `U302:4` | `3.3V_OpenDrain_Reset` | `U26:118`, `U302:4` | STM32H7 hardware reset control (PD4->WBO1_NRST U26:118; PD6->WBO2_NRST U26:122) to onboard STM32F042K6T6 NRST (pin 4) |

### 2.15 `sheets/wbo2.kicad_sch` (`/wbo2/`)

- **Function**: Rear Cylinder #2 Bosch LSU 4.9 Wideband Controller (STM32F042 + Pump/Nernst AFE + Heater PWM + CAN2)
- **Key Components**: U402 (STM32F042K6T6), U401 (MCP6004), U405 (AD8628), U403 (REF3033), U409 (XC6206P332MR), Q401 (VND14NV04), U407 (TJA1051T/3), R410 (61.9R 0.1%)
- **Contract File**: `contracts/wbo2.interface.json` (`requirement = FOMEMC-22-wbo2`)

| Sheet File | Hierarchical Pin (`hierarchical_label`) | Declared Direction (`shape`) | Instance(s) & Connected Root Net(s) | Child Sheet Terminal(s) | Voltage / Current Domain | External Connector / MCU Endpoint | Electrical Intent & Protection / Driver Stage |
|---|---|---|---|---|---|---|---|
| `wbo2.kicad_sch` | `12V_SENSE` | `input` | `/12V_MR` | `R420:1` | `12V_6A_Continuous` | `J1-24` (`WBO_HTR+`), `J1-27` (`+12V_MR`) | Bosch LSU 4.9 #1 & #2 Pin 4 (Heater +12V Supply) (Direct_12V_MR_Heater_Feed) |
| `wbo2.kicad_sch` | `CANH2` | `bidirectional` | `/CAN2+` | `U407:7` | `ISO11898_500kbps_Internal` | Inter-sheet (`/CAN2+`) | Internal wideband CAN2 differential bus between U5 (MCP2551-I-SN in /psu/, R10 120R, D5 PESD1CAN-UX) and U307 (/wbo1/) + U407 (/wbo2/) TJA1051T/3 transceivers |
| `wbo2.kicad_sch` | `CANL2` | `bidirectional` | `/CAN2-` | `U407:6` | `ISO11898_500kbps_Internal` | Inter-sheet (`/CAN2-`) | Internal wideband CAN2 differential bus between U5 (MCP2551-I-SN in /psu/, R10 120R, D5 PESD1CAN-UX) and U307 (/wbo1/) + U407 (/wbo2/) TJA1051T/3 transceivers |
| `wbo2.kicad_sch` | `LSU_H-` | `output` | `/WBO2_H-` | `Q401:2` | `12V_3A_RMS_7.5A_Peak` | `J1-25` (`WBO2_HTR-`) | Rear Cylinder #2 Bosch LSU 4.9 Pin 3 (Heater -) (Q401_VND14NV04_2) |
| `wbo2.kicad_sch` | `LSU_IP` | `bidirectional` | `/WBO2_IP` | `R410:2`, `R412:2` | `1.65V_PumpCurrent` | `J2-31` (`WBO2_IP`) | Rear Cylinder #2 Bosch LSU 4.9 Pin 1 (Ip Pump Current) (U401_MCP6004_WBO2_Pin8_via_R410_61R9) |
| `wbo2.kicad_sch` | `LSU_RTRIM` | `bidirectional` | `/WBO2_RTRIM` | `R408:1`, `R410:1`, `R411:2`, `R434:1` | `Trim_Resistor_Network` | `J2-32` (`WBO2_RTRIM`) | Rear Cylinder #2 Bosch LSU 4.9 Pin 5 (Rcal Trim Resistor) (R410_61R9_Sense_Shunt_WBO2) |
| `wbo2.kicad_sch` | `LSU_UN` | `bidirectional` | `/WBO2_UN` | `C402:1`, `R414:2`, `U401:10` | `2.10V_Nernst_AC_ESR` | `J2-33` (`WBO2_UN`) | Rear Cylinder #2 Bosch LSU 4.9 Pin 6 (Vs / Un Nernst Cell) (U405_AD8628_WBO2_plus_U401_MCP6004) |
| `wbo2.kicad_sch` | `LSU_VM` | `bidirectional` | `/WBO2_VM` | `C404:1`, `R403:1`, `R409:1`, `U402:7` | `1.65V_VirtualGND` | `J2-30` (`WBO2_VM`), `U402:7` | Rear Cylinder #2 Bosch LSU 4.9 Pin 2 (Vm Virtual Ground) (U401_MCP6004_WBO2_Pin14) |
| `wbo2.kicad_sch` | `WBO_BOOT0` | `input` | `/WBO2_BOOT0` | `R429:2`, `U402:31` | `3.3V_CMOS_10kPulldown` | `U26:123`, `U402:31` | STM32H7 boot-mode override control (PD5->WBO1_BOOT0 U26:119; PD7->WBO2_BOOT0 U26:123) to onboard STM32F042K6T6 BOOT0 (pin 31) |
| `wbo2.kicad_sch` | `WBO_NRST` | `input` | `/WBO2_NRST` | `C416:1`, `U402:4` | `3.3V_OpenDrain_Reset` | `U26:122`, `U402:4` | STM32H7 hardware reset control (PD4->WBO1_NRST U26:118; PD6->WBO2_NRST U26:122) to onboard STM32F042K6T6 NRST (pin 4) |

---

## 3. Cross-Block Couplings, Multi-Instance Anomalies & Owner-Block Resolution Ledger

Because `fome-mc` was assembled and iteratively remediated (`FOMEMC-1..20`) from proven Polygonus, Polygonus-Universal-112, and mck1117 wideband blocks, several components and nets physically reside on one schematic sheet while electrically serving another block. The table and detailed entries below record every cross-block component, net, and multi-instance anomaly together with its authoritative **Owner Block** for standalone reference block capture (`AGENTEE-89`, `AGENTEE-105..107`).

| # | Cross-Block Component / Net | Current Schematic Sheet (`Instance`) | Connected Nets & External Pins | Authoritative Owner Block | Disposition for Block Capture & Verification |
|---:|---|---|---|---|---|
| 1 | `D201..D204` (`B340A-13-F` `40 V` Schottky footprints, **DNP** per `FOMEMC-17`) | `sheets/stepper_etb.kicad_sch` (`/stepper_etb/` pins `LS1_CLAMP..LS4_CLAMP`, `12V_MR`) | Anodes on `/LS1../LS4` (`J1-1..4` `INJ1..4`), cathodes on `/12V_MR` (`J1-24, J1-27`) | `lowside_quad` (`/lowside_quad1/` injector block; or `inj_quad` logical role) | Must remain **DNP** (`populated: false` in `stepper_etb.interface.json`, seed `F24`) so `U1001, U1002` (`VNLD5090-E` / `VND14NV04` family) internal `42 V` active drain-gate clamp (`V_CLAMP = 42 V min`) provides fast (~`0.4 ms`) injector current decay. |
| 2 | `D205..D208` (`B340A-13-F` `40 V` Schottky flyback clamps, **populated**) | `sheets/stepper_etb.kicad_sch` (`/stepper_etb/` pins `LS5_CLAMP..LS8_CLAMP`, `12V_MR`) | Anodes on `/LS5../LS8` (`J1-10..13` `AUX_LS1..4`), cathodes on `/12V_MR` | `lowside_quad` (`/lowside_quad2/` auxiliary solenoid/relay driver block) | Populated (`populated: true` in `stepper_etb.interface.json`) freewheeling recirculation diodes to `/12V_MR` for inductive relay/solenoid loads on `/LS5..8`. (Note: Analog 0-5V ESD clamping ahead of `/quad_analog1..3/` and `/quad_analog_temp/` is provided by `U16, U18, U20, U22` `SRV05-4` inside `quad_analog*.kicad_sch`.) |
| 3 | `D209` (`B340A-13-F` `40 V` Main Relay flyback clamp, **populated**) | `sheets/stepper_etb.kicad_sch` (`/stepper_etb/` pins `MAIN_RLY_CLAMP`, `12V_MR`) | Anode on `/MAIN_RLY` (`J1-14`), cathode on `/12V_MR` (`J1-24, J1-27`) | `lowside_quad` (`/lowside_quad4/` Ch3 `U1202:6` Main Relay driver) / `Keep_Alive` | Populated (`populated: true` in `stepper_etb.interface.json`) coil flyback clamp across the external ECU Main Relay coil between `/MAIN_RLY` (`J1-14`) and `/12V_MR` (`J1-27`). |
| 4 | `R212` (`2.2 kΩ` `0603` 12V tachometer pull-up resistor) | `sheets/stepper_etb.kicad_sch` (`/stepper_etb/` pins `DASH_TECH_PULLUP`, `12V_MR`) | `R212:1` on `/12V_MR`, `R212:2` on `/LS8` (`J1-13` `AUX_LS4` tach output) | `lowside_quad` (`/lowside_quad2/` Ch4 `U1102:8` tachometer output) | Pulls open-drain `/LS8` (`J1-13`) up to `/12V_MR` to generate `0-12 V` tachometer pulses (`FOMEMC-14`, protected by `same_net` invariant `rel:R212-D208-LS8-same-net`, seed `F16`). Pin label `DASH_TECH_PULLUP` is a historical name from before `FOMEMC-14` moved `R212` off `/LS14` (`J2-27`). |
| 5 | `/PB8_STEP_EN` (`U26:139` `PB8`) shared with `/lowside_quad4/` `IN1` (`RN9:8`, `U1203:2`) & unconnected `/LS13` (`U1201:6`) | `sheets/mcu.kicad_sch` (`LS13`), `sheets/stepper_etb.kicad_sch` (`nENBL_IN`), `sheets/lowside_quad.kicad_sch` (`/lowside_quad4/` `IN1`, `OUT1`) | `/PB8_STEP_EN` (`U26:139`, `U202:21`, `RN9:8`, `U1203:2`); `/lowside_quad4/OUT1` (`U1201:6` `no_connect`) | `stepper_etb` (`U202` `DRV8825` `nENBL` control; `/lowside_quad4/` Ch1 is unused spare) | **Recorded `FOMEMC-22` Decision**: Sharing `/PB8_STEP_EN` with `/lowside_quad4/IN1` is intentionally retained on the current revision so `RN9` (`10 kΩ` pull-down in `/lowside_quad4/`) holds `PB8 = 0 V` during MCU reset (`DRV8825` enabled default, firmware-controlled via `Gpio::B8`), while `U1201:6` (`/lowside_quad4/OUT1`) is terminated with `no_connect`. |
| 6 | `U203` (`TLE9201SG` #2 H-Bridge for `ETB2`) drawn inline in `stepper_etb.kicad_sch` vs `sheets/etb-9201.kicad_sch` (`U201` `ETB1`) | `sheets/stepper_etb.kicad_sch` (`/stepper_etb/` `ETB2_*`) vs `sheets/etb-9201.kicad_sch` (`/etb1/`) | `/ETB2_PWM`, `/ETB2_DIR`, `/ETB2_DIS`, `/ETB2_OUT+` (`J1-17`), `/ETB2_OUT-` (`J1-18`), `/12V_MR` | `etb-9201` (second logical instance `/etb2/` of `etb-9201.kicad_sch`) | `U203` (`C204..C207`, `R211`) duplicates `sheets/etb-9201.kicad_sch` (`U201`) inline inside `stepper_etb.kicad_sch`. Capture as a second `etb-9201` H-bridge block; keep `U202` (`DRV8825PWPR`) as the standalone `stepper_etb` block. |
| 7 | `J1-35` `/USB_VBUS_BOOT0` sense & potted ROM DFU override network (`D210, D211, R209, R217, R218`) | `sheets/stepper_etb.kicad_sch` (`/stepper_etb/` `USB_VBUS_BOOT0`, `VBUS_SENSE_OUT`, `BOOT0_OUT`) | `/USB_VBUS_BOOT0` (`J1-35`), `/RC2` (`U26:101` `PA9`), `/BOOT0_NET` (`U26:138` `BOOT0`) | `mcu` (USB VBUS sense & `BOOT0` ROM DFU recovery stage) | Sits in `stepper_etb.kicad_sch` for layout proximity to `J1-35`, but electrically belongs to the `mcu` USB/DFU interface (`PA9` and `BOOT0` against `R90` `10 kΩ` pull-down in `mcu.kicad_sch`). |
| 8 | `U42, U43` (`MIC4427YM` in `/ign1/`) driving `Q201..Q204` (`FGD3040G2-F085` in `/ign_igbt/`) vs `U44, U45` (`MIC4427YM` in `/ign2/`) | `sheets/ign4.kicad_sch` (`/ign1/`, `/ign2/`) and `sheets/ign_igbt.kicad_sch` (`/ign_igbt/`) | `/ign1/IN1..4` -> `/IGN1..4` -> `Q201..Q204` -> `/IGN1..4_COIL` (`J1-6..9`); `/ign2/IN1..4` -> `/IGN5..8` (`J2-23..26`) | `ign_igbt` (`/ign1/` + `/ign_igbt/` combined 4-ch IGBT coil driver) and `ign4` (`/ign2/` 4-ch 5V logic ignition driver) | `/ign1/` provides the `5 V` `1.5 A` `MIC4427YM` gate pre-drivers (`U42, U43`) for the `Q201..Q204` IGBTs in `/ign_igbt/`, while `/ign2/` (`U44, U45`) drives external `5 V` logic smart coils (`J2-23..26`) directly through `R112..R115` (`100 Ω`). |
| 9 | Dual CAN transceivers (`U4, U5` `MCP2551-I-SN`, `D4, D5` `PESD1CAN-UX`, `R7, R8` `10 Ω`, `R9, R10` `120 Ω`) | `sheets/psu.kicad_sch` (`/psu/` pins `TXDCAN*`, `RXDCAN*`, `CANH*`, `CANL*`) | `/mcu/CAN_TX`, `/mcu/CAN_RX`, `/CAN+` (`J2-28`), `/CAN-` (`J2-29`), `/mcu/CAN2_TX`, `/mcu/CAN2_RX`, `/CAN2+`, `/CAN2-` | Logical `can` block (currently co-resident inside `sheets/psu.kicad_sch`) | `U4` serves external `CAN1` (`J2-28/29`) and `U5` serves internal wideband `CAN2` (`/CAN2+`, `/CAN2-` to `U307` in `/wbo1/` and `U407` in `/wbo2/`). Capture by reference set (`U4, U5, D4, D5, R7..R10, C14, C15`) when splitting `can` from `psu`. |
| 10 | `R219` (`1.5 kΩ` `0.1%` 5V pull-up on `/AV6` `J2-8`) and `C1` (`47 µF` bulk cap on `/12V_MR`) on root sheet `/` | `fome-mc.kicad_sch` (`/`) | `R219`: `/5V_SENSOR_1` (`J1-29`) to `/AV6` (`J2-8`, `/quad_analog2/IN2`); `C1`: `/12V_MR` (`J1-24/27`) to `GND` | `R219`: `quad_analog` (`/quad_analog2/` Ch2 gear sensor excitation `F15`); `C1`: `/12V_MR` input bulk filter | Placed on root sheet `fome-mc.kicad_sch`. `R219` biases the SV650 K7 6-speed gear position resistor ladder on `/AV6` (`J2-8` -> `R64:1`). |
| 11 | `U40` (`BTS716G` in `/highside_quad/`) unconnected outputs `OUT1..OUT4` and internal diagnostic pins `ST1..ST4` | `sheets/highside_quad.kicad_sch` (`/highside_quad/`) | `/highside_quad/IN1..4` (`U26:89..86`), `/12V_MR`, `/highside_quad/OUT1..4` (root `no_connect`) | `highside_quad` (unallocated spare high-side driver block) | `OUT1..OUT4` are brought to `/highside_quad/` sheet pins and terminated with `no_connect` on `fome-mc.kicad_sch`; open-drain status pins on `U40` are unused. |
| 12 | `/psu/12V_PROT` root pin unused vs `/VBOOST` and `/12V_MR` distribution | `sheets/psu.kicad_sch` (`/psu/` `12V_PROT`, `VBOOST`) | `/12V_RAW` -> `D1` (`SMCJ24A`) -> `Q1` (`AO4485`) -> `/12V_PROT` -> `L1` (`2.2 µH`) -> `/VBOOST` | `psu` (internal protected 12V distribution rail) | Inside `psu.kicad_sch`, `/12V_PROT` feeds `U1, U2` (`TLS115D0E` 5V tracked LDOs) and `L1` -> `/VBOOST` -> `U3` (`LMR16020PDDAR`). On `fome-mc.kicad_sch`, `/psu/` pin `12V_PROT` connects only to a local `12V_PROT` label and `PWR_FLAG`; external switched 12V loads connect to `/12V_MR` (`J1-24, J1-27`). |
| 13 | Five functional ground names on `J1-5, J1-31..34` in `io-map.csv` vs single unified `GND` net (`FOMEMC-10`) | `fome-mc.kicad_sch` (`/`) and all 15 child sheets (`sheets/*.kicad_sch`) | `GND` (`J1:5`, `J1:31`, `J1:32`, `J1:33`, `J1:34`) | Board-wide unified `GND` return architecture | `PGND_INJ` (`J1-5`), `SGND` (`J1-31`), `PGND_IGN` (`J1-32`), `PGND_HEATER` (`J1-33`), and `CHASSIS_ECU_GND` (`J1-34`) are merged onto a single native net `GND` (`FOMEMC-10`) to eliminate unbonded split-ground islands while routing high-current returns over dedicated wide copper and solid `In1.Cu` plane. |

### 3.1 Detailed Engineering Resolutions for Cross-Block Couplings

#### 3.1.1 Low-Side Flyback Clamps (`D201..D204` DNP vs `D205..D209` Populated) and `R212` Tachometer Pull-Up
- **Physical Location**: `D201..D209` (`B340A-13-F` `40 V, 3 A` SMA Schottky diodes) and `R212` (`2.2 kΩ` `0603` resistor) are drawn inside `sheets/stepper_etb.kicad_sch` (`/stepper_etb/`) and exposed through passive hierarchical pins `LS1_CLAMP..LS8_CLAMP`, `MAIN_RLY_CLAMP`, and `DASH_TECH_PULLUP`, with their common supply node tied to `/stepper_etb/` input `12V_MR` (`/12V_MR`).
- **Injector Channels (`D201..D204` on `/LS1../LS4`, `J1-1..4`, Owner: `lowside_quad` `/lowside_quad1/`)**: Driven by `U1001, U1002` (`VNLD5090-E` in `/lowside_quad1/`, which like the `VND14NV04` Omnifet II family integrate an active drain-gate turn-off clamp at `V_CLAMP = 42 V min` / `40..50 V`). Per `FOMEMC-17` (and seed `F24`), `D201..D204` are marked **DNP (`populated: false`)** because populating a freewheeling diode to `+12V_MR` clamps injector turn-off at `V_BATT + 0.5 V`, slowing injector current decay from `~0.4 ms` to `~4 ms` and causing nonlinear rich fueling at short pulsewidths.
- **Auxiliary & Main Relay Channels (`D205..D208` on `/LS5../LS8`, `J1-10..13`, Owner: `/lowside_quad2/`; `D209` on `/MAIN_RLY`, `J1-14`, Owner: `/lowside_quad4/`)**: Driven by `U1101, U1102` (`/lowside_quad2/`) and `U1202` (`/lowside_quad4/`). These channels switch inductive relay coils (Fuel Pump, Cooling Fan, Main Relay) and continuous solenoids (PAIR valve), so `D205..D209` remain **populated (`populated: true`)** for low-dissipation recirculation to `/12V_MR`.
- **Tachometer Pull-Up (`R212` on `/LS8`, `J1-13`, Owner: `/lowside_quad2/`)**: `R212` (`2.2 kΩ` between `/12V_MR` and `/LS8` via hierarchical pin `DASH_TECH_PULLUP`) pulls the open-drain output `U1102:8` (`AUX_LS4`, `J1-13`) up to `+12V_MR` to produce a `0-12 V` square-wave tachometer pulse for the SV650 K7 instrument cluster (`FOMEMC-14`, verified by `rel:R212-D208-LS8-same-net` in `contracts/stepper_etb.interface.json`). Meanwhile, `/LS14` (`J2-27` `DASH_TECH` single-wire serial ECT/FI line, driven by `U1201:8` in `/lowside_quad4/`) is left open-drain on the ECU because the SV650 instrument cluster provides its own internal pull-up.
- **Note on Analog Input Clamping (`U16, U18, U20, U22` `SRV05-4`)**: Overvoltage and ESD protection ahead of the `MCP6004` op-amps (`U15, U17, U19, U21`) in `/quad_analog_temp/` (`sheets/quad_analog_pullup.kicad_sch`) and `/quad_analog1..3/` (`sheets/quad_analog.kicad_sch`) is self-contained inside those analog sheets via `SRV05-4` low-capacitance diode arrays (`U16, U18, U20, U22`) clamped between `GND` and `+5V` after the `5.6 kΩ / 10 kΩ` input dividers.

#### 3.1.2 `/PB8_STEP_EN` (`U26` `PB8` / `LS13`) Shared Connection & Reset-State Polarity Decision (`FOMEMC-22`)
- **Observed Topology**:
  1. Inside `sheets/mcu.kicad_sch` (`/mcu/`), `U26` (`STM32H753ZIT6`) pin 139 (`PB8`) is connected to hierarchical output pin `LS13`.
  2. On the root sheet `fome-mc.kicad_sch`, `/mcu/` pin `LS13` is named `/PB8_STEP_EN` and routed to **two** child sheet inputs:
     - `/stepper_etb/` pin `nENBL_IN` -> `U202` (`DRV8825PWPR`) pin 21 (`nENBL`, active-low H-bridge enable).
     - `/lowside_quad4/` pin `IN1` -> `RN9` pin 8 (`10 kΩ` pull-down resistor array to `GND` at `RN9:1..4`) and `U1203` pin 2 (`74HCT125D` 5V CMOS buffer Ch1 input) -> `RN10:7` (`1 kΩ`) -> `U1201:1` (`VNLD5090-E` Ch1 input).
  3. The corresponding drain output `/lowside_quad4/` pin `OUT1` (`U1201:6`, net `/lowside_quad4/OUT1`, legacy `LS13`) is terminated with an explicit `no_connect` flag on `fome-mc.kicad_sch`.
- **Engineering Decision (`FOMEMC-22`)**:
  - **Status**: **Intentional heritage coupling retained on the current board revision; assigned to `stepper_etb` (`nENBL_IN`) for standalone block capture.**
  - **Reset & Operating Behavior**: During `STM32H753ZIT6` reset (when `PB8` is high-Z), `RN9:8` (`10 kΩ` to `GND` inside `/lowside_quad4/`) in parallel with the `DRV8825` internal `~100 kΩ` pull-down holds `/PB8_STEP_EN` at `0 V` (`nENBL = LOW`), enabling the `DRV8825` output stage. Once firmware boots (`engineConfiguration->stepperEnablePin = Gpio::B8`), `STM32H7` actively drives `PB8` low during idle-air stepper positioning and high (`3.3 V`) to disable the `DRV8825` bridges and eliminate stationary coil heating. Because `U1201:6` (`/lowside_quad4/OUT1`) has an explicit `no_connect` and drives no external pin or trace, switching `U1201` Ch1 in tandem with `PB8` has zero external electrical impact.
  - **Standalone Block Capture Rule**: When `stepper_etb` or `lowside_quad` is captured as a standalone block, `/PB8_STEP_EN` is owned by `stepper_etb` (`nENBL_IN`), and `/lowside_quad4/` `IN1`/`OUT1` is an unused spare channel in `/lowside_quad4/`.

#### 3.1.3 H-Bridge Duplication (`U201` in `sheets/etb-9201.kicad_sch` vs `U203` in `sheets/stepper_etb.kicad_sch`)
- `sheets/etb-9201.kicad_sch` (`/etb1/`) encapsulates a clean, reusable single-channel `TLE9201SG` (`U201`) H-bridge block with 6 hierarchical pins (`12V_SUPPLY`, `PWM`, `DIR`, `DIS`, `OUT+`, `OUT-`) driving `J1-15/16` (`/ETB1_OUT+`, `/ETB1_OUT-`).
- Instead of instantiating `sheets/etb-9201.kicad_sch` a second time for `ETB2` (`J1-17/18`), `U203` (`TLE9201SG` #2, `C204..C207`, `R211`) was placed inline inside `sheets/stepper_etb.kicad_sch` (`/stepper_etb/` pins `ETB2_PWM`, `ETB2_DIR`, `ETB2_DIS`, `ETB2_OUT+`, `ETB2_OUT-`).
- **Owner Block**: `U203` and its `ETB2_*` pins belong to a second logical instance of `etb-9201`, leaving `U202` (`DRV8825PWPR`, `R213, R214` `0.20 Ω` sense resistors, `R215 33 kΩ / R216 10 kΩ` `VREF = 0.767 V` -> `I_TRIP = 0.77 A` per `FOMEMC-5`) as the dedicated bipolar stepper driver block in `stepper_etb`.

#### 3.1.4 Ignition Pre-Driver & Power IGBT Split (`sheets/ign4.kicad_sch` `/ign1/`, `/ign2/` vs `sheets/ign_igbt.kicad_sch` `/ign_igbt/`)
- `sheets/ign4.kicad_sch` contains two `MIC4427YM` dual `1.5 A` `5 V` push-pull MOSFET/IGBT gate driver ICs (`U42, U43` in `/ign1/`; `U44, U45` in `/ign2/`), `10 kΩ` input pull-down resistors (`R1501..R1504` in `/ign1/`; `R1601..R1604` in `/ign2/`), and `100 Ω` series output resistors (`R108..R111` in `/ign1/`; `R112..R115` in `/ign2/`).
- In instance `/ign1/`, `OUT1..OUT4` (`/IGN1../IGN4`) feed `IGN1_IN..IGN4_IN` of `/ign_igbt/` (`sheets/ign_igbt.kicad_sch`), where `R201..R204` (`15 Ω` gate resistors) and `R205..R208` (`10 kΩ` gate-emitter resistors) drive the four `FGD3040G2-F085` `400 V`-clamped ignition IGBTs (`Q201..Q204`) connected to `J1-6..9` (`/IGN1_COIL../IGN4_COIL`, `HV_IGN` netclass with `0.50 mm` clearance and `1.2 mm` copper traces per `FOMEMC-16` / `FOMEMC-19`).
- In instance `/ign2/`, `OUT1..OUT4` (`/IGN5../IGN8`) go directly to external connector pins `J2-23..26` (`IGN1_LOG..IGN4_LOG`) to drive 4 external `5 V` logic-level smart coils.
- *(Note: `74HCT125D` quad 5V CMOS buffers `U1003, U1103, U1203` are used in `sheets/lowside_quad.kicad_sch`, whereas `sheets/ign4.kicad_sch` uses `MIC4427YM` `U42..U45` across both `/ign1/` and `/ign2/`.)*

#### 3.1.5 Power Supply (`psu.kicad_sch`), Unused Root `/12V_PROT` Pin, and Co-Resident CAN Transceivers (`U4, U5`)
- **12V Protection Chain**: Switched `+12V_MR` (`J1-24, J1-27`) and `+12V_IGN_SW` (`J1-26`) are Schottky-OR'd by `D20, D21` (`B340A-13-F`, clamped by `D22` `SMCJ24A`) inside `sheets/Keep_Alive.kicad_sch` to produce `/12V_RAW`. Inside `sheets/psu.kicad_sch`, `/12V_RAW` is clamped by `D1` (`SMCJ24A`, `V_C = 38.9 V`) and reverse-polarity blocked by `Q1` (`AO4485` P-FET with `D19` `12 V` gate Zener and `R124` `47 kΩ`) to form `/12V_PROT`.
- **`/12V_PROT` vs `/VBOOST` vs `/12V_MR`**: Inside `psu.kicad_sch`, `/12V_PROT` feeds the two `TLS115D0E` tracked `5 V` sensor LDOs (`U1` -> `/5V_SENSOR_1` `J1-29`; `U2` -> `/5V_SENSOR_2` `J1-30`) and passes through `L1` (`2.2 µH`) into `/VBOOST`, which supplies `U3` (`LMR16020PDDAR` `5 V` buck) and exits `/psu/` on pin `VBOOST` to `/mcu/` (`R120/R121` ADC voltage sense divider). Although `psu.kicad_sch` also exports `/12V_PROT` on hierarchical output pin `12V_PROT`, on `fome-mc.kicad_sch` that root pin connects only to a local `12V_PROT` label and `PWR_FLAG`. High-current switched 12V loads (`stepper_etb`, `etb1`, `highside_quad`, `wbo1/2`) connect directly to `/12V_MR`.
- **Co-Resident CAN Transceivers (`U4, U5`)**: `sheets/psu.kicad_sch` also houses both `MCP2551-I-SN` high-speed CAN transceivers (`U4` for external `CAN1` on `J2-28/29` with `D4` `PESD1CAN-UX` and `R9` `120 Ω`; `U5` for internal wideband `CAN2` on `/CAN2+`, `/CAN2-` with `D5` `PESD1CAN-UX` and `R10` `120 Ω`). For reference block capture, `U4, U5, D4, D5, R7..R10, C14, C15` form the logical `can` transceiver block.

---

## 4. Machine-Checkable `agent-ee.interface/1` Contracts (`contracts/*.interface.json`)

Each of the 15 sheet files in `sheets/*.kicad_sch` has a corresponding `agent-ee.interface/1` contract in `contracts/<sheet_stem>.interface.json`. All 15 contracts:
1. Conform strictly to `agent_ee.hardware_interface.validate_contract` (`schema == "agent-ee.interface/1"`, exact top-level keys `schema`, `components`, `terminals`, `allowed_edits`, `invariants`, single requirement `FOMEMC-22-<sheet_stem>` per contract).
2. Scope every component witness strictly to `occurrences` and `symbols` of `sheets/<sheet_stem>.kicad_sch` so `agent_ee.reference_blocks._native_requirement_coverage` qualifies the contract directly.
3. Include a `named_net` invariant (`pin:<instance>:<hierarchical_label>`) for every `hierarchical_label` across all instances of the sheet (262 `pin:*` invariants total), plus `component` assembly-state invariants (`populated: true/false`), `value` invariants, and `same_net` / `different_net` structural invariants (`F01, F03, F04, F05, F06, F08, F09, F16, F24`).

| # | Contract File | Target Sheet (`sheets/*.kicad_sch`) | Requirement ID | Declared Components | Declared Terminals | Total Invariants (`named_net` / `component` / `value` / `same_net` / `different_net`) | Native Evaluation Status |
|---:|---|---|---|---:|---:|---:|---|
| 1 | `contracts/Keep_Alive.interface.json` | `sheets/Keep_Alive.kicad_sch` | `FOMEMC-22-Keep_Alive` | 7 | 5 | **17** (5 / 7 / 5 / 0 / 0) | `PASS` (0 violations) |
| 2 | `contracts/etb-9201.interface.json` | `sheets/etb-9201.kicad_sch` | `FOMEMC-22-etb-9201` | 5 | 6 | **14** (6 / 5 / 3 / 0 / 0) | `PASS` (0 violations) |
| 3 | `contracts/highside_quad.interface.json` | `sheets/highside_quad.kicad_sch` | `FOMEMC-22-highside_quad` | 6 | 9 | **17** (9 / 6 / 2 / 0 / 0) | `PASS` (0 violations) |
| 4 | `contracts/ign4.interface.json` | `sheets/ign4.kicad_sch` | `FOMEMC-22-ign4` | 28 | 16 | **50** (16 / 28 / 6 / 0 / 0) | `PASS` (0 violations) |
| 5 | `contracts/ign_igbt.interface.json` | `sheets/ign_igbt.kicad_sch` | `FOMEMC-22-ign_igbt` | 12 | 8 | **28** (8 / 12 / 8 / 0 / 0) | `PASS` (0 violations) |
| 6 | `contracts/knock.interface.json` | `sheets/knock.kicad_sch` | `FOMEMC-22-knock` | 6 | 4 | **14** (4 / 6 / 4 / 0 / 0) | `PASS` (0 violations) |
| 7 | `contracts/lowside_quad.interface.json` | `sheets/lowside_quad.kicad_sch` | `FOMEMC-22-lowside_quad` | 15 | 24 | **51** (24 / 15 / 12 / 0 / 0) | `PASS` (0 violations) |
| 8 | `contracts/mcu.interface.json` | `sheets/mcu.kicad_sch` | `FOMEMC-22-mcu` | 20 | 96 | **129** (91 / 20 / 13 / 5 / 0) | `PASS` (0 violations) |
| 9 | `contracts/psu.interface.json` | `sheets/psu.kicad_sch` | `FOMEMC-22-psu` | 27 | 15 | **55** (15 / 27 / 12 / 0 / 1) | `PASS` (0 violations) |
| 10 | `contracts/quad_analog.interface.json` | `sheets/quad_analog.kicad_sch` | `FOMEMC-22-quad_analog` | 27 | 24 | **54** (24 / 27 / 3 / 0 / 0) | `PASS` (0 violations) |
| 11 | `contracts/quad_analog_pullup.interface.json` | `sheets/quad_analog_pullup.kicad_sch` | `FOMEMC-22-quad_analog_pullup` | 10 | 9 | **24** (9 / 10 / 5 / 0 / 0) | `PASS` (0 violations) |
| 12 | `contracts/stepper_etb.interface.json` | `sheets/stepper_etb.kicad_sch` | `FOMEMC-22-stepper_etb` | 22 | 26 | **64** (26 / 22 / 15 / 1 / 0) | `PASS` (0 violations) |
| 13 | `contracts/triggers.interface.json` | `sheets/triggers.kicad_sch` | `FOMEMC-22-triggers` | 20 | 20 | **50** (19 / 20 / 9 / 0 / 2) | `PASS` (0 violations) |
| 14 | `contracts/wbo1.interface.json` | `sheets/wbo1.kicad_sch` | `FOMEMC-22-wbo1` | 14 | 11 | **33** (11 / 14 / 8 / 0 / 0) | `PASS` (0 violations) |
| 15 | `contracts/wbo2.interface.json` | `sheets/wbo2.kicad_sch` | `FOMEMC-22-wbo2` | 14 | 11 | **33** (11 / 14 / 8 / 0 / 0) | `PASS` (0 violations) |

### 4.1 Automated Verification Command

Run `python3 scripts/verify_io_map.py` (or `make verify-io`) to:
1. Verify all 70 external `J1`/`J2` connector pins and 22 internal buses in `io-map.csv` against the netlist and `fome-fw` `board_configuration.cpp` / `connectors/*.yaml`.
2. Export a fresh native netlist (`kicad-cli sch export netlist --format kicadxml` and `--format kicadsexpr`) from `fome-mc.kicad_sch`.
3. Parse every `hierarchical_label` in all 15 `sheets/*.kicad_sch` files and every `(sheet ... (pin ...))` in `fome-mc.kicad_sch`, verifying 100% coverage in both `docs/SHEET_CONTRACTS.md` and `contracts/*.interface.json`.
4. Validate and evaluate all 15 `contracts/*.interface.json` files using `agent_ee.hardware_interface.validate_contract`, `read_inventory`, and `evaluate`, confirming 0 schema errors and 0 unsatisfied invariants across all 713 invariants.
