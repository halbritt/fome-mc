# Hall pull-up fault envelope and supply diagnostics

Use two **620 ohm CRCW2512620RFKEG (2512)** candidates in series for each Hall
pull-up. This preserves the existing 1.24 kohm circuit proposal while providing
more thermal capacity. Exact assembly binding and board thermal validation remain
open. The preceding wheel review's unspecified hot-rated resistors are replaced
by this concrete candidate; no native circuit change is implied.

The [Vishay source](https://www.vishay.com/docs/20035/dcrcwe3.pdf), document 20035,
14-Apr-2026, specifies the family rating and requires the assembled resistor and
PCB to keep film temperature within its limit. Its nominal derating curve gives
0.588 W at 105 C for this 1 W at 70 C case. A footprint's package rating alone does
not prove the assembled thermal path.

`calculate.py` reproduces `calculation.json`. With a provisional rail ceiling of
6.5 V, a continuous -24 V signal short, zero diode drop, 1% initial tolerance,
100 ppm/K through 155 C and an additional 2% life-drift allowance:

| Calculated quantity | Result |
| --- | ---: |
| Minimum individual resistance | 593.704 ohm |
| Maximum channel current | 25.686 mA |
| Maximum dissipation per resistor | 0.392 W |
| Four-resistor dissipation, both channels faulted | 1.567 W |
| Required film-to-local-ambient thermal resistance at 105 C | at most 127.6 K/W |

The resistor-power maximum occurs with both series resistors at their minimum
resistance. The life-drift allowance is a design budget, not an indefinite-life
guarantee. The 6.5 V ceiling must still be established for the protected rail.
At 125 C the nominal derated rating is only 0.353 W: this proposal does **not**
support the same continuous fault there. Local heating from all four resistors,
the diodes and other circuitry must be included. Place the four larger resistors
with thermal separation from the IMU, precision reference and antenna region;
verify enclosure temperature and film limits under simultaneous faults.

The stock snapshot identifies exact C3988368, with 1000 units reported on
2026-10-20. Its raw response has `assemblyComponentFlag=false`; catalog stock does
not establish JLC assembly eligibility. No purchase or assembly reservation was
made. If this part cannot be assembled, an alternate needs the same hot-power,
voltage, tolerance and thermal review; do not shrink the footprint by default.

## TPS1H200A-Q1 diagnostic restriction

The captured [TI source](../sources/tps1h200a-q1.pdf), electrical characteristics
and section 6.3.4/Table 6-3, gives an on-state open-load threshold of 10 mA typical,
20 mA maximum. A healthy GS100502 may draw less than that, even with its pull-up.
Consequently, do not wire this switch's FAULT output directly into
`SENSOR_FAULT_N` for an individually powered Hall sensor.

For this switch candidate, use **DIAG_EN low, IN high during operation**, and
leave FAULT unconnected. TI explicitly retains full protections in that state;
with both DIAG_EN and IN low it specifies no protection. Monitor each switched
rail independently through the planned diagnostics ADC and record missing pulses
separately. Rail voltage alone cannot distinguish an unplugged sensor from a
stationary wheel. This is a design choice for the pending branch circuit, not an
implemented diagnostic function. A later need for reliable open-wire detection
requires additional circuitry or a different switch.

Branch current-limit/retry behavior, reverse-current blocking, supply headroom,
exact diodes and sensor output/pulse specifications remain separate design work.
The shared switch cannot be assumed to trip on the 25.7 mA signal-fault current.
