# Pod I/O map and compiled contract

`io-map.csv` describes the committed v9 pilot: 23 AMPSEAL cavities, the integrated
BLE radio, two GNSS SMA contacts and six factory debug pads. Logical row names
bind to native references through `pinout-checks/bindings.json`. The three debug
rows for EN, BOOT and 3V3 come from the pilot5 inputs; this change adds no design
content. Notes retain the original proposal's wording, including historical
`TBD` text; the Net, MCU_Ref, MCU_Pin and MCU_Path columns carry the resolved
connectivity declarations.

CAN rows name `/POD_CAN_P` and `/POD_CAN_N`; sensor returns name `/GND`.
Concrete MCU pins use either `MCU_Path=direct` or semicolon-separated indirect
path IDs, one per MCU pin. `pinout-checks/paths.json` supplies the intermediate
terminals, devices, pin names and directions for the CAN and ADC paths.
Cavities 17–23 declare `N/C`, with no MCU pin. The integrated BLE antenna has
`Net=N/A` and no electrical connector terminal.

## Input provenance

The following files were copied byte-for-byte from:

```text
/tmp/agent469-coordination/pod-campaign-v1/driver-preparation-v8-90x65/work-inputs-pilot5/pinout-checks
```

| Pilot5 source file | Committed destination | SHA-256 |
| --- | --- | --- |
| `io-map.paths.csv` | `telemetry-pod/io-map.csv` | `be690c01194f2f77e9f3079e1e26d868d0d679c659c53afa457e4feb855b40ea` |
| `bindings.json` | `telemetry-pod/pinout-checks/bindings.json` | `6790d55291b35e32e3d80187a024b918d49f6e5ac877bb8480a63143442c178b` |
| `paths.json` | `telemetry-pod/pinout-checks/paths.json` | `b5cffef62beecb5a78af00cece8362f0d4561bfa758740b1d3cec303438cb47e` |

These are the pilot5 inputs matching the committed v9 board. The similarly named
`pinout-path-proposal-v1` directory was inspected but supplies no copied inputs.
Native `telemetry-pod/*.kicad_*` files are unchanged.

## Regenerate and verify

Compiler: agent-ee commit `62fb279fb0129de06154675d876989c53cb079a7`.
From the repository root, using that existing checkout:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 -m agent_ee.io_map telemetry-pod/io-map.csv --csv-path telemetry-pod/io-map.csv --requirement POD-AC-1-pinout --source telemetry-pod/REQUIREMENTS.md --locator 'Acceptance criteria / item 1' --bindings telemetry-pod/pinout-checks/bindings.json --paths telemetry-pod/pinout-checks/paths.json --out contracts/telemetry-pod.interface.json
make verify-io PROJECT=telemetry-pod
```

The contract is generated, never hand-edited. Its per-invariant `io_map` citations
include the CSV hash. A changed CSV with a stale contract fails verification.
The gate checks a fresh native netlist and source geometry on a snapshot and
reports 81 of 82 invariants satisfied, including 20 indirect paths. It prints
`BLE-RADIO` as declared wireless `not_evaluated`; that obligation remains unknown
and is never counted as satisfied. Any other non-satisfied invariant fails.
This connectivity gate does not establish analog performance, firmware behavior,
wireless operation, physical debug access, or fabrication approval.

`telemetry-pod/verify_io_map.py` is the earlier specification traceability check.
It expects the original proposal header and pinned revision-2 specification;
that specification differs from the current requirements. Its retained
`io-map-cross-check.txt` is historical evidence, not a current gate. Use the
repository `make verify-io PROJECT=telemetry-pod` command above for this pilot.
