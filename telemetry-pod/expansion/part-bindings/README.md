# Expanded pod identity bindings

This packet adds identity metadata to 181 previously unbound components: the
40 selected divider resistors, 32 additional 10 kohm resistors, 28 other 0603 resistors, 55 capacitors and 26 already-selected active, crystal and
inductor instances. The manifest has 42 exact manufacturer/supplier identities,
component IDs, references, footprints, source URLs and SHA-256 pins. It does not
change circuit connectivity, values, footprints, or earlier bindings.

The prepared source now contains 307 bindings, with 14 component bindings still
missing, five copper jumpers awaiting fabrication policy and six power flags.
Presence of a binding is not electrical, thermal, parameter, assembly or release
qualification. The earlier 126 bindings are retained without requalification.
New bindings explicitly state that qualification is pending. Required normalized
rating parameters and complete pipeline part qualification remain outstanding.

Each selected catalog is replayed against its retained raw responses. All 42
selected identities have raw `assemblyComponentFlag=false`; this packet records
that observation without inventing an assembly exception or claiming the field
alone proves availability or ineligibility. Stock figures are capture-time data,
not current purchasing promises. The 40 resistor selections are now identity-bound
in this prepared source; the older part-selection inventory remains a historical
snapshot of its own pinned intent.

## Additional 10 kohm resistors

The 32 new positions use YAGEO RT0603BRD0710KL / C95204. This exact identity
already appears in the baseline, but the new positions have a fresh exact-ID
stock capture and an independently downloaded manufacturer specification sheet
in `resistor-stock/` and `resistor-sources/`. The manifest lists every position;
all use the existing 0603 footprint. The part provides 10 kohm, 0.1% tolerance,
25 ppm/°C and a −55 to 155 °C temperature range, covering the stated nominal,
tolerance and temperature-coefficient requirements, including R170–R173.

The sheet rates power at 0.1 W at 70 °C and lists a 75 V maximum continuous
voltage. Both limits apply: at 10 kohm, 0.1 W corresponds to about 31.62 V.
This selection does not establish safe operation at 75 V, the power available
at higher local temperatures, or transient performance. Existing thermistor
fault dissipation, local-temperature and derating holds remain open. No prior
binding is replaced by this newer document.

## Remaining 0603 resistor identities

A further 28 positions use 15 exact YAGEO RT0603BRD07 parts. Their fresh
exact-ID captures and manufacturer sheets are retained in
`remaining-resistor-stock/` and `remaining-resistor-sources/`. The manifest maps
all positions to the exact MPN and supplier identity. These sheets specify the
required nominal values, 0.1% tolerance, 25 ppm/°C, 0603, −55 to 155 °C,
and 0.1 W at 70 °C. Tighter tolerance and temperature coefficient satisfy the
positions stated as 1% and 100 ppm/°C; this does not qualify circuit operation.

The lower resistance values have much lower power-limited voltage ceilings:
120 ohm R70 reaches 0.1 W at about 3.46 V rms differential, and 100 ohm
R118/R127 reach it at about 3.16 V rms. Sustained dominant CAN operation,
fault voltage, pulse energy and local-temperature derating need separate
verification. The 75 V sheet ceiling does not override power dissipation.

R60 (31.3 kohm), the four 1.05 Mohm positions, and the 2512 power resistors
remain unbound. The search for `RT0603BRD0731K3L` was rewritten by the server
to `RT0603BRD0711K3L`; its empty response does not establish availability of
the requested part. The exact manufacturer URLs for the requested 31.3 kohm
and 1.05 Mohm MPNs returned 404. `unresolved-searches.json` retains these
limited observations. Neither result justifies rounding a circuit value.

## Capacitor identities

Six exact KEMET identities cover 45 positions. Manufacturer sheets and fresh
exact-ID supplier responses are retained in `capacitor-sources/` and
`capacitor-stock/`. All are commercial parts specified from −55 to 125 °C;
these documents do not establish automotive qualification.

| Part | Positions | Nominal, dielectric, voltage, tolerance | Package |
| --- | --- | --- | --- |
| C0603C104K5RACTU | 25 | 100 nF, X7R, 50 V, 10% | 0603 |
| C0805C105K5RACTU | 11 | 1 uF, X7R, 50 V, 10% | 0805 |
| C0603C180J5GACTU | C81, C82 | 18 pF, C0G, 50 V, 5% | 0603 |
| C0603C221J5GACTU | C95, C96 | 220 pF, C0G, 50 V, 5% | 0603 |
| C0603C223K5RACTU | C71, C73, C75, C77 | 22 nF, X7R, 50 V, 10% | 0603 |
| C1206C106K4RACTU | C128 | 10 uF, X7R, 16 V, 10% | 1206 |

