# Agent notes for fome-mc

EDA tooling lives in `toolchain/` (see `toolchain/README.md`) and is driven through the
`Makefile`: `make doctor`, `make erc`, `make drc`, `make netlist`, `make export`,
`make analyze`, `make check`, `make renders`, `make verify-io`, `make fab-package`,
`make verify-fab-package`, `make simulate DECK=…`, `make smoke`, `make baseline`.
Load the `fome-eda-toolchain` skill for commands, paths and result semantics.
PCB routing uses the standalone kicad-route tool through `make route-doctor`,
`make route BACKEND=krt|freerouting`, `make route-validate`, `make route-compare`,
`make route-audit`, `make route-update`, `make route-smoke`; load the `kicad-route` and
`fome-pcb-routing` skills (details in `toolchain/ROUTING.md`).

- Native KiCad files are authoritative. Checks run on snapshots under `build/runs/`;
  never refill, upgrade or re-save the real design as a side effect of a check.
- KiCad's own ERC/DRC are the native checks; kicad-happy analysis supplements them.
- Routing attempts work on copies under `build/route/runs/`; a candidate is graded by
  KiCad against the input's unchanged rules. Never relax rules to make a route pass, and
  never relax them to make a board commit pass DRC (`make route-audit` reports it).
- **Owner sign-off means ask the owner.** If a check can only pass by changing a
  rule, exemption or constraint that this file reserves to the owner, put the
  question to the owner directly and immediately (the harness question tool, or a
  plain question in the reply): the exact values, the parts affected, the
  alternatives and a recommendation. Never record the work as "blocked, awaiting
  owner decision" without having asked, and never ask through a handoff note or
  a side channel the owner does not read.
- Check status (`PASS`/`FAIL`/`NOT_RUN`/`UNSUPPORTED`) describes the tool run; design
  violations are reported separately as findings.
