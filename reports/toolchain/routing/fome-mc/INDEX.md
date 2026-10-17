# FOME-MC routing trials

Bounded, read-only trials on isolated copies of the committed board. Each directory
holds the attempt's `result.json`, `RESULT.md`, `attempt.json` (input identity, scope,
settings), `preservation.json`, `new-findings.json` and `candidate-drc.json`; the
candidate boards themselves stay under `build/runs/route/fome-mc/`. Summary and next
actions: `toolchain/ROUTING.md`, section "FOME-MC real-board trials".

| Label | Backend | Process | Routing (unconnected, input 235) | Validation |
|---|---|---|---|---|
| trial-krt-initial | KRT 0.23.1 | FAIL (budget) | NOT_RUN | NOT_RUN |
| trial-freerouting-initial | Freerouting v2.5.0 | PASS | INCOMPLETE (199) | FAIL (adapter defects since fixed) |
| trial-krt-nofinalize-before-locking | KRT 0.23.1 | PASS | INCOMPLETE (14) | FAIL (existing copper reworked; since fixed) |
| trial-freerouting | Freerouting v2.5.0 | PASS | INCOMPLETE (188) | FAIL (1 short, 2 clearance) |
| trial-krt-nofinalize | KRT 0.23.1 | PASS | INCOMPLETE (26) | FAIL (18 new warnings) |
