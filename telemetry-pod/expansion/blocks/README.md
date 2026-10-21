> **2026-10-21 (fourth fix):** the `gnss` block is dissolved into the residual set. U3 and L3 are fixed in the reviewed RF corridor (iteration 3/5: U3 facing J2 with the bias tee L3 on the line), and locked parts cannot be rigid-block members; the remaining members C42, D3, R24–R26, U10 pack as residual parts held near U3 by packing groups. 19 blocks.

> **2026-10-21 (third fix, from the AGENTEE-355 diagnostic):** C18 (1 µF on PRE_6V3, the U5/L1 output node; U7 is not on that net) left `buck-3v3` and R33 (10 k MCU_BOOT46 strap pull-down, whose only non-plane net is to the fixed U1, which cannot be a block member) left `mcu`; both are residual (C16/C20 on the same node stay in `supplies-5v`, where they are reachable). Members must be reachable from the block through non-plane nets.

> **2026-10-21 (second fix):** the supervision block lost C73/C74/R58/R59/U17 and the diagnostic block lost C113/R140-R143, which the microSD change removed (agent-449 found the stale entries from the 340 review). Every member is now checked against `../storage-microsd/native.xml`.

> **2026-10-21:** the eMMC was dropped for a microSD socket (`../storage-microsd/`): the `storage` block is now J3 + R46–R50, R55, C64, C65 anchored on J3, and the `storage-power` block (U15 cluster) is gone: 20 blocks. `derived-2b16feb-seed6f458cea.json` was derived from the eMMC source and is history until re-derived on the forward-annotated seed.

# Block allocation for the expanded telemetry pod (AGENTEE-339 input)

The expanded pod schematic is flat (one sheet, no hierarchy), so the two-level placer
(agent-ee AGENTEE-339/340) cannot derive blocks from sheets. `allocation.json` is the
engineer allocation file (`agent-ee.block-allocation/1`) derived from the functional
groups the migration emitter used to draw the schematic
(`../released-source-migration/emitter-layout.json`, `groups`), with these edits:

- the bucks take their own input capacitors (C1–C3 to `pre-6v3`, C8–C10 to `buck-3v3`),
  which the emitter had drawn with the power-entry stage;
- the CAN transceiver group is mapped to its migrated references (U100, D100, R100, C100);
- fixed anchors (J1, J2, U1, U2, H1–H4) and the test points are residual, because locked
  or fixed footprints cannot be rigid-block members;
- each block names its IC as the anchor where there is one.

21 blocks, 313 of 331 footprints; 14 residual. `derived-2b16feb-seed6f458cea.json` is the
read-only derivation by the AGENTEE-339 stage-A candidate (agent-ee commit 2b16feb, not
released) on the unlocked migration seed (board 6f458cea…) with the released-source-migration
`native.xml`; the derivation refuses locked members, so it must run on a seed where the
cluster parts are not locked (the cluster-anchored candidates lock them).

The regulator blocks here are the same member sets as the hand clusters in
`../placement-candidate/iteration-3/inputs/cluster-poses.json` (pre-6v3 = U5 cluster,
buck-3v3 = U7 cluster, storage-power = U15 cluster; wheel-input contains the U26 cluster
plus its conditioning parts). Their poses are search-derived and advisory until a block
library entry with manufacturer or qualified-board provenance replaces them (AGENTEE-342).
