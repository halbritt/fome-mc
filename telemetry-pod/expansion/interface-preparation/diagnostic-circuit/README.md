# Prepared rail diagnostic circuit

This candidate layers three ADS1119IPWR devices and eight rail dividers on the
prepared wheel-input circuit. It implements the reviewed
[diagnostic selection](../diagnostics/README.md) for the rails that presently
exist. Native emission, ERC, layout and hardware qualification remain pending.
It does not replace the actual telemetry project.

The auxiliary 5 V branch is still absent from the base. U28 AIN2 remains explicitly
NC for its future monitor; J1 positions21/22 and their power/return implementation
are not changed here. Firmware must report the auxiliary rail as unimplemented,
not zero volts or a valid reading. The final target remains nine monitored rails
and the protected auxiliary supply required by expansion/README.md.

| ADC / seven-bit address | AIN0 / pin11 | AIN1 / pin10 | AIN2 / pin7 |
| --- | --- | --- | --- |
| U27 / 0x40 | POD_12V_PROTECTED | PRE_6V3 | +3V3 |
| U28 / 0x41 | EMMC_VCC_3V3 | POD_5V_SENSOR | NC, reserved for POD_5V_AUX |
| U29 / 0x44 | POD_WHEEL_FRONT_SUPPLY | POD_WHEEL_REAR_SUPPLY | POD_TIRE_SUPPLY |

U27 has A1/A0 grounded, U28 has A1 grounded/A0 at3.3 V, and U29 has A1 at3.3 V/A0
grounded. All devices use main3.3 V on AVDD/DVDD and RESET; both grounds join
GND. AIN3, REFP, REFN and DRDY are NC. The authored symbol uses TI's TSSOP PW
pinmap; the QFN pinmap is different. Exact part/footprint binding remains open.

ESP32 module pin22/GPIO14 now carries DIAG_I2C_SDA and pin23/GPIO21 carries
DIAG_I2C_SCL. Their former NC assignments are removed. No existing functional
connection is moved. R160/R161 are2.2 kohm1%,100ppm/C pull-ups to main3.3 V.
Each ADC gets two separate1 uF50 V X7R0805 bypass capacitors, C118–C123, for
placement beside its AVDD and DVDD pins. Confirm at least100 nF effective
capacitance at each supply pin across bias, temperature, tolerance and aging.
Nominal1 uF is a candidate value, not that confirmation.

## Divider map

Each row contains three series499 kohm upper resistors and one4.99 kohm lower
resistor to ground, all0.1%,25ppm/C. A100 nF50 V X7R0603 filter capacitor joins
the ADC input to ground. The three upper nodes use independent named nets;
none of the resistor segments is bypassed.

| ADC input | Upper / upper / upper / lower resistors | Filter |
| --- | --- | --- |
| U27 AIN0 | R128 / R129 / R130 / R131 | C110 |
| U27 AIN1 | R132 / R133 / R134 / R135 | C111 |
| U27 AIN2 | R136 / R137 / R138 / R139 | C112 |
| U28 AIN0 | R140 / R141 / R142 / R143 | C113 |
| U28 AIN1 | R144 / R145 / R146 / R147 | C114 |
| U29 AIN0 | R148 / R149 / R150 / R151 | C115 |
| U29 AIN1 | R152 / R153 / R154 / R155 | C116 |
| U29 AIN2 | R156 / R157 / R158 / R159 | C117 |

The eight dividers retain the301:1 nominal attenuation from the study. Under its
conditional +/-60 V node envelope, the passive unloaded model gives at most
+/-0.200731 V at an ADC input through125 C. That envelope is not proof of the
upstream transient clamp, and the calculation excludes ADC leakage, parasitics,
ground shift, resistor/capacitor faults and aging. Powered-off backfeed remains
unqualified. No new clamp or power-good claim is introduced here.

Use gain4 and the internal reference; nominal rail resolution is4.703125 mV per
code. This observes gross rail behavior, not compliance with the5 V +/-1%
requirement. Error, reference-drift and calibration limitations from the study
remain. A5 V step needs approximately3.81 ms to settle to half a code in the
nominal passive model; first-frame and transition readings need explicit validity
handling. All sampled diagnostics can miss brief disturbances between samples.

## I2C design envelope

At400 kHz, the captured ADS1119 timing table permits a20–300 ns rise time.
With2.2 kohm pull-ups, an assumed1% initial plus100ppm/C across100 C gives a
maximum resistance2244 ohm. The first-order30%-to70% rise model
`tr = ln(7/3) * R * C` permits about158 pF at300 ns. Use150 pF total bus
capacitance as a provisional layout ceiling and measure both minimum and maximum
edge timing. This includes every ADC, MCU, trace and probe load; the sheet's
10 pF input capacitance is typical, not a maximum. Parallel/unintended pull-ups,
leakage and source/sink edge behavior must be included in the real calculation.

With main3.3 V assumed+3% and pull-up resistance-2%, sink current at VOL=0.4 V
is about1.391 mA. That is below the ADC's stated3 mA test load; it does not prove
the MCU's drive or complete bus timing. These rail/tolerance assumptions must be
checked against exact bindings. The ADCs and bus share main3.3 V, so an absent
main rail is not an operating diagnostic condition even if another rail exists.

The study's nine-conversion6.817 ms ideal schedule is conservative for this
8-channel intermediate circuit; do not poll U28 AIN2. Retain per-device
configuration read-back, signed decoding, timeouts, sample age and channel
association. Apply status bit7 as a mask, not a whole-byte equality check. An
ADC/bus failure invalidates its observations. Keep independent supervisor events
and sensor validity rules; polling is not continuous fault protection.

## Verification and release boundary

There are51 additions:3 ADCs,32 divider resistors,2 bus pull-ups,8 filters and6
bypass capacitors. New passives and ADCs have no assembly binding copied from
donor components. All prior circuit components and authored CAD are preserved.

`prepare.py` refuses an existing destination and parses the complete authored
symbol library. `verify.py` checks captured library/footprint syntax and hashes,
reproduces the full inputs and runs an independent allowed-delta graph checker.
None of those checks establishes native ERC, actual land dimensions, current
inventory, thermal/error qualification, bus timing or hardware fault survival.

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 prepare.py \
  --base ../wheel-input/inputs --out /absolute/fresh-inputs
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 verify.py
```

Next: implement the protected auxiliary supply and its ninth divider; resolve
exact passive/ADC bindings and qualification holds; reconcile JP1 assembly policy
and regenerate all input layers once the released AGENTEE-288 emitter repair is
available. Then check native graph/ERC/BOM and proceed to physical placement.
The wheel negative-transient hold and input-power qualification remain open.
