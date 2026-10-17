# Routing attempt: krt on route_demo

- Backend: krt 0.23.1 (v0.23.1)
- Input: `route_demo.kicad_pcb` from working tree @ None (fingerprint 1f6c709d7d5cbe5a)
- Scope: all, 6 nets; protect: existing; budget 15 s
- Candidate: none

| Result | Status | Detail |
|---|---|---|
| process | FAIL | exit -15, 45.445 s; KRT exceeded the 15 s budget, did not stop at the stop file, and was killed (last output: 'No route found after 1000000 iterations (forward), trying backward...'); retry with a larger --budget or --backend-env KICAD_NET_RESCUE=0 |
| routing | NOT_RUN | - unconnected in scope, - total (input: -) |
| validation | NOT_RUN | backend produced no candidate |

Unsupported or approximated by this backend:

- KRT reads only a subset of .kicad_dru custom rules; every rule is still graded by KiCad DRC
- KRT moves copper gr_text and net-less copper graphics to silkscreen (not switchable on the CLI); the copper_graphics preservation check reports it
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class
- backend reported: .kicad_dru: rule 'power_to_signal_clearance': clearance 0.4mm has a non-layer scope (netclass/area/... condition) -- skipped, KiCad will still enforce it

