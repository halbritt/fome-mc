# AGENTEE-379 pod access-direction declarations (J3 declared; J1, J2, U1 unknown)

`declarations.json` holds the declarations in the form agent-ee's consumer reads
(`agent_ee_access_direction`, schema `agent-ee.access-direction/1`, agent-ee
`src/agent_ee/access_direction.py` at released main 1da27635; docs `docs/access-direction.md`).
No placement and no existing design file is changed; the property is applied only to copies by
`check.py`.

| Part | Status | Source |
| --- | --- | --- |
| J3 microSD (Hirose DM3AT-SF-PEJM5, PUSH-PUSH) | declared, class `board`, hard, no `travel_nm` | D-PCB-13 v2/v3 in `../design-rules/constraints.json` plus the F.Fab card outline of the patched footprint. The Hirose drawing is not in the repository, so no manufacturer/datasheet citation and no relaxing lane. |
| J1 AMPSEAL 776163 | unknown | TE drawing 776163 K1 gives the right-angle header and mouth direction (outward y+ in the footprint frame) but not the plug 776164 clearance or travel. |
| J2 SMA 73251-1153 | unknown | SD-73251-115 B3 web-extracted text covers 1150/1153 shared geometry; original PDF unavailable, cable/tool clearance unknown. |
| U1 ESP32 antenna | unknown | Cached manufacturer Hardware Design Guidelines HTML and figures give asymmetric antenna recommendations; board/feed orientation mapping remains unreviewed. |

The B-side J3 variant is the F-side variant with library y negated and outward `y-`; the
transform was confirmed on iter8n/iter8s (declared vector (-1,0), courtyard to x=-20.1).

Run (read-only on the board and on agent-ee):
`PYTHONDONTWRITEBYTECODE=1 python3 check.py --agent-ee <agent-ee checkout> --board <board> --out <dir>`

These runs are DIAGNOSTIC ONLY. On iter8n and iter8s (J3 pose 8.9, 32.0, 90 B), the assumed library mouth datum y=8.88 produces 0.22 mm² of inboard lane and a raw J3 access status of `defect`. The datum is not manufacturer-verified, so this is not an established manufacturer or physical design defect and does not authorize moving J3. The runner supplies no fixed-overhang policy; J1, J2 and U1 therefore also report `outside_outline`. The resulting `hard_fail` cannot establish design acceptance, design rejection, or a compulsory move. Changing the assumed datum to y=8.90 is a sensitivity probe only: the J3 access row passes, but the complete board verdict remains `hard_fail`. No travel is inferred and no outline relaxation is granted.

## Primary-source findings folded in (follow-up, no physical change, J3 fixed)

Source packet: `~/.cache/agent509-access-sources/` (REPORT.md sha256 50bb450e...). **Provenance:**
Hirose, TE and Molex content came from web-indexed or extracted text only; direct PDF downloads
returned 403 or timed out, so there are no original hashes and these are not manufacturer-original
citations. Only the Espressif HTML and PNG figures are hashed originals. Nothing is promoted to a
manufacturer-class declaration and no travel is inferred.

- **J3**: exact part is PUSH-PUSH (the footprint's push-pull description is wrong). Catalog common-datum
  positions give 4.00 mm lock-to-eject and 0.80 mm lock-to-overstroke; these are not full removal travel
  or finger clearance. The mouth datum 8.88/8.90 is not manufacturer-verified, so the 0.02 mm diagnostic discrepancy remains unresolved; it is not an established physical defect. No thermal claim (J3 manufacturer maximum temperature still to verify from an original).
- **J1** TE 776164-1: the 66 mm diameter (spec p. 8, Fig. 12) is the completed-plug pass-through opening,
  not mating stroke or lane depth; CPA/latch tool access is separate; numerical travel stays unknown.
- **J2** Molex SD-73251-115: the 1150 and 1153 plating variants share geometry, so the footprint suffix is
  not mismatch proof; cable and tool clearance unknown.
- **U1** Espressif figure: 6 mm antenna depth, 15 mm on the non-feed side, 2 mm / 1 mm maximum baseboard
  extents on feed/tip sides. Keep the feed-point orientation; not a symmetric 15 mm PCB blanket. The 15 mm
  housing clearance is a separate recommendation; applying it to this board still needs review.
