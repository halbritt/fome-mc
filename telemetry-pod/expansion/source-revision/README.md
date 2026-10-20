# Reviewed dated-source revision

The fresh captures for C2167136 (C71/C73/C75/C77), C452747 (C95/C96) and C723532 (R131/R135/R139/R143/R147/R151/R155/R159/R169/R179) are approved as source revisions for the next native candidate. Their old captures remain retained.

All nine PDF pages have identical extracted text except the printed generation date, which changes from 10/19/2026 to 10/20/2026. At 144 dpi, every changed pixel falls within the exact date-text bounding region plus a one-point raster margin; every pixel outside is identical. `comparison.json` retains both document hashes, full-page render hashes, changed pixel counts and bounds. The six first-page footer crops were visually inspected and show those dates. This is bounded text/raster evidence, not binary PDF equivalence.

Three new canonical part records replay through released agent-ee `014c7c3e4079c35c52bc5a42007ed7ed612feb55`. `revision.json` pins dependencies, original intent and the exact old/new document hashes. `intent.json` changes only `PARAM_Datasheet.sha256` for the 16 instances. Part numbers, suppliers, values, footprints, pins, nets and all other source data are unchanged. Captured supplier stock remains historical.

This intent is an explicit revision overlay for the reconstructed series-divider input root; its relative library paths still refer to that root. It is not a standalone capture directory. Reconstruct inputs, replace their intent with this reviewed intent, preserve the later presentation-heading changes, then regenerate and verify native bindings. No existing schematic or native receipt was modified. The prior 82-record/299-instance packet remains historically correct; these three records cover 16 more instances for the revised candidate. J1 remains without a canonical historical import, pending AGENTEE-306. Copper-feature parts membership remains pending AGENTEE-305.

Replay from repository root:

```sh
python3 telemetry-pod/expansion/source-revision/compare.py --verify
PYTHONPATH=/path/to/agent-ee-014c7c3/src python3 telemetry-pod/expansion/source-revision/build.py --verify
```

PyMuPDF 1.23.7 and NumPy were used for raster comparison. Both commands were independently replayed by `/root/expanded_pod_review`; independent intent comparison confirms only the 16 declared hashes change. This supports the source revision, not native adoption, electrical qualification or manufacturing release.
