# Production capture for the Rev-3 microSD pod (AGENTEE-207/197)

This directory captures the electrical and mechanical inputs a production pod run needs, for the
current microSD source (`../storage-microsd/`, 305 references). Phase B then runs the genuine
agent-ee producers on the capture and stops at the real `pod_driver` dry run. It is capture and
composition evidence. No placement, routing, campaign or model ran, and nothing is accepted.

**Status (j6b2, agent-ee main `7d5b0d4d`, the AGENTEE-466 runtime, run in its own image; j6 and j6b ran on
`81e387ee`, which predates the AGENTEE-454 read-once fix).** The authentic two-iteration production preparation exists. The
production scope (compiled Rev-3 microSD scope plus the assembly, blocks, envelope and requirement-source
layers) prepares with the plan of record: the real `pod_driver.build(dry_run)` returns `prepared` and its
driver receipt and campaign carry `max_iterations` 2 (source `plan`), routing backend budget 900 s, routing
timeout 2100 s, placement `timeout_s` 1500 s and the derived watchdog `max_seconds` 8400 s (source
`derived`, `2 * (2100 + 300) + 3600`; it changes none of the budgets). The production schematic is then
emitted and forward-annotated by the campaign's own schematic-stage steps with stage receipts (AGENTEE-445):
305 components and 235 nets, now the telemetry-pod project (`retain.py`). No campaign was launched; no
placement, routing or model ran. Nothing here is acceptance: every check of the checks-only dry run is
`stage_not_reached` on the empty scaffold, the final guard blocks on the five staged envelope obligations,
POD-AC-5 stays NOT CHECKED, and the four library-block obligations stay unresolved.

## j6b2: the AGENTEE-466 runtime, its binding receipt (review H1) and relayed-decision labels (review H2)

The independent review of `5d923c5` held two items. The coordinators then superseded the producer: the
81e387ee runs b4 and b5 were TERMINATED-SUPERSEDED, because 81e387ee predates the AGENTEE-454 read-once fix.
Following the corrected order (agent-449 relaying agent-521 a9cb03ad/2fbe5f08, Cairn 154cc9f6; coordinator
decisions, not owner-stated), every source change was committed first (`338fbd7`). Then ONE preparation ran.
No campaign is launched.

- **Producer and runtime: agent-ee `7d5b0d4d` in its own image.**
  - `pipeline.py` pins `7d5b0d4d`, which contains the AGENTEE-454 read-once fix and the router pin
    `b5774496`.
  - The run used the AGENTEE-466 gate image, addressed by its proximal config digest `d96f8e00…`. Its c4 tag
    is `agent-ee:ci-b29cead1…`, its OCI index `6dd73b15…`, and its linux/amd64 manifest `85fc188c…`.
  - The run was `production_run.sh` under `native-admit --class suite --weight 4`. It executed
    `production_steps.py`, stopping at the first failure:
    1. `build.py --out`;
    2. the composition copied into the run's own fome-mc copy, then `build.py --check` (byte for byte);
    3. `pipeline.py` (28/28 stages accepted);
    4. `runtime_receipt.py observe`.
  - `ROUTER_CHECKOUT` is the image's own `/opt/kicad-route`.
- **H1 receipt.** `evidence/production-runtime-j6b/receipt.json` binds four things:
  - **the image**, by:
    - its config blob, recomputed from a `docker save` stream on proximal;
    - the proximal OCI manifest's config;
    - the layer tars equal to the config `rootfs.diff_ids`;
    - the c4 index → manifest → config relation, taken from the AGENTEE-466 evidence and its independent
      review (c4 itself is not contacted).
  - **the agent-ee source**: the image's `/opt/agent-ee` equals `git archive 7d5b0d4d`, file for file.
  - **the router**, as measured in the image: preflight, the source digest recomputed with the router's own
    `engine.source_sha256`, the extension bytes and the interpreter.
  - **the prepared plan, scope, campaign, driver receipt, prepared tree and initial candidate.** The campaign
    is validated by the runtime without launching.

  It also records the exact invocation, with its pre-launch identity check. `runtime_receipt.py check`
  re-verifies every binding.
- **Launchable prepared tree.** `retain.py` keeps the complete prepared directory (inputs, pre-receipts, dry
  run) as `prepared-tree.json`, with content-addressed `prepared-blobs/`. `--materialize-prepared OUT`
  rebuilds it; the rebuilt tree equals, file for file, the tree the runtime observed in the image.
- **Evidence naming.** The retention is `evidence/emission-7d5b0d4d/`. The superseded `emission-81e387ee/` is
  removed and stays in git history (`05783ce`, `5d923c5`).
- **H2, provenance, fixed in the generator.** The thickness, enclosure and harness open items were generated
  agent prose; j6 wrote them as "Owner decision 2026-10-22" and "(owner direction 2026-10-22)".
  - They now carry `owner-relayed, agent-drafted, unconfirmed` and cite the committed record
    `connector-candidate/mating-interface/sources/owner-decision-2026-10-22-board-thickness.txt` by sha256.
    That record is copied into the candidate.
  - They quote the Cairn relays verbatim wherever authority is used: `b706da93…`, `d162e001…` and
    `9561cd0c…`. `build.py` refuses unless each quote occurs in its own relay section.
  - Agent reasoning is labelled as such. The fabricator tolerance stays separate from the AGENTEE-448
    component-side fit. No thickness limit is adopted, and the 1.6 mm board choice is not reopened.
  - At `7d5b0d4d`, agent-ee's contract screens J1 board thickness itself (`tht_thickness_fit`) and no longer
    requires `thickness-tolerance`. The item stays as an extra open item for the relayed board-side checks.
    Dropping it is a reviewed decision.
  - The antenna obligation statement is agent-ee's contract text, which must match verbatim. It cites D-PCB-16,
    whose `design-rules/constraints.json` entry quotes the owner's 2026-10-21 wording; it is unchanged.
- **Count attribution** (report-only, `count_attribution.py`): `evidence/count-attribution-j6b2/`.

## j6b: bound models, initial candidate and the JP1-JP5 copper contract

This continued j6 on the same pin (`81e387ee`) and the same plan bounds; its evidence (`evidence/emission-81e387ee/`)
is superseded by j6b2 and stays in history at `5d923c5`. Everything below is carried by the j6b2 run.

