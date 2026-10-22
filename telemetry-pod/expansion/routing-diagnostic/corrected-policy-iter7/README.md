# Corrected-policy diagnostic input, not a production placement

The iteration-7 microSD routing input with the current layer policy added as native KiCad rule
areas. It is a native corrected-policy **diagnostic input only**, a slice of KICADROUTE-91 (M1b),
built under the coordinator ruling of 2026-10-21 (agent-509; plan M1). It is not an adopted or
production placement. No routing has been run on it, and it supports no routability comparison
and no routed-success claim. The historical evidence in `../iteration-7/` is unchanged; this is
a separate copy.

Open (not done here): the remaining M1b work (effective-configuration binding, sidecar
versioning, comparison refusal, agent-ee boundary integration) and the single corrected-policy
route. The historical 55/32 and 51/30 counts, the ten lost nets and the 203/235 campaign result
are unresolved and ineligible for promotion. See "Open items" and "Known limits" below.

## Source identity (agent-507 owns baseline identity)

`source/ca2.kicad_pcb.gz` is the board that `kicad-route campaign iter8d-campaign` round 0
routed (the historical 203-of-235 count, `../iteration-7/`; unresolved, not a result of this
fixture). Its hashes are:

| File | SHA-256 |
| --- | --- |
| `ca2.kicad_pcb` (archived input) | `67782a5d8ff7ce3c21dbe90b6f50c2735e4827231f3f474c9db4522de43ca73f` |
| `ca2.kicad_pro` | `7c7933bf09fad1617887d95dce24ae2b994737bf4cc46c20662e447561515b74` |
| `ca2.kicad_dru` | `ff62208301c38bca2c963a0682e0a2ee843d8a546bace3719340cfcca1b08d0d` |

The board was taken from `/home/halbritt/.cache/agent499-microsd/iter8d/route/planes-1/candidate/`.
`../iteration-7/` has no README or SHA256SUMS of its own, and it does not hold the board.
The identity is bound through committed receipts instead:

1. `../SHA256SUMS` verifies all 30 `./iteration-7/` files (`sha256sum -c`: OK).
2. `../iteration-7/candidate/iter8d-campaign-r0/snapshot.json` and `campaign.json` name that directory and the three hashes above.
3. `../iteration-7/planes/result.json` records `kicad-route planes` turning `2c1ac944…` into `67782a5d…`.

Each input to that planes run is also in the repository:

- `2c1ac944…` is `../../placement-candidate/iteration-7/candidate-silk-policy.kicad_pcb.gz`, decompressed.
- The project and rules are `../../design-rules/board-setup.kicad_pro` and `telemetry-pod.kicad_dru`.
- The plane plan is `../../design-rules/planes.json`.

`policy-receipt.json` recomputes every one of these hashes.

## Corrections (native rule areas, nothing else)

The decisions come from `../../design-rules/constraints.json`, `decisions_pending_next_seed`.

| Rule area | Layers | Forbids | Polygon (mm) |
| --- | --- | --- | --- |
| `D-PCB-7v2 In1.Cu no tracks (board outline)` | In1.Cu | tracks (vias, pads, pour, footprints allowed) | the Edge.Cuts outline, (0,0)–(90,65) |
| `D-PCB-6 RF reference keep-out` | In1.Cu, In2.Cu | tracks and vias (pads, pour, footprints allowed) | x 76..88, y 26.5..30.6 |

D-PCB-6's coordinates were captured for the GNSS line from the U3 RF pad at (77.5, 29.1) to the
J2 pin at (86.96, 28.0). This board matches that geometry exactly: U3 pad 11 and J2 pad 1 are
both `/POD_GNSS_RF`, and both footprints are locked. The corridor is therefore used unchanged.

In2.Cu stays open to signals, with its +3V3 pour. Nothing else changed: the `.kicad_pro` and
`.kicad_dru` are byte-identical to the source. `evidence/source-to-corrected.diff` is a single
insertion of the two `(zone …)` blocks, 62 lines added and none removed.

