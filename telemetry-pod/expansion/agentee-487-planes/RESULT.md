# AGENTEE-487: missing copper planes (root cause, producer repair) and runtime-receipt binding

Decisions from agent-529, relayed via 519: d1bfc238, 783ad032, HOLD 76150ac4 (option **a**), and b2422ab3 v2.

## Run record

**Clock:** started 2026-10-23T10:41:24Z (as 449 recorded it), checkpoint ended 2026-10-23T10:59:54Z.

**Model and host:** Claude Opus 5.5 on proximal.

**Worktrees:**
- fome-mc `wt/agentee-487` (base d46183e, which contains 484r);
- agent-ee `wt/agentee-487-planes` (base 334ecbf9).

**Runtime:** native-admit only. No AppArmor work, routing campaign, placement change or broad suite.

## Root cause, stage by stage (`zone-inventory.json`, `zone_inventory.py`, read-only pcbnew)

| Stage / board | sha256 | Copper zones | Rule areas | `/GND` net (exact) | `GND` net |
|---|---|---|---|---|---|
| emitted (484r emission) | 0b68a0ac… | 0 | 2 | yes | no |
| prepared campaign candidate (scaffold) | 3b2b8359… | 0 | 2 | no (empty scaffold) | no |
| installed fome-mc board | 0b68a0ac… | 0 | 2 | yes | no |
| R5 placed | 8f3bc234… | 0 | 2 | yes | no |
| ROUTE-1 / ROUTE-3 / ROUTE-4 | 19ed7954 / 08066170 / 5690da57 | 0 | 2 | yes | no |

1. **Plan and net identity are correct.** `design-rules/planes.json` declares `/GND` on In1.Cu and `/+3V3` on In2.Cu, both `island_removal: always`. The exact native nets `/GND` and `/+3V3` exist on the boards, and `GND` does not, so there is no aliasing.
2. **The planes step is declared, not executed.** `pipeline.py:897` `add_planes.step(...)` only builds a step declaration. It enters `plan.json` → `implementation_steps` with **`stage: routing`** (prepared plan: binding-fill, emit-schematic and forward-annotate are `schematic`; add-planes is `routing`). The emission stage executes only the three schematic steps (`pipeline.py` emit_schematic).
3. **By design, add-planes belongs to the campaign routing turn.** agent-ee `docs/add-planes.md:4-6`, `pod_driver.py:23-26` and `campaign.validate_routing_predecessors` / `run_implementation_steps` run it in a campaign routing turn, on the adopted placed board, before the router. **Phase owner: the campaign routing turn (agent-ee campaign).**
4. **Why no saved board has planes.** None of these boards went through a campaign routing turn. R1–R5 and ROUTE-1/3/4 were out-of-campaign placement scripts and direct kicad-route runs.
5. **The actual defect.** Executing the DECLARED step exactly as the campaign does (`planes_phase_proof.py`, agent-ee `stage_receipts.run_step`/`adopt`, in the d96f8e00 image) on the real placed R5 board **refuses**: `plane_production_refused`, "native DRC found an error involving planned zones" (the `/+3V3` In2 zone, isolated_copper). A wholly unconnected planned `always` zone is refused (`docs/add-planes.md` "Island removal"). Before routing, In2 `/+3V3` has no connection, because every `/+3V3` load is SMD. **A campaign routing turn could never produce the planes.** The original evidence is retained in `regression-before.json` and `regression-final-old.json`.

## Fix (option a: the producer's pre-routing acceptance)