- **FOMEMC-34 model binding.** The two models are recorded in `composition/project-models.json` and are visual
  or mechanical models only.
  - Both sit in the capture at `project/inputs/models/`. That is `${KIPRJMOD}/inputs/models/`, because
    KIPRJMOD is the candidate's `project/` directory.
  - **J1** is the exact-part header STEP `connector-candidate/sources/c-1-776163-1-t-3d.stp` (TE 1-776163-1
    rev T, `43ba1f80…`). It is checked to be the verbatim member of the captured TE archive recorded in
    `connector-candidate/sources.json`. Its pose (offset `(0, -31.8, 11.72)`, rotation `(-90, 0, 0)`) is the
    captured footprint's own and is quoted from the connector README.
  - **U3** is the `neo-m9n-model` visualization (`8a7f1984…`, datasheet-derived, not mechanical
    qualification). The captured `RF_GPS:ublox_NEO` member had no model. `build.py` derives the bound member
    by inserting exactly one zero-transform model node, recorded in `library-updates.json` `model_bindings`.
  - In j6 the J1 reference did not resolve: the file was at the candidate root `models/`, and agent-ee's
    inventory reported it `missing`. U3 had no model at all. The unreferenced root copy is no longer carried.
  - The CVM_776164-1 rev F file is the mating plug. It is recorded under `not_bound`, with agent-521's
    correction quoted verbatim. A mated view stays OPEN, and no transform is inferred.
- **Native checks on the candidate** (`candidate_checks.py`). Each is a `pipeline.py` stage that refuses on any
  deviation:
  - `models.candidate_resolution`: agent-ee's `models3d.inspect_models` resolves J1 on the initial scaffold
    board, and J1 and U3 on the emitted board. Both resolve to the bound bytes, from the project, and pcbnew
    reads the recorded poses.
  - `fab.copper_features`: agent-509's JP1-JP5 ruling (below).
  - `j1.native_inspection`: the iter8t J1 audit, rerun natively on this board.
  - `campaign.initial_candidate`: agent-ee's `candidate.capture` of `prepared/scope.json`, which is what
    campaign iteration 1 captures. It must equal the dry-run candidate's identity and file manifest. The
    result is also in `pipeline.json` under `initial_candidate`.
- **`model_check.py`** runs on the host. It exports J1 and U3 alone through `kicad-cli pcb export step`, so
  KiCad itself must load each model, and then reads each export with CadQuery 2.8.0.
  - **J1:** the `connector-candidate/check_model.py` criteria (35 tail axes on the drill coordinates, 35 tips,
    two support flats, 3.50 mm projection, envelope), graded against this board's own exporter datum.
  - **The fixture check, run unchanged:** `check_model.py` itself refuses on its absolute Z values. The
    candidate stackup exports the board body at 0..1.5162 mm instead of the fixture's 0..1.48 mm, so the model
    sits 0.0362 mm higher, with the same 0.085 mm body-to-support offset. That refusal is kept verbatim in
    `model-check.json`.
  - **U3:** 29 solids at the board's U3 pose, 24 castellation/pad overlaps and the pin-1 marker.
  - Neither check is a fit, seating or mating claim.
  - `evidence/model-check-j6b/` holds the result, its logs and the native facts for the installed board
    `adfb7668…`. The native STEP exports are not retained; they carry export timestamps, and their hashes are
    in `model-check.json`.
- **JP1-JP5 (agent-509 source decision, coordinator notes 2026-10-22).** The composed `fab_package` check
  declares `copper_features` JP1..JP5. These are on-board, normally-open copper: not BOM, not DNP, never dropped
  or relabelled. On the emitted design, `fab.copper_features` verifies:
  - agent-ee's own `fab_parts_manifests` cross-check (unsuppressed), which binds exactly JP1-JP5;
  - agent-ee's board and schematic copper predicates, which return no problems;
  - natively, for each jumper:
    - one `Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` footprint with two F.Cu SMD pads 0.3 mm apart;
    - the pads on the two distinct declared nets (pcbnew, and the kicad-cli netlist);
    - the footprint excluded from BOM and from position files, and not DNP;
    - the schematic flags `in_bom no`, `on_board yes`, `dnp no`;
    - no track, via or zone joining the two pads (the board is unrouted), so each jumper is open by default.

## j6: production preparation and emission at agent-ee `81e387ee`

(History, superseded by j6b2.) `evidence/emission-81e387ee/` held the run (`pipeline.json`, the driver receipt, campaign, plan, scope,
dry-run record and result under `prepared/`), the three emission receipts, the emitted design with every
emitter input (`design/`, `MANIFEST.json`), and `SHA256SUMS`. It was produced in the pinned agent-ee CI image
(`ae-ci-exec` on an `81e387ee` checkout, network none); `pipeline.py` first verifies that the agent-ee export
is exactly the tree of `81e387ee` (every blob by its git hash). What changed against the a9dac2f-era
pipeline, each found by running the integrated producers:

- **Plan schema.** `requirement_source` is now required. The plan selects `telemetry-pod-rev3`, whose pinned
  capture fome-mc keeps at `../requirements/compiled/requirements-map/` (spec `e71dcca7…`, record
  `1d978fc1…`); it is added to the scope as baseline sources (`requirements-source/`). The scope itself is
  compiled from the current microSD spec (`0f52e0ae…`), which is not a pinned source (its own selection
  refuses `unapproved-source`, kept in `scope-composition.json`). `pipeline.py` checks that the two records
  are equal in every requirement and prose entry except the added `POD-CD-STORAGE` decision row, and that
  the acceptance sets (POD-AC-1..11) are identical. The receipt's `requirement_set` binds Revision 3 and the
  four bench obligations.
- **Staged envelope obligations.** The five generic obligations (corner holes, height, harness edge, antenna,
  IMU separation) carry `coverage` records under agent-ee's reviewed source contract
  `telemetry-pod-expanded/1` (`build.py` `stage_obligations`): the four explicit H1-H4 hole witnesses, J1
  fixed, J1 containment and J1 `part-identity/1`, U1 fixed, U1 containment and the U1 antenna keepout, and
  every named open item (20 in all) as text. `scope.envelope_obligation_coverage` reports all five `staged`
  with every witness `bound`, and `require_qualified` refuses, naming every open item. Enclosure and harness
  fit are recorded as open design deliverables, not blockers, and the JLC 1.6 mm board choice is recorded with
  its thickness tolerance kept separate from the AGENTEE-448 component-side fit screening. Since j6b2 (review H2)
  these texts are labelled `owner-relayed, agent-drafted, unconfirmed` and cite the committed relay record with
  verbatim Cairn quotes (below); j6 had written "Owner decision 2026-10-22".
