# AGENTEE-492 pod RF declaration (writer slice, PARTIAL)

`rf-geometry.json` is an `agent-ee.rf-geometry/1` declaration for the pod GNSS RF path, consumed by the
landed agent-ee `check_rf_geometry` checker (agent-ee 228d2854, accepted 31ac3920 by agent-529, relayed).
All prose here is agent-drafted; nothing here is owner text.

- Net `/POD_GNSS_RF`, ground net `/GND` (the board's actual net; not `GND`, review F1), F.Cu over In1.Cu.
  Derived from the current board `telemetry-pod.kicad_pcb` sha256
  fa7c2ca67e7ba3b832c0b89268052c6701695454bb17756af01854ef3ecaf46e (an unplaced scaffold).
- CPW: width 0.293 mm (293000 nm), physical flank gap 0.2032 mm (203200 nm), both at zero tolerance.
  No tolerance relaxation.
- POST-ROUTE acceptance check only. The unrouted board need not pass it, and nothing here claims RF
  qualification, verified impedance or fabrication tolerance.
- UNBOUND (not declared, nothing invented): stitching pitch and band, topology (trunk and stub maximum
  lengths; the pod maximum length stays unbound, and 15 mm is only a synthetic mechanism control),
  electrical length and guard width.
- REBIND: J2's final pose and UUID and the RF areas are AGENTEE-485 F7 duties. Re-derive the net and layer
  identities from the post-485 board before use.
- Evaluation must go through the bound `check_rf_geometry` entry point, which checks the board hash
  (review F6), with a fresh `agent-ee.rf-geometry-native/2` extraction. Old /1 reports are not reused.

Parse check (admitted `native-admit run --class test --weight 1`, agent_ee from agent-ee 337a75ce copied
into gitignored build/ee492-probe): `parse_declaration` accepts the declaration, resolving width_nm 293000
and gap_nm 203200; exit=0.
