# Independent CAN2 pre-emission review

Scope: MCP2518FD-E/SL at 3.3 V, shared ADC/IMU SPI initially 1 MHz, dedicated CS GPIO15/module8 and INT GPIO16/module9, separate TJA1051T/3 tire bus at 500 kbit/s, workload ceiling 800 received classic frames/s. This is circuit and firmware preparation, not a native graph review or physical qualification. No source repository modified.

## Conclusion

The proposed topology is feasible. Include a chip-select pull-up, explicit interrupt configuration/pull-up, local supply bypass, and a clock source before emission. Firmware must enforce MISO release time and implement the published errata. A 32-entry timestamped receive FIFO is adequate only with a bounded service schedule; 800 frames/s alone is not a burst bound. The four-bit eMMC bus is separate electrically but CPU/cache/DMA stalls can still delay CAN servicing.

## Verified controller and transceiver facts

Source: captured Microchip DS20006027B, Tables 1-1, 7-1, 7-3, 7-6; sections 3.3, 4 and 5. Source hashes/URLs are in ../sources/manifest.json.

SOIC-14 MCP2518FD pin map: 1 TXCAN, 2 RXCAN, 3 CLKO/SOF, 4 active-low INT, 5 OSC2, 6 OSC1, 7 VSS, 8 INT1/GPIO1, 9 INT0/GPIO0/XSTBY, 10 SCK, 11 SDI, 12 SDO, 13 nCS, 14 VDD. SOIC has no exposed pad. Supply 2.7–5.5 V; E temperature grade -40 to +125 C. These selected parts do not close temperature limits of other pod components.

TJA1051T/3 pin map (NXP Table 3): 1 TXD, 2 GND, 3 VCC, 4 RXD, 5 VIO, 6 CANL, 7 CANH, 8 S. Connect MCP1→TJA1 and TJA4→MCP2; VCC to existing 5 V CAN rail and VIO to main 3.3 V. NXP Table 1 gives VCC 4.5–5.5 V, VIO 2.8–5.5 V. Budget another transceiver's maximum 70 mA dominant current on 5 V plus IO consumption (Table 1), not its recessive typical current. Pin S high disables transmission while reception remains active; S low enables normal operation. A receiver-only silent transceiver does not ACK frames, so require another ACK-capable node or operate normally. Include local bypass for each supply and preserve a separate tire CANH/CANL network, protection and configurable end termination; existing ECU CAN pins must not be joined.

## SPI and startup requirements

Microchip section 4 permits mode 0 or 3, eight-bit transfers. Configure the bus per device. At 20 MHz SYSCLK the errata/data-sheet SCK ceiling is 0.85*(20 MHz/2) = 8.5 MHz, comfortably above the proposed 1 MHz. Do not assume the headline 20 MHz maximum applies.

Table 7-6 specifies SDO high impedance no later than **2 SCK periods after nCS rises**. At 1 MHz enforce at least 2 microseconds before another shared-bus device drives MISO. Also satisfy CS setup ≥0.5 SCK period, final-clock-to-CS ≥1 period and same-device CS-high ≥1 period. Verify peripheral-generated CS timing and measured shared-bus behavior; a software bus mutex alone does not establish these timings. A CS pull-up keeps the controller deselected during ESP reset. SDO needs a weak bias during controller Sleep to avoid excess sleep current (section 4 note 2).

There is no separate reset pin. Section 4.1.1 says issue SPI RESET only after entering Configuration mode. RESET resets SFR/state machines but leaves RAM unchanged. Request and verify Configuration mode before runtime reset; do not reset blindly during bus activity. Initialize message RAM with ECC enabled before relying on stored data, then configure FIFOs and filters before enabling normal reception. Poll oscillator-ready after power-up; Table 7-3 allows up to 3 ms stabilization. Table 7-1 also requires VDD rise ≥0.05 V/ms for POR; verify the actual main rail waveform. MCU-only supervisor reset does not necessarily reset a still-powered controller.

INT is push-pull at POR (IOCON.INTOD=0); configure open drain if desired, using a 10 kohm 3.3 V pull-up. Do not assume the pin is inherently open drain. Keep unused GPIO/clock outputs explicitly assigned or NC according to the configured mode. Use single-byte IOCON writes.

## All captured errata must be implemented

Microchip DS80000789C, pages 1–2:

