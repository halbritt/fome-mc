# Telemetry pod requirements

Oct 17, 2026 · @Heath · Revision 2, Oct 18, 2026: the owner decisions of 2026-10-18 are folded into the text below; this file supersedes the Oct 17 text (sha256 c5128ef9391e2114…).

## Purpose

The tail-cowl telemetry pod is the first real board the agent-ee generator must produce from a specification, before it is pointed at fome-mc. fome-mc already defines the pod's job and its CAN interface in its telemetry document but left the parts, mechanics and acceptance criteria open. This document closes them, with every choice settled with Heath on 2026-10-17, so the generator's input is fixed and its output can be judged.

Everything here is a requirement on the pod, not a design. Where a part is named, it is a decision made once by hand so that what the generator proposes can be compared against it. Facts about fome-mc are taken from the repository as of 2026-10-17 (commit c582b29). The pod design will live in the fome-mc repository alongside the ECU.

## Function

The pod is a CAN1 node mounted in the tail cowl of the SV650 that measures chassis dynamics the ECU cannot reach and publishes them twice: on CAN1 for the ECU's .mlg logs, and over Bluetooth LE to RaceChrono Pro together with the ECU's own 0x200..0x207 frames. It has no control outputs.

| Quantity | Sensor on the pod | Range | Rate | Published as |
| --- | --- | --- | --- | --- |
| Lateral, longitudinal, vertical acceleration | 6-axis IMU | ±16 g minimum | 100 Hz | 0x174, 0x178, 0x17C (Bosch MM5.10 format) |
| Yaw, roll, pitch rate | same IMU | ±2000 °/s | 100 Hz | 0x174, 0x178, 0x17C |
| Lean and pitch angle | computed on the pod from the IMU | ±65°, ±45° | 100 Hz | 0x301 |
| Front fork travel | external linear potentiometer, 0–5 V | 0–130 mm | 200 Hz | 0x300 |
| Rear shock travel | external linear potentiometer, 0–5 V | 0–70 mm | 200 Hz | 0x300 |
| Front and rear brake pressure | external transducers, 0.5–4.5 V | 0–100 bar | 100 Hz | 0x301 |
| Position, speed, heading, altitude | GNSS receiver | multi-constellation | 25 Hz | 0x302, and BLE GPS characteristic |

The pod also relays every CAN1 frame it receives from the ECU to RaceChrono over the BLE DIY CAN characteristic, filtered to the IDs RaceChrono subscribes to. The four analog channels are 12-bit and ratiometric to the pod's own 5 V sensor supply (see Interfaces), so the channels need no recalibration against the regulator. The pod is a standalone unit with its own power supply; the ECU's 5V\_SENSOR\_2 rail is not used.

## Interfaces

