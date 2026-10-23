# Storage stage: microSD socket replaces the eMMC (owner decision 2026-10-21)

Owner, 2026-10-21: "go with the microSD socket, drop the eMMC". The requirements never
named eMMC; the generator's storage stage chose it for the sealed enclosure, and the
BGA-153 then forced zero-margin 0.09 mm geometry, filled via-in-pad and a separate core
regulator. This stage replaces the whole eMMC block with one socket on the four-bit SDMMC
pins the MCU contract already reserves.

**Selected part:** Hirose DM3AT-SF-PEJM5 push-push microSD socket with detect switch,
LCSC `C114218`, JLCPCB extended part, 16,060 in assembly stock at 2026-10-21 07:21 UTC at
USD 1.39 (`stock/catalog.json`, `agent-ee.jlc-catalog/1`). Chosen because KiCad ships its
symbol (`Connector:Micro_SD_Card_Det_Hirose_DM3AT`) and footprint
(`Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5`), so no footprint is authored here.
Rated −25 to +85 °C: an 85 °C exception on the owner's U1/U2/U4 terms (design-rules
D-PCB-12). Datasheet capture is pending: LCSC and Hirose serve the PDF behind HTML
gates; the binding carries the LCSC URL without a byte hash.

## Circuit

- Removed: U14 FEMDME008G and R51–R54 (DAT4–7 pull-ups), R55's eMMC DS pull-down role,
  C63 (VDDi), C66/C67 (VCCQ bypass); the separate core supply U15 TPS62162, L4, C68–C70
  and its power flag; the core-rail supervisor U17 with R58/R59/C73/C74; the core-rail
  diagnostic divider R140–R143/C113 (U28 AIN0 is now a declared no-connect).
  24 components, 13 nets.
- Added: J3. CLK/CMD/DAT0–3 keep the MCU pins (module 31, 32, 33, 34, 35, 24) and the
  10 kΩ pull-ups R46–R50 on CMD/DAT0–3; VDD on +3V3 with C64 4.7 µF and C65 100 nF; VSS,
  detect common (pin 10) and shield on GND; detect (pin 9) is `SD_CD` to GPIO35 (module
  pin 28, formerly the optional storage reset) with R55 10 kΩ pulled up to +3V3.
- No card-side ESD array: the socket is inside the sealed enclosure and the card is
  never handled in service. Add one if a service procedure changes that.

## Decoupling repair (AGENTEE-484, agent-529 decision)

`inputs/intent.json` adds C130 (1 uF, U4 Vdd), C131 (100 nF, U8 V+), C132 (100 nF, U9 V+) and C133
(100 nF, U100 VIO), each on +3V3/GND and reusing an existing part binding (C44 or C38). `inputs/emitter-layout.json`
draws the rebound capacitors with their consumers: C38/C41 with the IMU (U2 VDD/VDDIO), C43/C44 with GNSS
(U10 IN, U3 VCC), C18 with the 5 V reference (U11 Vin). Rebinds do not change the netlist. Per-pin sources:
`../agentee-484-decoupling/dispositions.json`. Emission (agent-ee `f92d71c`, which reproduces the previous
`project/` byte for byte from the previous inputs): 309 components, 235 nets, ERC zero violations.

## Reproduction

`inputs/` is `../released-source-migration/inputs/` with `intent.json` and
`emitter-layout.json` edited as above, `symbols/Connector.kicad_sym` re-captured with
`agent_ee.symbol_capture` (`inputs/microsd-symbol-capture.json`; `symbol-captures.json`
updated), and `footprints/Connector_Card.pretty/` copied from KiCad 10.0.7's library
(`sha256 cc0efdbdb9b21e7cc31a577ea45e753c8985b1c67cf1f58d39e352018f0cb938`). Emission
with released agent-ee `f92d71c`:

```sh
python3 -m agent_ee.schematic_emitter inputs/intent.json --layout inputs/emitter-layout.json \
  --captures inputs --out project --receipt emission-receipt.json
```

`project/` holds the regenerated native schematic, project and library tables;
`native.xml` and `erc.json` are the retained exports (ERC: zero violations at every
severity, against the migration's zero). `verify.py` re-exports both on a temporary copy
and checks the storage contract.

## Downstream

This source supersedes `../released-source-migration/` as the pod's schematic. It changes:
`../allocation.json` (GPIO35 → `SD_CD`), `../design-rules/` (D-PCB-3 and the `BGA_EMMC`
class retired, D-PCB-12 added), `../electrical-locality/pad-obligations/` (the three U15
obligations withdrawn), `../blocks/allocation.json` (storage block = J3 + its passives),
and the placement seed, which must be forward-annotated from this `native.xml` before the
next placement pass. `../part-bindings/` and `../interface-contract/` are earlier stage
outputs and still describe the eMMC source; the J3 binding lives in `inputs/intent.json`.
