# Addendum: source capture (agent-521 c13da285, relayed by agent-449; coordinator decision, not owner text)

This addendum follows the accepted packet `53f6d5bd` (items a/b). It adds captured JLCPCB and TE sources and
compares them row by row with `evidence.json`. `evidence.json` itself is unchanged, and so is every native value,
design file and `production-capture/` file. The record is `addendum-c13da285.json`; the captured bytes are in
`sources-c13da285/` (`sources.json`, and `NOTICE.md` for the licence/redistribution note). `check.py --self-test`
verifies them.

*Reporting corrections H1/H2 (review-ee446g HOLD on b3d570ca) are applied: a11 stays unknown with the JLC value
recorded separately, and F8/a8 now carry JLCPCB's published precision-routing conditions, with that option left
unqualified.*

**There is no concrete incompatibility.** Three rows (a2, a4, a7) change from unknown to **documented uncertainty**.
In each, JLCPCB's published tolerance band does not nest inside TE's band. That is interval arithmetic between two
published tolerances: no source or physical check shows a failing feature, so nothing is tightened or gated.

## Reused first

- **JLC.** The captured fab profile (`production-capture/sources/fab-profile/`) holds only trace, via, edge,
  hole-to-hole, layers, size, stackup and thickness. It has none of the requested hole facts, so the official page
  was fetched.
- **TE.** These captures give no board-lock geometry, PCB-thickness range or PCB retention:
  - S3, E5 and K1;
  - the header CVM zip (one member, the rev T STEP);
  - the historical 776163 J8, 114-16016 G, the PCN E2 redline and the product-page print.

  K1's title block names **PRODUCT SPEC 108-1329**, so that document was fetched.

## Sources

| Key | URL | Retrieved (UTC) | HTTP | sha256 | Stated version/date | Conditions |
| --- | --- | --- | --- | --- | --- | --- |
| JLCCAP20261023 | https://jlcpcb.com/capabilities/pcb-capabilities | 2026-10-23T03:18:00Z | 200 | `03af7196304852caf7ad2c05b024d9d944aa767c21283a748535c72907404c9e` (136648 B) | none stated; no Last-Modified (ETag `"20379-sICJo0639jaCyxLAY1PA53uyb6o"`) | per fact, below |
| TE1081329-403 | TE DDEController `DocNm=108-1329`, `PartCntxt=1-776163-1` (full URL in `sources.json`) | 2026-10-23T03:18:01Z | **403** AkamaiGHost | `48fc3d8a15b0a8b8d6d6aa8db1f35f02fd5a4b13a389d89bebacd7b9747dff28` (416 B refusal page; Akamai ref 18.470ed217.1792725481.3307e1fc) | n/a | **UNKNOWN**: no workaround attempted |

## JLCPCB facts (quoted verbatim from the retained page; `check.py` verifies each one near its label)

| Fact | Label | Quote | Conditions |
| --- | --- | --- | --- |
| F1 | Hole size Tolerance | "Through-holes: +0.13 / -0.08 mm" | Finished hole. The page does not split round holes by plating |
| F2 | Hole size Tolerance | "Press-fit holes：±0.05 mm (Finished hole size: 0.55-2.0mm. Multilayer ENIG boards and circular holes only. Mention the specific holes in PCB Remark)" | Multilayer, ENIG, circular, PCB remark |
| F3 | Average Hole Plating Thickness | "18μm" | An average, not a minimum |
| F4 | Hole Position Tolerance | "±0.075 mm" | Datum not stated |
| F5 | PTH annular ring (Multilayer) | "1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm" | Multilayer, 1 oz |
| F6 | Drill Diameter | "Multilayer: 0.15 – 6.3 mm" | |
| F7 | Min. Non-plated holes | "0.50mm" | |
| F8 | Dimension Tolerance (PCB specifications table) | "±0.1mm(Precision) and ±0.2mm(Regular) for CNC routing, and ±0.4mm for V-scoring" | The precision option is conditional. Outline table, Routed row, item ③: "③ Dimension tolerance for routed board edges: ±0.2 mm (regular precision); ±0.1 mm (high precision)". Item ④: "④ Minimum dimension 50*50mm for high precision, and at least 3 tooling holes with minimum 1.5mm diameter on different corners." Applicability to this board is **unqualified** (not demonstrated, selected or assumed); the regular ±0.2 applies by default |
| F9 | Thickness Tolerance | "e.g. For the 1.6mm board thickness, the finished board thickness ranges from 1.44mm(T-1.6×10%) to 1.76mm(T+1.6×10%)" | Thickness ≥ 1.0 mm |
| F10 | NPTH pad annular ring | "Recommended 0.45 mm or more." | NPTH with a copper pad; the J1 locators have none |
| U1 | Layer / drill-to-copper registration | **UNKNOWN** | Not stated on the page; no capabilities sub-page is linked; no other JLC URL was fetched |
| U2 | TE 108-1329 board-lock / retention leg | **UNKNOWN** | HTTP 403 (above) |

