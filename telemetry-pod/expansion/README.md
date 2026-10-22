# Expanded pod implementation allocation

This directory records the implementation allocation for Revision 3. It is not
the released schematic, BOM or verified io-map. The committed v9 design remains
the earlier pilot. `allocation.json` reserves pins for the complete expansion so
that individual additions cannot consume the same terminal twice.

The latest prepared source is [series-divider](series-divider/README.md), built
on [component-fit](component-fit/README.md). It selects exact parts for the
expanded functions and implements R60 as two series resistors without shifting
the nominal supervisor threshold. Its native schematic now reproduces exactly
using unreleased agent-ee candidate `b42adf7`, with independent graph, metadata,
BOM and ERC checks. This is not released software or hardware qualification.
Earlier snapshots retain evidence of their individual preparation and review stages.
The [supply-monitor coverage](supply-monitor-coverage/README.md) records the
current series-divider graph's sensing boundaries and ten diagnostic channels,
including the added supervisor midpoint.
The [expanded endpoint contract](interface-contract/README.md) checks all 35
connector cavities and 15 expansion GPIO allocations against that source and
native netlist, with explicit tire CAN/eMMC aliases and unused reset state.
The full compiled interface and firmware contract remain outstanding.
The [production capture](production-capture/README.md) binds the microSD source's parts manifest,
deviations, patched CAD closure and revised envelope for a pod run. J3's datasheet is its one
exact missing capture.

## Connector and buses

Keep J1 positions 1–16 functionally unchanged. Positions 17–20 carry the four
auxiliary analog signals; 21–22 provide their shared protected 5 V branch and
return. Front and rear wheel sensors each get a power/signal/return triple at
23–25 and 26–28. Returns join board ground; separate pins do not imply galvanic
isolation or a Kelvin measurement.

The auxiliary branch must derive from the same regulated sensor rail that
generates `SENSOR_REF_2V5`. Include protection-switch resistance, connector and
cable drops in the ratiometric error budget. An independently regulated auxiliary
5 V supply would require a different reference/calibration treatment; equal
nominal voltages do not establish ratiometric tracking.
Place optional thermistor pull-ups on the protected auxiliary branch, downstream
of its switch; an auxiliary branch fault invalidates those channels. Calibration
must include the input divider's parallel loading. The prepared thermistor
candidate uses a separate2.495V shunt excitation downstream of AUX5V to absorb
input-fault current. It therefore needs explicit excitation/reference calibration;
it does not inherit ratiometric accuracy from its upstream power source.

Positions 29–30 and 33–34 carry the same dedicated tire-sensor CAN pair, providing
two harness legs for a linear bus. Positions 31–32 supply the tire sensors, and
35 remains unconnected. This avoids extending or changing the ECU CAN1 end
termination. Tire CAN needs its own controller and transceiver; the ESP32-S3's
existing TWAI remains assigned to ECU CAN1.

Use a 500 kbit/s classic CAN tire bus. Terminate at the two physical harness ends,
with no permanent termination at the pod when both legs are populated. Provide
an assembly option for pod termination when it is an end node. Verify harness
topology, stubs and termination in each supported installation. The captured
Izze sensor family is a compatibility candidate; its default 1 Mbit/s settings,
IDs, zone count and power must be configured and checked before connection.
This allocation does not establish compatibility with every CAN tire sensor.

Reserve a separate four-bit SDMMC bus for soldered logging media. Keep the
existing ADC/IMU SPI pins and chip selects. A tire CAN controller may share that
SPI bus with its own chip select and interrupt; bound transfer lengths and
interrupt service latency must preserve the acquisition deadlines. A separate
I2C diagnostic ADC with an independent reference can measure input, intermediate,
sensor and logic rails without consuming any of the eight external analog
channels. Exact identities and captured sources are now present in the prepared stages;
operating qualification remains open.
The maximum tire workload is 800 received classic CAN frames/s. Size the
controller receive buffers against worst-case SPI service latency, not average
bus utilization. Configure SDMMC width explicitly to four bits for the microSD socket
(`storage-microsd/`, owner decision 2026-10-21: eMMC dropped). Verify card I/O voltage
and pull-ups at selection.

`allocation.json` maps GPIO numbers to module terminals. Factory UART, GNSS,
IMU, ADC and existing CAN pins are retained. Strapping GPIOs are not repurposed.
GPIO35 is the microSD card-detect input (`SD_CD`, formerly the optional storage
reset); it must be reconsidered if the module's flash/PSRAM variant changes. The six
storage pins are reservations, not proof of timing or routing closure.

## Wheel sensor interface

Develop two three-wire Hall inputs with protected power, pull-up, input
protection and hysteretic conditioning into 3.3 V capture signals. VR compatibility
is not claimed. This choice provides useful low-speed sensing without requiring
the ADC to sample wheel pulses.

The captured ZF GS100502 is an electrical candidate: its manufacturer specifies
5–24 V supply, 6 mA maximum supply current, open-collector output and sensing up
to 15 kHz. Its minimum 5 V supply makes a nominal 5.00 V ±1% rail inadequate at
the low tolerance limit, even before cable drop. Develop a protected digital
sensor rail above 5 V; 6.3 V is a design candidate, subject to the power and fault
analysis. The output pull-up connects to sensor VCC per the manufacturer, so a
direct MCU connection is unsuitable.

