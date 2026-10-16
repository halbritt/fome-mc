# Agent notes for fome-mc

EDA tooling lives in `toolchain/` (see `toolchain/README.md`) and is driven through the
`Makefile`: `make doctor`, `make erc`, `make drc`, `make netlist`, `make export`,
`make analyze`, `make check`, `make simulate DECK=…`, `make smoke`, `make baseline`.
Load the `fome-eda-toolchain` skill for commands, paths and result semantics.

- Native KiCad files are authoritative. Checks run on snapshots under `build/runs/`;
  never refill, upgrade or re-save the real design as a side effect of a check.
- KiCad's own ERC/DRC are the native checks; kicad-happy analysis supplements them.
- Check status (`PASS`/`FAIL`/`NOT_RUN`/`UNSUPPORTED`) describes the tool run; design
  violations are reported separately as findings.
