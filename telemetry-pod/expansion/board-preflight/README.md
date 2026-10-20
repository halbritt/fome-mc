# Expanded PCB forward-annotation preflight

The exact 327-component native netlist cannot enter forward annotation on
agent-ee `4df4c9d`: `netlist_parity.MAX_COMPONENTS = 256` refuses its inventory.
`plan.json` retains the failed result. No board was written or placement attempted.
This is a software capacity refusal, not evidence that the board cannot fit.

`footprints.json` explicitly lists the 40 distinct selected footprint identities
from the series-divider intent and pins their existing captured bytes. It does
not select replacements or infer geometry. `provenance.json` pins the tool,
source repository, unchanged pilot board and native XML.

From the fome-mc repository root, with the pinned agent-ee source on PYTHONPATH:

```sh
python3 -m agent_ee.forward_annotation plan telemetry-pod/telemetry-pod.kicad_pcb \
  --netlist telemetry-pod/expansion/series-divider/native-candidate/native.xml \
  --manifest telemetry-pod/expansion/board-preflight/footprints.json \
  --captures telemetry-pod/expansion/series-divider/native-candidate/inputs \
  --work /path/to/fresh-plan-work --record /path/to/new-plan.json
```

This command only plans. The existing pilot is not a qualified mechanical seed
for the expansion; any subsequent apply requires a separate candidate and review
of connector, envelope, fixed positions, pad parity, net changes and leftover
copper. Increasing the inventory ceiling must retain byte/terminal/search limits
and fail-closed behavior, with boundary tests and this actual netlist exercised.
