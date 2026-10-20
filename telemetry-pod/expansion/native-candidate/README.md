# Expanded native schematic candidate

This candidate brings the complete 332-component prepared source into a native
KiCad schematic. Its netlist has 326 non-power symbols, including copper features, plus six
power flags in the source. The actual
telemetry-pod project remains unchanged. This is not a fabrication release.

The emitter is agent-ee `e4cf3ab31eca7c2ed74740e6a6db61c76d3b7372`.
Its released private-property support permits the captured CAN clock symbol to
retain its metadata. The emission receipt pins the implementation and inputs.

`prepare.py` layers three explicit adaptations onto the reviewed thermistor
source:

- Shorten the auxiliary-power group title from 70 characters to fit the
  emitter's 64-character limit, preserving the qualification-pending label.
- Set `in_bom=false` for JP1–JP5. These copper features remain on-board and
  present in native connectivity. No fictitious MPN or supplier identity is added.
- Capture the missing C128 1206 footprint from the installed KiCad library at
  `/usr/share/kicad/footprints/Capacitor_SMD.pretty/C_1206_3216Metric.kicad_mod`.
  Its SHA-256 is pinned in the preparation script. This supplies CAD, not a
  selected capacitor or qualified land pattern.

The generated project resolves symbols and footprints from captured libraries.
No symbol electrical types, circuit nets, component values or ERC exclusions
are changed. The retained native ERC report from KiCad 10.0.7 has zero errors
and one warning: U20 SDO (tri-state) shares a net with U4 DOUT (output).
This warning remains open pending verification of output enable/disable behavior,
chip-select sequencing and contention conditions. It is not waived here.
The native BOM contains 315 entries: JP1–JP5, six existing pogo pads and six
power flags are excluded. This checks schematic population policy, not assembly
readiness or PCB fabrication policy.

The report also records the project's existing ignored-check settings; this is
not a claim that every possible ERC check is enabled.

Run from the repository root:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/native-candidate/verify.py
```

The verifier regenerates the candidate byte-for-byte and checks native netlist
connectivity and the exact retained ERC findings on a fresh snapshot. It does
not modify the candidate. Independent review evidence is in `review/`.

Prior electrical, thermal, power, Hall-input, sensor-selection and assembly
holds remain in the source packets. The 40 resistor selections remain unbound;
existing bindings have not been requalified. Copper-feature fabrication policy
AGENTEE-289 is separate from schematic BOM exclusion. Expanded IO contracts,
placement, routing, DRC, manufacturing outputs and independent release review
remain outstanding.