1. READ_CRC can return correct data with incorrect CRC for changing register bits; retry CRC mismatches with a bounded policy and report persistent failures. Read receive RAM only after its receive flag asserts. Avoid FIFOs 7/15/23/31 to reduce affected status bits, although this does not eliminate all cases.
2. ECC single-error correction is not reliable in every case. Enable SECIE and DEDIE; treat either interrupt as data corruption at ERRADDR and invalidate/report affected data. Do not claim transparent correction.
3. SFR rollover 0x3FF→0x000 and 0xFFF→0xE00 does not work; split accesses before these boundaries. RAM rollover does work as specified.
4. RAM writes during CAN activity can corrupt at fast SPI speeds; enforce SCK ≤0.425*SYSCLK.
5. Multi-byte IOCON writes can clear LAT0/LAT1; use single-byte SFR writes.

## Proposed FIFO and service budget

Configure FIFO1 RX, FSIZE=31 (32 entries), PLSIZE=0 (8-byte payload), RXTSEN=1. Each received object is 8-byte header + 4-byte timestamp + 8-byte payload = 20 bytes (Table 3-6), hence 640 bytes. Enable not-empty and overflow interrupts and acceptance filters for only the tire identifiers. Timestamp close to reception, not after logging stalls.

Configure FIFO2 TX, FSIZE=3 (4 entries), PLSIZE=0: 4*16 = 64 bytes. Disable TXQ and TEF unless firmware needs them. Explicitly set the other 29 FIFOs to minimum one-entry, 8-byte payload without timestamps and route no filters to them; conservatively account for their 29*16 = 464 bytes because section 3.3 allocates FIFO1 through FIFO31. Total **1168 of 2048 bytes**, leaving 880 bytes; do not assume unused FIFOs consume zero or retain larger reset/default payload settings. This avoids the four erratum-sensitive FIFO numbers for active traffic.

At a perfectly paced 800 frames/s, 32 entries represent 40 ms. That is not a guaranteed blackout allowance. A synchronized two-sensor update can arrive as eight frames in a burst, and an eight-byte standard classic frame occupies at least 111 bits including intermission, so 32 back-to-back frames can fill this FIFO in about 7.1 ms at 500 kbit/s before stuffing. Shorter accepted messages can fill it faster. Proposal: begin servicing within 2 ms of an asserted receive interrupt, use bounded transactions and drain according to actual occupancy. The selected sensors' identifiers, DLCs and burst envelope must establish the final bound. Count/report overflow and loss rather than silently continuing.

Conservative illustrative 1 MHz service per full frame: 6-byte status read + 6-byte user-address read + 25-byte READ_CRC of a 20-byte object + 3-byte UINC write = 40 SPI bytes = 320 microseconds, plus CS guards/software overhead. At 800/s this uses 25.6% of wire time before retries. It is not a measured driver budget. The accepted 200 complete analog scans/s, eight channels and three SPI bytes/channel would add 38.4 kbit/s = 3.84% at 1 MHz. Actual ADC scan/IMU internal acquisition rates may exceed their log rates; inventory those real transfer workloads. Cap individual other-device bus holds and bound scheduling delays, including flash/cache and eMMC work. Do not let a long ADC/IMU transaction or unbounded drain loop starve the other acquisition deadlines.

## Proposed oscillator specification

Prefer a **20.000 MHz 3.3 V CMOS oscillator**, -40 to +125 C, ≤100 ppm total initial/temperature/supply/aging error, 45–55% duty cycle and rise/fall ≤20 ns at actual load, connected to OSC1 with OSC2 NC. Disable PLL and SYSCLK divide-by-two. Provide the oscillator's specified local bypass and default enabled control. This avoids unproven crystal startup/load selection; it is a component requirement, not an exact approved MPN. Verify output levels against MCP input specifications and avoid driving an unpowered MCP.

If a crystal is chosen instead, 20 MHz is supported, but select the exact fundamental-mode crystal/ESR/drive/CL and derive capacitors from its CL and estimated board/pin capacitance. The drawing's 22 pF parts are an example, not a universal validated load. The datasheet does not provide a 20 MHz transconductance minimum, so startup margin needs supplier guidance and measurement; do not infer a qualified ESR limit from the 40 MHz guidance.

At 20 MHz a provisional 500 kbit/s timing is BRP=0, 40 time quanta, TSEG1=31 and TSEG2=8 (encoded fields 30 and 7), 80% sample point; SJW up to 8 quanta (encoded 7). This is arithmetic from CiNBTCFG, not approval of an unknown harness length, propagation delay or peer oscillator tolerance. Confirm network timing before release.

## Remaining boundaries

No exact oscillator, CAN protection/termination or passives are qualified here. GPIO assignments require regenerated native graph verification. Protected switching of the 6.3 V sensor branch and wheel-input conditioning remain separate unresolved design tasks. No power-loss flush window, EMC, thermal, harness or production acceptance is inferred.
