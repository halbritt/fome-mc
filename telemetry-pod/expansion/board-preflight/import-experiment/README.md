# Expanded-board import experiment

The isolated combination of the committed AGENTEE-298 capacity repair and
AGENTEE-300 custom-pad repair advances the real pod past both earlier refusals.
It exposes a separate probe-metadata migration failure during apply. **No board
was published, placed or routed.** The internal board retained here is rejected
evidence, not a candidate approved for further manufacturing steps.

## Software identity

`software.json` pins the base archive at
`b41807e31479c5e4cfa33fd05f632dd73c03a661` and the exact patch from
`014c7c3` to `15fe86fbd93b95654d19165a3692bcec475aaa26` for only:

- `src/agent_ee/footprint_library.py`
- `src/agent_ee/footprint_probe.py`
- `src/agent_ee/forward_annotation.py`

The retained `software-overlay.patch` applies cleanly to that archive. This is
an experimental combined source tree, not a merged or released revision. It
changes neither the integrator's checkout nor either worker branch. Released
main was still `014c7c3` when tested. AGENTEE-301's `d2bebf2` is only a worker
start marker, not a committed text repair.

## Results

1. Planning against the unchanged pilot now passes inventory and footprint
   indexing, then refuses `footprint_change_unsupported` at U4. The pilot has
   the MCP3204 footprint; the expanded source uses MCP3208. Retaining the old
   placed footprint would not be a valid update. See `pilot-plan-refusal.json`.
2. A separate diagnostic scaffold retains the pilot's board settings, outline
   and four mounting holes. It removes all circuit footprints, tracks, zones
   and non-Edge.Cuts board drawings. `scaffold-receipt.json` lists removals and
   pins both boards. Existing unused net definitions may remain. The outline
   is a target inherited from the pilot, not qualified enclosure fit. This is
   not a production scaffold or an approved keepout/placement policy.
3. `plan.json` succeeds: 327 added footprints, four board-only mounting holes,
   369 new nets, 1,128 pad changes, no stale nets and no findings. All circuit
   footprints are destined for the normal staging column outside the outline.
4. Apply's native child writes the staged board, and the separate saved-board
   inventory/pad verification completes. Final `probe_features.validate_board`
   refuses `TP4: legacy AGENT_EE_Probe property requires forward-annotation
   migration`. `apply.json` reports execution failed, outcome unknown and
   output null. The requested destination was not created.

The six probe properties in the native XML are legacy raw JSON. Planning parses
and validates them with legacy admission enabled, but the apply path carries the
raw fields into the saved footprints. Its final validator disallows that legacy
encoding. No malformed identity or changed probe geometry was needed to trigger
the refusal. The next repair must establish a consistent migration contract
across source, plan, writer, native parity and final verification. Suppressing
probe validation or accepting arbitrary legacy fields is not demonstrated by
this experiment.

`rejected-board.kicad_pcb.gz` preserves the child's unpublished board for
investigation. `rejected-board-facts.json` and the execution records preserve
native observations. This board has no routing and has staged circuit footprints;
it must not be mistaken for the requested placed design. The unchanged pilot
hash is checked in `provenance.json`.

## Reproduce the observed failure

Extract the pinned base archive, apply `software-overlay.patch`, and put its
`src` on `PYTHONPATH`. From the fome-mc root, use fresh work/output paths:

```sh
python3 -m agent_ee.forward_annotation plan \
  telemetry-pod/expansion/board-preflight/import-experiment/scaffold.kicad_pcb \
  --netlist telemetry-pod/expansion/released-presentation/candidate/native.xml \
  --manifest telemetry-pod/expansion/board-preflight/footprints.json \
  --captures telemetry-pod/expansion/series-divider/native-candidate/inputs \
  --work /path/to/fresh-plan-work --record /path/to/new-plan.json
python3 -m agent_ee.forward_annotation apply \
  telemetry-pod/expansion/board-preflight/import-experiment/scaffold.kicad_pcb \
  --netlist telemetry-pod/expansion/released-presentation/candidate/native.xml \
  --manifest telemetry-pod/expansion/board-preflight/footprints.json \
  --captures telemetry-pod/expansion/series-divider/native-candidate/inputs \
  --plan /path/to/new-plan.json --out /existing/output-dir/new-board.kicad_pcb \
  --backup-dir /path/to/separate-backups \
  --work /path/to/fresh-apply-work --record /path/to/new-apply.json
```

The plan should succeed and apply should refuse as above, with no published
output. A different result requires inspection, not silently updating the retained
receipt. Native process paths in execution records identify the original run;
all substantive source and board bytes are retained or pinned here.
