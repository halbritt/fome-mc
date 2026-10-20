# R60 exact-part candidate and conditional threshold bounds

R60 remains the unbound 31.3 kohm source component. This study identifies an
exact 31.6 kohm candidate and quantifies the behavior change before any source
substitution. No component, net, footprint, binding or firmware contract changes.

YAGEO's captured manufacturer sheet identifies **RT0603BRD0731K6L**, 31.6 kohm,
0.1%, ±25 ppm/K, 0603, −55 to 155 °C, 0.1 W at 70 °C and a separate 75 V
continuous ceiling. Body dimensions are 1.6±0.1 × 0.8±0.1 × 0.45±0.1 mm.
The exact-ID supplier capture identifies **C705766**, with 3818 in stock at
2026-10-20T14:52:13.811782Z and `assemblyComponentFlag=false`. This is a dated
observation, not an assembly qualification, reservation or purchase.

Sources, hashes and raw supplier response are retained. The bottom resistor
R61 is already bound to RT0603BRD0710KL, 10 kohm, 0.1%, ±25 ppm/K; its existing
manufacturer capture is also pinned. The 31.2 and 31.3 kohm rows are numerical
comparisons using the same assumed tolerance/TCR, not newly selected parts.
The unbound 31.3 kohm source specifies 0.1% only; its 25 ppm/K row is not a
guaranteed bound for an existing selected component.

## Static comparison

Using the retained TI TPS3890 SLVSD65A specification, the nominal falling
threshold is `1.15 × (1 + R60/R61)`. Moving 31.3 to 31.6 kohm raises it from
4.7495 to 4.784 V, a **34.5 mV increase**. No silent nominal rounding is proposed.

At local resistor temperatures within −40 to 125 °C:

| Top resistor | Nominal falling | Conditional falling interval | Conditional maximum rising |
| --- | --- | --- | --- |
| 31.2 kohm | 4.7380 V | 4.661829–4.814880 V | 4.854577 V |
| 31.3 kohm, current | 4.7495 V | 4.673122–4.826590 V | 4.866383 V |
| 31.6 kohm, candidate | 4.7840 V | 4.707000–4.861718 V | 4.901801 V |

The calculation combines initial resistor tolerance and temperature drift
multiplicatively, with independent worst signs for each resistor. A reference
temperature anywhere from 20 to 25 °C is assumed conservatively; this interval
is a modeling assumption, not supplied by the exact-part sheet. The maximum
temperature excursion is 105 K. No matched-resistor drift cancellation is used.
TI specifies ±1% threshold accuracy and 0.825% maximum relative hysteresis.
The rising bound conservatively compounds both maxima. It is an outer bound,
not a claim that all these extrema occur together.

The divider equation includes sense current as `Vrail = Vsense × (1 + Rt/Rb)
+ Isense × Rt`. Both current signs are included conservatively. TI lists a
100 nA maximum for TPS389001 **at VSENSE=5 V**. Applying ±100 nA near the
1.15 V threshold is an explicit, unresolved assumption; the table is not a
guaranteed device limit at threshold.

For illustration only, the candidate's maximum release threshold is 48.199 mV
below a 4.95 V healthy rail. The actual delivered healthy minimum after regulator
error, tracking, current-dependent switch/drop, wiring and ripple is not yet
established. Therefore this margin does **not** close the selection decision.
The candidate would require a justified healthy minimum above its qualified
maximum release threshold, with an allocated dynamic noise margin. The desired
latest fault-assertion voltage also needs a downstream sensor requirement.

## Disposition and reproduction

Keep R60 unchanged until the delivered rail envelope and threshold-current
assumption are resolved. The candidate preserves the existing 0603 footprint
identifier but still needs ordinary land-pattern/assembly qualification.
Local resistor temperatures, not enclosure ambient, define the calculation;
self-heating and coupling are not qualified. Lifetime/load-life drift and
solder-induced resistance shifts are excluded from these bounds. Timing, startup, repeated dips,
noise, reset recovery and bench waveforms remain open. This study neither
closes those gates nor establishes a safe sensor operating range.

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/sensor-threshold/calculate.py
```

Output must reproduce `results.json`. The script verifies pinned source bytes
and exact-ID capture, and checks that the current R60/R61 baseline still applies.
The doctrine retrieval gate passed (packet `pkt-aaa70a216562d077`), but returned
no specifically matched hardware concepts. This analysis relies on manufacturer
and project evidence; no doctrine-backed electrical acceptance is claimed.

Independent review reproduced all numerical results, checked manufacturer
conditions and confirmed this disposition: sufficient as a conditional study,
insufficient to select or bind R60.
