# AGENTEE-488 source edits (agent-529 061a1b20 v2)

## Run record

**Clock:** started 2026-10-23T12:00:22Z, ended 12:21:54Z.

**Base and branch:** base `wt/agentee-stock-484r2` 13be7035; branch `wt/agentee-488`.

**Runtime:** native-admit only.

## Changes (canonical source, then regenerated)

| Ref | Before | After |
|---|---|---|
| C133 | pin 2 /GND | pin 2 **/+5V_CAN** (U100 VIO-to-VCC). Part unchanged: TDK CGA3E2X7R1H104KT0Y0N, C76711, 100 nF 0603 |
| C84 | pin 2 /GND | pin 2 **/+5V_CAN** (U21 VIO-to-VCC). Part unchanged: KEMET C0603C104K5RACTU, C127833 |
| C18 | TDK CGA3E1X7R1C105KT0Y0N (C76706), 1 uF/16 V, 0603 | **TDK CGA6P3X7R1E226MT000N (C694521), 22 uF/25 V X7R, 1210**. Nets unchanged (/PRE_6V3–/GND, U11.2) |

**C18 is an ENGINEERING MARGIN choice:**
- It sits inside REF50 section 9.3's 1–50 uF, deliberately above the section 9.4 layout example of 1–10 uF, and was accepted by 529.
- It is **not** a stability repair.
- The 0.1 uF minimum is NOT cited: that is the EI grade (section 6.6), and the fitted part is AI (section 6.5).
- The exact-family DC-bias characterization is agent-522's packet `~/.local/share/agent-ee/reviews/2026-10-23-ee488-agent522/` (tdk-c6-characterization). Package maximum height: 2.80 mm.

**No C134.** No other decoupling changed: C100/C83 VCC-GND bypass and C19 bulk are unchanged.

**Files:**
- `storage-microsd/inputs/intent.json` (source);
- the re-emitted `storage-microsd/project`, `native.xml` and `erc.json` (ERC 0);
- requirements: `temperature-ratings.json`, the `requirement-map.json` schematic sha, and `compiled/` (scope 53430e3a…);
- `production-capture/sources/decoupling-additions-agentee-484.json`: a new `rebindings` entry for C18, template C13;
- `build.py`: the rebinding mechanism, which takes the template's verified part and assignment with C18's identity;
- the hand-fit citation re-pinned (J1 still `/parts/303`);
- the regenerated composition.

The stock was the fresh slice-A capture. C694521 was already in the BOM (C13), so no new LCSC id needed refreshing.

## Regeneration and native checks

- **Production:** `production_run.sh` from 3caf4927: build reproduces byte for byte, pipeline 28/28, observe exit 0.
- **Retention:** `evidence/emission-7d5b0d4d-agentee488/` (415 files, `retain.py --check` OK).
- **Installed project:**
  - schematic `78637c6e…`;
  - board `cbfea9be…` (313 footprints);
  - pro `85c517aa…` (embedded provenance bytes only);
  - dru `2769902a…` (unchanged, the 484r selector).
- **ERC (`erc-new.json`):** 0 violations.
- **Correspondence (`correspondence-new.json`):** 309 schematic / 313 board; H1–H4 are board-only. Only the 2 inherited U3 pad 18/19 net-name escaping findings remain.
- **Board delta vs 484r2:** exactly three ELECTRICAL changes (C133.2 and C84.2 /GND → /+5V_CAN; C18 0603 1 uF → 1210 22 uF). The geometry is NOT unchanged: see the correction below.

## Relationships (`agentee-478-prep`)

- **New module `relationship_measure.py`:**
  - `named_return_leg` measures exactly the named device pad and support pad on the named net, with no GND inference.
  - `verdict` returns 'unsatisfied' for a declared but missing, wrong-net or unmeasurable return, never 'within'.
