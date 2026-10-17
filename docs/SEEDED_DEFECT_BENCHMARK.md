# fome-mc seeded-defect benchmark: plan

Status: plan, 2026-10-17. Nothing here has been run. This is input to agent-ee's
seeded-defect benchmark (AGENTEE-21), not a second benchmark. Plane: AGENTEE-108.

fome-mc's review history (FOMEMC-1..20) is a record of defects that a generator or a
repair writer actually produced on a real board, and that a review actually caught.
This document turns those findings into defect classes that can be seeded into a
copy of fome-mc, names the agent-ee check that should detect each one, and says
whether KiCad's native ERC/DRC would see it at all (generator decision 5: tool
evidence gates adjudication, so the gap between "native checks pass" and "the board
is right" is what the benchmark has to measure).

## Relation to AGENTEE-21

AGENTEE-21 is merged into agent-ee `main` (`8f83399`, branch `impl/seeded-benchmark`).
Its design is in agent-ee `docs/seeded-benchmark.md` and its preregistration in
`benchmarks/seeded/expectations.json` (schema `agent-ee.seeded-benchmark/1`): five
public boards, 30 synthetic seeds, expectations committed before any run, a
checks-only runner in a pinned image with no network, and a report that keeps
misses, unsupported cases and unresolved control findings in the denominator.

This plan adopts that format and its rules unchanged:

- Each seed is a case with `board_id`, `category`, `mutation` (operation, before,
  after, what is preserved), `source_selectors` (reference, symbol UUID, footprint
  UUID), `expected_checks` (check kind, predicate or target locator,
  `"certainty": "preregistered prediction; not an observed result"`) and `truth`
  (classification and engineering mechanism, with sources).
- Expectations are committed before the first run; corrections are new commits.
- Credit rules stay as written: a `hardware_interface` hit needs the exact invariant
  to fail with the paired control satisfied; a `drc` hit needs a new native record at
  the target UUID. Pre-existing violations at the target stay unresolved.
- Model reviews stay out of the deterministic report.

What fome-mc adds that the five public boards do not:

