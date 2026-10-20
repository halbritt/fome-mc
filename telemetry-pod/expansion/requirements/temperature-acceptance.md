# Per-part temperature acceptance

The owner correction relayed on 2026-10-20 in Cairn record
`9c82aea9-1345-46c0-9e85-aa44c5b47879` version 1 states:

> Obviously, that needs to be corrected. It should be tested against its actual limit.

The accepted 85 °C parts remain selected, with operating-temperature verification
required for each exact part. Acceptance of a lower component rating does not
waive the board's −20 to +85 °C ambient requirement or establish that the part
stays within its operating limit in the enclosure.

| Reference | Exact selected part | Accepted upper rating | Current qualification |
| --- | --- | --- | --- |
| U1 | ESP32-S3-WROOM-1-N8 | 85 °C | Unknown: part-bound assembly thermal evidence missing |
| U2 | LSM6DSO32TR | 85 °C | Unknown: part-bound assembly thermal evidence missing |
| U4 | MCP3208-BI/SL | 85 °C | Unknown: part-bound assembly thermal evidence missing |

For each reference, the executable acceptance input must retain the owner-cited
accepted range and the exact MPN, manufacturer and package binding. The captured
manufacturer rating must cover that range; failure is a defect. Expected operating
temperature must be within the actual rating using thermal evidence bound to that
part and the evaluated assembly. Missing thermal evidence is unknown, never pass.
Do not substitute enclosure ambient for the part's applicable temperature metric
without evidence that relates them.

AGENTEE-310 is released in agent-ee commit
`f507cf28e8c1874f219f98860df95d49488e2843`. The prepared replacement is
[temperature-acceptance-fragment.json](../temperature-acceptance-fragment.json),
with hash-pinned canonical declarations in
[operating-temperature-acceptances.txt](operating-temperature-acceptances.txt).
The declared -20 to 85 degC range preserves the existing lower requirement and
owner-accepted upper rating; it does not assert that -20 degC is the
manufacturer's lower rating. The board-wide part-selection criterion remains
-20 to 105 degC, while the board ambient requirement remains -20 to 85 degC.

Merge the fragment's `reduced_acceptance` into the regenerated scope's
`assembly_readiness.params.operating_temperature` and keep all three references
in the judged `parts` map with exact captured part bindings. No thermal evidence
is supplied: their thermal status must remain unknown. This preparation is not
an executed board-wide assembly predicate. The historical exemption fragment
and captures remain unchanged for provenance and must not be used in new scopes.

No enclosure thermal validation is supplied by this worksheet. Manufacturer
rating checks, assembled thermal qualification and overall design acceptance
remain separate obligations.
