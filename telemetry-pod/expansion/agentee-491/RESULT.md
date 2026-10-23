# AGENTEE-491: OVP ladder value/BOM binding (agent-529 110afb4e v1 / 74db43f0 v1)

## Run record

**Clock:** started 2026-10-23T13:42:20Z, ended 2026-10-23T13:45:19Z.

**Base:** `wt/agentee-488c` 0cb247f8, which is fome-mc main 33c5ba8 + stock-484r2 60f6a78d + 186 324b37ee + the 488c H1/H3 fixes.

**Packet:** agent-522 `~/.local/share/agent-ee/reviews/2026-10-23-ee491-agent522/`, SHA256SUMS 58040048…

## Canonical source edits (done)

`storage-microsd/inputs/intent.json`:
- **Middle:** R74, R78, R82 change from 68.1 kOhm (C861521) to **75 kOhm, YAGEO RT0603BRD0775KL, LCSC C723587**.
- **Bottom:** R75, R79, R83 change from 215 kOhm (C861226) to **208 kOhm, RT0603BRD07208KL, C861219**.
- **Top:** R73, R77, R81 are unchanged at 1.05 MOhm (RT0805BRD071M05L, C7353633).
- **Datasheet bindings** use agent-522's retained fetches:
  - RT0603BRD0775KL: sha256 7c8e6368…, fetched 2026-10-23T12:50:39Z;
  - RT0603BRD07208KL: sha256 ffde22da…, fetched 2026-10-23T12:50:39Z.
- **Ratings:** the old `AGENT_EE_Ratings` field pinned the PREVIOUS part's pilot rating record, so it is removed rather than carried onto a different part (see remaining work).
- **Unchanged:** the same 0603 footprints and the same nets. No 486 height or 479 relationship effect.

## Focused validation

- **storage-microsd re-emission** (agent-ee f92d71c emitter): verify.py "contract holds; ERC zero violations; 309 components, 235 nets".
- **Netlist delta:** EXACTLY the six value/LCSC changes above, 0 net changes, footprints unchanged.
- **ERC:** `storage-microsd-erc.json`, 0 violations.
- **Requirements:** temperature-ratings regenerated; the map's schematic sha updated; compiled scope recompiled (a7a4c954…). Placement subjects and temperature ratings match. The counts are unchanged.
- **Stock:** the read-only capture via agent-ee `jlc_stock_capture` is `production-capture/sources/assembly-stock-20261023-491`. C723587 is found with 182,799; C861219 is found with **1,901**. Both returned HTTP 200 at 2026-10-23T13:43:44Z. Generation-day stock must be refreshed at generation, especially for the 208 k part.
- **README:** `interface-preparation/sensor-power/README.md` records the corrections:
  - the stale 68.1 k / 215 k bounds are marked SUPERSEDED;
  - the new post-stress bounds come from the 522 packet (OV trip up to 8.21606 V);
  - the AGENT-DERIVED >= 8.3 V continuous STATIC screen; 5–8 V sensors are excluded; transients are UNQUALIFIED (OVP is not a clamp);
  - Izze 8.216 V is inside its 5–10 V operating range, with no absolute maximum published, and its 120 mA harness figure is the basis for 150 mA;
  - Honeywell/Izze and the CAN2 proposals are NOT adopted; the 650 mA / 210 mA / 1.487 A figures stay CONDITIONAL; 5 V +/-1% aux stays OPEN.
- **REQUIREMENTS.md** (owner text) is deliberately not edited.

## Regeneration: STOPPED (two blockers, not bypassed)

