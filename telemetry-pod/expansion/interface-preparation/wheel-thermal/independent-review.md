# Independent wheel pull-up thermal and diagnostic review

## Verdict

The proposed Vishay CRCW2512620RFKEG is a reasonable thermal resolution **conditional on assembled heat removal**. Four resistors under two simultaneous -24 V signal shorts dissipate approximately1.568 W, materially affecting a105 C enclosed board. The nominal1 W designation is not by itself proof of acceptable film temperature. Retain this as a source-backed candidate with explicit layout and thermal acceptance limits.

For TPS1H200A, tie DIAG_EN low and do not combine its FAULT output with SENSOR_FAULT_N. Keep the independently useful current/thermal protection while on. Monitor the switched rail separately if an ADC channel can be explicitly allocated. An ADC voltage check cannot substitute for missing open-load or current diagnostics.

## Source and part binding

Vishay document20035, revision14-Apr-2026, captured dcrcwe3.pdf: CRCW2512 P70=1.0 W, maximum film155 C, operating range-55 to155 C. Its order-code table maps620R to620 ohm, F to1%, K to100 ppm/K and EG to the2512 packaging option. Thus the proposed exact code is consistent with the family description; this review does not establish live stock or a purchased lot.

Page1 Application Information explicitly makes allowable dissipation dependent on the assembled resistor plus PCB thermal resistance and maximum film temperature. The linear standard derating curve permits1 W at70 C declining to zero at155 C. At105 C the corresponding allowance is50/85=0.58824 W per part. The family standard-operation stability table gives≤2% resistance change after8000 h under its stated rated-power/voltage conditions for stability-class1 parts. Treat the requested2% life drift as this bounded design allowance, not an unlimited field-life guarantee.

## Worst-case arithmetic

Assumptions: PRE_6V3 ≤6.5 V; continuously applied line short at-24 V; zero diode forward drop; two nominal620 ohm resistors in series; initial tolerance1%;100 ppm/K adverse TCR from25 C through155 C (1.3%); adverse life drift2%; local ambient105 C.

Conservatively adding the adverse fractions gives Rmin=620*(1-0.01-0.013-0.02)=593.34 ohm. This is slightly more conservative than multiplying the three fractions. Applied resistor-string voltage is30.5 V:

- String current:30.5/(2*593.34)=25.702 mA per channel.
- Individual resistor power:0.391955 W.
- One channel's two resistors:0.783910 W.
- Two channels' four resistors:1.567819 W.
- Per-part derating margin:0.588235-0.391955=0.196280 W, about33.4% of the derated allowance.

This is also the maximum individual resistor power over the independent resistance bounds: with the other resistor at Rmin, P=V²R/(R+Rmin)² is maximal at R=Rmin. A mismatched higher-value resistor does not exceed the equal-minimum result. Each resistor sees about15.25 V at this worst-power point, far below the family voltage rating; transient pulse ratings remain separate.

The necessary assembled thermal condition at local105 C is Rtheta_effective ≤(155-105)/0.391955=127.57 K/W for each resistor. For coupled heaters, the actual condition is P_i*Rtheta_ii + sum(P_j*Rtheta_ij) + other-board heating ≤50 K; four independent single-resistor checks do not prove it.

The1 W/70 C rating corresponds to an85 K/W illustrative reference heat path. If the actual assembly achieved that self-heating figure and had no mutual heating, film temperature would be138.32 C, leaving16.68 C for local/mutual heating. **85 K/W is inferred from rating endpoints, not a guaranteed package thermal-resistance specification.** Do not add an already-accounted local105 C board rise twice. Measure or model the actual solder pads, copper, placement spacing, enclosure and neighboring load. The accepted thermal design must address both channels faulted together plus the rest of the active pod power dissipation.

The arithmetic is retained in independent-calculations.json, with source hash. It does not qualify the pull-up diodes, sensor output transistor or protected power switch against this fault; those require their own current/temperature/voltage checks. Shared switch current limiting may not react to approximately51.4 mA added fault load.

## TPS1H200A diagnostics and protection

Captured TI TPS1H200A-Q1 SLVSEE0E, sections6.3.4–6.3.6 and electrical diagnostic table:

- On-state open-load threshold is10 mA typical,20 mA maximum; below threshold for200–450 us triggers the diagnostic.
- A GS100502 consumes at most6 mA, and its approximately5 mA pull-up load is intermittent. Even two sensors can draw below20 mA when their outputs are high. Therefore normal valid operation can assert FAULT; tying FAULT into the general sensor-fault line creates false fault indications.
- Table6-3 explicitly states DIAG_EN low, IN on: **diagnostics disabled, full protections**. With DIAG_EN low and IN off: **diagnostics disabled, no protection**. Preserve this off-state limitation exactly; do not claim fully protected off-state behavior.

Recommended implementation: DIAG_EN hard low, FAULT NC, independently controlled IN and correctly selected CL/DELAY mode. Current limit, on-state thermal shutdown and related on-state protection continue to operate. Firmware loses the FAULT notification and cannot distinguish current limiting, thermal shutdown or an unpowered upstream source solely from the switch. Do not mask FAULT in software while physically wiring it into a shared open-drain fault net.

If a free acquisition channel is explicitly identified, add a divided measurement of the **switched output rail**, compare it to commanded IN and upstream voltage, and allow startup/deglitch timing. The ADC interface itself needs safe maximum-voltage and powered-off analysis. Existing eight analog assignments must not be silently repurposed. Rail voltage supervision detects loss/sag but not an unplugged low-current sensor whose unloaded rail stays high. Use pulse plausibility and explicit sensor-disconnected handling for that separate fault class.

Do not add a dummy20+ mA load merely to satisfy open-load detection: at6.3 V it wastes at least0.126 W continuously and makes true sensor disconnection even less observable. If per-sensor current/open-load detection becomes a hard requirement, choose a switch or external current-monitor topology whose thresholds are guaranteed below the sensor's **minimum** valid current; the ZF sheet currently provides only typical/max supply current, so a new part alone cannot establish that discrimination.

TPS1H200A's reverse-current section also requires external measures for reverse polarity/backfeed. DIAG_EN low does not create reverse-current blocking. The Hall signal pull-up isolation and switched rail reverse-current design remain necessary independently of diagnostics.

No board-temperature measurement, fault test, final native design or production qualification is claimed.

## Check of implementation calculation

Independently inspected and executed the parent calculate.py. Its multiplicative tolerance/TCR/drift model gives Rmin593.704188 ohm, each power0.391714 W, total1.566858 W and required assembled thermal resistance≤127.644 K/W at105 C. These are arithmetically correct under the declared sequential model. The additive review bound above is slightly more conservative, not a defect in the parent arithmetic. Both give the same disposition. At125 C the nominal derated allowance is only0.352941 W, so this continuous fault envelope **does not fit the family curve at125 C**. The nominal-curve local-temperature ceiling is approximately121.7 C; real assembly/coupling can lower it. Preserve the105 C operating scope explicitly. Parent reports exact catalog stock but assemblyComponentFlag=false; qualified assembly availability remains open. No stock read was independently performed in this subreview.
