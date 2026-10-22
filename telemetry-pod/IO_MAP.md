# Pod I/O map and compiled contract (Rev-3)

`io-map.csv` describes the Rev-3 pod source schematic
`expansion/storage-microsd/project/telemetry-pod.kicad_sch` (SHA-256
`4da27afc8d9cd7ff3d1fd8e23f855747072c050d25601b89fb3909b688e49f23`, 305 references,
the microSD source that `expansion/production-capture/` binds). The schematic at the
project root is still the v9 pilot snapshot. Its former map, bindings, paths and
contract are kept unchanged in [`pinout-checks/v9-pilot/`](pinout-checks/v9-pilot/README.md).

## Derivation

`pinout-checks/generate.py` writes `io-map.csv`, `pinout-checks/bindings.json` and
`pinout-checks/paths.json` from a kicad-cli XML netlist of the schematic named in
`pinout-checks/source.json`. It exports that netlist from a temporary copy of the
schematic. It writes no pin data by hand, and a rerun is byte-identical.

- **Rows:** every pin of every `J<n>` and `TP<n>` component: J1 (35 cavities, TE
  1-776163-1), J2 (GNSS SMA), J3 (microSD socket, including `SH`) and the six factory
  pogo pads, 54 rows. `Connector_Pin` is `<ref>-<pin>`, `Net` is the native net name,
  and `Signal_Name` is that name without the leading `/`. A pin whose native net is a
  generated `unconnected-(...)` singleton is `N/C` / `NO_CONNECT` (only J1-35).
- **MCU pins (U1, ESP32-S3-WROOM-1-N8):**
  - *Direct:* the row's own net holds a U1 pin (`MCU_Path=direct`; J3 data/clock/detect, TP1/2/4/5).
  - *Rail:* rows on a net with any `power_in`/`power_out` pin declare no MCU pin.
  - *Indirect:* otherwise one path per conductor chain that reaches U1 through the
    crossing rules below. Each segment is one native conductor, and each part between
    segments is a declared intermediate device with its native value and pin names.
    MCU and connector endpoints are never equated across a part.
- **Crossing rules:** these are the only declarations, by native pin name. Two-pin `R`
  parts; `D` parts between the `A<n>`/`K<n>` pins of one diode element;
  ADA4096-4 `±IN<x>`→`OUT<x>`; LM2903 `IN<n>±`→`OUT<n>`; MCP3208 `CH<n>`→`~{CS}/SHDN`,
  `Din`, `Dout`, `CLK`; TJA1051T/3 `CANH`/`CANL`→`TXD`, `RXD`; MCP2518FD
  `TXCAN`/`RXCAN`→`SCK`, `SDI`, `SDO`, `nCS`, `INT`. A chain never enters a rail net or
  another contact's net. That rule stops J1-1 reaching CANL through the 120 Ω
  termination R100.
- **Segment directions** come from native pin types: a driver end
  (output/tri-state/open-collector) or an input end decides. Bidirectional pairs are
  `bidirectional`. Undecided segments inherit through passive parts only.
- **Descriptive columns:** `Direction_Class`, `Voltage_Current_Domain` and
  `External_Destination` are carried from the v9 row bound to the same native pin
  when its net name is identical (24 rows: J1-1..16, J2-1/2, TP1..TP6). The Notes cell says so; these values were
  not requalified for Rev-3. Every other row says `unknown`. No committed packet gives
  per-cavity destinations for J1-17..34. The J1 mating-interface packet is mechanical
  only.

The result has 11 direct rows, 16 indirect rows with 78 paths (CAN1 2×2, analog
8×4, wheel 2×1, tire CAN 4×10) and 27 rows without an MCU pin. J1-3 (`POD_12V_IN`)
and J2-1 (`POD_GNSS_RF`) are signal nets that no crossing rule takes to U1: the
reverse-polarity FET and the GNSS receiver are not crossed.

## Decision note: verify-io evaluates the Rev-3 source schematic

*Agent decision (AGENTEE-207, fm-iomap-rev3), not an owner decision.*

- **What:** for `PROJECT=telemetry-pod`, `scripts/verify_io_map.py` builds its fresh
  native inventory from the schematic named in `pinout-checks/source.json`, after
  checking that schematic's pinned SHA-256. Before, it used the root
  `telemetry-pod.kicad_sch`. It also reruns `generate.py --check`, so the committed map,
  bindings and paths must reproduce byte-identically from that netlist. It still
  recompiles the contract and compares bytes as before.
- **Why:** the map must be verified against the design it describes. The root
  schematic is the v9 23-cavity pilot and stays a historical snapshot. The Rev-3
  design exists only as the committed expansion source.
- **Alternatives:** (a) keep checking against the v9 root. That fails on every Rev-3
  row, and those failures would not be design findings. (b) Re-emit the root
  schematic as Rev-3. That is a design change outside this item (AGENTEE-445/j6).
- **Reverse:** when the root schematic becomes Rev-3, point `source.json` at it (or
  drop `pod_source_config`) and regenerate. `make check PROJECT=telemetry-pod` still
  checks the root v9 files and is unchanged.

## Regenerate and verify

From the repository root, with agent-ee's `io_map.py`/`hardware_interface.py` as at
release `ca15c9237c0f230cff2cea189710eae63099ba37` (unchanged through main `a8a1bee1`):

```sh
python3 telemetry-pod/pinout-checks/generate.py            # or --check to compare only
PYTHONPATH=$HOME/git/agent-ee/src python3 -m agent_ee.io_map telemetry-pod/io-map.csv --csv-path telemetry-pod/io-map.csv --requirement POD-AC-1-pinout --source telemetry-pod/REQUIREMENTS.md --locator 'Acceptance criteria / item 1' --bindings telemetry-pod/pinout-checks/bindings.json --paths telemetry-pod/pinout-checks/paths.json --out contracts/telemetry-pod.interface.json
make verify-io PROJECT=telemetry-pod
```

The contract is generated, never hand-edited. Its `io_map` citations carry the CSV
hash and each invariant binds `REQUIREMENTS.md` (revision 3) by SHA-256. The gate
reports 54 connector pins and 193/193 invariants satisfied (78 indirect paths) on a
fresh snapshot netlist. Logs are under `build/runs/verify-io/telemetry-pod/`.

This is a topology gate only. It does not establish analog accuracy, CAN timing,
firmware assignments, harness destinations, wireless behaviour or fabrication
approval. The BLE radio has no electrical pin and no row, so the v9 `BLE-RADIO` row
and its POD-IF-* traceability are not carried. Requirement traceability for Rev-3
has not been recaptured. `verify_io_map.py` in this directory is the retired
revision-2 checker; `io-map-cross-check.txt` and `IO_MAP_HISTORY.md` are historical.
