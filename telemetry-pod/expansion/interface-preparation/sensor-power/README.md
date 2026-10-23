# Three protected sensor-power branches

This circuit preparation adds U23–U25 TPS26625DRCR branches to the CAN preparation:
front wheel, rear wheel and the two tire sensors. It supersedes the unimplemented
TPS1H200A branch proposal. It does not replace the verified storage schematic.
Native emission remains pending AGENTEE-288; no native ERC result exists here.

The [TI datasheet](https://www.ti.com/lit/ds/symlink/tps2662.pdf) identifies this
variant as auto-retry with input/output reverse-polarity protection. Support
components and exposed pad reference RTN, which must remain separate from ground.
SHDN uses its internal pull-up; FLT is unused. The operating junction ceiling is
125 C. Its absolute ratings and typical fault-response timings are not a system
qualification. Captured sources, hashes and independent analysis are retained.

## Prepared circuit

| Branch | Device | J1 supply | Current-setting resistor |
| --- | --- | --- | --- |
| Front wheel | U23 | 23 | R76, 44.2 kohm |
| Rear wheel | U24 | 26 | R80, 44.2 kohm |
| Both tire sensors | U25 | 31 | R84, 26.7 kohm |

All inputs connect to PRE_6V3. J1 pins25/28 now connect to ground; pin32 was
already connected. Wheel signal conditioning is still pending. For each device,
pins5/11 and its threshold/current/ramp components share an isolated RTN net;
pin6 connects to system ground. FLT9 and SHDN4 are explicitly NC. Do not connect
FLT directly to SENSOR_FAULT_N: a reverse wiring fault can move RTN negative.

Each branch has a shared 1.05 Mohm / 75 kohm / 208 kohm ladder (AGENTEE-491; was 68.1 kohm / 215 kohm) from input through
UVLO and OVP to RTN, specified initially at 0.1%, 25 ppm/K. Each also has 1 uF
50 V 0805 input and 100 nF 50 V output MLCC bypass to system ground and 10 nF 50 V C0G, 10%, ramp
capacitance to RTN. Exact passive bindings remain open.

The shared ladder relies on TI's documented current-limited UVLO connection
through at least 1 Mohm; the minimum proposed upper resistance is 1.046325 Mohm
under the reviewed tolerance/temperature envelope. This avoids assuming that RTN
stays at zero during a negative output fault. The inferred clamp behavior and
actual transient pin voltages remain explicit release checks.

## Independent bounds

SUPERSEDED (68.1 k / 215 k ladder): the review gave UVLO re-enable 5.342–6.009 V, disable 4.920–5.560 V, OVP cutoff
7.058–7.889 V and re-enable 6.503–7.297 V. With the provisional PRE_6V3 range
6.111–6.489 V, OVP recovery has only 13.9 mV margin. No added life drift is included.
These values are preparation bounds, not a frozen tolerance budget. Exact rail
and resistor evidence may require retuning.

The current-setting selections target nominal 152 mA for each wheel branch and
250 mA for the tire branch. Characterized conditions differ from this 6.3 V
application. Normal sensor and inrush loads, simultaneous faults, source droop,
retry behavior and enclosure heating require verification. The lower UVLO bound
does not maintain a valid 5 V Hall supply until shutdown; a voltage-monitoring
path must mark sagging-supply wheel readings invalid. OVP cutoff is not an 8 V
transient clamp.

A generic captured KiCad VSON footprint matches the pin count and exposed-pad
size, but its peripheral lands differ from TI's example. It remains a footprint
candidate requiring explicit land/paste/thermal review. Route each RTN island
and exposed pad independently from ground, including any thermal vias. The
50 V MLCCs must tolerate the specified negative-output fault without a polarized
component substitution. Copper clearances must account for the fault voltage.

## Reproduction and advancement

From this directory, with a fresh output path:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 prepare.py \
  --base ../inputs --out /absolute/fresh-inputs
```

`inputs/` retains the resulting 24 added components. The producer refuses an
existing destination and parses its authored library before writing it. Once AGENTEE-288 is released, reconcile its JP1 assembly
policy into the base inputs, regenerate, then perform native emission/netlist/ERC
and independent preservation checks. The earlier CAN failure receipt applies to
the earlier CAN-only inputs; it is not an attempted emission of this branch set.

`stock/catalog.json` records C2862873 as TPS26625DRCR with 2550 units at capture;
the raw response has `assemblyComponentFlag=false`, so assembly eligibility is
open. No purchase or reservation was made. TPS25947 was rejected for this branch
because its output-voltage limit with zero input does not accommodate a +24 V
miswire. The TPS1H200A findings remain useful rejection history, not the current
sensor-power implementation.

Run the complete source-preparation check before integration:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 verify.py
```

This parses all captured libraries and footprints, verifies library hashes,
reproduces the prepared files and runs the independent graph checker. It does
not substitute for native KiCad emission or ERC.


## AGENTEE-491 OVP ladder repair (agent-529 110afb4e v1 / 74db43f0 v1; agent-522 packet 58040048…)

**Change:** R74/R78/R82 (middle) become 75 kOhm, YAGEO RT0603BRD0775KL (C723587). R75/R79/R83 (bottom) become 208 kOhm, RT0603BRD07208KL (C861219). R73/R77/R81 stay 1.05 MOhm, RT0805BRD071M05L. The footprints and nets are unchanged.
- The TPS2662 >= 1 MOhm top rule and UVLO hysteresis are kept.
- The 5 V +/-1% aux remains a separate OPEN item.

**Post-stress screen, under agent-522's CONDITIONAL model (`calculations.json`, findings.md):**
- rail 6.11746–6.55068 V;
- UV re-enable 5.30367–6.05557 V; UV disable 4.88537–5.60206 V;
- OV trip 7.23898–**8.21606 V**; OV recovery 6.67040–7.59843 V;
- minimum settled OVP recovery margin +119.72 mV.

The post-stress / typical-PFM model is a SCREEN, not guaranteed 9–16 V regulation.

**AGENT-DERIVED, not owner-stated:** the repair raises the maximum static OV trip from 7.889 V to 8.216 V post-stress.
- Any wheel or tire sensor must tolerate at least **8.3 V continuous** on its supply. This is a STATIC screen only.
- A 5–8 V sensor is excluded.
- OVP is not a clamp (see above), so this screen does NOT qualify transient survival. Transient amplitude, duration and protective response stay UNQUALIFIED, to be bounded against the selected sensor's published ratings before release.

**Example only:** Izze IRTS-60-V3 is cited with 8.216 V inside its 5–10 V OPERATING range; its sheet publishes NO absolute-maximum supply rating. Its 120 mA harness figure is the sourced basis for the 150 mA pair allocation.
- The Honeywell and Izze examples are ENGINEERING PROPOSALS. No sensor and no CAN2 protocol/node proposal is adopted.
- The 650 mA / 210 mA / 1.487 A figures stay CONDITIONAL, tied to the example allocation.

**Stock:** generation-day stock must be refreshed at generation, notably for the 208 k part (1,901 in stock at 2026-10-23T13:43Z, `production-capture/sources/assembly-stock-20261023-491`).

**Not authorized here:** no new footprint, height or membership; no SHDN sequencing; no pre-fab gate.
