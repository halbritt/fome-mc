# fome-mc reference block library: capture plan

Status: plan, 2026-10-17. No block is captured or verified yet. This document
records what each fome-mc sheet would contribute to the generator's library of
verified reference blocks (generator decision 2, see `CHANGELOG.md`), what evidence
exists for it today, and what is missing.

Plane: fome-mc block inventory AGENTEE-105 (rung-2 children AGENTEE-106 PSU,
AGENTEE-107 wideband channel), which feeds the generic block format AGENTEE-89, block
adaptation AGENTEE-90 and the rung-2 run AGENTEE-97; per-sheet boundary contracts
FOMEMC-22; doc defects FOMEMC-23; fab package FOMEMC-21; BOM defects FOMEMC-24.

## Sources of the facts below

- Design: committed `main` at `c582b29` (2026-10-17 10:29). Another session is
  editing `sheets/psu.kicad_sch`, `sheets/stepper_etb.kicad_sch`, `sheets/mcu.kicad_sch`,
  `sheets/wbo1.kicad_sch`, `sheets/wbo2.kicad_sch`, the root sheet and the PCB for
  FOMEMC-17..20. Part values on those sheets will change; capture must
  pin a commit made after those items land.
- Connectivity: a native netlist regenerated from a `git archive` of `c582b29` with
  `kicad-cli 10.0.7 sch export netlist --format kicadsexpr` in a scratch directory
  (sha256 `62e8532e9dd20401c9f749f02aea6e67fb76defc43a9d36a0ec04b90166a5868`; 506
  components, 491 nets). The design's own `export/fome-mc.net` is gitignored
  (`*.net` in `.gitignore`) and the local copy is stale (RN5/RN7/RN9 carry `C15402`
  there, `C29718` at HEAD), so it is not used as evidence here.
- Parts: `export/BOM-fome-mc.csv` at `c582b29`. Where `docs/DESIGN.md` cites a
  different LCSC number, the BOM value is used and the mismatch is listed in
  FOMEMC-23.
- Connector pins: `io-map.csv` joined to the regenerated netlist.
- Boundary: hierarchical labels parsed from each sheet file, plus every net that
  has pins both inside and outside a sheet instance in the netlist.

## How the blocks came to be

fome-mc is itself the model for decision 2. It was assembled from proven circuits,
not drawn part by part (`docs/DESIGN.md` §2 and §3):

| Origin | Revision | Became |
|---|---|---|
| FOME-Tech Polygonus `mcu`, `psu`, `quad_analog*`, `triggers`, `knock`, `etb-9201`, `lowside_quad`, `highside_quad`, `ign4` | `b3176cb` | H7 core, power, analog, triggers, drivers |
| Polygonus-Universal-112 `Keep_Alive`, `IGBT outputs`, `wbo-can-trans` | `ddcf0f7` | keep-alive, ignition IGBTs, WBO CAN |
| mck1117 wideband `board_module/wideband_controller.kicad_sch` Rev C | `ca2adce` | `wbo1`, `wbo2` |
| fome-mc brain-module checkpoint | `c43ad7b` | H7 pin remap, SDMMC1 |

`git log --stat -- sheets/` shows the pattern: the 15 sheet files arrived together
in `f5abd10`, then each review finding was repaired in place (FOMEMC-5 on
`stepper_etb`, FOMEMC-6 on `triggers`, FOMEMC-7 on `psu`/`Keep_Alive`/`stepper_etb`,
FOMEMC-8 on `mcu`, FOMEMC-13/14/15 inside `c582b29`). That is "copy a proven block,
then adapt it through a repair campaign", which is the generator's intended flow.

The upstream licences matter for any reuse outside fome-mc: the wideband repository
is MIT (Matthew Kennedy, 2023). The local Polygonus and Polygonus-Universal-112
checkouts contain no top-level licence file, and fome-mc has none. Publishing a
block library derived from them needs an owner decision first.

## Sheet instances

The root sheet instantiates 15 files as 21 sheet instances (root included):

