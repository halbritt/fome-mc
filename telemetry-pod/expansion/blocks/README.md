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