## Proof

- **Reload inspection.** `evidence/rule-area-inspection.json` comes from a pcbnew reload of a
  copy. It shows both rule areas with the layers, flags and polygons above. Re-saving the
  reloaded board reproduces `ca2.kicad_pcb` byte for byte.
- **Native DRC fixtures.** `evidence/fixtures.json` runs `kicad-cli pcb drc --refill-zones`
  in memory, on copies:
  - The source and corrected boards give identical DRC.
  - Each of these is flagged `items_not_allowed`:
    - an In1 track outside the corridor (1);
    - an In1 track inside it (2, one per area; with either area removed, 1);
    - an In2 track inside it (1);
    - a through via inside it (1, "keepout area 'D-PCB-6 RF reference keep-out'").
  - Nothing is flagged for:
    - a through via outside the corridor;
    - an In2 track outside it;
    - the same items on the uncorrected source.
- **Policy receipt.** `policy-receipt.json` binds the source, origin and output hashes, the
  rule-area geometry, the KiCad 10.0.7 version and the `routability-policy/1` fields. The fields
  are `experiment_class: current-policy`, `allowed_trace_layers: F.Cu, In2.Cu, B.Cu` and
  `allowed_via_spans: [F.Cu, B.Cu]`. The spatial RF exclusion is enforced by the native rule
  area, not by `allowed_via_spans`. That field is only a summary of layer pairs, and
  `allowed_trace_layers` likewise summarises the native D-PCB-7v2 rule area.

## Reproduce

```sh
tools/prove.sh /tmp/some-empty-dir        # rebuild + inspection + 13 native DRC runs; prints "prove: PASS"
# then, to refresh the evidence and receipt from that run:
cp /tmp/some-empty-dir/{rule-area-inspection.json,fixtures.json} evidence/
cp /tmp/some-empty-dir/out/source-to-corrected.diff evidence/
/usr/bin/python3 tools/make_receipt.py
```

The tools only open copies under the scratch directory and never write here.
`make_receipt.py` writes only `policy-receipt.json`.

## Open items

- **G1.** The remaining M1b work: effective-configuration/build/budget identity binding, sidecar
  versioning, refusing mismatched comparisons, exposing argument differences, and the agent-ee
  boundary integration. None of it is in this directory.
- **G2.** The historical 55/32 and 51/30 counts and the ten lost nets are unreconciled. They need
  complete native terminal/pad UUID evidence (KICADROUTE-98) or stay ineligible for promotion.
- **G3.** The single corrected-policy route (900-second backend ceiling plus measured
  grade/grace) has not been run.

## Known limits

- The `.kicad_dru` rule `agent_ee_netclass_RF_50` is preserved as found. This input's project
  defines only the Default class, so it matches no net. Changing net classes or widths is out
  of scope.
- Native DRC grades these rule areas. The kicad-route builtin engine was reported not to
  honour inner-layer rule areas (see `../README.md`). Any route on this input must be graded
  by native DRC against it, unchanged.
- The historical results are unresolved and ineligible for promotion: iteration 7's
  `net_completion` list (10 nets), the 203/235 campaign count, and the ticket's 55/32 and 51/30
  counts and ten lost nets. Nothing here reconciles them.
- The `RF_50` rule above is inactive, so no width rule applies to `/POD_GNSS_RF`.
- Fixture DRC runs with an empty `KICAD_CONFIG_HOME`. Both bases show 199 `lib_footprint_issues`,
  13 isolated-copper findings and 499 unconnected items; the verdicts are deltas against each
  fixture's own base, not a clean or connected design result.

## History

`policy-receipt.json` → `receipt_history` records the wording correction after commit 7e6fb02,
including the hashes of the README, receipt, `make_receipt.py` and `SHA256SUMS` at that commit.
Native inputs and evidence did not change.
