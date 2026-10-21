# Placement seed for the microSD source (forward-annotated, 2026-10-21)

Adoption-grade seed lineage for `../storage-microsd/` (owner decision 2026-10-21: eMMC
dropped), produced on released agent-ee main `f92d71c` (`source-commit.txt`):

1. `staged-microsd.kicad_pcb.gz`: `../probe-import/staged-board.kicad_pcb` forward-annotated
   with `../storage-microsd/native.xml` (`agent_ee.forward_annotation plan` + `apply`,
   records `forward-annotation-plan.json` / `forward-annotation-apply.json`, 0 findings):
   1 add (J3, staged beside the outline), 23 removes, 7 in-place net renames
   (`EMMC_*` → `SD_*`), 1 new net (`SD_CD`), 16 pad net changes, 6 probe migrations,
   304 retained. Footprint manifest `footprint-manifest.json` is
   `../board-preflight/footprints.json` plus `Connector_Card` (every member re-hashed
   against `../storage-microsd/inputs/footprints/`).
2. `base-seed.kicad_pcb.gz`: the same board with `side-assignment.json` applied
   (`../placement-inputs/side-assignment.json` minus the removed references, `storage`
   group = J3 + R46–R50, R55, C64, C65 on B) and the four historical anchors of
   `../placement-inputs/anchors.json`. 309 footprints: 162 F, 147 B.

Uncompressed SHA-256 in `uncompressed-sha256.txt`. The packer seed of a placement
iteration is this base seed plus that iteration's cluster anchoring (see
`../placement-candidate/iteration-5/inputs/`). No placement, routing or qualification
is claimed here.

3. `base-seed-viapatched.kicad_pcb.gz`: the base seed with the D-PCB-1 thermal-via patch
   applied by `via-patch.py` (44 pads 0.20 -> 0.30/0.70 mm on U1, U5, U6, U7, U12), which
   removes the 44 `drill_out_of_range` findings every candidate has carried. Use it as the
   input of the next placement pass, together with the D-PCB-13 `Connector_Card` footprint
   (courtyard over the inserted card) and the D-PCB-8 silk policy on the saved board.
