# Design-rule decision D-PCB-1: fine-pitch pad clearance and thermal-via drills

**Decision (design owner's agent, 2026-10-20, under the owner's standing direction that
owner-reserved decisions are made autonomously and recorded):**

1. **Thermal vias under exposed pads are 0.30 mm drill / 0.70 mm diameter (0.20 mm ring), a deliberate choice above the via minimum.** The 44
   vias in U1 (ESP32-S3-WROOM-1, 12), U5 and U7 (LMR36520 DDA0008B, 8 each) and U6 and
   U12 (TPS7B4253 DDA0008J_C02, 8 each) were 0.20 / 0.40 mm: within JLCPCB via capability
   (0.15 / 0.25 mm minimum) but carrying the small-hole surcharge and violating the project's
   0.30 mm hole minimum. The project minimum hole
   of 0.30 mm is **kept**. The footprint sources are changed instead; patched copies are
   in `footprints/` (before/after hashes in `evidence/`).
2. **Pad-to-pad clearance inside the fine-pitch footprints U2, U16, U17, U18 and U19 is
   0.15 mm.** The general 0.20 mm clearance is **kept** for everything else, including
   between footprints and for tracks. The scope is expressed as six custom rules in
   `telemetry-pod.kicad_dru` (`A.memberOfFootprint` on both pads), not by lowering any
   board-setup constraint. The board-setup minimum clearance of the expanded project is
   already 0.0 mm; the 0.20 mm comes from the default net class and still applies.

**Owner authorization (2026-10-20, after the decision was recorded):** "relax the
clearance rules if you must, as long as JLCPCB can manufacture it, and it doesn't affect
electrical performance." Both conditions bound every rule change in this directory:
each relaxation must cite the JLCPCB published capability it stays within, and must
not touch spacing that carries an electrical function (creepage at higher-voltage
nets, RF, differential pairs, loop geometry). D-PCB-1 satisfies both: the 0.15 mm
gaps are manufacturer land patterns within JLCPCB spacing capability, and the thermal
vias are same-net copper under exposed pads.

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
  library convention; 0.70 mm diameter puts a 0.20 mm ring of thermal copper around each
  hole. Signal vias keep the net-class 0.60 / 0.30 mm; the board minimum is 0.50 mm
  diameter with a 0.10 mm ring, twice JLCPCB's published via minimum (0.25 / 0.15 mm). Via pitch is 1.30 mm (DDA)
  and 0.70 mm (ESP32): the DDA vias keep 0.60 mm copper gaps, the ESP32 vias become
  tangent same-net copper inside the exposed pad, and hole-to-hole gaps are 1.00 mm and
  0.40 mm against JLCPCB's 0.20 mm via hole-to-hole minimum.

Alternatives considered and rejected: lowering the board-setup minimums globally
(loses protection everywhere), re-selecting the IMU and supervisor parts (no
functional reason; the parts are accepted and purchased), and leaving 0.20 mm thermal
drills with a global 0.20 mm hole minimum (surcharge, weaker rule for the whole board).

## Layer count (D-PCB-2)

The expanded board is a 4-layer board on JLCPCB's standard JLC04161H-7628 1.6 mm stackup,
which is what the scaffold generated. It is kept as a cited engineering decision, not a
default: the eMMC U14 is a 153-ball 0.5 mm BGA that cannot fan out on two layers, the
LMR36520 layout guide asks for a middle-layer ground plane, and the GNSS 50-ohm line needs
a defined reference. "Double-sided" in the owner's target means components on both sides.
Trace figures in `constraints.json` are quoted for JLCPCB multilayer. The PTH annular-ring
figures (recommended 0.20 mm, absolute 0.15 mm) apply to component through-holes; vias
have their own published minimum of 0.25 mm on a 0.15 mm hole.

## Constraint provenance (the structural fix)

