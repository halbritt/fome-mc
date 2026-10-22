# AGENTEE-379 pod access-direction declarations (J3 declared; J1, J2, U1 unknown)

`declarations.json` holds the declarations in the form agent-ee's consumer reads
(`agent_ee_access_direction`, schema `agent-ee.access-direction/1`, agent-ee
`src/agent_ee/access_direction.py` at released main 1da27635; docs `docs/access-direction.md`).
No placement and no existing design file is changed; the property is applied only to copies by
`check.py`.

| Part | Status | Source |
| --- | --- | --- |
| J3 microSD (Hirose DM3AT-SF-PEJM5) | declared, class `board`, hard, no `travel_nm` | D-PCB-13 v2/v3 in `../design-rules/constraints.json` plus the F.Fab card outline of the patched footprint. The Hirose drawing is not in the repository, so no manufacturer/datasheet citation and no relaxing lane. |
| J1 AMPSEAL 776163 | unknown | TE drawing 776163 K1 gives the right-angle header and mouth direction (outward y+ in the footprint frame) but not the plug 776164 clearance or travel. |
| J2 SMA 73251-1153 | unknown | Only the Molex product page for 73251-1150 is archived; sales drawing SD-73251-115 is missing. |
| U1 ESP32 antenna | unknown | Datasheet v1.8 p.10 Figure 3-1 shows a keep-out zone without dimensions; the Hardware Design Guidelines are not in the repository. |

The B-side J3 variant is the F-side variant with library y negated and outward `y-`; the
transform was confirmed on iter8n/iter8s (declared vector (-1,0), courtyard to x=-20.1).

Run (read-only on the board and on agent-ee):
`PYTHONDONTWRITEBYTECODE=1 python3 check.py --agent-ee <agent-ee checkout> --board <board> --out <dir>`

Measured result on iter8n and iter8s (identical J3 pose 8.9, 32.0, 90 B): the declared mouth
plane (courtyard front, library y 8.88) lands 0.02 mm inboard of the left edge because J3
sits at x=8.9, so 0.22 mm2 of lane is inboard and the check reports a defect. Moving the mouth
plane to y 8.90 (not sourced; sensitivity probe only) passes on both.
