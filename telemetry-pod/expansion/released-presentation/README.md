# Released emitter and corrected eMMC headings

This candidate regenerates the expanded 333-component series-divider design
with agent-ee release `014c7c3e4079c35c52bc5a42007ed7ed612feb55`. Both local
main and origin/main were observed at that revision. It includes the released
structured datasheet binding repair, replacing reliance on an unreleased emitter
for this new candidate. Historical series-divider evidence remains unchanged.

Two presentation headings now describe the actual circuit state:

- `eMMC interface - qualification pending`
- `Separate eMMC core supply - qualification pending`

The supplies and supervisor already exist in the source; their qualification
remains open. These headings replace the stale “supplies pending” and “supervisor
pending” wording. The emitter uses heading widths when packing groups, so these
changes also reflow several group positions. This is not a byte-identical
schematic or a full readability approval.

Native KiCad 10.0.7 ERC reports zero violations. The retained independent series
checker passes 34,521 checks against all source components, units, bindings,
pin definitions, actual no-connect coordinates, power flags, nets and BOM.
`compare.py` separately checks that the input change is exactly the two headings,
all other captured inputs are byte-identical, and all native instance UUIDs
remain unchanged. The XML comparison removes only source path/date metadata and
sorts the U14 multi-unit UUID list (preserving multiplicity). KiCad reordered
that list without changing its identities. Every other XML value matches the
prior series-divider export. The BOM is byte-identical.

The overview and enlarged eMMC render show the corrected headings. Only VIS-3
from the prior full-sheet review is addressed. VIS-1/VIS-2 text overlaps and
U31 crowding remain open under AGENTEE-301; after that repair, inspect the whole
sheet again because this candidate has a different arrangement. No placement,
routing, fabrication, assembly or operating qualification is established.

## Reproduce

Extract the exact agent-ee release with `git archive` to a fresh directory.
`provenance.json` pins that archive and all reconstructed inputs and retained
outputs. Point `PYTHONPATH` at the extracted `src` directory:

```sh
python3 telemetry-pod/expansion/released-presentation/prepare.py --out /path/to/fresh-candidate
```

The producer reconstructs the previously verified series-divider inputs and
changes only the two heading strings before native emission. It preserves all
captured libraries and bindings. It never patches the emitted schematic.
`candidate/` retains the project and evidence; redundant inputs are reconstructed
by the producer and pinned by hash in the provenance file.

Run these commands against that fresh candidate, replacing `CANDIDATE` with its
absolute path:

```sh
kicad-cli sch export netlist --format kicadxml -o CANDIDATE/native.xml CANDIDATE/project/telemetry-pod.kicad_sch
kicad-cli sch erc --format json -o CANDIDATE/erc.json CANDIDATE/project/telemetry-pod.kicad_sch
kicad-cli sch export bom --fields Reference,Value,Footprint,EXCLUDE_FROM_BOM,EXCLUDE_FROM_BOARD --labels Reference,Value,Footprint,ExcludeBOM,ExcludeBoard -o CANDIDATE/native-bom.csv CANDIDATE/project/telemetry-pod.kicad_sch
python3 telemetry-pod/expansion/released-presentation/compare.py CANDIDATE CANDIDATE/comparison.json
python3 telemetry-pod/expansion/series-divider/review/check_native_series.py telemetry-pod/expansion/series-divider CANDIDATE CANDIDATE/native-review.json
```

The reused independent checker retains its historical wording about an
unreleased emitter in its scope string; it does not establish software release
status. The exact release and candidate identity are recorded here and in
`provenance.json`. The source-preparation receipt likewise says `NOT_RUN` because
it precedes emission; native execution evidence is in the separate reports.
