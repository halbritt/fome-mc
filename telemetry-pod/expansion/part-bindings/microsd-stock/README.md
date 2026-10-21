# JLCPCB assembly stock, microSD source inventory (captured 2026-10-21)

`catalog.json` (`agent-ee.jlc-catalog/1`, owner-run `agent_ee.jlc_stock_capture --netlist
../../storage-microsd/native.xml`, one public search per LCSC id, 2 s apart) covers every
populated LCSC id of the current schematic: 81 ids, 81 found, raw responses under
`responses/`. It replaces the eMMC-era captures (`../emmc-stock/`, `../*-stock*/`) as the
assembly-readiness evidence for the next fab package.

**Finding:** `C596198`, TE AMPSEAL 1-776163-1 (J1, the owner-fixed 35-position right-angle
harness header) shows **0** JLCPCB assembly stock at capture time. Everything else is in stock
(see `catalog.json` for counts). Consequence for the fab package: J1 is a through-hole header
that JLCPCB cannot place from stock; either order it separately (TE/Digi-Key/Mouser) and
solder it by hand, use JLCPCB's pre-order/consign option, or wait for restock. This does not
change the design; it is an ordering decision for the owner at fab time.
