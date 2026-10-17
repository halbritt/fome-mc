# Routing attempt: freerouting on fome-mc

- Backend: freerouting v2.5.0 (freerouting-2.5.0.jar b647a2f824cfbc54bc4dcaee71b03b7cd945eb76)
- Input: `fome-mc.kicad_pcb` from git revision HEAD (e763e31eada62574871f0290775738c33ff529c5) @ e763e31eada62574871f0290775738c33ff529c5 (fingerprint e1bfff18bc32e4b7)
- Scope: all, 448 nets; protect: existing; budget 1200 s
- Candidate: `build/runs/route/fome-mc/trial-freerouting/20261017T052237.922324Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 1255.01 s |
| routing | INCOMPLETE | 199 unconnected in scope, 199 total (input: 235) |
| validation | FAIL | 64 new DRC violations: clearance 50, via_dangling 10, starved_thermal 3, track_dangling 1; preservation protected_copper: 2899 tracks and 879 vias designated (all pre-existing copper); max deviation 500 nm; preservation new_copper_netclass_geometry: 435 new tracks and 10 new vias checked against their net class width / via diameter / drill |

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
 "violations_total": 296,
 "parity_total": 382,
 "new_violations": {
  "count": 64,
  "by_type": {
   "clearance": 50,
   "via_dangling": 10,
   "starved_thermal": 3,
   "track_dangling": 1
  },
  "by_severity": {
   "error": 50,
   "warning": 14
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
 "new_tracks": 435,
 "new_vias": 10,
 "new_track_length_mm": 542.357,
 "new_track_length_mm_by_layer": {
  "B.Cu": 8.207,
  "F.Cu": 534.15
 },
 "new_copper_nets": 126,
 "removed_existing_tracks": 7,
 "removed_existing_vias": 0
}
```
