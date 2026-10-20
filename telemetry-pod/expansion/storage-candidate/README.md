# Storage interface candidate

This preserved schematic adds FORESEE FEMDME008G-A8A39 eMMC to the expanded
MCP3208 acquisition candidate. It is **not powered or ready for fabrication**.
The actual telemetry-pod project has not been replaced by this candidate.

U14 uses the reserved four-bit SDMMC interface at an initial 20 MHz SDR target.
R46–R54 provide 10 kΩ pull-ups on CMD and DAT0–7; R55 pulls DS down. C63 is
1 µF on the internal VDDi node. VCC and VCCQ each have nominal 4.7 µF and
100 nF bypassing on distinct, currently undriven 3.3 V nets. RSTN remains
unconnected pending the persistent-register/reset policy. All other NC, RFU
and VSF balls are isolated.

The captured manufacturer document A-00093 v1.0 specifies −40…+105 °C,
3.3 V-compatible VCCQ, and 7,818,182,656 user bytes. At the allocation plan's
60,400 bytes/s and an assumed 80% recording allocation this gives approximately
28.76 hours of capacity. This is arithmetic, not a measured logging duration;
eight hours remains a soft target. The JLCPCB catalog capture observed 247
C3249972 parts at 2026-10-20T10:14:47Z. Stock can change.

The manufacturer PDF was captured from:
https://datasheet.lcsc.com/datasheet/pdf/4a42a44db43b0649ea0f19c39bec79bb.pdf?productCode=C3249972

## Evidence and reproduction

`inputs/intent.json`, `inputs/emitter-layout.json`, and the captured symbol
libraries reproduce `telemetry-pod.kicad_sch` with agent-ee commit
`4ef3a7b0420d05a45636a7726f75557835d78517`:

```sh
python3 -m agent_ee.schematic_emitter inputs/intent.json \
  --layout inputs/emitter-layout.json --captures inputs \
  --out NEW_PROJECT_DIRECTORY --receipt NEW_RECEIPT.json
```

Run with that checkout's `src` on `PYTHONPATH`; create the output directory's
parent first. Output locations must not already exist. Capturing only the used
symbols reduced the libraries from 8 MB to 119 KB and reproduced the exact same
native schematic SHA-256:
`32fd8d8e7dd23f54128bb12aad69c3a615759ea67c7180e2b3f627621a823952`.

`native.xml` is the native KiCad export. `previous-adc-native.xml` is the
preceding candidate and permits verification that only six existing MCU
terminals changed nets. `check_storage_native.py native.xml OUTPUT.json`
checks 81 storage connections. Independent review covers the entire ball map,
unused balls, passive values and preservation of prior connectivity.

`erc.json` retains two undriven supply errors and the existing missing
AMPSEAL-35 footprint warning. There are no power flags masking those errors.
The referenced footprints are captured for ERC/link checks; their 3D model
paths and manufacturing suitability are not qualified by this package.
The inherited part bindings are historical inputs, not a new parts approval.

Run `python3 verify.py` from this directory to export a fresh native netlist,
repeat the 324-check independent review, and confirm the disclosed ERC findings
on a temporary snapshot. A successful command does not mean ERC is clean.

## Remaining work

- Implement separate storage supplies, size peak loads and establish sequencing
  and host-pin behavior while the eMMC is unpowered.
- Select/bind new passives, including effective capacitance at bias and temperature.
- Resolve manufacturer RFU/VSF handling and hardware reset provisioning.
- Implement and test logging, cache flush, power-off notification and recovery.
  The datasheet's long power-off notification timeout is 600 ms; it does not
  establish a bounded log-loss window or power hold-up requirement by itself.
- Validate BGA lands, paste, mask, assembly process and signal integrity.
- Establish endurance, actual throughput and enclosure thermal behavior.
- Complete wheel/tire interfaces, power redesign, connector CAD, placement,
  routing, independent release review and manufacturing artifacts.
