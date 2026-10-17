# `fome-mc` — Integrated FOME Motorcycle ECU

`fome-mc` is a 4-layer, `162.0 mm × 115.0 mm` single-PCB motorcycle ECU running [FOME](https://github.com/halbritt/fome-fw/tree/fome-mc/firmware/config/boards/fome-mc) (`firmware/config/boards/fome-mc`). The first vehicle application is the **2007 Suzuki SV650 (K7, dual-plug 90° V-twin)**.

---

## 1. Hardware Specifications & Status

| Subsystem | Implementation |
| :--- | :--- |
| **Main MCU** | `U26`: `STM32H753ZIT6` / `STM32H743ZIT6` (LQFP-144, 480 MHz, 2 MB Flash, 1 MB RAM) |
| **Wideband Controllers** | `U302`, `U402`: 2× onboard `STM32F042K6T6` + `MCP6004` + `AD8628` + `REF3033` + `VND14NV04` (`wideband_controller` Rev C) for two Bosch LSU 4.9 sensors on internal 500 kbps `CAN2` (`PB12/PB13`) |
| **Harness Connectors** | Dual 35-pin TE Connectivity AMPSEAL right-angle headers (70 pins total):<br>• `J1`: `776163-1` (Key 1 Black, mates with `776164-1`) — Power, Grounds, Injectors, IGBTs, Steppers, LSU Heaters<br>• `J2`: `776163-2` (Key 2 Grey, mates with `776164-2`) — Analog/VR/Hall Sensors, LSU Cells, Logic Coils, `CAN1`, `USB` |
| **Ignition Outputs** | • 4× High-Current IGBTs (`IGBT1..4` on `J1-6..9`): `FGD3040G2-F085C` (400 V, 30 A) driven by `MIC4427` (`PB3, PG15, PG14, PG13`)<br>• 4× 5 V Logic Outputs (`IGN1_LOG..4_LOG` on `J2-23..26`): `MIC4427` + 100 Ω series (`PG12, PG11, PG10, PG9`) |
| **Low-Side & High-Side** | • 4× Injector Low-Side (`INJ1..4` on `J1-1..4`): `VNLD5090TR-E` + `SK310A` clamp (`PG5..PG8`)<br>• 4× Aux Low-Side (`AUX_LS1..4` on `J1-10..13`): `VNLD5090TR-E` (`PC6, PC7, PA15, PD3`; `J1-13` has 2.2 kΩ `+12V_MR` pull-up for Tach)<br>• 1× Dash Serial Low-Side (`DASH_TECH` on `J2-27`): `VNLD5090TR-E` (`PB9`) with 2.2 kΩ `+12V_MR` pull-up (SV650 7800-baud dash)<br>• 1× High-Side (`HS1` on `J1-14`): `VNQ7140AJ` (`PG4`) |
| **Stepper & H-Bridges** | • Onboard `DRV8825PWPR` (`U202`) on `J1-19..22` (`STEP_1A/1B/2A/2B`, `PB4/PB7/PB8`, 0.75 A limit) for SV650 `ISC` 4-wire idle stepper<br>• 2× `TLE9201SG` 6 A H-Bridges (`U201`, `U203`) on `J1-15..18` (`ETB1_OUT+/-`, `ETB2_OUT+/-`) for SV650 `STVA` 4-wire secondary throttle stepper or dual DBW throttles |
| **Trigger & Digital Inputs** | • 2× Differential VR Conditioners (`VR1+/-`, `VR2+/-` on `J2-11..14`): `MAX9924UAUB+` (`U3 -> PE14`, `U4 -> PE15`)<br>• 4× Protected Hall/Switch Inputs (`J2-15..18`): 4.7 kΩ pull-up to `5V_SENSOR_2` (`PG1, PG0, PE11, PE10`) |
| **Analog & Knock Inputs** | • 2× Thermistor Inputs (`CLT`, `IAT` on `J2-1..2`): 2.7 kΩ 0.1% pull-up to `5V_SENSOR_2` (`PC1, PC2`)<br>• 6× Ratiometric 0–5 V Inputs (`J2-3..8`): 5.6 kΩ / 10 kΩ divider + `MCP6004` buffer (`PA0..PA5`; `J2-8` `AV6_GEAR` has 1.5 kΩ pull-up to `5V_SENSOR_1` for SV650 6-speed gear switch)<br>• 2× Piezo Knock Channels (`KNOCK1..2` on `J2-9..10`): Active bandpass into `PF4` (`ADC3_INP9`) & `PF5` (`ADC3_INP4`) |
| **Barometric Sensor** | `U24`: `LPS25HBTR` (`I2C2` on `PB10/PB11`) at `(121.62, 100.61 mm)` inside an `ID 8.0 mm × OD 11.0 mm` potting keep-out dam for an ePTFE membrane enclosure vent (`Amphenol LTW VE80410` / `Gore PMF100321`) |
| **Logging Storage** | `U25`: Soldered `XTSD04GLGEAG` (4 Gbit / 512 MB SLC SD NAND, `6 × 8 mm` LGA-8) on 4-bit `SDMMC1` (`PC8..PC12, PD2`), ~20.2 hr capacity at 50 Hz; optional DNP `J10` microSD footprint |
| **Power Supply** | `SMBJ24CA` TVS + reverse-polarity PMOS -> `LM2733`/`LM3481` `VBOOST` pre-regulator -> `LMR14020` 5 V 2 A buck -> 2× `TLS115D0E` tracked 5 V sensor LDOs (`5V_SENSOR_1`, `5V_SENSOR_2`) + `BD3571` 3.3 V LDO |
| **Current Design State** | Schematics (`0` ERC errors), 474-part PCB placement (`0` DRC violations), BOM/CPL exports, and `fome-mc` firmware (`16/16` unit tests passing) are complete. **`237` ratsnest connections across `168` nets remain to be routed in KiCad `pcbnew` before Gerber fabrication.** |

---

## 2. Connector Pinout (`J1` & `J2` TE AMPSEAL 35-Pin)

### `J1` — 35-Pin AMPSEAL Black (`776163-1`, Power & High-Current Actuators)

| Pin | Signal | Net | MCU Pin | Rating / Driver | 2007 Suzuki SV650 (K7) Connection |
| :---: | :--- | :--- | :---: | :--- | :--- |
| `J1-1` | `INJ1` | `/LS1` | `PG5` | Low-Side 5 A (`U1001` `VNLD5090` + `D201`) | Front Cyl #1 Primary Injector `-` (`Gr/W`, ECM Pin `a`) |
| `J1-2` | `INJ2` | `/LS2` | `PG6` | Low-Side 5 A (`U1001` `VNLD5090` + `D202`) | Rear Cyl #2 Primary Injector `-` (`Gr/B`, ECM Pin `b`) |
| `J1-3` | `INJ3` | `/LS3` | `PG7` | Low-Side 5 A (`U1002` `VNLD5090` + `D203`) | Spare / Staged Front Injector 3 `-` |
| `J1-4` | `INJ4` | `/LS4` | `PG8` | Low-Side 5 A (`U1002` `VNLD5090` + `D204`) | Spare / Staged Rear Injector 4 `-` |
| `J1-5` | `PGND_INJ` | `GND` | `GND` | Power Ground Return (15 A) | Injector & Low-Side Solenoid Return (`B/W`, ECM `p/q`) |
| `J1-6` | `IGBT1` | `/IGN1_COIL` | `PB3` | 400 V 30 A IGBT (`Q201` `FGD3040G2`) | Front Cyl #1 Primary Coil `-` (`W/Bl`, ECM Pin `l`) |
| `J1-7` | `IGBT2` | `/IGN2_COIL` | `PG15` | 400 V 30 A IGBT (`Q202` `FGD3040G2`) | Rear Cyl #2 Primary Coil `-` (`B`, ECM Pin `c`) |
| `J1-8` | `IGBT3` | `/IGN3_COIL` | `PG14` | 400 V 30 A IGBT (`Q203` `FGD3040G2`) | Front Cyl #1 Trailing Side Coil `-` (4-Coil Split Mode) |
| `J1-9` | `IGBT4` | `/IGN4_COIL` | `PG13` | 400 V 30 A IGBT (`Q204` `FGD3040G2`) | Rear Cyl #2 Trailing Side Coil `-` (4-Coil Split Mode) |
| `J1-10` | `AUX_LS1` | `/LS5` | `PC6` | Low-Side 5 A (`U1101` `VNLD5090` + `D205`) | Fuel Pump Relay Coil `-` (`Y/R`, ECM Pin `W`) |
| `J1-11` | `AUX_LS2` | `/LS6` | `PC7` | Low-Side 5 A (`U1101` `VNLD5090` + `D206`) | Cooling Fan Relay Coil `-` (`B/W`, ECM Pin `V`) |
| `J1-12` | `AUX_LS3` | `/LS7` | `PA15` | Low-Side 5 A (`U1102` `VNLD5090` + `D207`) | PAIR Solenoid Valve `-` (`Br/B`, ECM Pin `e`) |
| `J1-13` | `AUX_LS4` | `/LS8` | `PD3` | Low-Side + 2.2 kΩ pull-up to `+12V_MR` (`R211`) | Tachometer Pulse Output 0–12 V (`Y/Bl`, ECM Pin `Z`) |
| `J1-14` | `HS1` | `/HS1` | `PG4` | High-Side 12 V 5 A (`U40` `VNQ7140AJ`) | Configurable High-Side Output 1 |
| `J1-15` | `ETB1_OUT+` | `/ETB1_OUT+` | `PD12/10/11` | 6 A H-Bridge 1 (`U201` `TLE9201SG` `OUT1`) | SV650 `STVA` Stepper Phase A+ (`W/R`, ECM Pin `[`) |
| `J1-16` | `ETB1_OUT-` | `/ETB1_OUT-` | `PD12/10/11` | 6 A H-Bridge 1 (`U201` `TLE9201SG` `OUT2`) | SV650 `STVA` Stepper Phase A- (`R`, ECM Pin `f`) |
| `J1-17` | `ETB2_OUT+` | `/ETB2_OUT+` | `PD13/9/8` | 6 A H-Bridge 2 (`U203` `TLE9201SG` `OUT1`) | SV650 `STVA` Stepper Phase B+ (`P/W`, ECM Pin `Y`) |
| `J1-18` | `ETB2_OUT-` | `/ETB2_OUT-` | `PD13/9/8` | 6 A H-Bridge 2 (`U203` `TLE9201SG` `OUT2`) | SV650 `STVA` Stepper Phase B- (`P`, ECM Pin `d`) |
| `J1-19` | `STEP_1A` | `/STEP_1A` | `PB4/7/8` | 0.75 A Chopper (`U202` `DRV8825` `AOUT1`) | SV650 `ISC` Idle Stepper Phase A+ (`Br/B`, ECM Pin `g`) |
| `J1-20` | `STEP_1B` | `/STEP_1B` | `PB4/7/8` | 0.75 A Chopper (`U202` `DRV8825` `AOUT2`) | SV650 `ISC` Idle Stepper Phase A- (`Br/W`, ECM Pin `^`) |
| `J1-21` | `STEP_2A` | `/STEP_2A` | `PB4/7/8` | 0.75 A Chopper (`U202` `DRV8825` `BOUT1`) | SV650 `ISC` Idle Stepper Phase B+ (`G/W`, ECM Pin `i`) |
| `J1-22` | `STEP_2B` | `/STEP_2B` | `PB4/7/8` | 0.75 A Chopper (`U202` `DRV8825` `BOUT2`) | SV650 `ISC` Idle Stepper Phase B- (`G/B`, ECM Pin `\`) |
| `J1-23` | `WBO1_HTR-` | `/WBO1_H-` | `WBO1:PB0` | Low-Side PWM 7.5 A (`Q301` `VND14NV04`) | Front Cyl #1 LSU 4.9 Pin 3 (`Heater -`, White) |
| `J1-24` | `WBO_HTR+` | `/12V_MR` | — | Switched `+12V_MR` Heater Feed | LSU 4.9 #1 & #2 Pin 4 (`Heater +12V`, Grey) |
| `J1-25` | `WBO2_HTR-` | `/WBO2_H-` | `WBO2:PB0` | Low-Side PWM 7.5 A (`Q401` `VND14NV04`) | Rear Cyl #2 LSU 4.9 Pin 3 (`Heater -`, White) |
| `J1-26` | `+12V_IGN_SW` | `/12V_RAW` | `PC5` (`ADC_15`) | Ignition Switch Run +12 V + `VBatt` Sense | Ignition / Kill Switch Run +12 V (`O/W`, ECM Pin `D`) |
| `J1-27` | `+12V_MR` | `/12V_MR` | `PF11` (`ADC_16`) | Main Relay Switched +12 V Input | Main Relay +12 V Supply (`R/Y`, ECM Pins `A & B`) |
| `J1-28` | `+12V_BATT_KEEPALIVE`| `/Perm_Live` | — | Unswitched Battery +12 V Backup | Unswitched Battery +12 V (`O/G`, ECM Pin `H`) |
| `J1-29` | `5V_SENSOR_1` | `/5V_SENSOR_1` | `PF12` (`ADC_17`) | Tracked 5.00 V 150 mA (`U1` `TLS115D0E`) | Primary Sensor +5 V (`R`, ECM Pin `C`: TPS, STPS, MAP, GP) |
| `J1-30` | `5V_SENSOR_2` | `/5V_SENSOR_2` | `PF14` (`PG`) | Tracked 5.00 V 150 mA (`U2` `TLS115D0E`) | Secondary / Aux Sensor +5 V (Hall, VSS, Aux Pressure) |
| `J1-31` | `SGND` | `GND` | `VSSA` | Analog & Sensor Return | Sensor Ground (`Br/B`, ECM Pin `9`) |
| `J1-32` | `PGND_IGN` | `GND` | `GND` | Ignition IGBT Emitter Return (15 A) | Ignition Power Ground (`B/W`, ECM Pins `p & q`) |
| `J1-33` | `PGND_HEATER` | `GND` | `GND` | Wideband Heater & H-Bridge Return | Battery Negative / Chassis Ground |
| `J1-34` | `CHASSIS_ECU_GND` | `GND` | `VSS` | Main ECU Reference Ground | ECU Logic Ground (`B/W`, ECM Pin `r`) |
| `J1-35` | `USB_VBUS_DFU` | `/RC2` | `PA9` + `BOOT0` | `+5 V` = USB VBUS; `+12 V` = Force ROM DFU | Service / Tuning Connector Pin 1 (`+5 V` normal, `+12 V` DFU) |

### `J2` — 35-Pin AMPSEAL Grey (`776163-2`, Sensors, Wideband Cells, Logic Coils, CAN & USB)

| Pin | Signal | Net | MCU Pin | Conditioning / Pull-Up | 2007 Suzuki SV650 (K7) Connection |
| :---: | :--- | :--- | :---: | :--- | :--- |
| `J2-1` | `CLT` | `/AT1` | `PC1` (`ADC_11`) | 2.7 kΩ 0.1% pull-up to `5V_SENSOR_2` (`R39`) | Engine Coolant Temp (`B/L`, ECM Pin `6`) |
| `J2-2` | `IAT` | `/AT2` | `PC2` (`ADC_12`) | 2.7 kΩ 0.1% pull-up to `5V_SENSOR_2` (`R40`) | Intake Air Temp (`Lg/B`, ECM Pin `7`) |
| `J2-3` | `TPS1` | `/AV2` | `PA1` (`ADC_1`) | 0–5 V (`5.6k/10k` div + `MCP6004` buffer) | Primary TPS (`P/B`, ECM Pin `5`) |
| `J2-4` | `TPS2_STPS` | `/AV4` | `PA3` (`ADC_3`) | 0–5 V (`5.6k/10k` div + `MCP6004` buffer) | Secondary TPS `STPS` (`W`, ECM Pin `4`) |
| `J2-5` | `MAP1_FRONT` | `/AV1` | `PA0` (`ADC_0`) | 0–5 V (`5.6k/10k` div + `MCP6004` buffer) | Front Cyl #1 IAP / MAP & Cam Phase (`G/B`, ECM Pin `3`) |
| `J2-6` | `MAP2_REAR` | `/AV3` | `PA2` (`ADC_2`) | 0–5 V (`5.6k/10k` div + `MCP6004` buffer) | Rear Cyl #2 IAP / MAP or External Analog Baro |
| `J2-7` | `AV5_TIPOVER` | `/AV5` | `PA4` (`ADC_4`) | 0–5 V (`5.6k/10k` div + `MCP6004` buffer) | Tip-Over Sensor (`Br/W`, ECM Pin `J`) |
| `J2-8` | `AV6_GEAR` | `/AV6` | `PA5` (`ADC_5`) | 1.5 kΩ 1% pull-up to `5V_SENSOR_1` (`R210`) | 6-Speed Gear Position Switch (`P`, ECM Pin `1`) |
| `J2-9` | `KNOCK1` | `/KNOCK_1` | `PF4` (`ADC3_9`) | 3.3 nF (`C16`) + active bandpass (`U50`) | Cyl #1 Piezo Knock Sensor |
| `J2-10` | `KNOCK2` | `/KNOCK_2` | `PF5` (`ADC3_4`) | 3.3 nF (`C17`) + active bandpass (`U50`) | Cyl #2 Piezo Knock Sensor |
| `J2-11` | `VR1+` | `/VR1+` | `PE14` | `U3` `MAX9924UAUB+` #1 `IN+` (10 kΩ + 1 nF) | Crankshaft Position Sensor `CKP+` 24-2 (`G`, ECM Pin `R`) |
| `J2-12` | `VR1-` | `GND` | — | `U3` `MAX9924UAUB+` #1 `IN-` return | Crankshaft Position Sensor `CKP-` (`Bl`, ECM Pin `8`) |
| `J2-13` | `VR2+` | `/VR2+` | `PE15` | `U4` `MAX9924UAUB+` #2 `IN+` (10 kΩ + 1 nF) | Camshaft / Secondary VR+ (Spare on camless K7) |
| `J2-14` | `VR2-` | `GND` | — | `U4` `MAX9924UAUB+` #2 `IN-` return | Camshaft / Secondary VR- (Spare on camless K7) |
| `J2-15` | `HALL1_CAM` | `/DIGITAL_2` | `PG1` | 4.7 kΩ pull-up to `5V_SENSOR_2` (`R24`) | Hall Cam / Aux Digital Input 1 |
| `J2-16` | `HALL2_VSS` | `/DIGITAL_1` | `PG0` | 4.7 kΩ pull-up to `5V_SENSOR_2` (`R23`) | Vehicle Speed Sensor Hall Input (`P`, ECM Pin `K`) |
| `J2-17` | `DIN1_CLUTCH` | `/DIGITAL_4` | `PE11` | 4.7 kΩ pull-up to `5V_SENSOR_2` (`R26`) | Clutch Switch Active-Low (`Y/G`, ECM Pin `M`) |
| `J2-18` | `DIN2_NEUTRAL` | `/DIGITAL_3` | `PE10` | 4.7 kΩ pull-up to `5V_SENSOR_2` (`R25`) | Neutral / Sidestand Switch Active-Low (`Bl`, ECM Pin `N`) |
| `J2-19` | `WBO1_VM` | `/WBO1_VM` | `WBO1:PA2/6` | 1.65 V Virtual Ground (`U301` `MCP6004`) | Front Cyl #1 LSU 4.9 Pin 2 (`Vm`, Yellow) |
| `J2-20` | `WBO1_IP` | `/WBO1_IP` | `WBO1:PA1/5` | Pump Current via 61.9 Ω 0.1% (`R310`) | Front Cyl #1 LSU 4.9 Pin 1 (`Ip`, Red) |
| `J2-21` | `WBO1_RCAL` | `/WBO1_RTRIM` | — | Calibration Trim Node (`R310:1`) | Front Cyl #1 LSU 4.9 Pin 5 (`Rcal`, Green) |
| `J2-22` | `WBO1_UN` | `/WBO1_UN` | `WBO1:PA3/7/9`| Nernst Sense + 4.9 kHz AC ESR (`U305` `AD8628`)| Front Cyl #1 LSU 4.9 Pin 6 (`Un / Vs`, Black) |
| `J2-23` | `IGN1_LOG` | `/IGN5` | `PG12` | 5 V Push-Pull (`U44` `MIC4427` + 100 Ω `R112`)| Optional Smart Coil 1 Logic Trigger |
| `J2-24` | `IGN2_LOG` | `/IGN6` | `PG11` | 5 V Push-Pull (`U44` `MIC4427` + 100 Ω `R113`)| Optional Smart Coil 2 Logic Trigger |
| `J2-25` | `IGN3_LOG` | `/IGN7` | `PG10` | 5 V Push-Pull (`U45` `MIC4427` + 100 Ω `R114`)| Optional Smart Coil 3 Logic Trigger |
| `J2-26` | `IGN4_LOG` | `/IGN8` | `PG9` | 5 V Push-Pull (`U45` `MIC4427` + 100 Ω `R115`)| Optional Smart Coil 4 Logic Trigger |
| `J2-27` | `DASH_TECH` | `/LS14` | `PB9` | Low-Side + 2.2 kΩ pull-up to `+12V_MR` (`R212`)| SV650 K7 7800-Baud Dash Serial (`B/G`, ECM Pin `U`) |
| `J2-28` | `CAN1_H` | `/CAN+` | `PD0/PD1` | 500 kbps ISO 11898 (`U4` `TJA1051T/3` + 120 Ω)| External `CAN1_H` (Dash / OBD / OpenBLT) |
| `J2-29` | `CAN1_L` | `/CAN-` | `PD0/PD1` | 500 kbps ISO 11898 (`U4` `TJA1051T/3` + 120 Ω)| External `CAN1_L` (Dash / OBD / OpenBLT) |
| `J2-30` | `WBO2_VM` | `/WBO2_VM` | `WBO2:PA2/6` | 1.65 V Virtual Ground (`U401` `MCP6004`) | Rear Cyl #2 LSU 4.9 Pin 2 (`Vm`, Yellow) |
| `J2-31` | `WBO2_IP` | `/WBO2_IP` | `WBO2:PA1/5` | Pump Current via 61.9 Ω 0.1% (`R410`) | Rear Cyl #2 LSU 4.9 Pin 1 (`Ip`, Red) |
| `J2-32` | `WBO2_RCAL` | `/WBO2_RTRIM` | — | Calibration Trim Node (`R410:1`) | Rear Cyl #2 LSU 4.9 Pin 5 (`Rcal`, Green) |
| `J2-33` | `WBO2_UN` | `/WBO2_UN` | `WBO2:PA3/7/9`| Nernst Sense + 4.9 kHz AC ESR (`U405` `AD8628`)| Rear Cyl #2 LSU 4.9 Pin 6 (`Un / Vs`, Black) |
| `J2-34` | `USB_D+` | `/USB_D+` | `PA12` | USB FS 90 Ω Diff + `U27` `USBLC6-2SC6` | Service / Tuning USB `D+` (TunerStudio / MSD / DFU) |
| `J2-35` | `USB_D-` | `/USB_D-` | `PA11` | USB FS 90 Ω Diff + `U27` `USBLC6-2SC6` | Service / Tuning USB `D-` (TunerStudio / MSD / DFU) |

---

## 3. Internal Buses & Onboard Peripherals

| Function | `STM32H753` Pin(s) | Connected IC / Node | Notes |
| :--- | :--- | :--- | :--- |
| **Internal `CAN2` (Wideband Bus)** | `PB12` (`RX`), `PB13` (`TX`) | `U5` (`TJA1051T/3` H7) <-> `U200` (`WBO1/2` CAN) | 500 kbps; carries `0xEF50000` (`VBatt` + `HeaterAllow`), WBO telemetry (`0x190..0x193`), and OpenBLT wideband updates |
| **`WBO1` Address Strap & Recovery** | `PE2` (`NRST`), `PE3` (`BOOT0`) | `U302` (`STM32F042K6T6` #1) | Strapped `PB1 = GND`, `PA8 = Float` -> `CanIndexOffset = 0` (`0x190/0x191`) |
| **`WBO2` Address Strap & Recovery** | `PE4` (`NRST`), `PE5` (`BOOT0`) | `U402` (`STM32F042K6T6` #2) | Strapped `PB1 = Float`, `PA8 = +3.3V` -> `CanIndexOffset = 1` (`0x192/0x193`) |
| **4-Bit `SDMMC1` (Soldered SD NAND)** | `PC8..PC11` (`D0..D3`), `PC12` (`CK`), `PD2` (`CMD`) | `U25` (`XTSD04GLGEAG` LGA-8) + DNP `J10` | `SPI3` is disabled in `board_configuration.cpp` so `PC10..PC12` remain dedicated to `SDMMC1` |
| **Onboard Barometer (`I2C2`)** | `PB10` (`SCL`), `PB11` (`SDA`) | `U24` (`LPS25HBTR`, `0x5D`) | Placed in unpotted chimney pocket (`121.62, 100.61 mm`) beneath ePTFE vent |
| **Main Relay Self-Hold** | `PE0` (`mainRelayPin`) | `U1202` (`VNLD5090` `lowside_quad4/IN3`) | Holds main relay / keep-alive during shutdown log flush |
| **Onboard Voltage Sense Dividers** | `PC5`, `PF11`, `PF12`, `PF13` | `EFI_ADC_15..18` | `PC5` = `VBatt` (9.2:1), `PF11` = `MainRelay` (9.2:1), `PF12` = `5V_SENSOR_1` (2.0:1), `PF13` = `VBoost` (9.2:1) |

---

## 4. Schematic Sheet & Reference Designator Map

| Schematic File | Ref Range | Subsystem |
| :--- | :---: | :--- |
| [`fome-mc.kicad_sch`](fome-mc.kicad_sch) | `J1`, `J2` | Root sheet, dual 35-pin AMPSEAL headers, and hierarchical interconnects |
| [`mcu.kicad_sch`](mcu.kicad_sch) | `U23..U28`, `R209`, `D19` | `STM32H753ZIT6` (`U26`), `XTSD04GLGEAG` SD NAND (`U25`), `LPS25HBTR` baro (`U24`), `REF3033` (`U23`), `USBLC6` (`U27`), `J1-35` DFU override |
| [`psu.kicad_sch`](psu.kicad_sch) | `U1..U5`, `U46`, `D1..D18` | `VBoost` (`U46`), `LMR14020` 5 V buck (`U3`), 2× `TLS115D0E` (`U1`, `U2`), `BD3571` 3.3 V LDO, `TJA1051T/3` `CAN1`/`CAN2` (`U4`, `U5`) |
| [`ign_igbt.kicad_sch`](ign_igbt.kicad_sch) & [`ign4.kicad_sch`](ign4.kicad_sch) | `Q201..Q204`, `U42..U45`, `D201..D208` | 4× `FGD3040G2-F085C` IGBTs (`Q201..Q204`), 4× `MIC4427` gate/logic drivers (`U42..U45`), 8× `SK310A` low-side flyback diodes (`D201..D208`) |
| [`stepper_etb.kicad_sch`](stepper_etb.kicad_sch) & [`etb-9201.kicad_sch`](etb-9201.kicad_sch) | `U201..U203` | 2× `TLE9201SG` 6 A H-bridges (`U201`, `U203`) + `DRV8825PWPR` bipolar stepper driver (`U202`) |
| [`wbo1.kicad_sch`](wbo1.kicad_sch) | `301..399` | Wideband Controller #1 (`U302` `STM32F042K6T6`, `U301` `MCP6004`, `U305` `AD8628`, `U303` `REF3033`, `Q301` `VND14NV04`) |
| [`wbo2.kicad_sch`](wbo2.kicad_sch) | `401..499` | Wideband Controller #2 (`U402` `STM32F042K6T6`, `U401` `MCP6004`, `U405` `AD8628`, `U403` `REF3033`, `Q401` `VND14NV04`) |
| [`triggers.kicad_sch`](triggers.kicad_sch) | `U33`, `U34` | 2× `MAX9924UAUB+` adaptive VR conditioners + 4× Hall/Digital input filters |
| [`quad_analog.kicad_sch`](quad_analog.kicad_sch) & [`quad_analog_pullup.kicad_sch`](quad_analog_pullup.kicad_sch) | `U15`, `U17`, `U19`, `U21` | `MCP6004` analog buffers, 5.6 kΩ / 10 kΩ dividers, 2.7 kΩ 0.1% thermistor pull-ups, 1.5 kΩ SV650 gear pull-up (`R210`) |
| [`lowside_quad.kicad_sch`](lowside_quad.kicad_sch) & [`highside_quad.kicad_sch`](highside_quad.kicad_sch) | `U1001..U1202`, `U40` | 8× `VNLD5090TR-E` dual low-side switches + `VNQ7140AJ` high-side switch |
| [`knock.kicad_sch`](knock.kicad_sch) | `U50`, `C16`, `C17` | 2-channel active bandpass knock filter into `PF4`/`PF5` |

---

## 5. Build, Verification & Firmware Workflows

### Prerequisites
Expects the shared FOME KiCad libraries checked out as a sibling directory at `../kicad-libraries` (`https://github.com/FOME-Tech/kicad-libraries` @ `ab9c5f8a`) and the FOME firmware fork at `../fome-fw` (`https://github.com/halbritt/fome-fw`, branch `fome-mc`).

### Verify Hardware & Export Manufacturing Files
```bash
# 1. Verify pinned KiCad 10 / KiBot / Python toolchain and library mounts
make doctor

# 2. Verify 1-to-1 parity across io-map.csv, exported netlist, PCB footprints, and firmware mapping.yaml
python3 scripts/verify_io_map.py

# 3. Run hermetic KiCad 10 ERC, DRC, netlist, KiBot Gerber/drill/BOM/CPL/PDF export, and analysis
make check
```
Manufacturing outputs are written to [`export/BOM-fome-mc.csv`](export/BOM-fome-mc.csv), [`export/CPL-fome-mc.csv`](export/CPL-fome-mc.csv), and `build/runs/project/fome-mc/<timestamp>/export/`.

### Build `fome-mc` Firmware & Run Unit Tests
```bash
# Compile OpenBLT bootloader + fome-mc firmware image + TunerStudio .ini
cd ../fome-fw/firmware
bash config/boards/fome-mc/compile_fome-mc.sh

# Run host unit tests (including SV650 odd-fire trailing spark & overdwell tests)
cd ../unit_tests
make -j$(nproc)
./build/fome_test --gtest_filter="*trailingSpark*:*BufferedWriter*:*OddFire*"
```

---

## 6. Flashing, Log Retrieval & Post-Potting Recovery

1. **Routine Tuning & Firmware Updates (`OpenBLT`)**:
   - Connect USB (`J1-35` = `+5 V VBUS`, `J2-34` = `USB_D+`, `J2-35` = `USB_D-`) or `CAN1` (`J2-28/29`) and flash `deliver/fome_update.srec` from TunerStudio or OpenBLT `BootCommander`.
2. **SD NAND Log Download (`Single-Owner FatFs -> USBMSD1 Handoff`)**:
   - With the engine running (`RPM > 0`), `FatFs` owns `U25` (`SDCD1`) exclusively and syncs `.mlg` logs every 2 seconds.
   - When USB is plugged in with the engine stopped (`RPM == 0`), the firmware flushes and unmounts `FatFs` and mounts `U25` as a standard USB Mass Storage drive (`USBMSD1`).
3. **Unbricking the Main `STM32H753` After Potting (`ROM USB DFU`)**:
   - Apply **`+12 V`** (through a 1 kΩ current-limiting resistor or bench supply) to **`J1-35` (`USB_VBUS_DFU`)** while powering `+12V_MR` (`J1-27`). This conducts `6.8 V` Zener `D19` to drive `U26` `BOOT0 = 3.1 V`, enumerating the STM32 mask-ROM bootloader (`0483:df11`) on `J2-34/35`:
     ```bash
     dfu-util -a 0 -d 0483:df11 -s 0x08000000:leave -D deliver/fome.bin
     ```
4. **Updating or Recovering Onboard Wideband MCUs (`WBO1` / `WBO2`)**:
   - `STM32H753` pins `PE2` (`WBO1_NRST`), `PE3` (`WBO1_BOOT0`), `PE4` (`WBO2_NRST`), and `PE5` (`WBO2_BOOT0`) allow the H7 to hold one `STM32F042K6T6` in hardware reset while updating the other over internal `CAN2` via OpenBLT.

---

## 7. Further Documentation

- **[`DESIGN.md`](DESIGN.md)** — Architecture decisions, SV650 K7 factory wiring analysis, barometric vent pocket math, SD NAND endurance calculations, thermal dissipation budget, and 2-stage polyurethane potting specification.
- **[`VALIDATION.md`](VALIDATION.md)** — Verification ledger and pre-/post-encapsulation bench test gates.
- **[`CHANGELOG.md`](CHANGELOG.md)** — Chronological history of hardware and firmware changes from `Polygonus V1.6.1` -> `fome-mc` -> `fome-mc`.
