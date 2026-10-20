# Expanded source integration

This stage combines the prepared electrical circuits with the reviewed AMPSEAL
footprint and exact-part STEP. It is the input preparation for fresh native
schematic generation; it does not replace the current native pod project.

J1 is explicitly selected as TE **1-776163-1**, the black, gold-contact header in
776163 K1 sheet 1. The earlier generic intent named the tin-contact **776163-1**.
Both use the reviewed 35-position layout, but their part numbers and contact
finish are not interchangeable BOM identities. This selection aligns the exact
header with the captured model and supports a matching gold-contact harness.
The mating plug housing, exact gold-plated terminals, wire gauges, current
ratings and assembly sourcing remain to be bound and verified; no procurement
or universal harness compatibility is implied.

The generator copies the frozen auxiliary-power input snapshot and changes only
J1's value and footprint identifier. It adds the reviewed footprint and raw TE
STEP under project-local capture paths. All electrical components, pin numbers,
nets, no-connects, layout and previous captured files remain identical. No
component binding is invented from a CAD model or copied from a donor.

Run `python3 prepare.py --out /absolute/fresh-inputs` before native emission.
Use the resulting intent/layout/captures with the released emitter, then create
project-local library tables and verify native connectivity, ERC, assembly
policies and the connector's actual placed geometry. The current private-property
and copper-jumper release gates remain in force; source preparation is not an
emitter workaround. Optional thermistor configuration, Hall transient protection,
power qualification, remaining part bindings and physical layout are unfinished.
