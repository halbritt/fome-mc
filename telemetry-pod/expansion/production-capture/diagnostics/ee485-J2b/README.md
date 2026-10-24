# AGENTEE-485 J2b diagnostic evidence

**Partial delivery. 18 required stages accepted; C1 NOT_RUN; pipeline exit 3.**
Ten additional preparation stages refused. The run did not produce a native
schematic or a complete production candidate. The corrected pipeline was not
rerun: the dispatch permits one diagnostic run.

The saved `scaffold/` contains nine fixed native footprints. Its J2 has the
Amphenol 132134 footprint, UUID 18c6ebf4-5f6a-5227-b278-be0fa33a91c9, front-side
pose (80,28) mm, zero rotation, and the published centre 1.5 mm / four 1.7 mm
holes on a 5.08 mm square. The native pad/layer pattern matches the stock
132134 footprint. The rightmost native bound is 84.195 mm on the 90 mm board.
The recorded RF areas have their expected polygons and original prohibitions.
`native-scaffold-witness.json` identifies these exact board bytes. This is a
geometry witness, not an annotated schematic, full placement, routing, assembly,
mechanical-access or manufacturing acceptance. The scaffold schematic placeholder
is intentionally omitted.

`pipeline.json` and `diagnostic-run.log` preserve the failed run unchanged. The
primary new failures were the native identity guard comparing a KiCad UTF8 proxy
with a Python string, and the external record depending on writer-mutable
composition/deviations.json. The delivered corrections use the Unicode identity
API and an immutable copy of the complete merged deviation document. The actual
parts capability still refuses the old capture and accepts the corrected one
with 412 immutable inputs (`parts-boundary.log`). The corrected producer passes
its byte-for-byte check (`corrected-reproduce.log`).

Complete access declarations belong after forward annotation because the scaffold
omits non-fixed owners such as TP1. A separate full-source control generates
44 rows with zero unmaterialized rows; missing or ambiguous native owners/pads
refuse (`owner-binding-controls.log`). Those controls do not qualify access on a
new production candidate. Candidate access and native BOM/CPL/ ERC/DRC remain
unverified because no new annotated candidate exists.

The source area identities 460352a8 and 93d1ddf1 map to new native UUIDs when the
changed envelope hash enters the existing scaffold generator. The whole-board
In1 no-tracks geometry remains unchanged; the RF corridor follows the chosen J2
pose. The source-to-native mapping is in composition/j2-rf-binding.json. The mapping records the generated identities for the new envelope bytes.

The ECU's five make-check steps pass with zero ERC/DRC violations. Its native
inputs, the pilot design and the 201/261/214 block inputs and eleven pending
routing clauses remain unchanged. Existing retained-delivery integrity also
passes; the new diagnostic has no receipt or retention acceptance.

Run identities and limitations are in `source.json`. The worker result records
commands, final branch heads, remote confirmation and all unmet criteria.
