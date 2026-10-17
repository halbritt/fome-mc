# Agent notes for fome-mc

EDA tooling lives in `toolchain/` (see `toolchain/README.md`) and is driven through the
`Makefile`: `make doctor`, `make erc`, `make drc`, `make netlist`, `make export`,
`make analyze`, `make check`, `make simulate DECK=…`, `make smoke`, `make baseline`.
Load the `fome-eda-toolchain` skill for commands, paths and result semantics.
PCB routing runs through `make route-doctor`, `make route BACKEND=krt|freerouting`,
`make route-validate`, `make route-compare`, `make route-update`, `make route-smoke`;
load the `fome-pcb-routing` skill (details in `toolchain/ROUTING.md`).

- Native KiCad files are authoritative. Checks run on snapshots under `build/runs/`;
  never refill, upgrade or re-save the real design as a side effect of a check.
- KiCad's own ERC/DRC are the native checks; kicad-happy analysis supplements them.
- Routing attempts work on copies under `build/runs/route/`; a candidate is graded by
  KiCad against the input's unchanged rules. Never relax rules to make a route pass.
- Check status (`PASS`/`FAIL`/`NOT_RUN`/`UNSUPPORTED`) describes the tool run; design
  violations are reported separately as findings.
