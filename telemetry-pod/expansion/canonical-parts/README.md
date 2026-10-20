# Canonical records for expanded purchased parts

The existing `part_record.prepare_record` and `qualify_record` APIs at agent-ee
`014c7c3e4079c35c52bc5a42007ed7ed612feb55` now produce and replay **82 records
covering 299 purchased instances**. Four explicit gaps cover the remaining
17 instances. The source intent, native schematic and every existing binding
remain unchanged. A canonical record establishes captured exact identity;
it does not establish component suitability, assembly readiness or approval.

The preceding source-closure packet retained all exact PDF bytes, but 49
identity/document combinations lacked the canonical acquisition records required
by the producer. `targets.json` lists those combinations and their old hashes.
The existing network acquisition producer fetched all 49 URLs into a fresh
`acquisition/` directory: 47 succeeded, 44 matched the bound PDF bytes, three
changed bytes and two returned HTTP failures. These are actual capture results;
no final URL, time or acquisition outcome was fabricated from the older notes.
`capture-comparison.json` retains each outcome.

The builder searches tracked canonical acquisition manifests, including the
recovered historical pilot, for an exact PDF-hash and original-URL match. This
recovers the existing TJA1051 acquisition despite its fresh URL returning 404.
It selects the most recent retained exact-identity supplier catalog, with path
as a deterministic tie-break, and records every dependency. This is a historical
catalog choice, not a fresh supplier availability claim.

## Remaining exact-source gaps

| Identity | Positions | Observed result |
| --- | --- | --- |
| C596198 / 1-776163-1 | J1 | TE URL returned HTTP 403; the retained K1 PDF has no matching canonical acquisition manifest. |
| C2167136 / C0603C223K5RACTU | C71, C73, C75, C77 | New PDF bytes; extracted text differs in generated-date footer. |
| C452747 / C0603C221J5GACTU | C95, C96 | New PDF bytes; extracted text differs in generated-date footer. |
| C723532 / RT0603BRD074K99L | R131, R135, R139, R143, R147, R151, R155, R159, R169, R179 | New PDF bytes; extracted text differs in generated-date footer. |

Text diffs and extraction hashes are retained. Text-only comparison does not
prove visual/PDF equivalence and does not authorize silently replacing the bound
source. These three fresh documents are not adopted by the records or source
bindings. J1's existing bytes and source note remain retained; a blocked fetch
is not evidence that the part or drawing is unavailable.

The complete expanded `parts/1` manifest and CAD assignment qualification remain
open. There is also an apparent declaration gap for JP1–JP5: released
`parts_manifest.validate_manifest` admits ordinary purchased entries or the
one-pad `bare_copper_probe` union. `parts_subset.compare_inventory` treats an
undeclared populated item as unexpected even when `in_bom` is false. The five
two-pad solder jumpers have neither supplier identities nor one-pad probe
semantics. Fabrication copper-feature admission does not itself establish a
parts-manifest membership route. This is source inspection, not a completed
`parts_subset` execution; the integrator must reconcile the supported contract.

## Offline replay

From the repository root with the exact software's `src` on `PYTHONPATH`:

```sh
python3 telemetry-pod/expansion/canonical-parts/verify.py
python3 telemetry-pod/expansion/canonical-parts/build_records.py --out /path/to/fresh-records
```

The second command must reproduce every record and index byte. The builder
searches tracked telemetry-pod acquisition manifests; stage new captures before
running it. Retained record paths are relative to the repository root, so the
original temporary workspace is not required. Checks replay raw catalogs,
complete acquisition manifests and PDF envelopes/hashes offline. They do not
run native CAD, ERC/DRC, `parts_subset`, assembly or manufacturing acceptance.