1. A hierarchical, multi-instance design (21 sheet instances from 15 files). The
   harness currently refuses hierarchy (`benchmark.py`: "hierarchy/buses not
   structurally supported", "hierarchical mutation unsupported").
2. Defect classes that are not in the current corpus: part-identity mismatches
   (LCSC number, voltage rating, package), rule relaxation that hides findings,
   HV clearance, missing thermal copper, decoupling distance, fab-file drift, and
   claims in documentation that the design does not support.
3. Real review findings as ground truth, with the review that found them on record
   in Plane.

## Preconditions

- **Control commit.** At `c582b29` several findings are still present (FOMEMC-17..20
  are in flight), so `c582b29` is not a clean control for those classes. Use the
  first commit after FOMEMC-17..20 land as the control, and keep `c582b29` as a
  real-defect fixture for AGENTEE-68 (its open findings are real, not seeded).
- **Hierarchy.** Either extend the harness to address a symbol by sheet-instance
  path (agent-ee's `hardware_interface` already does), or seed standalone block
  copies produced by the rung-2 capture (`docs/BLOCK_LIBRARY.md`, AGENTEE-106 and
  AGENTEE-107). The second route needs no harness change for seeds that live inside
  one block.
- **Licences.** fome-mc is the owner's repository but has no licence file, and its
  Polygonus-derived sheets come from checkouts with no licence file. Keep seeded
  copies scratch-only, as AGENTEE-21 already does, until the owner decides.
- **Libraries.** Project-local footprints are in `libs/`; shared ones resolve through
  `~/git/kicad-libraries` at `ab9c5f8`. The dependency inventory must hash both.

## New mutation operations needed

The current operations are `replace_exact_value_properties`,
`delete_exact_schematic_wire`, `swap_wire_pin_endpoints`,
`replace_embedded_physical_footprint`, `remove_fuse_and_bridge` and
`remove_shunt_esd`. The catalogue below also needs:

| Operation | Edits | Used by |
|---|---|---|
| `replace_exact_field` | one symbol field other than Value (`LCSC`, `Description`, `PN`) in schematic and PCB | F07, F17, F23 |
| `set_assembly_state` | add or remove `(dnp yes)` / `exclude_from_bom` | F08, F24 |
| `remove_component` | delete one symbol and its footprint, keep the remaining connectivity partition | F06, F15, F27 |
| `project_rule_edit` | one key in `.kicad_pro` design rules or net classes | F12, F19 |
| `pcb_track_width` | set the width of the segments of one net | F13, F20 |
| `pcb_move_footprint` | move one footprint, leave its tracks | F28 |
| `pcb_delete_zone` | delete one zone by UUID | F21 |
| `fab_file_edit` | change one row of the CPL or BOM | F22 |

## Catalogue

"Native" says whether `kicad-cli sch erc` or `kicad-cli pcb drc --schematic-parity`
(agent-ee kinds `erc`, `drc`) would report the seeded defect on its own. Check ids
in the detection column are agent-ee check kinds that exist today (`erc`, `drc`,
`netlist`, `hardware_interface`, `geometry`, `rc_transient`) or Plane items for
planned checks; a seed whose only detector is planned is preregistered as
`unsupported` until that check exists.

| ID | From | Defect, in behavioural terms | Where | Detection (existing / planned) | Seed (in a copy) | Expected finding | Native? |
|---|---|---|---|---|---|---|---|
| F01 | FOMEMC-5 (CIR-002) | Symbol pin map does not match the part: motor outputs land on supply and sense pins, the driver never drives the winding | U202 DRV8825, `stepper_etb` | `hardware_interface` `named_net` (U202 pin 5 on `/STEP_1A`); AGENTEE-35, AGENTEE-36, AGENTEE-59 | `swap_wire_pin_endpoints` between U202 pin 5 (AOUT1) and pin 4 (VMA) | `named_net` fails for U202.5; AGENTEE-59 must-connect | No: both pins stay connected |
| F02 | FOMEMC-5 | Required pin left floating: nSLEEP not tied, part stays asleep | U202 pin 17 | `erc`; AGENTEE-59 | `delete_exact_schematic_wire` on U202 pin 17 | ERC `pin_not_connected` at U202.17 | Yes, if the pin type is input |
| F03 | FOMEMC-5 | Current-limit set point wrong: I = VREF / (5 × Rsense) misses the 0.75 A target | R213, R214, R215, R216 | `hardware_interface` `value`; AGENTEE-61 (interval check of declared assertion) | `replace_exact_value_properties` R213 `200m` to `330m` | `value` fails on R213; AGENTEE-61 computes 0.46 A | No |
| F04 | FOMEMC-6 (CIR-003) | VR sensor wired single-ended with the minus side shorted to ground at the connector | `/VR1-`, U13, `triggers` | `hardware_interface` `different_net` (`/VR1-` vs GND); AGENTEE-60 | `swap_wire_pin_endpoints` so U13 IN- joins GND | `different_net` fails | No |
| F05 | FOMEMC-7 (CIR-005) | TVS clamp above the absolute maximum of downstream drivers (53 V clamp vs 40 V TLE9201) | D1, `psu` | `hardware_interface` `value`; AGENTEE-61 with AGENTEE-18 datasheet facts | `replace_exact_value_properties` + `replace_exact_field` D1 `SMCJ24A` to `SMCJ33A` | AGENTEE-61 clamp 53.3 V > 40 V | No |
| F06 | FOMEMC-8 (CIR-006) | Open-drain bus without pull-ups (SD CMD/DAT) | R127..R131, `mcu` | AGENTEE-59 (must-have pull-up), AGENTEE-60 | `remove_component` R127 | AGENTEE-59 missing pull-up on SD_CMD | No |
| F07 | FOMEMC-8 (CIR-007f) | Supplier part number names a different package than the footprint | D16 SOD-123 | AGENTEE-30, AGENTEE-29 | `replace_exact_field` D16 `LCSC` to the SMA B340A number | AGENTEE-30 package mismatch | No |
| F08 | FOMEMC-8 (CIR-007g) | Part meant to be unpopulated is assembled (or the reverse) | U24 | `hardware_interface` `component` (`populated: false`); AGENTEE-73 | `set_assembly_state` remove `dnp` on U24 | `component` fails | No |
| F09 | FOMEMC-2, FOMEMC-8 | Pin map in `io-map.csv` disagrees with the schematic; one MCU pin carries two functions | `io-map.csv`, U26 | `hardware_interface` contract generated from `io-map.csv` (FOMEMC-22); project `verify_io_map.py` | `swap_wire_pin_endpoints` WBO1_NRST and SPI4 SCK at U26 | `named_net` fails on U26 PE2 | No |
| F10 | FOMEMC-9 (CIR-001) | Board and schematic out of sync: stale footprint, missing footprint, pad on wrong net | PCB | `drc` (parity) | delete one footprint from the PCB copy | `schematic_parity` missing footprint | Yes |
| F11 | FOMEMC-10 | Net left unrouted | PCB | `drc` | delete one track segment | `unconnected_items` | Yes |
| F12 | FOMEMC-11 | Design rule relaxed so DRC passes: `min_resolved_spokes` 2 to 1 hides single-spoke thermals | `.kicad_pro` | AGENTEE-63, AGENTEE-75 (rules compared to a pinned profile, not the candidate's own); `kicad-route audit` | `project_rule_edit` `min_resolved_spokes` = 1 on a board with a single-spoke GND pad | rule-drift finding | No: DRC grades with the relaxed rule |
| F13 | FOMEMC-12 | Tracks at the fab minimum (0.127 mm) on nets whose class asks 0.254 mm; no teardrops | signal nets | `geometry` with `copper-width/1`; AGENTEE-76 | `pcb_track_width` one signal net to 0.127 mm | copper-width defect on that net | No: 0.127 is the DRC minimum |
| F14 | FOMEMC-13 (circuit-001) | 3.3 V logic drives an input whose high threshold is 3.5 V | U1003 bypass, VNLD5090 IN | AGENTEE-59 (voltage compatibility); kicad-happy VM-001 (AGENTEE-17, noisy) | `swap_wire_pin_endpoints` so RN6 is fed from U26 instead of U1003 | AGENTEE-59 V_OH 3.3 V < V_IH 3.5 V | No |
| F15 | FOMEMC-14 (circuit-002) | Resistive sensor input without its excitation pull-up | R219, `/AV6` | `hardware_interface` `component`; AGENTEE-60; AGENTEE-61 (ladder voltages) | `remove_component` R219 | `component` fails | No |
| F16 | FOMEMC-14 (circuit-004) | Pull-up on the wrong output (dash line instead of tach) | R212, `/LS8` vs `/LS14` | `hardware_interface` `same_net` (R212.2 with J1-13) | `swap_wire_pin_endpoints` R212 between `/LS8` and `/LS14` | `same_net` fails | No |
| F17 | FOMEMC-15 (circuit-003) | Value and supplier part disagree (10 µF symbol bound to a 100 nF part) | C12 | AGENTEE-29 with AGENTEE-27 catalog parameters | `replace_exact_field` C12 `LCSC` to `C161115` | catalog capacitance 100 nF ≠ 10 µF | No |
| F18 | FOMEMC-15 (check/erc) | Power input with no driver on the net | `triggers` 5V_SENSOR_SUPPLY | `erc` | delete the PWR_FLAG wire | ERC `power_pin_not_driven` | Yes |
| F19 | FOMEMC-16, FOMEMC-19 | HV copper (400 V coil flyback) at the default 0.1524 mm clearance | `/IGN1..4_COIL` | AGENTEE-47, AGENTEE-63 (HV netclass compiled to DRC rules) | `project_rule_edit` remove the HV class assignment | missing-requirement finding on `/IGN1_COIL` | No: DRC only knows the default class |
| F20 | FOMEMC-16 (physical-003) | Coil conductor too narrow for its current | `/IGN3_COIL` | `geometry` `copper-width/1` with a per-net limit; AGENTEE-13 | `pcb_track_width` `/IGN3_COIL` 1.2 to 0.254 mm | copper-width defect | No |
| F21 | FOMEMC-16 (physical-004) | Power device without its heat-spreading copper | Q301 drain zone | geometry probe zone facts; new check (thermal copper area per declared device) under AGENTEE-83 | `pcb_delete_zone` on `/WBO1_H-` F.Cu | zone missing for Q301.2 | No |
| F22 | FOMEMC-16 (physical-001) | Placement file disagrees with the board | `export/CPL-fome-mc.csv` | AGENTEE-73, AGENTEE-72 | `fab_file_edit` shift one CPL row by 1 mm | CPL/board position mismatch | No |
| F23 | FOMEMC-17 (c4-overvoltage) | Capacitor voltage rating below the rail's clamp voltage | C4 on `/12V_PROT` | AGENTEE-61 with AGENTEE-27 ratings | `replace_exact_field` C4 to a 16 V part | rating 16 V < 38.9 V | No |
| F24 | FOMEMC-17 (injector-clamp) | External freewheel diode defeats the driver's fast active clamp | D201..D204 | `hardware_interface` `component` (`populated: false`); AGENTEE-67 | `set_assembly_state` populate D201 | `component` fails | No |
| F25 | FOMEMC-17 (brownout-margin) | Operating range claimed from a typical threshold instead of the guaranteed minimum | DESIGN.md §6.3.3, U3 | AGENTEE-18 datasheet fact plus AGENTEE-61 | requirement text cites 3.6 V typical UVLO as the floor | assertion fails against 4.3 V minimum VIN | No |
| F26 | FOMEMC-18 (physical-001) | Land pattern does not match the datasheet drawing | U29 footprint | AGENTEE-31, AGENTEE-38 | `replace_embedded_physical_footprint` U29 with a wrong-pitch pattern | land-pattern IoU below threshold | No, unless the library copy differs |
| F27 | FOMEMC-18 (physical-002) | Required bypass capacitors missing on a module supply pin | U29 pin 24 | AGENTEE-59 (decoupling presence) | `remove_component` of the pin-24 capacitor once FOMEMC-18 adds it | AGENTEE-59 missing decoupling | No |
| F28 | FOMEMC-19 (physical-004) | Decoupling placed too far from the supply pin | U25 pin 4 | AGENTEE-53 (decoupling distance) | `pcb_move_footprint` the U25 bypass capacitor by 10 mm | distance > 2 mm | No |
| F29 | FOMEMC-20 | Label and wiring hygiene: isolated pin label, dangling wire, two names on one net | any sheet | `erc` | `delete_exact_schematic_wire` leaving a label isolated | ERC `isolated_pin_label` (warning) | Yes, as warning |
| F30 | FOMEMC-11 | Single-spoke thermal on a ground pad | GND pads | `drc` with the unrelaxed rule | delete the stitching via next to one pad | `starved_thermal` (warning) | Yes, if the rule is not relaxed |
| F31 | FOMEMC-13..17 docs | Documentation claims a fix that the design files do not contain (for example DESIGN.md naming C12 `C3092605` while the BOM has `C96446`) | DESIGN.md, CHANGELOG.md | reviewer packet with the claim as a requirement and a `hardware_interface` `value` invariant; adjudication gated on tool evidence | edit a doc claim only | `value` invariant fails against the claim | No |

FOMEMC-1, -3 and -4 are feature changes, not defects, and give no seed. FOMEMC-2's
pin remap gives F09.

## Real defects at `c582b29` (not seeds)

Found while preparing this plan, from the committed BOM, CPL and regenerated
netlist. They belong in the AGENTEE-68 real-defect fixture with these expected
findings, and in FOMEMC-24 for repair:

- One LCSC number, `C22787`, is bound to two values: R7, R8 (10 Ω) and R9, R10,
  R101, R102 (120 Ω). At most one binding is right. Detector: AGENTEE-29 with
  AGENTEE-27.
- The BOM lists C1 and C6 (47 µF, `C454346`) but the CPL has no rows for them, so
  JLCPCB would not place them. Detector: AGENTEE-73.
- Nine BOM lines have no LCSC number (BT1, J8, J9, J11..J16, JP1, JP2) and are not
  marked DNP. Detector: AGENTEE-29 (assembly intent).

## Count and coverage

31 classes. Native ERC/DRC alone would report 6 (F02, F10, F11, F18, F29, F30), two
of them only as warnings. The other 25 need a contract, catalog data, datasheet facts,
geometry criteria or fab-file checks; for 13 of them (F06, F07, F12, F14, F17, F19,
F21..F23, F25..F28) every named detector is still a Plane item.
Preregistering them now, with `unsupported` as the honest expected execution
for planned checks, gives each planned check a fixed target before it is built.

Suggested first batch for AGENTEE-21: seeds that use only existing mutation
operations and the check kinds the harness already scores (`hardware_interface`,
`drc`): F01, F03, F04, F05 (value only), F16, F26. Six seeds, each confined to one sheet,
so they work on a flat block copy before the harness supports hierarchy. F15 and F24
follow once `remove_component` and `set_assembly_state` exist.
