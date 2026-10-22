# Pod I/O map and compiled contract (Rev-3)

`io-map.csv` describes the Rev-3 pod source schematic
`expansion/storage-microsd/project/telemetry-pod.kicad_sch` (SHA-256
`4da27afc8d9cd7ff3d1fd8e23f855747072c050d25601b89fb3909b688e49f23`, 305 references,
the microSD source that `expansion/production-capture/` binds). The schematic at the
project root is still the v9 pilot snapshot. Its former map, bindings, paths and
contract are kept unchanged in [`pinout-checks/v9-pilot/`](pinout-checks/v9-pilot/README.md).

## Derivation

`pinout-checks/generate.py` writes `io-map.csv`, `pinout-checks/bindings.json`,
`pinout-checks/paths.json` and `pinout-checks/citations.json` from a kicad-cli XML netlist of the schematic named in
`pinout-checks/source.json`. It exports that netlist from a temporary copy of the
schematic. It writes no pin data by hand, and a rerun is byte-identical.

- **Rows:** every pin of every `J<n>` and `TP<n>` component: J1 (35 cavities, TE
  1-776163-1), J2 (GNSS SMA), J3 (microSD socket, including `SH`) and the six factory
  pogo pads, 54 rows. `Connector_Pin` is `<ref>-<pin>`, `Net` is the native net name,
  and `Signal_Name` is that name without the leading `/`. A pin whose native net is a
  generated `unconnected-(...)` singleton is `N/C` / `NO_CONNECT` (only J1-35).
- **Wireless row:** `BLE-RADIO` follows the 54 contact rows (55 rows in all). It is
  declared in `source.json`, not read from the netlist: `Net`, `MCU_Ref`, `MCU_Pin` and
  `MCU_Path` are `N/A`, and no native pin is invented for it. It cites
  `POD-IF-BLUETOOTH-LE`, `POD-IF-PROGRAMMING-AND-DEBUG` (field updates over BLE) and
  `POD-AC-9` from the Rev-3 spec record
  `expansion/requirements/rev3-microsd/spec-record.json`. The generator checks that the
  record's digest and byte locators match the current `REQUIREMENTS.md`. `Signal_Name`
  and the three descriptive columns are carried from the v9 `BLE-RADIO` row, not
  requalified. The compiler keeps it as one `unresolved` invariant, and `verify-io`
  prints it as `NOT_EVALUATED` apart from the wired count.
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
  when its net name is identical (24 rows: J1-1..16, J2-1/2, TP1..TP6). The v9 row's
  `POD-IF-*` citations are carried with them, and each must exist in the Rev-3 spec
  record. The Notes cell says so, and `citations.json` records it in machine-readable
form (see *Citation status* below); these values were not requalified for Rev-3. Every other row says `unknown`. No committed packet gives
  per-cavity destinations for J1-17..34. The J1 mating-interface packet is mechanical
  only.

The result has 11 direct rows, 16 indirect rows with 78 paths (CAN1 2×2, analog
8×4, wheel 2×1, tire CAN 4×10) and 28 rows without an MCU pin (27 contacts and
`BLE-RADIO`). J1-3 (`POD_12V_IN`)
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
hash and the row's `POD-IF-*` IDs, and each invariant binds `REQUIREMENTS.md`
(revision 3) by SHA-256. It has 194 invariants: 193 wired ones (78 indirect paths) and
the unresolved `BLE-RADIO:net`. On a fresh snapshot netlist the gate verifies 54
connector pins and reports `193/194 invariants satisfied ...; 1 declared wireless
not_evaluated`, with `NOT_EVALUATED: BLE-RADIO` printed by name. Any other
non-satisfied invariant fails. Logs are under `build/runs/verify-io/telemetry-pod/`.

This is a topology gate only. It does not establish analog accuracy, CAN timing,
firmware assignments, harness destinations, wireless behaviour or fabrication
approval. `verify_io_map.py` in this directory is the retired revision-2 checker;
`io-map-cross-check.txt` and `IO_MAP_HISTORY.md` are historical.

## Citation status (machine-readable)

The AGENTEE-188 compiler can only emit a row's `POD-IF-*` IDs as bare strings in
`io_map.requirements`; its citation schema has no status field. So the generator also
writes `pinout-checks/citations.json` (`fome-mc.pod-io-map-citations/1`). It is bound
to the `io-map.csv` SHA-256 that every contract citation carries. For each cited or
carried row it records the CSV row number, each cited ID and each carried descriptive
value, all with `rev3_qualified: false`, a status and an origin:

- `v9-historical-unqualified`: carried from the v9 pilot row on the same native pin and
  net. The origin gives the v9 `io-map.csv` path, its SHA-256, row number and v9
  `Connector_Pin`. This applies to the 24 carried rows (J1-1..16, J2-1/2, TP1..TP6),
  and to `BLE-RADIO`'s `Signal_Name` and descriptive columns.
- `rev3-declared-obligation`: `BLE-RADIO`'s `POD-IF-BLUETOOTH-LE` and
  `POD-IF-PROGRAMMING-AND-DEBUG`, declared in `source.json`. The origin gives the
  Rev-3 spec-record locator. The row is not evaluated.

