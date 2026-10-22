# Production capture for the Rev-3 microSD pod (AGENTEE-207/197)

This directory captures the electrical and mechanical inputs a production pod run needs, for the
current microSD source (`../storage-microsd/`, 305 references). Phase B then runs the genuine
agent-ee producers on the capture and stops at the real `pod_driver` dry run. It is capture and
composition evidence. No placement, routing, campaign or model ran, and nothing is accepted.

**Status (j6, agent-ee main `81e387ee`; AGENTEE-197 landed with 197s/t/v, the hand-fit chain `08ddaa17`
and the emitter field order `41e91eca`).** The authentic two-iteration production preparation exists. The
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

## j6: production preparation and emission at agent-ee `81e387ee`

`evidence/emission-81e387ee/` holds the run (`pipeline.json`, the driver receipt, campaign, plan, scope,
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
  fit are recorded as open design deliverables (owner direction 2026-10-22), not blockers; the JLC 1.6 mm
  board is accepted and its thickness tolerance is kept separate from the AGENTEE-448 component-side fit
  screening.
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

## Reproduce

```sh
# inside the pinned agent-ee CI image (ae-ci-exec on an 81e387ee checkout; the host pdftotext has drifted):
/usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --check
/usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --out /new/capture
AGENT_EE_GIT=AGENT_EE_CHECKOUT AGENT_EE_TOOL_SOURCE_CACHE=/abs/cache \
  /usr/bin/python3 telemetry-pod/expansion/production-capture/pipeline.py \
  AGENT_EE_EXPORT ROUTER_CHECKOUT COMPILED_SCOPE_DIR /new/capture /new/pipeline-out \
  telemetry-pod/expansion/production-capture/sources/assembly-stock-20261022 [REPACK_DIR]
# on the host, fome-mc root:
/usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py /new/pipeline-out --install
/usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py --check
/usr/bin/python3 telemetry-pod/expansion/production-capture/repack.py AGENT_EE_EXPORT ITER8N_DIR /new/repack-out
# read-only stock refresh (network; one public request per id; no purchase, order or upload):
PYTHONPATH=AGENT_EE_EXPORT/src /usr/bin/python3 -m agent_ee.jlc_stock_capture --allow-network \
  --ids-file BOM_IDS.json --out /new/stock
```

`AGENT_EE_EXPORT` is `git archive` of agent-ee `81e387ee` (pipeline.py refuses any other tree; the
history sections used `a9dac2f3`). `COMPILED_SCOPE_DIR` is
`requirements/rev3-microsd/compiled/` from fome-mc main (scope-b, `6a74fee2…`). `ITER8N_DIR` is the
coordinator's iter8n cache (seed, netlist, allocation, library entries). The build exports the microSD
netlist on a temporary copy; no design file is re-saved.

## Remaining

- **Launch.** The prepared two-iteration campaign is not launched; agent-509 authorizes the single bounded
  run separately. The stock capture (2026-10-22T10:50-10:57Z) is fresh until 2026-10-23T10:50Z; a later
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