- **The old defect:** `measure()` had `ok = s <= max and (r is None or ...)`, so a None return PASSED. Fixed.
- **U100.5–C133 and U21.5–C84** carry named returns (U100.3/U21.3 → C133.2/C84.2 on /+5V_CAN, 5 mm).
- **`electrical-locality-named-returns.json`** emits them as agent-524's `agent-ee.electrical-locality/1` obligations: supply and return from/to reference, pad and net; max_distance_nm; citation and provenance.
- **C133's allocation note** now reads VIO-to-VCC.
- **Tests:** `test_relationship_measure.py` passes 9/9: positive, overrun, wrong-net, no-GND-inference, missing support/device return pad, unmeasurable generic return, supply-only.
- **Real-data negative:** on the pre-change R5 board, U21.5–C84 is 'unsatisfied', because its pad 2 is still on /GND there.
- **Validator:** PASS, 313 footprints, 0 unassigned, 0 duplicates, 214 relationships.

## Deltas for 449 to forward (486/479)

- **486 / 480 height table:** C18 is now 1210 (2.80 mm package maximum) instead of 0603. agent-507's height/reservation data must update the C18 row.
- **479 / 524:** the named-return obligations (`electrical-locality-named-returns.json`) are ready for the effective-policy `electrical_locality`. The contract relationships must equal the policy entries. No agent-ee code was changed here.


## Correction (AGENTEE-488c, Astra HIGH H3)

The earlier claim "board delta EXACTLY three" holds only for the component, net, value and footprint delta.

**The native geometry changed:** 287 footprints moved between board 0b68a0ac and board cbfea9be.
- 286 moved by +2.54 mm in Y; C18 moved by +1.27 mm. No rotation changed.
- The outline UUIDs also changed.
- **Cause:** the scaffold's off-board staging column, ordered by reference, reflowed after C18's larger 1210 courtyard.
- **Unmoved:** C1–C17, the fixed parts J1–J3, U1 and U2, and H1–H4.
- **Electrically preserved but moved:** C100, C83 and C19.
- The scaffold reflow is NOT reverted.

**Downstream implication:** no prior placement or routing acceptance (R1–R5, ROUTE-1 to ROUTE-4, or any evidence measured on an earlier emitted board) carries over to this board. Placement and routing must be redone from this emission.

## AGENTEE-488c checkpoint (Astra HIGH H1 to H3): 2026-10-23T12:56:42Z to 13:35:12Z, over the 25-minute bound

**Base:** fome-mc main **33c5ba8** + `wt/agentee-stock-484r2` head **60f6a78d** (clean merge) + `wt/agentee-186` **324b37ee**, which includes 488 c98e1135 (clean merge). Branch `wt/agentee-488c`.

### H1: FIXED

- **Emitter:** `agentee-478-prep/build_prep.py` emits each supply/return pair in the consumer's schema: `from`, `to`, `max_distance_nm`, `citation` and a `provenance` OBJECT (`class: default`, numeric_provenance, decision).
  - The unsourced 3/5 mm values stay advisory; no hard authority is claimed.
- **New test:** `test_locality_consumer.py` runs agent-ee a085fbfa `electrical_locality.validate` and `locality_provenance.classify` on the EMITTED file.
- **Before** (`h1-validate-before.txt`): "locality pair needs from/to, optionally max_distance_nm and citation".
- **After** (`h1-validate-after.txt`): validates; all 4 legs are `default / advisory`; the named returns are on /+5V_CAN at 5 mm.
- `electrical-locality-named-returns.json` is regenerated, and the validator still PASSes 313/0/0.

### H3: FIXED (report corrected above)

- **Delta:** 3 electrical changes plus 287 moved footprints (286 by +2.54 mm Y, C18 by +1.27 mm).
- **Implication:** no prior placement or routing acceptance carries over.

### H2: NOT CLOSED, a concrete HOLD

**Done (existing workflow):**
- `requirements/rev3-microsd/spec-record.json` and its receipt were re-captured with the recorded `agent_ee.spec_record capture` argv for main's REQUIREMENTS.md (dd6555f7…; record 21288e01…; `verify` OK).
  - Main itself carried a stale spec record after 7a1cdd9 changed REQUIREMENTS.md without re-capture.
