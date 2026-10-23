# AGENTEE-477: telemetry-pod 3D model gaps — 9 resolved, 15 intended-none, 2 blocked (owner fetch)

Source: owner to agent-519, 2026-10-23, "the missing 3d models need to tracked down" (Cairn e460bb2c), relayed by agent-529 via agent-519. These are coordinator records, not owner text.

**Clock:** started 2026-10-23T08:55:44.41Z, ended about 09:05Z, within the 60-minute bound.

**Input (immutable; isolated copies only):**
- the render pin ROUTE-4 `5690da57e291dff46f80b239c1c81f164d0622c6d4c0d03b65437e653f025825` (`~/.local/share/agent-ee-render-job/pinned/5690da57…`, with `inputs/models/`);
- the working board ROUTE-3 `0806617082c33df6daaa00f5d9c6131e7e07ac6160aadc07a2b2bcb90b5ac651` (fome-mc main `route-3/candidate/`).

The footprints are identical in both.

**Runtime:** host KiCad 10.0.7 (`kicad-cli` 10.0.7; pcbnew 10.0.7-10.0.7~ubuntu24.04.1) and `kicad-packages3d` 10.0.7, every step under native-admit on proximal (`logs/native-admit-events.jsonl`).

**Not done:** no gallery publish or pin (449's job), no footprint or pad changes, no login, purchase, upload or cloud. Models are visualization only; this is **not** mechanical or placement acceptance.

## Coverage (native inventory: a declared, existing, shown model per footprint)

| | Footprints with a loadable model | Without |
|---|---|---|
| Before (ROUTE-4 pin) | **283 / 309** | 26 |
| After (candidate) | **292 / 309** | 17: H1–H4, JP1–JP5, TP1–TP6 (intended-none), L1, L2 (blocked) |

- **KiCad load evidence** (`kicad-cli pcb export step`, exit 0 both; `logs/load-*.log`; STEP product lists in `logs/products-*.txt`): the after export adds exactly the STEP products `HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm`, `WSON-6_1.5x1.5mm_P0.5mm` (also `WSON6_15x15mm_Pitch05mm`), `D_SOD-882D` and `SOT-223`. J1's `c-1-776163-1-t-3d` and U3's `U3` products are present before and after.
- **Not committed:** the STEP exports are 25 MB; their hashes are in `sources.txt`.
- **Caveat:** `kicad-cli pcb render` logs nothing when a model file is missing, so the STEP products and the renders are the load evidence.

## Per-reference table

| Ref(s) | Part (LCSC) | Footprint | Model source / licence / sha256 | Offset / rotation / fit evidence | Status |
|---|---|---|---|---|---|
| U5, U7 | TI LMR36520ADDAR (C2879422), DDA0008B SO-8 PowerPAD | `PodPower:DDA0008B` | KiCad 10.0.7 stock `${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm.step`, CC-BY-SA 4.0 + KiCad exception, `4fd09ee3…401f` | 0,0,0 / 0,0,0. All 8 signal pads match the stock footprint by number and 1.27 mm pitch; rows at ±2.70 vs ±2.65 mm (0.05 mm). Our EP is larger (2.95×4.9, 9 sub-pads) than the model's 2.41×3.1 EP, which is visual only. `fit.json`; `views/fit-U5.png`, `fit-U7.png` | **resolved** |
| U6, U12 | TI TPS7B4253QDDARQ1 (C129339), DDA0008J | `PodPower:DDA0008J_C02` | same HSOP-8-1EP model | same pad match (0.05 mm); `views/fit-U6.png`, `fit-U12.png` | **resolved** |
| U16, U18, U19 | TI TPS389001DSER (C1509297), DSE0006A WSON-6 1.5×1.5 | `PodSupervisor:DSE0006A` | stock `Package_SON.3dshapes/WSON-6_1.5x1.5mm_P0.5mm.step`, `b286efb1…652f` | 0 / 0. All 6 pad centres within 0.025 mm of the stock footprint; our pads are longer (0.7–0.9 vs 0.75–0.85 mm). `views/fit-U16/18/19.png` | **resolved** |
| D3 | Nexperia PESD5V0C1BLS-QYL (C5311564), SOD882BD | `PodPower:SOD882BD` | stock `Diode_SMD.3dshapes/D_SOD-882D.step`, `741b952a…b3d7` | 0 / 0. Pads identical to stock `D_SOD-882D` (0.0 mm, 0.0 mm size). `views/fit-D3.png` | **resolved** |
| Q1 | Diodes DMP6023LE-13 (C154901), SOT-223 | `PodPower:DMP6023LE_SOT223` | stock `Package_TO_SOT_SMD.3dshapes/SOT-223.step`, `77ad6dba…f654` | offset 0, **rotation Z −90°**. Our footprint is the stock SOT-223 turned a quarter turn (pins at +y, tab at −y; row 3.20 vs 3.15 mm). Rendered both signs: −90 puts the 3 leads on the 3 pads and the tab on the tab pad; +90 puts the tab on a signal pad (`views/q1-rotation-plus90-left-minus90-right.png`). `views/fit-Q1.png` | **resolved** |
| L1 | Bourns SRP7050TA-150M (C2045384), 15 µH | `PodPower:SRP7050TA` | **none**: no KiCad stock model (KiCad has SRP1050WA/2313AA/5030T/6060FA only); Bourns product page returns HTTP 403 to a scripted fetch | n/a | **blocked link** (owner fetch) |
| L2 | Bourns SRP7050WA-6R8M (C19947708), 6.8 µH | `PodPower:SRP7050WA` | same: no KiCad model; Bourns page 403 | n/a | **blocked link** (owner fetch) |
| H1–H4 | M3 NPTH mounting holes | `AgentEE_Mechanical_MountingHole_NPTH` | none needed: a bare NPTH, no component body (KiCad stock `MountingHole:MountingHole_3.2mm_M3` declares 0 models) | n/a | **intended-none** |
| JP1–JP5 | 2-pad solder jumpers (open) | `Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` | none needed: copper-only feature, no body (KiCad stock `Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` declares 0 models) | n/a | **intended-none** |
| TP1–TP6 (B side) | Pogo test pads ⌀1.5 mm | `PodFeatures:PogoPad_D1.5mm` | none needed: an exposed copper pad, no body (KiCad stock `TestPoint:TestPoint_Pad_D1.5mm` declares 0 models) | n/a | **intended-none** |
| J1 | TE AMPSEAL 1-776163-1 (C596198) | `PodConnector:AMPSEAL_35_1-776163-1` | existing `${KIPRJMOD}/inputs/models/c-1-776163-1-t-3d.stp` (TE Creo AP214, `43ba1f80…a473`) | unchanged: off (0, −31.8, 11.72), rot (−90, 0, 0); renders correctly in the pin | **loads**; see cause below |
| U3 | u-blox NEO-M9N-00B (C5119087) | `RF_GPS:ublox_NEO` | existing datasheet-derived visualization (`8a7f1984…62a5d9`; fome-mc `telemetry-pod/expansion/neo-m9n-model/`) | unchanged | **visualization-only** (classification below) |

## J1 cause

J1 **does load**:
- the current gallery isometric (bundle `5690da57e291-216cf677a645`) shows the AMPSEAL body on the bottom edge;
- the native STEP export contains `PRODUCT('c-1-776163-1-t-3d')`;
- the file is a valid TE Creo AP214 STEP.

**Cause of the "J1 missing" observations:** J1 (and U3) use a **project-local path** `${KIPRJMOD}/inputs/models/…`. Any render made from a project copy that lacks `inputs/models/` drops them **silently**, because `kicad-cli pcb render` reports nothing. Examples:
- kicad-route's routed candidate directory (ROUTE-1 `…/candidate/project/` has no `inputs/`);
- the ROUTE-1 front render.

**Remedy (for 449):** always pin or render with the models directory, as `render-job-pin.sh … [models-dir] …` already allows.

## GPS (U3) classification

The model stays **datasheet-derived visualization-only, not manufacturer CAD**:
- KiCad's stock `RF_GPS:ublox_NEO` footprint references `RF_GPS.3dshapes/ublox_NEO.step`, but **KiCad 10.0.7's `kicad-packages3d` ships no `RF_GPS.3dshapes`**;
- the fome-mc `neo-m9n-model/README.md` records that no official downloadable u-blox STEP was found;
- this slice found none either.

The basis is u-blox NEO-M9N-00B datasheet UBX-19014285 R08, nominal 16.0 × 12.2 × 2.4 mm (maxima 16.1 × 12.3 × 2.6 mm). If u-blox CAD is wanted, it is an owner fetch item (u-blox support/portal), not attempted.

## Pin-ready model set and mapping

- **No project-local model files are needed** for the 9 resolved references: all are KiCad 10.0.7 stock models resolved through `${KICAD10_3DMODEL_DIR}` (`/usr/share/kicad/3dmodels` on proximal). Nothing third-party is committed, and the licence travels with the KiCad package (`sources.txt` records the LICENSE hash).
- **The existing `inputs/models/`** (J1, U3) stays as is: the same directory as the current pin.
- **Mapping:** `model-mapping.json` (reference → filename, offset, rotation).
- **Candidate boards** (only model declarations added; `build_candidate.py` verified all 309 footprints keep FPID, pose, side, pads and nets, and that only the 9 mapped footprints gained exactly one model each):
  - `candidate/telemetry-pod.route4-models.kicad_pcb` (from the ROUTE-4 pin), sha256 **`b1bb009b4e4cb7a104b56ed5795c01006e0bc079af0faae3b575a8ba3de218c6`**: the render pin candidate;
  - `candidate/telemetry-pod.route3-models.kicad_pcb` (from ROUTE-3), sha256 **`57a7968d2547a24e395bd8bd87ab0325de7cd2c67108b21e0c2fdf25e46473b4`**.
- **Pin command shape for 449:** `render-job-pin.sh <candidate board> <pinned project .kicad_pro> <pinned inputs-models parent> <label> <note>`. Exact arguments are 449's.

**Views** (local `kicad-cli pcb render`, fit evidence only, not a publication): `views/candidate-b1bb009b4e4c-{top,bottom,isometric}.png`, per-reference crops `views/fit-<ref>.png`, `views/fit-montage.png`, and the Q1 rotation comparison.

## Blocked links (owner fetch, via 519)

- Bourns SRP7050TA (L1) 3D model: `https://www.bourns.com/products/magnetic-products/power-inductors-smd-shielded/product/SRP7050TA` (HTTP 403 to a scripted fetch).
- Bourns SRP7050WA (L2) 3D model: `https://www.bourns.com/products/magnetic-products/power-inductors-smd-shielded/product/SRP7050WA` (HTTP 403).
- Optional: u-blox NEO-M9N official CAD (none public; support/portal request).

## Sourced geometry for AGENTEE-474 / 472 (from the parts' own datasheets; hashes in `sources.txt`)

| Ref | Part | Body (datasheet) | Source |
|---|---|---|---|
| L1 | Bourns SRP7050TA | **7.3 ± 0.3 × 6.6 ± 0.3 mm, height 4.8 ± 0.2 mm**; terminal 1.8 ± 0.3 × 3.0 ± 0.3; a 6.7 ± 0.3 mm dimension also appears on the drawing | LCSC-hosted Bourns datasheet `5a7926dd…` |
| L2 | Bourns SRP7050WA | **7.9 ± 0.3 × 7.3 ± 0.2 mm, height 5.2 ± 0.2 mm** | LCSC-hosted Bourns datasheet `3f16305b…` |
| U3 | u-blox NEO-M9N-00B | 16.0 × 12.2 × 2.4 mm nominal; maxima 16.1 × 12.3 × 2.6 | u-blox UBX-19014285 R08 (fome-mc `neo-m9n-model/`) |

L1 and L2 are the tallest of the gap parts. Their footprint names match these datasheets.

The other resolved packages are standard: HSOP-8 body 3.9 × 4.9 mm, WSON-6 1.5 × 1.5 mm, SOT-223, SOD-882D. Their **heights were not extracted** from the TI/Diodes/Nexperia datasheets in this slice (the PDFs are retrieved; hashes in `sources.txt`). The KiCad models are nominal visualization, not sourced limits.

## Scripts (all read-only or isolated-copy)

- `inventory.py`: model inventory and coverage;
- `fit.py`: pad fit against the stock footprints;
- `build_candidate.py`: adds the declarations and verifies preservation;
- `crop.py`: fit views.
