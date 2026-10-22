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
| `revision-delta.json` | comparison with `../spec-record.json` | One entry added (`POD-CD-STORAGE`), none changed or removed |
| `requirement-map.json` | authored, derived from `../requirement-map.json` | Scope template and dispositions (below) |
| `datasheet-ratings.json` | authored | Datasheet citations for parts rated below 105 °C |
| `temperature_ratings.py`, `temperature-ratings.json` | script and its output | Rating inventory of all 305 references from captured catalog records |
| `probe_configuration.py` | script | Runs `pod_driver.validate_configuration` on a compiled scope |
| `compiled/` | `agent_ee.requirement_scope` (agent-ee `1da2763`) | `scope.json`, `receipt.json`, `requirements-map/` |

## What changed in the map

- **Stages.** The order is `schematic, placement, routing, verification`, and `finding_retry_limit` is 2.
  Fab stays out of the order until AGENTEE-146-compatible pod step wiring exists. Subjects: the schematic
  and verification stages list symbols, placement lists footprints, and routing requires at least one track.
  The references are the 305 that `agent_ee.stages.native_references` reads from the current microSD
  schematic (sha256 `4da27afc…`). Board-only footprints are not subjects. Project files are named
  `telemetry-pod.*`, as in the storage source.
- **Checks.** Each stage needs a check. POD-AC-3 maps to `erc` and `netlist` (schematic),
  `placement-drc` (DRC with `projection: placement-stage/1`) and routed `drc` (routing). POD-AC-6 maps to
  `netlist`, `routing-geometry` (copper facts only) and `fab-package` (verification, the
  `generation` done check). There is no numeric width gate, because no pod-wide minimum has a cited
  source here; native DRC grades the net-class widths. POD-AC-6's owner DFM upload and PREVIEW_REQUIRED
  confirmation remain an explicit limitation.
- **Review profile.** The scope embeds agent-ee's existing `profiles/pod-review.json`
  (`pod-rf-review-v1`: circuit, physical and rf reviewers plus an adjudicator) unchanged. No new provider
  route is introduced. A declared rf reviewer is not an RF review result.
- **Temperature.** No part is exempted. `POD-TEMP-ACTUAL-LIMITS` judges every part below 105 °C against its own rating:

  | Ref | Part | Rating | Citation | Owner acceptance |
  | --- | --- | --- | --- | --- |
  | U1 | ESP32-S3-WROOM-1-N8 | −40 to 85 °C ambient | datasheet `27d71971…` p. 27 | line 1 |
  | U2 | LSM6DSO32TR | −40 to 85 °C | datasheet `d1776336…` p. 26 | line 2 |
  | U3 | NEO-M9N-00B | −40 to 85 °C | datasheet `e21b35c1…` p. 11 | none (D-PCB-9) |
  | U4 | MCP3208-BI/SL | −40 to 85 °C ambient | datasheet `89bc1e17…` p. 37 | line 3 |
  | J3 | DM3AT-SF-PEJM5 | −25 to 85 °C | LCSC catalog record only; datasheet not captured | none (D-PCB-12) |

  Owner acceptance lines are in `../operating-temperature-acceptances.txt` (sha256 `7ca91bc7…`). U3 and J3 are
  agent decisions without an owner line. They fail the 105 °C part-selection criterion until the owner accepts
  them or a part rated to 105 °C replaces them. Missing thermal evidence is unknown, never pass. `POD-TEMP-UNRATED`
  keeps the 117 bound parts with no captured rating, and the 11 unbound JP/TP references, explicitly unknown.
  The old exemption file is cited only as superseded provenance.

Every other disposition, including the BENCH REQUIRED rows for POD-AC-8 to AC-11, is carried
unchanged from `../requirement-map.json`.

## Reproduce

From the fome-mc root, using an agent-ee checkout at `1da27635c990418ec4360434ee2a879e6918cf57`:

```sh
D=telemetry-pod/expansion/requirements/rev3-microsd
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$AGENT_EE/src python3 -m agent_ee.spec_record verify $D/spec-record.json telemetry-pod/REQUIREMENTS.md
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$AGENT_EE/src python3 -m agent_ee.requirement_scope $D/requirement-map.json \
  --spec-record $D/spec-record.json --spec telemetry-pod/REQUIREMENTS.md --out /path/to/new-dir
python3 $D/temperature_ratings.py --check [--pdf U3=/path/to/NEO-M9N-00B_DataSheet_UBX-19014285.pdf]
PYTHONDONTWRITEBYTECODE=1 python3 -I $D/probe_configuration.py $AGENT_EE $D/compiled /path/to/new-work-dir
```

The compile must reproduce `compiled/` byte for byte: scope sha256 `ee0381c1…`, baseline
`f38b5554…`. The U3 datasheet is not in this repository. Without `--pdf`, the script reports its
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
