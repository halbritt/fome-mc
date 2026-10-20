# Independent prepared diagnostic-circuit review

```sh
PYTHONPATH=/path/to/agent-ee/src python3 check_prepared_diagnostic.py OLD_INPUTS NEW_INPUTS REPORT_JSON
```

OLD_INPUTS is wheel-input/inputs; NEW_INPUTS is diagnostic-circuit/inputs. The checker independently constructs the permitted additions, preserving complete old component records, net membership and no-connect state except MCU module pins22/23. It imports the complete authored-library parser but no producer helper. All authored libraries are parsed, declared hashes checked, and old authored sources preserved byte-for-byte.

Result: **1256 checks passed**. This covers exactly51 new components, two MCU NC assignments,13 new NC pins, eight complete301:1 dividers, three distinct address straps, the16-pin TSSOP physical map, nominal values and assigned footprint names. No prepared wiring defect found.

Eight rails are implemented. U28 AIN2/pin7 is explicitly NC because the auxiliary5V branch is absent. The ninth measurement remains deferred; neither the circuit nor this pass completes the nine-rail target. J1 auxiliary positions21/22 remain unchanged. Firmware must not poll the unused channel or treat it as a valid zero-volt rail.

Four meaningful negative probes were detected:

- Swapped AIN0/AIN1 names in the ADC physical symbol, with updated declared library hash: physical pin-map check failed.
- Moved U28 A0 to ground, colliding with U27: exact strap graph failed.
- Grounded the prior U23 RTN exposed pad: preservation checks failed.
- Removed the outer library closing parenthesis, with updated declared hash: complete-library parsing failed.

See prepared-report.json for input, CAD, parser and checker hashes; negative-probes.json retains failure labels. The source README correctly preserves the provisional I2C capacitance/timing assumptions and treats the nine-conversion study schedule as conservative for this eight-channel intermediate circuit. It correctly reserves U28 AIN2 and records first-frame settling requirements.

This verifies prepared source only. Native emission, ERC, footprint physical dimensions, exact passive/ADC assembly bindings, effective capacitance, powered-off leakage/back-powering, transient envelope, full-temperature errors and measured I2C behavior remain open. All prior Hall negative-transient, thermal and fault-survival holds remain. No hardware or fabrication acceptance is claimed.
