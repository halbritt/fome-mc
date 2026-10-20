# Expanded pod identity bindings

This packet adds identity metadata to 60 previously unbound components: the
40 selected divider resistors and 20 already-selected active, crystal and
inductor instances. The manifest has 13 exact manufacturer/supplier identities,
component IDs, references, footprints, source URLs and SHA-256 pins. It does not
change circuit connectivity, values, footprints, or earlier bindings.

The prepared source now contains 186 bindings, with 135 component bindings still
missing, five copper jumpers awaiting fabrication policy and six power flags.
Presence of a binding is not electrical, thermal, parameter, assembly or release
qualification. The earlier 126 bindings are retained without requalification.
New bindings explicitly state that qualification is pending. Required normalized
rating parameters and complete pipeline part qualification remain outstanding.

Each selected catalog is replayed against its retained raw responses. All 13
selected identities have raw `assemblyComponentFlag=false`; this packet records
that observation without inventing an assembly exception or claiming the field
alone proves availability or ineligibility. Stock figures are capture-time data,
not current purchasing promises. The 40 resistor selections are now identity-bound
in this prepared source; the older part-selection inventory remains a historical
snapshot of its own pinned intent.

## Native generation blocker

Agent-ee e4cf3ab rejects the valid 278-character MCP2518FD `PARAM_Datasheet`
structured JSON through the emitter's generic 256-character display-field limit.
The existing `part_binding.parse_param_value` accepts this exact payload.
`emitter-blocker/valid-binding.json` and `receipt.json` retain the reproduction.
The full official URL and captured hash are preserved. No data was shortened or
removed to make emission succeed. A repair request was sent to the designated
agent-ee integrator; native generation and metadata round-trip remain unverified.
The last reviewed native schematic remains `../native-candidate/`.

Run the available source checks:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/part-bindings/verify.py --source-only
```

This command reports native verification **NOT_RUN**. Once the emitter repair
is released, run without `--source-only` to require generation, native ERC,
connectivity and metadata checks. Failure to generate is a failure of that run,
not an electrical result. `prepare.py --out NEW_DIRECTORY` preserves the full
inputs needed to reproduce the generation attempt; `--source-only` explicitly
limits it to preparation. No actual pod project has been replaced.

## eMMC provenance gap

U14 is deliberately not part of these 60 bindings. Its earlier stock catalog
lacks the referenced raw response files in the committed packet. A new exact-ID
C3249972 capture is retained under `emmc-stock/`; its current datasheet URL
returned HTTP 403 during retrieval. The earlier manufacturer PDF and its reviewed
hash remain in storage-candidate, but this packet has not established a URL-to-byte
binding for that document. The supplier identity observation and document identity
are preserved separately until that link is repaired.

Independent review is in `review/`. All earlier shared-SPI, Hall-input, rail,
thermistor, transient, thermal, mechanical, firmware and manufacturing holds
remain. This packet is a step toward complete part binding, not manufacturing
acceptance.
