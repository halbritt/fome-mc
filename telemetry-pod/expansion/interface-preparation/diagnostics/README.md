# Rail-diagnostic ADC selection and input study

Status: pre-emission candidate. No schematic, placement, firmware, or hardware
qualification is established by this study. The existing eight-channel MCP3208
remains dedicated to sensor acquisition. This separate diagnostic path observes
power rails against an internal reference; it does not replace the supervisors.

## Candidate and allocation

Use three ADS1119IPWR TSSOP-16 devices for the next design iteration. Nine rail
measurements fit three groups of three, leaving one unused analog input per ADC.
The reserved diagnostic bus is ESP32 GPIO14/SDA and GPIO21/SCL, module pins22/23.
Use only static address straps: 0x40 (A1/A0=GND/GND), 0x41 (GND/DVDD),
0x44 (DVDD/GND). These are seven-bit addresses. Do not assign designators or
alter allocation.json until the complete circuit is prepared and checked.

| Address | AIN0 | AIN1 | AIN2 |
| --- | --- | --- | --- |
| 0x40 | protected input, after reverse/transient protection | PRE_6V3 | main +3V3 |
| 0x41 | eMMC core 3.3 V | POD_5V_SENSOR | POD_5V_AUX |
| 0x44 | POD_WHEEL_FRONT_SUPPLY | POD_WHEEL_REAR_SUPPLY | POD_TIRE_SUPPLY |

Resolve exact input/core/aux net names against the native design before wiring.
Do not monitor raw connector battery voltage through an assumed protected node.

AVDD and DVDD would use main 3.3 V, each with local 100 nF decoupling. Grounds
join the board ground. Tie RESET to DVDD; use addressed software reset. Poll
status rather than consuming extra MCU pins for DRDY. Leave unused DRDY, AIN3,
REFP and REFN unconnected, following TI's unused-pin guidance. No external
reference is required. I2C pull-up values and bus capacitance remain to be bounded.

Relevant TSSOP physical pins: A0=1,A1=2,RESET=3,DGND=4,AGND=5,AIN3=6,
AIN2=7,REFN=8,REFP=9,AIN1=10,AIN0=11,AVDD=12,DVDD=13,DRDY=14,SDA=15,SCL=16.
This mapping must be independently checked against the emitted native symbol.

The exact captured TI sheet is SBAS925A (November2018), not its web crawl date.
It specifies -40..125 C operation and an internal nominal 2.048 V reference.
TSSOP reference initial accuracy is +/-0.15% at25 C, with30 ppm/C maximum
specified drift. This is compatible with the owner's temperature rule without
adding an exception. It does not establish an assembled thermal limit.

Live catalog capture on2026-10-20: TI ADS1119IPWR C701613 has5 units;
ADS1119IPW C5215179 has10; ADS1119IRTER C2670235 has52. All returned
assemblyComponentFlag=false. These are inventory observations, not assembly
approval or reserved stock. The zero-stock JLCPCB Assembly name duplicate is
not a TI substitution. TSSOP is preferred for the next circuit, but assembly
availability and exact binding are release holds. QFN has a different pinmap
and initial-reference specification; do not silently substitute it.

