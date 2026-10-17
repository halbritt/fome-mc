# Routing attempt: krt on fome-mc

- Backend: krt 0.23.1 (v0.23.1)
- Input: `fome-mc.kicad_pcb` from git revision HEAD (e763e31eada62574871f0290775738c33ff529c5) @ e763e31eada62574871f0290775738c33ff529c5 (fingerprint e1bfff18bc32e4b7)
- Scope: all, 448 nets; protect: existing; budget 1200 s
- Candidate: none

| Result | Status | Detail |
|---|---|---|
| process | FAIL | exit -15, 1440.079 s; KRT exceeded the 1200 s budget, did not stop at the stop file, and was killed (last output: 'GND: (26.50,25.50) coincident link -- skipping the raw retry (zero-length bridge, #648)'); retry with a larger --budget or --backend-env KICAD_NET_RESCUE=0 |
| routing | NOT_RUN | - unconnected in scope, - total (input: -) |
| validation | NOT_RUN | backend produced no candidate |

Unsupported or approximated by this backend:

- KRT moves copper gr_text and net-less copper graphics to silkscreen (not switchable on the CLI); the copper_graphics preservation check reports it
- KRT's cleanup may neck wide new segments near foreign pads without a flag; the new_copper_netclass_geometry check reports any new copper below its net class

