# Expanded connector and GPIO contract

This contract checks all 35 J1 cavities and all 15 expansion GPIO reservations
against the latest series-divider source and its retained native netlist. It
preserves `../allocation.json` as the historical planning record and makes the
selected naming changes explicit. It does not replace the pilot `io-map.csv`,
compiled path contract, firmware configuration or full interface qualification.

The selected connector is **TE 1-776163-1**, with gold contacts. The historical
allocation's `776163-1` is a different part and is not the selected identity.
Both source and native component metadata must match the selected connector
and ESP32-S3-WROOM-1-N8. The connector's availability and mechanical holds remain.

Tire CAN's planned `POD_TIRE_CAN_H/L` names became `TIRE_CAN_H/L`. Storage's
planned `STORAGE_*` names became `EMMC_*`. The optional reset reservation on
GPIO35/module pin28 remains explicitly unconnected. This contract does not
claim that a storage reset line was implemented. J1 cavity35 is also explicitly
unconnected, checked in both source and native XML.

## Connector cavities

| J1 cavity | Current native net | State |
| --- | --- | --- |
| 1 | POD_CAN_P | connected |
| 2 | POD_CAN_N | connected |
| 3 | POD_12V_IN | connected |
| 4 | GND | connected |
| 5 | POD_5V_SENSOR | connected |
| 6 | POD_FRONT_FORK_SIGNAL | connected |
| 7 | GND | connected |
| 8 | POD_5V_SENSOR | connected |
| 9 | POD_REAR_SHOCK_SIGNAL | connected |
| 10 | GND | connected |
| 11 | POD_5V_SENSOR | connected |
| 12 | POD_FRONT_BRAKE_SIGNAL | connected |
| 13 | GND | connected |
| 14 | POD_5V_SENSOR | connected |
| 15 | POD_REAR_BRAKE_SIGNAL | connected |
| 16 | GND | connected |
| 17 | POD_AUX1_SIGNAL | connected |
| 18 | POD_AUX2_SIGNAL | connected |
| 19 | POD_AUX3_SIGNAL | connected |
| 20 | POD_AUX4_SIGNAL | connected |
| 21 | POD_5V_AUX | connected |
| 22 | GND | connected |
| 23 | POD_WHEEL_FRONT_SUPPLY | connected |
| 24 | POD_WHEEL_FRONT_SIGNAL | connected |
| 25 | GND | connected |
| 26 | POD_WHEEL_REAR_SUPPLY | connected |
| 27 | POD_WHEEL_REAR_SIGNAL | connected |
| 28 | GND | connected |
| 29 | TIRE_CAN_H | connected |
| 30 | TIRE_CAN_L | connected |
| 31 | POD_TIRE_SUPPLY | connected |
| 32 | GND | connected |
| 33 | TIRE_CAN_H | connected |
| 34 | TIRE_CAN_L | connected |
| 35 | N/C | no_connect |

## Expansion processor pins

| GPIO | Module terminal | Planned role | Current native net |
| --- | --- | --- | --- |
| 1 | 39 | WHEEL_FRONT_CAPTURE | WHEEL_FRONT_CAPTURE |
| 2 | 38 | WHEEL_REAR_CAPTURE | WHEEL_REAR_CAPTURE |
| 8 | 12 | POWER_FAIL_N | POWER_FAIL_N |
| 14 | 22 | DIAG_I2C_SDA | DIAG_I2C_SDA |
| 21 | 23 | DIAG_I2C_SCL | DIAG_I2C_SCL |
| 15 | 8 | TIRE_CAN_CS | TIRE_CAN_CS |
| 16 | 9 | TIRE_CAN_INT_N | TIRE_CAN_INT_N |
| 38 | 31 | STORAGE_CLK | EMMC_CLK |
| 39 | 32 | STORAGE_CMD | EMMC_CMD |
| 40 | 33 | STORAGE_D0 | EMMC_DAT0 |
| 41 | 34 | STORAGE_D1 | EMMC_DAT1 |
| 42 | 35 | STORAGE_D2 | EMMC_DAT2 |
| 47 | 24 | STORAGE_D3 | EMMC_DAT3 |
| 48 | 25 | SENSOR_FAULT_N | SENSOR_FAULT_N |
| 35 | 28 | STORAGE_RESET_N_OPTION | N/C |

The checker requires complete allocation membership, unique cavities and GPIO
terminals, explicit NC evidence, exact source/native net names and native library
GPIO labels. It refuses expansion use of GPIO0/3/45/46. Pin labels are captured
library evidence, not a new manufacturer datasheet qualification.

## Replay and remaining work

```sh
python3 telemetry-pod/expansion/interface-contract/check.py
```

Output must match `report.json`. `--intent` and `--native` permit exact alternate
or damaged evidence inputs. The selected contract and historical allocation are
hashed into the report along with both design artifacts.

Independent `review/check_review.py` checks a separately stated cavity/GPIO
map and rejects swapped wheel cavities, an incorrect GPIO label and a removed
native NC marker. Its output matches `review/report.json`.

The next full interface contract must include all existing processor connections,
CAN/analog/Hall conditioning paths, SPI ownership, I2C addresses, SDMMC settings,
power/reset behavior, firmware assignments and timing/error limits. This contract
establishes connector and allocated processor endpoints only. It does not prove
sensor compatibility, transient tolerance, logging duration, wireless retrieval
or assembled hardware operation.
