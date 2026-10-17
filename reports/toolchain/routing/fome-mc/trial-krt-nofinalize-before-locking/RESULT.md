# Routing attempt: krt on fome-mc

- Backend: krt 0.23.1 (v0.23.1)
- Input: `fome-mc.kicad_pcb` from git revision HEAD (351339cf91ab375f7a1747185ba37c836dc6ab72) @ 351339cf91ab375f7a1747185ba37c836dc6ab72 (fingerprint e1bfff18bc32e4b7)
- Scope: all, 448 nets; protect: existing; budget 1500 s
- Candidate: `build/runs/route/fome-mc/trial-krt-nofinalize/20261017T054730.240303Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 3, 1377.381 s; KRT --strict-sizes: it reports delivering geometry below a requirement (candidate kept for grading) |
| routing | INCOMPLETE | 14 unconnected in scope, 14 total (input: 235) |
| validation | FAIL | 19 new DRC violations: starved_thermal 16, track_dangling 2, via_dangling 1; preservation protected_copper: 2899 tracks and 879 vias designated (all pre-existing copper); max deviation 0 nm; 138 missing or altered; preservation new_copper_netclass_geometry: 2934 new tracks and 426 new vias checked against their net class width / via diameter / drill (1 um quantisation tolerance); 12 below |

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
| protected_copper | FAIL |
| new_copper_netclass_geometry | FAIL |
| routing_scope | PASS |

Native DRC (original rules and severities):

```json
{
 "violations_total": 240,
 "parity_total": 382,
 "new_violations": {
  "count": 19,
  "by_type": {
   "starved_thermal": 16,
   "track_dangling": 2,
   "via_dangling": 1
  },
  "by_severity": {
   "warning": 19
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
 "new_tracks": 2934,
 "new_vias": 426,
 "new_track_length_mm": 9355.682,
 "new_track_length_mm_by_layer": {
  "B.Cu": 1633.387,
  "F.Cu": 2603.747,
  "In1.Cu": 2999.354,
  "In2.Cu": 2119.194
 },
 "new_copper_nets": 167,
 "removed_existing_tracks": 121,
 "removed_existing_vias": 17
}
```
