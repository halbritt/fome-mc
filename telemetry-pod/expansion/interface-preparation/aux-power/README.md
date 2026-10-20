# Protected auxiliary supply and ninth rail monitor

Prepared candidate, not a released or hardware-qualified supply. U30 TPS26625DRCR
feeds POD_5V_AUX from POD_5V_SENSOR. This preserves the relationship to the
sensor rail used to derive SENSOR_REF_2V5; it does not introduce an independent
nominal5 V regulator. Protection-switch and harness drops must still be included
in each sensor's ratiometric error/calibration treatment.

J1 pin21 is auxiliary power and pin22 is ground. U28 AIN2/pin7 now measures the
auxiliary branch through the same301:1 divider and100 nF filter as the other
eight diagnostics. Firmware may include configuration0xBC for U28 only when
using this candidate. The earlier diagnostic-circuit snapshot correctly leaves
this channel NC. Native emission, ERC and component assembly bindings are pending.

## Circuit

U30 reuses the previously reviewed TPS26625 symbol and candidate DRC footprint.
IN1 connects to POD_5V_SENSOR; OUT10 to POD_5V_AUX; GND6 to system ground.
RTN5 and exposed pad11 share a new isolated SENSOR_POWER_AUX_RTN net. They
must not join ground or another protection branch's RTN. SHDN4 and FLT9 remain
NC. The moving RTN reference forbids a direct FLT-to-MCU connection.

| Component | Value | Connection |
| --- | --- | --- |
| R162 |1.05 Mohm0.1%,25ppm/K| sensor5V to UVLO2 |
| R163 |95.3 kohm0.1%,25ppm/K| UVLO2 to OVP3 |
| R164 |287 kohm0.1%,25ppm/K| OVP3 to RTN |
| R165 |44.2 kohm0.1%,25ppm/K| ILIM7 to RTN |
| C124 |1uF50V X7R0805| input to GND |
| C125 |100nF50V X7R0603| output to GND |
| C126 |10nF50V C0G10%0603| dVdT8 to RTN |
| R166/R167/R168 |499 kohm0.1%,25ppm/C each| three series upper diagnostic resistors |
| R169 |4.99 kohm0.1%,25ppm/C| diagnostic input to GND |
| C127 |100nF50V X7R0603| diagnostic input to GND |

The5 V ladder intentionally differs from the6.3 V wheel/tire ladder. Keep the
upper resistor above TI's1 Mohm minimum through tolerance and temperature so
its documented current-limited UVLO connection can be used during a negative
RTN excursion. The OVP tap still requires the conditional clamp analysis and
actual fault-waveform validation; a DC corner calculation is not surge protection.
Independent threshold/leakage corners for the proposed0.1%/25ppm resistors
(combined adverse0.35% through125 C) give the following static planning values:

| Transition | Minimum | Maximum |
| --- | ---: | ---: |
| UVLO re-enable |4.2151 V|4.8164 V|
| UVLO disable |3.8797 V|4.4587 V|
| OVP cutoff |5.6373 V|6.3932 V|
| OVP recovery |5.1906 V|5.9164 V|

The assumed4.95–5.05 V source range lies inside the static start/recovery window.
The wide trip bands do not enforce5 V +/-1%; operation during droop is invalid
before these switches necessarily trip. Published timing and these threshold
models do not bound transient overshoot. Aging, contamination and application
conditions remain to be included. See the retained independent corner calculation.

Input/output capacitors must remain nonpolar and meet effective-capacitance and
pulse-voltage limits. The inherited DRC land geometry remains unqualified.

## Accuracy and usable load

The152 mA nominal current-limit setting is a protection setting, not a promise
of5.00 V +/-1% at that load. Published current-limit endpoints apply under the
sheet's24 V input/1 V drop conditions. Their applicability to this5 V branch,
startup, current limiting and retry must be verified. Upstream U6 supplies both
original sensors and this branch; a branch fault can disturb the original rail
if U6's current/thermal capability is exhausted. Independent fault containment
has not been proved.

The TPS26625 full-temperature0.8 ohm maximum RON entry has stated test conditions,
including24 V input,7.5 kohm ILIM resistor and at least25 mA load. Use it only as
a planning value here, not a newly guaranteed5 V/44.2 kohm/low-load bound.
At25 mA it would drop20 mV; at40 mA,32 mV; at150 mA,120 mV.

The upstream U11 is **REF5050AIDR, standard grade**. It is not the higher-accuracy
REF5050IDR. Captured TI SBOS410O specifies0.1% initial accuracy and8ppm/C
full-range box drift for the standard grade. Across-40..125 C these two terms
alone give11.6 mV of5 V uncertainty. U6 TPS7B4253-Q1 contributes a specified
+/-4 mV tracking term under its stated conditions, including VADJ<VIN-1 V.
The resulting15.6 mV static screening allowance excludes further line/load
terms, noise, thermal hysteresis, solder shift, aging and actual operating limits.
It is not a complete sensor-supply error bound.

If the source minimum were4.9844 V and the switch were bounded to0.8 ohm in
this application,25 mA would leave14.4 mV for all remaining errors and wiring
before crossing4.95 V. At40 mA only2.4 mV remains. These are conditional
examples, not qualified load ratings or new owner requirements. A useful general
acceptance condition is:

`I_aux * R_switch_max + connector/cable_drop <= V_sensor_min - 4.95 V`

Use actual qualified bounds and include all branch loads, thermistor pull-ups,
monitor current, inrush and leakage. If only the existing5 V +/-1% source limit
is known, V_sensor_min=4.95 V leaves no series-drop allowance. Before assigning
an operational load rating, establish a tighter upstream bound and application
RON bound, or redesign the protection/reference arrangement. Do not relax the
owner's supply accuracy requirement or treat calibration as evidence of supply
compliance. No selected external sensor configuration is qualified yet.

The ninth diagnostic observes gross rail behavior. Its own error/settling limits
do not certify the +/-1% supply requirement or repair ratiometric errors. Optional
thermistor pull-ups still need values, calibration and verified DNP handling; they
are not added by this change.

## Evidence and verification

The [sensor-power review](../sensor-power/review/independent-review.md) retains
TPS26625 pinning, RTN, reverse-fault and transient constraints. New primary
reference/LDO sources and exact hashes are in sources.json. The auxiliary review
adds its ladder/error calculations and graph verification. All previous wheel,
CAN, storage and diagnostic qualification holds remain.

There are13 new components. Only three old NC assignments change: J1 pin21,
J1 pin22 and U28 pin7. U30 adds two NC assignments. Every prior component and
existing net terminal is preserved. Donor assembly bindings are removed from
new parts rather than inherited as approval.

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 prepare.py \
  --base ../diagnostic-circuit/inputs --out /absolute/fresh-inputs
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 verify.py
```

Prepared graph checks and byte reproduction do not establish native ERC,
assembly availability, actual supply accuracy, transient survival or fabrication
readiness. Regenerate native artifacts after the released emitter/JP1 support,
then verify the expanded contract and continue physical placement and routing.