`constraints.json` classes every board-setup value for the expanded project as owner,
manufacturer, datasheet, engineering or default, with the JLCPCB figure or datasheet
locator beside each number. `board-setup.kicad_pro` is the diagnostic project file with
those values applied. The scaffold's 0.0 / 0.5 / 0.1 / 0.08 / 0.8 mm defaults are
recorded as superseded and must never gate again. Two consequences on the frozen board:
the five copper-edge findings on J2 disappear (the 0.50 mm edge rule was a default; JLCPCB
needs 0.20 mm and 0.30 mm is kept), and 22 silkscreen findings appear (text below the
1.0 mm / 0.15 mm legibility minimum, overlaps) that the lax defaults had hidden. Those are
real manufacturability findings for the silk relocation stage (AGENTEE-320), not copper.

## D-PCB-3: eMMC interior fanout (RETIRED 2026-10-21: eMMC dropped for a microSD socket)

**Retired.** The owner dropped the eMMC on 2026-10-21 (`../storage-microsd/`). The `BGA_EMMC`
net class, the U14 via-in-pad rule and the patched `Package_BGA` footprint are withdrawn;
what follows is the history of the decision and stays for the record.

The first KRT routing diagnostic on this board (`~/.cache/agent499-route-diag`, run
`cited-krt-norescue`) routed 142 of 194 nets and left every eMMC bus net open: U14 is a
0.5 mm-pitch BGA-153 with ten connected interior balls, and a 0.60 mm via cannot dogbone
between its balls. `constraints.json` records the history. The bounded routing experiment (D-PCB-3 v2,
`../routing-diagnostic/iteration-3/bga-exp/`) routed every EMMC_* net with 0.22 mm pads and
the `BGA_EMMC` class, but a B.Cu GND pour cannot reach the five interior GND balls.

**Decision v3 (autonomous under the owner's 2026-10-20 ruling; owner review after the
fact):** E7, G5, H10, J5 and K8 are filled-and-capped via-in-pad, 0.15 mm hole /
0.25 mm diameter, carried as through-hole pads by the patched footprint
`footprints/Package_BGA.pretty/LFBGA-153_11.5x13mm_Layout14x14_P0.5mm.kicad_mod`
(all pads 0.22 mm NSMD). `telemetry-pod.kicad_dru` scopes hole 0.15 / ring 0.05 mm to
U14's through-hole pads (JLCPCB 4-layer via minimum). Order form: via covering = epoxy
filled and capped. Evidence in `evidence/d-pcb-3-v3/`: the derived iteration-3 board
(`../placement-candidate/iteration-3/derived-d-pcb-3-silk/`) has 0 silk, 0 hole and 0
annular findings; its 6 clearance + 4 pth_inside_courtyard findings are the via-in-pad
sites under U1's pads 19-22 on the other side, which the next seed must avoid (the
patched footprint lets the packer's hole-conflict check enforce that). Reverse: restore
the stock footprint and delete the U14 rule.

## Decisions D-PCB-8 to D-PCB-11 (2026-10-21, autonomous, owner review after the fact)

- **D-PCB-8 silkscreen policy.** `silk/apply-silk-policy.py` hides the reference/value
  fields and moves to Fab the footprint silk graphics that KiCad's own DRC names in
  silk findings. Cosmetic only; JLCPCB assembles from the position file. On iteration 3
  it removed all 58 silk findings (29 references hidden, 12 graphics moved).
- **D-PCB-9 NEO-M9N.** U3 accepted as an exact 85 C exception on the owner's terms for
  U1/U2/U4 (AGENTEE-209: tested against its actual limit, thermal evidence required).
  NEO-M9L-01A has 0 stock and changes three pin functions.
- **D-PCB-10 J1.** Right-angle, fixed by the owner on 2026-10-21: the 35-position TE
  AMPSEAL 1-776163-1 already on every candidate. The vertical/right-angle question in
  AGENTEE-209 was about the superseded 23-position part and is closed.
