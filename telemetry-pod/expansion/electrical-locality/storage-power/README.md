# Storage-regulator placement diagnostic

This retained candidate contains all 331 footprints and passes seven declared
origin-distance groups. It is not the adopted board, a routed design, or a
manufacturing release. The producer uses the frozen, unreleased AGENTEE-318
source snapshot identified by `producer-source-hashes.json`. Execution completed
in 855.843 seconds with board SHA256
`d5dc1cf1652d3f1af6c2bc7c1f356839b62f9c061b624f8781a9f76592efb8ef`.
The original 90 x 65 mm outline and clearances were retained.

Native DRC against the adopted schematic from `../../released-source-migration`
reports 137 findings: 44 drill, 20 clearance, 5 copper-edge and 68 silkscreen.
There are 499 unconnected items and zero schematic-parity findings. The 69
copper/drill/edge findings persist from the baseline. Neither a successful
placement nor parity closure discharges them.

The U15 input capacitor C70 VIN pad-center distance is 2.577 mm and its PGND
connection is 4.815 mm; the switch-to-L4 distance is 3.850 mm. The prior six-group
candidate had corresponding distances 50.804, 48.592 and 8.875 mm. These are
straight-line pad-center distances, not copper-edge routing-length bounds.

The improvement is not uniform: U26 C97/C98 supply distances improve to
2.510/1.963 mm while nearest ground distances regress to 8.276/8.578 mm
(previously 3.642/2.069 mm). Ten other assigned bypass components retain their
relative supply/ground geometry. Origin-distance acceptance therefore cannot
stand in for power-loop qualification. Independent review confirms preservation,
exact write scope, group grades and the measured tradeoff.

The reports retain diagnostic evidence; this directory is not a standalone
replay capture. DRC input hashes identify the original captured inputs, and the
producer manifest identifies an unreleased source snapshot rather than an
installed release. Full replay requires those exact captures. Source files and
DRC rules must not be changed to reproduce a passing result. The next main-buck
experiment and pad-level placement work remain separate from this candidate.
