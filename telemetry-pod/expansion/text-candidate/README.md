# Expanded pod replay of AGENTEE-301

The unreleased agent-ee candidate `f80016c230930196dafaa7b258be5f2e1b183eeb`
regenerates the expanded telemetry pod without changing its captured source.
The source is fome-mc `43bc6f0f646bfd95576ab047b6482974744623d6`; use the existing
`../released-presentation/prepare.py` with the candidate's archived `src` on
`PYTHONPATH`. `software.json` pins the archive and `provenance.json` pins the
reconstructed inputs and retained outputs. No worker checkout was modified.

Native KiCad ERC has zero violations. The independent series source checker
passes 34,533 assertions. The existing presentation comparison confirms that
all inputs other than the two previously corrected headings, native component
identities, connectivity and BOM match the retained series-divider baseline.
Its native XML comparison removes source/date and sorts only the U14 unit UUID
list. The original captured probe markers are unchanged.

The candidate's native SVG diagnostic reports zero label-to-text overlaps.
Running the same diagnostic on the released-presentation baseline reports 17:
six probe pin-name collisions plus overlaps involving R18, R128, R129, R140,
R144 and U31. Both reports retain 684 labels and 668 visible fields. Independent review attributes the 86 fewer `other` texts entirely to
excluded drawing-sheet borders and title-block furniture; circuit label and
field text/reference multisets are identical.

The optional `--native-text-work` emission also passes, with no additional field
moves and a schematic byte-identical to the ordinary candidate. Its execution
receipt and placement report are retained under `native-text/`. This is an
isolated software candidate replay, not a software release or full readability
acceptance. The diagnostic excludes label/label and field/field collisions;
independent targeted visual review supports closure of VIS1/VIS2 and the U31
text collision for this exact candidate. It found no new blocking defect in
the inspected regions, including long thermistor fields. Whole-sheet readability
remains open. Electrical, placement, routing,
fabrication, assembly and operating qualification are not established.

## Replay

Extract the exact software commit into a fresh directory using `git archive`.
Set `PYTHONPATH` to its `src` directory, then from the fome-mc root:

```sh
python3 telemetry-pod/expansion/released-presentation/prepare.py --out "$CANDIDATE"
kicad-cli sch export netlist --format kicadxml -o "$CANDIDATE/native.xml" "$CANDIDATE/project/telemetry-pod.kicad_sch"
kicad-cli sch erc --format json -o "$CANDIDATE/erc.json" "$CANDIDATE/project/telemetry-pod.kicad_sch"
kicad-cli sch export bom --fields Reference,Value,Footprint,EXCLUDE_FROM_BOM,EXCLUDE_FROM_BOARD --labels Reference,Value,Footprint,ExcludeBOM,ExcludeBoard -o "$CANDIDATE/native-bom.csv" "$CANDIDATE/project/telemetry-pod.kicad_sch"
kicad-cli sch export svg --exclude-drawing-sheet -o "$CANDIDATE/svg/" "$CANDIDATE/project/telemetry-pod.kicad_sch"
python3 -m agent_ee.schematic_text "$CANDIDATE/project/telemetry-pod.kicad_sch" "$CANDIDATE/svg/telemetry-pod.svg" > "$CANDIDATE/text-overlaps.json"
python3 telemetry-pod/expansion/released-presentation/compare.py "$CANDIDATE" "$CANDIDATE/comparison.json"
python3 telemetry-pod/expansion/series-divider/review/check_native_series.py telemetry-pod/expansion/series-divider "$CANDIDATE" "$CANDIDATE/native-review.json"
python3 -m agent_ee.schematic_emitter "$CANDIDATE/inputs/intent.json" --layout "$CANDIDATE/inputs/emitter-layout.json" --captures "$CANDIDATE/inputs" --native-text-work "$TEXT_WORK" --out "$STRICT_PROJECT" --receipt "$STRICT_RECEIPT"
```

All output directories must be fresh. The archived SVG and full diagnostic
reports use deterministic gzip compression. Decompress before running the SVG
checker. Use the checker on the retained released-presentation schematic/SVG
for the baseline comparison (expected exit 1, 17 overlaps); the new candidate
returns exit 0. `native.xml` must be force-added because the repository ignores
XML files globally.
