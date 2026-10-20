# Electrical locality evidence

The 90 × 65 mm double-sided packing candidate contains all 331 footprints under its declared overhang policy, but geometric packing does not establish a usable electrical layout. These boards are retained diagnostic artifacts, not adopted project boards or routing inputs.

The baseline places the explicitly assigned U14 core bypass capacitors C64/C65 about 73–75 mm from their supply balls. C66/C67 IO bypass distances are about 32–37 mm. The storage-candidate README identifies their local bypass roles. This is a concrete placement deficiency; it is not evidence that the complete design cannot fit.

The U26-only experiment constrains C97/C98 footprint origins to within 5 mm of U26. Both pass that screen and retain their mounting side, but supply-pad distances are still 5.589 and 6.791 mm, down from 14.267 and 13.677 mm. Origin distance alone does not establish direct bypass. The 5 mm radius is an engineering experiment, not a manufacturer limit.

The retained checker measures all seven explicitly assigned U26/U14 capacitors against matching native supply and ground pads. It checks saved net labels, not independently verified pin functions or routed connectivity. Straight-line pad distances are lower bounds on routes; nearest ground-pad distance does not establish a return loop. Orientation, vias, planes, actual loop geometry and impedance remain unevaluated.

## Reproduce the geometric measurements

Use the system Python with KiCad pcbnew available:

```sh
/usr/bin/python3 check-bypass-geometry.py baseline.kicad_pcb > /tmp/locality-baseline.json
/usr/bin/python3 check-bypass-geometry.py u26-constrained.kicad_pcb > /tmp/locality-u26.json
sha256sum -c SHA256SUMS
```

Compare parsed JSON against the corresponding retained bypass-geometry files. The checker does not save or mutate the input board. Independent reviews confirm all seven baseline assignments and exact replay of the constrained measurements.

## Native checks and remaining work

The U26 experiment completed in 782.642 seconds using an unreleased frozen AGENTEE-318 source snapshot. Independent review verified all 331 references, mounting sides, pad identities, geometry and nets, and exact placement write scope. Fresh DRC with unchanged original project settings reports 127 violations: 44 drill, 20 clearance, five copper-edge, 15 silk overlap and 43 silk-over-copper. There are 499 unconnected items and six legacy schematic-parity warnings. There are no reported shorts, through-hole courtyard collisions or mask bridges. This is not a clean DRC or fabrication release.

The original 8 mm U14 grouping attempt exhausted its search at C66 after 7,039 candidates and six backjumps (410.591 seconds). The search result itself did not prove infeasibility. Subsequent independent geometry review proved that this local policy cannot accommodate the five capacitors: U14 has a 13.5 × 15 mm courtyard; the two larger capacitors require opposite side strips and each excludes the smaller capacitors on that side. This says nothing about whole-board infeasibility. The original proposal is preserved in `rejected-8mm-groups.json`.

`next-groups.json` corrects the engineer-proposed U14 radius to 9 mm while retaining the U26 group. `local-witness.json` records an isolated six-footprint arrangement with a maximum origin distance of 8.485452 mm and pairwise separating gaps of at least 0.25 mm. The witness uses mathematical transforms of native-extracted rectangles; it is not a saved native-board DRC result, a complete-board placement, or electrical acceptance. The reviewed proof and its assumptions are in `independent-failure-review.md`.

The full-board 9 mm experiment result is not included here. General rules, fixed anchors and overhang declarations remain unchanged. The radius correction fixes an infeasible engineering proposal; it does not waive any manufacturer layout requirement or native DRC rule.

Pending source integration, electrical placement, existing rule conflicts, silkscreen repair, physical-envelope validation, routing, thermal/EMC qualification and manufacturing review remain open. No component purchase, project upload or fabrication is authorized by this packet.
