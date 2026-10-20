# Two Hall wheel-input channels

This prepared circuit adds U26, D102–D104, R110–R127 and C95–C98 to the protected
sensor-power candidate. It connects J1 signal pins24/27 to ESP32 module pins39/38
(GPIO1/2) through independent conditioning channels. It is not a verified native
schematic; emission remains pending AGENTEE-288.

U26 is LM2903BQDRQ1, powered from PRE_6V3. Each output pulls up to main 3.3 V.
D102/D103 are exact Nexperia BAV199,215 series dual-diode candidates; D104 is the
previously reviewed Nexperia PESD2CANFD24V-TR protection device. Similar catalog
names from other manufacturers are not approved substitutes. Exact part bindings
and assembly eligibility remain open.

| Function | Front | Rear |
| --- | --- | --- |
| Dual isolation diode | D102 | D103 |
| Two series 620 ohm pull-up resistors, 2512 | R110/R111 | R119/R120 |
| 10 kohm input / 10 kohm ground divider | R112/R113 | R121/R122 |
| 56 kohm to 3.3 V / 10 kohm ground / 100 kohm feedback | R114/R115/R116 | R123/R124/R125 |
| 4.7 kohm output pull-up / 100 ohm GPIO series | R117/R118 | R126/R127 |
| 220 pF input filter | C95 | C96 |
| U26 input-minus / input-plus / output | 2 / 3 / 1 | 6 / 5 / 7 |

Each pull-up starts at its corresponding protected wheel supply. Diode pin1
receives the pull-up; pin3 connects to the external signal; pin2 feeds the input
divider. The comparator is inverting. C97/C98 provide local 100 nF/1 uF bypass.
Existing ADC, CAN, storage and sensor-power components are preserved.

## Limits carried forward

The original [circuit review](../wheel-review/recommendation.md) and
[thermal follow-up](../wheel-thermal/README.md) provide the threshold and fault
calculations. Those calculations do not establish exact Hall compatibility:
GS100502 lacks guaranteed output-low voltage and minimum pulse widths in the
captured sheet. Ring geometry, cable capacitance, maximum edge rate and sensor
supply validity still need validation. This preparation does not select or
purchase a sensor or tone ring.

The [exact diode review](review/diode-fault-review.md) supports the static topology
but identifies a material dynamic hold. Diode2 reverse recovery and capacitance
can drive a comparator input below its -0.3 V limit. The 10 kohm resistor limits
current and the 220 pF capacitor slows the event; neither guarantees a voltage
clamp. Before release, either demonstrate acceptable pin waveforms across the
specified harness/fault/temperature envelope or add a bounded clamp design.
Do not describe this candidate as proven to survive negative transients.

Two simultaneous negative signal faults can dissipate about 1.57 W in the four
pull-up resistors, plus diode heat. Their assembled thermal path remains open.
The power branches do not necessarily trip on this smaller signal-fault current.
BAV199 diode forward-voltage and recovery specifications do not establish a
complete hot/cold dynamic model. The captured exact catalog-linked PDF is dated
2020; its automotive qualification language is not used as current qualification.

The comparator remains powered while individual sensor supplies are faulted or
retrying. Rail monitoring and firmware must invalidate wheel readings during
these intervals; that monitoring path is still to be implemented. GPIO output
logic is not a claim of valid speed during startup, brownouts or powered-off
external drive.

## Reproduce and check

From this directory, use a fresh output path:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 prepare.py \
  --base ../sensor-power/inputs --out /absolute/fresh-inputs
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 verify.py
```

The producer refuses an existing destination and parses its authored library.
Verification covers whole-library/footprint syntax, hashes, byte reproduction and
independent prepared-graph checks. It does not run native KiCad ERC or establish
layout, timing, thermal or fault-survival qualification. After the emitter fix,
regenerate from the reconciled sensor-power baseline and check the native result.
