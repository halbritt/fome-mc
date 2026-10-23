# J1 board-side mechanical evidence on candidate 5504a022 (AGENTEE-446, lane ee446g)

This packet is design evidence for two AGENTEE-446 board-side items on the current accepted
candidate:

- **(a)** finished hole, plating and registration;
- **(b)** board-lock/retention and solder tails of J1 (TE AMPSEAL 1-776163-1).

Items (c) and (d) are **deferred: needs the placed candidate** (agent-449 lane scope, after
agent-521's campaign decision):

- (c) U3 maximum-envelope clearance;
- (d) vibration mounting, design part, linked to AGENTEE-447.

Nothing was placed, routed, moved or edited. No footprint, track, zone, board geometry, captured
source, historical receipt or `production-capture/` file changed. The values are the board's own
nominal native values and the geometry of TE's customer view model. This packet makes **no claim**
of TE compliance, seating, retention, assembled clearance or vibration fitness.

The machine-readable record is `evidence.json`. Run `python3 -I check.py --self-test` to verify
it. The check:

- verifies `SHA256SUMS` against the packet;
- recomputes every binding and source hash from the repository bytes;
- requires each row's board values to equal those derived from `logs/native-facts.json` and
  `logs/boardlock-faces.json`;
- enforces the reporting rules: TE page/section, a fixed verdict set, a named missing source for
  each unknown, relay labels, no owner-stated text, and (c)/(d) deferred.

The self-test also requires 34 negative controls to be rejected: 18 for the packet and 16 for the
addendum below.

**Source-capture addendum (agent-521 c13da285; coordinator decision, not owner text).** See
`ADDENDUM-c13da285.md` and `addendum-c13da285.json`; the captured bytes and their licence note are in
`sources-c13da285/`. It captured JLCPCB's official capabilities page. TE 108-1329 returned HTTP 403, so that fact
stays UNKNOWN. The addendum then compares each fact with the rows below:

- No concrete incompatibility.
- a9 → consistent.
- a11 → no TE requirement.
- a2, a4, a7 → documented uncertainty (published tolerance bands do not nest).
- a6, b1 and registration stay unknown.

The tables below are the accepted packet as reviewed; the addendum supersedes their verdicts where it says so.

## Binding (recomputed from the bytes before any check)

| Identity | Value |
| --- | --- |
| Candidate | `5504a022417b5bf49ad6b1cec7f39f65bd3f8a566e46a286bb656904bef837ba` (printed by `runtime_receipt.py check`) |
| Retained commit | `2bd0f5c71abfce9a7a1a116edd5c1648521dd34a` (ancestor of this branch) |
| `production-capture/evidence/emission-7d5b0d4d/MANIFEST.json` | `161f71b0b1438830885a9f0badb0c913e17b55083f8216113483efe186b6d81f` |
| Schematic `telemetry-pod/telemetry-pod.kicad_sch` | `f5840ecc8a44a2e36cd05da9c3a14d80074919f441c3ef73a107dc98d5aea6a2` |
| Runtime receipt `production-runtime-j6b/receipt.json` | `31ce57f6ab16e338477657f63f5e2e802d2bf855102990228ceca187230521f1` |
| **Board** `telemetry-pod/telemetry-pod.kicad_pcb` (= retained `design/project/telemetry-pod.kicad_pcb`, MANIFEST `emission.board`) | `2f1c955704ab1fb38217c24cbaf5a45f4219a74a6a2309be710452c54db3b673` |
| Fab profile `production-capture/sources/fab-profile/fab-profile.json` | `02e484728bbcf695422ab2aa70ff3923ddd82b871fc28715aa1e9e9104822632` |

`retain.py --check` and `runtime_receipt.py check` were run before and after the work, and each
exited 0 (`logs/retain-check-*.log`, `logs/runtime-receipt-check-*.log`). The TE sources and the fab profile were
re-hashed with `sha256sum -c` (`logs/sources-sha256-check.log`, exit 0):

| Source | sha256 |
| --- | --- |
| 114-16016 rev S3 | `645a74cb…0c55` |
| 2293782 rev E5 | `a692de19…6aea` |
| 776163 rev K1 | `7ed1f2a5…85a7` |
| CVM_776164-1 rev F STEP zip | `be5ceb67…d537` |
| header STEP rev T | `43ba1f80…a473` |
| the relayed decision record | `e190ade5…9ac2` |

The CVM_776164-1 file is the mating plug. It is still unbound and is not used here.

**Native pose on this board** (pcbnew, KiCad 10.0.7, in `fome-runtime:d96f8e00`):

- **J1** `PodConnector:AMPSEAL_35_1-776163-1`: at (45.0, 55.5) mm, 0°, F.Cu, locked. It is a fixed
  placement, taken from the envelope's `fixed_footprints` entry: bottom edge, inset 9.5, position
  45, tolerance 0.
- **U3** `RF_GPS:ublox_NEO`: at (95.25, 1137.92) mm, unlocked, far outside the board outline
  (Edge.Cuts bbox −0.05..90.05 × −0.05..65.05 mm). U3 therefore has **no placement on this
  unplaced candidate**.

## What changed since adfb7668 (iter8t / j6b2-r1): nothing for J1 or U3

The probe loaded the current board 2f1c9557 and the prior board adfb7668 (`git show
5d923c5:telemetry-pod/telemetry-pod.kicad_pcb`). Each was a snapshot copy with its own
`.kicad_pro`/`.kicad_dru` under `build/runs/ee446g/`. For J1 and U3, the two boards have:

- equal native footprint-local geometry digests (pads, graphics, models);
- equal footprint text-block digests (uuids, nets and the footprint's own pose removed);
- equal poses.

| | J1 | U3 |
| --- | --- | --- |
| geometry digest | `d60e5206…017e` | `a0bdc928…7e6b` |
| text-block digest | `de49f0cb…e4d3` | `6f32b6e6…a472` |

J1's pads equal the captured library footprint (`a0982315…`, byte-identical in `PodConnector.pretty`
and the emitted design). The earlier evidence below therefore applies unchanged and is **reused,
not repeated**:

| Ref | Reused evidence | Where |
| --- | --- | --- |
| R1 | `j1.native_inspection` **on this very board** (35 PTH 1.75/2.4, annulus 0.325, NPTH 2.85 at (±28.5, +0.5), grid matches K1 sheet 2) | `production-capture/evidence/emission-7d5b0d4d/pipeline.json` (`f1f67fc7…`) |
| R2 | j6b2-r1 nominal pattern, 35 PTH + 2 locators vs K1 | `review/coordinates.json`, `review/geometry.md`, `review/candidate-review.md` |
| R3 | Model solder tails (35 axes r 0.65, 3.50 mm projection, two support flats), the `check_model.py` seating refusal and the 0.0362 mm exporter datum shift | `../README.md`, `../check_model.py`, `production-capture/evidence/model-check-j6b/` |
| R4 | Native J1 (rev T STEP) and U3 (NEO-M9N, visual-only) model resolution and poses | `pipeline.json` `models.candidate_resolution`, `model-check-j6b/facts.json` |
| R5 | Board-lock shaft sections of the header STEP | `review/boardlock-sections.json` |
| R6 | TE drop custody and lead-claim verdicts | `mating-interface/interface.json`, `mating-interface/README.md` |

## (a) Finished hole, plating and registration

| Row | Check | TE / fab source (page, section) | Board value (native) | Verdict |
| --- | --- | --- | --- | --- |
| a1 | Plated-hole finished Ø | S3 p.9 §3.6.A Fig. 13a "Ø1.75 ±0.1 After Plating", 35 places; K1 sh. 2 "35X Ø1.75±0.1 AFTER PLATING" | 35 PTH, drill 1.75 (KiCad PTH drill = finished hole) | consistent (nominal) |
| a2 | Fabricator finished-hole tolerance vs ±0.1 | S3 p.9 Fig. 13a; FAB has none | 1.75 | **unknown**: JLC PTH finished-hole tolerance not captured |
| a3 | Pattern and position, Ø0.1 (S) to datum A (S) | S3 p.9 Fig. 13a (pitch 4, rows 4/4, stagger 2, 0.5, 6.5); K1 sh. 2 | all 35 at the K1-derived coordinates (R1, R2, probe) | consistent (nominal) |
| a4 | Fabricator drill position / registration | S3 p.9 Fig. 13a Ø0.1; FAB has none | nominal exact | **unknown**: JLC drill-position and registration tolerances not captured |
| a5 | Locators Ø2.85 ±0.08, 2 places, Z = 57.0 | S3 p.9 Fig. 13a and its table; K1 sh. 2 | 2 NPTH 2.85 at (±28.5, +0.5), 57.0 apart | consistent (nominal) |
| a6 | Locator plating | S3 p.9 / K1 sh. 2: "after plating" is on the Ø1.75 callout only | NPTH, no copper | **unknown**: TE states none (108-1329 not captured). NPTH is a design assumption, not a mismatch |
| a7 | Fabricator NPTH tolerance vs ±0.08 | S3 p.9 Fig. 13a; FAB has none | 2.85 | **unknown**: JLC NPTH tolerance not captured |
| a8 | Board edge 9 from the locator centreline | S3 p.9 Fig. 13a "Edge of PC Board" 9; K1 sh. 2 dashed line, 9 | 9.0 / 9.0 mm to Edge.Cuts | consistent (nominal) |
| a9 | Land size and annular ring | S3 p.9 and K1 sh. 2 give hole callouts only; FAB has no PTH ring minimum | 2.4 lands on every copper layer; nominal annulus 0.325 (0.275 at TE max hole 1.85, arithmetic only) | **unknown**: JLC minimum PTH annular ring not captured. TE prescribes no land |
| a10 | Plating present | S3 p.9 "After Plating" | 35 PTH, copper on all layers | consistent |
| a11 | Hole-wall plating thickness | neither S3 nor FAB states one | not a board-file property | **unknown** |
| a12 | Hole-to-hole vs fab minimum | FAB `holes`: "pad / hole / hole: 0.45 mm" | min J1 hole-wall gap 2.25 (pins 1–2) | consistent |
| a13 | Copper to edge vs fab minimum | FAB `edge`: "routed / copper / edge: 0.2 mm" | min J1 land to Edge.Cuts 4.3 | consistent |
| a14 | Board thickness | S3 p.9 §3.6.A "1.57 mm"; relay b706da93 (owner-relayed, agent-drafted, unconfirmed); FAB ±10 % | 1.6 mm, 4 copper layers | **settled**: not reopened, no gate (AGENTEE-448 band 1.413–1.727 mm) |

## (b) Board-lock/retention and solder tails

These rows are design assumptions only. PCB retention force is never inferred from contact-wire
retention. The physical retention/pull test stays OPEN as a future bench item.

| Row | Check | Source (page, section) | Board / model value | Verdict |
| --- | --- | --- | --- | --- |
| b1 | Board-lock spec | S3 p.1 Fig. 1 names "Retention Leg" only. S3 pp.1–13 give no board-lock dimension, thickness range or force. K1 sh. 1 bottom view: two pegs, undimensioned. E5 is the plug drawing, with no header/PCB data | two Ø2.85 NPTH receive the pegs | **unknown**: TE board-lock spec (e.g. 108-1329) not captured |
| b2 | Peg vs a 1.6 mm board (**MODEL-ONLY**) | header STEP rev T: shaft radial ≤ 1.2992 at Y −11.72..−13.29 (R5); a +Y-facing snap-shoulder plane at raw Y −13.5 with 1.90 radial reach (`logs/boardlock-faces.json`, new); support flats at −11.72 | shoulder 1.78 mm below the seat, 0.18 mm below the nominal 1.6 mm underside; shaft Ø ≈ 2.60 in the Ø2.85 (min 2.77) hole | consistent (model-only design assumption; no force, engagement or TE claim) |
| b3 | Physical retention/pull | S3 p.5 §3.5.A.2 4.45/8.9 N is a contact-in-plug check, **not used** | none | open-bench |
| b4 | Primary attachment | S3 p.11 §3.6.B "The header assembly is designed to be fastened to the enclosure by four self-tapping thread-forming screws"; K1 sh. 1 note 1 | enclosure/panel are team design deliverables | open-design |
| b5 | Tail length vs thickness | K1 sh. 1 Section A-A "(3.0-4.0)", reference, from the seating plane to the tips; model 3.50 (R3) | about 1.90 mm below a 1.6 mm board (1.74–2.06 over 1.44–1.76). Even 3.0 > 1.76 | consistent (design assumption; no solder-joint claim) |
| b6 | Trim after soldering | relay d162e001, verbatim: "Assembly sequence described by owner: secure/seat the connector, tack-solder one pin, re-seat/align, solder remaining pins, trim excess lead stickout." (owner-relayed, agent-drafted, unconfirmed) | n/a | open-design (no trimmed length sourced) |
| b7 | Tail section vs hole | model tails r 0.65 (R3); S3 p.9 gives no tail dimension | hole 1.75 (1.65–1.85) | **unknown**: no TE tail dimension captured |
| b8 | Soldering process | S3 p.9 §3.6.A "compatible with any standard wave soldering process, which uses tin solder" | n/a | open-design (the relayed hand sequence is not addressed by TE; no incompatibility established) |

In b2, the model shoulder stays below the board underside across JLC's board-side 1.44–1.76 mm
range, by 0.34 to 0.02 mm. That is recorded arithmetic on a visual customer model. It is not a
gate and not a finding.

## Findings

**None.** No concrete, source-backed mismatch was found. Every unknown names its missing source.

## Observations (no change made)

- On the J1 board instance, the two pin-1 marker lines are on F.Fab; the captured library
  footprint has them on F.Silkscreen. Both boards are the same here. This is not hole, plating or
  tail geometry.
- The project rule `min_hole_to_hole` is 0.25 mm, below the captured JLC "pad / hole / hole:
  0.45 mm". J1 clears both (2.25 mm). That rule's provenance is outside AGENTEE-446.

## Open items

- **JLCPCB published values to capture** (rows a2, a4, a7, a9, a11):
  - PTH finished-hole tolerance;
  - NPTH tolerance;
  - drill position and registration;
  - minimum PTH annular ring;
  - hole-wall plating thickness.
- **TE board-lock/retention-leg specification** and supported PCB-thickness range (e.g. 108-1329;
  rows a6, b1).
- **Bench work:** physical retention/pull test and solder-joint inspection (b3).
- **Assembly instruction:** trim length and soldering process (b6, b8).
- **Enclosure/panel:** four-screw attachment per TE, a team design deliverable (b4).
- **(c)** U3 maximum-envelope clearance: deferred, needs the placed candidate. Any envelope from
  `neo-m9n-model` is VISUAL-ONLY.
- **(d)** Vibration mounting design part, linked to AGENTEE-447: deferred, needs the placed
  candidate. The vibration test stays OPEN.

## Reproduce

From the fome-mc root on proximal. Snapshots go under `build/runs/ee446g/{current,prior}/`: copy
`telemetry-pod.kicad_{pcb,pro,dru}`, and for `prior` use `git show 5d923c5:…`.

```sh
P=telemetry-pod/expansion/connector-candidate
~/.local/bin/native-admit run --label "ee446g native probe" --class test --weight 1 -- sh -c '
  exec docker run --rm --network none --label native-admission.lease=$NATIVE_ADMISSION_LEASE \
    --cpus $NATIVE_ADMISSION_CPUS --pids-limit $NATIVE_ADMISSION_PIDS --user $(id -u):$(id -g) \
    --tmpfs /tmp -e HOME=/tmp/home -v "$0:/work/fome-mc:ro" -w /work/fome-mc fome-runtime:d96f8e00 \
    python3 -I '"$P"'/board-side-ee446g/probe.py build/runs/ee446g/prior/telemetry-pod.kicad_pcb \
      build/runs/ee446g/current/telemetry-pod.kicad_pcb \
      --library '"$P"'/PodConnector.pretty:AMPSEAL_35_1-776163-1 --coordinates '"$P"'/review/coordinates.json' \
  "$PWD" > $P/board-side-ee446g/logs/native-facts.json
(cd $P && ~/.local/bin/native-admit run --label "ee446g boardlock faces" --class test --weight 1 -- \
  uv run --offline --no-project --python 3.12 --with cadquery==2.8.0 python -B \
  board-side-ee446g/boardlock_faces.py sources/c-1-776163-1-t-3d.stp > board-side-ee446g/logs/boardlock-faces.json)
python3 -I $P/board-side-ee446g/check.py --self-test
```

The image ID is `sha256:3d57118c…559c`, and the image has a tini entrypoint. Both outputs are
deterministic: the probe gave the same digest on repeated runs.
