# Schmitt NAND silent gate and CAN protection review

The proposed equation S = NOT(MCU_EN AND GPIO0_TX_ENABLE) improves the previous circuit: while the gate supply is valid, MCU_EN low forces the transceiver silent even if the MCP controller retains GPIO0 high. A 10 kohm GPIO0 pulldown establishes disabled transmit while the controller pin is an input. This is a suitable candidate for emission, with the documented limitation that MCU_EN rising can immediately re-enable transmit if GPIO0 retained high. It is not latched silence throughout firmware restart.

## Gate source and EN loading

Independently captured https://www.ti.com/lit/ds/symlink/sn74lvc1g132.pdf into this review directory; document SCES546E, revised August 2026. DBV pin map: A1, B2, GND3, Y4, VCC5. Supply the gate from main 3.3 V and add local 100 nF bypass. A/B are interchangeable. Schmitt inputs support the slow RC transition; an ordinary LVC NAND is not a drop-in substitute for the 1 ms MCU_EN edge.

The current datasheet page 6 gives input leakage ±1 microamp at VI=5.5 V or ground, over -40 to +125 C, with VCC 1.65–5.5 V. This is smaller than the initially hypothesized 5 microamps. Using that leakage allowance plus two supervisor output leakages of 250 nA and the prior ESP input allowance of 50 nA gives 1.55 microamps total. A 100 kohm pull-up drops 0.155 V; at 3.201 V supply the illustrative minimum EN high is 3.046 V. Include actual resistor tolerance and confirm ESP input specifications remain applicable. Input leakage is characterized at the stated endpoint test voltages, not a complete EN waveform model.

At normal valid supply, the gate's output high with ≤100 microamp load is at least VCC-0.1 V, ample for TJA S threshold 0.7*VIO. The low output is also comfortably below TJA S maximum 0.3*VIO at the small load. A retained optional S pull-up adds ~0.33 mA low-state load; that is within the gate's drive rating. GPIO0 high sources ~0.33 mA through its 10 kohm pulldown, also small compared with the MCP output rating. Configure GPIO mode and disable automatic XSTBY as before. Firmware sequence is now LAT0=0, then output enable, and LAT0=1 only after initialization; use single-byte IOCON writes throughout.

Do not extend the above leakage calculation to the supervisor's 0.8 V POR test point. Gate electrical guarantees start at VCC=1.65 V; Ioff is specified at VCC=0, not all intermediate voltages. The pull-up alone draws at most 8 microamps at 0.8 V, but the additional gate input behavior there is not bounded by those two specifications. Therefore the TPS3890 15 microamp POR sink-load margin is not fully proved at that voltage. Normal held-reset operation above the gate minimum is supported; actual power-ramp and reset waveforms remain a required bench check. Also do not claim valid logic for the gate below its supply range or for every transceiver undervoltage transition.

## TVS

Nexperia PESD2CANFD24V-T captured source page 1/Table 1 and page 4/Table 6 give 24 V stand-off and maximum 42 V clamp at 1 A, 8/20 microseconds, 25 C. The 175 C ambient/junction ratings support selection at the intended temperature but do not extend the 25 C clamping guarantee to 105 C. This is a reasonable CAN protection candidate, not proof of protection against every harness surge or ESD pulse.

Pin map from Table 2: pad1 K1 and pad2 K2 to the two CAN lines; pad3 common cathode to local protection ground. This is a bidirectional CAN protection topology; do not infer ordinary single unidirectional diode wiring from the word cathode. Keep each line's protection return short and avoid steering discharge through sensitive ADC/clock return paths. Comparing 42 V with TJA's ±58 V absolute bus limit leaves nominal voltage space at the specified pulse, but PCB inductance, hot clamping, pulse current/shape, repeated pulses and transceiver transient ratings still determine survival. An absolute maximum comparison does not qualify EMC.

## Termination

A 120 ohm resistor in series with a normally open solder jumper across CANH/CANL is suitable to make pod termination explicit. Both parts may be assembled; default open means the pod is not a bus endpoint until deliberately bridged. Closing the jumper is appropriate only when the pod occupies an end and the other end is already terminated. The path is series, not a permanent parallel resistor with a cosmetic jumper. This avoids relying on an unrepresented DNP assembly assumption. Select resistor tolerance/power/temperature and verify worst-case dominant dissipation plus any required fault survival; no prolonged battery-short survival follows from the TVS selection.

Native wiring, footprint and preservation checks remain pending emission. No circuit qualification or release acceptance is claimed.
