# telemetry-pod

Project skeleton for the tail-cowl CAN1 telemetry pod (`FOMEMC-28`). The design is
generated into this directory later by agent-ee; the KiCad files remain empty
placeholders that let the toolchain address the project. The proposed interface
input and its verification limits are documented in [IO_MAP.md](IO_MAP.md).

| Path | Content now |
|---|---|
| `telemetry-pod.kicad_sch` | empty root sheet (`kicad-cli sch upgrade` normalised) |
| `telemetry-pod.kicad_pcb` | empty board saved by the pcbnew API (KiCad defaults, no outline) |
| `telemetry-pod.kicad_pro` | KiCad 10 stock template project, top-level sheet set |
| `sym-lib-table` | empty |
| `fp-lib-table` | `ampseal` → `${KIPRJMOD}/../libs/footprints/ampseal.pretty` (the ECU's library) |
| `sheets/`, `contracts/`, `export/` | empty (`.gitkeep`) |
| `io-map.csv` | proposed harness, radio, antenna and factory UART interface input |
| `verify_io_map.py`, `io-map-cross-check.txt` | pinned spec-ID cross-check and its output |

The project is `[projects.telemetry-pod]` in `toolchain/versions.toml`, so the usual
targets take `PROJECT=telemetry-pod` (`make erc|drc|check PROJECT=telemetry-pod`).
`${KIPRJMOD}/../<dir>` resolves one level up, to the repository root; the snapshot links
`../libs` to the root's `libs/`.
