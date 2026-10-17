# fome-mc: toolchain run PASS

- Description: FOME-MC brain module (fome-mc, STM32H7)
- Run: `build/runs/project/fome-mc/20261016T214759.589014Z` (2026-10-16T21:47:59.589147+00:00 → 2026-10-16T21:51:03.419803+00:00)
- Source: `/home/halbritt/git/fome-mc` — git revision HEAD (c43ad7bafc9a8e3be337f1342ae0cb259918882a) @ `c43ad7bafc9a8e3be337f1342ae0cb259918882a` (0 uncommitted file(s) in snapshot)
- Fill mode: `asis`
- Tools: kicad-cli 10.0.7, ngspice 42, kibot 1.9.1, kicad-happy 06840467ad0f5d76af45f64449b1f5ecb10f052f, fome-kicad-libraries ab9c5f8a1517a04b9cada6880d67d190bfd48c05, python 3.12.3

| Step | Check status | Design clean | Findings |
|---|---|---|---|
| erc | PASS | False | `{"sheets_checked": 16, "violations": 1481, "by_severity": {"warning": 1446, "error": 35}, "by_type": {"endpoint_off_grid": 1118, "lib_symbol_mismatch": 295, "pin_not_connected": 14, "isolated_pin_label": 9, "pin_to_pin": 9, "lib_symbol_issues": 8, "footprint_link_issues": 6, "power_pin_not_driven": 6, "pin_not_driven": 6, "label_dangling": 3, "same_local_global_label": 3, "similar_labels": 2, "unc…` |
| drc | PASS | False | `{"violations": 540, "unconnected_items": 99, "schematic_parity": 259, "by_severity": {"warning": 566, "error": 332}, "by_type": {"lib_footprint_mismatch": 199, "footprint_symbol_field_mismatch": 199, "shorting_items": 149, "unconnected_items": 99, "clearance": 50, "starved_thermal": 42, "net_conflict": 39, "silk_over_copper": 36, "courtyards_overlap": 28, "silk_overlap": 25, "footprint_symbol_mism…` |
| netlist | PASS | None | `{"components": 336, "nets": 346}` |
| export | PASS | None | `{"artifacts": {"schematic PDF": 16, "schematic SVG": 16, "PCB PDF": 6, "BOM CSV": 5746, "kibot gerber F.Cu": 1, "kibot gerber B.Cu": 1, "kibot gerber Edge.Cuts": 1, "kibot gerber job file": 1, "kibot excellon drill": 1, "kibot drill report": 1, "kibot position files": 2, "kibot BOM CSV": 1, "kibot BOM HTML": 1, "kibot schematic PDF": 1, "kibot PCB print PDF": 1}}` |
| analyze | PASS | None | `{"schematic": {"components": 336, "nets": 349, "findings": {"error": 19, "warning": 26, "info": 242}, "native_netlist_components": 336}, "pcb": {"footprints": 336, "nets": 349, "routing_complete": false, "cross_reference_input": "schematic.json", "power_net_resolution_source": "schematic", "findings": {"error": 33, "warning": 27, "info": 120}}, "cross_analysis": {"checks_run": 10, "findings": {"er…` |