- **D-PCB-11 layers.** Stay 4-layer. Go to 6 only if the block-placed routing campaign
  leaves +3V3 plane pads open or fails pour integrity on In2 (the via-fill trigger went
  with D-PCB-3).
- **D-PCB-16 antenna overhang (owner).** U1 stays with its antenna 6.46 mm past the top
  edge; the 3D-printed enclosure gets a non-metallic antenna pocket (≥ 20 × 8 mm, ~5 mm of
  air, nothing within the 15 mm keep-out, no support under the module).
- **D-PCB-15 EFUSE_SET net class: withdrawn.** A 0.15/0.15 mm class for the eFuse setting
  nets did not route them (placement-channel problem, not copper width); the class is gone.
- **D-PCB-14 SD bus length.** Up to 90 mm pad-to-pad at the 20 MHz SDR target (iteration 7
  places the socket in the far corner because the card lane no longer fits under U1); route
  the six SD nets as one matched bundle; higher SD clocks need the block moved next to U1.
- **D-PCB-13 v3 (owner): slot off the edge.** J3 fixed at (8.9, 32.0) B rot 90 with the
  mouth at the left edge; the card lane lies outside the outline (overhang band 20.3 mm).
- **D-PCB-13 J3 card envelope.** `footprints/Connector_Card.pretty` extends the socket's
  courtyard over the inserted card and its 15 mm insertion lane (to y=29.0 mm; v2 after the
  iteration-6 review found U4 in the lane) so packers and DRC keep the card path
  clear (iteration-5 review: TP2/TP5 were 0.06 mm from the card edge).
- **D-PCB-12 J3.** The microSD socket (−25 to +85 °C) is an 85 °C exception on the
  owner's U1/U2/U4 terms; no 105 °C socket is stocked with a library footprint.

Full text with reversal paths: `constraints.json` `decisions`.

## Evidence on the frozen diagnostic board

Native `kicad-cli pcb drc --severity-all` (KiCad 10.0.7) on the retained 17-group
candidate (board SHA256 `79cc1310…55f36`), with the same `.kicad_pro`/`.kicad_prl`:

| Variant | Violations | Clearance | Drill out of range | Unconnected |
| --- | ---: | ---: | ---: | ---: |
| baseline (no custom rules beyond RF_50) | 341 | 20 | 44 | 499 |
| + `telemetry-pod.kicad_dru` | 321 | 0 | 44 | 499 |
| + 0.30/0.60 mm thermal vias (first pass, ring too small) | 277 | 0 | 0 | 499 |
| cited board setup + rules + 0.30/0.70 mm vias (`evidence/cited-constraints-*`) | 294 | 0 | 0 | 499 |

`evidence/drc-comparison.json` records that the removed findings are exactly the 64
UUIDs (20 clearance, 44 drill) of the prior proposal, on U1, U2, U5, U6, U7, U12 and
U16–U19 only, and that no new finding appears in either step. The remaining 277 are the
pre-existing silk (73), copper-edge (5) and library-mismatch (199) findings, which are
unaffected by this decision and remain open. With the cited board setup the 294 are
199 library-mismatch, 86 silk and 8 silk-text findings; copper-edge is 0. The patched
candidate is retained only as DRC evidence (`cited-constraints-candidate.kicad_pcb.gz`);
it is not an adopted board.

## How this is applied and reversed

- The next expanded-board import or placement run must use `footprints/` in place of the
  three sources in `../released-source-migration/inputs/footprints/` and of
  `../storage-microsd/inputs/footprints/Connector_Card.pretty` (D-PCB-13), run
  `silk/apply-silk-policy.py` on the seed (D-PCB-8), carry
  `telemetry-pod.kicad_dru` as the project's rule file, and apply the board-setup values
  of `constraints.json` (as in `board-setup.kicad_pro`) to the generated project. Until the migration is
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

