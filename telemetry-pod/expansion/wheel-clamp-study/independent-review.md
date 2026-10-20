# Independent source/algebra review

PASS as a source-supported next circuit experiment, not protection qualification. TI SNOAA35F section6.9.3.2.1 page21 describes splitting the upper resistor and clamping its intermediate node; section6.9.3.1 page20 warns that even a Schottky directly at the comparator input can exceed its negative limit. Primary text independently checked at https://www.ti.com/lit/an/snoaa35/snoaa35.pdf . No visual schematic review claimed.

For positive Ra,Rb,Rc and an unloaded comparator, G=Rc/(Ra+Rb+Rc), K=Rc/(Rb+Rc), and K-G=Rc*Ra/((Rb+Rc)*(Ra+Rb+Rc))>0. Thus preserving G=0.5 requires K>0.5: no positive Ra achieves K<0.5. The10k/30k/10k example gives G=0.2,K=0.25 and conditional input=-0.25V for an assumed1V clamp. JSON arithmetic is correct. The ratio alone does not establish a real diode bound, operating common-mode compliance or dynamic protection.

One useful quantitative caution for the next experiment: at a-24V source and1V clamp, Ra current is2.3mA and its dissipation52.9mW. Ideal clamp diode current is approximately2.3mA-1V/40k=2.275mA, before bias/leakage. TI recommends at most1mA for its simple direct-input clamp; that is not automatically a specified maximum for an external split-tap diode, but the proposed example must not be presented as following that simple-clamp current prescription. Select and bound the actual diode at its actual current/temperature.

The study appropriately leaves source impedance and BAV199 recovery, comparator bias, leakage, ground error, threshold/hysteresis redesign, RC timing, startup and transient overshoot unresolved. Negative absolute-rating protection would not by itself guarantee valid comparator behavior during the fault. No source/CAD/rules changed.

## Follow-up threshold/load algebra

Verified both threshold models independently and checked actual source pin topology: U26 pin2 receives filtered front input, pin3 threshold; rear6/5 likewise. With signal on the inverting input, a rising input starts with output high and switches at the high-feedback threshold; a falling input starts low and switches at the selected VOL threshold. The labels and switching direction are correct. Solving the high-state node with100k feedback plus4.7k pullup in series correctly includes loading; high output is not3.3V.

4k/12k/4k retains20k nominal DC load, gain0.2 and clamp ratio0.25. With3.43k threshold ground, falling thresholds rise by approximately0.694–0.759mV over the baseline at the three assumed VOL values, while rising threshold falls by1.927mV. Input Thevenin resistance falls from5k to3.2k;343.75pF preserves the ideal1.1us pole. This does not preserve complete fault/startup/diode dynamics.

At-24V and assumed1V clamp, first-resistor current is5.75mA and dissipation(23V)^2/4000=132.25mW. That exceeds the earlier ordinary0603 100mW-at70C family rating even before derating; this algebraic resistor must not inherit that package/rating selection. Ideal diode current is about5.6875mA after subtracting1V/16k. Exact parts, waveform duration, thermal conditions and clamp VF/leakage remain selection gates. No CAD or rules changed; no fault-survival or timing qualification.