| Instance | File | Parts | Notes |
|---|---|---|---|
| `/` | `fome-mc.kicad_sch` | 4 | J1, J2 (AMPSEAL), C1 bulk, R219 |
| `/psu/` | `psu.kicad_sch` | 39 | power plus both CAN transceivers |
| `/Keep_Alive/` | `Keep_Alive.kicad_sch` | 10 | diode-OR, VBAT LDO |
| `/mcu/` | `mcu.kicad_sch` | 82 | 81 hierarchical pins |
| `/wbo1/`, `/wbo2/` | `wbo1.kicad_sch`, `wbo2.kicad_sch` | 58 each | two files, not two instances of one file |
| `/ign_igbt/` | `ign_igbt.kicad_sch` | 12 | IGBTs only |
| `/ign1/`, `/ign2/` | `ign4.kicad_sch` | 16 each | ign1 drives the IGBT gates, ign2 the logic outputs |
| `/lowside_quad1/`, `/lowside_quad2/`, `/lowside_quad4/` | `lowside_quad.kicad_sch` | 6 each | no `lowside_quad3` |
| `/highside_quad/` | `highside_quad.kicad_sch` | 14 | outputs not connected to J1/J2 |
| `/quad_analog1..3/` | `quad_analog.kicad_sch` | 20 each | |
| `/quad_analog_temp/` | `quad_analog_pullup.kicad_sch` | 21 | |
| `/triggers/` | `triggers.kicad_sch` | 43 | |
| `/knock/` | `knock.kicad_sch` | 24 | |
| `/stepper_etb/` | `stepper_etb.kicad_sch` | 26 | DRV8825, second TLE9201, clamp diodes, BOOT0 network |
| `/etb1/` | `etb-9201.kicad_sch` | 5 | one instance only; U203 is drawn inline in `stepper_etb` |

## What "verified block" means

Under agent-ee's model a block counts as verified only when all of these exist and
are bound to one hash:

1. Captured native files: the sheet file(s), the symbols they embed, the footprints
   they reference (project-local `libs/footprints/*.pretty`, the shared
   `kicad-libraries` at `ab9c5f8`, or KiCad 10.0.7 stock), each with sha256.
2. A boundary contract in `agent-ee.interface/1` form (`docs/hardware-interface.md`
   in agent-ee): the hierarchical pins, rails and connector pins as `named_net`,
   `same_net` and `different_net` invariants, with key parts as `component` and
   `value` invariants. agent-ee's contract already addresses components by sheet
   instance path, so hierarchy is supported.
3. Requirements with sources (DESIGN.md sections, datasheet pages through AGENTEE-18),
   including operating conditions, in an `agent-ee.scope/2` baseline whose check set
   is fixed before the first run.
4. Check results on that baseline: ERC, native netlist, `hardware_interface`,
   simulation where a requirement is numeric, kicad-happy (AGENTEE-17) as a
   supplement, and parts checks (AGENTEE-29/30/31) once they exist. Tool failure is
   missing coverage, not a pass.
5. Independent review and adjudication gated on that tool evidence.
6. For layout reuse (AGENTEE-56): the block's footprints, tracks, vias and zones
   extracted from `fome-mc.kicad_pcb` as a sub-board, with geometry probe results.

Today no fome-mc block has items 2, 3, 5 or 6, and item 4 exists only at board
level. Item 1 is possible now.

## Evidence that exists today (board level)

| Evidence | State |
|---|---|
| `scripts/verify_io_map.py` | Tracked. README reports PASS (70 pins + 22 buses). No committed run output. |
| ERC/DRC/parity (`make check`) | README reports 0 errors. No committed result for `c582b29`; the committed baseline in `reports/toolchain/baseline/` is at `36db604`, before most of the design. The latest local run (working tree at `07f8d8c` plus 9 uncommitted files, under the ignored `build/`) shows 0 errors but 2087 ERC warnings and 473 DRC warnings, 199 of them `lib_footprint_mismatch`. |
| kicad-happy (`make analyze`) | Local run only: 40 schematic and 33 PCB findings at error severity, not adjudicated. Many are false alarms (for example VM-001 on TJA1051T/3, which has a VIO pin), some need a look (PP-001 on U26 VBAT and U41 IN). |
| Simulation | None per block. `make smoke` covers the RC fixture only. |
| Routing | `reports/toolchain/routing/fome-mc/verify-216eb9a/` (committed): independent check of the FOMEMC-10 routing, which found the relaxed `min_resolved_spokes` rule (FOMEMC-11). |
| Independent review | FOMEMC-5..20 came from agent-ee adversarial reviews of the whole board. Their packets and verdicts are not stored in this repository. |

