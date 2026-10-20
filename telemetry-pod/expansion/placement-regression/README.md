# Rejected expanded-pod placement

This is a regression case, not the current board design or a routing input.
The native placer saved 331 footprints and passed its pad-geometry, netlist,
write-scope and courtyard checks. Full native DRC with the original project
settings then found through-board pad collisions with components on the other
side. Independent review confirmed the defect. Do not adopt this candidate.

The software is agent-ee `58999a9b1d411db8d6914823b34cd079943a532b`.
The seed is the decompressed `../placement-inputs/rejected-seed.kicad_pcb.gz`.
Its name refers to the earlier flip rejection; this software's flip/write-scope
checks passed. `derived-policy.json` adds only the existing envelope's fixed
references and overhang declarations to its packing policy. The 90 × 65 mm
outline, 0.25 mm courtyard gap and 0.5 mm movable courtyard edge margin were
unchanged. The complete plan used 13,585 of 200,000 steps.

## What the checks establish

| Evidence | Result |
| --- | --- |
| Native writer | Exited 0; `placed`, with authority `disposable-unsealed-proposal` |
| Pad geometry and native net membership | Preserved by the writer |
| Placement write scope | Allowed, zero violations |
| Saved-board courtyard judge / native courtyard overlaps | Pass / zero |
| Full DRC, unchanged project settings | 221 violations, 499 unconnected items, six schematic-parity warnings |
| Baseline comparison | 152 added violations, six courtyard overlaps removed, 69 prior violations retained |

The 152 added violations comprise 17 shorts, 14 clearance violations,
four through-hole pads inside courtyards, 13 solder-mask bridges,
25 silkscreen overlaps and 79 silkscreen-over-copper findings.
All 17 shorts involve front-side U1/U5/U6/J1 plated through pads meeting
back-side copper. J1 pins also enter JP2–JP5 courtyards. The packer reserves
declared courtyard sides, which misses these opposite-side features.

The 69 retained violations are 44 holes below the 0.30 mm minimum,
20 internal footprint pad-clearance violations, and five J2 copper-edge
clearance violations. These need separate source-CAD/manufacturing review.
The six schematic-parity warnings are the older schematic's legacy probe
markers versus equivalent canonical encodings in the board; independent
review checked decoded equality. They remain reported, not suppressed.

The original five ignored DRC checks remain unchanged: missing courtyard,
track centered on via, tuning-profile geometry, footprint-filter mismatch and
footprint-type mismatch. No DRC settings or pads were changed to obtain a pass.
The 14 physical-envelope obligations, electrical placement/locality, firmware,
thermal validation, routing and manufacturing acceptance remain open.

## Retained files and replay

`provenance.json` pins the board, software, seed and retained reports.
`SHA256SUMS` checks the packet bytes. `placement-result.json` includes the plan
and writer result. `candidate-comparison.json` identifies added/removed DRC
findings by type and native item UUID. Execution reports retain the original
workspace paths as historical evidence. `independent-review.txt` records the
separate review conclusion.

`replay-inputs.tar.gz` contains the exact original project settings, schematic,
library tables and 73 captured source inputs; no board is hidden in the archive.
For a native replay, run from this directory with KiCad 10.0.7 and a fresh
scratch directory (the example must not already exist):

```sh
sha256sum --check SHA256SUMS
mkdir "$HOME/.cache/pod-placement-regression-replay"
tar -xzf replay-inputs.tar.gz -C "$HOME/.cache/pod-placement-regression-replay"
cp rejected-candidate.kicad_pcb "$HOME/.cache/pod-placement-regression-replay/project/telemetry-pod.kicad_pcb"
KICAD_CONFIG_HOME="$HOME/.cache/pod-placement-regression-replay/config" kicad-cli pcb drc --format json --severity-all --schematic-parity --units mm --output "$HOME/.cache/pod-placement-regression-replay/drc.json" "$HOME/.cache/pod-placement-regression-replay/project/telemetry-pod.kicad_pcb"
```

An exit code of zero means DRC completed; inspect the findings. It does not
mean this board passes. Archive replay was checked against the retained
candidate report: all221 violation records and six parity records match exactly.
Seven of499 unconnected records select different same-net pads at identical
coordinates; all coordinate/net edge pairs match. `replay-verification.json`
retains those differing records. This is not byte-identical DRC output. To replay the
baseline instead, substitute the decompressed seed for the candidate PCB while
retaining all other inputs. The supported `agent_ee.placer_runner` rebuilds the
placement from that seed and `derived-policy.json`; it requires a fresh isolated
writable root, exact seed-hash authorization and a networkless sandbox.

Repair must reserve qualified through-board copper and mechanical occupancy
on their actual layers, and independently check the saved candidate. Blanket
mirroring of front courtyards, altered pads or weaker rules would not establish
a correct repair.
