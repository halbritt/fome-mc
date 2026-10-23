# Revision 3 campaign scope on the microSD source (AGENTEE-197, AGENTEE-310)

This directory recompiles the Revision 3 requirement scope against the current
microSD source (`../../storage-microsd/`). It supersedes `../compiled/` for campaign use.
The earlier capture in `..` was compiled for a verification-only preparation and is now
stale in five ways:

- `stages.order` was `[verification]`, which `pod_driver.validate_configuration` refuses;
- it declared no review profile, so the RF gate reported "the review profile declares no rf reviewer";
- its stage subject listed 333 references from the eMMC schematic;
- its temperature limitations still described U1/U2/U4 as excluded from the operating-temperature predicate;
- its spec record no longer verifies, because `REQUIREMENTS.md` gained the Storage decision row (`POD-CD-STORAGE`) in b6ba9a0.

Nothing here places, routes or accepts a board. No campaign, reviewer, router or
placer ran. Compilation and the configuration probe are preparation evidence only.

## Files

| File | Producer | Content |
| --- | --- | --- |
| `spec-record.json`, `spec-record.receipt.json` | `agent_ee.spec_record capture` (agent-ee `1da2763`, same arguments as `../spec-record.receipt.json`) | 59 requirements and 20 prose entries; all 11 acceptance criteria |
| `revision-delta.json` | comparison with `../spec-record.json` (`make_revision_delta.py`) | One entry added (`POD-CD-STORAGE`), one changed (`POD-ME-1`, accepted height-estimate correction, AGENTEE-488c), none removed |
| `requirement-map.json` | authored, derived from `../requirement-map.json` | Scope template and dispositions (below) |
| `datasheet-ratings.json` | authored | Datasheet citations for parts rated below 105 °C |
| `temperature_ratings.py`, `temperature-ratings.json` | script and its output | Rating inventory of all 309 references from captured catalog records |
| `probe_configuration.py` | script | Runs `pod_driver.validate_configuration` on a compiled scope |
| `placement_subjects.py` | script | Checks the placement subject and `POD-ME-HOLES` against the schematic and `envelope.json` |
| `compiled/` | `agent_ee.requirement_scope` (agent-ee `ce12718`; compiler modules unchanged since `1da2763`) | `scope.json`, `receipt.json`, `requirements-map/` |

## What changed in the map

- **Stages.** The order is `schematic, placement, routing, verification`, and `finding_retry_limit` is 2.
  Fab stays out of the order until AGENTEE-146-compatible pod step wiring exists. Subjects: the schematic
  and verification stages list symbols, placement lists footprints, and routing requires at least one track.
  The references are the 309 (305 before the AGENTEE-484 decoupling repair) that `agent_ee.stages.native_references` reads from the current microSD
  schematic (sha256 `4da27afc…`). The placement subject also expects the four board-only corner holes
  H1–H4 from `../../placement-inputs/envelope.json` (sha256 `ad0a3597…`), so it lists 309 footprints.
  `POD-ME-HOLES` states each hole's declared position and drill: 3.2 mm NPTH at (4, 4), (86, 4),
  (86, 61) and (4, 61) mm, tolerance 0. The stage subject witness only reports expected references
  that are missing, so it catches an absent hole but cannot check where a hole is or its drill. That
  binding is agent-ee's `board_envelope` `mounting-holes/1` check, and the compiler refuses the
  envelope declaration it needs ("envelope references a fab profile; declare its captured path"). It
  stays NOT CHECKED. The envelope's hole values are a candidate declaration (the generator picks drill,
  inset and coordinates), not owner or manufacturer limits, so they do not gate acceptance until
  sourced. Project files are named `telemetry-pod.*`, as in the storage source.
- **Checks.** Each stage needs a check. POD-AC-3 maps to `erc` and `netlist` (schematic),
  `placement-drc` (DRC with `projection: placement-stage/1`) and routed `drc` (routing). POD-AC-6 maps to
  `netlist`, `routing-geometry` (copper facts only) and `fab-package` (verification, the
  `generation` done check). There is no numeric width gate, because no pod-wide minimum has a cited
  source here; native DRC grades the net-class widths. POD-AC-6's owner DFM upload and PREVIEW_REQUIRED
  confirmation remain an explicit limitation.
- **Review profile.** The scope embeds agent-ee's existing `profiles/pod-review.json`
  (`pod-rf-review-v1`: circuit, physical and rf reviewers plus an adjudicator) unchanged. No new provider
  route is introduced. A declared rf reviewer is not an RF review result.
