# telemetry-pod (`FOMEMC-28` — Pilot Snapshot)

> **PILOT SNAPSHOT — NOT A RELEASE:** This placed-and-routed 4-layer `90 × 65 mm` board (`driver-preparation-v9-90x65`) is committed as an owner-approved pilot snapshot so the complete schematic, placement, routing, and 2D/3D renders are visible in-tree while trunk requalification finishes. It will be replaced by the clean-`main` requalified board once the open items below land.

## Pilot Provenance & Open Requalification Items

- **Status:** Pilot snapshot (`driver-preparation-v9-90x65`, board SHA256 `2938ee1ee2cae459c869ee5c4c8443e66322034736fe3fcbf4b5e56377ea1cfa`). Not a fabrication release.
- **`agent-ee` Source SHA:** `a02c952` (`main`).
- **Router Provenance:** Routed with the validated fix content from the rejected runtime prototypes `kr63` (`d7ceadf`, multi-point pad weld stub layer mapping) and `kr64` (`670f5c6`, non-rectangular pad perimeter weld stub filtering). The runtime patching mechanism was superseded by owner decision in favor of pinning the fork `halbritt/KiCadRoutingTools` (`branch kicad-route-fixes` based on `v0.23.1` `295f9ee1`, tracked under `KICADROUTE-65`) and filing the two defects upstream.
- **Stage 7 (`agent-ee` 18-Check Review Gate) Status:**
  - **Raw `agent-ee` `a02c952`:** `12/18` checks `pass` (`erc`, `interface`, `package-nc`, `power-interface`, `intent-parity`, `parts`, `part-bindings`, `pinout-electrical`, `placement-drc`, `net-constraint-assignment`, `routing-drc`, `drc`), `2/18` `info` (`netlist`, `geometry`), `4/18` non-pass (`fab_package`, `pinout-ble`, `assembly`, `severity`).
  - **With `AGENTEE-275` (`fab_package` delegated parameter & `board_only` mounting-hole fix):** `15/18` checks `pass`/`info` (including `fab_package: pass` with 11 plots, PTH/NPTH drills, 43 BOM rows, 101 CPL rows, 1 rule-excluded connector `J1`, and 8 sealed artifacts `452630826d34`).
  - **Open Software / Library Items Being Landed for Clean-`main` Requalification:**
    1. **`AGENTEE-275`:** `fab_package` delegated parameters (`probe_manifest`, `assembly_exclusion`, `bom_variant`, `model_libraries`) and `fab_export` support for `board_only` mechanical mounting holes (`H1..H4`).
    2. **`AGENTEE-276`:** Geometry/policy handling for silkscreen (`H1..H4` reference silk over drill, reference labels outside courtyards, `IMU_AXES` obstacle, `J1`/`U1` overhanging edge silk) and inner-plane layer types (`In1.Cu` `power`, `In2.Cu` `mixed`).
    3. **`KICADROUTE-65`:** Pin `halbritt/KiCadRoutingTools` (`kicad-route-fixes`) in `kicad-route` and re-pin in `agent-ee`.
    4. **Upstream `ublox_NEO` 3D Model Gap:** `RF_GPS.3dshapes/ublox_NEO.step` is 404 in upstream `kicad-packages3D` (`10.0.7`); tracked as an explicit upstream library gap rather than silently passing.
    5. **`U3` (`NEO-M9N-00B`, `C2843985`) JLCPCB Stock Gate:** `stock_count: 0` at JLCPCB (`assembly_readiness: unknown`), pending restock or owner hand-fit authorization.
