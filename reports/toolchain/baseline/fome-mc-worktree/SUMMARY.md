# fome-mc-worktree: toolchain run FAIL

- Description: FOME-MC brain module (Atlas-clone, STM32H7)
- Run: `build/runs/project/fome-mc-worktree/20261016T215539.765831Z` (2026-10-16T21:55:39.766004+00:00 → 2026-10-16T21:57:59.013818+00:00)
- Source: `/home/halbritt/git/Atlas-clone` — working tree @ `c43ad7bafc9a8e3be337f1342ae0cb259918882a` (12 uncommitted file(s) in snapshot)
- Fill mode: `asis`
- Tools: kicad-cli 10.0.7, ngspice 42, kibot 1.9.1, kicad-happy 06840467ad0f5d76af45f64449b1f5ecb10f052f, fome-kicad-libraries ab9c5f8a1517a04b9cada6880d67d190bfd48c05, python 3.12.3

## Library resolution issues

- fp-lib-table: ${KIPRJMOD}/../kicad-libraries/project_footprints.pretty does not exist
- fp-lib-table: ${KIPRJMOD}/../kicad-libraries/mx120.pretty does not exist

| Step | Check status | Design clean | Findings |
|---|---|---|---|
| erc | PASS | False | `{"sheets_checked": 21, "violations": 2223, "by_severity": {"warning": 2154, "error": 69}, "by_type": {"endpoint_off_grid": 1626, "lib_symbol_mismatch": 327, "multiple_net_names": 56, "similar_labels": 41, "isolated_pin_label": 35, "lib_symbol_issues": 30, "pin_not_connected": 22, "label_dangling": 21, "pin_to_pin": 20, "unconnected_wire_endpoint": 19, "power_pin_not_driven": 9, "footprint_link_iss…` |
| drc | PASS | False | `{"violations": 540, "unconnected_items": 99, "schematic_parity": 480, "by_severity": {"warning": 787, "error": 332}, "by_type": {"lib_footprint_mismatch": 199, "footprint_symbol_field_mismatch": 199, "shorting_items": 149, "missing_footprint": 144, "net_conflict": 109, "unconnected_items": 99, "clearance": 50, "starved_thermal": 42, "silk_over_copper": 36, "courtyards_overlap": 28, "silk_overlap":…` |
| netlist | PASS | None | `{"components": 472, "nets": 452}` |
| export | FAIL | None | `{"artifacts": {"schematic PDF": 21, "schematic SVG": 21, "PCB PDF": 6, "BOM CSV": 7508}}` |
|  | ↳ kibot: exit code 22 |  |  |
| analyze | PASS | None | `{"schematic": {"components": 472, "nets": 450, "findings": {"error": 23, "warning": 36, "info": 337}, "native_netlist_components": 472}, "pcb": {"footprints": 336, "nets": 349, "routing_complete": false, "cross_reference_input": "schematic.json", "power_net_resolution_source": "schematic", "findings": {"error": 33, "warning": 27, "info": 120}}, "cross_analysis": {"checks_run": 10, "findings": {"er…` |
