# Pod I/O map input

`io-map.csv` is an input to the future pod generator. Its 23 `AMPSEAL-<cavity>`
rows describe the TE 776228-1 header. Six other rows cover the module's BLE radio,
the GNSS SMA connector (center and shield), and the factory UART pogo pads
(TX, RX, return). These extra rows are outside the AMPSEAL housing.

The cavity allocation is proposed by FOMEMC-30: 1–2 CAN, 3–4 power and ground,
5–7 front fork, 8–10 rear shock, 11–13 front brake, 14–16 rear brake, and 17–23
plugged. Revision 2 specifies the functions and counts but does **not** specify
cavity numbers. The generated design must reconcile this proposal with its
connector symbol and footprint. `AMPSEAL` is a logical connector identifier;
it does not assign a KiCad reference. Net names in this CSV are proposed names
to bind when generating the schematic, not observations of the empty skeleton.

The columns, in order, are:

```text
Connector_Pin,Signal_Name,Net,Direction_Class,Voltage_Current_Domain,MCU_Ref,MCU_Pin,External_Destination,Notes
```

Each row has nine nonempty fields, with ordinary CSV quoting. Directions are
relative to the pod. `N/A` means a field does not apply; `N/C` is reserved for
an explicitly unconnected cavity. Each unused cavity has `Signal_Name=NO_CONNECT`,
`Direction_Class=No_Connect`, no PCB net, no harness contact, and a TE 770678-1
cavity plug. No-connect rows do not mean spare signals wired to the board.

`MCU_Ref=TBD` means the ESP32-S3-WROOM-1 reference is not assigned. `MCU_Pin=TBD`
means the specification leaves its GPIO assignment open. CAN pins reach the MCU
through the TJA1051T/3, and analog signals through the protected divider and
MCP3204 SPI ADC; they are not direct GPIO/ADC connections. ADC channel assignments,
UART test-pad references and boot-entry implementation, the SMA reference and
active-antenna bias, and sensor-return topology remain generator obligations.
The BLE antenna is integrated into the MCU module and has no external GPIO.

The power row names a harness splice on the relay circuit feeding ECU J1-27,
through the pod's own 2 A fuse. Ground returns to the J1-34 CHASSIS_ECU_GND circuit.
Sensor supplies share the pod's own 5.00 V ±1% rail with a **total** 200 mA budget;
the four rows do not each promise 200 mA. The ADC reference is derived from this
rail at the connector, with both inputs and reference divided by two per the
MCP3204 decision. ECU J1-30/J1-31 are unused by the pod.

## Pinned sources

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

## Reproduce the cross-check

From this worktree, extract the pinned capture into an existing scratch directory
(the command reads Git objects without checking out or modifying agent-ee):

```sh
git --git-dir=/home/halbritt/git/agent-ee/.git show \
  ffa8c85c0840937f3ae6861ffb58ed4392c3df4a:fixtures/telemetry-pod/spec-record.json \
  > "$scratch/spec-record.json"
python3 telemetry-pod/verify_io_map.py "$scratch/spec-record.json"
```

`verify_io_map.py` uses only Python's standard library. It verifies the pinned
spec, capture and document identities, validates every captured interface-row
byte range against the spec, checks the CSV structure and cavity declarations,
and prints the requirement-to-row mapping and every cell containing `TBD`.
`io-map-cross-check.txt` is the committed output. Compare a fresh run with that
file to check reproducibility.

This cross-check proves CSV structure and traceability. The pod still has an
empty schematic, so electrical connectivity and MCU pin suitability remain
unverified. The existing `make verify-io PROJECT=fome-mc` gate checks the ECU;
it does not consume the pod CSV.

AGENTEE-188 (`pod-33`) will compile this file using agent-ee `io_map` and produce
`contracts/telemetry-pod.interface.json`. That compiler is not built at this
assignment's pinned input. No contract is hand-written here, and compiler
acceptance is **not evaluated**. Its eventual strict input rules and generated
netlist agreement must be checked before this map is accepted as a board pinout.