Do not commit to this sensor's mechanics yet. Its reference target geometry
includes 6.35 mm target thickness and 10 mm tooth spacing. A thin motorcycle tone
ring is not qualified by this datasheet. Compare a compact motorsport Hall
sensor and validate the actual ring, bracket, gap/runout, cable and speed range
before freezing the sensor BOM. No arbitrary ABS sensor interchangeability is
implied. No sensors or tone rings have been purchased.

## Logging workload and capacity

The proposed binary records below include timestamps and status fields. Log
wheel estimates and counters at 100 Hz per wheel; this budget does not log every
raw wheel edge. IMU data here means the filtered 100 Hz output, not the full
internal sampling rate. CAN records include identifier, direction, DLC, payload
and timing. Raw ECU frames preserve the original telemetry alongside pod data.
Tire records are decoded, assembled zone samples with validity information;
the budget does not also retain their individual raw CAN frames. Missing or
inconsistent constituent frames must be reported rather than silently combined
into a fresh complete sample.

| Stream | Records/s | Bytes/record | Bytes/s |
| --- | ---: | ---: | ---: |
| Eight analog samples in one record | 200 | 24 | 4,800 |
| Filtered IMU and orientation | 100 | 32 | 3,200 |
| GNSS solution | 25 | 40 | 1,000 |
| Eight ECU CAN frames at 50 Hz each | 400 | 24 | 9,600 |
| Two wheel estimates at 100 Hz each | 200 | 24 | 4,800 |
| Two tire sensors, 16 zones, 100 Hz each | 200 | 48 | 9,600 |
| Supply and health diagnostics | 10 | 32 | 320 |
| Pod transmitted CAN frames | 625 | 24 | 15,000 |
| **Subtotal** | | | **48,320** |
| **With 25% framing/index/future allowance** | | | **60,400** |

The ECU frame rate comes from `docs/TELEMETRY_AND_RACECHRONO.md` section 2.
The pod CAN count is 3×100 + 200 + 100 + 25 frames/s. Tire coverage is a declared
upper workload, not a selected sensor or achieved rate.

At 60,400 bytes/s, eight hours needs 1,739,520,000 bytes. A 4 GB decimal device
with only 80% allocated to recordings would provide 14.72 hours by capacity.
This is arithmetic headroom, not measured logging duration or endurance.
Select at least 4 GB soldered managed media with a verified temperature grade
and power-loss behavior. Compare the ECU's SDNAND precedent with automotive
eMMC; do not inherit either part's qualification from the ECU.

Use monotonic timestamps anchored to GNSS PPS/UTC when available, with explicit
time-validity and epoch records. Retain timing through GNSS loss without
inventing UTC. Require sequence numbers, per-block CRCs and recoverable segment
boundaries. Do not silently overwrite old sessions when full: stop recording
with a persistent full-media indication until the owner deletes/downloads data.
Wireless retrieval uses Wi-Fi while parked; BLE retains RaceChrono and OTA.

A completed file-system write does not establish that managed flash survives
power loss. Keep write caching and flush semantics explicit. Measure storage
busy time and power consumption before sizing hold-up energy. Until those
tests pass, neither bounded log loss nor safe power removal is established.

## Connector CAD hold

The [connector candidate](connector-candidate/README.md) now captures TE's current
K1 drawing and exact 1-776163-1 revision T STEP. Its project-local footprint
corrects the locator pattern, and native drill/model checks cover all35 contacts
and both locator holes. The earlier J8 mirror remains historical evidence.
The shared ECU library and actual pod still need deliberate adoption; this
standalone candidate is not whole-board mechanical qualification.

The local `Simon.pretty/ampseal-35` and fome-mc
`libs/footprints/ampseal.pretty/ampseal-35` contain four PCB NPTH at the panel
mounting pattern. TE J8 sheet 2 specifies two PCB locating holes, diameter
2.85 ±0.08 mm, on 57 mm centers. The four panel mounting holes belong to the
enclosure face, in a different plane. The 35 contact holes are 1.75 ±0.1 mm
after plating; board fabrication must meet that finished-hole tolerance.

The footprint also uses the 76.9 ×32.1 mm mating-face dimensions as a board-plane
rectangle. The 32.1 mm flange height is not the right-angle connector's PCB
depth. Its referenced `1-776231-1` STEP model does not establish the identity or
placement of 776163-1. Independent review confirmed these defects.

Before binding the replacement footprint:

1. Use the captured K1 drawing and exact-part revision T model, retaining the
   documented revision differences and physical tolerance checks.
2. Adopt the reviewed connector-candidate coordinates and model transform into
   the regenerated project, then recheck its emitted pins, drills and model.
   Row 1–12 is farthest from the mating face; row 24–35 is nearest.
3. Project the full housing into the board plane for courtyard/keepout and
   verify mounting-hole, enclosure, connector access and antenna clearance.
4. Establish installed height from a board-plane datum and measure actual
   enclosure/cowl clearance. The owner clarified on 2026-10-20 that the earlier
   12 mm limit was arbitrary and not owner-specified. Clearance is unknown;
   no connector-specific exception is pending. J1 orientation remains an
   engineering choice subject to the measured enclosure and harness geometry.
5. Confirm nominal 1.6 mm board thickness and tolerances against TE's 1.57 mm
   recommended-board drawing.

Neither library footprint is copied into the candidate merely to clear an ERC
warning. No ECU/global library was modified by this investigation.

The [storage circuit candidate](storage-candidate/README.md) preserves an
expanded native schematic with eMMC wiring, a separate core regulator and
independent review. Supervision and power qualification remain unfinished;
it does not replace the actual project or qualify release.
