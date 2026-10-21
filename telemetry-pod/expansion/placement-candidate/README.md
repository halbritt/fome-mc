# Placement candidate: cluster-anchored expanded pod (pending independent review)

**Status: candidate, not adopted.** Produced 2026-10-20 by agent-499 under the owner's
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
| Native DRC, scaffold project rules (`evidence/native-drc.json`) | 331 findings: the 64 default-rule findings closed by D-PCB-1, 5 J2 copper-edge, 63 silk, 199 library-mismatch |
| Native DRC, cited rules + enlarged thermal vias (`evidence/cited-rules-drc.json`) | 267: 199 library-mismatch, 63 silk, 5 J2 copper-edge; **no clearance, drill, courtyard or hole finding** |
| Unconnected items | 499 (unrouted, as expected) |
| Routing readiness (`evidence/blocked-by.json`, heuristic) | 486 of 499 connections unobstructed |

The 5 J2 findings are the edge-launch SMA whose anchor sits 0.20 mm too far outboard
(D-PCB-4 in `../design-rules/`); the fix is the anchor, not a rule. The 63 silk findings
are field placement for AGENTEE-320. The 199 library-mismatch findings are the known
captured-library differences and are unchanged from every earlier board.

## What it is not

Not routed, not reviewed independently, no planes, no thermal or EMC qualification, no
assembly review. Component sides are the packer's choice (169 B, 162 F). The RF path
(J2 to U3), the IMU (U2) and the antenna keep their historical fixed anchors. Adoption
requires the independent review in `review/` to come back without blocking findings and
the owner's design-change commit.
