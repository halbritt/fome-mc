# Independent thermistor excitation review

Verdict: suitable as a prepared circuit candidate, with the conditions below retained. No graph/pin defect found. This does not qualify any thermistor, temperature accuracy, fault survival, powered-off system behavior, native ERC or assembly. The earlier3.0V LM4040/330Ω proposal is superseded by the higher-current fixed2.495V TL431 circuit.

## Why the selected architecture is defensible

The selected circuit takes power downstream of protected POD_5V_AUX, through one BAV199 junction and two200Ω bias resistors, into TL431BQDBZR with REF tied to cathode. Four optional10k pullups connect through normally open JP2–5. A100k bleeder terminates the upstream auxiliary node; U28 AIN3 observes excitation through the301:1 divider.

Primary TI TL431 datasheet SLVS543S §6.4 specifies1–100mA recommended cathode current and−40..125°C Q-grade operation. §6.1 gives150°C maximum junction temperature. DBZ pinning on p.3 is1 cathode,2 REF,3 anode. The exact TL431BQDBZR appears in the ordering table. Do not substitute TL432's different pinout. §6.13 specifies2.483..2.507V at25°C,10mA, and34mV maximum full-temperature reference deviation. Its0.7mA Imin entry is under the table's25°C default; it is not explicitly a full-temperature guarantee. The budget therefore retains the recommended1mA minimum.

The2.4..2.586V excitation range used in calculations is a planning guardband, not an independently guaranteed DC error envelope. The upper value includes initial tolerance, full-temperature deviation and a current-change allowance based on the0.5Ω dynamic-impedance entry over1–100mA. That dynamic specification and its frequency/test conditions must not be presented as a complete calibrated DC accuracy specification. Aging, hysteresis and application behavior remain additional limits.

The original LM4040C30QDBZR is a real−40..125°C3V candidate (TI SLOS456Q §6.13:±45mV at100µA full range,82µA maximum minimum operating current). However, its15mA recommended maximum is exceeded by AUX6.4V plus four16V inputs with330Ω:15.747mA under the declared tolerance case. A power-pin16V fault is worse. TL431LI also has only15mA recommended maximum (18mA absolute), so it is not the higher-current substitute. LM66100's5.5V recommended/6V absolute input does not tolerate an assumed AUX bound derived merely from U30's6.393V worst cutoff, much less an external power-pin fault. Its reverse-leakage maximum is specified only through105°C. Those alternatives do not close the requested envelope as proposed.

## Conditional current and thermal budget

Latest selected case: two200Ω CRCW2512-HP resistors, each1%,100ppm/K. Budget symmetric product bounds±2.313% through155°C film temperature; four10k pullups and monitor resistors use±0.425325% through155°C film temperature. No life drift is included. AUX normal minimum4.95V is conditional on the still-unqualified auxiliary supply delivering that voltage. Excitation guardband2.4..2.586V as above; monitor load included.

With all four inputs grounded and diodeVF≤1.5V, minimum shunt current is1.070621mA. The calculated diode ceiling for1mA is1.528902V. This is meaningful but finite headroom; verify cold diode VF, actual upstream minimum, resistor drift and excitation behavior together. The BAV199 data sheet's forward-voltage maxima are at25°C, so it does not establishVF≤1.5V across the application temperature range.

Zero diode drop conservatively maximizes positive-fault current:

| AUX / four signal voltages | Maximum shunt current | Maximum shunt power | Each bias resistor | Each10k pullup |
|---|---:|---:|---:|---:|
|5.05V /16V|12.245mA|30.24mW|8.98mW|18.57mW|
|6.4V /16V|15.700mA|39.18mW|20.47mW|18.57mW|
|16V /16V|40.268mA|102.71mW|236.67mW|18.57mW|
|24V /24V|63.955mA|163.96mW|597.01mW|46.86mW|

These are simultaneous DC load cases for this new circuit, not proof of system fault survival. Actual fault duration, input clamps, upstream sources, diode switching and parasitic coupling remain unqualified.

Vishay doc20043 confirms CRCW2512-HP P70=1.5W and maximum film temperature155°C. Linear ambient derating gives0.882W at105°C and0.529W at125°C. Thus the all24V case fits the105°C nominal-rating screen but not125°C local ambient; board heat removal and mutual heating must still be established. It dissipates about1.19W in the two bias resistors alone. The alternative rating based on terminal temperature requires its own terminal-temperature evidence and is not assumed here. For TL431's163.96mW case, keeping junction≤150°C at local105°C requires assembled thermal resistance≤274.5K/W before mutual-heating allowances; the datasheet206K/W DBZ figure is a standardized-board metric, not the actual PCB guarantee. Check the10k0603 resistor's own exact derating and voltage rating as well;24V fault power is46.86mW each.

## Blocking, startup and stability

BAV199,215 uses1=A1,3=K1/A2 and2=K2. Selected direction is AUX→pin1→pin3→bias;pin2 is NC. The retained Nexperia2020 sheet specifies75V reverse working voltage,150°C junction limit and80nA reverse-current maximum at75V/150°C. It does not guarantee zero reverse current. At that leakage screening value,100k bleed gives about8mV, whereas a floating auxiliary node could charge. Other existing backfeed sources and diode dynamic recovery remain outside this simple estimate. The diode blocks a reverse supply fault within its voltage rating; neither this nor the shunt resolves existing ADC/input powered-off paths.

