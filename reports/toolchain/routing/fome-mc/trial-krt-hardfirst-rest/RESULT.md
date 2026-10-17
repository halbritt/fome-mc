# Routing attempt: krt on fome-mc

- Backend: krt 0.23.1 (v0.23.1)
- Input: `fome-mc.kicad_pcb` from working tree @ 2864afbc90bd2bbfda7fb82b699cfc5e350794c0 (fingerprint 95850c271aab5576)
- Scope: all, 448 nets; protect: existing; budget 1500 s
- Candidate: `build/runs/route/fome-mc/trial-krt-hardfirst-rest/20261017T084836.861780Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 3, 1086.469 s; KRT --strict-sizes: it reports delivering geometry below a requirement (candidate kept for grading) |
| routing | INCOMPLETE | 20 unconnected in scope, 20 total (input: 219) |
| validation | FAIL | 9 new DRC violations: starved_thermal 8, track_dangling 1 |

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

Native DRC (original rules and severities):

```json
{
 "violations_total": 232,
 "parity_total": 382,
 "new_violations": {
  "count": 9,
  "by_type": {
   "starved_thermal": 8,
   "track_dangling": 1
  },
  "by_severity": {
   "warning": 9
  }
 },
 "preexisting_violations": 223,
 "resolved_violations": 11,
 "new_parity": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
 },
 "resolved_parity": 0
}
```

Unsupported or approximated by this backend:

- KRT moves copper gr_text and net-less copper graphics to silkscreen (not switchable on the CLI); the copper_graphics preservation check reports it
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class

Route statistics:

```json
{
 "new_tracks": 6260,
 "new_vias": 383,
 "new_track_length_mm": 8750.087,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1739.186,
  "F.Cu": 2212.828,
  "In1.Cu": 2640.367,
  "In2.Cu": 2157.705
 },
 "new_copper_nets": 147,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
