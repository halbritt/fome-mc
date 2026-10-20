# Expanded purchased-parts source closure

All 316 purchased instances in the current 333-component source now have exact
supplier identity captures and bytes matching their bound datasheet hashes in
this repository. This closes a source-retention prerequisite for building the
expanded parts manifest. It does not qualify parts, assemblies or the design.

`trace.py` inventories all 85 exact LCSC/MPN/manufacturer identity groups. It
replays tracked `agent-ee.jlc-catalog/1` catalogs against their raw responses,
requires exact identity equality, and matches PDFs by the SHA-256 already in
each instance's datasheet binding. It does not substitute a newer datasheet,
infer manufacturer aliases, or merge historical stock observations. The six
probes, five copper jumpers and six power symbols are separately accounted for.

Before recovery, 48 groups were fully sourced (165 instances). Another 32
instances in the mixed C95204 group had both sources, giving **197 individually
sourced instances and 119 incomplete instances**. The newer C95204 datasheet
was not substituted for the missing older hash used by 24 instances.
`before-recovery.json` preserves that bounded search result.

The independent reviewer recovered a pointer to the historical pilot inputs:
`/tmp/agent469-coordination/pod-campaign-v1/driver-preparation-v9-90x65/inputs`.
Live inspection found `parts-electrical.json` and matching named part records
for all 37 incomplete identity groups. `recovery.json` pins that manifest, the
99 matching instance records and their complete canonical dependency closures.
Every recovered record was replayed through the released `part_record` validator
at agent-ee `014c7c3e4079c35c52bc5a42007ed7ed612feb55` before copying.
`recovered-pilot/` retains exact bytes with original relative paths, including
whole acquisition manifests and their dependencies. Replay does not depend on
the temporary source path. Repeated records are retained as historical evidence;
this is not an instruction to duplicate physical instances in the new manifest.

The recovered historical manifest is explicitly **not the expanded manifest**:
its instance counts, MCP3204 selection, old CAD and authority context cannot be
adopted as current. Only records matching current exact identities and bound
PDF hashes were selected. PDF hash identity does not prove applicability;
canonical part-record replay does not authenticate historical source acquisition
or owner approval. Stock is capture-time data, not a fresh generation-day stock
check. Thermal, operating, assembly, source-selection and existing electrical
holds remain unchanged.

The next step is to compose the expanded `agent-ee.parts/1` declaration, retain
per-part decision and acquisition provenance, qualify all current CAD assignments,
and execute `parts_subset` against the expanded native schematic/netlist. The
48 previously sourced groups still need their canonical record/adaptation work;
this trace does not claim those records have been produced.

From the repository root, with the pinned software on `PYTHONPATH`:

```sh
python3 telemetry-pod/expansion/parts-closure/trace.py --verify telemetry-pod/expansion/parts-closure/inventory.json
python3 telemetry-pod/expansion/parts-closure/verify_recovery.py
```

The trace searches tracked telemetry-pod captures only; stage newly retained
captures before regenerating it. It refuses missing or altered raw responses.
Its source inventory and validator hashes are retained. This is an offline
source prerequisite check, not a native ERC/DRC or fabrication gate.

Verification replays the retained dependency set and requires every file to remain
tracked. New generation discovers current tracked captures. Later acquisition
packets therefore do not silently expand an earlier trace or invalidate it merely
by adding duplicate PDFs; changes to retained sources still fail verification.
