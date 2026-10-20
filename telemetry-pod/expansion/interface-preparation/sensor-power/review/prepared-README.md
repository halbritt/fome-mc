# Prepared graph check

Run:

```sh
python3 check_prepared_graph.py OLD_INTENT NEW_INTENT AUTHORED_SYMBOL REPORT_JSON
```

The checker independently constructs all allowed additions from the prior graph. It verifies all old component records, exact complete net and NC sets, the five connector NC reassignments,24 new components/values and all11 physical TPS26625 pin names. It imports no producer helper. Result:880 checks passed for the final prepared intent with10nF50V C0G10% dVdT capacitors. Source hashes are in prepared-report.json. Both deliberate regressions—grounding U23 EP and moving an existing ADC terminal—are detected; see negative-probes.json.

This is prepared-source graph evidence only. Native emitter compatibility, final emitted pin identities, ERC, footprint physical dimensions, component sourcing and board qualification remain separate.

The final candidate uses1uF50V X7R0805 input capacitors C86/C89/C92 and100nF output capacitors. The checker verifies the intended input values and footprints. Exact effective capacitance, voltage/temperature behavior and transient performance remain binding gates; a nominal1uF label alone does not establish1uF at operating conditions.

The selected generic footprint differs from TI's example land dimensions (parent reports0.85x0.28mm pads at±1.475mm versus TI0.6x0.24mm at±1.4mm); the checker verifies the assigned footprint name, not land qualification. Separate RTN/EP islands, no direct FLT/SHDN MCU connections, narrow ladder recovery margin and other limits in independent-review.md remain binding review conditions.
