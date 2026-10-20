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

Native verification for this new topology is not yet implemented or passed.
A fresh emission attempt against agent-ee `1962cf0` again rejects U20
PARAM_Datasheet before producing a schematic. Its exact receipt is retained
in `native-attempt/emission-receipt.json`; AGENTEE-293 remains the blocker. The component-fit checker
cannot be applied unchanged: it expects the prior 332-symbol graph and poses.
The next native review must validate all 333 symbols and the added intermediate
net, then prove the permitted series reduction preserves the previous electrical
connections. It must also check metadata, BOM, ERC, explicit NCs and readability
before placement. This source is not a placed, routed or fabrication-ready pod,
and does not replace the committed pilot project.
