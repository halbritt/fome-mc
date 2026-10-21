# Iteration 3, derived: D-PCB-3 v3 via-in-pad + D-PCB-8 silk policy

`telemetry-pod.kicad_pcb.gz` is the reviewed iteration-3 candidate (board fc28ba79…) with
two non-placement edits applied by `../../../design-rules/evidence/d-pcb-3-v3/derive.py`:
U14's pads set to 0.22 mm and E7/G5/H10/J5/K8 made 0.15/0.25 mm through-hole via-in-pad
(D-PCB-3 v3), and the D-PCB-8 silk policy (29 references hidden, 12 footprint silk
graphics moved to Fab). Native DRC with `design-rules/telemetry-pod.kicad_dru`:
silk findings 58 -> 0; new findings are only the 6 clearance + 4 pth_inside_courtyard
between U14's via-in-pad sites and U1's F.Cu pads 19-22 (cross-side conflict; the next
seed must place U14's interior away from U1's pad rows, which the patched footprint lets
the packer enforce). It is a reference for the next seed, not a routing input: the
iteration-3 review hash and its routing receipts apply to the parent board only.
