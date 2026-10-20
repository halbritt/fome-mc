# Independent TPS26625 sensor-power circuit review

## Disposition

TPS26625 is a credible three-branch candidate, but **reject direct MCU connection to FLT and reject ordinary low-voltage dividers without reverse-fault analysis**. Use independent RTN islands, FLT NC and SHDN open. The parent's revised shared resistor ladder below is a defensible static candidate using TI's documented UVLO current-limited connection. Preserve its narrow recovery margin and the unresolved transient/sensor-voltage limits. No assembly availability or hardware acceptance follows from this review.

Source: captured TPS2662 SLVSDT4F, December2021; sections6,7,9.3–9.4,10.4,12 and DRC0010J drawing. Device comparison confirms TPS26625 is the adjustable overvoltage-cutoff, auto-retry version with both input and output reverse-polarity protection.

## Exact circuit and pinning

Each DRC10 device: IN1 to PRE_6V3; UVLO2 to upper ladder tap; OVP3 to lower ladder tap; SHDN4 NC; RTN5 to its own isolated reference island; GND6 to system ground; ILIM7 through selected resistor to RTN; dVdT8 through capacitor to RTN; FLT9 NC; OUT10 to its individual sensor branch. Exposed pad11 belongs to **RTN**, not GND. Connect pin5 electrically; EP is not its only connection. Three RTN islands must not be joined to each other or to ground, main3.3 V or sensor returns. Sensor returns remain system ground.

DRC0010J drawing confirms EP1.65×2.4 mm,0.5 mm lead pitch, example lead lands0.6×0.24 mm, centers across rows2.8 mm. Compare actual installed footprint to the complete drawing; pin count and EP size alone are not final footprint verification. Add1 uF nonpolar ceramic input bypass from IN to system ground per branch. Use at least100 nF nonpolar ceramic from OUT to system ground, sized/rated for externally imposed±24 V and transients;50 V MLCC is a candidate voltage rating, with actual effective capacitance checked. Do not put a polarized output capacitor on a line that can be driven negative. IN and OUT require at least0.01 uF effective capacitance per recommended conditions.

SHDN has an internal pull-up and a specified open-output voltage2.39–3.1 V at the stated0.1 uA loading. Leaving it open is consistent with automatic enable. Do not tie it to main3.3 V because its reference moves with RTN. Future remote control requires isolation or a fully analyzed negative-domain interface.

## Reverse-output and FLT constraints

Absolute limits require OUT−RTN≥−0.3 V. Therefore an allowed-24 V output fault implies RTN may move near-24 V; it cannot be treated as ground. This conclusion is also consistent with the protected reference architecture. OUT minimum is−(60−VIN): atVIN6.5 V the limit is−53.5 V, so−24 V is within the voltage envelope. AtVIN0 the limit is−60 V. PositiveOUT24 V also fits the62 V output and±IN−OUT limits; atVIN0 the difference is−24 V. These are absolute constraints, not guaranteed functional performance across every transient.

FLT's sink is referenced to the internal RTN domain. A direct pull-up/wire-OR to SENSOR_FAULT_N can drag that shared node negative during reverse faults. Leave FLT unconnected until an isolated interface is selected. No open-load detection appears in the fault list: UVLO, OVP, overload, reverse current, thermal shutdown, SHDN and startup report faults. Thus it avoids TPS1H200A's low-load false-open-load problem, but its moving reference prevents direct reuse of that diagnostic net. Fault startup assertion is expected; lack of an open-load detector does not imply the sensor is present.

## Shared ladder and clamp analysis

Use R1=1.05 Mohm from IN to UVLO, R2=68.1 kohm UVLO to OVP, R3=215 kohm OVP to RTN, initially0.1%,25 ppm/K. TI section9.3.1 explicitly allows≥1 Mohm from IN to UVLO when UVLO is unused, limiting current below60 uA at60 V; the block diagram shows the UVLO clamp. This supplies a documented current-limited pin connection, rather than an invented external zener rating. The shared ladder reduces UVLO injection further. At30.5 V total span and minimumR1=1.046325 Mohm, upper-resistor current is below29.15 uA even before subtracting clamp voltage.

