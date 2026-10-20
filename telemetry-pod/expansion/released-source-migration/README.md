# Released expanded-pod source migration

This is the expanded pod's canonical-probe source stage, following `revised-native` and the complete physical-part declaration. It adopts the supported source migration on released agent-ee `f507cf28e8c1874f219f98860df95d49488e2843`. Future expanded-pod schematic and forward-annotation work should use this migrated source. Earlier native candidates and diagnostic PCB files remain retained history; no placed board is adopted here.

The completed migration receipt records six probe migrations with zero violations and preserves all 316 purchased components verbatim. Five solder-jumper copper features remain declared. All 409 original capture inputs and 201 released producer files were checked unchanged; no provisional software overlay was used. The final native membership evaluation covers all 327 physical references with zero defects or unknowns. Six virtual power components are separately qualified exclusions.

`intent.json` is the migrated source, `emitter-layout.json` its layout, and `project/telemetry-pod.kicad_sch` the regenerated native schematic. Captured project library tables and dependencies are retained for native inspection. The membership report retains its qualification and dependency evidence; the source capture reconstruction is defined by `../complete-parts-manifest/reconstruction.json` and the unchanged original declarations there. `replay-input-hashes.json` identifies the complete isolated capture used for this replay, including the original legacy intent; it is not a checksum list for this new migrated packet.

Independent review verified the exact release bytes, receipt, purchased-component preservation, feature qualification, native graph and complete membership. Fresh native ERC reports zero violations with the same four existing ignored checks. These results establish source migration and circuit preservation, not component availability, temperature validation, electrical performance, placement, routing or fabrication acceptance.

## Native replay

From this directory, use a fresh report path:

```sh
kicad-cli sch erc --severity-all --format json --output /tmp/released-source-erc.json project/telemetry-pod.kicad_sch
kicad-cli sch export netlist --format kicadxml --output /tmp/released-source-native.xml project/telemetry-pod.kicad_sch
sha256sum -c SHA256SUMS
```

Compare electrical inventory semantically: export path/date metadata can change. Native source files must not be upgraded or saved by verification. `migration-receipt.json` is retained evidence from its isolated execution, whose absolute capture paths are historical; it is not a receipt that can be adopted again at a new path.

## Remaining boundaries

Existing diagnostic PCB candidates already carry canonical probe markers. Future PCB adoption requires released forward-annotation reconciliation and fresh board/source parity checks against this migrated source. Source migration does not fix electrical locality, existing drill/clearance/edge findings, silkscreen, physical envelopes, source suitability, power/fault behavior, thermal validation of the accepted 85 °C parts, firmware or hardware qualification. Routing and manufacturing outputs remain open. J1's captured stock remains historical zero and its source-acquisition limitations remain explicit.
