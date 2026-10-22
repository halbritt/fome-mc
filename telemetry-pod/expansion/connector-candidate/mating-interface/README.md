# J1 mating interface: source-bound evidence (AGENTEE-207)

This folder checks the mechanical interface around the selected J1 header, TE
**1-776163-1** (LCSC C596198; gold-finish, black, 35-position right angle), against
captured TE sources. It covers the mating plug, the panel and the PCB thickness. It
is evidence only. The PCB thickness is owner-accepted (2026-10-22, see
`sources/owner-decision-2026-10-22-board-thickness.txt`). No design file,
footprint, model pose or requirement is changed, and it claims no physical fit. The header STEP pose, support flats and 35-tail
alignment are covered in `../README.md` and `../review/`, and are not repeated here.

The machine-readable record is `interface.json`. `SHA256SUMS` must list exactly
`README.md`, `check.py`, `interface.json` and the seven in-packet sources, once each,
with well-formed digests. `python3 -I check.py --self-test` checks that first and
stops if any entry is missing, duplicated, malformed or unexpected. It then
re-hashes every listed file and every source (including the existing
`../sources/776163-K1.pdf` and the captured fab profile
`../../production-capture/sources/fab-profile/fab-profile.json`, each checked against
its record hash). Item IDs must be
unique before anything is indexed, so acceptance cannot depend on item order.
Every citation must name a known source with a page and figure, and the
installed-fit items must stay UNRESOLVED. The 2026-10-22 TE drop record must
match the captured sources: each drop file is a capture or a byte duplicate of
one, the STEP zip holds exactly its recorded member (re-hashed, no absolute or
`..` path), no TE source carries an owner class, and every lead-claim verdict
is known and cited. Nineteen negative controls must be rejected, including a
duplicate promoted item in both orders, an empty `SHA256SUMS` and a TE source
relabelled as an owner statement.

## Sources

