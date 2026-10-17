# Routing attempt: freerouting on route-fixture

- Backend: freerouting v2.5.0 (freerouting-2.5.0.jar b647a2f824cfbc54bc4dcaee71b03b7cd945eb76)
- Input: `route_demo.kicad_pcb` from working tree @ 3cb485925655a3ee06b11a2401fd9f78712a20ec (fingerprint ba2f343c49e2f971)
- Scope: selected, 2 nets; protect: existing; budget 180 s
- Candidate: `build/runs/route/route-fixture/smoke-freerouting-netclass/20261017T093631.096096Z/candidate/route_demo/route_demo.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 4.435 s |
| routing | COMPLETE | 0 unconnected in scope, 3 total (input: 6) |
| validation | PASS | no new findings |

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
 "violations_total": 0,
 "parity_total": 0,
 "new_violations": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
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

- Freerouting never rips up pre-existing copper (KiCad exports it as fixed/protected); --protect locked behaves like --protect existing
- Specctra carries per-class width/clearance/via only: custom .kicad_dru rules, diff pairs and length tuning are not exported; KiCad DRC grades them
- rule areas export only their no-tracks/no-vias restrictions; zones export as plane outlines
- route_demo.kicad_dru: net-class-to-net-class clearance rules are translated to Specctra class_class rules; any other custom rule is listed as untranslated below

Route statistics:

```json
{
 "new_tracks": 11,
 "new_vias": 1,
 "new_track_length_mm": 45.703,
 "new_track_length_mm_by_layer": {
  "F.Cu": 45.703
 },
 "new_copper_nets": 2,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
