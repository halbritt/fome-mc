# universal-112: toolchain run PASS

- Description: Polygonus Universal 112 dual-WBO base board (electrical baseline donor)
- Run: `build/runs/project/universal-112/20261017T003509.204925Z` (2026-10-17T00:35:09.205089+00:00 → 2026-10-17T00:39:16.245136+00:00)
- Source: `/home/halbritt/git/Polygonus-Universal-112` — git revision HEAD (ddcf0f77fecf3ea7f093954ce1becb7c4a26e970) @ `ddcf0f77fecf3ea7f093954ce1becb7c4a26e970` (0 uncommitted file(s) in snapshot)
- Fill mode: `asis`
- Tools: kicad-cli 10.0.7, ngspice 42, kibot 1.9.1, kicad-happy 06840467ad0f5d76af45f64449b1f5ecb10f052f, fome-kicad-libraries ab9c5f8a1517a04b9cada6880d67d190bfd48c05, python 3.12.3

## Library resolution issues

- sheet file 'VR Conditioner.kicad_sch' (referenced by Polygonus-Universal-Base.kicad_sch) exists only as 'VR conditioner.kicad_sch'; a case-sensitive filesystem cannot open it. The snapshot adds a case alias so the checks cover that sheet; the source repo is unchanged.
- fp-lib-table: ${KIPRJMOD}/wideband_module.pretty does not exist

| Step | Check status | Design clean | Findings |
|---|---|---|---|
| erc | PASS | False | `{"sheets_checked": 10, "violations": 353, "by_severity": {"warning": 348, "error": 5}, "by_type": {"endpoint_off_grid": 229, "lib_symbol_mismatch": 89, "lib_symbol_issues": 14, "footprint_link_issues": 8, "isolated_pin_label": 5, "power_pin_not_driven": 3, "multiple_net_names": 2, "pin_not_connected": 1, "pin_to_pin": 1, "same_local_global_label": 1}, "ignored_checks": ["single_global_label", "fou…` |
| drc | PASS | False | `{"violations": 142, "unconnected_items": 0, "schematic_parity": 114, "by_severity": {"warning": 243, "error": 13}, "by_type": {"footprint_symbol_field_mismatch": 111, "lib_footprint_mismatch": 106, "silk_over_copper": 14, "lib_footprint_issues": 9, "padstack": 5, "annular_width": 5, "starved_thermal": 3, "footprint_symbol_mismatch": 3}, "ignored_checks": ["missing_courtyard", "track_not_centered_o…` |
| netlist | PASS | None | `{"components": 139, "nets": 199}` |
| export | PASS | None | `{"artifacts": {"schematic PDF": 10, "schematic SVG": 10, "PCB PDF": 6, "BOM CSV": 2594, "kibot gerber F.Cu": 1, "kibot gerber B.Cu": 1, "kibot gerber Edge.Cuts": 1, "kibot gerber job file": 1, "kibot excellon drill": 1, "kibot drill report": 1, "kibot position files": 2, "kibot BOM CSV": 1, "kibot BOM HTML": 1, "kibot schematic PDF": 1, "kibot PCB print PDF": 1}}` |
| analyze | PASS | None | `{"schematic": {"components": 139, "nets": 200, "findings": {"error": 2, "warning": 35, "info": 108}, "native_netlist_components": 139}, "pcb": {"footprints": 139, "nets": 199, "routing_complete": true, "cross_reference_input": "schematic.json", "power_net_resolution_source": "schematic", "findings": {"error": 5, "warning": 7, "info": 67}}, "cross_analysis": {"checks_run": 10, "findings": {"error":…` |
