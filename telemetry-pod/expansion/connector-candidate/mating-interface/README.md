# J1 mating interface: source-bound evidence (AGENTEE-207)

This folder checks the mechanical interface around the selected J1 header, TE
**1-776163-1** (LCSC C596198; gold-finish, black, 35-position right angle), against
captured TE sources. It covers the mating plug, the panel and the PCB thickness. It
is evidence only. No design file, footprint, model pose or requirement is changed,
and it claims no physical fit. The header STEP pose, support flats and 35-tail
alignment are covered in `../README.md` and `../review/`, and are not repeated here.

The machine-readable record is `interface.json`. `SHA256SUMS` covers the captured
sources and the record. `python3 -I check.py --self-test` re-hashes every source
(including the existing `../sources/776163-K1.pdf`). It also checks that every
citation names a known source with a page and figure, and that the installed-fit
items stay UNRESOLVED. Four negative controls must be rejected.

## Sources

| Key | Document | Revision | Class | sha256 (first 16) |
| --- | --- | --- | --- | --- |
| K1 | TE drawing 776163, header, 2 sheets (`../sources/776163-K1.pdf`) | K1, 16SEP2024 | manufacturer original (existing capture) | `7ed1f2a5f6ebf57a` |
| D2293782 | TE PCN-24-229857 (13-JAN-25). Pages 4-5 carry TE drawing 2293782, *Plug assembly, AMPSEAL family* | E2, 28JUN2023 (PCN redline marked PRELIMINARY) | TE document via distributor (Farnell) | `07c8c4466907c56b` |
| AS114 | TE application spec 114-16016, 9 pages | G, 14 MAR 11 (superseded; current S3 not captured) | TE document, third-party mirror | `245aa46bdc39c1e1` |
| PP776164 | TE.com product-page print for 776164-1, 5 pages | print of 2023-07-05 | web attributes, corroboration only | `1ffe925281e8cc11` |

URLs, capture times and byte counts are in `interface.json`. TE's own document
endpoint returned HTTP 403 for every request on 2026-10-22. That includes the K1 URL
that worked on 2026-10-20, so the block is host-wide. The missing captures are listed
in `missing_captures` with exact URLs: the current 2293782, drawing 776164, 114-16016
S3, 108-1329, and the 776164-1 STEP model. No TLS check was bypassed.

## Findings

| Item | Status | Basis |
| --- | --- | --- |
| Mating plug identity and keying | **SOURCED** | **776164-1**, black, key slots 6 and 20. K1 sheet 1 note 5 (header mates to plug assembly 776164) and note 3 (color keying), plus the K1 color table (1-776163-1 = gold/black). 2293782 E2 sheet 1 part table (35-position plugs mate right-angle 776163 headers; black = 776164-1) and note 2, plus sheet 2 *35-position key slot locations*. |
| Mated height / envelope | **UNRESOLVED** | No mated drawing, engagement depth or plug STEP was captured. Plug reference dimensions only: 35-position A 63.4, B 66 (pass-through opening diameter), C 27.45 (2293782 E2 sheet 1 table). 38.29 ± 1.40 length and 7.0 latch rise appear on the 23-position view only. |
| Panel cutout and mounting | **PARTIAL** | K1 sheet 2: 4× Ø3.00–3.30 holes at 63.4 × 18.1; opening 60.0–60.5 × 24.2–25.2, R6.60–6.80; panel 5 max with Z-Z options above 2.0; flatness 0.5; flush before torque. K1 sheet 1 note 1: Ø2.5 thread-forming screw, 0.6–0.8 N·m, which the customer must test. AS114 G's 2 mm panel limit is overridden by K1 under G's own §2.3 drawing-priority rule. The enclosure, screws and seal are open. |
| PCB thickness | **PARTIAL** | TE states only a nominal **1.57 mm** (K1 sheet 2 layout title; AS114 G p.6 §3.9.A), with no tolerance. The pod's board is 1.6 mm (REQUIREMENTS.md line 59). The allowed range and board-lock retention at 1.6 mm are UNRESOLVED. |
| Latch / CPA and tool access | **PARTIAL** | AS114 G p.9 Fig. 13: latch must be engaged for mating; screwdriver slot lifts it for unmating. Pages 4-5 §3.4 / Fig. 7: 4.8 mm blade opens the wedge lock (harness-side). CPA 2373965-1 appears only as a compatible part on the product-page print; the CPA procedure is not captured. |
| Harness exit direction | **PARTIAL** | Axial, out the rear wire seal, away from the mating face (2293782 E2 sheet 1 section; product print: exit angle 180°). On the pod this is +Y in the footprint frame, outward through the panel. Bend radius, routing and strain relief are open. |
| Installed enclosure fit | **UNRESOLVED** | No enclosure or cowl source. |
| Installed harness | **UNRESOLVED** | No routing or bend-radius source. |
| Installed tool access | **UNRESOLVED** | No source for latch-slot or panel-screw tool lanes. |

### Notes for reviewers

- **REQUIREMENTS.md lines 43/58.** The candidate mate 776164-1 is confirmed by two
  TE drawings that agree. Those lines name the tin header 776163-1, but the
  selection is the gold 1-776163-1. Both are black, so both mate 776164-1. The
  finish deviation itself remains open in `POD-CD-HARNESS-CONNECTOR`.
- **Status of the 2293782 copy.** It is the PCN redline at E2, watermarked
  PRELIMINARY. The PCN states it changes only the housing-material note.
  Re-confirm identity and keying against the current released revision when TE
  access returns.
- **Different plug family in the same PDF.** Drawing 2371886 (pages 2-3) is the
  reduced-wire-size 2371885 family. It is not the selected mate.
- **Contacts and seal plugs.** The sources name contact families 770520 / 770854
  and seal plug 770678-1. None is selected here.
- **PCB thickness arithmetic.** For a rigid header, a 1.6 mm board instead of
  1.57 mm shortens the 3.50 mm modeled tail projection by about 0.03 mm. That stays
  within K1's (3.0–4.0) reference range. This is arithmetic, not qualification.
