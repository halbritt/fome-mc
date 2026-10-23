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
- **Board delta vs 484r2:** EXACTLY the three changes (C133.2 and C84.2 /GND → /+5V_CAN; C18 0603 1 uF → 1210 22 uF).

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
