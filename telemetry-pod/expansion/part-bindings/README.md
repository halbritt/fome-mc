# Expanded pod identity bindings

This packet adds identity metadata to 66 previously unbound components: the
40 selected divider resistors and 26 already-selected active, crystal and
inductor instances. The manifest has 17 exact manufacturer/supplier identities,
component IDs, references, footprints, source URLs and SHA-256 pins. It does not
change circuit connectivity, values, footprints, or earlier bindings.

The prepared source now contains 192 bindings, with 129 component bindings still
missing, five copper jumpers awaiting fabrication policy and six power flags.
Presence of a binding is not electrical, thermal, parameter, assembly or release
qualification. The earlier 126 bindings are retained without requalification.
New bindings explicitly state that qualification is pending. Required normalized
rating parameters and complete pipeline part qualification remain outstanding.

Each selected catalog is replayed against its retained raw responses. All 17
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

## Recovered eMMC provenance

U14 now has an identity binding. The four original raw stock responses were
recovered from retained local artifacts and restored to storage-candidate; each
matches the hash and byte count in the original committed catalog. The newer
exact-ID C3249972 capture remains under `emmc-stock/`.

The current supplier API's datasheet endpoint returned HTTP 403. A working
supplier-hosted manufacturer-document URL was found and downloaded independently
by both producer and reviewer. Both downloads are byte-identical to the reviewed
A-00093 revision 1.0 PDF already in storage-candidate. `emmc-source.json` records
the working URL, digest and recovery. This repairs provenance without changing
the document or component selection.

The primary MCP3208, three ADS1119 diagnostic converters and TL431 shunt also
receive exact identities from `adc-shunt-stock/`, using their existing reviewed
manufacturer documents. Exact MPN matching excludes similarly named ATL431,
other grades, packages and manufacturers. Accepted 85 °C exceptions and all
operating qualification holds remain unchanged.

Independent review is in `review/`. All earlier shared-SPI, Hall-input, rail,
thermistor, transient, thermal, mechanical, firmware and manufacturing holds
remain. This packet is a step toward complete part binding, not manufacturing
acceptance.
