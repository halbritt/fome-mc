# Routing attempt: krt on fome-mc

- Backend: krt 0.23.1 (v0.23.1)
- Input: `fome-mc.kicad_pcb` from git revision HEAD (351339cf91ab375f7a1747185ba37c836dc6ab72) @ 351339cf91ab375f7a1747185ba37c836dc6ab72 (fingerprint e1bfff18bc32e4b7)
- Scope: all, 448 nets; protect: existing; budget 1500 s
- Candidate: `build/runs/route/fome-mc/trial-krt-nofinalize/20261017T061208.669111Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 3, 767.497 s; KRT --strict-sizes: it reports delivering geometry below a requirement (candidate kept for grading) |
| routing | INCOMPLETE | 26 unconnected in scope, 26 total (input: 235) |
| validation | FAIL | 18 new DRC violations: starved_thermal 14, track_dangling 2, via_dangling 2 |

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
 "violations_total": 239,
 "parity_total": 382,
 "new_violations": {
  "count": 18,
  "by_type": {
   "starved_thermal": 14,
   "track_dangling": 2,
   "via_dangling": 2
  },
  "by_severity": {
   "warning": 18
  }
 },
 "preexisting_violations": 221,
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
 "new_tracks": 6386,
 "new_vias": 415,
 "new_track_length_mm": 9074.457,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1417.753,
  "F.Cu": 2493.874,
  "In1.Cu": 2986.548,
  "In2.Cu": 2176.282
 },
 "new_copper_nets": 159,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
