# fome-mc-worktree: toolchain run PASS

- Description: FOME-MC integrated motorcycle ECU (STM32H753 + 2x STM32F042 WBO)
- Run: `build/runs/project/fome-mc-worktree/20261017T003917.386554Z` (2026-10-17T00:39:17.386729+00:00 → 2026-10-17T00:43:55.060707+00:00)
- Source: `/home/halbritt/git/fome-mc` — working tree @ `36db604471e65ccab12c2572aad6d8b458ad31fc` (45 uncommitted file(s) in snapshot)
- Fill mode: `asis`
- Tools: kicad-cli 10.0.7, ngspice 42, kibot 1.9.1, kicad-happy 06840467ad0f5d76af45f64449b1f5ecb10f052f, fome-kicad-libraries ab9c5f8a1517a04b9cada6880d67d190bfd48c05, python 3.12.3

| Step | Check status | Design clean | Findings |
|---|---|---|---|
| erc | PASS | False | `{"sheets_checked": 21, "violations": 2190, "by_severity": {"warning": 2130, "error": 60}, "by_type": {"endpoint_off_grid": 1644, "lib_symbol_mismatch": 330, "similar_labels": 45, "lib_symbol_issues": 30, "isolated_pin_label": 29, "pin_not_connected": 22, "unconnected_wire_endpoint": 21, "multiple_net_names": 17, "label_dangling": 16, "pin_to_pin": 12, "power_pin_not_driven": 9, "footprint_link_iss…` |
| drc | PASS | False | `{"violations": 228, "unconnected_items": 237, "schematic_parity": 251, "by_severity": {"warning": 479, "error": 237}, "by_type": {"unconnected_items": 237, "lib_footprint_mismatch": 199, "footprint_symbol_field_mismatch": 199, "net_conflict": 34, "starved_thermal": 28, "footprint_symbol_mismatch": 18, "track_dangling": 1}, "ignored_checks": ["missing_courtyard", "solder_mask_bridge", "track_not_ce…` |
| netlist | PASS | None | `{"components": 474, "nets": 456}` |
| export | PASS | None | `{"artifacts": {"schematic PDF": 21, "schematic SVG": 21, "PCB PDF": 6, "BOM CSV": 7534, "kibot gerber F.Cu": 1, "kibot gerber B.Cu": 1, "kibot gerber Edge.Cuts": 1, "kibot gerber job file": 1, "kibot excellon drill": 1, "kibot drill report": 1, "kibot position files": 2, "kibot BOM CSV": 1, "kibot BOM HTML": 1, "kibot schematic PDF": 1, "kibot PCB print PDF": 1}}` |
| analyze | PASS | None | `{"schematic": {"components": 474, "nets": 457, "findings": {"error": 31, "warning": 32, "info": 349}, "native_netlist_components": 474}, "pcb": {"footprints": 474, "nets": 450, "routing_complete": false, "cross_reference_input": "schematic.json", "power_net_resolution_source": "schematic", "findings": {"error": 53, "warning": 16, "info": 163}}, "cross_analysis": {"checks_run": 10, "findings": {"er…` |
