# Captured third-party bytes: licence and redistribution note

This directory holds unmodified HTTP responses captured for AGENTEE-446 lane ee446g in the source-capture session.
The session was a coordinator decision (agent-521 c13da285, relayed by agent-449); it is not owner text. Every file
is listed in `sources.json` with its URL, retrieval time, HTTP status and sha256.

- `jlcpcb-pcb-capabilities-20261023T031800Z.html` is JLCPCB's public "PCB Manufacturing & Assembly Capabilities"
  page, copyright JLCPCB. No licence is granted to this repository. It is retained verbatim and unmodified, only as
  provenance for the numeric capability facts cited in `../addendum-c13da285.json`.
  - Do not republish or redistribute it.
  - If fome-mc is ever made public or shared outside the team, replace it with a hashed facts-only record. That is
    the earlier `production-capture/sources/fab-profile/sources/*.txt` convention ("numbers and names only").
- The page embeds JLCPCB's public analytics loader, including an mPulse `BOOMR_API_key`. That key is served to every
  visitor of the public page; it is not a credential of this project. It is left as captured, because editing the
  bytes would break custody.
- `te-108-1329-20261023T031801Z-http403.*` is TE Connectivity's CDN refusal (HTTP 403, AkamaiGHost "Access Denied")
  for product specification 108-1329. It is retained as evidence of the retrieval limit. No TE document was obtained.
- `*.headers` are the response headers exactly as curl wrote them.

These files are never edited. A newer capture goes in a new directory with its own manifest.