- **(1) Canonical part records do not exist for C723587 and C861219.** `production-capture/build.py` re-verifies every bound part against `canonical-parts/records` (part_record.prepare_record / qualify_record at agent-ee 014c7c3e). It will refuse "binding differs from the canonical record: R74". The existing `rebindings` mechanism only reuses a part already in the design. This needs:
  - the canonical acquisition of the two datasheets through the existing acquisition producer (522's packet bytes are review captures, not canonical acquisition manifests);
  - `prepare_record` for both ids;
  - the parts-manifest declaration for a NEW part (a small `build.py` extension: the additions/rebindings source naming a canonical record instead of a template);
  - the passive rating source for binding-fill (`composition/rating-sources.json`), so the ratings are regenerated rather than inherited.
- **(2) The same `pipeline.py:718-729` requirement-source guard as 488c** (POD-ME-1 changed by 486). The agent-529 ruling had not been relayed when this slice reached regeneration.
- **Then:** production run, new retention, `retain.py --check`, the composed check on the then-current main, a fresh-checkout proof, and the board delta.
  - **Expected board delta:** the six value/part changes, plus any staging moves. Same-footprint resistors should not reflow the column; this must be verified and disclosed.
- **Not done:** the guard was not weakened, no sums were rewritten, and retain.py was not edited.

## AGENTEE-488c/491 coherent production (13:54:53Z to the 14:34:53Z bound): INCOMPLETE, stopped at the stock gate

**Done (commits 8757050, ed884e4, 9bb03d0 on wt/agentee-488c, base 92e66373):**
- **Acquisition (existing path):** `agent_ee.datasheet_capture` (agent-ee 7d5b0d4d) on `canonical-parts/acquisition-491-bindings.json` wrote `canonical-parts/acquisition-491/`. Both parts were captured, and their bytes equal the bound PARAM_Datasheet hashes:
  - C723587: 7c8e6368…;
  - C861219: ffde22da….
- **Catalog:** `jlc_stock_capture` into `canonical-parts/catalog-491/`, as_of 2026-10-23T13:55:30Z.
  - C723587: stock 182799.
  - C861219: stock 1901.
- **Records:** `prepare_record` + `qualify_record`, called exactly as in `build_records.py`, wrote `canonical-parts/records-491/` (C723587-7c8e63688a91.json, C861219-ffde22da4914.json, index.json). These parts are not in `parts-closure/inventory.json`, so `build_records.py` itself does not list them. This is recorded in index.json.
- **build.py declarations:** six `rebindings` entries with a `record` key in `sources/decoupling-additions-agentee-484.json` (R74/R78/R82 to C723587; R75/R79/R83 to C861219).
  - build.py builds each part entry from that canonical record.
  - The existing binding-vs-record check still applies unchanged.
  - The 98 AGENT_EE_Ratings rule is unchanged: the six never carried the field. This corrects my earlier note above, which said otherwise.
- **Rating source:** `canonical-parts/records-491/rating-source.json`, taken from the acquired YAGEO per-part product sheets (page 1). These sheets are not the RT series datasheet.
  - 0.1 W (70C);
  - 75 V DC max continuous, 150 V max overvoltage, 100 V dielectric withstanding;
  - -55/+155°C;
  - -/+25 ppm/C.
- **Build:**
  - build-only in the image: exit 0, 309 references (`build-only-ed884e4.log`);
  - in production: build-out exit 0 and build-check exit 0.

**Gap (concrete):** pipeline.py refused at 14:07:29Z (`production-refusal-stale-stock.log`): `stock capture needs a refresh for ['C723587', 'C861219'] (older than 24 h ..., or not observed); no generation on stale stock`.
- The pipeline default `sources/assembly-stock-20261023` (81 ids, 11:14Z) lacks the two new ids. A single capture covering all 83 ids is required.
- A read-only 83-id capture into `sources/assembly-stock-20261023-491b` was started at about 14:08Z. It had not completed when the remaining time ran short.
- A full production run takes about 17 min, which could not finish inside the bound, so it was not launched.

**Not done:** production pipeline, new retention + `--install`, composed `retain.py --check`, fresh git-archive proof, ERC/correspondence/validator on a new board, and the board delta vs cbfea9be. No checksum repair, no guard or retention weakening, and no old placement evidence carried over.

**Next:**
1. Complete or redo the 83-id capture.
2. Point `pipeline.py` STOCK at it, then commit.
3. Run `production_run.sh`, then `/tmp/a491b/post.sh`-style retain (DEST `evidence/emission-7d5b0d4d-agentee491`, which does not yet exist) + `--install`, `--check`, the archive proof, and the checks.
