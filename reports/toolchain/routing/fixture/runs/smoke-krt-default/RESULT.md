# Routing attempt: krt on route-fixture

- Backend: krt 0.23.1 (v0.23.1)
- Input: `route_demo.kicad_pcb` from working tree @ 3cb485925655a3ee06b11a2401fd9f78712a20ec (fingerprint ba2f343c49e2f971)
- Scope: all, 6 nets; protect: existing; budget 180 s
- Candidate: `build/runs/route/route-fixture/smoke-krt-default/20261017T093538.405739Z/candidate/route_demo/route_demo.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 4.855 s |
| routing | COMPLETE | 0 unconnected in scope, 0 total (input: 6) |
| validation | FAIL | 1 new DRC violations: clearance 1 |

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
 "violations_total": 1,
 "parity_total": 0,
 "new_violations": {
  "count": 1,
  "by_type": {
   "clearance": 1
  },
  "by_severity": {
   "error": 1
  }
 },
 "preexisting_violations": 0,
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
- KRT moves copper gr_text and net-less copper graphics to silkscreen (not switchable on the CLI); the copper_graphics preservation check reports it
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class
- backend reported: .kicad_dru: rule 'power_to_signal_clearance': clearance 0.4mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it

Route statistics:

```json
{
 "new_tracks": 14,
 "new_vias": 1,
 "new_track_length_mm": 117.87,
 "new_track_length_mm_by_layer": {
  "B.Cu": 0.028,
  "F.Cu": 117.842
 },
 "new_copper_nets": 5,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