- **agent-ee `wt/agentee-487-planes` commit `2c2d99f70805502a04adf079b6b60ff786b264bb`** (not merged; agent-524's 479 diff does not touch these paths):
  - **`src/agent_ee/add_planes.py`:** a planned `always` zone whose EVERY fill polygon is reported `isolated_copper` is wholly unconnected. It keeps its definition and its `always` policy, and the report lists it under `deferred_connectivity` (obligation: connected fill under island_removal always after routing). Still refused: partial isolation, every other planned-zone error, missing or unplanned nets.
  - **`tests/test_add_planes.py`:** the island test now asserts the deferral.
  - **`docs/add-planes.md`:** documents the deferral.
  - Patch: `agent-ee-add_planes.patch`.
- **fome-mc:**
  - **`design-rules/planes.json`:** `e780472`'s `never` is **reverted** to the original bytes (sha 9e592e3e…, both `always`).
  - **`design-rules/README.md`:** the note is superseded with this explanation.
  - **Final policy:** island_removal=always throughout. No intermediate policy is used, so nothing has to be restored.

## Regression (fails before, passes after)

- **agent-ee unit test** (CI image, native-admit + ae-ci-exec):
  - `tests.test_add_planes` **15/15 OK** with the fix (`test_add_planes-after.log`).
  - The updated island test against the unfixed producer **FAILS** (`'failed' != 'ok'` for always; `test_add_planes-before.log`).
- **Real placed board** (`regression_check.py` → 8/8 PASS; a control with the old result as "after" exits 1):
  - **Before** (production producer 7d5b0d4d, final `always` plan): refused, not adopted.
  - **After** (7d5b0d4d plus the fix, same plan): exit 0, adopted. Copper zones are exactly `/GND` In1.Cu and `/+3V3` In2.Cu. The plan stays always/always. `/+3V3` is deferred with policy `always`; `/GND` is not deferred (connected through THT pads). Rule areas are preserved.
  - **Wrong net** (`GND` for `/GND`): still **FAILS** ("planned plane net is missing: GND").
- **Unplaced emitted board:** refused, "saved copper outside board outline", because its parts are staged off-board. Planes belong after placement.

## Runtime receipt (783ad032, b2422ab3 v2)

`production-capture/runtime_receipt.py`:
- **Retained evidence** defaults to `retain.py` DEST.
- **`--receipt-dir`** is explicit, and `write` never overwrites an existing receipt; old receipts are history.
- **`--authority`** is a neutral parameter, and no agent-521 text is in the receipt body.
- **`run_bindings`** covers `--source-commit`, `--contract` (repeatable), the mounted Python source (from the observation), the Rust binary and receipt, and `--native`.

**The receipt-binding answer:**
- `check` and `write` accept **any** actual Rust binary and build-receipt pair whose receipt names the binary's sha256.
- A **mismatched pair is rejected**.
- **No `5261cb13` literal** exists or is required.

**Test:** `test_runtime_receipt_params.py` passes **11/11**, including those three cases and "the historical j6b receipt still checks against its own evidence". It fails before the change.

## Also found and partly repaired: retained-evidence files dropped by `.gitignore`

My AGENTEE-484 and 484r retention commits did not force-add files matching `*.xml` and `*.kicad_prl`. As a result, `retain.py --check` fails on a fresh checkout. The original `emission-7d5b0d4d` retention has them.
- **`emission-7d5b0d4d-agentee484/`:** all 4 missing files were restored byte-exact from the scratch run, with SHA256SUMS OK. They are force-added here.
- **`emission-7d5b0d4d-agentee484r/`:** 2 of 4 were restored. `native.xml` and `receipts/3-forward-annotate/run/out/netlist/design.xml` cannot be reproduced, because the scratch output was cleared by the failed rerun. **REMAINING:** regenerate the 484r-equivalent retention.

## Remaining limits

1. **The production rerun is blocked by stock freshness.** The 487 rerun (`/tmp/a487/run.log`) failed at the pipeline's stock gate: the JLC stock capture is older than 24 h, and there is no generation on stale stock. A stock refresh (a read-only catalog capture) needs coordinator authorization before any new production retention, including the 484r one.
2. **The post-routing verification is not wired.** No consumer yet reads `deferred_connectivity` after routing to verify connected `always` fill (and the 480 In1 reference continuity). That belongs to the routing phase, the campaign routing turn after the router. It is not implemented or run here.
3. **agent-ee main fails differently.** `334ecbf9`'s producer (mounted unpinned) refused differently on this project: "constraint provenance geometry inventory differs from saved project/rules". That is separate from this fix and should be checked when the production pin moves.
4. **Integration needs a repin.** Using the add_planes fix in production needs agent-ee integration and a repin, sequenced with agent-524 by 449.

## Files changed (sha256)

| File | sha256 |
|---|---|
| fome-mc `telemetry-pod/expansion/design-rules/planes.json` (reverted to original) | 9e592e3ee4bdf5b6042fd3a595235cc5425359f4a69f87787ce00fc3624779aa |
| fome-mc `telemetry-pod/expansion/production-capture/runtime_receipt.py` | 5e0064b9972dbfdaabc888467e7ef7a303dbba5e89aa3422ceb889f706fad7bb |
| fome-mc `telemetry-pod/expansion/production-capture/test_runtime_receipt_params.py` | d5c81686778089c9d85c19f537b2212f34d3ebb818c47f4e9f268561cf309e3d |
| agent-ee `src/agent_ee/add_planes.py` | 35e4e7ce7b44f8dae22de940dd783da407b0b838f5d40551902d7dc5553ea126 |
| agent-ee `tests/test_add_planes.py` | ddb9afbfdd3530ef1c116d3f8705f902a0b3bc23d3f111341a8da78da0709798 |
| agent-ee `docs/add-planes.md` | af1f6bbb178c89ff39ec848e2386378d8ee8b7f0df2b0cb52bed1343ff71047a |

## Review fixes R (Astra HIGH HOLD, H1 to H4), 2026-10-23T11:19Z to 11:28Z

### H1 and H2: agent-ee `wt/agentee-487-planes` commit `259b3eecf27b9771286687db7c627e2f009fd0f1` (on top of 2c2d99f7, not merged)

**Stable phase interface (for agent-522's post-routing consumer):**
- **Producer call:** `add_planes.step(source_root, board=..., plan=..., phase='pre-routing')`. The declared argv adds `--phase pre-routing`. `add_planes.PRE_ROUTING == 'pre-routing'` is the ONLY accepted phase value; any other value raises ValueError. The CLI `--phase` choices are `('pre-routing',)`.
- **Default:** `phase=None`, for any other caller and every post-routing use. It NEVER defers: a wholly isolated planned `always` zone refuses exactly as before.
- **Report (`out/planes.json`, schema `agent-ee.add-planes/1`):**
  - `phase`: `'pre-routing'` or `null`;
  - `deferred_connectivity`: a list, always present, of `{zone: <planned zone uuid>, net: <exact native net>, layer: <layer name>, island_removal: 'always', obligation: 'connected fill under island_removal always after routing'}`. It is empty unless phase is pre-routing and the zone is proven wholly unconnected.
- **Native evidence:** `out/native/islands.json`, per planned zone `{layer, polygons, islands: [bool per fill polygon], method}`.
- **Not done here:** the post-routing consumer that discharges each entry (saved final zone identity, `always` policy, connected fill after routing and refill, and 480 In1 continuity) belongs to agent-522 (`agentee-487c`).

**H2 contract.** Deferral requires both of these:
- **Native per-polygon connectivity of the fresh fill** (fill child): a fill polygon is connected iff a same-net pad present on the zone layer, or a same-net via or track endpoint on that layer, lies inside that polygon's outline. EVERY polygon must be an island.
- **One-to-one attribution:** the `isolated_copper` findings for the zone have distinct positions, and their count equals the saved polygon count.

Duplicate attribution, a position-less item, or a missing native record **fails closed** (ValueError, so a refusal). Partial isolation is not deferred, and every other planned-zone error still refuses.

**Evidence:**
- `tests.test_add_planes` passes **21/21** in the CI image (native-admit + ae-ci-exec; `r-test_add_planes-after.log`). The new cases:
  - phase-bound native deferral: always plus no phase refuses; always plus pre-routing defers with islands.json all true; never does not defer;
  - `_phase_argv` declaration;
  - no-phase and post-routing never defer;
  - duplicate and position-less findings and a missing native record fail closed;
  - partial isolation and a count mismatch are not deferred.
- **Fails before / passes after** (`review_probe_h1h2.py` in the CI image):
  - **2c2d99f7 producer:** `H1_NO_PHASE_ALWAYS_ISOLATED ok deferred [...]` and `H2_DUPLICATE_FINDINGS deferred` (both defects).
  - **259b3eec:** `H1_NO_PHASE_ALWAYS_ISOLATED failed deferred []` and `H2_DUPLICATE_FINDINGS FAIL-CLOSED`.
- **Integration for 449:** fome-mc `pipeline.py:897` must pass `phase='pre-routing'` once production is repinned to an agent-ee containing 259b3eec. Passing it to the current 7d5b0d4d pin would raise, so it is NOT changed here. No conditional fallback was added.

### H3 and H4: fome-mc `runtime_receipt.py`

- **H3:**
  - `rust_receipt_problem()` parses the installation receipt as JSON, requires schema `agent-ee.placement-engine-install/1`, and compares `binary_sha256` with the recomputed binary digest. This is the agent-ee `placement_rust_runtime.py` contract.
  - It is used in `write` (`rust_pair`) and in `check`.
  - Missing inputs fail closed.
- **H4:**
  - The fixed identities are now `HISTORICAL_J6B`, reachable only by the explicit `--runtime historical-j6b`.
  - A current run selects an immutable `pod-capture.runtime-manifest/1` file (`--runtime`); its path and sha256 are bound in the receipt as `runtime_selection`.
  - No runtime is implicit. `check` re-selects the bound manifest and refuses if its hash differs. A historical receipt without a selection needs the explicit `historical-j6b`.
  - `--source-commit` is required for `write` and VALIDATED: every production-capture and design-rules file in the run's `fome/` copy must equal that commit's blob.
  - The current manifest `production-capture/runtime/agentee-484r2.json` is passed to `observe` by `production_steps.py`.
- **Test:** `test_runtime_receipt_params.py` passes **24/24** (`r-receipt-test-after.txt`). New probes:
  - H3: good pair accepted; wrong field (previous_binary_sha256 correct, binary_sha256 wrong) rejected; non-JSON containing the digest rejected; wrong schema rejected; missing receipt rejected; binary without receipt rejected; full `check()` with good, wrong-field and binary-mismatch pairs;
  - H4: no implicit runtime; manifest selected and hash-bound; malformed manifest refused; a non-commit refused; a run copy differing from the source commit refused; historical receipt without selection refused, and with explicit selection OK.
- **Before the fix,** the test stops at the missing contract attribute (`r-receipt-test-before.txt`). The reviewer's probe on 8204a29 also recorded `FULL_CHECK wrong_field ACCEPTED`.

**agent-ee file hashes (259b3eec):**

| File | sha256 |
|---|---|
| `add_planes.py` | c00ccfd202a23754ebccbec41bc2a20bd881c8097b07f4f12c820e6412485778 |
| `add_planes_probe.py` | 07c4755d9fae6905356d2f68ce3cf90a06977add297f082533aa0a5bf1f7a8a3 |
| `tests/test_add_planes.py` | a5f2839acbd59df08e553c5889c3416abe2e7ea5b67a984d137bab9a08fb2095 |
| `docs/add-planes.md` | 6bf8b18bbec2091250a9465e00cd2bb13a6a829c4e4d0ebbec6353cd142d63f9 |
