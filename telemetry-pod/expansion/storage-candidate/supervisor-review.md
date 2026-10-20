# Supervisor circuit review — not implemented

The proposed TPS386000 circuit would monitor main 3V3, eMMC core, sensor supply
and protected input. Main/core resets would share MCU_EN; sensor fault and input
warning would use the allocated GPIOs. Independent review found reasons to
resolve the design before adding it to the native candidate.

- The captured TI SBVS105F document specifies recommended `0 ≤ VSENSE ≤ VDD`.
  Independently powered sources can exceed a supervisor powered by main 3V3
  during startup or decay. A higher absolute maximum does not establish behavior
  outside that recommended condition. Choose a suitable independently sensed
  supervisor or establish a compliant supply/input arrangement.
- The PDF's physical page 39, drawing 4206346-2/AA, specifies a 2.15±0.10 mm
  exposed pad. The installed RGP0020D footprint has a 2.7 mm exposed pad.
  The shared package-family name does not establish a dimensional match.
- A 67.3 kΩ/10 kΩ divider can require 3.2075 V to release reset when threshold,
  hysteresis, ±0.1% resistors and input leakage are included. That exceeds a
  3.201 V rail at −3%. A 66.5 kΩ/10 kΩ main-rail candidate releases by 3.1743 V
  under the same assumptions; ripple, temperature drift and wiring still need
  margins. A 62.4 kΩ/10 kΩ eMMC-core candidate has nominal 2.896 V falling
  threshold and 3.0041 V maximum release threshold.
- A 205 kΩ/10 kΩ input-warning divider gives nominal 8.6 V falling threshold,
  with calculated 8.4927–8.7077 V bounds and 8.9231 V maximum release. It provides
  no demonstrated time for flushing storage during abrupt removal.
- CT pins open give a 14–24 ms release delay. WDI tied low does not disable the
  watchdog; its unused WDO can be left disconnected. A proposed 10 kΩ reset
  pull-up does not satisfy the special 0.9 V startup guarantee's 15 µA load.
- The proposed reset network would reduce existing C47 from 1 µF to 10 nF,
  but that change is also deferred. EN discharge and startup waveforms require
  verification with the selected supervisor. Include its local 100 nF bypass.

The existing design does not yet provide this supervision. These calculations
are component-selection evidence, not power-loss or hardware-test results.
