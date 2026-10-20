# Complete MCU terminal contract

This packet extends the endpoint evidence to **all 41 terminals of U1**, the
ESP32-S3-WROOM-1-N8. It complements `../interface-contract` (35 J1 cavities and
15 expansion GPIO reservations). It does not replace the historical pilot IO
map, the full compiled hardware-interface contract or firmware configuration.

The source is the retained series-divider intent; the native evidence is the
released-presentation candidate generated with agent-ee `014c7c3`. The checker
requires exact selected-part identity, complete pin inventory, unique source
and native terminal assignments, native library pin labels, explicit NCs and
source/native net correspondence. For each signal, the independently stated
contract also lists every direct peer. Power-net members are compared between
source and native XML but are not independently enumerated here. Power flags
are omitted only from that membership comparison because native XML omits them;
the retained independent native review checks their physical schematic wiring.

The 41 terminals comprise 30 signals, four power/ground terminals and seven
explicit no-connects. No electrical changes are made by this contract.

| Module pin | Library label | Net | Direct signal peers |
| --- | --- | --- | --- |
| 1 | GND | GND | Source/native membership |
| 2 | 3V3 | +3V3 | Source/native membership |
| 3 | EN | MCU_EN | C47.1, R29.2, TP4.1, U16.6, U17.6, U22.1 |
| 4 | IO4 | TWAI_TX | U100.1 |
| 5 | IO5 | TWAI_RX | U100.4 |
| 6 | IO6 | IMU_INT1 | U2.4 |
| 7 | IO7 | GNSS_PPS | U3.3 |
| 8 | IO15 | TIRE_CAN_CS | R66.2, U20.13 |
| 9 | IO16 | TIRE_CAN_INT_N | R67.2, U20.4 |
| 10 | IO17 | GNSS_RX_IN | U3.21 |
| 11 | IO18 | GNSS_TX_OUT | U3.20 |
| 12 | IO8 | POWER_FAIL_N | R65.2, U19.6 |
| 13 | USB_D- | NC | Explicit NC |
| 14 | USB_D+ | NC | Explicit NC |
| 15 | IO3 | NC | Explicit NC |
| 16 | IO46 | MCU_BOOT46 | R33.1 |
| 17 | IO9 | ADC_CS | R32.2, U4.10 |
| 18 | IO10 | IMU_CS | R31.2, U2.12 |
| 19 | IO11 | SPI_MOSI | U2.14, U20.11, U4.11 |
| 20 | IO12 | SPI_SCK | U2.13, U20.10, U4.13 |
| 21 | IO13 | SPI_MISO | U2.1, U20.12, U4.12 |
| 22 | IO14 | DIAG_I2C_SDA | R160.2, U27.15, U28.15, U29.15 |
| 23 | IO21 | DIAG_I2C_SCL | R161.2, U27.16, U28.16, U29.16 |
| 24 | IO47 | EMMC_DAT3 | R50.2, U14.B2 |
| 25 | IO48 | SENSOR_FAULT_N | R64.2, U18.6 |
| 26 | IO45 | NC | Explicit NC |
| 27 | IO0 | MCU_BOOT | R30.2, TP5.1 |
| 28 | IO35 | NC | Explicit NC |
| 29 | IO36 | NC | Explicit NC |
| 30 | IO37 | NC | Explicit NC |
| 31 | IO38 | EMMC_CLK | U14.M6 |
| 32 | IO39 | EMMC_CMD | R46.2, U14.M5 |
| 33 | IO40 | EMMC_DAT0 | R47.2, U14.A3 |
| 34 | IO41 | EMMC_DAT1 | R48.2, U14.A4 |
| 35 | IO42 | EMMC_DAT2 | R49.2, U14.A5 |
| 36 | RXD0 | POD_UART_RX | TP2.1 |
| 37 | TXD0 | POD_UART_TX | TP1.1 |
| 38 | IO2 | WHEEL_REAR_CAPTURE | R127.2 |
| 39 | IO1 | WHEEL_FRONT_CAPTURE | R118.2 |
| 40 | GND | GND | Source/native membership |
| 41 | GND | GND | Source/native membership |

## Interpretation and remaining work

- The shared SPI nets connect the MCU to U2 IMU, U4 MCP3208 and U20 tire-CAN
  controller. Their distinct chip selects are present. This does not prove
  mode/frequency selection, arbitration, chip-select timing or MISO release.
- Diagnostic I2C reaches all three converters and the two pull-ups. Address
  selection, pull-up loading, conversion timing and firmware scheduling remain
  separate checks.
- Six MCU signals reach eMMC clock, command and DAT0..3. GPIO35/module28 remains
  NC; an optional reset reservation was not implemented. This is not evidence
  of a working SDMMC driver, media recovery or firmware pin-matrix setup.
- GNSS_RX_IN names the receiver input: it connects to U3.21. GNSS_TX_OUT
  connects U3.20. Firmware transmit/receive directions must follow the actual
  endpoints, not infer MCU direction from the net suffix.
- Wheel capture ends here at R118.2 and R127.2. The conditioner and external
  sensor paths, their voltage/pulse limits and selected sensors require separate
  qualification.
- MCU_EN has both supervisor outputs, U22.1, RC components and a debug pad.
  Static wiring does not establish reset timing, hysteresis or supply validity.
  SENSOR_FAULT_N only reflects its implemented sensing path.
- GPIO0 and GPIO46 retain boot circuitry. GPIO3 and GPIO45 are NC. The check
  preserves those assignments; it does not validate boot-strap voltage margins.
- Module/library pin labels are captured design evidence, not independent
  manufacturer pinout qualification. UART loading, debug access, radio/storage
  concurrency and power behavior remain open.

## Replay

```sh
python3 telemetry-pod/expansion/mcu-contract/check.py
```

Output must match `report.json`. Alternate `--contract`, `--intent` and
`--native` paths support checking subsequent candidates or damaged controls.
The report hashes all three inputs. Four retained negative controls reject a
swapped SPI assignment, an omitted module terminal, a missing explicit NC and
an unexpected native SPI peer. These checks establish static correspondence,
not complete satisfaction of acceptance criterion 1.
