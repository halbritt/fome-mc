# Pod I/O map and compiled contract (Rev-3)

`io-map.csv` describes the Rev-3 pod source schematic
`expansion/storage-microsd/project/telemetry-pod.kicad_sch` (SHA-256
`4da27afc8d9cd7ff3d1fd8e23f855747072c050d25601b89fb3909b688e49f23`, 305 references,
the microSD source that `expansion/production-capture/` binds). The schematic at the
project root is still the v9 pilot snapshot. Its former map, bindings, paths and
contract are kept unchanged in [`pinout-checks/v9-pilot/`](pinout-checks/v9-pilot/README.md).

## Derivation

`pinout-checks/generate.py` writes `io-map.csv`, `pinout-checks/bindings.json`,
`pinout-checks/paths.json` and `pinout-checks/history.json` from a kicad-cli XML netlist of the schematic named in
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
  record. The Notes cell says so, and the compiled contract and its qualification
  record carry it (see *Qualification record* below). These values were not
  requalified for Rev-3. Every other row says `unknown`. No committed packet gives
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

fome-mc pins no agent-ee. `verify_io_map.py` and the compile use the `agent-ee` CLI on
PATH. They ask that CLI's own interpreter where `agent_ee` lives, import the evaluator
and loader from there, and compile with that interpreter's `python -m agent_ee.io_map`
(the CLI has no io-map subcommand). The CLI's source must be a clean git checkout (or
an install that records its VCS commit), so the compiler identity is exact.

The compiler identity is provenance. `contracts/telemetry-pod.compile-receipt.json`
(`fome-mc.pod-contract-compile/1`) records it:

- the agent-ee commit, distribution version and module digests (`io_map.py`,
  `hardware_interface.py`, `symbol_library.py`);
- the exact arguments, and the input and output digests.

It is written only by the compile path, alongside the contract and record. The current
receipt records agent-ee `e906c9c7546043e75e45009de5bc08990c470e93`, the AGENTEE-188
compiler and qualification-record loader that agent-521 accepted (35ff0e93). That
commit is not on agent-ee main yet. Before fome-mc lands, regenerate with the landed
agent-ee main (which contains e906c9c7) on PATH, so that the receipt records that SHA.
An agent-ee on PATH without the AGENTEE-188 loader fails verify-io, naming the
checkout and commit it found.

From the repository root, with the intended agent-ee first on PATH:

```sh
python3 telemetry-pod/pinout-checks/generate.py                 # or --check to compare only
python3 scripts/verify_io_map.py --project telemetry-pod --compile # contract, record and receipt
make verify-io PROJECT=telemetry-pod
```

