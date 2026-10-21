# Placement candidate: cluster-anchored expanded pod (pending independent review)

**Status: REJECTED by independent review (`review/independent-review.md`, 2026-10-20); superseded by the next cluster-anchored iteration.** Produced 2026-10-20 by agent-499 under the owner's
direction to decide and proceed autonomously. It is the first expanded-pod placement that
meets the declared electrical bar; it still needs independent review, the J2 anchor
correction (D-PCB-4), silkscreen relocation (AGENTEE-320), plane planning and routing
before it can become the project board.

## How it was made

1. The four regulator clusters were placed by construction, not by search:
   - U5 and U7 (LMR36520) at agent-491's isolated-witness poses
     (`~/.cache/agent491-main-buck-locality/isolated-witnesses.json`);
   - U15 (TPS62162 with C70, L4, C68, C69) and U26 (LM2903B with C97, C98) at poses
     found by `inputs/solve.py`, a grid search over position and rotation that accepts
     only poses satisfying every pad obligation of
     `../electrical-locality/pad-obligations/electrical-locality.json` (rev 2) and a
     0.25 mm courtyard gap, using agent-ee's own footprint transform and courtyard boxes.
   `inputs/clusters.py` checks all four clusters: 33 pairs pass, no courtyard gap below
   0.25 mm. `inputs/anchor.py` chose cluster origins clear of the fixed anchors and the
   outline: U5 (15, 16) F, U7 (37, 16) F, U15 (10, 10) B, U26 (8, 26) F.
2. The 33 cluster footprints were written into the seed board with pcbnew and locked
   (`inputs/anchored-footprints.json`); re-reading the saved seed with pcbnew measures the
   same 33 pairs with 0 failures. `inputs/seed.kicad_pcb.gz` is that seed.
3. The **released** agent-ee origin-group packer (main `39a6b626…`, `inputs/source-hashes.txt`)
   placed the remaining 290 footprints with 41 fixed references and the five non-regulator
   groups (`inputs/request.json`), in 275.7 s: 5230 steps, 3 backjumps, judgment `pass`,
   group grading `pass`, 331 of 331 placed (`evidence/placement-*.json`).

## Checks on the candidate (board SHA256 `ed6ecdb0…93d974`)

| Check | Result |
| --- | --- |
| Pad obligations (33 pairs, independent `measure.py`) | 33 pass, 0 exceed, 0 unknown |
| Pad obligations, released AGENTEE-322 grader (agent-ee main `9c96a1f`, `electrical_locality.grade`) | pass: 33 measured, 0 defects, 0 unknown (the frozen 79cc1310 board grades 13 defects with the same code) |
| Native DRC, scaffold project rules (`evidence/native-drc.json`) | 331 findings: the 64 default-rule findings closed by D-PCB-1, 5 J2 copper-edge, 63 silk, 199 library-mismatch |
| Native DRC, cited rules, on a copy with the thermal vias patched to 0.30/0.70 (`evidence/cited-rules-drc.json`; the committed candidate itself still carries the unpatched 0.20 mm vias, so it shows 44 drill findings) | 267: 199 library-mismatch, 63 silk, 5 copper-edge; no clearance, courtyard or hole finding. The reviewer's own run on the unpatched candidate with the cited project: copper-edge 0, drill 44, silk 81, clearance/courtyard/hole 0 |
| Unconnected items | 499 (unrouted, as expected) |
| Routing readiness (`evidence/blocked-by.json`, heuristic) | 486 of 499 connections unobstructed |

The reviewer's run shows the J2 copper-edge findings vanish under the cited 0.30 mm edge rule;
the five in the packet's file came from a project copy that still carried the 0.50 mm default.
D-PCB-4 (J2 anchor 0.20 mm inboard) remains a seating-datum correction, not a DRC fix. The 63 silk findings
are field placement for AGENTEE-320. The 199 library-mismatch findings are the known
captured-library differences and are unchanged from every earlier board.

## Review outcome

Blocking: U15 and L4 are placed directly under the fixed IMU U2 through the board, and L1
sits 0.56 mm from U2 with L1 and L4 back-to-back; `inputs/anchor.py` checked only same-side
clearance. Should-fix: the GNSS RF corridor U3 to J2 is filled with the CAN cluster, and
F-side parts sit over the eMMC BGA where fan-out vias must go. The cluster internals,
courtyard spacing, pad obligations and fixed anchors were verified independently and hold.
The next iteration keeps the cluster poses and adds cross-side clearance, an IMU exclusion
zone, an RF corridor keep-out and a BGA fan-out keep-out.

## What it is not

Not routed, not reviewed independently, no planes, no thermal or EMC qualification, no
assembly review. Component sides are the packer's choice (169 B, 162 F). The RF path
(J2 to U3), the IMU (U2) and the antenna keep their historical fixed anchors. Adoption
requires the independent review in `review/` to come back without blocking findings and
the owner's design-change commit.