- **Parts membership.** A `parts_subset` check over `composition/parts.json` (requirement
  `POD-DERIVED-PARTS-MEMBERSHIP` at the manifest's declaration source) binds the J1 identity witness. The
  `fab_package` done check therefore declares the manifest's copper features (JP1-JP5), its bare-copper
  probes (`probe_manifest`, TP1-TP6) and the `JLCPCB_Assembly=not_assembled` exclusion binding-fill writes
  for the hand-fitted J1.
- **Antenna facts.** The `radio-antenna` keepout names an earlier `datasheet_facts` check `antenna-facts`
  (informational requirement `POD-DERIVED-ANTENNA-FACTS`); agent-ee grades that legacy dynamic keepout
  unknown, never pass.
- **Fab profile.** `composition/fab-profile.json` is the captured profile `02e48472…` with only each limit's
  `requirement` relabelled to this envelope's derived `R-envelope-expanded-pod-microsd-production-fab-profile`
  (agent-ee requires the profile's mapping to equal the scope's); values, tiers, stackup, tolerance and source
  citations are checked unchanged.
- **Hand-fit chain.** The scope's assembly check carries the declared J1 citation (`assembly/hand-fit-policy.json`),
  which `81e387ee` verifies (`category_selection`, both part-record links). The a9dac2f pipeline passed the
  validator's normalized output instead, which the scaffold refuses.
- **Emitter declaration.** `captures` is the candidate root. The a9dac2f-era `footprints` made
  emit-schematic fail on every library (`resolution_library_coverage`), so the first campaign iteration
  would have failed.
- **No surrogate.** The driver-default (10-iteration) probe plan and the compiled+assembly probe scope are gone.
  Stock is graded per id at generation: any id older than 24 hours, unobserved or failed refuses before
  composition (refresh it read-only; never substitute).

## History: a9dac2f (j3-j5c)

**Status (agent-ee main `a9dac2f3`, AGENTEE-439 released).** All 305 references are declared, J3
included. The genuine binding-fill accepts the writer intent with source-derived ratings. The
production scope (compiled Rev-3 scope plus the assembly and envelope layers) still refuses, on
exactly five envelope generator obligations that no agent-ee criterion binds yet (AGENTEE-177/179).
The plan of record carries the authorized bounded budget (`max_iterations` 2), which the pod driver
at this pin refuses (`max_iterations must be between 8 and 100`). Only the **preparation probe**
(compiled scope plus the assembly layer, driver-default budget) prepares. Its campaign carries
`rating_provenance`, is outside the authorized budget and is set aside as not launchable. The probe
is not the production scope. All 18 blocks repack with the derived request policy, as geometry
only. The two library blocks the engine refused (pre-6v3, buck-3v3, `copper_unknown`) carry
unresolved copper/native-check and witness-pose obligations into the scope and the review packet.

**j5 (review-pod-capture-chain HOLD).** H1: the binding-fill, emitter, annotation and planes
declarations now mount the export's `src`, and each declared module is imported from its actual
mount (the export root, the old declaration, fails as the control). H3: the library refusals are
source-bound obligations through candidate provenance, both scopes and the actual review packet.
H2 waits on agent-ee AGENTEE-197u. **j5b** (review-pod-capture-j5 HOLD): the obligation
identities are derived from the verified library refusals, and the cited library entry is verified by
bytes. **j5c** (review-pod-capture-j5b HOLD): one validator compares every block limitation with
its canonical source-bound line; any library output other than a verified refusal refuses; the
candidate's block identity and the seed board's captured bytes are verified (Blocks layer, below). Assembly: a fresh read-only JLC capture of all 81 BOM LCSC ids
(2026-10-22) and the J1 hand-fit source chain (`assembly/hand-fit-policy.json`), which agent-ee
`a9dac2f3` cannot express (a narrow agent-ee change is reported separately). POD-AC-5 stays NOT
CHECKED.

## What is captured (`composition/`, generated by `build.py`)

| File | Content | Validator outcome (agent-ee a9dac2f) |
| --- | --- | --- |
| `refs.json` | The 305 native references (intent ids, CAD, sheet), bound to the source schematic `4da27afc…` | 305 = intent = native netlist |
| `parts.json` (`agent-ee.parts/1`) | 305 references: 294 named canonical records (J3 now among them), 6 bare-copper probes and 5 copper features. Each is re-verified against the microSD intent. C40 carries the pilot's datasheet `source_selection` (ratings, below) | `validate_manifest`, `qualify_manifest`: CAD `ok/pass/complete`, 400 dependencies |
| `footprints.json`, `assignments.json`, `declarations.json` | The microSD CAD closure with the four D-PCB-1/13 patched footprints (`library-updates.json`). J3's assignment is new (`smd`, no connector grid), graded by `check_assignments` | Included in `qualify_manifest` |
| `part-refs.json`, `deviations.json` | Component id to part id for all 305; the J1 hand-fit deviation (decision below) | `part_decisions.validate_deviation` |
| `intent.writer.json` | The intent binding-fill reads: the original with its 174 `Qualification` fields, 98 pilot `AGENT_EE_Ratings` strings and J3's historical `Datasheet` URL moved to the ledger. `Power`/`Voltage` stay | Restores the original byte for byte (with field order) when the ledger is applied |
| `binding-ledger.json`, `binding-migration.json` | The ledger keyed by component id: source intent hash, exact original text and class of each limitation (166 identity-only, 5 package-selection, 2 series-divider, 1 historical J3), the field migrations, and a separate J3 annotation that leaves the historical statement intact. The migration record gives exact component and text coverage | `build.py` refuses any other text, count or change |
| `rating-sources.json`, `rating-facts.json`, `datasheet-source-selection.json` | The `--ratings` declaration: catalog plus the v9 pilot's documented C40 fact, cited from its selected KEMET PDF, with the pilot's pinned pdftotext (`88263e23…`, 24.02.0) | `passive_ratings.load_sources`; citation verified in the sandbox |
| `rating-comparison.json` | All 98 original rating records (the pilot's receipted report, `sources/pilot-ratings/binding-fill.json`) against the regenerated ones | 98/98 values equal; differences are explained per row |
| `j3-source.json` | J3's catalog row, the captured datasheet (record, acquisition, origin record), all failed acquisitions, the re-read detect mapping and the limitations | `jlc_stock_capture.validate_capture`, `part_record.qualify_record` |
| `envelope.json`, `antenna-facts.json`, `captured-rule-areas.json` | Unchanged from the previous capture except the parts hash the retention binds | `board_envelope.validate` structural pass; `load_retention` |
| `placement-policy.json` | The derived request policy (identity `b07059a5…`), unchanged | `refuse_policy_sources` |

`sources/` holds bytes not yet in the repository:

- `j3-datasheet/`: agent-509's J3 capture. It holds the DigiKey mirror of the Hirose DM3 Series MicroSD
  2010.6 catalog (`ab978e9d…`) with its `agent-ee.datasheet-capture/1` manifest (`795abc9d…`). It also
  holds the four failed acquisitions (Hirose 403s, LCSC and Mouser non-PDF) and their bindings. The
  record `C114218.part-record.json` was regenerated by `part_record` at the repository root. The
  origin record (`70525df3…`) from the volatile sourcing root differs only in its three paths, which
  `build.py` checks. `review/` holds the agent-509 J3, detect-mapping, audit and binding-composition
  notes.
- `pilot-ratings/`: the v9 pilot's binding-fill report, rating declaration, C40 fact and citation
  verification. These came from the volatile
  `/tmp/agent469-coordination/pod-campaign-v1/driver-preparation-v9-90x65/inputs/`.
- `rating-sources.json`: the captured catalog-only declaration
  `{"schema":"agent-ee.passive-rating-sources/1","catalog":true,"facts":null,"extractor":null}`.
- `pilot-assembly-stock/`: the v9 pilot's `agent-ee.jlc-catalog/1` producer capture (`catalog.json`
  `a6d7d441…` and its 40 raw responses, 2026-10-19T16:21Z). It is the stock input of that pilot's
  `assembly` check (`assembly-stock/catalog.json` in the pilot scope `e0129bca…`), copied byte for byte
  from the volatile `/tmp/agent469-coordination/pod-campaign-v1/driver-preparation-v9-90x65/inputs/`.
  It is the only BOM-scoped stock capture made for a pod assembly check. `pipeline.py` uses it as the
  assembly layer's default stock, so it is not part of the capture root `build.py` writes.
- the earlier ESP32 guidelines, fab profile `02e48472…` and the first J3 attempt (unchanged).

`reconstruction.json` pins every file of the capture root with its source and hash.

## J3 (Hirose DM3AT-SF-PEJM5, LCSC C114218)

J3 is a named part on the regenerated record. It does not override what the sources say:

- The source is a distributor mirror of the 2010.6 reference catalog, not the latest engineering drawing.
- PDF page 3 names DM3AT-SF-PEJM5 with code 609-0031-0.
- Card detect switches A/B are normally open and close on insertion. The JLCPCB attribute
  "Additional Card Detection Pins: No" is contradicted and does not override the manufacturer evidence.
- Detect mapping (agent-509 delegated review, verified for these sources): manufacturer B is pad 9
  (DET_B, SD_CD), and A is pad 10 (DET_A, GND). `build.py` re-reads the pad positions, symbol pin names
  and intent nets and refuses on any difference.
- Page 2's -25 to +85 C includes current-induced rise. That shows the source exists. It does not
  qualify the actual board thermal or DFM.

## Ratings

The catalog-only declaration refuses on `power/C40/Voltage`: C452751's captured row has null
attributes. The v9 pilot rated C40 50 V from its selected KEMET datasheet (fact `C452751-rated-voltage`,
page 1). The same fact, with its path rebased onto the retained recovered-pilot PDF, is verified by the
pinned pdftotext and regenerates 50 V. All 98 original records reproduce their values exactly:

- 74 differ only by the part id (pilot `power-r1` vs `power/R1`) and the repository path of the same
  response or PDF bytes;
- 24 (C95204, 0603 0.1 % resistors) cite the pilot's `stock-passives-1` response and are regenerated
  from `part-bindings/resistor-stock`. Both rows give `Power(Watts)` = 100mW, which `build.py` checks.

Binding-fill also rates 150 further passives from their captured rows. These are new producer fields,
listed in `rating-comparison.json`. The binding-fill step declares `--ratings`. The compiled scope has
no `assembly_readiness` check, so on it the pod driver sets no coordinator `rating_provenance`. The
assembly layer of `pipeline.py` adds that check, and `pod_driver._rating_provenance` then returns
`rating-provenance` on both the production and the probe scope. The probe's prepared campaign and
driver receipt carry it. The campaign then copies the adopted binding-fill receipt and report into
each candidate (AGENTEE-256). This connects the provenance; it does not qualify assembly (below).

## Phase B (`pipeline.py`), on a fresh copy of the capture

`evidence/pipeline-a9dac2f-j5c-image.json` holds the exact results of this version, run in the pinned
agent-ee CI image (`ae-ci-exec` on an a9dac2f3 checkout, network none; container paths under
`/opt/agent-ee/build`) on the default repack. Its 28 stage statuses equal j5's host run
`evidence/pipeline-a9dac2f-j5.json` and j5b's image run `evidence/pipeline-a9dac2f-j5b-image.json` (21
accepted, 7 refused); the blocks record names the verified seed board, candidate policy and library entry
hashes, the expected obligations and (j5c) their canonical limitation lines. Each
records each stage verbatim, including every refusal. `evidence/pipeline-a9dac2f-bounded.json` (j4) and
`evidence/pipeline-a9dac2f.json` (j3) are earlier runs, kept as history; their producer
declarations mount the export root, which cannot import `agent_ee` (review H1).
`evidence/DIAGNOSTIC-pipeline-agent-ee-bf8a2836-handfit-patch.json` is a diagnostic only: the same
pipeline on agent-ee main plus the hand-fit patch, run to show the chain becomes expressible. Its
plan refusals are agent-ee main's newer plan schema, not a result of this capture. Its `placement.block_candidates_repack.detail.dry_runs_passed` key meant only
that `pod_driver.build(dry_run)` returned `prepared`, not that a native check passed. The two older
pipeline files are the run on agent-ee 014b349.

