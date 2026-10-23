# AGENTEE-489 source declaration (writer slice, ee489-source)

Verdict: PARTIAL. The source-bound reservations are declared in the agent-ee consumer schema, bound to the
immutable pod board snapshot, and accepted by agent-ee's own validate/bind/materialize/grade and the
envelope opt-in on the real pod source. They do not pass: required unknowns stay unknown, and four real
overlaps are reported on the v9 pilot snapshot. The production builder carries an opt-in, but it was not
regenerated end to end (gap G1).

Model and effort: claude-opus-5-5 (Opus 5.5), writer worker ee489-source.

## Files

| File | Role |
|---|---|
| `materialize.py` | Producer. It converts `../agentee-490-mechanical-inputs/bound-reservations.json` (agentee-490.bound-reservations/1, a recipe) into `reservations.json`. |
| `reservations.json` | `agent-ee.mechanical-reservations/1`, 34 rows, bound to `telemetry-pod/telemetry-pod.kicad_pcb` (captured as `mechanics/original-board.kicad_pcb`). |
| `unmaterialized.json` | The 10 required JP1..JP5 iron-access rows that the consumer cannot bind (see U1). They are NOT satisfied. |
| `consumer_check.py`, `consumer-check.json` | agent-ee consumer regression and its output on the real snapshot (fome-runtime, network none, native-admit). |
| `stackup-materials.json` | The agent-529 1f09c567@1 stackup material declaration with captured-source bindings and the NP-155F condition (declared, not consumed; see G3). |
| `../production-capture/build.py` | New opt-in `--mechanical-reservations` (`--out` only). It pins the three `mechanics/` files and adds `envelope.mechanical_reservations`. The default and `--check` paths are byte-unchanged. |

## Declaration rules applied

- Every row has classification `engineering` (author: this AGENT writer lane; recipe by agent-507). None is labelled manufacturer or owner.
- The owner statements are cited as "owner answers a13a1ba8@2 / 842b3689@1, relayed via AGENTEE-486 (agent-449), class owner-relayed": the 90 mm HEIGHT is an estimate, not a cap, and is not encoded as a limit; pogo/solder access is bench-only.
- Board-fixed vs attached: no board-frame rows are declared. The existing keepouts (In1, RF reference, antenna) stay in the envelope, and enclosure reservations are excluded (owner direction ~16:00Z via agent-519). All 34 rows are footprint-frame and attached with `self_exclusion: true`.
- Faces are `same`/`opposite` relative to the owner's snapshot side. Phases: installed, bench-fastening, bare-board-bench, bare-board-sd-access, bench-sma-attach.
- Cylinders are circumscribed 16-gons with vertices rounded outward to integer nm (a conservative per-face projection).
- UNKNOWN is never zero. Pogo tips with an open upper Z have `height_nm: null` and coverage unknown. Driver rows whose recipe states UNKNOWN tolerance have access `unknown`. The conditionals have `polygons_nm: null`, `required: true` and are each attached under their activation note:
  - J2 132134 part box and assembly expansion. The snapshot J2 is still the Molex 73251-1153 edge footprint, so the box is materialised only after the AGENTEE-485 rebind to `Agentee494.pretty/SMA_Amphenol_132134_Manufacturer` (2b65c583).
  - J1 internal mate/tail.
  - J3 card and flat tool. The 490 J3 study used an idealised 110x80 rectangle, not the saved Edge.Cuts (disclosed).
- Open 486 findings stay explicit: J1 mate (and K1 4.75+-0.15 vs the application spec's 2..5, unreconciled), J3 card/tool tolerance, and J2 slot vs board thickness (now J2 = vertical 132134, option A per agent-529 82f08e7a v1).
- Carried D2-1..D2-3 (agent-529 49106e9b v1):
  - D2-1: the L3 relief stays explicitly conservative at +0.021 mm. It was not regenerated here.
  - D2-2: installed-stage U2 axis/mount verification is NOT_RUN and is not a pre-fabrication gate.
  - D2-3: the historical "retain 0.335" text is superseded by the 0.293 adoption. That adoption is chief-engineering direction 4cf9d43d@2, not owner, and 37bc38d9@1 superseded the early-rebase ordering. The review-fix-map.json H1_2 label correction is NOT edited here, because this slice does not touch the 486 handoff (follow-up).

## Consumer evidence (consumer-check.json)

- `bind` succeeds against the native probe of board fa7c2ca6. The document sha256 is 106d6976...
- Full grade: status `defect`, 16 rows materialized, 18 required `unknown`, 4 defects. The defects are H3/H4 ISO7089 washer and ISO7380 head (F) overlapping the J1 courtyard on the v9 pilot snapshot. This is a real finding for 485 placement, not fixed here.
- Controls:
  - Refused: a stale board hash, a wrong owner UUID, a non-engineering classification, a stale envelope snapshot, and an uncaptured envelope input.
  - A missing required owner (H1 removed) gives `unknown`, not pass.
  - Attached rows move with their owner: H1 +10 mm gives a vertex shift of [10000000, 0], and the H2 polygons are unchanged.
  - A legitimate resolved-only subset (H1 washer F) grades `pass`.
- Envelope opt-in: `board_envelope.mechanical_reservations` binds the captured `mechanics/` layout (34 rows, source f354678d...).

## Unmet and gaps

- U1: the JP1..JP5 iron-access recipes (10 rows) are unbindable. The owners have custom pads (shape 6), which agent-ee refuses as attached owners. This needs a consumer change (agent-524) or a non-custom pad bound. These rows are listed as required and unsatisfied in `unmaterialized.json`.
- G1: production regeneration. `build.py` fails in fome-runtime:d96f8e00 at `qualify_manifest` (build.py:973, "captured CAD assignments unavailable or inconsistent"), with both agent-ee 7d5b0d4d and 935d854b. This step runs before the new branch, and the same failure occurs on `--check`. The earlier production logs ran in a different runtime. In addition, the production pin 7d5b0d4d predates the consumer (1177cbc2), so emitting this field needs a pin bump decided by the integrator. The opt-in is therefore wired but has not been exercised through build.py.
- G2: J2 geometry and the RF areas 460352a8/93d1ddf1 rebind, final pose, launch/antipad and native DRC are F7 duties in AGENTEE-485.
- G3: the stackup materials are declared but not consumed. The fab-profile stackup takes no per-layer material, so they need to go into the envelope's sourced stackup and through a regeneration.
- F6: adding 132134-revC.pdf (1ec1d365...) to canonical-parts acquisition through its producer is NOT done (named follow-up).
- F1 In1/In2 vertex counts remain due at add-planes (485).
- The power cluster is untouched (provisional, AGENTEE-497).
