# Complete physical-part declaration

This packet adds J1 to the prior 326-reference declaration. It contains all
327 native physical references: 316 purchased instances, six bare copper probes
and five solder-jumper copper features. Every prior part and assignment is
unchanged; J1 uses the existing through-hole CAD assignment and the historical
source record in `j1-historical-source`.

J1's historical stock is zero. Its acquisition retains unknown redirect history
and fetch time. These records describe exact captured identity and source bytes;
they confer no approval, suitability or availability.

`reconstruction.json` pins 406 repository source files used to reconstruct the
capture. `parts.json` and `assignments.json` supply the two generated declarations.
`build.py` reuses the historical partial-manifest producer and appends only J1.
The prior packet is preserved.

Software is an isolated diagnostic combination of AGENTEE-305 commit
49587ed7824e6b3d3bbbf0cc03d974bdbd69a90a and the two historical-import source
changes from AGENTEE-306 commit 5140939bf0d2b7a323cc30f7e3876b9032d991db.
`software.json` and `software-overlay.patch` pin that combination. It is not
a claim that either candidate has been integrated or released.

The full native comparison is retained in `report.json`. The legacy probe
marker in the source schematic still requires the supported producer migration;
complete reference coverage alone cannot bypass that check. The manifest does
not establish placement, routing, manufacturing or hardware qualification.

Reconstruct and replay with the exact software composition and a fresh output:

```sh
PYTHONPATH=/path/to/combined-archive/src \
  python3 telemetry-pod/expansion/complete-parts-manifest/verify.py --out /fresh/capture
```
