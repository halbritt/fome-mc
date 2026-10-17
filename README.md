# `fome-mc` — Integrated FOME-Native Motorcycle ECU

`fome-mc` is a compact (`162.0 mm × 115.0 mm`), 4-layer, single-PCB, pottable motorcycle ECU combining an **STM32H753ZIT6** main processor, **dual onboard STM32F042K6T6 Bosch LSU 4.9 wideband controllers** (`wideband_controller` Rev C over internal `CAN2`), **4× 400 V / 30 A ignition IGBTs** (`FGD3040G2-F085C`) + **4× 5 V logic ignition outputs** (`MIC4427`), **8× protected low-side drivers** (`VNLD5090TR-E`), **dual 6 A H-bridges** (`TLE9201SG`) + **onboard bipolar stepper driver** (`DRV8825PWPR`), **dual adaptive VR conditioners** (`MAX9924UAUB+`), **soldered 4 Gbit SLC SD NAND** (`XTSD04GLGEAG` on 4-bit `SDMMC1`), and **onboard barometric sensing** (`LPS25HBTR` in an unpotted ePTFE-vented chimney pocket) behind **dual 35-pin sealed TE AMPSEAL headers** (`J1` Key 1 Black `776163-1`, `J2` Key 2 Grey `776163-2`).

The first committed vehicle application is the **2007 Suzuki SV650 (K7, Gen 2 dual-plug 90° V-twin)**, with full support for independent primary and trailing ignition timing, dual wideband closed-loop lambda control, camless MAP phase detection, and both SV650 4-wire stepper actuators (`ISC` idle valve + `STVA` secondary throttle valve).

> **Note on Prior `Atlas-clone` Checkpoint**: The earlier standalone `Atlas-clone` 107-pin brain-module work (which remapped Polygonus pins to impersonate the upstream `atlas` binary) is preserved on branch [`atlas-brain-module-checkpoint`](https://github.com/halbritt/fome-mc/tree/atlas-brain-module-checkpoint). Because `fome-mc` has its own dedicated FOME firmware target ([`halbritt/fome-fw` `firmware/config/boards/fome-mc/`](https://github.com/halbritt/fome-fw/tree/fome-mc/firmware/config/boards/fome-mc)), `fome-mc` retains the native Polygonus LQFP-144 copper routing rather than remapping `U26` pins to impersonate `atlas`.

---

## Key Repository Documents & Artifacts

- **[`DESIGN.md`](DESIGN.md)** — Complete engineering architecture, SV650 K7 interface specification, circuit-reuse ledger, and closure of the four reviewer domains (barometric sensing, soldered SD NAND storage, single-owner `FatFs` $\to$ `USBMSD1` handoff + post-potting recovery, and 2-stage selective encapsulation).
- **[`VALIDATION.md`](VALIDATION.md)** — Automated ERC/DRC/netlist/BOM verification results, FOME firmware build & unit test results (`16/16` passing), and pre-/post-encapsulation bench and vehicle test gates.
- **[`io-map.csv`](io-map.csv)** & **[`scripts/verify_io_map.py`](scripts/verify_io_map.py)** — Machine-verified 70-pin `J1`/`J2` AMPSEAL connector pinout, 16 internal bus contracts, 474-part schematic/PCB parity, and `mapping.yaml` verification script.
- **[`fome-mc.kicad_sch`](fome-mc.kicad_sch)** & **[`fome-mc.kicad_pcb`](fome-mc.kicad_pcb)** — Root KiCad 10 schematic (21-sheet hierarchy) and 4-layer `162.0 mm × 115.0 mm` PCB layout.
- **[`export/BOM-fome-mc.csv`](export/BOM-fome-mc.csv)** & **[`export/CPL-fome-mc.csv`](export/CPL-fome-mc.csv)** — Production JLCPCB Bill of Materials (`101` unique rows, `474` parts) and Component Placement List (`474` placements).

---

## Verification Commands

```bash
# 1. Verify toolchain environment
make doctor

# 2. Verify 70-pin J1/J2 netlist, internal buses, BOM/CPL, and firmware mapping.yaml parity
python3 scripts/verify_io_map.py

# 3. Run full hermetic KiCad 10 ERC, DRC, netlist, KiBot Gerber/BOM/PDF export, and analysis
make check
```
