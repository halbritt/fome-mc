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

## Preserved design intent and historical sources

The complete prior proposal document from `13c0bfb:telemetry-pod/IO_MAP.md` is
preserved verbatim in [IO_MAP_HISTORY.md](IO_MAP_HISTORY.md). Its proposal,
empty-skeleton and future-compiler statements describe that historical stage;
the resolved connectivity and current gate are documented here above and below.
In particular, the current map has ten columns including `MCU_Path` and 32 rows.

Directions are relative to the pod. `N/A` means a field does not apply; `N/C`
is reserved for an explicitly unconnected cavity. `TBD` denotes an unresolved
assignment in the original proposal; it does not establish connectivity.
The current compiler and native gate evaluate the resolved columns and paths.

The power row names a harness splice on the relay circuit feeding ECU J1-27,
through the pod's own 2 A fuse. Ground returns to the J1-34 CHASSIS_ECU_GND circuit.
Sensor supplies share the pod's own 5.00 V ±1% rail with a **total** 200 mA budget;
the four rows do not each promise 200 mA. The ADC reference is derived from this
rail at the connector, with both inputs and reference divided by two per the
MCP3204 decision. ECU J1-30/J1-31 are unused by the pod.

These are design-intent decisions, not analog-performance verdicts from verify-io.
The following pinned identities describe the original revision-2 source capture;
they do not claim that today's `REQUIREMENTS.md` still has that digest.
The historical verifier and its output are retired, as explained below.

Owner decision 6 requires identities rather than moving `main` links:

| Source | Identity |
| --- | --- |
| `telemetry-pod/REQUIREMENTS.md` revision 2 | SHA-256 `09e02c8d9471aabfa5d25935c87f436370cf1be367a96425b35305a53ce93493` |
| agent-ee `fixtures/telemetry-pod/spec-record.json` | commit `ffa8c85c0840937f3ae6861ffb58ed4392c3df4a`; Git blob `2b7f861c50368e665517c1aa0a783d409469f2ea`; SHA-256 `58f07c5ab3206aad70fc31561d873200d18ff9145b97cc0b1570c465a84fd250` |
| `docs/WIRING_SV650_K7.md`, section 7 | Git blob `bb0ff8c1a32faef6e7cc8fe1e67538829544b106` |
| `docs/TELEMETRY_AND_RACECHRONO.md` | Git blob `3dafed620a10f8fba209c2707b8f832eec6f6303` |

The CSV includes full wiring-document blob citations in external destinations.
Its Notes carry the captured `POD-IF-*` requirement IDs and relevant sensor
function IDs. SMA is fixed by the NEO-M9N component decision even though the
interface row alone allows SMA or U.FL.

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

Compiler: agent-ee release `ca15c9237c0f230cff2cea189710eae63099ba37`.
From the repository root, using that existing checkout:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 -m agent_ee.io_map telemetry-pod/io-map.csv --csv-path telemetry-pod/io-map.csv --requirement POD-AC-1-pinout --source telemetry-pod/REQUIREMENTS.md --locator 'Acceptance criteria / item 1' --bindings telemetry-pod/pinout-checks/bindings.json --paths telemetry-pod/pinout-checks/paths.json --out contracts/telemetry-pod.interface.json
make verify-io PROJECT=telemetry-pod
```

The contract is generated, never hand-edited. Its per-invariant `io_map` citations
include the CSV hash. Each invariant also binds the requirements source with
`source.sha256`. A changed CSV or requirements source with a stale contract fails verification.
Every pod verification also recompiles the CSV, bindings and paths with the installed agent-ee checkout
and compares the output bytes against the committed contract. Hand edits, including
swaps between terminals on the same net, fail. Compiler logs and the fresh JSON
are retained under `build/runs/verify-io/telemetry-pod/`.
The gate checks a fresh native netlist and source geometry on a snapshot and
reports 81 of 82 invariants satisfied, including 20 indirect paths. It prints
`BLE-RADIO` as declared wireless `not_evaluated`; that obligation remains unknown
and is never counted as satisfied. Any other non-satisfied invariant fails.
This connectivity gate does not establish analog performance, firmware behavior,
wireless operation, physical debug access, or fabrication approval.

`telemetry-pod/verify_io_map.py` is explicitly retired: it exits 2 with a
retirement message and points to the current gate. The old checker and reproduction
instructions can be inspected at `13c0bfb:telemetry-pod/verify_io_map.py` and in
`IO_MAP_HISTORY.md`. It checked the original nine-column proposal against the
revision-2 capture; later requirements changes invalidated that pinned-input
precondition, and the current map also has `MCU_Path`. We have not recaptured or
claimed current specification traceability. The retained `io-map-cross-check.txt`
is historical evidence only. Use `make verify-io PROJECT=telemetry-pod` for current
native connectivity and compiled-input parity; that gate does not replace a
specification traceability review.
