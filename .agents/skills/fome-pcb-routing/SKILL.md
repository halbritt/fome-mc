---
name: fome-pcb-routing
description: "Use for any fome-mc PCB trace-routing or board-change audit task: the project's make targets around kicad-route, where fome-mc runs and evidence go, and what earlier real-board trials established. Load the global kicad-route skill for result fields and the retry playbook."
---

# fome-mc PCB routing

Routing in this repo (`~/git/fome-mc`) uses **kicad-route**, a standalone tool. Load the
global `kicad-route` skill for the result fields, exit codes and the retry playbook. The
`krt-*` skills cover deeper diagnosis. This skill adds only what is specific to fome-mc.
Project page: `toolchain/ROUTING.md`.

If `make route-doctor` reports that kicad-route is missing:
`git clone https://github.com/halbritt/kicad-route ~/git/kicad-route && ~/git/kicad-route/scripts/install.sh`.

## Commands (repo root)

| Command | What it does |
|---|---|
| `make route-doctor` | Readiness and versions of both backends |
| `make route BACKEND=krt\|freerouting [BUDGET=300] [REV=HEAD] [ARGS='…']` | One attempt on a copy of `fome-mc.kicad_pcb`; prints the run directory |
| `make route-validate RUN=<run> [AGAINST=<first run>]` | Re-grade a candidate, or the end of a `--dir` chain against its first input |
| `make route-compare RUNS='<run> <run> …'` | Compare attempts from the same input |
| `make route-publish RUN=<run>` | Evidence (not the board) to `reports/toolchain/routing/fome-mc/<label>/` for committing |
| `make route-audit OLD=<rev> [NEW=HEAD]` | Grade a committed board change, made by hand or by another agent, against its parent |
| `make route-update` / `make route-smoke` | Update the backends / run kicad-route's integration tests |

`ARGS` are `kicad-route run` options: `--nets`, `--netclass`, `--protect`,
`--default-clearance`, `--clearance-margin`, `--passes`, `--max-iterations`,
`--backend-arg`, `--backend-env`, `--label`.

- **`REV=HEAD`:** use it while other agents edit the tree, so the attempt routes the
  committed board.
- **Run location:** runs go to `build/route/runs/fome-mc/<label>/<stamp>/`. The
  candidate is `candidate/fome-mc/fome-mc.kicad_pcb`.
- **Continuing a chain:** `make route` always routes `--dir .`. To continue from a
  candidate, call kicad-route directly:
  `kicad-route --out build/route run --backend krt --dir build/route/runs/fome-mc/<label>/<stamp>/candidate/fome-mc …`.
  Then grade the end of the chain with `make route-validate RUN=<last> AGAINST=<first>`.

## Rules here

- Never route the design in place, and never relax rules, severities, widths or
  clearances to make an attempt pass, or to make a board commit pass DRC (`AGENTS.md`).
- A candidate is adopted only by a deliberate design change after review. Commit
  evidence with `make route-publish`; do not commit candidate boards from `build/`.

## What the FOME-MC trials established (2026-10-17)

The full table is in `toolchain/ROUTING.md`.

- **KRT is the productive backend on this partly routed 4-layer board.**
  - Its plane finalize step on `GND`/`+3V3`/`+5V` ran past the budget. Use
    `--backend-env KICAD_PLANE_FINALIZE=0` and plan the planes separately.
  - Its net rescue reworked existing copper. kicad-route now locks existing copper
    during a run.
- **Route the hardest nets first, on the original input.** Finishing leftovers on a
  fully locked candidate routed 0 of 16 on both backends.
- **New F.Cu tracks starve GND thermal spokes.** That's a design call (stitching vias);
  never lower `min_resolved_spokes`.
- **Freerouting was not competitive within 20 minutes on this board.**
- **Open follow-ups from the FOMEMC-10 audit:** FOMEMC-11 (24 single-spoke GND
  thermals; restore `min_resolved_spokes` 2) and FOMEMC-12 (teardrops, 0.127 mm
  tracks, 0.45/0.2 mm vias).
