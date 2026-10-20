# Independent prepared Hall review

```sh
PYTHONPATH=/path/to/agent-ee/src python3 check_prepared_wheel.py OLD_INPUTS NEW_INPUTS REPORT_JSON
```

OLD_INPUTS is the sensor-power inputs directory. NEW_INPUTS is the prepared wheel-input inputs directory. The checker imports only the complete symbol-library parser, not the circuit producer. It independently builds the complete permitted graph delta and parses every authored library, verifies declared library hashes, preserves prior authored libraries and component records, and checks physical comparator/diode/TVS pin functions.

Final result:1068 checks passed, covering exactly26 new components, four old NC assignments, complete old graph preservation, resistor/capacitor nominal values and assigned footprint names. No prepared wiring defect found. The checker does not prove actual footprint dimensions, passive tolerances or native emitter behavior. Source/parser/checker hashes are recorded in prepared-report.json.

Three negative probes all failed as expected: swapping D102 anode/cathode nets, grounding an existing U23 RTN exposed pad, and removing the outer wheel-library close. For the syntax probe the declared library hash was updated to the damaged content, so parser rejection—not merely stale hash detection—establishes coverage. See negative-probes.json.

The electrical release holds in diode-fault-review.md remain: unbounded negative recovery/transient voltage at the LM2903B input, missing sensor VOL/minimum pulse widths, exact part/thermal coupling and assembled qualification. No native KiCad ERC, physical fault survival, current automotive qualification or production acceptance is claimed.
