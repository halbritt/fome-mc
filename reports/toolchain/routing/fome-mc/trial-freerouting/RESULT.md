# Routing attempt: freerouting on fome-mc

- Backend: freerouting v2.5.0 (freerouting-2.5.0.jar b647a2f824cfbc54bc4dcaee71b03b7cd945eb76)
- Input: `fome-mc.kicad_pcb` from git revision HEAD (351339cf91ab375f7a1747185ba37c836dc6ab72) @ 351339cf91ab375f7a1747185ba37c836dc6ab72 (fingerprint e1bfff18bc32e4b7)
- Scope: all, 448 nets; protect: existing; budget 1200 s
- Candidate: `build/runs/route/fome-mc/trial-freerouting/20261017T054642.594262Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1258.338 s |
| routing | INCOMPLETE | 188 unconnected in scope, 188 total (input: 235) |
| validation | FAIL | 3 new DRC violations: clearance 2, shorting_items 1 |

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
 "violations_total": 235,
 "parity_total": 382,
 "new_violations": {
  "count": 3,
  "by_type": {
   "clearance": 2,
   "shorting_items": 1
  },
  "by_severity": {
   "error": 3
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

- Freerouting never rips up pre-existing copper (KiCad exports it as fixed/protected); --protect locked behaves like --protect existing
- Specctra carries per-class width/clearance/via only: custom .kicad_dru rules, diff pairs and length tuning are not exported; KiCad DRC grades them
- rule areas export only their no-tracks/no-vias restrictions; zones export as plane outlines

Route statistics:

```json
{
 "new_tracks": 323,
 "new_vias": 0,
 "new_track_length_mm": 845.701,
 "new_track_length_mm_by_layer": {
  "B.Cu": 238.481,
  "F.Cu": 607.22
 },
 "new_copper_nets": 99,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
