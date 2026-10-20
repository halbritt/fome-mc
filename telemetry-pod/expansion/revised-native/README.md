# Native candidate with reviewed datasheet revisions

This candidate adopts the three independently reviewed dated PDF revisions from `../source-revision` into all 16 affected schematic instances. It uses the same unreleased AGENTEE-301 emitter `f80016c230930196dafaa7b258be5f2e1b183eeb` as `../text-candidate`; the software archive hash is retained in `software.json`.

Native KiCad ERC reports zero violations. The existing independent series-source checker passes 34,533 assertions: 333 source components, 337 schematic units, 327 native XML components, 194 named nets, 175 explicit no-connects, 316 BOM instances and 322 bound components. It checks the new intent against the actual schematic and exported native graph.

`compare.py` requires the entire schematic to equal the prior text-candidate byte for byte after reversing only the three declared PDF SHA values at the 16 instances. No other schematic content, positions, pin wiring, UUIDs, field layout or footprint assignments changed. The native XML comparison permits only those field/property hash changes plus source/date metadata and U14 UUID-list ordering. The native BOM is byte-identical.

Source captures and old native candidates remain retained unchanged. Canonical sources now cover 315 of 316 purchased instances for this revised native candidate: the prior 299 plus the 16 revised instances. J1 historical PDF import remains pending AGENTEE-306; the full parts manifest and copper-jumper membership remain pending AGENTEE-305. The earlier CAD assignment pass applies to the unchanged symbol/footprint content, but its receipt is still pinned to the older XML; downstream execution must use this candidate explicitly and produce fresh receipts.

No placement, routing, DRC, manufacturing, assembly or operating approval is established. Electrical and physical holds recorded in the campaign remain open. The software is not represented as released.

## Replay

From the repository root, point PYTHONPATH at the exact archived emitter source and select a fresh output directory:

```sh
python3 telemetry-pod/expansion/revised-native/prepare.py --out "$CANDIDATE"
kicad-cli sch export netlist --format kicadxml -o "$CANDIDATE/native.xml" "$CANDIDATE/project/telemetry-pod.kicad_sch"
kicad-cli sch erc --format json -o "$CANDIDATE/erc.json" "$CANDIDATE/project/telemetry-pod.kicad_sch"
kicad-cli sch export bom --fields Reference,Value,Footprint,EXCLUDE_FROM_BOM,EXCLUDE_FROM_BOARD --labels Reference,Value,Footprint,ExcludeBOM,ExcludeBoard -o "$CANDIDATE/native-bom.csv" "$CANDIDATE/project/telemetry-pod.kicad_sch"
python3 telemetry-pod/expansion/series-divider/review/check_native_series.py telemetry-pod/expansion/series-divider "$CANDIDATE" "$CANDIDATE/native-review.json"
python3 telemetry-pod/expansion/revised-native/compare.py "$CANDIDATE" "$CANDIDATE/comparison.json"
```

Reconstructed inputs are pinned in `input-hashes.json`; native outputs and scripts are pinned in `provenance.json`. The upstream source-preparation receipt precedes native execution and its NOT_RUN status is historical preparation status; the separate native reports describe the executed checks. KiCad's XML source/date fields depend on output location/time and must not be treated as deterministic raw bytes across fresh exports.
