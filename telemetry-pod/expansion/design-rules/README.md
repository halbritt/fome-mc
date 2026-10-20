# Design-rule decision D-PCB-1: fine-pitch pad clearance and thermal-via drills

**Decision (design owner's agent, 2026-10-20, under the owner's standing direction that
owner-reserved decisions are made autonomously and recorded):**

1. **Thermal vias under exposed pads are 0.30 mm drill / 0.60 mm diameter.** The 44
   vias in U1 (ESP32-S3-WROOM-1, 12), U5 and U7 (LMR36520 DDA0008B, 8 each) and U6 and
   U12 (TPS7B4253 DDA0008J_C02, 8 each) were 0.20 / 0.40 mm. The project minimum hole
   of 0.30 mm is **kept**. The footprint sources are changed instead; patched copies are
   in `footprints/` (before/after hashes in `evidence/`).
2. **Pad-to-pad clearance inside the fine-pitch footprints U2, U16, U17, U18 and U19 is
   0.15 mm.** The general 0.20 mm clearance is **kept** for everything else, including
   between footprints and for tracks. The scope is expressed as six custom rules in
   `telemetry-pod.kicad_dru` (`A.memberOfFootprint` on both pads), not by lowering any
   board-setup constraint. The board-setup minimum clearance of the expanded project is
   already 0.0 mm; the 0.20 mm comes from the default net class and still applies.

## Why

- The restrictive values are agent-ee scaffold defaults on the generated expanded
  project (0.20 mm net-class clearance, 0.30 mm minimum hole, 0.50 mm via, 0.50 mm edge).
  They are not the owner's committed pilot rules, which allow 0.09 mm clearance and
  0.15 mm holes. There is no owner-stated 0.20 / 0.30 requirement being relaxed.
- The 0.15 mm (TPS3890 DSE0006A) and 0.175 mm (LSM6DSO32 LGA-14) gaps are the
  manufacturer land patterns at 0.5 mm pitch, documented in the retained source review
  (`~/.cache/agent491-pad-clearance-source-review/`, TI drawing 4220552/B p.25; ST
  datasheet p.149 Fig. 22 with TN0018 Rev 8 §3.7). JLCPCB's published capability
  (read 2026-10-20) supports pad spacing below 0.15 mm on 1 oz outer copper. Shrinking
  the copper to reach 0.20 mm would depart from the manufacturer pattern for no
  manufacturing benefit.
- 0.20 mm drills carry a small-hole surcharge at JLCPCB and offer no thermal advantage
  here; 0.30 mm is the ordinary thermal-via drill in TI PowerPAD guidance and the KiCad
  library convention. Via pitch is 1.30 mm (DDA) and 0.70 mm (ESP32), so 0.60 mm pads
  leave 0.70 mm and 0.10 mm copper gaps and 1.00 mm and 0.40 mm hole-to-hole gaps, all
  within the unchanged 0.25 mm hole-to-hole minimum and on the same net.

Alternatives considered and rejected: lowering the board-setup minimums globally
(loses protection everywhere), re-selecting the IMU and supervisor parts (no
functional reason; the parts are accepted and purchased), and leaving 0.20 mm thermal
drills with a global 0.20 mm hole minimum (surcharge, weaker rule for the whole board).

## Evidence on the frozen diagnostic board

Native `kicad-cli pcb drc --severity-all` (KiCad 10.0.7) on the retained 17-group
candidate (board SHA256 `79cc1310…55f36`), with the same `.kicad_pro`/`.kicad_prl`:

| Variant | Violations | Clearance | Drill out of range | Unconnected |
| --- | ---: | ---: | ---: | ---: |
| baseline (no custom rules beyond RF_50) | 341 | 20 | 44 | 499 |
| + `telemetry-pod.kicad_dru` | 321 | 0 | 44 | 499 |
| + 0.30 mm thermal vias | 277 | 0 | 0 | 499 |

`evidence/drc-comparison.json` records that the removed findings are exactly the 64
UUIDs (20 clearance, 44 drill) of the prior proposal, on U1, U2, U5, U6, U7, U12 and
U16–U19 only, and that no new finding appears in either step. The remaining 277 are the
pre-existing silk (73), copper-edge (5) and library-mismatch (199) findings, which are
unaffected by this decision and remain open. The patched candidate is retained only as
DRC evidence (`rules-and-vias-candidate.kicad_pcb.gz`); it is not an adopted board.

## How this is applied and reversed

- The next expanded-board import or placement run must use `footprints/` in place of the
  three sources in `../released-source-migration/inputs/footprints/` and must carry
  `telemetry-pod.kicad_dru` as the project's rule file. Until the migration is
  re-sealed with these sources, every candidate board must be checked with this rule
  file and the enlarged vias, as above.
- To reverse: delete this directory's `.kicad_dru` rules and restore the three
  footprint hashes in `evidence/footprint-sources-before.txt`. The owner may also
  tighten the 0.15 mm value or the via size by editing those files; the DRC above is
  the acceptance test to re-run.

Not resolved here (unchanged holds): J2 edge clearance and seating, the 17 cross-side
shorts and 14 clearances of earlier reports (addressed by the AGENTEE-318 reservation),
mask and silk findings, via-in-pad assembly process (tenting or plugging of the 0.30 mm
vias under the exposed pads must be specified with the fabricator), thermal validation,
and final DFM review.