`--compile` runs, with the CLI's interpreter, `python -m agent_ee.io_map
telemetry-pod/io-map.csv --csv-path telemetry-pod/io-map.csv --requirement
POD-AC-1-pinout --source telemetry-pod/REQUIREMENTS.md --locator 'Acceptance criteria /
item 1' --require-source-sha256 --bindings telemetry-pod/pinout-checks/bindings.json
--paths telemetry-pod/pinout-checks/paths.json --history
telemetry-pod/pinout-checks/history.json --history-source
telemetry-pod/pinout-checks/v9-pilot/io-map.csv --record-path
contracts/telemetry-pod.qualification.json --record-out … --out …`. It then writes the
receipt.

The contract and its record are generated, never hand-edited. The contract has 194
invariants: 193 wired ones (78 indirect paths) and the unresolved `BLE-RADIO:net`.
Their predicates, terminals and components are unchanged from the earlier bare-ID
contract. Only the `io_map` citations (now typed) and the `qualification_record`
declaration changed. Each invariant binds `REQUIREMENTS.md` (revision 3) by SHA-256.

`make verify-io PROJECT=telemetry-pod` fails on any of these:

- the source digest differs, or `generate.py --check` does not reproduce;
- a fresh compile with the agent-ee on PATH does not reproduce the contract, the
  record and the compile receipt byte for byte; in particular, a receipt that names
  another agent-ee commit fails;
- the contract is not accepted by agent-ee's `capability()` under a scope that pins
  `contracts/telemetry-pod.qualification.json`;
- the history checks below fail;
- either native grading run below has a non-satisfied invariant other than
  `NOT_EVALUATED: BLE-RADIO`.

The native grading runs twice. It runs on a fresh netlist of the canonical source, and
on the actual candidate pinned in `source.json` `candidate`. Each run must report
`193/194 invariants satisfied ...; 1 declared wireless not_evaluated`. Logs are under
`build/runs/verify-io/telemetry-pod/`.

This is a topology gate only. It does not establish analog accuracy, CAN timing,
firmware assignments, harness destinations, wireless behaviour or fabrication
approval. `verify_io_map.py` in this directory is the retired revision-2 checker;
`io-map-cross-check.txt` and `IO_MAP_HISTORY.md` are historical.

## Qualification record (AGENTEE-188)

`generate.py` writes `pinout-checks/history.json` (`agent-ee.io-map-history/1`), the
compiler's history input:

- **Origin:** the v9 io-map. Its path is the retained
  `pinout-checks/v9-pilot/io-map.csv`, and its sha256 is
  `be690c01194f2f77e9f3079e1e26d868d0d679c659c53afa457e4feb855b40ea`. Its revision
  is `36b19506e22a3d59e14b325f64c16e14e12ba3f1`: those bytes were committed there as
  `telemetry-pod/io-map.csv` (FOMEMC-32), then moved unchanged by `72b18901`. The
  generator checks that the bytes at that revision equal the retained file.
- **Per-row locators:** each of the 25 carried rows (J1-1..16, J2-1/2, TP1..TP6 and
  `BLE-RADIO`) gets its own locator, for example `row 2 (AMPSEAL-1): carried
  Direction_Class, Voltage_Current_Domain, External_Destination, POD-IF citations; not
  requalified for Rev-3`.
- **Other rows:** the compiler gives every compiled row an origin, so the other 30
  rows get the origin's default locator. It states that no v9 row was carried, so the
  origin supplies nothing to those rows.
- **`sourced` is empty:** no ID is promoted.

The compiler writes every cited ID as `{"id": ..., "qualification":
"unqualified-carryover"}`. It emits `contracts/telemetry-pod.qualification.json`
(`agent-ee.io-map-qualification/1`) and declares that record's path and sha256 in the
contract. The 8 carried IDs are `POD-IF-ANALOG-INPUTS`, `-BLUETOOTH-LE`, `-CAN1`,
`-GNSS-ANTENNA`, `-HARNESS-CONNECTOR`, `-POWER-IN`, `-PROGRAMMING-AND-DEBUG` and
`-SENSOR-SUPPLY`.

`verify-io` reads the contract only through agent-ee's `capability()`, with a scope
that pins the record. That runs the one loader (`load_qualification_record` and
`bind_qualification_record`), which:

- refuses a contract that does not declare the pinned record, or a record whose
  bytes differ from the pin;
- refuses a citation that differs from its record row (status, IDs, signal,
  destination), and a record row that differs from the captured CSV;
- refuses v9 origin bytes that differ from the declared sha256, and reports the
  origin `verified` only when they match.

The gate prints `QUALIFICATION: ... bound to 55 io-map rows; v9 origin ... verified`
and `REQUIREMENT_AUTHORITY: sourced: none; unqualified-carryover (reported, never
authority): ...`.

Two fome-mc checks stay on top of the loader, because the loader authenticates the
origin bytes but does not open the origin row:

1. Every located row must reproduce its v9 row: the row number and `Connector_Pin`,
   each carried column value, and every cited ID present in that row's Notes.
2. A row under the default locator may carry no ID, and may have no descriptive value
   other than `unknown`, `N/A` or the N/C template.

Separately, any `sourced` ID fails. No Rev-3 qualification source is committed, so
`sourced` would be an upgrade.

`toolchain/tests/test_project_scripts.py` builds a consistent bundle (contract,
record and pin all agree) that promotes `POD-IF-CAN1` on J1-1/J1-2 to `sourced`.
agent-ee's loader accepts that bundle, and its authority lists `POD-IF-CAN1` as
sourced. This verifier refuses it. A fresh compile would also differ. The tests also
check these cases:

- the rev3c bare-ID contract cannot stand in for the bound one;
- citation loss, a contract-only upgrade, a record-only upgrade, a stripped record
  row, a stripped declaration, a deleted record and a rewritten origin digest each
  refuse in the loader;
- a moved or removed v9 locator refuses in the fome-mc history check.

*Retired from rev3c (fm-iomap-rev3c, bb58520):* `pinout-checks/citations.json` and its
`fome-mc.pod-io-map-citations/1` schema, the `v9-historical-unqualified` and
`rev3-declared-obligation` statuses, the `rev3_qualified` flag, `check_pod_citations`,
`pod_requirement_coverage`, `REV3_QUALIFIED_STATUSES` and the `REQUIREMENT_COVERAGE`
line. The accepted record, loader and `requirement_authority` replace them. BLE-RADIO's
two IDs are now `unqualified-carryover`, the same as the v9 `BLE-RADIO` row that cites
them. This is not an upgrade.

## Decision note: candidate-bound verification

*Agent decision (AGENTEE-207, fm-iomap-rev3c round 4), not an owner decision.*

- **What:** `source.json` `candidate` pins the actual emitted pod candidate. That is
  pod-capture-j6b2 commit `5d923c5412d3659638c67c9cfa9f097e24620518`, project
  schematic `telemetry-pod/telemetry-pod.kicad_sch` with sha256
  `f5840ecc8a44a2e36cd05da9c3a14d80074919f441c3ef73a107dc98d5aea6a2`, and
  `candidate_id` `3688390f4b30506f2c32af4550c10c53bd9f0205433d8126b012702939704928`.
  The pin is bound to that emission's `MANIFEST.json` digest, its candidate id and
  its installed schematic digest. verify-io grades the same contract on a fresh
  netlist of that candidate. It reads the candidate in place once the project root
  holds those bytes, and otherwise snapshots the commit (`eda.make_snapshot` with
  `rev`). The snapshot's schematic must equal the pinned digest.
- **Why:** canonical-source agreement does not show that the emitted candidate
  consumes the intent. The candidate has the same 305 references, sheet paths,
  symbols and values as the canonical source, and identical nets on all 931 pins.
- **Also changed:** `fresh_inventory` now parses only the design's own sheet
  hierarchy (`schematic_files`), as agent-ee's native check does (`verified_hierarchy`).
  Before, it parsed every `*.kicad_sch` under the snapshot. The candidate project keeps
  retained copies of the same emitted schematic under `expansion/`, so J1's symbol UUID
  was ambiguous and J1-35's no-connect stayed unknown. The ECU result is unchanged.
- **Not claimed:** this is topology agreement of the candidate's schematic with the
  intent. It is not j6 electrical acceptance or production qualification. The
  AGENTEE-188 software acceptance is not that either.
- **Reverse:** drop `candidate` and `pod_candidate_config`. When j6 lands, keep the
  pin: the root then holds the candidate and verification runs in place.

## Interface requirement traceability

One row per Rev-3 `Interfaces` entry (spec-record IDs). *Cited rows* carry the ID in
their Notes cell, and the compiled contract repeats it in `io_map.requirements`. All are
carried from v9 rows and compiled as `unqualified-carryover`, bound to their v9 rows
through the qualification record. `BLE-RADIO`'s two IDs are declared in
`source.json` and are also cited by the v9 `BLE-RADIO` row. *Uncited rows*
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
