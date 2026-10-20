# Independent TPS389001 pre-emission review

The four-supervisor topology resolves the TPS386000 independent-sense objection.
TPS3890 page12 section8.3.4 explicitly permits SENSE0..5.5V regardless of VDD.
Page3 pins: SENSE1, GND2, MR3, VDD4, CT5, RESET6. No exposed pad.

Pin assignments and open-drain reset wiring are consistent with the proposed
circuit. MR tied to local VDD is the manufacturer's unused-MR disposition.
Use100nF local bypass on each supervisor. The two MCU reset outputs may share
MCU_EN; the sensor and input fault signals remain separate10k pull-up nets.

Main16.5k/10k static threshold remains above3.0V, but only by11.6mV at the
conservative corner. This excludes temperature drift and transient droop.
16.9k/10k is an alternative with more lower-threshold margin and still releases
below3.201V; see calculations.json. Do not claim guaranteed protection of the
MCU operating range from a typical18us assertion delay and static threshold alone.

R29=100k with10nF gives nominal1ms RC. Two250nA supervisor leakage contributions
plus50nA MCU input leakage would lower released EN by55mV at100k. This is ample
normal-operation high-level margin. At0.8V, the resistor alone draws8uA, below
the supervisor15uA POR test load. Low-VDD leakage outside each device's stated
test conditions and external factory probe loading remain unqualified.

CT22nF nominal release delay is23.565ms. With an illustrative10% capacitor and
independent current/threshold corners the algebra gives about17.185..34.712ms;
the additive25us is nominal, so this is not a guaranteed datasheet timing bound.
Repeated faults must retain at least the ESP32 reset pulse duration; observe the
actual EN trace. ESP module power-up/reset timing table requires 50 us low reset and stable
rails before enable.

Protected-input divider64.9k/10k gives about5.35V at40V including resistor corners.
The independent SENSE recommended maximum5.5V still limits the tolerated input
to approximately41.1V; hot transient clamp/overshoot must satisfy this. Higher
absolute maximum7V is not the intended design limit. No flush-time claim follows
from the8.61V nominal early-warning threshold.

## Footprint

The installed generic WSON6 footprint is not an exact reproduction of TI's
current DSE0006A4220552/B land dimensions or asymmetric mask rules. Page25 calls
for pads1-3 solder-mask-defined with at least0.05mm overlap and pads4-6 NSMD
with at most0.05mm clearance. Page26 stencil dimensions are0.8x0.25mm forpad1
and0.7x0.25mm for the other five pads.

The proposed custom interpretation (left copper enlarged0.05mm all around,
negative0.05mm mask/paste margins; right nominal copper and positive0.05mm mask)
is coherent as an engineering candidate. However, page25's top illustration
shows outer green outlines around all six inner blue shapes and dimensions the
inner shapes; it does not unambiguously establish the left-side dimensions as
mask openings rather than copper. Record the interpretation explicitly, rather
than claiming a literal manufacturer copper match. Verify actual mask/paste
Gerbers and corner radii after emission. A0.05mm nominal minimum mask overlap
also needs fabrication registration tolerances; no assembly qualification is implied.

No native files edited. Retained report supports candidate construction only.