| Key | Document | Revision | Class | sha256 (first 16) |
| --- | --- | --- | --- | --- |
| K1 | TE drawing 776163, header, 2 sheets (`../sources/776163-K1.pdf`) | K1, 16SEP2024; the 2026-10-22 TE drop copy is byte-identical | manufacturer original (existing capture) | `7ed1f2a5f6ebf57a` |
| AS114S3 | TE application spec 114-16016, 13 pages (`sources/TE-114-16016-S3.pdf`) | S3, 30 APR 25 | manufacturer original (owner TE drop, 2026-10-22) | `645a74cb6e245a15` |
| D2293782E5 | TE drawing 2293782, *Plug assembly, AMPSEAL family*, 2 sheets (`sources/TE-2293782-E5.pdf`) | E5, 22APR2026 | manufacturer original (owner TE drop, 2026-10-22) | `a692de1959237481` |
| CVM776164F | TE customer view model CVM_776164-1, plug-only STEP in a zip (`sources/TE-CVM_776164-1-F-3d_stp.zip`; member `c-776164-1-f-3d.stp`, sha256 `81d69bbdf51f28d7…`) | F (from TE's file names only; the STEP header states none) | manufacturer original (owner TE drop, 2026-10-22) | `be5ceb67574a916f` |
| D2293782 | TE PCN-24-229857 (13-JAN-25). Pages 4-5 carry TE drawing 2293782, *Plug assembly, AMPSEAL family* | E2, 28JUN2023 (PCN redline marked PRELIMINARY; historical, superseded by E5) | TE document via distributor (Farnell) | `07c8c4466907c56b` |
| AS114 | TE application spec 114-16016, 9 pages | G, 14 MAR 11 (superseded by S3; historical) | TE document, third-party mirror | `245aa46bdc39c1e1` |
| PP776164 | TE.com product-page print for 776164-1, 5 pages | print of 2023-07-05 | web attributes, corroboration only | `1ffe925281e8cc11` |
| OWNER20261022 | Owner decision, J1 board thickness and design deliverables (`sources/owner-decision-2026-10-22-board-thickness.txt`); owner -> agent-509 -> agent-449, Cairn d162e001 and b706da93 | 2026-10-22 | owner-relayed (agent-drafted, unconfirmed) | `e190ade5ee8e7c75` |
| FAB | Captured JLCPCB fab profile, `finished_thickness_tolerance` (`../../production-capture/sources/fab-profile/fab-profile.json`) | as of 2026-10-18 | manufacturer published capability (existing capture) | `02e484728bbcf695` |

URLs, capture times and byte counts are in `interface.json`. TE's own document
endpoint returned HTTP 403 for every request from this host on 2026-10-22. That includes the K1 URL
that worked on 2026-10-20, so the block is host-wide. The missing captures are listed
in `missing_captures` with exact URLs: the current 2293782, drawing 776164, 114-16016
S3, 108-1329, and the 776164-1 STEP model. No TLS check was bypassed. The owner
then supplied S3, 2293782 E5, the rev F plug STEP and K1 as a drop folder
(AGENTEE-451); those entries are marked `resolved_by`. Still missing: product
data for 1-776163-1 and 776164-1, drawing 776164, and 108-1329.

## Findings

| Item | Status | Basis |
| --- | --- | --- |
| Mating plug identity and keying | **SOURCED** | **776164-1**, black, key slots 6 and 20. K1 sheet 1 note 5 (header mates to plug assembly 776164) and note 3 (color keying), plus the K1 color table (1-776163-1 = gold/black). 2293782 **E5** (released) sheet 1 part table (35-position plugs mate right-angle 776180 / 776163 headers; black = 776164-1) and note 2, plus sheet 2 *35-position key slot locations* (6 & 20); E2 says the same and stays historical. |
| Mated height / envelope | **UNRESOLVED** | No mated drawing or engagement depth is captured. The plug STEP (CVM776164F) is plug-only, in its own frame, with no mating datum. S3 p.8 Fig. 12: a completed 35-position plug clears a Ø66 opening. Plug reference dimensions only: 35-position A 63.4, B 66 (pass-through opening diameter), C 27.45 (2293782 E2 and E5 sheet 1 table). 38.29 ± 1.40 length and 7.0 latch rise appear on the 23-position view only. |
| Panel cutout and mounting | **PARTIAL** | K1 sheet 2: 4× Ø3.00–3.30 holes at 63.4 × 18.1; opening 60.0–60.5 × 24.2–25.2, R6.60–6.80; panel 5 max with Z-Z options above 2.0; flatness 0.5; flush before torque. K1 sheet 1 note 1: Ø2.5 thread-forming screw, 0.6–0.8 N·m, which the customer must test. S3 p.11 §3.6.B agrees: panel 2–5 mm, the same screw, torque 0.6–0.8 N·m in a cross pattern after a 0.3–0.4 N·m pre-torque. S3 Fig. 14 gives the opening height as 24.8–25.2 against K1's 24.2–25.2; K1 governs (S3 §2.3). Rev G's 2 mm limit is historical. The enclosure, screws and seal are open. |
| PCB thickness | **SOURCED** (owner-accepted) | Owner decision as relayed by agent-509, 2026-10-22 (OWNER20261022; agent-drafted wording, not owner-confirmed). Component-side fit, the J1 basis: at least ±10% of the manufacturer's recommended nominal is the owner's inclusive through-hole fit-screening default (AGENTEE-448). TE's 1.57 mm (K1 sheet 2 layout title) gives 1.413–1.727 mm, and the 1.6 mm board is inside it (about 1.9% from nominal). Explicit manufacturer functional limits would override; outside the band alone is advisory. Board side, separately: the standard JLCPCB four-layer 1.6 mm board is accepted, with JLCPCB's published ±10% finished tolerance (1.44–1.76 mm; FAB `finished_thickness_tolerance`) as a board-side fact that is not the component-fit basis. No special tolerance, TE confirmation, enclosure CAD or owner harness is needed for placement, routing or bare-board fab readiness. The normal footprint, finished-hole/pad, retention and solder-joint checks remain. *Historical context, not a gate:* superseded AS114 rev G p.6 §3.9.A ("shall be 1.57 mm") with its p.1 general ±0.13 mm reads as 1.44–1.70 mm. |
| Latch / CPA and tool access | **PARTIAL** | S3 p.13 Fig. 17: latch must be fastened for mating; the screwdriver slot lifts it for unmating. S3 p.7 §3.5.D: optional CPA, pre-staged before mating, fully engaged after, slid back to pre-staged before separation. S3 p.6 §3.5.B: a 4.8 mm blade opens the wedge lock (harness-side). S3 names no CPA part number; 2373965-1 appears only on the product-page print. |
| Harness exit direction | **PARTIAL** | Axial, out the rear wire seal, away from the mating face (2293782 E2 sheet 1 section; product print: exit angle 180°). On the pod this is +Y in the footprint frame, outward through the panel. S3 p.8 §3.5.E: an optional backshell acts as cable strain relief (no part number). Bend radius, routing and strain relief selection are open. |
| Installed enclosure fit | **UNRESOLVED** | Future design deliverable: the enclosure and panel are team-designed; the only external constraint is the seat cowl. Verified after design. Not a blocker for placement, routing or bare-board fab readiness. |
| Installed harness | **UNRESOLVED** | Future design deliverable: the harness is team-designed; the only external constraint is the seat cowl. Routing and bend radius are verified after design. Not a blocker for placement, routing or bare-board fab readiness. |
| Installed tool access | **UNRESOLVED** | No source for latch-slot or panel-screw tool lanes. |

## 2026-10-22 TE drop (AGENTEE-446)

The owner put the TE files in a drop folder (AGENTEE-451). Each was copied into its
own empty directory, never executed, and verified against the dispatcher's manifest.
`reg343.pdf` is a byte duplicate of the S3 file and the drop's K1 is byte-identical
to the existing capture. The zip was listed before extraction (one member, no
absolute or `..` path). Everything below is a TE fact with its page; none of it is
an owner statement. The record is `interface.json` `te_drop_2026_10_22`.

| Lead claim | Verdict | Where |
| --- | --- | --- |
| (a) S3 §3.6.A board 1.57 mm | VERIFIED | S3 p.9 |
| (b) S3 p.1 ±0.13 mm default, and whether it governs the thickness | PARTIAL: the note is verified; S3 does not say it governs §3.6.A, so that part stays UNVERIFIED | S3 p.1 |
| (c) S3 §2.3 customer drawing first | VERIFIED; S3 names no drawing or revision | S3 p.2 |
| (d) pp.11–13: panel 2–5 mm, screws/torque, latch access, backshell | PARTIAL: the first three are verified on pp.11–13; the backshell is on p.8 §3.5.E | S3 pp.8, 11–13 |
| (e) E5 sheet 1 Table 1: black 776164-1 mates right-angle 1-776163-1 | PARTIAL: verified in content, but in the unlabelled part table (Table 1 is the terminal table), and it names the 776163 family, not the dash number | E5 sheet 1 |

Board-side checks (nominal): the 35-position footprint
`../PodConnector.pretty/AMPSEAL_35_1-776163-1.kicad_mod` matches S3 Fig. 13a and the
K1 sheet 2 layout. That covers the Ø1.75 plated holes (S3: ±0.1 after plating), the
two Ø2.85 locators at Z = 57.0, the 4 mm pitch, the 2 mm row stagger, the 0.5 offset
and the 6.5 offset. S3 gives no board-lock, retention or solder-tail dimension. The
documents do not address U3 clearance or vibration mounting. The one concrete
source-to-source difference is the panel opening height (K1 24.2–25.2 against S3
24.8–25.2); K1 governs and no enclosure exists yet. Board thickness stays as
recorded in `pcb_thickness`: owner-accepted as relayed, not reopened.

### Notes for reviewers

- **REQUIREMENTS.md lines 43/58.** The candidate mate 776164-1 is confirmed by two
  TE drawings that agree. Those lines name the tin header 776163-1, but the
  selection is the gold 1-776163-1. Both are black, so both mate 776164-1. The
  finish deviation itself remains open in `POD-CD-HARNESS-CONNECTOR`.
- **Status of the 2293782 copy.** The E2 copy is the PCN redline, watermarked
  PRELIMINARY, and is kept unchanged as historical. Released E5 (22APR2026,
  captured 2026-10-22) carries the same identity and keying.
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
