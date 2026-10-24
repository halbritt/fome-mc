# J2 identity bound to the composed F8 source

The historical J2 import pins the pre-F8 `agentee-494-j2/source-manifest.json`.
F8 archived the superseded enlarged-hole footprint and updated that manifest.
The manufacturer footprint, Amphenol 132134 Rev C drawing, MPN and published hole
pattern are unchanged. The historical identity and record remain untouched.

This separate identity pins the current F8 manifest. Its external part record
uses the existing historical acquisition manifest and the existing hand-fit
deviation. It makes no new capture-time, HTTP, stock or owner-text claim.
`agent_ee.part_record.prepare_external_record` and `qualify_external_record` from
agent-ee 00d3243a generated and checked the record locally. `build.py` consumes
this record and pins the complete merged deviations document in the emitted
capture, as before.

Reversal: restore `build.py`'s prior record input and remove this separate source
with the corresponding generated composition. Do not change the F8 library or
rewrite historical source records to make an old digest match new bytes.
