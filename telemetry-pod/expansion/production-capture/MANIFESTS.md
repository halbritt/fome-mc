# Checksum manifests in production-capture/ (AGENTEE-485 slice A, H6)

Agent-drafted (claude-opus-5-5 writer, AGENTEE-485 slice A). Not owner text.

| Manifest | Status | Applies to | Verifier |
|---|---|---|---|
| `SHA256SUMS` | **HISTORICAL**. Bytes and path are preserved (sha256 `f26e5c09a4441606d49bb1ad8b3ca2f3bea9e1bce93b4851617dd1975665e793`), because a sealed record cites the path (ERRATA-20261023.md, "Binding rule"). | fome-mc `769c6c660a6a0c1e1fd127088b74695b2d74de7e` (AGENTEE-207 pin-refresh) and no later revision. At later revisions its listed source files changed (21 mismatches at 22bb131), which is expected and not a defect of those revisions. | `git archive 769c6c66 telemetry-pod/expansion/production-capture \| tar -x -C DIR && cd DIR/telemetry-pod/expansion/production-capture && sha256sum -c SHA256SUMS` |
| `SHA256SUMS.ee485-slice-A` | **CURRENT** scoped manifest for the AGENTEE-485 slice A candidate | The commit that adds it, on branch wt/ee485-A. It is valid only while none of the listed files change. A later revision that changes a listed file adds its own scoped manifest and leaves this one as history. | From this directory: `sha256sum -c SHA256SUMS.ee485-slice-A` |
| `evidence/<retention>/SHA256SUMS` | Managed by `retain.py` (written by retain, checked by `retain.py --check`) | The retention it sits in. The active one is retain.py `DEST`. | `/usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py --check` (fome-mc root) |
| `sources/*/SHA256SUMS`, packet sums | Verbatim captures, hash-bound | Their own capture | `sha256sum -c` in the capture directory. Captured bytes are never normalised. |

The scoped manifest covers:

- every tracked file in this directory outside `evidence/` and `sources/`, except the two manifests themselves;
- the bound runtime manifest `runtime/agentee-485d.json`;
- the evidence this candidate binds: the delivered retention's `SHA256SUMS`, `MANIFEST.json` and `pipeline.json`; the
  receipt `production-runtime-485d/receipt.json`; and `repack-8ab3b0b9-485c/repack.json`.

It was generated with:

```sh
{ git ls-files . ':!evidence' ':!sources' ':!SHA256SUMS' ':!SHA256SUMS.ee485-slice-A';
  printf '%s\n' evidence/emission-8ab3b0b9-agentee485/SHA256SUMS evidence/emission-8ab3b0b9-agentee485/MANIFEST.json \
    evidence/emission-8ab3b0b9-agentee485/pipeline.json evidence/production-runtime-485d/receipt.json \
    evidence/repack-8ab3b0b9-485c/repack.json; } | LC_ALL=C sort -u | sed 's|^|./|' | xargs sha256sum > SHA256SUMS.ee485-slice-A
```
