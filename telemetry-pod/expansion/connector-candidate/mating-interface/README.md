# J1 mating interface: source-bound evidence (AGENTEE-207)

This folder checks the mechanical interface around the selected J1 header, TE
**1-776163-1** (LCSC C596198; gold-finish, black, 35-position right angle), against
captured TE sources. It covers the mating plug, the panel and the PCB thickness. It
is evidence only. The PCB thickness is owner-accepted (2026-10-22, see
`sources/owner-decision-2026-10-22-board-thickness.txt`). No design file,
footprint, model pose or requirement is changed, and it claims no physical fit. The header STEP pose, support flats and 35-tail
alignment are covered in `../README.md` and `../review/`, and are not repeated here.

The machine-readable record is `interface.json`. `SHA256SUMS` must list exactly
`README.md`, `check.py`, `interface.json` and the four in-packet sources, once each,
with well-formed digests. `python3 -I check.py --self-test` checks that first and
stops if any entry is missing, duplicated, malformed or unexpected. It then
re-hashes every listed file and every source (including the existing
`../sources/776163-K1.pdf` and the captured fab profile
`../../production-capture/sources/fab-profile/fab-profile.json`, each checked against
its record hash). Item IDs must be
unique before anything is indexed, so acceptance cannot depend on item order.
Every citation must name a known source with a page and figure, and the
installed-fit items must stay UNRESOLVED. Thirteen negative controls must be
rejected, including a duplicate promoted item in both orders and an empty
`SHA256SUMS`.

## Sources

| Key | Document | Revision | Class | sha256 (first 16) |
| --- | --- | --- | --- | --- |
| K1 | TE drawing 776163, header, 2 sheets (`../sources/776163-K1.pdf`) | K1, 16SEP2024 | manufacturer original (existing capture) | `7ed1f2a5f6ebf57a` |
| D2293782 | TE PCN-24-229857 (13-JAN-25). Pages 4-5 carry TE drawing 2293782, *Plug assembly, AMPSEAL family* | E2, 28JUN2023 (PCN redline marked PRELIMINARY) | TE document via distributor (Farnell) | `07c8c4466907c56b` |
| AS114 | TE application spec 114-16016, 9 pages | G, 14 MAR 11 (superseded; current S3 not captured) | TE document, third-party mirror | `245aa46bdc39c1e1` |
| PP776164 | TE.com product-page print for 776164-1, 5 pages | print of 2023-07-05 | web attributes, corroboration only | `1ffe925281e8cc11` |
| OWNER20261022 | Owner decision, J1 board thickness and design deliverables (`sources/owner-decision-2026-10-22-board-thickness.txt`); owner -> agent-509 -> agent-449, Cairn d162e001 and b706da93 | 2026-10-22 | owner-relayed (agent-drafted, unconfirmed) | `e190ade5ee8e7c75` |
| FAB | Captured JLCPCB fab profile, `finished_thickness_tolerance` (`../../production-capture/sources/fab-profile/fab-profile.json`) | as of 2026-10-18 | manufacturer published capability (existing capture) | `02e484728bbcf695` |

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
| PCB thickness | **SOURCED** (owner-accepted) | Owner decision as relayed by agent-509, 2026-10-22 (OWNER20261022; agent-drafted wording, not owner-confirmed). Component-side fit, the J1 basis: at least ±10% of the manufacturer's recommended nominal is the owner's inclusive through-hole fit-screening default (AGENTEE-448). TE's 1.57 mm (K1 sheet 2 layout title) gives 1.413–1.727 mm, and the 1.6 mm board is inside it (about 1.9% from nominal). Explicit manufacturer functional limits would override; outside the band alone is advisory. Board side, separately: the standard JLCPCB four-layer 1.6 mm board is accepted, with JLCPCB's published ±10% finished tolerance (1.44–1.76 mm; FAB `finished_thickness_tolerance`) as a board-side fact that is not the component-fit basis. No special tolerance, TE confirmation, enclosure CAD or owner harness is needed for placement, routing or bare-board fab readiness. The normal footprint, finished-hole/pad, retention and solder-joint checks remain. *Historical context, not a gate:* superseded AS114 rev G p.6 §3.9.A ("shall be 1.57 mm") with its p.1 general ±0.13 mm reads as 1.44–1.70 mm. |
| Latch / CPA and tool access | **PARTIAL** | AS114 G p.9 Fig. 13: latch must be engaged for mating; screwdriver slot lifts it for unmating. Pages 4-5 §3.4 / Fig. 7: 4.8 mm blade opens the wedge lock (harness-side). CPA 2373965-1 appears only as a compatible part on the product-page print; the CPA procedure is not captured. |
| Harness exit direction | **PARTIAL** | Axial, out the rear wire seal, away from the mating face (2293782 E2 sheet 1 section; product print: exit angle 180°). On the pod this is +Y in the footprint frame, outward through the panel. Bend radius, routing and strain relief are open. |
| Installed enclosure fit | **UNRESOLVED** | Future design deliverable: the enclosure and panel are team-designed; the only external constraint is the seat cowl. Verified after design. Not a blocker for placement, routing or bare-board fab readiness. |
| Installed harness | **UNRESOLVED** | Future design deliverable: the harness is team-designed; the only external constraint is the seat cowl. Routing and bend radius are verified after design. Not a blocker for placement, routing or bare-board fab readiness. |
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
- **Lead protrusion (datums stated).** The 3.50 mm in `../README.md` runs from the
  rear support flats, which rest on the PCB top, to the tail tips, so about 1.9 mm
  of tail remains below a nominal 1.6 mm board. That is not a fit limit: J1 is a
  through-hole header whose leads are trimmed after soldering, per the owner's
  assembly sequence (seat, tack one pin, re-seat/align, solder the rest, trim the
  excess stickout). K1 sheet 1 section A-A's (3.0–4.0) runs from the header seating
  plane to the tips, not from the board underside, and is not compared with it.
  The solder-joint check remains a normal board-side check.