1. **Assembly layer.** One `assembly_readiness` check (`assembly`, verification stage), with:
   - the captured stock (`assembly-stock/catalog.json`), `deviations`, `require_passive_ratings` and
     `max_age_hours` 24 (POD-AC-5, "on the day of generation"; the campaign caps it at 24 anyway);
   - its requirement `POD-DERIVED-AC-5-ASSEMBLY`, citing the spec-record locator of POD-AC-5.

   The stock is `sources/assembly-stock-20261022/`: the agent-ee `jlc_stock_capture` producer, one
   public search request per id, 2026-10-22T10:50:06Z to 10:57:28Z, read only (no account, no
   purchase, no order, no upload). `scope_composition.assembly.stock.per_id` records, for each of the
   81 ids, the status, stock, quantity per board, fetch time, HTTP status, response hash, age and
   staleness. At composition all 81 were found; 80 are in stock for one board and J1 (C596198,
   1-776163-1) has stock 0. Staleness is graded again by the check at its own run (24 hours): the
   capture must be refreshed for any later generation.

   J1's hand-fit chain is verified link by link (`scope_composition.assembly.hand_fit`): the
   unchanged POD-AC-5 owner statement (`telemetry-pod/REQUIREMENTS.md` line 139, "the AMPSEAL
   header", `0f52e0ae…`), the owner-ruled D-PCB-10 line naming AMPSEAL 1-776163-1 / C596198
   (`design-rules/constraints.json` line 175, `e7e095b3…`), the C596198 part record (`f07570cc…`), the
   complete-parts manifest entry (`759d3be5…`, `/parts/326`) and the current production manifest entry
   (`composition/parts.json` `/parts/303`). Both manifests name the part record by that exact hash.
   The pinned agent-ee refuses the declaration (`expected fields: source sha256 line quote
   identities`), so the scope carries no `hand_fit_policy` and the refusal is kept. It is an assembly
   disposition only, not mating or enclosure qualification or purchase permission.

   POD-AC-5 stays NOT CHECKED. Captured stock and bindings are not assembly qualification.
2. **Envelope layer.**
   - The scope envelope declaration and one check per derived obligation, with lowercase, unique check
     IDs (`envelope-hole-h1`…).
   - `outline-containment/1` over the declared overhangs (its own requirement, citing D-PCB-13).
   - `electrical-locality/1` over `../electrical-locality/pad-obligations/`; the bounds stay advisory,
     per that README.

   `placement_adapter.envelope_fixed` passes fixed refs H1-H4/J1/J2/J3/U1/U2, overhangs J1/J2/U1/J3
   and their provenance to the packer. `bind_locality` binds the 12 obligations the policy embeds.
   Obligation coverage: 16 bound. The unbound five are `obligation-antenna`, `-corner-holes`,
   `-harness-edge`, `-height` and `-imu-separation` (AGENTEE-177/179). The envelope's requirements are
   incomplete for the same reason.
3. **Blocks layer.** `block-obligations.json` from the repack (REPACK_DIR, default
   `evidence/repack-a9dac2f-j5/`) is verified before it is copied or used (j5b, review-pod-capture-j5
   H1/H2; j5c, review-pod-capture-j5b H1-H3). The expected obligations are not read from the record.
   Both iter8n library blocks are expected: their entries are pinned by bytes to the iter8n capture,
   and both are `board-region/1`, which agent-ee `a9dac2f3` never materializes (`copper_unknown`). Each
   retained `logs/<block>.library.out` must be a JSON refusal naming its block, its tail equal to
   repack.json's for a generic pack with a nonzero rc. Unknown, non-JSON, missing-status, failed or
   materialized output refuses, whatever path label repack.json gives, so no output can drop a block
   (a future engine that materializes an entry needs its own verified success path). Each refused block must carry
   exactly `<block>-board-region-copper-native-check` and `<block>-witness-pose-equivalence`, unresolved,
   rebuilt from that refusal as `repack.py` writes them; a missing, duplicate, substituted, changed or
   empty obligation, block or status refuses. The retained `seed.kicad_pcb` is read and its bytes must
   be the captured iter8n seed `0365485e…` (iter8n `SHA256SUMS`); the default repack retains a verified
   copy, and a missing or changed seed refuses even when every recorded digest is rewritten to match.
   repack.json's seed, netlist and allocation inputs must be the captured ones. The library entry is read
   at `<block>.v4.entry.json`. Its bytes must be the captured iter8n entry and match the record and
   repack.json's input hash. It must be the `pod-<block>` `board-region/1` entry, from the iter8n `lib/` of
   the recorded seed. The refusal record and repack.json's record hash and lists are checked the same way.
   The generic candidate is checked by bytes and status, and must be an `agent-ee.block-candidate/2`
   whose `block_id` is the block and whose members hold its library reference. It must bind the captured
   seed board, allocation and netlist and repack.json's policy. The candidates' policy must be the
   derived request policy's identity. Missing, changed or swapped entries or candidates refuse.
   `obligation_probes.py` holds the regression probes (32 tests). The record is then copied to
   `composition/block-obligations.json` and declared as a scope `packet_inputs` entry. Each expected
   obligation becomes its canonical `POD-DERIVED-BLOCK-…: NOT CHECKED (unresolved; <record> sha256
   <digest>): <statement> …` limitation on both scopes, rendered from the rebuilt obligation and carried in
   the verified record (`limitations`). One validator, `block_limitation_problems`, is used by composition
   and by every consumer. It counts every line naming a reserved obligation id, in any case and with any
   status prefix, as an occurrence. Each expected obligation must occur exactly once, as its canonical
   line. Any other `POD-DERIVED-BLOCK` line refuses, so a changed meaning, record digest or disposition, a
   contradictory duplicate (also one inherited from the base scope) and an extra line all refuse. Stage
   `review.packet_obligations probe scope` builds the
   actual packet with agent-ee's `reviewers.build_packet` over the prepared dry run and refuses unless
   the validator accepts the packet and the candidate scope, `copper_unknown`, the record (byte-equal, cited and excerpted) and the
   174-entry ledger are present, and the driver's campaign scope differs from the probe scope only in
   its own `inputs`/`mutable_inputs`. Stage `scope.block_obligations production scope` checks the same
   expected set, exactly once each, on the production scope, which still cannot be prepared.
4. **Binding-fill.** `binding_fill.configuration` (writer intent, `--ratings`, distinct output) and `fill`
   are accepted: 305 components, 248 derived ratings, `ratings_missing` `{}`, 6 probe migrations, and
   the ledger's 174 Qualification entries all bound.
5. **Scaffold and envelope content.** Refused on the production scope (step 2's five). Accepted on the
   probe scope (9 fixed footprints, J3 included). The emitter, annotation, planes, routing preflight
   (pin 5f1c072) and the AGENTEE-439 blocks declaration shape are accepted.
6. **Budget.** The plan of record (`planning/plan.json`) declares `max_iterations` 2 and the placement
   `timeout_s` 1500 (authorized 900-1500 s, ROUTE.md R2). `pod_driver.validate_plan` and `build` refuse
   it: `max_iterations must be between 8 and 100`. The probe plan omits the budget fields, so the
   driver applies its defaults: `max_iterations` 10 and `max_seconds` 8400, its minimum, which is two
   routing receipts of 2100 + 300 s plus the 3600 s review reserve.
7. **`pod_driver.build(dry_run)`.**
   - Production scope: refused with the bounded plan (step 6) and with the probe plan (step 2's five).
   - Probe scope: **prepared**, with receipted scaffold and content, the first capture bound and
     `rating_provenance` set. Its campaign is checked against the authorized budget and refused, then
     renamed to `campaign.NOT-AUTHORIZED.json`. Its hash still equals the driver receipt's
     `campaign_sha256`, and no campaign within the bound exists.

   Its checks-only grading (`dry-run-record.json`: exit 1, `done` false) reports every stage
   `stage_not_reached`; each check is `ok/defect` with that reason, `assembly` included. That is
   expected: `run_dry` grades the scaffold without executing the implementation steps, and the ERC
   stage subject observes no native references in the scaffold schematic. It is not a schematic
   defect. The next unexecuted step is schematic emission from the bound intent (`emit-schematic`
   after `binding-fill`), then the native checks.

The repack gate (`placement.block_candidates_repack`) lists the calls under
`preparation_not_refused`: `pod_driver.build(dry_run)` returned `prepared`. That is not a native check
pass. The refused calls and every dry-run check record are kept beside it. `repack.py` repacks the
18 blocks on the iter8n seed with the derived policy (`evidence/repack-a9dac2f-j5/`; the j3 run
`evidence/repack-a9dac2f/` kept only a 300-character tail of the library refusal). The candidates bind
policy `b07059a5…` (iter8n's bound `a8b2585e…`) and the seed board `0365485e…`. `all_packed` counts
geometry candidates; `unresolved_obligations` and `qualified: false` sit beside it.

Producer import roots (stage `producers.import_from_declared_mount`): for binding-fill,
emit-schematic, forward-annotate, add-planes and envelope-content, the declared module imports from
the step's own mount source, in an empty directory with that source as the only path entry, and its
`__file__` lies inside the mount. The export root (the pre-j5 declaration) fails with
`No module named 'agent_ee'`. This is an import check, not native execution.

### Why `max_iterations` 2 does not reach a campaign at this pin

The 8-100 range is a `pod_driver` policy, not an engine limit. `campaign.run_campaign` accepts
`max_iterations` 1-100 (campaign.py:454-456). The floor came with the driver in agent-ee `d8cd3589`,
with no cited rationale (docs/pod-driver.md:71, "minimum 8"). The test
`test_small_iteration_budget_and_provider_fallback_refused` enforces it. Nothing in the two-iteration
R2 run needs eight: iteration 1 grades the seed, and iteration 2 is one placement turn.

Reconciling it is an agent-ee change outside this lane. The driver would have to accept the declared
bound, for example by aligning its range with the engine or adding an explicit bounded-run field.
Until then, no prepared campaign carries the authorized bound, and the pipeline never raises the
plan to 8.

The 900-1500 s bound is the placement adapter `timeout_s` (1500 here), not the campaign wall clock.
`max_seconds` stays at the driver's derived minimum. That minimum follows from the routing adapter
contract (timeout at least 2 × budget + 300) and the review reserve.

## Decisions (autonomous, recorded per AGENTS.md; owner review after the fact)

- **J1 is hand-fitted (POD-AC-5)**, unchanged. J1 (C596198) has captured stock 0 and
  `assemblyComponentFlag` false. Reverse by emptying `deviations` in `build.py`.
- **Qualification moves to a ledger (agent-509 binding composition decision).** No producer owns these
  project-authored limitations, and binding-fill's exact comparison is unchanged. They stay visible in
  `binding-ledger.json`. Reverse by keeping them in the writer intent, which then refuses.
- **Pilot rating strings are migrated, values kept.** Each `AGENT_EE_Ratings` pins a pilot record whose
  id and paths name the pilot root, so equal values cannot reproduce the hash. The values stay in the
  writer intent and are regenerated exactly; the rows explain each record. Reverse: restore the strings
  from the ledger, which then refuses.
- **C40 rating from the pilot's documented fact**, rebased path only, with the pinned extractor; never a
  copied number. The alternative is leaving C40 unrated, which the catalog-only refusal shows.
- **Two library blocks are packed generically.** At a9dac2f, `block_library materialize` refuses the
  iteration-5 board-region entries for pre-6v3 and buck-3v3 (`copper_unknown`). They are packed by the
  same `blocks pack` as the other 16, which drops the iteration-5 witness poses. The refusal is a
  source-bound unresolved obligation (`block-obligations.json`) in the scope limitations and the review
  packet, never acceptance. Reverse: repack once the engine applies board-region copper.
- **Assembly stock is a fresh 81-id producer capture (`sources/assembly-stock-20261022`)**, taken
  read-only under the existing task authorization (agent-509, 2026-10-22). The v9 pilot capture
  (38/81) stays as the default for history. Replace it again near any actual generation.
- **J1 hand-fit is a source chain, not a new owner approval.** The POD-AC-5 quote is used verbatim;
  D-PCB-10 and the captured records supply the exact identity. Reverse by deleting
  `assembly/hand-fit-policy.json` (the pipeline then refuses to start).
- **The probe campaign is set aside, not edited** (j4-j5c). At `81e387ee` the driver accepts the bounded
  plan, so j6 removes the probe plan and probe scope entirely; the a9dac2f evidence keeps them as history.
- **The fab profile values stay `02e48472…`.** It needs an applicability check against agent-ee's
  `00e3e2fc…` (they differ in `small-drill` and `small-via`) before any manufacturing qualification claim.
- **j6: the requirement source is the pinned Revision 3 capture.** The microSD spec only adds the
  POD-CD-STORAGE decision row (checked mechanically), so every acceptance criterion and bench obligation the
  driver binds is the same. The alternative, refusing preparation until agent-ee admits the microSD capture
  to `pod_driver.SOURCES`, would block the authorized dry run on a component-decision row that no acceptance
  criterion depends on. Reverse: once a reviewed agent-ee commit admits the microSD capture, select it and
  drop `requirements-source/`.
- **j6: the fab profile's requirement mapping is relabelled for the production envelope** (only the
  `requirement` field; values and citations are checked unchanged). The alternative, the old envelope id
  `telemetry-pod`, is refused by the reviewed source contract, which names `expanded-pod-microsd-production`.
  Reverse: author a profile mapped to the production envelope at the source.
- **j6: the emitted schematic and annotated board replace the v9 pilot as the telemetry-pod project**
  (AGENTEE-445: "the next real pod schematic comes from the production run (j6)"; the v9 emitter inputs are
  lost). The v9 pilot files stay a historical snapshot at commit `13c0bfb` and in its renders. The board is the
  generation seed: fixed parts posed by the envelope content, the rest unplaced and unrouted. Reverse:
  `git checkout 243b17d -- telemetry-pod/telemetry-pod.kicad_sch telemetry-pod/telemetry-pod.kicad_pcb
  telemetry-pod/telemetry-pod.kicad_pro telemetry-pod/telemetry-pod.kicad_dru telemetry-pod/sym-lib-table
  telemetry-pod/fp-lib-table`.
- **j6: the emitter `captures` root is the candidate root** (the declared libraries are root-relative).
- **j6b: the models live in the candidate project, `project/inputs/models/`.** The J1 member was authored to
  name `${KIPRJMOD}/inputs/models/`. agent-ee resolves KIPRJMOD to the board's directory and carries project
  models into placement proposals from there. The alternative, rewriting the footprint path to
  `${KIPRJMOD}/../models/`, would edit the reviewed connector footprint.
  - Reverse: drop `project_models()` from `build.py`.
- **j6b: the U3 footprint member gains one model node, and no other byte changes.** This follows
  `neo-m9n-model/README.md` ("Bind U3 to `${KIPRJMOD}/inputs/models/<same STEP filename>` with zero
  transform"). The captured member is otherwise unchanged; its pads, courtyard and fields are the same.
  - **Hash ripple:** `footprints.json`, the `parts.json` CAD digest and `captured-rule-areas.json` follow. So
    does the `composition/parts.json` digest cited in `assembly/hand-fit-policy.json`; its `/parts/303` J1
    entry is byte-identical (checked).
  - **Reverse:** drop the `U3_FOOTPRINT` branch in `libraries()`.
- **j6b: J1 model checks use the candidate's exporter datum.** The pose is fixed by the footprint and verified
  against the drill axes. A Z offset between two KiCad exports is an exporter datum, which the connector README
  says is not a physical stand-off.
  - **Alternative:** require the fixture's absolute Z. That would fail every real candidate whose stackup
    differs, without saying anything about the model pose.

## Reproduce

```sh
# inside the pinned agent-ee image (since j6b2 the AGENTEE-466 image; the host pdftotext has drifted):
/usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --check
/usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --out /new/capture
AGENT_EE_GIT=AGENT_EE_CHECKOUT AGENT_EE_TOOL_SOURCE_CACHE=/abs/cache \
  /usr/bin/python3 telemetry-pod/expansion/production-capture/pipeline.py \
  AGENT_EE_EXPORT ROUTER_CHECKOUT COMPILED_SCOPE_DIR /new/capture /new/pipeline-out \
  telemetry-pod/expansion/production-capture/sources/assembly-stock-20261022 [REPACK_DIR]
# on the host, fome-mc root:
/usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py /new/pipeline-out --install
/usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py --check
# j6b2: the single preparation run in the AGENTEE-466 image (RUN_DIR layout in production_run.sh), then on the host:
~/.local/bin/native-admit run --class suite --weight 4 --label LABEL -- \
  bash telemetry-pod/expansion/production-capture/production_run.sh RUN_DIR
/usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py RUN_DIR/pipe --install
/usr/bin/python3 telemetry-pod/expansion/production-capture/runtime_receipt.py write RUN_DIR/observation.json IMAGE_DIR RUN_DIR
/usr/bin/python3 telemetry-pod/expansion/production-capture/runtime_receipt.py check
/usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py --materialize-prepared /new/prepared
# j6b native STEP export and CadQuery 2.8.0 model checks (uv offline, cached cadquery):
/usr/bin/python3 telemetry-pod/expansion/production-capture/model_check.py telemetry-pod/telemetry-pod.kicad_pcb /new/model-check
/usr/bin/python3 telemetry-pod/expansion/production-capture/repack.py AGENT_EE_EXPORT ITER8N_DIR /new/repack-out
# read-only stock refresh (network; one public request per id; no purchase, order or upload):
PYTHONPATH=AGENT_EE_EXPORT/src /usr/bin/python3 -m agent_ee.jlc_stock_capture --allow-network \
  --ids-file BOM_IDS.json --out /new/stock
```

`AGENT_EE_EXPORT` is `git archive` of agent-ee `7d5b0d4d` (pipeline.py refuses any other tree; j6 and j6b used
`81e387ee`, the history sections `a9dac2f3`). `IMAGE_DIR` holds the `docker save` probe of the image. `COMPILED_SCOPE_DIR` is
`requirements/rev3-microsd/compiled/` from fome-mc main (scope-b, `6a74fee2…`). `ITER8N_DIR` is the
coordinator's iter8n cache (seed, netlist, allocation, library entries). The build exports the microSD
netlist on a temporary copy; no design file is re-saved.

## AGENTEE-485 correction (R1-R3)

- **R1 policy.** `policy.py ITER8N_POLICY [--check]` is the producer of `composition/placement-policy.json`: the
  recorded derivation (iter8n policy `63138a34…` minus `fixed_overhangs`) with the embedded `electrical_locality`
  replaced by the scope's A3 document (`electrical-locality.json` `9852c3ed…`, 201 obligations), so
  `placement_adapter.bind_locality` binds it. The repack of that policy is `evidence/repack-8ab3b0b9-485c/` (agent-ee
  `8ab3b0b9`, the pipeline REPACK default); `repack-a9dac2f-j5/` binds the superseded `5fab430a` and stays as history.
- **R2 block variants.** pipeline.py stages the 485-A stage-owned block request (`composition/block-stage/`: the A3
  templates, the A3 allocation bridge, the iter8n arrangement, empty producer placeholders and the pending report),
  declares it as `placement_adapter.blocks`, and inserts agent-ee's own `block-variants` step after forward-annotate.
  The stage `blocks.stage_owned_variants C1` runs that step on a copy of the emission and records the pending
  refusal, the consumed /1 sets, the legal-underside count and the stale move/rotate/flip refusals.
- **R3 launch.** Preparation (`production_run.sh`, `retain.py`, `runtime_receipt.py write`) and launch are separate.
  The one launch command, from the fome-mc root of the integrated commit (RUN as for production_run.sh):

  ```sh
  POD_RUST_DIR=~/.cache/agent-ee-evidence/agentee-485-runtime-503 ~/.local/bin/native-admit run --class suite \
    --weight 4 --label LANE -- /usr/bin/python3 -I -B telemetry-pod/expansion/production-capture/launch.py \
    telemetry-pod/expansion/production-capture/evidence/RECEIPT_DIR RUN NEW_OUT [--preflight]
  ```

  `launch.py` refuses unless the committed receipt checks, `retain.py --check` passes, the materialized prepared tree
  hashes to the receipt's campaign/plan/driver bindings, the mounted Rust pair hashes to the receipt, the image is
  present by digest and the receipt's pre-launch identity check (observe) reports no problems. `--preflight` stops
  there; without it the receipt's own `agent_ee.cli campaign` command runs. It is the existing runner, unchanged.

## Remaining

- **Launch.** The prepared two-iteration campaign is not launched. agent-521 (telemetry-pod lead since
  2026-10-22, replacing agent-509) authorizes the single bounded run after review and integration. The stock capture (2026-10-22T10:50-10:57Z) is fresh until 2026-10-23T10:50Z; a later
  generation refreshes the stale ids read-only first.
- **POD-AC-5 stays NOT CHECKED** until the assembly check runs on a native netlist in a campaign iteration.
  J1's zero stock keeps its owner hand-fit disposition; no purchase and no substitution.
- **Final qualification.** The five staged obligations keep 20 open items (enclosure and harness fit are open
  design deliverables), and the final guard blocks acceptance on them. The radio-antenna keepout stays
  unknown by design.
- **Library blocks.** The four pre-6v3/buck-3v3 copper/native-check and witness-pose obligations stay
  unresolved until a real placement repacks those blocks on its own board and native checks run.
- **Requirement source.** Admit the microSD spec capture to agent-ee `pod_driver.SOURCES` (a coordinator
  action) to bind the current spec directly.
- **Emitted board.** It is the generation seed, not a design result: DRC reports the unrouted connections,
  overlaps among the unplaced parts and `lib_footprint_mismatch` on the posed J1/J2/J3 as findings.
- The structural envelope validity, retention and J3 transform are not mechanical qualification. The fab
  profile needs its applicability check before any manufacturing claim.

## Stock refresh 2026-10-23 (agent-529 a57b675c)

`sources/assembly-stock-20261023/` is a fresh read-only capture through the same agent-ee `jlc_stock_capture` producer
(agent-ee 7d5b0d4d export, `--allow-network`), one public search per id.
- **Ids:** the 81 LCSC ids of the current `composition/parts.json` (`2e9afa70…`, which includes the AGENTEE-484 additions). These are the same 81 ids as before.
- **Timing:** as_of 2026-10-23T11:14:36Z, completed 11:21:50Z.
- **Result:** 81 found (HTTP 200), 0 failed, 0 unavailable. J1 C596198 stock is 0, the hand-fit part, unchanged.
- **Responses:** retained byte for byte with sha256 and UTC in `catalog.json`.
- **Constraints:** no account, cart, purchase, upload or credential.

`pipeline.py` now defaults to this capture. The 20261022 capture stays as history. The AGENTEE-488 part changes are not adopted; refresh their ids after adoption.

## Retention emission-7d5b0d4d-agentee484r2 (agent-529 a57b675c): SUPERSEDES emission-7d5b0d4d-agentee484r

- **New retention:** `evidence/emission-7d5b0d4d-agentee484r2/`. It was generated through the production path
  (`production_run.sh`, 28/28 stages) from commit `92dc5acf` on the refreshed stock (`sources/assembly-stock-20261023`;
  stock gate evaluated 2026-10-23T11:32:07Z: 81 observed, 0 stale, 0 unobserved).
- **Superseded retention:** `evidence/emission-7d5b0d4d-agentee484r/` is incomplete. Its .gitignored `native.xml` and
  `receipts/3-forward-annotate/run/out/netlist/design.xml` were never committed. It is kept UNCHANGED as defect evidence.
- **No recovered bytes:** the new retention's XML is newly generated by this run; it is NOT the original 484r bytes.
- **Runtime receipt:** `evidence/production-runtime-484r2/receipt.json`, written by the review-fixed `runtime_receipt.py` with
  `--runtime runtime/agentee-484r2.json` and a validated `--source-commit`.
  - The image identity is read from the j6b docker-save evidence of the same config digest (not re-saved).
  - No Rust binary runs in the preparation, so `run_bindings.rust` is null.

## Runtime receipt production-runtime-484r2-v2 (agent-529 582c157c v1, after the Astra H4 re-fix)

`evidence/production-runtime-484r2-v2/receipt.json` is the CURRENT receipt for the 484r2 preparation.
- **Script:** written by the H4-fixed `runtime_receipt.py`. It compares every selected identity with the receipt, the observation and the pipeline. The pre-launch command carries and mounts the selected manifest, and no unselected c4 evidence is used.
- **Inputs:** the retained 484r2 observation and the same selected manifest `runtime/agentee-484r2.json`.
- **Source commit:** 92dc5acf, validated against a `git archive` reconstruction of that commit. The original run copy was not retained.
- **Superseded:** `evidence/production-runtime-484r2/` was written before the H4 fix. It is unchanged and kept as history. It is NOT relabelled as qualified.
