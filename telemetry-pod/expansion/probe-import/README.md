# Expanded native import with legacy-probe migration

The AGENTEE-302 candidate repair advances the real expanded pod through forward annotation. Planning and apply both complete without findings, and the requested output exists with the hash in `apply.json`. This is the imported diagnostic board, **not a placed or routed design**.

The software is an isolated archive of integrator stack `2b24cc4448da8ce9ffd580410bc95d0f0a0ab3a2` plus only the `forward_annotation.py` patch from AGENTEE-302 `5df0ad8efc78b7725c169e753323d31f94a1d0cf`. Exact source/archive/patch hashes are in `software.json`. Neither released main nor worker checkouts were changed. This experiment is not a software release.

The input is the revised native candidate from fome-mc `650a27a`, the unchanged 40-type captured footprint library and the prior diagnostic scaffold. Planning adds 327 circuit footprints, retains four board-only mounting holes, introduces 369 net definitions and assigns 1,128 pads. Six migrations explicitly preserve each decoded probe record while replacing its legacy JSON marker with the canonical encoding. Captured source XML and footprint bytes remain unchanged. Apply runs a fresh native child to read the saved board, verifies the planned transformations and validates all probe identities, geometry, nets and exclusions before publishing its local output.

`staged-board.kicad_pcb` contains 331 footprints and no tracks or zones. Circuit footprints remain in the emitter's staging column outside the outline. Board dimensions, enclosure fit, mounting-hole suitability, placement policy and keepouts are unqualified. This output must not be passed off as a manufacturing candidate.

`verify.py` replays saved-fact correspondence and probe validation, checks exact source/footprint/output hashes and proves equality of all six decoded old/new records. It uses the pinned experimental source on PYTHONPATH. It does not replace a fresh native run; the retained native facts originate from the actual saved-board verification child. Historical execution paths identify the original runs.

## Reproduce

Extract the pinned base archive and apply `software.patch` to that isolated copy. Set PYTHONPATH to its `src`. Use the command sequence in `../board-preflight/import-experiment/README.md`, replacing its netlist with `../revised-native/native.xml` and selecting fresh work, result and output paths. Both steps should now complete. The captured source markers must remain unchanged; migration belongs to forward annotation.

The full parts manifest, qualification, placement, routing, DRC, fabrication outputs and manufacturing review remain open.
