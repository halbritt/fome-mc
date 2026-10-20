# Expanded-pod diagnostic parts manifest

This is the first combined `agent-ee.parts/1` declaration for the revised expanded native schematic. It declares 315 purchased instances from canonical exact-source records, six existing bare-copper probes and five source-bound copper jumpers. J1 is explicitly omitted pending its canonical historical PDF import; it is not made DNP, excluded from native comparison or given invented supplier metadata. No complete parts pass is claimed.

The software is unreleased AGENTEE-305 commit `49587ed7824e6b3d3bbbf0cc03d974bdbd69a90a`, pinned with its archive hash in `software.json`. All five real JP1–JP5 declarations independently qualify against the captured stock symbol/footprint, schematic flags/embedded symbol, native pin metadata and nets. Assembly and custom geometry use the existing explicit CAD declarations, including the attrless jumper's reviewed surface-pad classification.

The full `parts_subset.evaluate` result is **malformed / unknown / missing**, with zero matches:

> TP2: legacy AGENT_EE_Probe property requires forward-annotation migration

Canonical manifest/CAD qualification completed before that strict schematic-probe refusal. Full native membership comparison never ran. Board-only migration from AGENTEE-302 does not migrate the captured schematic. A supported canonical probe-source migration is needed; silently normalizing source markers or bypassing this validator is not a demonstrated repair. The exact native-reference difference is J1, but J1 is not yet the sole evaluated failure.

`parts.json` and `assignments.json` retain the authored declarations. All 326 physical references are unique. The declaration source and per-part decision references point to the reviewed intent; they do not establish authenticated approval. Supplier stock remains historical. Required datasheet records and their immutable dependencies replay through the existing producer contracts. The six original probe IDs and their symbol/footprint capture paths are preserved.

`reconstruction.json` pins 400 copied files and their actual repository source paths. Reconstruction preserves source bytes and paths inside a fresh root, including canonical records' existing dependency paths and the probe markers' CAD paths. Dependencies already live in the repository; they are not copied again into this packet. `build.py --out NEW_ROOT` regenerates the declarations and capture. `verify.py --out OTHER_NEW_ROOT` reconstructs the retained declaration, checks source/artifact hashes, reruns the full evaluator and requires the exact retained refusal. Set PYTHONPATH to the exact archived software's `src`.

Independent review replayed the same full refusal and separately checked all five copper features, all 400 dependencies and the exact 326-reference membership. The evidence establishes that copper-feature support advances this workflow, while probe-source migration and J1 remain unresolved. It does not establish complete component suitability, live stock, native membership acceptance, placement or manufacturing readiness.
