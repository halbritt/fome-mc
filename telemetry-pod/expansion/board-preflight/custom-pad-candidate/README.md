# Custom-pad index repair exercised on the expanded pod

The **unreleased** AGENTEE-300 commit
`15fe86fbd93b95654d19165a3692bcec475aaa26` indexes all 40 selected footprint
types and matches the pin-number sets of all 327 native physical components.
There are no index findings, unindexed references or numbering mismatches.

The prior 39 indexed footprint records are unchanged. The only added type is
`Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm`, used by JP1–JP5.
Its exact captured bytes are unchanged and no custom-pad declaration was added.
The index retains the primitives, native pad number and anchor, and the copper
bounding box obtained through KiCad 10.0.7. Pad 1 spans -1.15 to -0.15 mm in X;
pad 2 spans 0.15 to 1.15 mm. Both span -0.75 to 0.75 mm in Y. This agrees with
the intended 0.3 mm open gap, but bounding boxes alone do not qualify all copper,
mask or fabrication behavior.

The original refusal remains in `../footprint-report.json`. This new packet is
candidate evidence, not a replacement claim that released main supports the
jumper. Main and origin/main were observed at `014c7c3`, where the 256-component
reader limit still blocks the complete design. AGENTEE-298's capacity repair and
AGENTEE-297's mask/courtyard predicate repair are separate pending work.
No board import, placement or routing was attempted by this index check.

## Reproduce

Extract the exact candidate commit with `git archive` into a fresh directory,
then run from the fome-mc root:

```sh
PYTHONPATH=/path/to/15fe86f/src python3 telemetry-pod/expansion/board-preflight/check_footprints.py
```

The output must match `footprint-report.json` byte-for-byte. The existing checker
still describes its bounded scope as index/numbering diagnostics; this candidate
adds native custom-pad facts, not general geometry or assembly qualification.
It exits zero after producing diagnostics even if findings exist, so inspect
execution, coverage, findings, unindexed references and numbering mismatches.
`provenance.json` pins the tool archive, exact inputs, report and comparison.
