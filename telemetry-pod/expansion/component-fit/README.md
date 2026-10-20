# Six package changes for exact component selection

This revision moves C64/C66 and R73/R77/R81/R162 from 0603 to 0805 and
binds their exact selected parts. Nominal values, connectivity, no-connects,
symbols and all 314 previous bindings remain unchanged. It starts from the
pinned `part-bindings/prepared/inputs` tree. It does not replace the actual pod
project or establish a placed, routed or fabrication-ready design.

| References | Exact part | Supplier ID | Package and required characteristics |
| --- | --- | --- | --- |
| R73, R77, R81, R162 | YAGEO RT0805BRD071M05L | C7353633 | 0805, 1.05 Mohm, 0.1%, 25 ppm/K, −55 to 155 °C |
| C64, C66 | KEMET C0805C475K4RACTU | C7224519 | 0805, 4.7 uF, 16 V, X7R, 10%, −55 to 125 °C |

Exact manufacturer documents and fresh supplier responses are retained. Both
supplier captures have positive stock and `assemblyComponentFlag=false`;
these are historical observations, not assembly eligibility or reservations.
The resulting source has 320 bindings present but unqualified. R60 (31.3 kohm)
is the sole component without an identity binding. Five copper jumpers still
need fabrication-policy acceptance; six power flags are schematic-only.

## Decision and limits

The prior 0603 choices lacked verified exact identities. The captured 0805
parts match the stated nominal values and ratings. Moving these six packages
is preferable to relaxing voltage, dielectric, tolerance or temperature
requirements, or silently changing the protected-supply divider ratios.
An exact 0603 implementation remains a possible alternative if separately
verified; these searches do not prove that no such part exists.

The resistor body is 2.0 ±0.1 by 1.25 ±0.1 by 0.5 ±0.1 mm; its rating is
0.125 W at 70 °C with a separate 150 V ceiling. The capacitor body is
2.0 ±0.2 by 1.25 ±0.2 by 1.25 ±0.20 mm. Its nominal capacitance does not
prove effective capacitance under bias, temperature, tolerance and aging.
The manufacturer sheet specifies 3% loss per decade hour at its referee
conditions. Power-rail stability, storage supply dips and recovery remain open.

The larger land patterns require new placement, clearance, enclosure-height
and routing checks. `sources/R_0805_2012Metric.kicad_mod` captures the installed
KiCad footprint; its source path and hash are in the manifest. The existing
C_0805 capture is reused. Standard KiCad geometry is not proof of manufacturer
land-pattern or assembled-joint qualification. No board-fit or thermal claim
follows from source-level pad inspection.

The inherited Hall negative-input problem, both 125 °C resistor fault-screen
failures, TL431 stability, rail accuracy and transient behavior, shared-SPI
operation, logging recovery, EMC and mechanical holds remain. The gold AMPSEAL
connector's retained zero-stock observation is unchanged. The existing
`part-bindings` packet remains the historical predecessor rather than being
rewritten to hide the footprint change.

## Reproduction and review

From the repository root:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/component-fit/verify.py --source-only
```

`prepare.py --out NEW_DIRECTORY --source-only` reconstructs the complete input
tree, applies exactly six footprint and binding changes and adds the captured
resistor footprint. `prepared/` retains only the resulting intent and receipt;
the other inputs are pinned in the manifest and reconstructed from the predecessor.
Independent review checks the full source delta, captures and pad geometry.

Native generation remains blocked by AGENTEE-293 in agent-ee e4cf3ab.
`prepare.py` without `--source-only` attempts emission with full metadata and
copies the existing project library tables. Native acceptance for this stage
is deliberately not implemented or claimed: `verify.py` requires the explicit
source-only flag. After the emitter repair, add and exercise native XML/ERC
and metadata/footprint round-trip review before advancing to placement.