## RF width rule binding (AGENTEE-484r, agent-529 decision 39bfdc72)

AGENTEE-480 found that the project has only the Default net class and no RF_50 assignment, so
`agent_ee_netclass_RF_50` (track_width min 0.335 mm) never applied to /POD_GNSS_RF. The rule condition in
`telemetry-pod.kicad_dru` now also selects the net directly:
`A.NetClass == 'RF_50' || A.NetName == '/POD_GNSS_RF'`.
- The width is unchanged: 0.335 mm, inherited from the retained stackup calculation.
- No other rule or clearance changed.
- The F.Cu-over-In1 requirement is unchanged.

The selector is in this fome-mc source because the pipeline copies this file into the project byte for byte,
while `board-setup.kicad_pro` is rewritten by the agent-ee scaffold. A net-class assignment there would depend
on agent-ee preserving it.

`constraints.json` is not edited: its bytes are pinned by the J1 hand-fit chain. Its `custom_rules` entry keeps
the rule name and width; this section records the selector.

The binding enforces a minimum width. It does **not** prove 50-ohm impedance, which needs the fabricator stackup
and a reference-plane check (AGENTEE-480).

## RF rule: AGENTEE-186 adopted CAD nominal (agent-529 4cf9d43d v2)

`telemetry-pod.kicad_dru` keeps the 484r exact-net selector `A.NetName == '/POD_GNSS_RF'`.
- **Width:** min = opt = max = **0.293 mm**, replacing the 0.335 mm minimum. This is the CAD nominal lower/drawn width: the exact inverse W1 0.29286522460874 mm (W2 0.28016522460874 mm is taper metadata only), AGENT-selected and CONDITIONAL.
- **`agent_ee_RF_50_cpw_gap`:** clearance min **0.2032 mm** from other nets on F.Cu. This is the coplanar gap lower bound on both flanks. KiCad has no maximum-clearance constraint, so a gap above nominal is not a DRC finding; the measured two-flank gap belongs to the agent-ee `rf_geometry` cpw check.
- **`agent_ee_RF_50_launch_transition_REVIEW`:** an explicit exception SCOPE for segments intersecting the U3 or J2 courtyard. Its values equal nominal until a reviewed relaxation exists. It is never a net-wide waiver.
- **Basis:** Z 50.0087997251 ohm, eff Er 3.1696914377 at T1 0.04064 mm (JLC calculator 1.6 mil basis), H1 0.2104 mm, Er1 4.4, mask C1 1.2 / C2 0.6 mil, CEr 3.8, taper 0.5 mil (client config; the JLC guide's 0.7 mil is recorded as a difference, not merged). The guide is https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator (529-read).
  - The historical forward point is 47.394 ohm at 0.335 mm, T1 0.035 mm, with its own inputs. No width sensitivity is derived from the pair.
- **Not claimed:** no tolerance band and no impedance verification.
- **Unchanged:** calculator parameters stay distinct from the fab stackup; the board's layer thicknesses and its 1.6 mm thickness are unchanged.

## Plane plan island policy (AGENTEE-487)

The final policy is `island_removal: "always"` for both `/GND` (In1.Cu) and `/+3V3` (In2.Cu).

Checkpoint `e780472` had changed `/+3V3` to `never`. agent-529 rejected that (76150ac4), and it is reverted here.

The underlying defect was that the declared routing-turn `add-planes` producer refused a wholly unconnected `always` zone. Before routing, In2 `/+3V3` has no connection, because every `/+3V3` load is SMD. This is repaired in the producer:
- **Change:** agent-ee `add_planes` (AGENTEE-487 branch) keeps such a zone's definition and its `always` policy, and reports it as `deferred_connectivity`.
- **Obligation:** connected fill under `always` after routing.
- **Still refused:** partial isolation, missing nets and unplanned zones.

Evidence and the before/after regression are in `../agentee-487-planes/`.
