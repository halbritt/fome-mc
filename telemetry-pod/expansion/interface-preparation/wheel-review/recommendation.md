# Two-channel Hall conditioner: independent pre-emission recommendation

Recommend **LM2903BQDRQ1 on PRE_6V3**, with divided/filtered inputs and 3.3 V open-collector outputs, as the next circuit candidate. This is Hall-only. GPIO1/module39 and GPIO2/module38 are the proposed outputs; native graph preservation must still be checked. Exact diode/passive bindings and fault testing remain open. Do not emit this as a fully qualified sensor interface.

## Why this comparator

TI LM2903B-Q1 primary source SLCS141M, sections 2.2, 2.5 and 2.8: input pins allow -0.3 to +38 V absolute independently of supply; full-temperature common-mode limit is VCC-2 V; output low maximum is 550 mV at sink current ≤4 mA and stated -1 V differential overdrive. Full-temperature offset is ±4 mV, input bias ≤50 nA. Grade 1 is -40 to +125 C. Use the **B** variant, not legacy LM2903. SOIC-8 pin map: OUT1=1, IN1-=2, IN1+=3, GND=4, IN2+=5, IN2-=6, OUT2=7, VCC=8. Verify exact MPN availability separately.

Power from unswitched PRE_6V3 with 100 nF at pins8/4 and a nearby 1 uF. Sensor power is separately switched/protected; switching a sensor off must not remove comparator supply. The normal signal divider places both inputs well below PRE_6V3-2 V. Main 3.3 V power is not recommended for this comparator: its guaranteed common-mode ceiling would be only about1.2 V, unnecessarily restricting the interface. During severe PRE undervoltage, wheel measurements are invalid.

TI TLV1702-Q1 SLOS890C sections7.1/7.5 offers rail-to-rail input but has input absolute voltage tied to its supply and max output low900 mV at the stated test load. That alone cannot prove an ESP input low below about800 mV on a3.201 V rail. A lighter pull-up may work typically but is not a guaranteed fix from that table. LM2903B's550 mV limit provides a better direct logic margin, subject to its stated overdrive. Both comparator propagation delays are characterized typical values, not guaranteed worst-case15 kHz timing bounds.

## Concrete per-channel candidate

One low-leakage series dual diode, e.g. **BAV199**, can serve both isolation functions. This specific diode is a catalog candidate, not AEC-qualified; BAV199-Q would need its exact source and stock verification. Pin1=A1, pin3=K1/A2, pin2=K2. Connect:

- Protected switched6.3 V sensor supply → two series620 ohm resistors → diode pin1.
- Diode pin3 → external Hall output line and connector protection.
- Diode pin2 →10.0 kohm0.1% → comparator inverting input.
- Inverting input →10.0 kohm0.1% to ground, and220 pF C0G to ground.
- Comparator noninverting input →56.0 kohm0.1% to main3.3 V;10.0 kohm0.1% to ground;100 kohm0.1% to its own output.
- Comparator output →4.70 kohm1% to main3.3 V; then100 ohm series to its assigned ESP GPIO. Do not add a large output capacitor.

The first diode prevents a positive output-line short from charging the switched sensor supply through the pull-up. The second diode blocks negative line faults from the comparator divider. This changes the literal ZF resistor-to-VCC pull-up into a diode-isolated pull-up: its added drop and resulting rise-time/load must be accepted for the exact sensor. Do not call it the manufacturer's validated application circuit. If that change is rejected, use a reverse-current-blocked per-channel pull-up source or redesign the protection; a plain resistor permits rail backfeed.

For connector protection, a second PESD2CANFD24V-T device can protect the two wheel signal lines: pads1/2 to signals, pad3 to protection ground. Its42 V max clamp is specified at1 A8/20 us and25 C, not a general hot surge guarantee. The divider approximately halves a positive clamp excursion; a negative excursion is blocked by the series diode. Keep external-discharge return separate from sensitive threshold/ADC return routing until joining the board ground structure. This is a proposed topology, not an IEC/ISO pulse qualification.

## Thresholds and bandwidth

The comparator is inverting: line high produces MCU low; account for this in edge counting. Positive feedback provides hysteresis. The high-state feedback calculation includes loading of the4.7 kohm output pull-up; it must not assume an ideal3.3 V output source.

`calculations.json` enumerates initial resistor tolerances,3.3 V±3%, output low0–550 mV, and an illustrative combined±5 mV input-error allowance. Calculated line thresholds **excluding the input diode's forward drop** are falling0.882–1.048 V and rising1.364–1.476 V. Add the actual diode forward voltage at the divider current and temperature. Thus nominal switching is roughly around1.5–2.1 V at the connector, not a guaranteed fixed voltage band. Minimum corner hysteresis before diode effects is about315 mV. Exact diode forward behavior, sensor VOL and line leakage still need inclusion in the acceptance calculation.