If UVLO is held within its5 V absolute boundary by that documented clamp connection, OVP is at most3.809 V after ladder tolerance/TCR and worst100 nA OVP leakage, below its4 V recommended maximum. This is a DC circuit inference from TI's approved UVLO connection; the datasheet does not separately guarantee a detailed clamp voltage/current curve or layout-induced transient overshoot. Capture this condition and verify reverse-fault waveforms before release. Do not substitute a nominal1 Mohm resistor whose tolerance or temperature makes it less than TI's specified minimum.

With independent input leakages±100 nA, published threshold endpoints,0.1% resistors and25 ppm/K over25–125 C (combined adverse0.35%), exact ladder corner calculation gives:

| Transition | Minimum | Maximum |
|---|---:|---:|
| UVLO rising/re-enable |5.342 V|6.009 V|
| UVLO falling/disable |4.920 V|5.560 V|
| OVP rising/cutoff |7.058 V|7.889 V|
| OVP falling/re-enable |6.503 V|7.297 V|

UVLO maximum re-enable is below assumedPREminimum6.111 V by102 mV. OVP minimum re-enable is above assumedPREmaximum6.489 V by only13.9 mV. Static maximum cutoff is below8 V by111 mV. These margins do not include extra life drift, rail-reference offset, contamination or transient overshoot. In particular, no universal2% aging allowance fits here. Use exact resistor stability evidence or retune the ladder if that drift must be included. Full calculations and the older ladder's failed recovery margin are retained in ladder-corners.json.

The minimum falling UVLO is below5 V even before switch/cable drop. Therefore it **does not guarantee valid Hall supply until switch-off**. Mark wheel data invalid during supply sag using an explicitly selected voltage-monitoring path or revise the threshold architecture. Similarly, TI's OVP response4.84 us is typical, not a maximum; a7.889 V static cutoff does not guarantee that an8 V transient is never delivered to a tire sensor. Confirm actual sensor absolute limits rather than treating the conservative8 V target as a clamp specification.

## Current limit and startup

RILIM44.2 kohm gives published145/152/159 mA min/typ/max;26.7 kohm gives237/250/257 mA. Use one44.2k for each wheel branch and26.7k for the two-tire branch. With the same0.35% resistor allowance, approximate inverse-R bounds expand to144.49–159.56 mA and236.17–257.90 mA respectively. Preserve the table's statedVIN24 V, VIN−VOUT1 V test conditions; validate behavior at6.3 V rather than asserting these are measured application limits. Tire operating/inrush current remains to be bound against the minimum limit. These limits will not necessarily detect modest signal pull-up shorts; the resistor thermal design remains necessary.

Choose10 nF C0G,±10% or tighter, from dVdT8 to RTN. Its minimum9 nF exceeds the recommended6.8 nF. Nominal ramp time is20.5e3*6.3*10e-9=1.292 ms. Combining published charging-current/gain endpoints and9–11 nF gives about0.966–1.726 ms at6.3 V, excluding other startup delays. For1 uF output capacitance this corresponds to roughly3.65–6.52 mA capacitive inrush, to be added to load current. Larger remote sensor capacitance scales this current. FLT also remains low through gate enhancement; the nominal deglitch expression is750+573*C[nF], or6.48 ms for10 nF. Do not use ramp time alone as a data-valid timer.

The specified operating junction range is-40 to125 C, despite150 C absolute junction rating and155 C typical thermal shutdown. At105 C ambient only20 C remains to the specified junction ceiling. The table's maximumRON800 mohm is specified under its current/voltage conditions; it suggests~50 mW at250 mA before quiescent power, but is not a thermal model. Short circuits dissipate much more and invoke retry/thermal cycling. Verify all three branches together, source droop and RTN-island thermal paths. Protection recovery is not proof of continuous full-load operation during a fault.

No device purchase, native graph verification, hot fault test, EMC, sensor-mechanical or production acceptance is claimed.
