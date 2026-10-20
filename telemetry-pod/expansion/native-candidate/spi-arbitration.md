# Shared SPI arbitration: implementation and qualification still required

The native graph connects U1 pin21, U4 pin12, U2 pin1 and U20 pin12 on SPI_MISO.
U4, U2 and U20 have distinct chip selects, each with a pull-up. The corrected
MCP3208 symbol represents its deselected high-impedance state. ERC cannot prove
that the devices never drive concurrently.

The retained source evidence supports these bounded conclusions:

| Device | Evidence | Limit of this evidence |
| --- | --- | --- |
| MCP3208 | DS21298E timing diagrams show disabled DOUT; table lists tDIS 100 ns maximum and tCSH 500 ns minimum | Default table conditions include 5 V. Neither number is promoted to a guaranteed 3.3 V bound here. |
| MCP2518FD | Captured AC table defines TSCK=1/FSCK and TCS2SDOZ up to 2 TSCK at 50 pF | At the proposed initial 1 MHz this calculates to 2 µs; actual clock, load, setup/hold and all errata constraints must be met. |
| LSM6DSO32 | Captured SPI table gives output release timing; its interface description enables I²C when CS is high by default | SPI startup must deliberately handle I2C_disable configuration and resets. Timing conditions and full-device behavior remain part of review. |

The required firmware behavior is one owner of the entire physical bus, including
chip-select changes, DMA/interrupt completion, mode/clock changes and recovery.
It must establish all chip selects high before enabling transfers, select only
one device at a time, wait for the final clock and peripheral completion, then
deselect and satisfy a qualified release interval before selecting the next
device. Release intervals must follow the previous device and actual clock/load
conditions. A fixed delay inferred from a single device or a faster clock is
insufficient. Changes of SPI mode must occur with all chip selects inactive.

Reset, abort, brownout and retry paths need the same ownership and deselection
rules. Pull-ups do not by themselves prove contention-free power sequencing,
partial-power behavior or MCU pin behavior during reset. The IMU's default I²C
interpretation of shared clock/data activity before configuration needs explicit
analysis and hardware observation; writing a register once does not cover a
later device reset. CAN CRC/errata handling and diagnostic schedules remain
separate requirements.

No telemetry-pod firmware implementing this contract or measured bus-turnaround
waveforms were present in the inspected packet. Qualification requires device
specifications at the actual rails and temperature, selected bus loading and
clock/mode constraints, firmware review, and measurements across device changes,
reset and fault recovery. These remain open even though native ERC is clean.

Sources: [MCP3208 manufacturer PDF](sources/mcp3208.pdf),
[CAN manufacturer capture](../interface-preparation/sources/mcp2518fd.pdf), and
[the independent source review](review/README.md). `spi-sources.json` pins the
new ADC source bytes; earlier captures retain their existing provenance.