The220 pF filter with10k/10k has about1.1 us rising time constant and up to2.2 us falling time constant when the series diode stops conducting, corresponding to about145/72 kHz poles. At15 kHz the period is66.7 us; this modest filter should preserve ordinary50% duty pulses. It does not prove capture of arbitrary narrow pulses. Cable capacitance adds a separate rise delay through the approximately1.24k pull-up, and diode recovery/comparator delay introduce further distortion. Bound minimum high/low time from the actual sensor/ring geometry; validate at15 kHz with worst harness, temperature and voltage. Firmware glitch rejection must be short enough to preserve that measured pulse width.

## Fault and powered-off limits

A positive steady signal short up to24 V reverse-biases the supply-isolation diode and produces less than12 V at the comparator input. It is within the comparator's supply-independent absolute input rating; the valid reference input stays in common-mode. Each10k divider resistor dissipates roughly14 mW at24 V or44 mW for a42 V clamp, before tolerances. Select voltage and pulse ratings explicitly. The exact shorted sensor's output transistor may not survive a direct battery short; board input survival is not sensor survival.

A negative signal short is blocked from the comparator, but current still flows from sensor supply through the pull-up resistors and first diode. **This is a material thermal requirement.** At6.3 V supply and -16 V line, conservatively ignoring diode drop, current is18.0 mA and each620 ohm resistor dissipates0.20 W. At-24 V it is24.4 mA and0.37 W per resistor. Choose resistor parts retaining at least0.4 W dissipation capability at the actual hot ambient if continuous±24 V signal shorts are required. A nominal1 W or2 W marking alone is insufficient without the temperature derating curve. The common TPS1H200 supply switch may not trip for this small added current. If that footprint/heat is unacceptable, add per-channel current-limited pull-up circuitry or narrow the continuous reverse-fault requirement explicitly; do not silently rely on the shared supply switch.

With board power off and a positive externally driven line, the diode/divider routes current to ground without a deliberate3.3 V or6.3 V clamp path. LM2903B input/output absolute limits are independent of supply, so this is preferable to TLV1702's supply clamp. Nevertheless unpowered output state/leakage and device cross-coupling are not specified as a functioning pulse receiver. The MCU must ignore outputs when board or sensor power is invalid. Negative-fault steady leakage through a low-leakage diode is small; fast capacitively coupled/recovery transients still require measurement to ensure comparator pins never cross-0.3 V. Do not use the-50 mA absolute current entry as permission to violate that voltage limit.

The captured ZF GS1005–GS1007 sheet gives5–24 V supply,6 mA maximum sensor current,20 mA output sink maximum and15 kHz sensing, but does **not** specify worst-case output saturation voltage, pulse widths, powered-off output leakage or output short-to-battery survival. Those missing endpoints prevent a fully guaranteed end-to-end claim from these documents alone. Two sensors need at least12 mA operating current plus their pull-up currents and switch overhead. Prove protected supply minimum at the sensor is≥5 V after switch, diode-free sensor supply path, harness and tolerance losses. The proposed diode is in the output pull-up path, not in the sensor power feed.

## Primary evidence and capture scope

- `lm2903b-q1.pdf/.txt`: https://www.ti.com/lit/ds/symlink/lm2903b-q1.pdf (SLCS141M).
- `tlv1702-q1.pdf/.txt`: https://www.ti.com/lit/ds/symlink/tlv1702-q1.pdf (SLOS890C).
- Existing `../../sources/GS1005-GS1007.pdf`, manufacturer ZF, updated2024-09-11.
- Existing `../sources/pesd2canfd24v-t.pdf`, Nexperia.
- Nexperia BAV199,1 April2023, primary PDF read via web tool because direct capture returned403: https://assets.nexperia.com/documents/data-sheet/BAV199.pdf?hkey=EF798316E3902B6ED9A73243A3159BB0 . Pages1–3 specify series topology/pinmap,75 V continuous reverse,150 C ambient,80 nA maximum reverse leakage at75 V/150 C, maximum3 us reverse recovery under stated25 C test. Forward-voltage maxima are specified at25 C; none is a guaranteed cold/hot bound. Exact automotive substitute remains open.
- TI negative-input explanation: https://www.ti.com/document-viewer/lit/html/SSZT104/GUID-FB5C9E6E-A8A5-41B8-966C-5D99713A85BD . Do not treat input-current limitation alone as compliance with the-0.3 V input limit.

No ring mechanics, VR support, pulse accuracy, sensor qualification, component purchase or production acceptance is implied.