Neither status is Rev-3 harness or electrical qualification. `verify-io` joins the
record with every contract citation. It fails if a cited ID has no record entry, if
the entry is stripped or does not match the citation exactly, or if the status is
missing or upgraded, or `rev3_qualified` is not `false`. It also fails if a v9 origin
row does not reproduce (file digest, row, `Connector_Pin`, the cited ID in its Notes,
or the value), if a Rev-3 locator differs from the spec record, or if the record is
stale or missing. Any descriptive value that is not `unknown` must be recorded.

The gate's requirement-coverage line counts only statuses in
`REV3_QUALIFIED_STATUSES` (`scripts/verify_io_map.py`) as Rev-3 evidence. That set is
empty because no Rev-3 qualification record exists. The gate therefore prints
`REQUIREMENT_COVERAGE: 0/11 Rev-3 POD-IF requirements have Rev-3-qualified row evidence;
24 rows carry only v9-historical-unqualified citations; declared, not evaluated:
POD-IF-BLUETOOTH-LE, POD-IF-PROGRAMMING-AND-DEBUG`. The pod compile is run without
`--spec-record`, so the compiler's own coverage count, which reads the bare strings,
is not used. `toolchain/tests/test_project_scripts.py` shows that a consumer reading
the bare strings counts J1-1/J1-2 as `POD-IF-CAN1` coverage, while this consumer does
not. It also checks each strip, upgrade and origin mutation.

*Agent decision (AGENTEE-207, fm-iomap-rev3c), not an owner decision.* **Alternatives:**
extend the agent-ee citation schema (outside this repository, and every interface/1
consumer would change) or drop the inherited IDs (this loses traceability that the
earlier review asked to keep). **Reverse:** delete `citations.json`, its generator
block and `check_pod_citations`; the contract bytes do not depend on them.

## Interface requirement traceability

One row per Rev-3 `Interfaces` entry (spec-record IDs). *Cited rows* carry the ID in
their Notes cell, and the compiled contract repeats it in `io_map.requirements`. All are
carried from v9 rows (`v9-historical-unqualified` in `citations.json`), except
`BLE-RADIO`, which `source.json` declares (`rev3-declared-obligation`). *Uncited rows*
are this agent's reading of native net names and topology. That reading is not a
requirement citation and gives no harness or electrical authority. A cited or uncited
row shows only where the interface lands in the schematic. It does not show that the
requirement is satisfied.

| Interface (spec-record ID) | Cited rows | Uncited rows (agent reading of native names) | Open beyond topology |
| --- | --- | --- | --- |
| CAN1 (`POD-IF-CAN1`) | J1-1, J1-2 | none | timing, termination value, ESD qualification, firmware |
| Bluetooth LE (`POD-IF-BLUETOOTH-LE`) | `BLE-RADIO` (no pin; NOT_EVALUATED) | none | radio range, GATT service, OTA; POD-AC-9 bench test |
| Power in (`POD-IF-POWER-IN`) | J1-3, J1-4 | none | transients, reverse polarity, current budget; J1-3 has no MCU path |
| Sensor supply (`POD-IF-SENSOR-SUPPLY`) | J1-5, 7, 8, 10, 11, 13, 14, 16 | J1-21 (`POD_5V_AUX`), J1-22 (`GND`) | 200 mA budget to be reassessed for Rev-3; reference error |
| Analog inputs (`POD-IF-ANALOG-INPUTS`) | J1-6, 9, 12, 15 | J1-17..20 (`POD_AUX1..4_SIGNAL`) | range, protection, settling, calibration, rate |
| Wheel speed (`POD-IF-WHEEL-SPEED`) | none | J1-23..28 (`POD_WHEEL_*`, `GND`) | sensor type and electrical compatibility |
| Digital tire temperature (`POD-IF-DIGITAL-TIRE-TEMPERATURE`) | none | J1-29..34 (`TIRE_CAN_*`, `POD_TIRE_SUPPLY`, `GND`) | protocol, sensor and harness compatibility |
| Standalone logging (`POD-IF-STANDALONE-LOGGING`) | none | J3-1..10, J3-SH (`SD_*`, `+3V3`, `GND`) | duration, power-loss, media and firmware |
| GNSS antenna (`POD-IF-GNSS-ANTENNA`) | J2-1, J2-2 | none | antenna bias, RF; J2-1 has no MCU path |
| Programming and debug (`POD-IF-PROGRAMMING-AND-DEBUG`) | TP1-1..TP6-1, `BLE-RADIO` (OTA) | none | fixture access, firmware load, OTA |
| Harness connector (`POD-IF-HARNESS-CONNECTOR`) | J1-1..16 | J1-17..35 | plug, contacts, cavity plug and per-cavity harness destinations |

`J1-35` is a proven native no-connect, and its cavity-plug selection is unknown.
`J1-17..34` and `J3` have no committed per-pin source, so their descriptive columns stay
`unknown` and they carry no citation.

## Source packet integrity

`source.json` points into `expansion/storage-microsd/`. That packet's `SHA256SUMS`
lists `native.xml` and `project/telemetry-pod.kicad_prl`, but both match `.gitignore`
patterns and were left out of b6ba9a0. AGENTEE-207 force-added them unchanged from the
ignored copies in the authoring checkout. Those copies were written at
2026-10-21 00:24–00:25 −0700, minutes before b6ba9a0 (00:28). Their bytes match the
listed digests, so nothing was regenerated and the manifest is unchanged. Apart from
its `<source>` path and `<date>`, `native.xml` is identical to a fresh kicad-cli 10.0.7
export of the committed schematic. `sha256sum -c SHA256SUMS` passes in that directory.
