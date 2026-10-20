# Expanded pod part selections

This packet selects exact identities for the 40 resistors in the ten 301:1
monitor dividers. It inventories every component in the pinned 332-component
thermistor source. It does not modify that source or fill its part bindings.

| Positions | Manufacturer part | Supplier identity | Captured stock |
| --- | --- | --- | --- |
| 30 × 499 kohm upper resistors | YAGEO RT0603BRD07499KL | C515607 | 101082 |
| 10 × 4.99 kohm lower resistors | YAGEO RT0603BRD074K99L | C723532 | 16395 |

Stock was captured on 2026-10-20; exact timestamps and raw responses are in
`stock/catalog.json`. Both raw `assemblyComponentFlag` values are **false**.
Stock does not establish assembly eligibility. No alternative assembly process
or hand-fitting exception has been approved.

The retained exact-MPN manufacturer PDFs specify 0603, 0.1% tolerance,
±25 ppm/°C, −55 to 155 °C operation, and 0.1 W at 70 °C with temperature
derating. The 75 V maximum continuous voltage is also constrained by power:
the 4.99 kohm part reaches 0.1 W at approximately 22.34 V. The 150 V overload
entry is not an automotive transient qualification. Circuit stress, local
film temperature, aging, PCB land qualification and fault operation remain
separate checks. See the preceding diagnostic and thermistor calculations for
their conditional screening assumptions.

`selections.json` maps each exact identity to component IDs and references.
`inventory.json` records these mutually exclusive states:

| State | Count |
| --- | --- |
| Binding present, not requalified | 126 |
| Selected here, not bound | 40 |
| Unselected | 155 |
| Copper feature policy pending | 5 |
| Power symbol | 6 |

The five copper features are JP1 and JP2–JP5; they must not acquire fictitious
purchased-part bindings. Agent-ee e4cf3ab releases private-property emission
and per-component BOM policy; the expanded source still needs regeneration
and native verification. Copper-feature fabrication acceptance remains open
under AGENTEE-289. Full assembly binding, ERC, placement, routing,
DRC, thermal and electrical qualification, and manufacturing release remain open.

The retained discovery query for `RT0603BRD071M05L` returned no rows but was
normalized by the server to `RT0603BRD071K05L`. This is an unresolved search,
not evidence that a 1.05 Mohm part is unavailable. No divider redesign follows
from that response.

Run from the repository root with the agent-ee source available:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/part-selection/verify.py
```

Verification replays official stock parsing from retained bytes, checks source
hashes, regenerates the inventory, and reruns the independent 616-check review.
It performs no network requests and changes no project artifacts. Review scope
and limitations are in `review/README.md`.
