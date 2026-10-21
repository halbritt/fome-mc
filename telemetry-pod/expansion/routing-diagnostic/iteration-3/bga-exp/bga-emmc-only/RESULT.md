# Routing attempt: builtin on bga-exp

- Backend: builtin 0.23.1 (owned-c6c09054f684)
- Input: `bg.kicad_pcb` from working tree @ None (fingerprint 80ddcdbd880043c7)
- Scope: selected, 14 nets; protect: existing; budget 600 s
- Candidate: `/home/halbritt/.cache/agent499-cluster-anchored/iter3/route/runs/bga-exp/bga-emmc-only/20261021T021925.704175Z/candidate/bga-exp/bg.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 229.174 s |
| routing | COMPLETE | 0 unconnected in scope, 499 total (input: 499) |
| validation | FAIL | preservation pour_integrity: 4 copper zones, 77 zone-connected pads compared on the refilled boards (min spokes 2); /+3V3@In2.Cu 5400.4 mm2 (-0.158 %), 13 polygons, 5.5 mm2 off the main pour; /EMMC_VCC_3V3@B.Cu 165.0 mm2 (+1386.454 %), 2 polygons, 10.7 mm2 off the main pour; /GND@B.Cu 1.1 mm2 (-99.304 %), 11 polygons, 1.1 mm2 off the main pour; /GND@In1.Cu 5430.4 mm2 (-0.157 %), 1 polygons; 4 isolated_island |

| Preservation check | Status |
|---|---|
| project_files | PASS |
| board_outline | PASS |
| layers | PASS |
| stackup | PASS |
| board_setup | PASS |
| nets_and_netclasses | PASS |
| pad_connectivity | PASS |
| footprints | PASS |
| zones | PASS |
| keepouts | PASS |
| copper_graphics | PASS |
| protected_copper | PASS |
| new_copper_netclass_geometry | PASS |
| routing_scope | PASS |
| net_completion | PASS |
| pour_integrity | FAIL |

Native DRC (original rules and severities):

```json
{
 "violations_total": 208,
 "parity_total": 0,
 "new_violations": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
 },
 "preexisting_violations": 208,
 "resolved_violations": 0,
 "new_parity": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
 },
 "resolved_parity": 0
}
```

Unsupported or approximated by this backend:

- KRT reads only a subset of .kicad_dru custom rules; every rule is still graded by KiCad DRC
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class
- backend reported: .kicad_dru: rule 'fine-pitch intra-footprint pad clearance (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U16 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U17 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U18 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it
- backend reported: .kicad_dru: rule 'supervisor intra-footprint pad clearance U19 (D-PCB-1)': clearance 0.15mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it

Route statistics:

```json
{
 "new_tracks": 126,
 "new_vias": 10,
 "new_track_length_mm": 151.125,
 "new_track_length_mm_by_layer": {
  "B.Cu": 79.422,
  "F.Cu": 71.704
 },
 "new_copper_nets": 8,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