- **Temperature.** No part is exempted. Three obligations stay separate: the 105 °C selection
  criterion (`POD-TEMP-SELECTION`), each part's exact limit (`POD-TEMP-ACTUAL-LIMITS`), and the 85 °C
  board ambient plus self-heating (`POD-TEMP-ENCLOSURE`). `POD-TEMP-AUTHORITY` records who retained each part:

  | Ref | Part | Rating | Citation | Retention authority |
  | --- | --- | --- | --- | --- |
  | U1 | ESP32-S3-WROOM-1-N8 | −40 to 85 °C ambient | datasheet `27d71971…` p. 27 | owner, acceptances line 1 |
  | U2 | LSM6DSO32TR | −40 to 85 °C | datasheet `d1776336…` p. 26 | owner, acceptances line 2 |
  | U3 | NEO-M9N-00B | −40 to 85 °C | datasheet `e21b35c1…` p. 11 (bytes not in this repository) | delegated engineering, D-PCB-9 |
  | U4 | MCP3208-BI/SL | −40 to 85 °C ambient | datasheet `89bc1e17…` p. 37 | owner, acceptances line 3 |
  | J3 | DM3AT-SF-PEJM5 | −25 to 85 °C | LCSC catalog record only; manufacturer rating not captured | delegated engineering, D-PCB-12 |

  Owner acceptance lines are in `../operating-temperature-acceptances.txt` (sha256 `7ca91bc7…`). D-PCB-9
  and D-PCB-12 (`../../design-rules/constraints.json`, sha256 `e7e095b3…`) record delegated engineering
  acceptance under the AGENTS.md autonomous-decision rule, on the owner's U1/U2/U4 terms: actual limit, plus
  thermal evidence. The owner reviews them after the fact. They are not owner acceptance lines. The AGENTEE-310
  `reduced_acceptance` contract can only cite a canonical line of that owner file, and it has no form for
  delegated authority. So the executable provenance for U3 and J3 is unresolved, and no line is written for
  them. D-PCB-12's "passive contact set, no self-heating" basis is an assumption that needs review. Actual
  thermal qualification is pending for all five parts. Missing thermal evidence is unknown, never pass.
  `POD-TEMP-UNRATED` keeps the 117 bound parts with no captured rating, and the 11 unbound JP/TP references,
  explicitly unknown. The old exemption file is cited only as superseded provenance.

Every other disposition, including the BENCH REQUIRED rows for POD-AC-8 to AC-11, is carried
unchanged from `../requirement-map.json`.

## Reproduce

From the fome-mc root, using an agent-ee checkout at `ce1271858e6fc086bb3c14dfcf7946439cff50dc` (the scope compiler, spec record, stages and pod driver modules are byte-identical to `1da2763`):

```sh
D=telemetry-pod/expansion/requirements/rev3-microsd
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$AGENT_EE/src python3 -m agent_ee.spec_record verify $D/spec-record.json telemetry-pod/REQUIREMENTS.md
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$AGENT_EE/src python3 -m agent_ee.requirement_scope $D/requirement-map.json \
  --spec-record $D/spec-record.json --spec telemetry-pod/REQUIREMENTS.md --out /path/to/new-dir
python3 $D/temperature_ratings.py --check [--pdf U3=/path/to/NEO-M9N-00B_DataSheet_UBX-19014285.pdf]
PYTHONDONTWRITEBYTECODE=1 python3 -I $D/placement_subjects.py --agent-ee $AGENT_EE [--board PCB ...]
PYTHONDONTWRITEBYTECODE=1 python3 -I $D/probe_configuration.py $AGENT_EE $D/compiled /path/to/new-work-dir
```

The compile must reproduce `compiled/` byte for byte: scope sha256 `534b9223…`, baseline
`8020c370…` (AGENTEE-484: C130-C133 added to the subjects; before it, `6a74fee2…` / `30bb6af0…`). The U3 datasheet is not in this repository. Without `--pdf`, the script reports its
bytes as unavailable instead of verified.

## Configuration probe

`probe_configuration.py` calls `pod_driver.validate_configuration` with the compiled scope. Its input tree
holds the captured requirement files, the current microSD schematic and project, and a placeholder empty
board. The plan-side declarations are **synthetic**, following agent-ee's `tests/test_pod_driver.py`:
`/usr/bin/false` producer steps, a stand-in router checkout with a mocked pin, and writer files that hold
no design data. The probe therefore tests only the scope-side gates: stage order, subjects, checks per stage,
the `fab_package` done gate, spec capture, POD-AC-8/9 bench obligations, and the review profile.
It is not a production pod plan. The real plan still needs the envelope, parts, binding, emitter,
placement adapter, plane plan and pinned router declarations (see agent-ee `docs/pod-composition.md`).