## Block catalogue

Boundary lists name nets as they appear in the netlist. "J" pins are the AMPSEAL
pins from `io-map.csv`. GND is shared by every block and is not repeated.

### Power supply (`psu.kicad_sch`, without CAN)

- Boundary in: `/12V_RAW` (from Keep_Alive). Out: `+5V`, `+3V3`, `/5V_SENSOR_1`
  (J1-29), `/5V_SENSOR_2` (J1-30), `/VBOOST` (to the MCU divider),
  `5V_SENSOR_1_PG`, `5V_SENSOR_2_PG` (to U26). Hierarchical label `12v_PROT` exists
  but is not used at the root.
- Key parts: D1 SMCJ24A `C224045`; Q1 AO4485 `C51499` with D19 BZT52C12 `C43491`
  and R124 47k `C25819` (reverse block); L1 2.2 µH `C75646` and C6 47 µF hybrid
  polymer `C454346` (input filter); U3 LMR16020PDDAR `C190006` with L2 10 µH
  `C408412`, D3 `C8678`, R5/R6 12k/68k (5.00 V); U1, U2 TLS115D0E `C3747428`
  (sensor supplies, fed from `/12V_PROT`); U6 TLV75733PDBVR `C485517` (+3V3 from
  +5V); C12 10 µF `C96446`.
- Requirements (DESIGN.md §3 and §6.3): survive load dump with the TVS clamp at
  38.9 V; reverse-battery block without a series diode drop; +5V = 5.00 V ± 2 % above
  5.5 V input; `5V_SENSOR_1/2` = 5.00 V ± 1 %; +3V3 = 3.30 V ± 1 %; regulation down
  to the connector brownout floor. FOMEMC-17 is changing the floor statement: 4.0 to
  4.2 V is the typical UVLO, the guaranteed loaded floor is 4.65 to 4.8 V.
- Evidence today: board-level ERC/DRC only. Real findings already raised on this
  block: TVS clamp above downstream limits (FOMEMC-7), C12 value/part mismatch
  (FOMEMC-15), C4 16 V on the 12 V rail (FOMEMC-17, in flight), brownout margin
  (FOMEMC-17).
- Missing: contract; requirements with datasheet citations (LMR16020 UVLO and
  minimum VIN, TLS115D0E tracking, SMCJ24A clamp); a load-dump and cranking
  simulation (needs AGENTEE-19 active models; the LC filter alone fits
  `rc_transient`); capacitor voltage-derating check (AGENTEE-61 with catalog data
  from AGENTEE-27); independent review.
- Adaptation parameters: output voltage (R5/R6), input range and TVS part, sensor
  supply count, 3V3 load, whether the reverse block is present, bulk capacitance.

### Keep-alive (`Keep_Alive.kicad_sch`)

- Boundary in: `/12V_IGN_SW` (J1-26, also sensed by the MCU), `/12V_MR` (J1-24,
  J1-27), `/Perm_Live` (J1-28). Out: `/12V_RAW`, `/Keep_Alive/Keep_Alive` (to U26
  VBAT path).
- Key parts: D20, D21 B340A-13-F `C64982` (diode-OR); D22 SMCJ24A `C224045`; U41
  MIC5205-3.3YM5 `C5370979`; IC1 PSM712 `C32677`; D16, D17 B5819W `C8598`.
- Requirements: key-off detection while `/12V_MR` holds `/12V_RAW`; VBAT backup from
  `Perm_Live`. Bench items in VALIDATION.md §3.
- Missing: everything after capture. The main-relay hold also depends on
  `lowside_quad4` (U1202) and the MCU (PE0), so its behavioural requirement spans
  three blocks; the contract must say so.
- Adaptation: whether a main relay exists, battery-backup need.

### MCU core (`mcu.kicad_sch`)

