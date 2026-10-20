# Rail supervision candidate

Four TPS389001DSER supervisors add reset and diagnostic signals to the storage
candidate. TI SLVSD65A page 12 explicitly permits SENSE from 0 to 5.5 V regardless
of VDD. This resolves the sequencing objection to the earlier TPS386000 proposal
in `supervisor-review.md`. It does not establish power-loss recovery.

Each supervisor uses +3V3 for VDD and MR, 100 nF local bypassing and a 22 nF CT
capacitor. Pins are SENSE 1, GND 2, MR 3, VDD 4, CT 5 and open-drain RESET 6;
the DSE package has no exposed pad. Outputs are active low.

| Reference | Monitored rail | Divider top / bottom | Nominal falling threshold | Output |
|---|---|---|---|---|
| U16 | MCU +3V3 | 16.9 kΩ / 10 kΩ | 3.0935 V | MCU_EN |
| U17 | EMMC_VCC_3V3 | 15.2 kΩ / 10 kΩ | 2.898 V | MCU_EN |
| U18 | POD_5V_SENSOR | 31.3 kΩ / 10 kΩ | 4.7495 V | SENSOR_FAULT_N, GPIO48 |
| U19 | POD_12V_PROTECTED | 64.9 kΩ / 10 kΩ | 8.6135 V | POWER_FAIL_N, GPIO8 |

The main and storage-core reset outputs share MCU_EN. Sensor and protected-input
faults are separate MCU inputs, each with a 10 kΩ pull-up. U1 module pins 25 and
12 lose their previous NC markers. No strap or SDMMC assignments change.
R29 becomes 100 kΩ and C47 becomes 10 nF; their old part bindings are removed.
All added parts remain unbound pending source and rating closure.

## Threshold and timing limits

Divider resistors require 0.1% initial tolerance. The independent calculation in
`independent-review/supervisor-calculations.json` evaluates 16.9 kΩ as the selected
main-rail alternative: conservative static falling range 3.0570–3.1301 V and
maximum rising threshold 3.1559 V. The latter remains below the assumed 3.201 V
minimum valid rail. These bounds include initial resistor tolerance, threshold
accuracy and conservative sense leakage; resistor temperature drift and dynamic
rail movement are excluded. Exact resistor selection must close those omissions.

The 22 nF CT nominal release delay is 23.565 ms. The illustrative 17.185–34.712 ms
calculation uses capacitor/current/comparator corners and a nominal additive
term, so it is not a guaranteed interval. Assertion delay is specified typically
as 18 µs; a guaranteed worst-case loss or reset response is not established.
Startup, repeated short dips and the ESP32's required reset-low duration need
waveform validation at MCU_EN and both supply domains.

The 100 kΩ EN pull-up draws 8 µA at 0.8 V, within the supervisor's 15 µA POR
measurement load. Two specified 250 nA output leakages and 50 nA MCU input leakage
would cause a 55 mV high-state drop. Low-supply leakage outside the published
conditions and probe loading remain open. R29/C47 give a nominal 1 ms RC.

At 40 V on the protected input, U19's divider puts approximately 5.35 V at SENSE
at the resistor corner. Its 5.5 V recommended limit is reached around 41.1 V.
The actual hot-clamp voltage and overshoot must stay within that limit; neither
an unqualified TVS nominal value nor the supervisor's 7 V absolute maximum is
adequate evidence. The warning threshold provides no guaranteed flush interval.

## Custom footprint interpretation

`PodSupervisor:DSE0006A` is an engineering interpretation of TI drawing
4220552/B (January 2024), not a qualified manufacturer copper match. The drawing
calls for pads 1–3 to be solder-mask-defined and pads 4–6 non-solder-mask-defined,
but its dimensioned illustration does not unambiguously identify the left
shapes as mask openings. That ambiguity remains explicit.

The candidate uses 0.8 × 0.25 mm mask/paste opening at pin 1 and 0.7 × 0.25 mm
at pins 2–6, with pin 1 centered at x = −0.55 mm and other left/right columns
at x = ±0.6 mm. Left copper is enlarged 0.05 mm on every side; mask and paste
margins are −0.05 mm. Right copper uses the nominal opening dimensions, with
+0.05 mm mask clearance and zero paste margin. Pad pitch is 0.5 mm.

`supervisor-sources/footprint-check.kicad_pcb` and its three native KiCad Gerbers
retain the actual copper, mask and paste geometry for inspection. The paste
apertures have 0.05 mm corner radius. Fabrication registration capability,
manufacturer interpretation and assembled joints still need validation. This
small footprint fixture is not a board fabrication package.

The TI PDF, dated JLC stock response and source hashes are retained under
`supervisor-sources/` and `supervisor-migration.json`. The observed stock was 243
C1509297 devices at 2026-10-20T10:47:24Z; this is historical availability.
