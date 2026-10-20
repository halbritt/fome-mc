# Optional auxiliary thermistor excitation

Prepared circuit for all four auxiliary analog inputs. This adds19 components
to the integrated expanded source. It does not replace the native pod project,
qualify a thermistor, or close the emitter, assembly, layout or hardware gates.
The accepted goal remains eight0–5V analog channels with optional thermistor
pull-ups; each jumper defaults open so the voltage-input configuration is retained.

## Circuit and configuration

The excitation comes from **POD_5V_AUX**, downstream of U30, as required. D105
uses one diode of BAV199,215 to isolate reverse current. Two200ohm bias resistors
feed a TL431BQDBZR with REF tied to cathode for nominal2.495V excitation.
The shunt provides a current sink when an external analog input is shorted to a
positive supply. Direct5V pull-ups would instead feed fault current into the
shared auxiliary supply. This separate excitation is **not ratiometric** to the
MCP3208 reference; firmware must use calibration and a valid excitation estimate.
It does not change the separate5V sensor-supply accuracy requirement.

| Parts | Connection / purpose |
| --- | --- |
| D105 BAV199,215 | pin1/anode to AUX5V; pin3/K1-A2 to bias input; unused pin2/K2 NC |
| R174/R175 | two200ohm,1%,100ppm/K CRCW2512-HP e3,1.5W at70°C, in series |
| U31 TL431BQDBZR | DBZ/SOT-23: pins1/K and2/REF to excitation; pin3/A to GND |
| C128 |10uF16V X7R1206 across excitation; effective capacitance/ESR/stability pending |
| R170–R173 |10kohm0.1%,25ppm/K pull-up, one per auxiliary input |
| JP2–JP5 | open copper jumpers between each pull-up and AUX1–AUX4 respectively |
| R180 |100kohm1%,100ppm/K AUX5V-to-ground bleed for static reverse leakage |
| R176–R179/C129 |3×499kohm +4.99kohm,0.1%,25ppm/K,100nF diagnostic filter to U28 AIN3/pin6 |

Close only the jumper for an installed passive thermistor. Record its physical
jumper state, sensor identity and calibration in the channel configuration.
Firmware cannot enable a copper jumper. An active0–5V sensor requires that
channel's jumper open. JP2–JP5 inherit JP1's copper-only assembly policy; the
released emitter/fabrication support is still required. They are not fabricated
resistor parts or DNP pseudo-parts. New parts have no invented or copied donor
assembly bindings. The exact bias-resistor ordering candidate is
CRCW2512200RFKEGHP (200R,1%,100ppm/K,EG packaging,HP series); stock, assembly
availability, land pattern and exact bindings are still to verify.

All prior circuit terminals are preserved except U28 pin6's former NC. The
reviewed connector assets remain included. `prepare.py` calls the existing
integration entry point, then adds this circuit. The earlier integration receipt
is renamed `pre-thermistor-integration-receipt.json` because its output hashes
describe the baseline, not this new graph. `verify.py` verifies the final snapshot.

## Current and thermal budget

`calculate.py` retains reproducible **conditional DC screening**, not a fault
survival certificate. It uses an excitation planning range2.4–2.586V, bias
resistor tolerance plus TCR of±2.313% through155°C film temperature, and±0.425325%
for the10k pull-ups through155°C. These symmetric bounds multiply initial
tolerance and temperature factors, then apply the larger excursion to both
sides. Aging is excluded. The excitation envelope
screens initial reference error,34mV temperature deviation and current-related
change; the datasheet's dynamic-impedance row is at25°C and does not establish
that envelope across all current/temperature combinations.

With AUX at4.95V, four grounded inputs, excitation at2.586V and diode drop
at most1.5V, at least1.07062mA remains in the shunt after the diagnostic load.
This clears the recommended1mA minimum. The computed forward-drop ceiling is
1.52890V. **BAV199's forward limits are specified at25°C, so≤1.5V at the cold
operating current remains a characterization requirement.** This is not a newly
claimed datasheet guarantee. Use the recommended1mA, not the25°C0.7mA Imin
entry, for this budget.

The simultaneous-fault cases below drive AUX power and all four auxiliary signal
pins to the stated voltage. They conservatively use zero forward drop and do
not credit the diagnostic load's small reduction in shunt current.

| Conditional case | Maximum shunt current | Maximum shunt power | Each bias resistor | Each pull-up |
| --- | ---: | ---: | ---: | ---: |
|16V |40.268mA |102.71mW |236.67mW |18.58mW |
|24V stress screen |63.955mA |163.96mW |597.01mW |46.86mW |

