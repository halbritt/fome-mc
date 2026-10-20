# GSXR wheel fit and sensor-selection boundary

Owner clarification, 2026-10-20: the SV650 has GSXR wheels, which would need
modification to suit wheel-speed sensing. No wheel year/model, ring attachment
dimensions, available clearance or existing ABS hardware was supplied.
Treat front and rear as separate custom fits. Do not infer compatibility with
stock SV650 rings or brackets. This clarification supplements Revision 3;
the historical captured specification and compiled map remain unchanged.

The existing GS100502 is a candidate, not a selected sensor. Its mechanical
target guidance needs attention before committing to that part:

| ZF guidance | Value |
| --- | --- |
| Preferred target material | Low-carbon cold-rolled steel |
| Tooth height | 5.0 mm |
| Tooth width | 2.5 mm |
| Space between teeth | 10 mm |
| Target thickness | 6.35 mm |
| Typical air gap, with the recommended target | 1.5 mm |

Source: [ZF GS1005–GS1007 datasheet, 2024-09-11, pages 1–2](https://switches-sensors.zf.com/wp-content/uploads/2024/09/Datasheet_GS1005-GS1007_EN_2024-09-11.pdf),
also retained in `../sources/GS1005-GS1007.pdf`. ZF allows that smaller target
dimensions may work but requires application testing. These guidelines do not
qualify a thin OEM ABS ring, stainless brake rotor or smaller air-gap tolerance.

For an initial circumferential pitch screen only, 2.5 mm tooth width plus
10 mm gap gives 12.5 mm pitch. At a sensing radius of 60 mm,
`floor(2*pi*60/12.5) = 30` teeth fit this pitch screen; 48 teeth would need
at least `48*12.5/(2*pi) = 95.49 mm` radius. These are geometric illustrations,
not measured wheel dimensions, a complete tooth design or qualified targets.
A thin, high-tooth-count ring therefore cannot be assumed compatible with
this sensor merely because its electrical output is Hall/open-collector.

Before selecting a sensor and drawing production rings/brackets, record:

- Exact front/rear wheel identification, brake carriers, fork and rear caliper/
  swingarm arrangement; existing mounting faces and hole patterns.
- Available sensing radius, radial and axial envelope, target thickness,
  fastener clearance, and full-rotation/suspension clearance.
- Ring and bearing runout, bracket deflection and thermal movement, so the
  complete minimum/maximum sensing-gap range is known.
- Loaded rolling circumference and intended speed range. Derive pulse rate as
  `teeth * speed_m_per_s / circumference_m`; verify minimum high/low times
  against tooth geometry, sensor, cable and conditioner.

Keep existing wheel sensor supply and LM2903B conditioner limits open:
the retained ZF sheet does not provide guaranteed VOL or minimum pulse widths,
and the diode-isolated pull-up is not its unmodified application circuit.
The negative-transient comparator-input hold also remains. No wheel machining,
bracket attachment, sensor purchase or hardware qualification is established.