- Boundary: 81 hierarchical pins. Rails in: `+3V3`, `+5V` (VREF source),
  `/12V_MR`, `/12V_IGN_SW` (sense), `/VBOOST`. External: `/USB_D+` (J2-34),
  `/USB_D-` (J2-35). Everything else is internal to the board: AV1..AV11, AT1..AT4,
  DIGITAL1..6, VR_1/2, LS1..LS16, IGN1..8, HS1..4, ETB1/2, CAN, WBO1/2 NRST/BOOT0,
  knock FILTERED_1/2.
- Key parts: U26 STM32H753ZIT6 `C730207`; Y1 8 MHz `C115962`; U23 REF3333 `C130016`;
  U25 CSNP32GCR01-AOW `C2841139` with R127..R131 47k and R132 22 Ω; U29
  ATWINC1500-MR210UB `C1558703`; U27 USBLC6-2SC6 `C111212`; U24 LPS25HB `C87898`
  (DNP). Bench parts without LCSC numbers: BT1, J8, J9, J11..J16.
- Requirements: DESIGN.md §3 row 2 and §6.3.4 (fixed 3.30 V VREF+, non-ratiometric
  ADC), SDMMC1 bus termination, DFU entry via BOOT0.
- Evidence today: FOMEMC-8 (SDMMC pull-ups), FOMEMC-18/19 (U29 land pattern,
  U29 and U25 decoupling) are in flight.
- Missing: contract (the pin map is the contract, and `io-map.csv` already holds most
  of it), datasheet pin contracts (AGENTEE-59), land-pattern check (AGENTEE-31).
- Adaptation: the MCU pin map. This is the hardest block to adapt and the least
  suitable for rung 2.

### CAN (inside `psu.kicad_sch`)

- Boundary in: `/mcu/CAN_TX`, `/mcu/CAN_RX`, `/mcu/CAN2_TX`, `/mcu/CAN2_RX`, `+5V`.
  Out: `/CAN+` (J2-28), `/CAN-` (J2-29), `/CAN2+`, `/CAN2-` (to U307/U407 in the
  WBO blocks).
- Key parts: U4, U5 MCP2551-I-SN `C7376`; D4, D5 PESD1CAN-UX `C907839`; R9, R10
  120 Ω terminations; R7, R8 10 Ω on Rs. The BOM binds R7/R8 (10 Ω) and R9/R10 (120 Ω)
  to the same LCSC number `C22787` (FOMEMC-24).
- Requirements: 500 kbps; one termination per bus end (DESIGN.md §3 row 1: 60 to
  120 Ω bus resistance); Vref pin 5 left open (fixed in `7c3806c`).
- Missing: everything after capture. Capture as its own block by instance and
  reference set; moving it to its own sheet is a design change for later.

### Wideband channel (`wbo1.kicad_sch`, `wbo2.kicad_sch`)

- Boundary (10 hierarchical pins per channel): in `+5V`, `/12V_MR` (as
  `12V_SENSE`), `/WBOn_NRST`, `/WBOn_BOOT0` (from U26 PD4..PD7); bus `/CAN2+`,
  `/CAN2-`; sensor `/WBOn_VM`, `/WBOn_IP`, `/WBOn_RTRIM`, `/WBOn_UN` (J2-19..22 for
  WBO1, J2-30..33 for WBO2); heater low side `/WBOn_H-` (J1-23 / J1-25). Heater
  supply comes in on J1-24 (`/12V_MR`). Local rails `+3V3_WBOn` (U309) and
  `VDDA_WBOn` (U303) are power symbols with per-channel names.
- Key parts per channel (WBO1 references; WBO2 is +100): U302 STM32F042K6T6
  `C69216`; U301 MCP6004 `C50282`; U305 AD8628 `C29309`; U303 REF3033 `C36658`;
  U309 XC6206P332MR `C5446`; Q301 VND14NV04 `C2649436`; U307 TJA1051T/3 `C38695`;
  R310 61.9 Ω `C23092` (pump-current shunt).
- Requirements (DESIGN.md §3 row 3 and §5): 1.65 V virtual ground, Nernst ESR
  injection, 500 kbps CAN at 0x190/0x191 (WBO1) and 0x192/0x193 (WBO2) set by the
  PB1/PA8 straps, heater PWM under CAN control, separate VDDA per channel.
