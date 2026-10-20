# Expanded pod requirement capture

This is the Revision 3 input inventory for the expanded-pod campaign. It captures
`../../REQUIREMENTS.md` directly, without rewriting or omitting its paragraphs.
It does not replace the historical Revision 2 fixture in agent-ee and does not
establish design acceptance.

The capture contains **58 requirements and 20 prose entries**: 29 table rows,
18 bullets and 11 numbered acceptance criteria. Prose must also be mapped: it
contains obligations such as thermal validation and power-disturbance testing.
The revision comparison finds 30 added entries, 13 changed entries, no removed
entries and 35 byte-identical entries. Unchanged text does not transfer old
candidate evidence to the expanded assembly.

`spec-record.json` and its receipt were produced by agent-ee's existing
`spec_record` module at commit `4df4c9da263065d495cb2f59d9c3075a28f997ef`.
The receipt records the parser hash, arguments and specification identity.
`revision-delta.json` compares exact entry text against that commit's Revision 2
fixture and includes both texts for changed entries. Its source commit is the
fome-mc revision from which these requirement bytes were captured.

From the fome-mc root, with that agent-ee checkout available:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 -m agent_ee.spec_record verify \
  telemetry-pod/expansion/requirements/spec-record.json telemetry-pod/REQUIREMENTS.md
```

For reproduction, use `python3 -m agent_ee.spec_record capture` with the codes
and arguments in `spec-record.receipt.json`, writing to a fresh output path.
The existing files must not be overwritten by the capture command.

## Acceptance evidence still required

This table is a campaign work inventory. `requirement-map.json` now accounts
for all 78 entries and `compiled/` retains the compiler output. Only AC-3 has
executable predicates (native ERC/DRC); the other obligations are explicit
limitations or bench requirements. No criterion is claimed complete by capture
or compilation. Unchanged IDs do not transfer old candidate evidence.

| Criterion | Evidence required for the expanded candidate | Current boundary |
| --- | --- | --- |
| AC-1 | Complete interface contract, connector/MCU/external destinations, native schematic verification and interface-specific evidence | `../interface-contract` checks 35 connector cavities and 15 expansion GPIOs; full processor/peripheral and firmware coverage remains open. |
| AC-2 | Exact selected parts against each decision, with supported deviations | Native bindings exist; reconcile gold J1 `1-776163-1` against the spec's mechanical candidate `776163-1`, and qualify the full selection. |
| AC-3 | Native ERC and routed-board DRC with zero errors and zero unwaived warnings, bound to the same candidate | Series-divider schematic has retained ERC evidence; expanded board placement/routing and DRC remain open. |
| AC-4 | Offline schematic, PCB, cross-analysis and EMC results, with warning dispositions | Full expanded-board analysis remains open. Native ERC alone does not satisfy this criterion. |
| AC-5 | Generation-day raw JLC stock responses, hashes and UTC times for assembly lines; explicit hand-fit exclusions and purchase-source deviations | Captured component identities are not a generation-day stock or assembly qualification. Gold J1 stock/hand-fit disposition remains open. |
| AC-6 | Sealed Gerbers, drills, BOM and CPL; package-bound DFM report and placement-preview dispositions | Manufacturing outputs remain open. The required owner upload and preview cannot be replaced by local geometry checks; this packet authorizes neither upload nor ordering. |
| AC-7 | Board/enclosure fit, holes, IMU silk axes and datasheet antenna keepout | 90 × 65 mm is a layout target; enclosure clearance, harness fit and expanded placement are unqualified. |
| AC-8 | Built-board ECU CAN capture with all stated frame rates within 5%, plus ECU .mlg contents | Firmware and bench evidence missing. |
| AC-9 | Built-board RaceChrono pairing and simultaneous ECU RPM, lean and 25 Hz GPS display | Firmware and installed-radio evidence missing. |
| AC-10 | Eight-channel range/accuracy/acquisition evidence during concurrent wheel, IMU/GNSS, CAN, BLE and logging operation; wheel speed and fault tests | Circuit analysis has unresolved findings; selected wheel sensor/tone geometry and physical tests remain open. |
| AC-11 | Declared standalone workload/duration, interrupted-power/full-media integrity tests, and tire-interface harness/zone verification | Eight hours is a soft target. Storage provision alone does not establish duration, recovery or sensor compatibility. |

## Mapping constraints

- The new wheel, tire and logging interface rows require explicit mappings.
  CAN tire provision is not proof of compatibility with an arbitrary sensor.
- The six power-integrity bullets and their prose include physical evidence.
  Keep simulated, injected and on-bike disturbances distinct. The reported
  SV650 behavior near 2,500 rpm is still an unmeasured investigation lead.
- Carry the exact three temperature exemptions and the unresolved own-rating,
  exact-part and enclosure-thermal obligations from
  `../temperature-scope-fragment.json`. Exemption from a blanket predicate does
  not qualify operation at the manufacturer's limit.
- The six pre-layout decision bullets require closure evidence, even where
  candidate implementation choices already exist. A generated circuit is not
  evidence that all its design choices were resolved or qualified.
- The source's statement that AC-1 through AC-7 are checked on files does not
  remove AC-6's explicit external DFM and owner-preview requirements.
- This capture preserves the specification's wording. Mechanical, electrical
  and parts deviations belong in the subsequent map and evidence, not in a
  silent rewrite of the requirement source.

## Compiled map

The map was compiled with agent-ee `4df4c9da263065d495cb2f59d9c3075a28f997ef`.
It declares all 58 requirement IDs and all 20 prose IDs, including built-board
AC-8 through AC-11 and the separate on-bike power waveform obligation. The
verification-stage subject lists the 333 references in the current series-divider
intent. It is not the old fixture's single-U1 subject.

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 -m agent_ee.requirement_scope \
  telemetry-pod/expansion/requirements/requirement-map.json \
  --spec-record telemetry-pod/expansion/requirements/spec-record.json \
  --spec telemetry-pod/REQUIREMENTS.md --out /path/to/fresh-output
```

The compiled scope expects a future expanded native project at
`scaffold/project`, relative to its output directory. This directory is not
supplied here: a routed expanded PCB does not yet exist. Compilation without
`--inputs` validates declarations and their baseline, and does not run ERC/DRC,
prove schematic/PCB parity, or capture a candidate. Do not populate that path
with the historical v9 pilot to obtain a passing result.

This is a verification-stage preparation scope. The full campaign still needs
parts, schematic, placement, routing and manufacturing stage declarations,
complete captured contracts, and supported predicates/evidence to replace
limitations when justified. In particular, the temperature exceptions are
cited and their limits retained, but no assembly predicate is declared or
exempted by this map. The canonical exemption input and assembly parameters
must be integrated together when that predicate is added.

`compiled/receipt.json` records all dispositions, tool identities and baseline
hashes. `map-negative-controls.json` retains rejection of missing AC-10,
missing on-bike power prose, and a stale specification-record hash. These
refusals test accounting boundaries; they do not validate the circuit.
