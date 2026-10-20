# Expanded native schematic candidate

This candidate brings the complete 332-component prepared source into a native
KiCad schematic. Its netlist has 326 non-power symbols, including copper features, plus six
power flags in the source. The actual
telemetry-pod project remains unchanged. This is not a fabrication release.

The emitter is agent-ee `e4cf3ab31eca7c2ed74740e6a6db61c76d3b7372`.
Its released private-property support permits the captured CAN clock symbol to
retain its metadata. The emission receipt pins the implementation and inputs.

`prepare.py` layers four explicit adaptations onto the reviewed thermistor
source:

- Shorten the auxiliary-power group title from 70 characters to fit the
  emitter's 64-character limit, preserving the qualification-pending label.
- Set `in_bom=false` for JP1–JP5. These copper features remain on-board and
  present in native connectivity. No fictitious MPN or supplier identity is added.
- Capture the missing C128 1206 footprint from the installed KiCad library at
  `/usr/share/kicad/footprints/Capacitor_SMD.pretty/C_1206_3216Metric.kicad_mod`.
  Its SHA-256 is pinned in the preparation script. This supplies CAD, not a
  selected capacitor or qualified land pattern.

- Correct MCP3208 DOUT pin 12 from `output` to `tri_state`. The exact captured
  manufacturer datasheet DS21298E shows output disable/high impedance in
  Figures 1-2/1-3 and 5-1/5-2. Only this electrical-type atom changes; pin
  geometry, names, numbers, other metadata and circuit connectivity are preserved.
  The corrected library digest is propagated to the intent.

The generated project resolves symbols and footprints from captured libraries.
Circuit nets, component values and ERC exclusions are unchanged. The native ERC
report from KiCad 10.0.7 now has zero errors and zero warnings. The preceding
shared-output warning is retained in `previous-spi-erc.json`; it was resolved by
correcting an inaccurate symbol type, not by an ERC waiver.

This does not qualify shared-SPI arbitration. MCP3208's 100 ns maximum output
release and 500 ns minimum chip-select high times are listed under default 5 V
conditions; the ADC operates at 3.3 V here. They are not asserted as guaranteed
3.3 V turnaround limits. The CAN controller and IMU also require their own
release-time, startup and configuration checks. See `spi-arbitration.md`.
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