- Evidence today: the upstream Rev C design is an independent oracle. The two
  channels are a ready-made adaptation pair: after mapping U3xx to U4xx, the only
  connectivity differences are the straps (WBO1: U302 pin 15 PB1 to GND, pin 18 PA8
  open; WBO2: U402 pin 18 PA8 to `+3V3_WBO2`, pin 15 open) and the channel suffix in
  net names. Values, LCSC numbers and footprints are identical.
- Missing: contract; requirement sources (wideband firmware `port.cpp` for the
  strap decode, LSU 4.9 datasheet); active simulation of the pump-current loop
  (AGENTEE-19); thermal copper for Q301 as a geometry requirement; independent
  review.
- Adaptation: channel index (strap pattern and CAN IDs), reference offset, net
  suffix, connector pins, heater supply source.

### Ignition IGBT (`ign_igbt.kicad_sch` with `/ign1/`)

- Boundary in: `/IGN1..4` from `/ign1/` (MIC4427 outputs). Out: `/IGN1_COIL` ..
  `/IGN4_COIL` (J1-6..9). The gate drivers U42, U43 are in the `/ign1/` instance of
  `ign4.kicad_sch`, so the IGBT block is two instances: `/ign1/` (U42, U43, with
  inputs `/ign1/IN1..4` from U26) plus `/ign_igbt/`.
- Key parts: Q201..Q204 FGD3040G2-F085 `C606124`; R201..R204 15 Ω gate;
  R205..R208 10k gate-emitter; U42, U43 MIC4427 `C171845`.
- Requirements: 0 V gate during MCU reset; 400 V clamp on coil turn-off;
  HV clearance on collector copper (FOMEMC-16 rule areas, FOMEMC-19 in flight);
  1.2 mm coil traces.
- Missing: HV netclass as a captured rule (FOMEMC-19), clearance check
  (AGENTEE-47/63), contract, review.
- Adaptation: channel count, IGBT part, clearance class.

### Logic ignition (`/ign2/`, `ign4.kicad_sch`)

- Boundary in: `/ign2/IN1..4` from U26, `+5V`. Out: `/IGN5..8` (J2-23..26).
- Key parts: U44, U45 MIC4427 `C171845`; R112..R115 100 Ω series.
- Note: README and DESIGN.md name these drivers U9/U10; in the netlist U9/U10 are
  SN74LVC2G17 Hall buffers (FOMEMC-23).

### Low-side quad (`lowside_quad.kicad_sch`, three instances)

- Boundary in: `INn` from U26, `+5V`. Out: `/LS1..4` (J1-1..4, injectors),
  `/LS5..8` (J1-10..13), `/LS14` (J2-27 DASH_TECH), `/MAIN_RLY` (J1-14).
  `/LS13` and `/LS16` go nowhere.
- Key parts per instance: two VNLD5090 `C222209`, one 74HCT125D `C5947`, RN 10k
  pull-down array, RN 1k series array, 100 nF.
- Cross-block nets the contract must name: the flyback diodes D201..D209 and the
  R212 pull-up for `/LS8` live in `stepper_etb.kicad_sch`, not here. In
  `/lowside_quad4/`, IN1 is `/PB8_STEP_EN`, the same U26 pin (PB8) that drives the
  DRV8825 nENBL; it buffers into U1201 channel 2, whose output `/LS13` is not
  connected, and RN9 holds PB8 low (driver enabled) while U26 is in reset. Whether
  that shared pin is intended is an open question for the contract (FOMEMC-22).
- Requirements: 5 V gate drive (FOMEMC-13), 42 V active clamp, injector channels
  without external freewheel diodes (FOMEMC-17, in flight).
- Adaptation: channel use (injector, relay, tach, serial), clamp choice.

### High-side quad (`highside_quad.kicad_sch`)

- Boundary in: `/highside_quad/IN1..4` (HS1..4 from U26), `/12V_MR`, `+3V3`.
  Outputs OUT1..4 are not connected to the connectors: README calls U40 a spare.
- Key parts: U40 BTS716G `C85135`.
- A block with no connector-facing output is a poor library entry until a
  requirement uses it.

### Quad analog (`quad_analog.kicad_sch`, three instances) and pull-up variant (`quad_analog_pullup.kicad_sch`)

