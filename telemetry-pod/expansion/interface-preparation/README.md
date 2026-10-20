# Tire CAN and wheel-input preparation

This package retains the proposed tire CAN circuit, captured component sources,
stock snapshots and independent circuit reviews. **Native emission is blocked;
this is not a verified schematic or a replacement for `../storage-candidate`.**
The baseline is fome-mc `e89a033b8c0972d47e5eae6f38ee8b2819a7e7c8`.

`inputs/intent.json` adds twenty components for a dedicated MCP2518FD controller,
TJA1051T/3 transceiver, Schmitt NAND transmit gate, 20 MHz crystal, protection,
bypass and optional termination. Existing component records remain unchanged.
New component bindings are deliberately absent pending exact part selection.
`preparation-status.json` lists the additions and records the preparation boundary.

The wheel circuit is only a reviewed proposal in `wheel-review/`; it is not yet
in the intent. Tire sensor power at J1 pin31 is still NC, as are wheel pins23–28.
The 6.3 V protected sensor branches and their power budget remain to be designed.

## Circuit and firmware reading order

1. `review/can2-review.md`: pin maps, shared SPI timing, all five captured
   MCP2518FD errata, FIFO allocation and service-budget limits.
2. `review/crystal-and-silent-addendum.md`: crystal candidate and startup limits.
3. `review/silent-gate-and-protection.md`: final Schmitt gate, reset behavior,
   EN loading, TVS and configurable termination. This supersedes earlier silent
   gate proposals. Ordinary NAND SN74LVC1G00 is not selected.
4. `wheel-review/recommendation.md`: LM2903B-Q1 Hall candidate, hysteresis/filter,
   fault isolation and unresolved reverse-short heating.

The controller shares SPI with the ADC and IMU. Start at 1 MHz and allow at least
2 microseconds after its CS rises before another device drives MISO. A 32-entry
receive FIFO is proposed; 800 frames/s does not establish the burst or scheduling
bound. Parked downloads and eMMC operation must not break acquisition deadlines.

The final transmit gate is `S = NOT(MCU_EN AND GPIO0_TX_ENABLE)`. It enforces
silence while reset is held with valid gate supply. An MCU-only reset can leave
controller GPIO0 high; transmission can resume as EN rises before firmware
reinitializes. Firmware must handle that retained state. It is not a latched
startup interlock. Added gate input leakage changes the prior EN calculation:
normal-supply illustrative total is 1.55 microamps / 155 mV at 100 kohm.
Gate behavior around the supervisor's 0.8 V POR test point remains unbounded.

Y1 is Epson X1E0003410031, using the FA238-specific footprint. The initial 18 pF
load capacitors assume 3 pF stray capacitance; oscillator startup, drive, actual
parasitics and temperature require validation. JP1 is copper, normally open;
bridge it only when the pod is a physical bus endpoint. R70 remains assembled.
The exact resistor's power/pulse/temperature rating remains open.

## Emission blocker and next check

`failed-emission-receipt.json` retains the failure on agent-ee
`4ef3a7b0420d05a45636a7726f75557835d78517`: the emitter mistakes multiple valid
KiCad 10 private properties for duplicate properties. Stock crystal metadata is
retained intact. AGENTEE-288 also covers explicit BOM/assembly policy: JP1 must
remain on board while excluded from the BOM. No metadata stripping or native
file flag edits are permitted as a workaround.

After the integrator releases that fix, reconcile its explicit component-policy
schema into these inputs and emit to a fresh directory:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 -m agent_ee.schematic_emitter \
  inputs/intent.json --layout inputs/emitter-layout.json --captures inputs \
  --out /absolute/fresh-directory/project \
  --receipt /absolute/fresh-directory/receipt.json
```

Then configure project-local library tables and run native KiCad netlist/ERC,
independent pin-map and baseline-preservation checks, and BOM exclusion checks.
Only after those checks may the verified candidate advance. No native ERC/DRC,
placement, routing, thermal, EMC or manufacturing acceptance exists for this
interface preparation.

`sources/manifest.json` hashes the captured CAN/power/gate PDFs. Alternative
crystal and plain NAND sources are retained for review history, not selection.
`stock*/catalog.json` are timestamped availability snapshots, not reservations.
The wheel review records its primary source URLs; sensor evidence is also in
`../sources/GS1005-GS1007.pdf`. Exact sensor output voltage/pulse limits, hot diode
behavior and continuous negative-short pull-up dissipation remain release gates.

The [Hall thermal follow-up](wheel-thermal/README.md) specifies a 2512 pull-up
resistor candidate and excludes the supply switch's open-load FAULT indication
from the shared fault line. It retains the unresolved assembled thermal and
sensor qualification boundaries.

The newer [sensor-power preparation](sensor-power/README.md) adds three TPS26625
branches to a separate input snapshot. It supersedes the unimplemented TPS1H200A
supply-switch proposal; its independent RTN domains and unused FLT pins are
required to avoid fault propagation into logic. Native checks remain pending.

The [wheel-input preparation](wheel-input/README.md) adds both Hall channels to
the protected sensor-power snapshot. Its diode recovery/negative-input transient
hold remains explicit; source-graph verification does not establish survival.

[Rail diagnostics study](diagnostics/README.md) selects a three-ADS1119 candidate
and examines high-attenuation inputs, nine-rail acquisition and validity rules.
It is a pre-emission study; passive-model bounds do not establish fault survival.
Its [independent review](diagnostics/independent-review.md) confirms the candidate
pinmap, protocol and arithmetic, and requires a separate first-frame settling
policy. The nominal 5 V step example needs about 3.81 ms to reach half a code;
normal scan timing alone does not guarantee settled readings after a transition.

The [prepared diagnostic circuit](diagnostic-circuit/README.md) connects three
ADCs to eight existing rails. The ninth channel remains reserved until the
protected auxiliary 5 V branch is implemented. Its generator preserves the
wheel/CAN/storage/supervision circuits; native verification is still pending.

The [auxiliary-power preparation](aux-power/README.md) extends that snapshot with
an independently protected branch from the precision sensor supply, J1 pins21/22,
and the ninth diagnostic channel. Its wiring passed independent graph checks;
5 V ±1% at a positive external load remains unqualified because source tolerance,
switch voltage drop, harness loss and shared-rail fault behavior need bounds.
