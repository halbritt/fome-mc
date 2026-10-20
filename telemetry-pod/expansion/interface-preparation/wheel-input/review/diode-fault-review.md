# Exact BAV199 candidate fault review

Proceed with a **bounded prepared-circuit candidate**, retaining negative-edge and hot fault survival as release holds. Static resistor/diode limits support further work; they do not establish dynamic protection of the LM2903B input.

Source: wheel-input/bav199.pdf, Nexperia BAV199 product datasheet1 September2020, Tables2,5–7. Exact proposed catalog binding is BAV199,215 / C40919. Do not infer current AEC status from this old sheet; this review treats the selected ordinary BAV199 as a catalog part. Pinmap1=A1,3=K1/A2,2=K2 is confirmed. Protected wheel supply feeds two620 ohm resistors then pin1; pin3 is the external wheel line; pin2 feeds the10k/10k conditioner. There is one such package per wheel.

## Continuous negative signal short

At protected supply≤6.5 V, signal−24 V and the prior worst-case resistor lower bound, zero diode drop gives25.7 mA through diode1 and the pull-up pair. Diode2 is reverse-biased by approximately24 V and isolates the divider in steady state. These are below the75 V continuous reverse and160 mA single-diode forward absolute limits, but the160 mA limit is not an ambient-independent thermal allowance.

The source states150 C maximum junction,500 K/W junction-to-ambient for its specified single-diode FR4 mounting, and250 mW at25 C. At105 C this thermal model permits90 mW; at125 C,50 mW. As an illustrative—not guaranteed across temperature—estimate using the1.1 V maximum specified at50 mA/25 C, diode dissipation is25.7mA*1.1V=28.3 mW. Junction rise would be14.1 C:119.1 C at105 C local ambient,139.1 C at125 C. The reverse-biased companion's24V*80nA≈1.9 microwatts is negligible in this DC estimate. The80 nA bound is specified at75 V/150 C; use it as a conservative design allowance, not an independently characterized24 V waveform.

For an actual25.7 mA forward current at125 C local ambient and500 K/W assembly, keeping junction below150 C requires Vf≤1.945 V. This is a useful acceptance condition. The sheet does not explicitly guarantee maximum Vf at every temperature, so the25 C1.1 V entry must not be promoted to a hot/cold specification. Verify actual diode voltage, local temperature and assembly thermal behavior. Heating from the nearby four pull-up resistors (about1.57 W for two faults) must be included: at125 C only about10.9 C of additional local heating remains in the illustrative estimate. Do not substitute resistor film temperature for the diode's local ambient or count the same board rise twice.

The protected TPS26625 wheel branch has a minimum current limit near145 mA, well above this25.7 mA signal-fault current. It will not necessarily trip; the resistor and diode thermal requirements remain continuous. This board-side analysis does not prove the Hall sensor's output transistor survives a−24 V signal fault.

## Positive signal short and power-off behavior

At a+24 V external line, diode1 blocks positive backfeed through the pull-up into the protected supply (including when that supply is off). Diode2 conducts into the10k+10k divider; comparator input is approximately12 V minus half its forward drop, below the LM2903B supply-independent38 V absolute limit. Each10k resistor dissipates about14.4 mW when diode drop is conservatively ignored. The comparator's other input remains in its normal common-mode range while powered. Only the LM2903B **B** version and exact stated operating conditions are covered by this analysis.

With the whole pod off, the divider remains a ground return and neither diode intentionally connects the fault to3.3 V. Do not treat this as a guaranteed valid unpowered comparator output. Sensor-disconnected status and power-invalid suppression remain firmware requirements. Positive/negative line faults are distinct from a fault on the protected sensor supply lead; do not use the TPS26625 supply protection as evidence of signal-pin protection.

## Negative transient is the material unresolved issue

The BAV199 is a medium-speed diode: its maximum3 microsecond reverse recovery applies to10 mA forward/reverse test currents,100 ohm load and25 C. Its2 pF capacitance is typical, not maximum. Neither number bounds recovery or displacement current for this exact~0.3 mA divider, automotive temperature range and connector surge waveform.

When the line changes rapidly from a positive level to−24 V, diode2 can briefly conduct reverse recovery current or couple charge through junction capacitance before it blocks. The10k input resistor limits current but **does not guarantee the LM2903B input stays above−0.3 V**. Its220 pF capacitor may delay the excursion; it is not a clamp. The LM2903B negative input current absolute rating does not waive the negative voltage limit. An ideal-diode DC model or3 us nominal blanking cannot establish safe input voltage.

Bench/simulation acceptance must capture the actual comparator pin during hot/cold negative steps, defined connector ESD/surge waveforms, removal of a fault and power sequencing, with the intended cable and board parasitics. Either demonstrate pin≥−0.3 V under the declared envelope or add a source-bounded negative clamp/alternative conditioning circuit. No transient fault survival claim is permitted before this closes. Sampling firmware cannot prevent a hardware input overstress event.

## Remaining signal-quality gates

ZF's GS100502 sheet lacks guaranteed VOL, minimum high/low pulse width, powered-off leakage and signal short-fault ratings. Diode forward drop also shifts the effective connector switching thresholds and lowers the diode-isolated pull-up high level. The existing220 pF filter and comparator typical propagation delay are compatible with exploring15 kHz, but cannot prove pulse accuracy or chatter immunity without those endpoints. A15 kHz period is66.7 us; it does not imply33 us minimum pulse width.

Exact parts, effective capacitance, grounding, native pin wiring and physical layout still require review. Prepared source may proceed with these holds explicitly attached; it is not ready for a fault-survival or hardware qualification claim.
