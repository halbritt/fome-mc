# Exact 31.3 kohm series divider

This source revision resolves the last unbound orderable component while
preserving the intended U18 nominal trip point. It replaces the unbound
31.3 kohm R60 with **30.1 kohm R60 + 1.2 kohm R181 in series**. R61 remains
10 kohm. The nominal falling threshold remains **4.7495 V**. The 31.6 kohm
single-part alternative in `sensor-threshold/` is not selected.

| Reference | Exact selected part | Supplier ID | Capture stock |
| --- | --- | --- | --- |
| R60 | YAGEO RT0603BRD0730K1L | C705764 | 410 |
| R181 | YAGEO RT0603BRD071K2L | C136970 | 7556 |

Both manufacturer sheets specify 0603, 0.1%, ±25 ppm/K, −55 to 155 °C,
0.1 W at 70 °C and a separate 75 V continuous ceiling. Both supplier responses
have `assemblyComponentFlag=false`. Captures are historical observations,
not assembly eligibility or procurement commitments. PDFs and raw responses
are pinned in the manifest.

## Exact change

```
POD_5V_SENSOR -- R60 30.1k -- SUP_U18_TOP_SERIES -- R181 1.2k -- SUP_U18_SENSE
                                                               |
                                                U18 SENSE and R61 10k to GND
```

The intermediate node has exactly R60 pin2 and R181 pin1. The existing SENSE
net replaces only R60 pin2 with R181 pin2; all other endpoints remain. R181 uses
the already captured Device:R symbol and R_0603_1608Metric footprint. It is added
to the existing supervisor presentation group immediately after R60.

After collapsing the two-resistor top arm back to the original R60, the complete
intent must equal the pinned component-fit baseline, including all prior
bindings and no-connects. Removing R181 from the layout must likewise reproduce
the baseline layout. No library or footprint capture is changed or added.
The result has 333 schematic components and 322 metadata bindings: 316
orderable part identities plus six bare-copper probe records. Five copper
jumpers and six power flags remain intentionally without orderable identities.

## Electrical interpretation and limits

The worst-case initial tolerance of the sum remains 0.1%: 30.1 ohm plus
1.2 ohm uncertainty equals 31.3 ohm on 31.3 kohm. The same-sign worst-case
TCR remains 25 ppm/K; no cancellation or root-sum-square assumption is used.
The two resistors must remain within the evaluated local temperature envelope.
This supplies an explicit TCR specification that the old unbound R60 lacked.

At nominal 5 V, the full 41.3 kohm divider draws about 121.1 uA. R60 dissipates
about 0.441 mW and R181 about 17.6 uW. These calculations do not qualify assembled
thermal behavior. The extra component and exposed midpoint add layout area,
parasitic capacitance, contamination/leakage sensitivity and a possible failure
site. Keep the midpoint local to the divider and evaluate those effects in the
fresh placement/routing and EMC review.

The unchanged nominal threshold does not close the existing supervisor
sense-current applicability, healthy local-rail envelope, sensor fault window,
aging, noise, timing or recovery holds. U18 remains an upstream local-rail
alarm, not an all-sensors-valid indication; see `supply-monitor-coverage/`.
All other electrical, thermal, mechanical, assembly and availability holds
remain, including zero-stock J1 and the jumper fabrication gate.

## Reproduction and next gate

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/series-divider/verify.py --source-only
```

`prepare.py --out NEW_DIRECTORY --source-only` reconstructs the pinned full
component-fit inputs and applies only this series change. `prepared/` retains
intent, layout and receipt; the other inputs are reconstructed. Without the
source-only flag the producer attempts native emission with all metadata intact.

Independent source review passed 1,062 checks and five negative controls
(midpoint attachment, bypassed series resistor, wrong value, damaged prior
binding and wrong layout placement). Reports and reviewer scripts are retained.

Native verification now passes against the **unreleased agent-ee integration
candidate b42adf763948364547febc5f0767b2913b365af8**, including AGENTEE-293.
This does not establish that the repair is released on main. The prior failed
1962cf0 emission receipt remains in `native-attempt/` as historical evidence.

`native-candidate/` retains the portable project, complete captured inputs,
emission receipt, native XML, BOM and ERC report. `native-provenance.json`
pins the source archive and every retained file. The producer receipt still
says `NOT_RUN` because it records preparation; subsequent independent reports
record the actual native checks.

Independent native review passes 34,521 checks: all 333 source components,
337 units, 327 non-power XML components, 194 named nets, 175 explicit NCs,
316 BOM rows and 322 bindings. It compares embedded pin definitions with the
captured libraries, checks actual NC coordinates and power-flag connections,
and contracts the series subdivision to prove exact prior native connectivity.
All eight negative controls reject damaged bindings, series endpoints,
embedded pin types, NC markers, power flags, DNP state, BOM exclusions and ERC
sheet coverage. KiCad 10.0.7 reports zero ERC violations under the unchanged
recorded policy.

To reproduce, obtain the exact agent-ee commit with `git archive` into a fresh
local directory, then point `PYTHONPATH` at that directory's `src`:

```sh
PYTHONPATH=/path/to/b42adf7/src python3 telemetry-pod/expansion/series-divider/verify.py --out /path/to/new-evidence
PYTHONPATH=/path/to/b42adf7/src python3 telemetry-pod/expansion/series-divider/review/negative_native_probes.py telemetry-pod/expansion/series-divider telemetry-pod/expansion/series-divider/native-candidate /path/to/negative-report.json
```

The native verifier requires a fresh output directory and retains failures.
It requires byte-exact reconstructed inputs, project and receipts; then compares
native XML with only source path/date removed, exact BOM, and ERC with only date
removed. Its emission receipt also pins the emitter module. Later software must
reproduce this evidence or establish a separately reviewed candidate.

The retained overview and enlarged supervisor renders were inspected. The new
series connection is legible, with the resistor value close to adjacent graphics;
full-sheet detailed readability review remains open. See `review/visual-review.json`.
The subsequent [full-sheet review](review/full-sheet/README.md) found overlapping
net labels and component fields, plus stale group titles. Those findings remain
open despite the passing native graph and ERC checks.
This is not a placed, routed or fabrication-ready pod and does not replace the
committed pilot project. Placement/routing, hardware qualification, the jumper
fabrication gate and software release remain separate outstanding work.