The pod's external interfaces are fixed by fome-mc and are not the generator's to change. Frame layouts, scaling and the RaceChrono channel equations are in [fome-mc docs/TELEMETRY\_AND\_RACECHRONO.md](https://github.com/halbritt/fome-mc/blob/main/docs/TELEMETRY_AND_RACECHRONO.md); the harness pins are in [docs/WIRING\_SV650\_K7.md](https://github.com/halbritt/fome-mc/blob/main/docs/WIRING_SV650_K7.md).

| Interface | Requirement |
| --- | --- |
| CAN1 | ISO 11898-2, 500 kbit/s, classic CAN 2.0B. Transmit 0x174/0x178/0x17C at 100 Hz, 0x300 at 200 Hz, 0x301 at 100 Hz, 0x302 at 25 Hz. Receive 0x200..0x207. 120 Ω termination on the pod (far end of the harness; the ECU carries the other). ESD protection on CAN\_H and CAN\_L. |
| Bluetooth LE | BLE 5.0 peripheral implementing the RaceChrono DIY GATT service (0x1FF8) with the CAN main, filter and two GPS characteristics. Range to a phone in a tank bag or jacket pocket. |
| Power in | Switched 12 V from the main-relay output, spliced in the harness on the same circuit that feeds the ECU's J1-27 input, through the pod's own 2 A fuse; ground to chassis on the ECU's J1-34 (CHASSIS\_ECU\_GND) circuit. The pod never draws power from the ECU. Operate from 9 V to 16 V; survive 12 V automotive transients (ISO 7637-2 pulses, 40 V clamp) and reverse polarity. Budget under 2 A at 12 V including sensors. |
| Sensor supply | Provide 5.00 V ±1 % at 200 mA to the four external sensors from the pod's own regulator. The ADC reference derives from this same rail at the connector so the channels stay ratiometric. The ECU's 5V\_SENSOR\_2 is not used. |
| Analog inputs | Four channels, 0–5 V, 12-bit, ratiometric to the sensor supply, input-protected to 16 V, 200 Hz per channel. |
| GNSS antenna | Active antenna connector (SMA or U.FL) if the receiver has no integrated antenna; see component decisions. |
| Programming and debug | Factory firmware load and serial console over UART pogo-pin test pads before the enclosure is sealed. Field updates over BLE using the ESP-IDF OTA dual-partition scheme from the first firmware. No CAN1 bootloader and no external USB connector. |
| Harness connector | One TE AMPSEAL 23-position header, TE 776228-1 (right-angle PCB header, black, the ECU J1 family), carrying CAN\_H, CAN\_L, +12 V, ground, and the four sensors (each with supply, signal and return): 16 signals in a 23-position housing, unused cavities plugged. |

## Component decisions

These are the choices fome-mc's telemetry document left as alternatives, settled here. Where fome-mc already carries a verified part for the same job, the pod reuses it, in line with the composition approach. LCSC numbers are given only where fome-mc's BOM already has them; the parts stage captures the rest.

| Function | Decision | Why | Not chosen |
| --- | --- | --- | --- |
| MCU and radio | ESP32-S3-WROOM-1 module (8 MB flash) | BLE 5 for the RaceChrono DIY service without a second radio, a built-in CAN 2.0B controller (TWAI), a pre-certified module antenna, and existing RaceChrono DIY firmware on ESP32 (RejsaCAN) to start from. | STM32G4: needs a separate BLE radio and firmware. Bare ESP32-S3 chip: RF layout and certification burden for no gain. |
| CAN transceiver | TJA1051T/3 (LCSC C38695) with PESD1CAN-UX (C907839) and a 120 Ω termination (C22787) | The transceiver fome-mc's wideband sheets use, composed with the ESD part and termination from fome-mc's PSU sheet (which itself uses an MCP2551 at the ECU end); VCC on 5 V, VIO on 3.3 V logic. Composing from two sheets is a recorded deviation from "block carried over unchanged". | MCP2562FD: equivalent, but a new part with no fome-mc precedent. |
| IMU | LSM6DSO32, SPI | ±32 g accelerometer and ±2000 °/s gyro so engine vibration does not clip the signal; output rate to 6.66 kHz so the pod can filter down to 100 Hz on-board. | BMI270: ±16 g ceiling, consumer grade. BMI088: good vibration behaviour, kept as the fallback if bench tests show rectification errors with the LSM6DSO32. |
| GNSS | NEO-M9N with an external active antenna on an SMA connector | The 25 Hz requirement. The NEO-M9N delivers [25 Hz with four concurrent constellations](https://www.mouser.lt/pdfDocs/ProductOverview_Sparkfun_NEO-M9NGPSBreakoutBoard.pdf); the SAM-M10Q with its integrated antenna tops out at [18 Hz single-constellation and 10 Hz multi-constellation](https://cdn.sparkfun.com/assets/1/1/d/f/4/SAM-M10Q_DataSheet_UBX-22013293.pdf). | SAM-M10Q: simpler (no antenna cable) but too slow for the spec. |
| Analog front end | MCP3204 12-bit 4-channel SPI ADC. Inputs and the ADC reference are both divided by two from the 5 V sensor rail. | Keeps the four channels ratiometric to the sensor supply with the ADC on 3.3 V, and samples far above the 200 Hz needed. | ESP32-S3 internal ADC: nonlinear and noisy. ADS1115: 860 samples/s total, below 4 channels at 200 Hz. |
| Power | Reverse-polarity and transient protection at the input (TVS clamp at 24 V working, 40 V peak), a synchronous buck rated for 40 V input making the 5 V sensor rail, a second regulator making 3.3 V at 1 A for the module's radio peaks | Standard automotive front end; the 1 A rail covers ESP32-S3 transmit peaks. Exact regulators are the generator's choice from LCSC stock. | A single LDO from 12 V: dissipation at 1 A is unacceptable. |
| Harness connector | TE AMPSEAL 23-position header 776228-1 (right-angle, black) with the matching 23-position plug, cavity plugs 770678-1 and 770520-3 contacts (the family comes in 8, 14, 23 and 35 positions), same family as the ECU's J1 and J2, 16 cavities used | One crimp tool, one seal system and one set of cavity plugs across the bike. | A separate waterproof connector family: more tooling for no benefit. |
| Board | 4 layers, 1.6 mm FR-4, JLCPCB standard stackup, JLCPCB basic parts preferred where a basic part meets the requirement | A solid ground under the module antenna and the GNSS RF path, and easier routing for kicad-route. The price difference to 2 layers is small at this size. | 2 layers: possible, but RF grounding and routing both suffer. |

## Mechanical and environment

The pod lives under the tail cowl of a 2007 SV650, next to the battery and tail light wiring, and is treated like the ECU: sealed, vibration-loaded, and not serviced on the roadside.

- Board envelope 80 mm by 50 mm or smaller, component height 12 mm or less above the board, mounting holes in all four corners. The rear seat cowl is large, so the envelope is not tight.
- Enclosure sealed to IP67, non-metallic over the ESP32 module antenna, with the harness connector and the SMA antenna connector the only penetrations. Potting is acceptable as for the ECU, provided the IMU is rigidly coupled to the enclosure and the enclosure to the frame; a floating IMU measures the pod, not the bike.
- Operating temperature −20 °C to +85 °C board ambient. Parts rated to 105 °C or higher.
- Vibration: a V-twin at 10,000 rpm puts strong content between 50 Hz and 400 Hz into the frame. The IMU's ±32 g range is chosen for this. Mount the pod on the frame, not the cowl plastic, and keep tall or heavy parts (connector, SMA, electrolytic capacitors) away from the IMU.
- IMU axes aligned to the bike: X forward, Y left, Z up, marked on the silkscreen, so that the frame scaling matches Bosch MM5.10 conventions without a software rotation.
- GNSS antenna mounted inside the cowl, as high as possible and facing up. The cowl is fiberglass and therefore transparent to GNSS and BLE, so neither antenna needs to penetrate it. Antenna cable no longer than 500 mm to the SMA connector.

## Acceptance criteria

A generated pod design is accepted when all of the following hold, each backed by tool output in the evidence trail. Items 1 to 7 are checked on the files; 8 and 9 on a built board.

1. Every interface row above is satisfied, with a pinout table equivalent to fome-mc's io-map that names, for each connector position, the signal, the net, the MCU pin and the external destination, verified by a script against the schematic.
2. Every part in the component decisions table is present, with the stated part number, or a deviation is recorded with a reason.
3. ERC and DRC report zero errors and zero unwaived warnings under the fome-mc toolchain rules. A warning is waived only by an owner-recorded disposition bound to the exact violation (rule, items, reason, location hash); a moved or new violation needs a new disposition, and agents do not waive.
4. The kicad-happy schematic, PCB, cross-analysis and EMC analyzers, run offline, report no findings at error level; findings at warning level are listed with a disposition. SPICE is not part of this criterion.
5. Every BOM line has an LCSC part number that is in stock at JLCPCB on the day of generation, captured from JLCPCB's public component search per LCSC id with the response hash and UTC timestamp as evidence. Parts JLCPCB does not stock or assemble (the 776228-1 header, and the NEO-M9N or SMA connector if unstocked) are hand-fitted after delivery: excluded from assembly with a not\_assembled marker and a recorded deviation naming the purchase source.
6. The fab package contains Gerbers, drill files, BOM and CPL in JLCPCB's formats, and a JLCPCB DFM check on the Gerbers passes: the owner uploads the sealed Gerber package to JLCPCB once and the saved DFM report is bound to the package hash as evidence; geometry pre-checks against JLCPCB's captured capability limits run in the pipeline but do not replace it. CPL rotations the captured policy cannot verify are listed as PREVIEW\_REQUIRED obligations for the owner to confirm in JLCPCB's placement preview before ordering.
7. The board fits the envelope, the mounting holes are where the mechanical section says, the IMU axis marking is on the silkscreen, and the module antenna keep-out matches the ESP32-S3-WROOM-1 datasheet.
8. On a bench CAN bus with the ECU, the frames 0x174, 0x178, 0x17C, 0x300, 0x301 and 0x302 appear at their stated rates within 5 %, and the ECU logs lean angle, brake pressure and suspension travel in its .mlg file.
9. RaceChrono Pro pairs with the pod over BLE and shows ECU RPM alongside pod lean angle and GPS speed at 25 Hz.

The design does not need to be routed by hand, placed by hand, or match any particular layout. If the generator proposes a different part from the decisions table and records a reason that holds up, that is a finding about the table, not a failure.
