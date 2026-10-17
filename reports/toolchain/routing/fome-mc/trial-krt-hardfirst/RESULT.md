# Routing attempt: krt on fome-mc

- Backend: krt 0.23.1 (v0.23.1)
- Input: `fome-mc.kicad_pcb` from git revision HEAD (2864afbc90bd2bbfda7fb82b699cfc5e350794c0) @ 2864afbc90bd2bbfda7fb82b699cfc5e350794c0 (fingerprint e1bfff18bc32e4b7)
- Scope: selected, 16 nets; protect: existing; budget 1500 s
- Candidate: `build/runs/route/fome-mc/trial-krt-hardfirst/20261017T084502.572918Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 159.736 s |
| routing | INCOMPLETE | 5 unconnected in scope, 219 total (input: 235) |
| validation | FAIL | 2 new DRC violations: starved_thermal 2 |

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
 "violations_total": 234,
 "parity_total": 382,
 "new_violations": {
  "count": 2,
  "by_type": {
   "starved_thermal": 2
  },
  "by_severity": {
   "warning": 2
  }
 },
 "preexisting_violations": 232,
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

- KRT moves copper gr_text and net-less copper graphics to silkscreen (not switchable on the CLI); the copper_graphics preservation check reports it
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class

Route statistics:

```json
{
 "new_tracks": 364,
 "new_vias": 23,
 "new_track_length_mm": 655.078,
 "new_track_length_mm_by_layer": {
  "B.Cu": 23.199,
  "F.Cu": 251.646,
  "In1.Cu": 333.833,
  "In2.Cu": 46.4
 },
 "new_copper_nets": 12,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
