# Routing attempt: freerouting on fome-mc

- Backend: freerouting v2.5.0 (freerouting-2.5.0.jar b647a2f824cfbc54bc4dcaee71b03b7cd945eb76)
- Input: `fome-mc.kicad_pcb` from working tree @ c883c2f25166602499986fa153c262e27546c447 (fingerprint 48c3eb26ea89c5b7)
- Scope: selected, 16 nets; protect: existing; budget 600 s
- Candidate: `build/runs/route/fome-mc/trial-fr-on-krt/20261017T092247.075697Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 663.081 s |
| routing | INCOMPLETE | 16 unconnected in scope, 26 total (input: 26) |
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
 "violations_total": 239,
 "parity_total": 382,
 "new_violations": {
  "count": 0,
  "by_type": {},
  "by_severity": {}
 },
 "preexisting_violations": 239,
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
 "new_tracks": 1,
 "new_vias": 0,
 "new_track_length_mm": 0.005,
 "new_track_length_mm_by_layer": {
  "F.Cu": 0.005
 },
 "new_copper_nets": 1,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
