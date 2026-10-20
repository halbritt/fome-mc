# Independent rail-diagnostic ADC selection review

Disposition: the ADS1119/301:1-divider design is justified as a bounded pre-emission candidate. No pinmap, configuration-byte, address, divider arithmetic or ideal schedule arithmetic error was found. The reference-drift assumption identified during review has been corrected in the final source as described below. The prepared circuit must retain the explicit powered-off leakage, transient and measurement-error holds; this review does not establish hardware safety or diagnostic validity during supply failure.

Reviewed README.md, calculate.py, calculations.json, sources.json and captured ADS1119 SBAS925A (November2018) in the pod-diagnostics-selection worktree. Executed calculate.py --check successfully after its update. No repository edits made.

## Verified device and protocol details

TI pin-function table confirms the proposed **TSSOP**, not QFN, mapping: A0=1,A1=2,RESET=3,DGND=4,AGND=5,AIN3=6,AIN2=7,REFN=8,REFP=9,AIN1=10,AIN0=11,AVDD=12,DVDD=13,DRDY=14,SDA=15,SCL=16. Local100nF or larger bypass on each supply is prescribed. Tie RESET to DVDD; section9.1.3 permits unused DRDY NC and unused analog/reference pins floating. Both supply recommended minima are2.3 V; results obtained while main supply is outside the ADC operating range are invalid, regardless of I2C ACK behavior.

Address table confirms A1/A0 DGND/DGND→0x40, DGND/DVDD→0x41 and DVDD/DGND→0x44. Static straps avoid address dependence on active bus transitions. These are seven-bit addresses, not already-shifted wire address bytes.

Configuration field table confirms0x7C/0x9C/0xBC select AIN0/1/2 relative to AGND, gain4,1000-SPS setting, single-shot, internal reference. WREG0x40, START0x08, RDATA0x10, configuration RREG0x20 and status RREG0x24 are correct. An addressed RESET can use0x06. Status bit7=1 means new data; mask reserved bits rather than demanding a fixed whole status byte. Signed16-bit interpretation is required even for single-ended readings near zero. Single-ended gain4 operation is supported; its lower common-mode endpoint is not an obstacle to these small positive signals.

## Does attenuation materially change powered-off behavior?

Yes. The earlier ordinary divider would impose approximately1–2 V while AVDD=0 and violate the analog input absolute maximum directly. With three499k upper resistors and4.99k lower resistor, the unloaded static pin range is bounded to±0.200731 V for the declared±60 V source envelope, resistor0.1% tolerance and25ppm/K allowance through125 C. That removes the **deterministic passive DC overvoltage**, leaving99.269mV to the±0.3V absolute boundary at zero AVDD. Normal powered positive inputs are also within the recommended analog range. Negative60 V faults remain outside recommended operation; no conversion accuracy is claimed there.

This is more than a cosmetic narrowing of the old violation, and is sufficient reason to prepare candidate wiring. It does not characterize the ADC's unpowered input network. The approximately4.97k Thevenin resistance means an adverse unmodeled input current of about20 microamps can consume99mV. This is a sensitivity calculation, not a datasheet leakage bound. Current flowing from the measured node into an unpowered supply can also back-power that supply while the external pin voltage remains below0.3 V. Absolute voltage compliance and negligible back-powering are separate claims.

The input-current table's±5nA entries are typical and apply under stated powered test conditions. At5nA, the approximate rail-referred offset is already5nA*4.97k*301≈7.5mV, about1.6codes; a worst-case claim cannot use this typical value as a bound. Obtain powered/unpowered current limits or measure the exact system across temperature, voltages and relevant power sequences. Existing safeguards correctly exclude resistor/capacitor faults, ground displacement, parasitic injection and an unproved60 V upstream clamp envelope. Keep those exclusions visible; three upper resistors do not automatically establish single-fault tolerance.

The first-order RC no-overshoot claim is mathematically correct only for its stated bounded source, initial condition and passive model. A rapid negative or positive fault, main-rail collapse and subsequent recovery require pin and supply-current waveforms on the actual board, not just a DC divider calculation.