- **`fome-mc` Native Toolchain Check Results (`make check PROJECT=telemetry-pod` / `make verify-io PROJECT=telemetry-pod`):**
  - `erc`: **PASS** (`Design clean: True`, `0` violations across 1 sheet).
  - `drc`: **PASS** (`Design clean: True`, `0` violations, `0` unconnected items, `0` schematic parity issues).
  - `netlist`: **PASS** (`108` components, `116` nets).
  - `analyze` (`kicad-happy`): **PASS** (`108` schematic components, `112` PCB footprints, `routing_complete: true`).
  - `export` (KiBot): **FAIL** (KiBot `1.9.1` exits `22` when parsing `agent-ee`'s JSON `bare-copper-probe/1` metadata property on `TP1..TP6` as a colon-delimited footprint string; native `kicad-cli` fab export passes).
  - `verify-io`: **FAIL** (`contracts/telemetry-pod.interface.json` intentionally fails closed per `FOMEMC-29` until `AGENTEE-188` generates the root contract).

---

## 3D Ray-Traced Board Renders (`4096 × 3072`)

### Top View (`F.Cu`)
![Telemetry Pod 3D Top View](renders/3d/telemetry-pod-3d-top.png)

### Isometric View
![Telemetry Pod 3D Isometric View](renders/3d/telemetry-pod-3d-isometric.png)

### Bottom View (`B.Cu`)
![Telemetry Pod 3D Bottom View](renders/3d/telemetry-pod-3d-bottom.png)

---

## 2D Layer & Schematic Renders

### Top Copper & Silkscreen (`F.Cu`)
![Telemetry Pod 2D Top](renders/telemetry-pod-pcb-top.png)

### Top Assembly & Courtyards
![Telemetry Pod 2D Assembly](renders/telemetry-pod-pcb-assembly.png)

### Bottom Copper & Silkscreen (`B.Cu`)
![Telemetry Pod 2D Bottom](renders/telemetry-pod-pcb-bottom.png)

### Inner Layer 1 (`In1.Cu` — `GND` Plane)
![Telemetry Pod In1.Cu GND](renders/telemetry-pod-pcb-in1-gnd.png)

### Inner Layer 2 (`In2.Cu` — `+3V3` Plane)
![Telemetry Pod In2.Cu +3V3](renders/telemetry-pod-pcb-in2-pwr.png)

### Schematic (`telemetry-pod.kicad_sch`)
![Telemetry Pod Schematic](renders/telemetry-pod-schematic.png)

- Multi-layer PCB PDF: [`renders/telemetry-pod-pcb-layers.pdf`](renders/telemetry-pod-pcb-layers.pdf)
- Schematic PDF: [`renders/telemetry-pod-schematic.pdf`](renders/telemetry-pod-schematic.pdf)

---

## Directory Contents

| Path | Description |
|---|---|
| `telemetry-pod.kicad_sch` | Complete telemetry-pod schematic (`108` components, `116` nets, `0` ERC violations) |
| `telemetry-pod.kicad_pcb` | Placed-and-routed 4-layer `90 × 65 mm` pilot board (`112` footprints, `62/62` signal nets routed, `0` DRC violations) |
| `telemetry-pod.kicad_pro` | KiCad 10 project configuration and netclass rules |
| `telemetry-pod.kicad_dru` | Custom design rules (`agent-ee` net constraint rules) |
| `telemetry-pod.net-constraints.record.json` | Provenance record for assigned net classes and RF/differential constraints |
| `sym-lib-table`, `fp-lib-table` | Project-relative symbol and footprint library tables (`${KIPRJMOD}/...`) |
| `captured-symbols/`, `captured-footprints/` | KiCad-library-derived and project-authored symbols and footprints |
| `kicad-libraries/` | Shared FOME AMPSEAL-23 footprint and 3D STEP model (`c-1-776228-1-e-3d.STEP`) |
| `renders/` | 2D layer SVGs/PNGs/PDFs, schematic SVG/PNG/PDF, and 4K 3D ray-traced views (`renders/3d/`) |
| `io-map.csv`, `IO_MAP.md`, `verify_io_map.py`, `io-map-cross-check.txt` | Proposed harness, radio, antenna, and factory UART interface input and spec-ID cross-check |
| `REQUIREMENTS.md` | Captured hardware requirements and owner design decisions |
