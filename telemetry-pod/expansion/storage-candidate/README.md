# Storage circuit candidate

This preserved schematic adds FORESEE FEMDME008G-A8A39 eMMC and its core supply
and four rail supervisors to the expanded MCP3208 acquisition candidate. It is **not ready for fabrication**
and has not replaced the actual telemetry-pod project.

U14 uses the reserved four-bit SDMMC interface at an initial 20 MHz SDR target.
R46–R54 provide 10 kΩ pull-ups on CMD and DAT0–7; R55 pulls DS down. C63 is
1 µF on the internal VDDi node. RSTN remains unconnected pending the persistent
register/reset policy. All other NC, RFU and VSF balls are isolated.

U15, TPS62162QDSGRQ1, makes a separate 3.3 V core supply from PRE_6V3 through
L4, SRP4020TA-2R2M. C68/C69 add two nominal 22 µF output capacitors; C70 adds
22 µF at the input. Existing C64/C65 remain local eMMC core bypassing. VCCQ and
its pull-ups now use the same +3V3 supply as the MCU, with C66/C67 local bypassing.
This keeps host and memory I/O on the same supply while separating VCC from VCCQ.

The native power flag at the core output describes the verified path from
U15's switch output through L4. KiCad does not propagate the power-output type
through that inductor. The flag does not establish load capacity or rail quality.
U15's PG is unconnected: it becomes high-impedance on UVLO, disable and thermal
shutdown. U16/U17 now supervise main and eMMC core rails and share MCU_EN.
U18/U19 report sensor-supply and protected-input faults separately. See
[supervision.md](supervision.md) for thresholds, footprint interpretation and
remaining qualification limits.

The captured eMMC manufacturer document A-00093 v1.0 specifies −40…+105 °C,
3.3 V-compatible VCCQ, and 7,818,182,656 user bytes. At 60,400 bytes/s and an
assumed 80% recording allocation this gives approximately 28.76 hours of
capacity. This is arithmetic, not measured duration; eight hours remains soft.
The catalog observed 247 C3249972 parts at 2026-10-20T10:14:47Z. Subsequent
captures observed 48 C2071196 regulators and 1059 C719179 inductors. Stock can
change; the captured timestamps and responses are retained.

## Evidence and reproduction

`inputs/intent.json`, `inputs/emitter-layout.json`, and captured symbols reproduce
the native schematic with agent-ee `4ef3a7b0420d05a45636a7726f75557835d78517`:

```sh
python3 -m agent_ee.schematic_emitter inputs/intent.json \
  --layout inputs/emitter-layout.json --captures inputs \
  --out NEW_PROJECT_DIRECTORY --receipt NEW_RECEIPT.json
```

Run with that checkout's `src` on `PYTHONPATH`; create the output directory's
parent first. Output locations must not already exist. `emission-receipt.json`
pins the inputs and native outputs.

Run `python3 verify.py` here to export a fresh native netlist and check the
independent circuit contract and expected ERC findings on a temporary snapshot.
`native.xml` is the retained export; `previous-power-native.xml`,
`previous-storage-native.xml` and `previous-adc-native.xml` preserve the preceding
circuit boundaries. Historical
interface-only migration assumptions are in `interface-migration.json`;
`power-migration.json` describes the preceding storage power change;
`supervisor-migration.json` describes the current supervision change.

ERC has no electrical errors and retains the missing AMPSEAL-35 footprint
warning. This is not a waiver or a release pass. Captured footprints support
native checks; 3D model paths and assembly suitability remain unqualified.
Inherited part bindings are historical inputs, not a new parts approval.

Sources are the captured eMMC PDF, `power-sources/` and `supervisor-sources/`. The regulator and
inductor documents were downloaded from TI and Bourns. The supervisor PDF is
retained as evidence for the rejected circuit described in
[supervisor-review.md](supervisor-review.md).

## Remaining work

- Qualify reset supervision, input/rail diagnostics and sequencing, including
  host behavior when eMMC core power disappears; circuit implementation alone
  does not establish reset or logging recovery.
- Complete input protection/filter damping, whole-system peak-load and thermal
  budgets, sensor-branch protection and a declared dip/recovery envelope.
- Select and bind new passives; verify effective capacitance, bias, temperature,
  inductor behavior and source-current limits. Nominal values are insufficient.
- Implement and test logging, cache flush, power-off notification and recovery.
  No bounded loss window or safe-flush hold-up time is established.
- Resolve RFU/VSF manufacturer disposition and hardware-reset provisioning.
- Validate BGA lands, paste, mask, assembly, endurance, throughput and signal integrity.
- Complete wheel/tire interfaces, connector CAD, placement, routing, independent
  release review and manufacturing artifacts.
