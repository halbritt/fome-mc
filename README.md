# Atlas-clone (STM32H7 Brain Module for FOME `atlas` Firmware)

`Atlas-clone` is a KiCad 8.0 hardware design derived from [FOME-Tech/Polygonus](https://github.com/FOME-Tech/Polygonus) V1.6.1 (`polygonus-Shortage-Version`) and adapted to run the FOME [`atlas`](https://github.com/FOME-Tech/fome-fw/tree/master/firmware/config/boards/atlas) (`ARCH_STM32H7`) firmware while resolving all JLCPCB component shortages.

It preserves the exact 107-pin 0.1" Polygonus baseboard footprint (`J4` 32p, `J5` 32p, `J6` 16p, `J7` 16p, `J11` 6p AUX SPI, `J9` 6p SWD) as a drop-in replacement.

---

## 1. Summary of Hardware Changes vs. Polygonus V1.6.1

1. **MCU (`U26`) — `STM32H753ZIT6` (`C730207`) / `STM32H743ZIT6` (`C114408`):**
   * Upgraded from `STM32F767ZIT6` (`C90235`) to `STM32H753ZIT6` (`C730207`, 2 MB dual-bank Flash, 1 MB RAM, 480 MHz Cortex-M7, LQFP-144; 100% pin- and binary-compatible with `STM32H743ZIT6` `C114408`).
2. **No WiFi (`SPI4` omitted):**
   * `PE2` (`SPI4_SCK`), `PE3` (`ISR`), `PE4` (`CS`), `PE5` (`SPI4_MISO`), `PE6` (`SPI4_MOSI`), and `PC13` (`RST`) are left unconnected (`no_connect`).
3. **`VBoost` Pre-Regulator (`psu.kicad_sch`):**
   * Added `U46` (`LM2733XMFX/NOPB`, SOT-23-5, LCSC `C80169`), `L3` (`10uH` `MWSA0503`, LCSC `C408412`), `D18` (`D_Schottky` SMA, LCSC `C8678`), `C107` (`4.7uF`, LCSC `C19666`), and feedback divider `R122` (`68k`, LCSC `C36871`) / `R123` (`10k`, LCSC `C25744`).
   * Sets minimum `VBoost` floor to $1.23\,\text{V} \times (1 + 68\text{k}/10\text{k}) = 9.59\,\text{V}$ so the `LMR14020` (`U3`) 5V buck regulator and `TLS115D0E` (`U1`, `U2`) 5V sensor trackers never drop out during low-voltage cranking (4.5–6V). During normal 13.8V operation, `U46` stays idle and `12V_PROT` passes through `L3` + `D18`.
4. **Onboard Voltage Sense ADC Dividers (`mcu.kicad_sch`):**
   * `PC5` (Pin 45, `EFI_ADC_15`, `BatteryVoltage`): Connected to existing `R96` (`82k`) / `R97` (`10k`) `12V_DIVIDED` sense divider (`9.2:1`).
   * `PF11` (Pin 49, `EFI_ADC_16`, `MainRelayVoltage`): Added `R116` (`82k`, `C23254`) / `R117` (`10k`, `C25744`) + `C103` (`100n`, `C14663`) divider from `12V_MR` (`9.2:1`). Required by `main_relay.cpp` fault check.
   * `PF12` (Pin 50, `EFI_ADC_17`, `Sensor5vVoltage`): Added `R118` (`10k`, `C25744`) / `R119` (`10k`, `C25744`) + `C104` (`100n`, `C14663`) 1:1 divider (`2.0:1`) from `5V_SENSOR_1`. Required by `sensor_checker.cpp` (expects `4.75V–5.25V`).
   * `PF13` (Pin 53, `EFI_ADC_18`, `VboostVoltage`): Added `R120` (`82k`, `C23254`) / `R121` (`10k`, `C25744`) + `C105` (`100n`, `C14663`) divider from `VBOOST` (`9.2:1`).
5. **32.768 kHz CMOS Active Oscillator (`mcu.kicad_sch`):**
   * Added `U28` (`S3225SMD32.768KOSC`, LCSC `C7431189`) + `C106` (`100n`, LCSC `C14663`) driving `PC14` (Pin 8, `OSC32_IN`) as required by `atlas/board.mk` (`-DSTM32_LSE_BYPASS`).
6. **4-Bit `SDMMC1` MicroSD Wiring (`J10` in `mcu.kicad_sch`):**
   * Upgraded `J10` from 1-bit `SPI3` to 4-bit `SDMMC1`:
     * `PC8` (Pin 98) $\rightarrow$ `SD_D0` (`J10` Pad 7 `DAT0`)
     * `PC9` (Pin 99) $\rightarrow$ `SD_D1` (`J10` Pad 8 `DAT1`)
     * `PC10` (Pin 111) $\rightarrow$ `SD_D2` (`J10` Pad 1 `DAT2`)
     * `PC11` (Pin 112) $\rightarrow$ `SD_D3` (`J10` Pad 2 `CD/DAT3`)
     * `PC12` (Pin 113) $\rightarrow$ `SD_CLK` (`J10` Pad 5 `CLK`)
     * `PD2` (Pin 116) $\rightarrow$ `SD_CMD` (`J10` Pad 3 `CMD`)
7. **`IGN9–12` Kept as Direct MCU Passthroughs:**
   * `IGN1–8` (`PB3, PG15, PG14, PG13, PG12, PG11, PG10, PG9`) drive the 4× dual `MIC4427` (`U42–U45`) 5V push-pull ignition drivers.
   * `IGN9–12` (`PD7, PD6, PD5, PD4`) remain direct MCU passthroughs to the baseboard headers (and `PD5`/`PD6` remain connected to `J12` for `USART2`).
8. **SMD Automotive Hybrid Polymer Bulk Capacitors (`C1, C6`):**
   * Replaced THT `56uF 50V` (`CP_Radial_D8.0mm_P3.50mm`) with SMD `47uF 50V` AEC-Q200 Conductive Polymer Hybrid Aluminum Electrolytic (`Capacitor_SMD:CP_Elec_8x10.5`, Panasonic `EEHZC1H470P`, LCSC `C454346`) so JLCPCB SMT places the entire board.

---

## 2. Complete MCU Pin Remap (`Polygonus` $\rightarrow$ `Atlas-clone`)

| Function | Polygonus (`proteus_f7`) | `Atlas-clone` (`atlas` H7) |
|---|---|---|
| `LS1..LS4` (`VNLD5090` `U1001, U1002`) | `PD7, PG9, PG10, PG11` | `PG5, PG6, PG7, PG8` (Pins 90–93) |
| `LS5..LS8` (`VNLD5090` `U1101, U1102`) | `PG12, PG13, PG14, PB4` | `PC6, PC7, PA15, PD3` (Pins 96, 97, 110, 117) |
| `LS9..LS12` (Passthrough) | `PB5, PB6, PB7, PB8` | `PB4, PB5, PB6, PB7` (Pins 134–137) |
| `LS13..LS16` (`VNLD5090` `U1201, U1202`) | `PB9, PE0, PE1, PE2` | `PB8, PB9, PE0, PE1` (Pins 139–142) |
| `IGN1..IGN4` (`MIC4427` `U42, U43`) | `PD4, PD3, PC9, PC8` | `PB3, PG15, PG14, PG13` (Pins 133, 132, 129, 128) |
| `IGN5..IGN8` (`MIC4427` `U44, U45`) | `PC7, PG8, PG7, PG6` | `PG12, PG11, PG10, PG9` (Pins 127, 126, 125, 124) |
| `IGN9..IGN12` (Passthrough) | `PG5, PG4, PG3, PG2` | `PD7, PD6, PD5, PD4` (Pins 123, 122, 119, 118) |
| `HS1..HS4` (`BTS716G` `U40`) | `PA9, PA8, PD15, PD14` | `PG4, PG3, PG2, PD15` (Pins 89, 88, 87, 86) |
| `AV1..AV8` (`MCP6004` `U17, U19`) | `PC0..PC3, PA0..PA3` | `PA0..PA7` (Pins 34–37, 40–43) |
| `AV9..AV11` (`MCP6004` `U21`) | `PA4..PA6` | `PB0, PB1, PC0` (Pins 46, 47, 26) |
| `AT1..AT4` (`MCP6004` `U15`) | `PC4, PC5, PB0, PB1` | `PC1, PC2, PC3, PC4` (Pins 27–29, 44) |
| `12V_DIVIDED` (`BatteryVoltage`) | `PA7` (Pin 43) | `PC5` (Pin 45, `EFI_ADC_15`) |
| `MR_DIVIDED` (`MainRelayVoltage`) | — | `PF11` (Pin 49, `EFI_ADC_16`) |
| `5V_SENSE_DIVIDED` (`Sensor5vVoltage`) | — | `PF12` (Pin 50, `EFI_ADC_17`) |
| `VBOOST_DIVIDED` (`VboostVoltage`) | — | `PF13` (Pin 53, `EFI_ADC_18`) |
| `DIGITAL1..DIGITAL6` | `PC6, PE11..PE15` | `PG0, PG1, PE10..PE13` (Pins 56, 57, 63–66) |
| `VR_1, VR_2` | `PE7, PE8` | `PE14, PE15` (Pins 67, 68) |
| `LED1` (Red `D10`), `LED2` (Blue `D11`), `LED3` (Green `D12`), `LED4` (Orange `D13`) | `PE3, PE4, PE5, PE6` | `PF0` (Pin 10), `PF2` (Pin 12), `PD14` (Pin 85), `PF1` (Pin 11) |

---

## 3. JLCPCB BOM & CPL Exports

* [`export/BOM-Atlas-clone.csv`](export/BOM-Atlas-clone.csv) & [`export/CPL-Atlas-clone.csv`](export/CPL-Atlas-clone.csv): Complete JLCPCB SMT BOM and component placement list for `Atlas-clone` using verified in-stock LCSC part numbers.
* [`export/BOM-Polygonus-V1.6.1-InStock.csv`](export/BOM-Polygonus-V1.6.1-InStock.csv): Drop-in BOM for the unmodified Polygonus V1.6.1 Gerbers/CPL using `C5271061` (`STM32F777ZIT6`, 262 in stock at JLCPCB) and all verified in-stock substitutes.

> **Note before plotting Gerbers for `Atlas-clone.kicad_pcb`:**
> All net assignments on `U26`, `J10`, `J12`, `C1`, `C6`, and the newly added footprints (`U28`, `C106`, `U46`, `L3`, `D18`, `R122`, `R123`, `C107`, `R116–R121`, `C103–C105`) are updated in `Atlas-clone.kicad_pcb`. Open `Atlas-clone.kicad_pcb` in KiCad 8 `pcbnew`, update the local fanout tracks around `U26` and the newly placed components to clear the ratsnest and DRC, refill zones (`B`), and plot the Gerbers.
