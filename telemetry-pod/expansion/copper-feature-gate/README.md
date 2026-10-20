# Captured jumper rejected by the released copper-feature gate

Agent-ee `1962cf0` accepts a `copper_features` declaration but rejects the
expanded pod's unchanged captured KiCad solder jumper. Native KiCad 10.0.7
loaded five instances of that footprint into the retained board fixture;
`copper_feature_problems` returned `graphics are outside silk/fab layers`
for JP1–JP5. `report.json` pins the gate and footprint bytes.

Each footprint already has `exclude_from_bom` and `exclude_from_pos_files`,
two custom surface copper/mask pads, no 3D model and no orderable part fields.
The rejected graphics are one filled `F.Mask` rectangle opening the gap
between pads and four `F.CrtYd` lines. These are part of the captured footprint;
the source has not been edited to bypass the predicate. The courtyard remains
useful for placement checks and the mask opening affects the solder bridge.

The declaration to merge into the eventual captured fab-export check is:

```json
{"copper_features": ["JP1", "JP2", "JP3", "JP4", "JP5"]}
```

This is a parameter fragment, not an executable full scope or fabrication
approval. The board is a reproduction fixture with arbitrary separated poses
and no electrical net assignments, board outline or routing. It is not the
expanded pod candidate. Full schematic/netlist parity, BOM/CPL omission,
placement, routing, DRC and manufacturing-package verification remain open.

Replay against the current agent-ee checkout from the repository root with a
fresh output directory:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/copper-feature-gate/reproduce.py --out /tmp/pod-copper-gate-fresh
```

The script records the current predicate result; a successful script exit
means reproduction completed, not that the predicate accepted the footprint.
The committed report preserves the original refusal after the software changes.
Native pcbnew printed three property-enum assertion diagnostics on import;
footprint loading and board serialization completed. This is not an ERC/DRC run.

Next: the agent-ee integrator must decide and review support for bounded mask
and courtyard graphics, retaining rejection of unqualified physical content.
After that release, replay this real footprint and the complete fabrication
gates. Do not remove the mask opening or courtyard to obtain a passing result.
