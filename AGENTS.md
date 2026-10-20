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
- **Owner-reserved decisions are made autonomously, not parked.** When a check
  can only pass by changing a rule, exemption, footprint or constraint, the agent
  decides: pick the engineering answer, record it as a short decision note (what,
  why, alternatives, how to reverse) next to the affected design, implement it,
  and tell the owner in the reply. Never record work as "blocked, awaiting owner
  decision"; the owner reviews decisions after the fact and reverses the ones
  they disagree with. Relaxing a rule purely so a commit passes DRC is still
  forbidden; a documented engineering decision that changes a rule is not.
- **Every gating constraint needs a cited provenance class.** A design rule,
  envelope dimension, clearance, hole size or limit may gate work only when it is
  owner-stated, a manufacturer's published capability, or a datasheet/standard value,
  each with a citation next to the number. A value an agent or a tool chose as a
  default or a placeholder is advisory: record it as `class: default`, never let it
  block, and replace it with a sourced value at the first opportunity. When a check
  fails against a limit, first ask where the limit came from; an unsourced limit is a
  defect in the limit, not in the design.
- Check status (`PASS`/`FAIL`/`NOT_RUN`/`UNSUPPORTED`) describes the tool run; design
  violations are reported separately as findings.