- Boundary in: `/AVn` from J2 (J2-3..8 on instances 1 and 2), `+5V`. Out:
  `/mcu/AVn`. The pull-up variant adds `5V_PULLUP_SUPPLY` (`/5V_SENSOR_1`) and
  serves J2-1, J2-2 (CLT, IAT).
- Key parts per instance: MCP6004 `C50282`, SRV05-4 `C85364`, 470k/5.6k/10k
  networks, 100 nF; pull-up variant uses 2.7 kΩ `C13167`. R219 1.5 kΩ (gear input
  pull-up, FOMEMC-14) sits on the root sheet, not in the block.
- Requirements: 0 to 5 V input range scaled to the 3.30 V ADC, ESD on every input,
  gear-ladder voltages (DESIGN.md §4.4).
- Evidence: `rc_transient` already fits the input filters (ideal passives).
- Adaptation: divider ratio, pull-up value, filter corner.

### Triggers (`triggers.kicad_sch`)

- Boundary in: `/VR1+`, `/VR1-`, `/VR2+`, `/VR2-` (J2-11..14), `/DIGITAL_1..4`
  (J2-15..18), `/5V_SENSOR_1`, `+5V`, `+3V3`. Out: `/mcu/VR_1`, `/mcu/VR_2`,
  `/mcu/DIGITAL1..6`.
- Key parts: U13, U14 MAX9924UAUB+ `C143633`; U8..U10 SN74LVC2G17DB `C10429`;
  U11, U12 SRV05-4.
- Requirements: Mode A1 adaptive threshold, 50 mVpp to 100 Vpp input (DESIGN.md §3
  row 6), differential input (FOMEMC-6).

### Knock (`knock.kicad_sch`)

- Boundary in: `/KNOCK_1`, `/KNOCK_2` (J2-9, J2-10), `+3V3`. Out:
  `/knock/FILTERED_1`, `/knock/FILTERED_2`.
- Key parts: U7 MCP6004; C16, C17 3.3 nF `C472819`; band-pass resistor network.
- Requirements: pass band and gain for ADC3 sampling. A good active-SPICE target
  once AGENTEE-19 lands.

### Stepper/ETB (`stepper_etb.kicad_sch`)

- Boundary: 26 hierarchical pins. DRV8825 (U202 `C50506`) with STEP on `/LS9`,
  DIR on `/LS12`, nENBL on `/PB8_STEP_EN`, outputs `/STEP_1A..2B` (J1-19..22);
  the second TLE9201SG (U203) with `/ETB2_*` (J1-17, J1-18); flyback diodes D201..D209
  for the low-side channels; the J1-35 DFU network (D210, R209, R217, R218, D211).
- This sheet mixes four unrelated functions. Capture it as four blocks by reference
  set (stepper, H-bridge, clamp diodes belonging to the low-side blocks, DFU entry)
  and treat splitting the file as a later design change.
- Current-limit check: R215 33k from `+3V3` and R216 10k to GND give VREF =
  0.767 V; with R213/R214 = 0.20 Ω, I = VREF / (5 × R) = 0.77 A, matching the 0.75 A
  target in FOMEMC-5. README and `io-map.csv` still say 0.33 Ω and VREF = 0.38 V,
  which would give 0.23 A (FOMEMC-23).

### H-bridge (`etb-9201.kicad_sch`)

- Boundary in: `12V_SUPPLY` (`/12V_MR`), `PWM`, `DIR`, `DIS` (`/ETB1_*` from U26),
  `+3V3`. Out: `/ETB1_OUT+`, `/ETB1_OUT-` (J1-15, J1-16).
- Key parts: U201 TLE9201SG `C112633`, C1201 2.2 µF.
- The only multi-use candidate in the TLE9201 family: U203 repeats the circuit
  inline in `stepper_etb`. A second instance of this file would replace it.

## Capture format (proposal for agent-ee)

AGENTEE-89 defines `agent-ee.block/1` (a directory with `block.json`, the sheet, an
optional sub-layout, a parts subset, provenance, requirements and references to
sealed runs). The table lists what fome-mc needs that format to hold; the
`interface`, requirement sources and multi-instance reference sets are the parts
not yet spelled out there.

