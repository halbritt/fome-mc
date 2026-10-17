# Routing attempt: krt on fome-mc

- Backend: krt 0.23.1 (v0.23.1)
- Input: `fome-mc.kicad_pcb` from working tree @ 2864afbc90bd2bbfda7fb82b699cfc5e350794c0 (fingerprint 48c3eb26ea89c5b7)
- Scope: selected, 16 nets; protect: existing; budget 1500 s
- Candidate: `build/runs/route/fome-mc/trial-krt-continue/20261017T083752.440288Z/candidate/fome-mc/fome-mc.kicad_pcb`

| Result | Status | Detail |
|---|---|---|
| process | PASS | exit 0, 328.006 s |
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

- KRT moves copper gr_text and net-less copper graphics to silkscreen (not switchable on the CLI); the copper_graphics preservation check reports it
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class

Route statistics:

```json
{
 "new_tracks": 0,
 "new_vias": 0,
 "new_track_length_mm": 0,
 "new_track_length_mm_by_layer": {},
 "new_copper_nets": 0,
 "removed_existing_tracks": 0,
 "removed_existing_vias": 0
}
```
