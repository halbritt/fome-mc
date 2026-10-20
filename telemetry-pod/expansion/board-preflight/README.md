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

## Independent footprint-index preflight

`check_footprints.py` invokes the ordinary footprint index on the same complete
40-member captured manifest, without entering the native inventory reader. On
agent-ee `4df4c9d`, the index refuses the selected custom-pad solder jumper with
`unsupported native pad type/geometry`; coverage is `missing`, execution
`failed`, outcome `unknown`. The complete index is retained in
`footprint-report.json`. No custom-pad declaration or altered geometry was used.

The 39 indexed footprint types cover 322 native components whose complete
electrical pin-number sets match. JP1–JP5 remain unindexed; no mismatched number
sets were found among the indexed components. This is partial numbering
evidence, not full footprint coverage or package/geometry qualification.

```sh
PYTHONPATH=/path/to/agent-ee-4df4c9d/src python3 telemetry-pod/expansion/board-preflight/check_footprints.py
```

The output must match `footprint-report.json` at that software revision.
This refusal is separate from AGENTEE-297's solder-mask/courtyard fabrication
predicate. The forward-annotation implementation calls `index_footprints`
without a declaration input; its public command exposes no declaration option.
An integration repair must preserve the exact captured jumper, qualify the
permitted representation or carry an explicit bounded declaration through the
whole pipeline, and retain missing/unsupported coverage for everything outside
that qualification. A numbering declaration alone must not become geometry
acceptance.

Independent review reproduced the retained report exactly and confirmed that a
temporary MCP3208 pin-number mutation produces a U4 numbering mismatch. The
script exits zero after emitting diagnostics even when findings remain: callers
must inspect the index execution/coverage and numbering results. It is not an
acceptance gate.