ADS7828 and ADS7828-Q1 were not selected: [TI product pages](https://www.ti.com/product/ADS7828-Q1) list -40..85 C,
outside the accepted exceptions. ADS7138-Q1 offers more channels per device,
but uses AVDD as reference and also has supply-relative input absolute limits;
it does not by itself solve independent rail measurement or powered-off inputs.
The captured ADS7138 sheet is retained only as comparison evidence.

## Attenuation instead of an unbounded power-off clamp

A normal divider that presents1-2 V to an ADC violates its AVDD+0.3 V absolute
input limit when main power is absent. Merely limiting current does not prove
that voltage limit. For this candidate, deliberately use a large attenuation:
three499 kohm upper resistors in series and a4.99 kohm lower resistor, giving
301:1 nominal. Add100 nF from the ADC pin to ground. Proposed resistor limits
are0.1% initial,25 ppm/C; actual MPNs, pulse ratings, aging and capacitor effective
value remain unselected. No clamp diode is credited.

The calculation assumes each monitored node is bounded to +/-60 V relative to
local ADC ground, including when main power is zero. This is an engineering
analysis envelope, NOT a new owner requirement or an assertion that the current
power protection bounds automotive transients to60 V. That upstream envelope
must be demonstrated or the attenuation reconsidered. Normal measurement is
for positive rails; a large negative fault is outside ADC recommended operation.

At the temperature/tolerance corners in calculations.json, a60 V node produces
less than0.201 V at an unloaded ADC input, leaving about99 mV to the +/-0.3 V
absolute limits even with AVDD=0. Each upper resistor sees approximately20 V.
The lower resistance also provides a ground return while the ADC is unpowered.
This removes the simple DC dependence on AVDD in the passive model. It does
NOT prove powered-off ADC leakage, internal clamping current, parasitic coupling,
ground shift, resistor faults, capacitor faults or transient survival. In
particular, the ADC sheet does not bound powered-off analog input leakage:
measure or obtain a bound before claiming freedom from rail back-powering.
With approximately5 kohm source resistance, an unmodeled20 uA pin current
could consume roughly100 mV of voltage margin. Do not substitute the powered
ADC's typical5 nA input current for a powered-off leakage maximum.

The passive RC model cannot overshoot the bounded input's extrema from an
initial state inside the same bounds; a real harness/PCB has parasitics outside
that model. A100 nF capacitor gives about0.497 ms nominal time constant. Allow
settling after turn-on, rail steps and changes in validity. The ADC's single-cycle
digital settling does not remove this analog delay.

Use gain4, internal reference, single-ended channels: full scale +/-0.512 V,
15.625 uV nominal per code. Referred to the rail, one code is4.703125 mV.
Nominal3.3 V gives about702 codes,5 V about1063 and6.3 V about1340. This is
useful for gross rail diagnostics despite using only part of the converter's
range. It is not a precision acceptance instrument for the5 V +/-1% requirement.

Initial ratio tolerance plus opposing25 ppm/C drift can contribute about0.70%
at125 C. For reference screening, initial error plus30 ppm/C over the full
165 C operating span gives0.645%. This assumes a full-range box interpretation,
not a30 ppm/C pointwise slope from25 C. TI explains the general distinction in
[its voltage-reference guide](https://www.ti.com/lit/an/slyt183/slyt183.pdf);
the ADS1119 sheet does not explicitly define its drift method, so this allowance
is conditional and is not a guaranteed complete reference bound. The resulting
scale budget already exceeds1%, before ADC error,
leakage, aging and noise. Input-current and several ADC error entries are typical,
not maximum. Do not turn the illustrative typical noise or gain error into a
guaranteed error budget. Calibration may improve observations but does not
establish temperature/fault bounds by itself.

## Acquisition and validity contract

Start with a10 ms diagnostic frame at400 kHz I2C, three sequential channels per
ADC, with the three ADC conversions overlapped in each round. This is a scheduling
target to validate under storage/radio load, not a proven driver latency.

For channels0/1/2, configuration bytes are0x7C/0x9C/0xBC: single-ended, gain4,
1000-SPS setting, single-shot, internal reference. Read back configuration before
accepting its result. WREG is0x40, START/SYNC0x08, RDATA0x10; configuration read
uses RREG0x20, status read RREG0x24. Status bit7 is1 when a NEW result is ready;
this has opposite polarity to the physical active-low DRDY pin. Read signed
16-bit output; do not reinterpret negative codes as a large unsigned voltage.

The slow-clock single-shot conversion bound from1061 cycles and-2% oscillator
error is1.0573 ms, excluding commands and host scheduling. Nine transactions
sets, each WREG27+readback36+START18+status36+RDATA45=162 SCL clocks, take
3.645 ms at400 kHz. Three overlapped conversion rounds add3.172 ms. The resulting
6.817 ms ideal schedule leaves about3.18 ms of the10 ms target for bus conditions,
software and RC/initial settling policy. This is not a system worst-case proof.

Wait for power stabilization and the documented approximately500 us POR time,
then reset/configure/read back every device. Treat500 us as approximate, not a
specified maximum. Do not broadcast I2C general-call reset on a shared bus.
Only one outstanding single-shot request per ADC is allowed; retain its channel,
configuration and start timestamp. After a timeout/reset/configuration mismatch,
invalidate the pending result before starting another conversion. A late result
must never be assigned to the next channel.

Each sample record must contain rail identity, raw code, conversion interval,
configuration, validity and calibration version. Any missing ADC, I2C failure,
stale result, timeout, invalid power state or uncertain channel association means
UNKNOWN/INVALID, never zero volts or last-value-as-current. Require fresh results
after recovery. Preserve hardware supervisor events independently of this scan.

A finite scan can miss a brief dip between readings. Do not claim continuously
valid wheel/tire supply or use polling as immediate fault protection. Sensor
readings within an uncertain power interval must remain flagged; a verified
hardware fault latch or a separately justified timing/error policy is needed to
make stronger guarantees. ADC readings cannot rescue measurements after the
MCU or its supply has failed.

## Next executable work

Resolve assembly supply and passive bindings; independently review attenuation,
error and scan calculations; define measured-node transient envelopes; prepare
three ADCs and nine dividers in the intent; then check native pin maps and ERC
when AGENTEE-288 is released. Qualify power-off leakage, input settling, effective
capacitance, full-temperature errors and bus recovery on the assembled design.
This study leaves wheel negative-transient protection and input-power qualification
open. It does not grant a fabrication release.

Evidence: local PDFs/text and request responses are hash-pinned in sources.json.
Run `python3 calculate.py` to reproduce arithmetic and verify captured hashes.
