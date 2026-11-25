# Manufacturing the main FOME-MC ECU

## Assembly sourcing

Use the main-board files in [export/](../export/). The 25 November 2026 JLCPCB catalog lookup returned these manufacturer parts for the corrected supplier codes. Recheck available quantities when quoting the build.

| References | Manufacturer part | LCSC |
|---|---|---|
| J1, J2 | TE 776163-1 and 776163-2, 35-position right-angle through-hole AMPSEAL | C412117, C5172878 |
| L1 | Murata LQH32PH2R2NNCL, 2.2 µH power inductor, 1210 | C2043220 |
| U202 | Texas Instruments DRV8825PWPR, HTSSOP-28 with exposed pad | C81582 |
| U1003, U1103, U1203 | Nexperia 74HCT125D,653, SO-14 | C5962 |
| U27 | ST USBLC6-2SC6, two-line USB protection | C7519 |
| U29 | Microchip ATWINC1500-MR210UB1961, external U.FL, firmware suffix 1961 | C1558698 |
| U41 | Microchip MIC5205-3.3YM5-TR, SOT-23-5 | C37970 |
| U42–U45 | Microchip MIC4427YM-TR, SOIC-8 | C461590 |
| U201, U203 | Infineon TLE9201SG, PG-DSO-12 | C2653438 |
| C303, C403 | Murata GRM155R71H333KE14D, 33 nF, 50 V, X7R, 0402 | C415530 |
| R23–R34, R39–R42 | Yageo RT0603BRD072K7L, 2.7 kΩ, 0.1%, 0603 | C705760 |
| R201–R204 | UNI-ROYAL 0603WAF150JT5E, 15 Ω ignition gate resistors | C22810 |
| R212 | UNI-ROYAL 0603WAF2201T5E, 2.2 kΩ tach pull-up | C4190 |
| D20, D21, D205–D209 | Diodes Incorporated B340A-13-F, 3 A SMA | C85098 |
| R310, R410 | Panasonic ERA-3AEB61R9V, 61.9 Ω, 0.1%, 0603 | C2087389 |

The 12 V input filter previously called out a Bourns power inductor by name but ordered a 450 mA RF inductor. The selected Murata fits the existing 1210 pads and has 64 mΩ nominal DC resistance, a 2.0 A inductance-change rating and a 1.85 A thermal rating at 85 °C ambient. Check the filtered input during crank and load steps as the lower resistance changes filter damping. [Murata specification](https://www.ic-components.se/files/57/LQH32PH100MNCL.pdf)

The harness mates are the black A-key 776164-1 for J1 and the natural B-key 776164-2 for J2. Specify both headers in the through-hole assembly step and verify the keyed faces against the enclosure. [TE AMPSEAL connector selector](https://www.te.com/content/dam/te-com/custom/media/connector-selector/docs/ict-connector-selector-en.pdf)

Three BOM lines had zero JLCPCB assembly stock. Arrange exact-part sourcing or consignment before releasing a fully assembled order.

| References | Required part | Sourcing route |
|---|---|---|
| U25 | CS Semiconductor CSNP32GCR01-AOW, C2841139 | Request the AOW grade through the [manufacturer](https://www.cs-semi.com/product/36-en.html) or [LCSC](https://www.lcsc.com/product-detail/C2841139.html). The cataloged BOW alternative is rated 0–70 °C and reduces the ECU's operating range. |
| U29 | Microchip ATWINC1500-MR210UB1961 | [DigiKey exact MPN](https://www.digikey.com/en/products/detail/microchip-technology/ATWINC1500-MR210UB1961/9657713). Check firmware compatibility with the ECU host driver at bring-up. The PB variant's PCB antenna cannot serve the enclosure bulkhead pigtail. |
| U1001, U1002, U1101, U1102, U1201, U1202 | ST VNLD5090TR-E, C222209 | [DigiKey exact MPN](https://www.digikey.com/en/products/detail/stmicroelectronics/VNLD5090TR-E/4552573). Allow six per board plus the assembler's attrition allowance. |

## Copper and assembly process

U29 moved 0.15 mm toward the board interior while retaining the module orientation and external antenna connection. Pads 10–19 now have 0.335 mm from copper to the routed outline. The board rule enforces the manufacturer's 0.20 mm minimum. The module uses the UB land pattern and center ground paddle. [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) · [Microchip footprint drawing](https://onlinedocs.microchip.com/oxy/GUID-84670AC3-A299-4E2D-858F-83426F5FC5E9-en-US-6/GUID-B3708120-24DB-4C5F-AF72-4EAFF71F5856.html)

The Gerber job uses the specified four-layer JLC04161H-7628 construction, with 35 µm outer copper, 15.2 µm inner copper, two 0.2104 mm prepregs and a 1.065 mm core. [JLCPCB stackup](https://jlcpcb.com/impedance)

The four ignition collector nets use 1.20–1.50 mm tracks and 28 through vias with 0.80 mm lands and 0.40 mm drills. Two gate traces moved locally to retain the collector class's 0.50 mm clearance. The board marks 159 vias whose drills intersect exposed SMD lands for epoxy fill and copper capping. The [via-in-pad coordinates](../export/via-in-pad.csv) use the KiCad origin, X right and Y down. Keep the connector and mounting holes open. Confirm the via treatment and the through-hole assembly step in the supplier preview. [JLCPCB via covering](https://jlcpcb.com/help/article/pcb-via-covering)

For IGN3's 19.8 mm inner-layer segment, 1.20 mm width and nominal 15.2 µm copper give about 19 mΩ at 20 °C, half the previous segment resistance. At the design point of 6.5 A peak, 3.2 ms dwell and 10,500 rpm, a conservative rectangular current pulse once per revolution gives 56% duty and about 0.44 W in that segment. Actual coil current ramps, copper resistance rises with temperature and the board spreads heat. This estimate covers that segment only. Measure coil current and ignition-path temperatures at the intended duty and ambient before approving a potted unit. [ECU operating assumptions](DESIGN.md)

The earlier design and harness assignments remain available in Git. To change part selection or geometry, edit the schematic and board together and regenerate all manufacturing files from that revision.