## Row-by-row comparison

| Row | Before | Now | Basis |
| --- | --- | --- | --- |
| a1 | consistent | consistent | Ø1.75 lies inside the 0.15–6.3 mm drill range (F6) |
| a2 | unknown | **documented uncertainty** | TE 1.65–1.85; JLC F1 gives 1.67–1.88 on 1.75, so the upper end is +0.03. The JLC band (0.21) is wider than TE's (0.20), so no nominal nests. Not a concrete incompatibility. The sourced F2 press-fit option (±0.05, giving 1.70–1.80; needs ENIG, multilayer, a remark) would nest. It is recorded but **not adopted** |
| a3 | consistent | unchanged | |
| a4 | unknown | **documented uncertainty**, registration still UNKNOWN | TE true position Ø0.1 (S) to datum A (radius 0.05) vs JLC ±0.075 with no datum (F4). They are different measurands. U1 is unknown |
| a5 | consistent | consistent | Ø2.85 ≥ the 0.50 NPTH minimum, inside the drill range (F6, F7) |
| a6 | unknown | unknown | TE is silent and 108-1329 returned 403 (U2). F10 does not apply because there is no copper |
| a7 | unknown | **documented uncertainty** | TE 2.77–2.93; JLC F1 gives 2.77–2.98, so the upper end is +0.05. Model-only context: the TE model's shoulder reaches radius 1.90 (Ø3.80) |
| a8 | consistent | consistent (nominal) | **Nominal conclusion, unchanged and independent of any fab tolerance:** both locator centres are 9.0 mm from Edge.Cuts, equal to TE's 9. **Fab capability, information only:** JLC routed edge is ±0.2 regular, the default (F8). The ±0.1 high-precision option requires "Minimum dimension 50*50mm for high precision, and at least 3 tooling holes with minimum 1.5mm diameter on different corners." (Outline table, Routed row ④); its applicability here is **unqualified**. The TE tolerance on the 9 is unresolved (S3 p.1 ±0.13 vs K1 governing with no 0-place value). No rule or geometry change; this is for the panel/enclosure deliverable |
| a9 | unknown | **consistent** | Design annulus 0.325 ≥ JLC multilayer 1 oz recommended 0.20 and minimum 0.15 (F5). At the JLC maximum finished hole it is 0.26 (informational) |
| a10, a12, a13 | consistent | unchanged | |
| a11 | unknown | **unknown** (TE requirement unknown) | Sourced JLC value, recorded separately: average hole plating 18 μm (F3; an average, not a minimum). **Missing:** the applicable TE hole-wall plating requirement or minimum for 1-776163-1, if any. S3, K1 and E5 state none, and 108-1329 (named in the K1 title block) was refused with HTTP 403 AkamaiGHost at 2026-10-23T03:18:01Z (sha256 `48fc3d8a…`, ref 18.470ed217.1792725481.3307e1fc). Absence from the captured documents is not evidence of no requirement |
| a14 | settled | settled | F9 confirms 1.44–1.76. Not reopened |
| b1 | unknown | unknown | U2 (HTTP 403). The reused TE captures contain no board-lock spec |
| b2–b8 | — | unchanged | Not informed by this capture |

## Proposal (not an action)

An owner drop of TE product specification **108-1329**, current revision, for 1-776163-1, following the AGENTEE-451
precedent. It is the only captured-source gap for rows a6 and b1. Registration (U1) would need a JLCPCB source
other than the capabilities page, which was outside this session's URL scope.

## Time

| Interval | Time |
| --- | --- |
| Session start | 2026-10-23T03:17:42Z |
| Capture lease (`native-admit --label "ee446g source capture" --class test --weight 1`) | requested and admitted at epoch 1792725480, done at 1792725481: **queued 0 s, admitted 1 s** |

The rest of the session was offline host work (reading, writing, `check.py`).