## Timing and settling

1061 clock cycles divided by1.024MHz*0.98 gives1.057278ms per single shot. Unlike the continuous-mode first-conversion delay, Table4's single-shot count already starts at the latched START command; no extra28.5cycles should be added.

Per conversion the declared transactions cost27+36+18+36+45=162SCL clocks. Nine conversions cost3.645ms at400kHz. Configuring/starting all three devices and then waiting for the latest start in each round allows three overlapping conversion waits, totaling3.171835ms. Their conservative sum is6.816835ms, leaving3.183165ms of10ms. It is a feasible ideal schedule, not a worst-case implementation bound. Clock timing, bus-free/start/stop requirements, extra not-ready polls, arbitration, retries and host stalls consume additional time. An absolute deadline per requested conversion is preferable to an unbounded polling loop. A three-device round also introduces inter-device acquisition skew; timestamps must reflect each device's actual conversion interval.

The0.497342ms RC constant is correct. As an example, a5V rail step settling to half one rail-referred code requires aboutln(5/0.00235156)*tau≈3.81ms, before capacitor tolerance and ADC acquisition effects. This exceeds the3.18ms spare budget if spent entirely after the step. Do not promise a fully settled first10ms frame after every rail transition; delay/flag initial readings separately. In steady state each channel has its own permanently connected filter, so selecting a different ADC channel does not itself impose a full new external RC step. Mux/buffer settling and input leakage still require verification.

## Error-budget correction — resolved in final source

Divider ratio corners of approximately−0.695%/+0.700%, LSB15.625uV at the ADC,4.703125mV at the rail, and nominal rail codes are correct. The README appropriately declines1% rail acceptance from these readings.

However, **do not label0.15%+30ppm/C*100C=0.45% a guaranteed conservative reference allowance** without the reference-drift definition. The captured ADS1119 sheet gives30ppm/C maximum but does not define it as a pointwise slope about25 C. TI's reference training explains a full-range box method, which bounds total max-minus-min variation rather than guaranteeing linear drift from25 C: https://www.ti.com/content/dam/videos/external-videos/en-us/3/3816841626001/5783793652001.mp4/subassets/voltage-reference-overview-presentation.pdf . That general training is not device-specific confirmation of ADS1119's production calculation. Either label0.45% an illustrative linear model, obtain TI clarification, or use a provisional full−40..125 C span:0.15%+30ppm/C*165C=0.645%. The last is a more conservative box-compatible planning allowance, still not a complete measurement guarantee. ADC offset/gain typical values, loading, noise, long-term drift and assembly effects remain additional terms.

No change to the basic candidate selection is required by this correction. Stock/assembly observations were not independently re-queried and remain unqualified. Negative Hall transient protection and input-power envelope qualification remain outside what this diagnostic scan can establish.

## Final source recheck

Verified the revised README explicitly labels0.645% as conditional full-span box screening, cites TI guidance, and declines a guaranteed complete reference bound. The20uA/~100mV powered-off sensitivity example is now present. calculate.py --check passes after regeneration, and the JSON field is named reference_screening_fraction_if_full_span_box_drift. These changes close the identified wording issue; no remaining selection-study arithmetic or protocol defect was found. The settling example and all physical/error/backfeed conditions above remain recommendations for implementation and qualification.

Final reviewed source hashes:

- `README.md`: `8f53ac705faae072403e350a44ac7da8eb0aa66e0b21213d4be5c429cd1f0f61`
- `calculate.py`: `4f0221a34a0e0d721e52a560b2ea27d26358e4b7f4c3e1339332bde08101ef4a`
- `calculations.json`: `c48234b9603ed1217b44184ae1af26fe2d3b5733fecd8063ef0e649fa0fcbcba`
- `ads1119.pdf`: `32237c38221c5cb12ab000190c2a5a353198deb4adc290e6124a091950f432e7`
