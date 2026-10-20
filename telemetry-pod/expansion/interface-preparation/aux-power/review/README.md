# Independent auxiliary branch review

Disposition: defensible as a prepared circuit candidate with an unresolved precision-load requirement. No prepared wiring defect found. This does not qualify any positive external load for 5.00 V ±1%, fault survival, native KiCad ERC, assembly or fabrication. The source README accurately preserves these distinctions.

## Voltage and protection limits

The branch must draw from POD_5V_SENSOR to preserve the common supply/reference relationship. A series protection switch still causes a load-dependent ratiometric error because SENSOR_REF_2V5 senses the upstream rail. Branch monitoring does not cancel this error. Calibration is not evidence that the supply itself meets ±1%.

TPS2662 Rev F, electrical characteristics pp.6–7: thresholds and leakage were enumerated independently over every endpoint. With each resistor ±(0.1% + 25 ppm/K ×100 K) = ±0.35%, IUVLO and IOVP independently ±100 nA, and published threshold extremes:

| Input threshold | Minimum V | Maximum V |
|---|---:|---:|
| UV rising |4.215121|4.816437|
| UV falling |3.879657|4.458683|
| OV rising |5.637290|6.393207|
| OV falling/recovery |5.190642|5.916437|

Thus a valid 4.95–5.05 V input permits startup/recovery. These cutoffs do not keep the output within ±1%; undervoltage or overvoltage can invalidate sensors before protection operates. No aging or solder drift is included. Temperature allowance covers −40..125°C resistor temperature, referenced to 25°C; self-heating above that range requires recalculation.

For R1=a, R2=b, R3=c, positive leakage defined as current entering each device pin:

- At UV threshold t: Vin=t(1+a/(b+c))+Iuv·a+Iov·ac/(b+c).
- At OV threshold t: Vin=t(1+(a+b)/c)+Iov(a+b)+Iuv·a.

TPS2662 pp.4–5 and §9.3.1 p.16: R1 minimum is 1.046325 MΩ, exceeding the documented 1 MΩ current-limiting connection. At input +5.05 V and RTN −24 V, a conservative zero-pin-voltage current ceiling is 27.764 µA, below TI's described 60 µA connection condition. Conditional on UVLO staying at or below 5 V, the OVP tap remains below 3.767315 V including 100 nA outward OVP leakage. The datasheet's current-limited UVLO connection supports candidate preparation; it does not supply a separately guaranteed clamp-voltage-versus-current curve for this shared ladder. Exact reverse-fault waveforms, moving RTN, absolute limits and startup remain measurement/release holds. FLT and SHDN stay disconnected; EP and RTN share an isolated branch island, not GND.

## Usable precision load

REF50xx SBOS410O table4-2 p.3 and electrical table p.6 identify REF5050AIDR as standard grade: ±0.1% initial, 8 ppm/°C maximum full-range box drift. Full165°C span adds6.6 mV to5 mV initial error:11.6 mV screening allowance. Box method is described in §8.3 on p.24. TPS7B4253-Q1 electrical table p.5 contributes ±4 mV tracking under stated conditions including VADJ < VIN−1 V; line/load entries and all other operating conditions must be accounted for separately. The combined15.6 mV screening is not a complete source error bound.

The TPS26625 0.8 Ω full-temperature RON entry is specified with global24 V input, RILIM7.5 kΩ and load≥25 mA. It is not a guaranteed5 V,44.2 kΩ,arbitrary-low-load value. Its use below is conditional planning only:

| Load | Drop assuming0.8Ω | Remaining budget after15.6mV source screening |
|---|---:|---:|
|25mA|20mV|14.4mV|
|40mA|32mV|2.4mV|
|152mA|121.6mV|−87.2mV|

Required operating condition at the actual sensor is:

`I_total * R_switch_max + positive_lead_drop + return_lead_drop + other_branch_error <= qualified_V_sensor_min - 4.95 V`.

Also verify the5.05 V upper bound and transient behavior. Include monitor current (~3.3µA nominal), optional thermistor pullups, sensor loads, leakage and startup. With only the existing4.95 V minimum source promise, the right-hand side is zero: no positive series-drop budget is proven. The25 mA example is a useful characterization target, not a rated output. Tighter source and switch bounds are required, or redesign before declaring compliance. Shared U6 current/thermal limits and its interaction with a branch short remain unresolved;152 mA nominal protection is not independent fault containment or a precision load rating.

## Prepared source checks

`check_prepared_aux.py OLD_INPUTS NEW_INPUTS REPORT` requires agent_ee on PYTHONPATH. No producer helper is imported. It reconstructs the permitted delta independently and checks all old component records and graph terminals,13 exact new components, values and footprints, three consumed NC assignments, two new NC assignments, unchanged library manifests, complete authored-library parsing/hashes, preserved old CAD bytes, ADS1119 physical pin functions and TPS26625 physical pin functions. 1359 checks pass. Negative controls independently moving U30 IN to PRE_6V3, EP to GND and ninth ADC input to GND all fail exact graph membership.

J1 21/22 become protected auxiliary power/ground; U28 physical pin7 is the ninth monitor. No thermistor pullups are added. All prior ADC powered-off leakage, error, transient envelope, firmware schedule, Hall, CAN, storage, footprint and native acceptance holds remain. The ninth channel is connected in prepared source only.

Retained calculations are reproduced by `python3 calculate.py`; `prepared-report.json` pins input, checker, parser and authored CAD hashes. `negative-probes.json` records expected failures. `run_probes.py` uses the review worktree paths as an optional local reproduction helper; the checker itself is portable.
