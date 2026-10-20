# Expanded-pod placement admission

The native placement probe reads the successful imported board from `../probe-import` without changing it. Its outline and captured courtyards are proven by the geometry parser. The packer nevertheless refuses before search:

> JP1 pad '1': native pad shape 6 not qualified for packing

`result.json` records `unsupported_geometry`, `outcome: unknown`, zero steps and no placements. This is an actual call to `placer.pack` on the captured native probe, using the same isolated software pinned in `../probe-import/software.json`. Import's custom-pad support does not qualify the placement writer or its geometry-preservation checks. The footprint must not be replaced with a rectangle or its primitive data discarded to evade this boundary.

The policy is a diagnostic admission input: 200,000 steps, 0.25 mm courtyard gap, 0.5 mm edge margin and the four existing holes fixed. J1/U1/J2/U14/U3 have search priority only, not approved mechanical locations. All 331 imported footprints are currently on F.Cu; the intended double-sided design still requires explicit side assignments, mechanical anchors, overhang declarations, antenna constraints and electrical grouping. No placement search ran and no double-sided fit conclusion follows from this refusal. The old pilot's envelope is historical context, not an automatically adopted expanded-board constraint.

The repair needs to qualify the real native custom pad geometry for rigid placement transforms and enforce saved-board preservation of its custom primitives and electrical membership. Admission in the importer alone is insufficient. Any unsupported pad geometry must continue to refuse explicitly; custom geometry must not become a generic waiver.

Replay with the exact experimental source on PYTHONPATH:

```sh
python3 telemetry-pod/expansion/placement-preflight/verify.py
```

For a fresh native extraction, decompress the retained probe only for inspection or run the pinned `agent_ee.placement_probe` with the KiCad Python interpreter on `../probe-import/staged-board.kicad_pcb` to a fresh output. This is placement admission evidence, not a placed board, a failed physical fit proof or manufacturing approval.