A10µF shunt capacitor is plausible but remains an effective-capacitance/ESR and stability candidate. TL431 figure6-18 specifically covers B/Q/SOT-23 devices; its unstable-region curves are at25°C. Do not confuse it with the other TL431-family figure or assume nominal10µF is retained after voltage, tolerance and temperature effects. Startup/settling and stability require validation across current, temperature and fault conditions, including the connected cables and four optional branches. Do not sample immediately after excitation starts or a fault clears.

## Measurement implications

The2.495V rail is independent of the sensor5V-derived MCP3208 reference. It is not ratiometric merely because its power comes from that rail. Excitation and reference monitoring/calibration can support interpretation, but their errors and timing must be included.

Each existing10k/10k input divider presents20k loading to the thermistor. For pullupRp=10k, thermistorR, excitationE:

`Vsignal = E * (R || 20k) / (Rp + (R || 20k))`.

The ADC seesVsignal/2. At nominal2.495V excitation and5V sensor rail, an open thermistor yields1.6633V at the connector and about1363 MCP3208 codes; a10k thermistor yields0.998V and about818 codes. These are illustrative resistance cases, not a selected sensor/temperature range. Maximum nominal thermistor dissipation is about103.75µW atR=6.667k; convert that into temperature error only with the sensor's dissipation constant and mounting environment.

The existing100nF filter sees a0.5..0.667ms time constant with enabled10k pullup, before tolerances. A full-scale step settling to half a12-bit LSB takes up to approximately6.01ms nominal, in addition to excitation startup and other dynamics.200Hz sampling is not evidence that a changed input or enabled excitation settles within each5ms interval.

U28 AIN3 is physical pin6. With the existing gain4/1000SPS/single-shot/internal-reference scheme, its configuration is0xDC. The301:1 monitor provides about4.703mV of excitation per ADC code, roughly0.1885% of2.495V per code before all other errors. It supports a coarse monitor, not an assumed precision temperature calibration. Ten conversions distributed across the three diagnostic devices need four overlapped conversion rounds; the earlier idealized bus/conversion calculation becomes8.279ms, before software overhead and settling. Firmware scheduling remains unimplemented/unqualified.

## Prepared source verification

Ran the live main integration prepare.py independently and confirmed its generated base was byte-identical to integrated-inputs-v1. The independent checker reconstructs the allowed19-component delta, preserves old components and complete net memberships, checks exact new values/footprints/symbol bindings, consumes only U28 pin6 NC and adds D105 pin2 NC. It parses whole authored libraries, verifies library hashes and physical TL431/BAV199/ADS1119 functions, and preserves prior captures except the intended intent/layout and obsolete integration receipt.1526 checks pass.

Negative controls reject reversed diode connections, REF grounded, pullup tied to upstream sensor5V and a malformed complete library even after its manifest hash is updated. No producer helper is imported. All jumpers remain open by default and retain the existing captured jumper symbol/footprint. Existing JP1/copper-feature assembly-policy and native-emission gates remain; this source check does not bypass them.

Artifacts: check_prepared_thermistor.py OLD_INPUTS NEW_INPUTS REPORT; negative_probes.py OLD_INPUTS NEW_INPUTS REPORT; prepared-report.json; negative-probes.json; calculate.py and calculations.json. Use agent_ee on PYTHONPATH for source parsing. No repository circuit source was edited by the reviewer.

## Final frozen-source reconciliation

Reviewed the final worktree README and calculation model. C128 now has plain value `10uF 16V X7R`; effective-capacitance/stability holds remain in the README and this review. The independent expectation was updated only for that intended value change, then rerun against the frozen worktree inputs:1526 checks pass and all four negative controls remain rejected.

Agreed with extending the precision-resistor TCR allowance through155°C film temperature:±0.425325% for pullups and the monitor divider, while bias uses±2.313%. The conservative minimum monitor-divider resistance is included. Independently reproduced1.070621245mA minimum shunt,1.528901886V diode ceiling,40.268277mA all16V and63.955499mA all24V currents, and0.163964738W maximum all24V shunt dissipation. The older3V/330Ω study calculation retains its separately declared earlier resistor assumptions; it does not describe the final design.

The source calculation --check passes. Its loaded-divider inverse matches the independently derived KCL expression, and invalid/open/short readings are rejected rather than turned into temperature. README limitations correctly distinguish the25°C dynamic-impedance entry from a full-temperature DC guarantee. No new material issue found; verdict remains prepared-only.

Final arithmetic correction: resistor initial tolerance and TCR bounds are multiplied, not added. The symmetric allowances are`(1.01×1.013)−1=0.02313` for bias and`(1.001×1.00325)−1=0.00425325` for precision resistors. Applying these allowances in both directions is conservative for the corresponding lower product. Independent results match the final source model; its --check passes. Circuit/intent and checker are unchanged, so the retained graph and negative-control results remain applicable.