- The requirement-map spec and spec-record pins were updated, and `compiled/` recompiled (scope 3271312d…; placement subjects match).
- The J1 hand-fit REQUIREMENTS pin was updated in `pipeline.py` HAND_FIT_CHAIN and `assembly/hand-fit-policy.json` (the quoted line 139 is unchanged).
- New retention dir: `emission-7d5b0d4d-agentee488c`.

**Blocked:** the composed production run (`production_run.sh` from c7328b03) fails at pipeline.py:718-729: "the microSD spec differs from telemetry-pod-rev3 beyond the POD-CD-STORAGE row: changed ['POD-ME-1']". The guard admits ONLY the POD-CD-STORAGE addition relative to the pinned telemetry-pod-rev3 source. Main's 486 height correction changed POD-ME-1, so no coherent retention can be produced without a decision.

**Remaining work, for 449/529 to authorize:**
- (1) Either record the POD-ME-1 change as an accepted revision delta:
  - extend the guard's allowed set to {added POD-CD-STORAGE, changed POD-ME-1}, citing the 486/529 decision (owner relay 27c51f73@1, a13a1ba8 v2);
  - and, if that file is meant to record the current comparison, add the POD-ME-1 entry to `requirements/rev3-microsd/revision-delta.json`.
- (2) Or re-pin the telemetry-pod-rev3 requirement source to include the correction.
- Then re-run `production_run.sh`, `retain.py` (new retention, `--install`), the composed `retain.py --check`, and the fresh git-archive proof.
- **Not done:** I did not weaken the guard, rewrite checksums or edit retain.py.

## AGENTEE-488c H2 (agent-529 38f1ac7e v1 item 1): 2026-10-23T13:49:39Z to 13:52:05Z

**Base:** `wt/agentee-488c` feaf9997, which includes the 491 BOM commits.

**Done:**
- **New module `production-capture/requirement_revision.py`:** the EXPLICIT accepted revision delta. The historical telemetry-pod-rev3 registry source and its identity are unchanged, and `pipeline.py` still checks the pinned capture against `pod_driver.SOURCES`. It admits ONLY:
  - the adopted POD-CD-STORAGE addition (non-acceptance);
  - the EXACT POD-ME-1 correction: text sha256 d865a76d… → 09c89ce3…, with id/kind/section/cells unchanged and `text_sha256` consistent.
  - Both are bound to REQUIREMENTS.md dd6555f7… and the recaptured spec record 21288e01…, citing owner-relayed a13a1ba8@2 and accepted AGENTEE-486 / 27c51f73. This is a height ESTIMATE, not a measured 90 mm cap.
- **Refusals:** every other added/removed/changed row, prose change, acceptance-set change, stale pin, and a different text under the allowed ID.
- **`pipeline.py` `compose_requirement_source`:** uses it. The docstring and the composed-scope limitation no longer say "only one row differs". The limitation states that the current POD-ME-1 text is the governing mechanical obligation and the same ID transfers no earlier acceptance.
- **`requirements/rev3-microsd/revision-delta.json`:** regenerated by the new `make_revision_delta.py` with the accurate current identity and counts (1 added, 1 changed POD-ME-1 with before/after text and hashes, 77 unchanged). The README row is updated.
- **Controls** (`test_requirement_revision.py`, `h2-revision-controls.txt`): 9/9.
  - Positive: the exact delta on the REAL pinned/current records.
  - Negative: changed-same-ID text, POD-ME-1 changed outside its text, unrelated changed row, removed row, stale spec pin, stale record pin, correction absent, prose change.

**Gap at cutoff:** the coherent production / new retention / COMPOSED `retain.py --check` / fresh-checkout proof was NOT run.
- The accepted source stack includes the 491 resistors, and build-out refuses (`h2-build-out-refusal-491.log`): "binding differs from the canonical record: R74". No canonical part records exist for C723587 or C861219.
- **Needed** (the 491 remaining work):
  - canonical datasheet acquisition plus `prepare_record` for both ids;
  - a `build.py` declaration for a part not yet in the design;
  - the rating source;
  - then production on generation-day stock (refresh C723587/C861219), a new retention, the composed `retain.py --check`, and the fresh proof.
- **Not done:** no manual checksum repair, no retention change, no carryover of old placement evidence.
