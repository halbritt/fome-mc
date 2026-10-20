# Wheel input clamp: source-supported next experiment

TI SNOAA35F (December 2024), sections6.9.3.1–6.9.3.2.1, pages20–21, describes a split upper divider with a ground clamp at the intermediate tap. Primary source: https://www.ti.com/lit/an/snoaa35/snoaa35.pdf . Read via web text2026-10-20; no local PDF capture or visual schematic review claimed.

TI explicitly warns that even a Schottky at the comparator input can exceed its negative voltage limit. Thus the existing LM2903BQDRQ1 -0.3V hold remains valid; the -50mA absolute current rating does not resolve it. Datasheet SLCS141M page6 also explicitly prohibits more than0.3V negative input.

For topology source--Ra--clamp tap--Rb--comparator input--Rc--GND, normal unloaded gain is Rc/(Ra+Rb+Rc), while negative clamped input magnitude is Vf*Rc/(Rb+Rc). A positive Ra makes the clamp attenuation ratio greater than normal signal gain. Our current 10k/10k divider gain0.5 therefore cannot be preserved while achieving a clamp attenuation below0.5 in this passive topology. A lower signal gain implies a coordinated comparator threshold/hysteresis revision, rather than adding a diode without checking signal behavior.

Exploratory values Ra=10k,Rb=30k,Rc=10k give normal gain0.2 and clamp ratio0.25. A hypothetical qualified1.0V maximum clamp drop would produce -0.25V nominal, before resistor tolerances, input bias, ground displacement, dynamic overshoot and parasitics. This is an algebraic example, not a selected clamp or approved circuit. Resistor/current/power bounds must include the actual negative waveform; current through Ra is approximately(|Vfault|-Vf)/Ra, and must meet selected diode limits. The inherited BAV199 isolation diode and its recovery cannot be ignored.

Next experiment: derive threshold/hysteresis network values to preserve connector switching levels at gain0.2; identify an exact clamp with usable full-temperature bounds; evaluate timing/pulse width, diode leakage, power-off, ±24V faults and transient behavior. Do not modify native circuit or close qualification from this example.

## Nominal threshold-preservation experiment

thresholds.py/thresholds.json compare the actual56k/10k/100k hysteresis network and4.7k output pull-up with an algebraic4k/12k/4k split input divider,3.43k threshold-ground resistor and343.75pF input capacitor. Values are unselected. Total DC input resistance stays20k; gain drops0.5 to0.2; ideal filter time constant remains1.1us. The calculation includes high-state loading through the feedback branch (output voltage is not simply3.3V). Falling thresholds for assumed VOL0/.11/.55V change by about0.7mV after the isolation diode; the rising threshold changes by about-1.93mV. This is nominal arithmetic, not connector-level switching qualification.

At -24V with a hypothetical1V clamp, the4k first resistor carries5.75mA and dissipates132.25mW. The diode supplies slightly less current because the lower resistor branch supplies current too. Resistor sizing and simultaneous-fault thermal analysis therefore remain consequential; do not reuse a small resistor footprint automatically. This same-loading example trades higher clamp current/power for preservation of normal diode loading. The earlier10k/30k/10k example has50k input loading and52.9mW first-resistor fault power. Neither example selects a part or proves protection.

Doctrine discovery pkt-56532e3e722a770a matched no specific hardware concepts. This study relies on circuit algebra and manufacturer/project sources, not a doctrine-backed intervention. Material missing evidence includes exact diode full-temperature/dynamic bounds, tolerated switching levels and pulse timing, component ratings and board parasitics. No source circuit adoption.

## Reproduction and disposition

Run `python3 telemetry-pod/expansion/wheel-clamp-study/thresholds.py`; it must reproduce `thresholds.json`. `sources.json` pins the project evidence used. The initial divider example is retained in `calculation.json`. The independent review covers both nominal studies. No native schematic, board, part binding, rule or acceptance status changes.

The132.25mW example exceeds the previously used ordinary0603 family's100mW rating even before derating. The eventual first resistor needs a separate selection and thermal qualification. Also, lower signal gain amplifies comparator input-offset error when referred back to the signal: a conditional4mV offset corresponds to20mV at gain0.2 versus8mV at gain0.5. Nominal threshold matching does not preserve the full error envelope. Exact component tolerances, temperature and sensor compatibility remain open.