| Field | Content |
|---|---|
| `source` | repository, full commit, instance path(s), reference set |
| `files` | sheet file(s) and every referenced footprint and symbol library file, with sha256 and origin (project-local, `kicad-libraries@ab9c5f8`, KiCad 10.0.7 stock) |
| `interface` | an `agent-ee.interface/1` contract: one `named_net` invariant per hierarchical pin and connector pin, `component`/`value` invariants for the parts the requirements depend on |
| `requirements` | ids, statements, operating conditions, sources (DESIGN.md section, datasheet page via AGENTEE-18) |
| `scope` | the `agent-ee.scope/2` baseline: check set and `baseline_id` |
| `parts` | LCSC number per reference and the catalog snapshot hash (AGENTEE-27) |
| `layout` (optional) | sub-board extracted from `fome-mc.kicad_pcb` plus geometry probe output (AGENTEE-56) |
| `evidence` | agent-ee run ids, check results, reviewer and adjudicator outcomes, tool versions |

The block identity is the sha256 of the canonical manifest without `evidence`.
Evidence binds to that identity; changing a file, contract, requirement or check
specification produces a new identity with no evidence. This is the same rule
AGENTEE-46 states for blocks inside one design.

Adaptation (AGENTEE-90) is a repair campaign on a copied block (decision 1): copy the block's
files into an empty candidate, rename references and nets by the adaptation
parameters, change the requirement parameters, and let the writer, checks,
reviewers and adjudicator run as for any repair. The copy inherits the check set
and the contract structure, not the verdicts. `wbo1` to `wbo2` is a worked example
whose expected diff is known (above).

## Rung-2 candidates

Rung 2 is one fome-mc sheet run end to end. Two blocks qualify:

1. **PSU** (`psu.kicad_sch` power part, with `Keep_Alive.kicad_sch` as the source of
   `/12V_RAW` or a connector in its place). It has numeric requirements with
   datasheet sources, a short boundary (one input, five outputs), and five real
   findings already raised against it, which double as seeded defects. It needs no
   firmware to judge. Costs: FOMEMC-17 is editing it now, the CAN transceivers share
   the file, and the buck regulator needs a vendor model for any transient claim.
2. **One wideband channel** (`wbo1.kicad_sch`). It has a 10-pin boundary, an
   independent upstream reference (Rev C, MIT), a known adaptation pair (`wbo2`), and
   it is the core of rung 3 (standalone wideband controller). The working tree shows
   FOMEMC-20 wiring cleanup on `wbo1`/`wbo2` now, so capture also waits for that
   commit. Costs: functional proof needs firmware and active models; static
   checks (ERC, contract, parts, land patterns, layout geometry) do not.

Not rung 2: the MCU core (81 pins, LQFP-144, whole-board context), `stepper_etb`
(four functions), `highside_quad` (no connector-facing output).

agent-ee's seeded benchmark harness (AGENTEE-21) refuses hierarchical designs. A
block captured as a standalone root schematic avoids that, so rung-2 capture also
unblocks fome-mc seeds (`docs/SEEDED_DEFECT_BENCHMARK.md`).

## Fab package for rung 4

README.md (repository tree, line 177, and the status table, line 210) describes
`export/gerbers/` with Gerbers, drills, a job file and `fome-mc-gerbers.zip`,
produced by `make export`. None of it is committed: only `export/BOM-fome-mc.csv`
and `export/CPL-fome-mc.csv` are tracked, and `export/fome-mc.net` is ignored.
`make export` writes the KiBot bundle under the ignored
`build/runs/project/fome-mc/<stamp>/export/kibot/`, nothing writes to
`export/gerbers/`, and nothing produces the zip. No tracked script produces the
committed BOM or CPL either.

So rung 4 has no reference fab package to compare against. Its baseline must be
regenerated from a pinned commit with pinned tools (KiCad 10.0.7, KiBot 1.9.1) and
recorded as hashes, before or alongside the generator's own fab stage (AGENTEE-23,
AGENTEE-73, AGENTEE-74). The current BOM and CPL also disagree: the BOM lists C1 and
C6 (47 µF, `C454346`) but the CPL has no rows for them, and nine BOM lines carry no
LCSC number (BT1, debug and USB connectors, solder jumpers). FOMEMC-21 covers the
regeneration, FOMEMC-24 the BOM and CPL defects.