These nominal matches do not close effective-capacitance, ESR, leakage, ripple,
transient or assembled-temperature requirements. The X7R sheets specify ±15%
temperature change and 3% loss per decade hour under their referee conditions;
DC bias, initial tolerance and aging must enter the relevant circuit budgets.
Their plotted simulations describe typical behavior, not guaranteed limits.

C128 remains subject to the TL431 stability and effective-capacitance check.
The four 22 nF supervisor capacitors require a release-delay tolerance budget.
C81/C82 provide nominal 9 pF in series before board and pin capacitance; this
does not establish the crystal's required load or oscillator startup margin.
The Hall input's selected C0G part does not resolve the existing negative-input
clamp problem. No source connectivity, value or footprint changes accompany
these identity bindings.

## Further capacitor identities

Three additional exact identities cover ten positions. Fresh exact-ID captures
and manufacturer documents are in `capacitor-stock-v2/` and
`capacitor-sources-v2/`:

| Part | Positions | Nominal, dielectric, voltage, tolerance | Package |
| --- | --- | --- | --- |
| KEMET C0603C105K4RACTU / C2167386 | C63, C80 | 1 uF, X7R, 16 V, 10% | 0603 |
| YAGEO CC1210KKX7R8BB226 / C5341638 | C68, C69, C70 | 22 uF, X7R, 25 V, 10% | 1210 |
| Murata GRM1885C1H103JA01D / C85973 | C47, C88, C91, C94, C126 | 10 nF, C0G, 50 V, 5% | 0603 |

All three captures show positive stock at capture time. This is not a reservation
or assembly approval. No existing bound TDK or other component is replaced.
The Murata reference sheet explicitly maps the D suffix to its paper reel
package and gives −55 to 125 °C operation. Its ±30 ppm/°C coefficient row
specifies 25 to 125 °C; that row alone does not establish the same linear bound
below 25 °C. The 5% initial tolerance meets the four positions specified as 10%.

The Yageo 22 uF body is 2.5 ±0.2 mm thick. Nominal package compatibility does
not establish enclosure clearance, land-pattern suitability or vibration life.
The 1 uF and 22 uF parts retain effective-capacitance, DC-bias, aging, ripple,
regulator-stability and hold-up checks. All three manufacturers' rating data
remain inputs to qualification, not completed vehicle qualification.

## Native generation blocker

Agent-ee e4cf3ab rejects the valid 278-character MCP2518FD `PARAM_Datasheet`
structured JSON through the emitter's generic 256-character display-field limit.
The existing `part_binding.parse_param_value` accepts this exact payload.
`emitter-blocker/valid-binding.json` and `receipt.json` retain the reproduction.
The full official URL and captured hash are preserved. No data was shortened or
removed to make emission succeed. A repair request was sent to the designated
agent-ee integrator; native generation and metadata round-trip remain unverified.
The last reviewed native schematic remains `../native-candidate/`.

Run the available source checks:

```sh
PYTHONPATH=/home/halbritt/git/agent-ee/src python3 telemetry-pod/expansion/part-bindings/verify.py --source-only
```

This command reports native verification **NOT_RUN**. Once the emitter repair
is released, run without `--source-only` to require generation, native ERC,
connectivity and metadata checks. Failure to generate is a failure of that run,
not an electrical result. `prepare.py --out NEW_DIRECTORY` preserves the full
inputs needed to reproduce the generation attempt; `--source-only` explicitly
limits it to preparation. No actual pod project has been replaced.

## Recovered eMMC provenance

U14 now has an identity binding. The four original raw stock responses were
recovered from retained local artifacts and restored to storage-candidate; each
matches the hash and byte count in the original committed catalog. The newer
exact-ID C3249972 capture remains under `emmc-stock/`.

The current supplier API's datasheet endpoint returned HTTP 403. A working
supplier-hosted manufacturer-document URL was found and downloaded independently
by both producer and reviewer. Both downloads are byte-identical to the reviewed
A-00093 revision 1.0 PDF already in storage-candidate. `emmc-source.json` records
the working URL, digest and recovery. This repairs provenance without changing
the document or component selection.

The primary MCP3208, three ADS1119 diagnostic converters and TL431 shunt also
receive exact identities from `adc-shunt-stock/`, using their existing reviewed
manufacturer documents. Exact MPN matching excludes similarly named ATL431,
other grades, packages and manufacturers. Accepted 85 °C exceptions and all
operating qualification holds remain unchanged.

Independent review is in `review/`. All earlier shared-SPI, Hall-input, rail,
thermistor, transient, thermal, mechanical, firmware and manufacturing holds
remain. This packet is a step toward complete part binding, not manufacturing
acceptance.