Both currents are below the plain TL431's100mA recommended ceiling. The
similarly named **TL431LI and ATL431LI are15mA devices** and cannot be silently
substituted. LM4040+330ohm was also rejected for the larger AUX power-pin fault
case; a normal5V-only budget does not cover that fault. TMUX1072 was considered,
but its11.5uA worst-case on leakage,5.55–6V trip band and stated9.6V transient
pass-through require additional treatment. ADG4612's85°C specification would
need an additional owner exception, so it is not selected.

The HP resistors have a1.5W P70 rating, not the ordinary CRCW2512's1W.
A linear70–155°C ambient derating screen gives0.882W at105°C and0.529W
at125°C. The24V screen therefore fails at125°C local ambient. The TL431's
206K/W datasheet-board thermal resistance would imply a33.8°C rise at the
24V corner, before neighboring heating. Neither this thermal model nor the
resistor rating proves the actual board's thermal performance. Validate combined
heating, film temperature, creepage, harness and capacitor stress. The24V case
is an additional design stress screen, not an owner requirement or proof that
the rest of the pod survives24V on these pins.

R180 gives static leakage a defined sink. For illustration,80nA into100kohm
is8mV; BAV199 specifies that leakage limit at its stated150°C/75V condition.
It is not a no-backfeed proof: reverse recovery, displacement current, floating
rails and power sequencing need waveform validation. C128's effective C and ESR
must be verified against the shunt stability region across temperature and bias.
A nominal10uF is not that verification. Native ERC cannot close these holds.

## Conversion and fault interpretation

The existing ADC-side divider is10k+10k, so it presents **20kohm in parallel
with the thermistor**. Let `V` be the external signal voltage recovered from the
buffer/ADC reading, `E` the excitation voltage, `Rp` the pull-up resistance and
`RL` the total divider resistance. Then:

`Rtherm = 1 / ((E - V)/(V * Rp) - 1/RL)`

Nominally `V = 2 * Vadc`, `Rp = 10k`, `RL = 20k`. Use calibrated values and
include buffer, ADC and reference errors. A10k sensor produces0.998V at the
connector and0.499V at the buffer. Ignoring the20k load would report6.667k,
not10k. The included calculation checks the inverse against KCL; it is a design
model, not production logging firmware.

A disconnected sensor approaches1.6633V at the connector, not5V; a short
approaches0V. Establish open/short thresholds with actual sensor-range, cable,
resistor and measurement-error bounds. A voltage at/above the loaded open limit
must not be converted into a negative or enormous temperature. A reading above
that limit can also mean an externally driven input, wrong jumper configuration,
reference failure or a fault. Reject invalid excitation, ADC saturation, unsettled
samples and stale diagnostics. Do not guess a thermistor beta or temperature
accuracy: no external sensor is selected yet.

The nominal maximum thermistor power over all positive resistances is0.10375mW,
at6.667k. Actual self-heating in degrees depends on the selected sensor and its
mounting medium. Lead/return resistance and ground offset also require treatment.
At100ohm the ideal ADC reading is only20.14 counts, versus817.56 at10k;
this10k pull-up does not promise useful resolution for every thermistor or range.

The100nF analog input filter has an open-sensor pole of0.667ms nominal. A
conservative full-scale step takes6.007ms to settle within half a12-bit code,
which exceeds one5ms sample interval. Continue sampling at200Hz but mark
post-switch/startup/fault-recovery values invalid until the measured excitation
and analog path have settled. Include capacitance/tolerance and actual buffer
settling in that policy. No anti-aliasing or rapid-step accuracy claim is made.

U28 AIN3 adds a tenth diagnostic. Its single-ended gain4 configuration is0xDC;
read back the configuration and honor ready/status, timestamps and deadlines.
The nominal excitation resolution is4.703125mV per code, approximately0.1885%
of2.495V. ADC/reference/divider errors add to this quantization; the monitor
alone does not establish temperature accuracy. Ten conversions over four
rounds take8.279ms in the same ideal400kHz schedule model, leaving only1.721ms
of a10ms frame for unmodeled latency. Validate the actual schedule and settling,
or lower the diagnostic rate while retaining the required analog sample rate.

## Verification and next step

Primary datasheets, capture hashes and source calculations are retained here.
The BAV199 primary capture is the exact previously reviewed1September2020 version;
its source URL may now serve a newer revision. The independent review checks
pin mapping, graph preservation, source reproduction and adversarial changes.
These checks do not establish native ERC, routing, assembly availability or
physical qualification. No doctrine-backed hardware acceptance is claimed.

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 verify.py
python3 prepare.py --out /absolute/fresh-inputs
```

This is the next source preparation entry point, superseding plain integration
for the expanded candidate. Once the emitter/private-property and copper-jumper
fixes are released, generate the fresh native schematic, check graph/ERC and
bindings, and carry this circuit through placement, routing and independent
review. Cold drop, reverse transients, shunt stability, thermal coupling and
sensor calibration remain explicit hardware gates.
