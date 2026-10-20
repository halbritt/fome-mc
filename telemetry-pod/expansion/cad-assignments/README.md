# Expanded-pod CAD assignments

All 327 physical component assignments pass native symbol identity, pin names/types, footprint pin/pad correspondence and assembly-attribute checks. Six omitted power symbols are separately accounted for. This uses the experimental combined AGENTEE-298/300 software pinned in `../board-preflight/import-experiment/software.json`, not a released software revision.

`before-report.json` retains the five refusals for JP1–JP5: the captured stock footprint omits an assembly-type attribute. `declarations.json` explicitly classifies its two undrilled surface copper pads as `smd`. Native custom geometry remains checked; `custom_pads` is empty. This does not make a solder jumper a purchased or pick-and-place component. The original footprint bytes are unchanged.

Four historical declarations for shared-number ground vias transfer only after exact footprint-byte comparison, retained in `declaration-transfer.json`. J1 is assigned through-hole; the remaining physical footprints are assigned surface mount. No rectangular connector-grid assumption is applied to AMPSEAL.

Replay with the exact pinned combined source on PYTHONPATH:

```sh
python3 telemetry-pod/expansion/cad-assignments/check.py --verify
```

Independent replay matched both result and retained report bytes. This evidence does not qualify manufacturer land dimensions, thermal behavior, process/paste selection, board placement, connector fit, routing or assembly. Parts-manifest support for the five two-pad copper jumpers remains open. No source schematic, footprint, board or parts binding changed.
