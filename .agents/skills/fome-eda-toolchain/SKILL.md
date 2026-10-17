---
name: fome-eda-toolchain
description: "Use for any fome-mc KiCad, ngspice, KiBot or kicad-happy task: make targets, pinned versions, library paths, snapshot and zone-fill rules, result semantics, and output locations."
---

# fome-mc EDA toolchain

Project-specific entry points for the FOME-MC motorcycle ECU (repo `~/git/fome-mc`).
Full documentation: `toolchain/README.md`.

## Ground rules

- Native KiCad project files are authoritative. Do not edit, refill, upgrade or re-save
  design files as part of a check. All commands below copy the project into a fresh
  snapshot under `build/runs/` and work only on the copy.
- KiCad's own `kicad-cli` ERC/DRC/netlist are the native checks. kicad-happy analysis
  supplements them; it never replaces, overrides or suppresses them.
- Check status is about the tool, not the design: `PASS` means the tool ran to
  completion and produced a complete, well-formed result. Design violations are in
  `findings` / `design_clean`. `FAIL` means missing tool, crash, malformed output or
  skipped work (for example DRC that could not load the schematic for parity).
  `NOT_RUN` means a prerequisite failed; `UNSUPPORTED` means the operation is not
  available in this toolchain. Never report a FAIL/NOT_RUN step as a design result.

## Commands (run from the repo root)

| Command | What it does |
|---|---|
| `make bootstrap` | Install/repair pinned tools, venv, kicad-happy, skills; then doctor |
| `make doctor` | Check executables, versions, venv, libraries, capabilities, skills |
| `make erc` | `kicad-cli sch erc` (JSON, all severities) |
| `make drc` | `kicad-cli pcb drc --schematic-parity` (JSON, all severities) |
| `make netlist` | `kicad-cli sch export netlist` + parsed `connectivity.json` |
| `make export` | DRC, then schematic PDF/SVG, PCB PDF, BOM CSV and the KiBot bundle from the same board |
| `make analyze` | kicad-happy schematic → PCB (`--schematic` cross-reference) → cross-analysis → SPICE |
| `make check` | All of the above in one snapshot |
| `make simulate DECK=path.cir [EXPECT=path.json]` | ngspice run with `.meas` validation |
| `make smoke` | Toolchain integration tests on the RC fixture |
| `make baseline` | Read-only run on committed fome-mc and Universal-112 (+ fome-mc working tree); publishes `reports/toolchain/baseline/` |

Options: `PROJECT=fome-mc|universal-112|fixture` (default `fome-mc`), `FILL=asis|refill`,
`REV=<git rev>` (check a committed revision instead of the working tree, which may hold
other agents' unfinished edits).
Projects are defined in `toolchain/versions.toml`.

## Outputs

- Every run: `build/runs/project/<project>/<UTC stamp>/` (`latest` symlink), containing
  `snapshot/` (the copy that was checked), `snapshot.json` (file sha256s, source git
  head, uncommitted files, library links), `summary.json`, `SUMMARY.md`, and one
  directory per step with `result.json`, tool logs and the tool's own reports
  (`erc/erc.json`, `drc/drc.json`, `netlist/*.net`, `export/native/`, `export/kibot/`,
  `analyze/{schematic,pcb,cross,spice}.json`).
- Simulations: `build/runs/sim/<deck>/<stamp>/simulate/` (`result.json`, `ngspice.log`,
  `result.raw`, generated `control.sp`).
- Committed reports: `reports/toolchain/smoke/` and `reports/toolchain/baseline/`.

## Zone fill

`FILL=asis` (default) checks and exports the copper fill saved in the board file.
`FILL=refill` runs `kicad-cli pcb drc --refill-zones --save-board` on the snapshot,
then checks and exports the saved result. `--refill-zones` alone refills only in
memory and leaves the file unchanged; exports would not match. Export refuses to run
if the board hash differs from the one DRC checked.

## SPICE decks

Write plain netlists with analyses and `.meas` statements and no `.control` block. The
runner generates the control script (`set ngbehavior=kicad`, `source`, `run`, `write`)
and runs `ngspice -n -b` (no `~/.spiceinit`). Do not rely on `ngspice -b -r`: in that
mode ngspice writes the raw file but silently skips `.meas`. Missing, failed or
non-finite measurements, convergence errors and incomplete raw files fail the run.
Output directories must be fresh. Example: `toolchain/fixtures/rc_filter/sim/`.

## Paths

- Tools: `kicad-cli` (system, KiCad 10.0.7 stable), `ngspice` 42, `toolchain/.venv/bin/kibot`
  (KiBot 1.9.1, run with `-A`), kicad-happy v2.3.1 at `toolchain/vendor/kicad-happy`.
- Libraries: project tables use `${KIPRJMOD}`; the shared FOME library repository is
  `~/git/kicad-libraries` (`FOME_KICAD_LIBS`). Snapshots link `../kicad-libraries` and the
  donor's uninitialised `fome-kicad-libs` submodule to it. Stock KiCad libraries are
  under `/usr/share/kicad/{symbols,footprints}`.
- KiCad config is hermetic: `KICAD_CONFIG_HOME=build/kicad-config` with stock global
  library tables, so results do not depend on GUI settings.
- Datasheet PDFs: `pdftotext -layout -f N -l M file.pdf -` for text,
  `pdftoppm -png -r 150 -f N -l N file.pdf out` to render a page you can view,
  `pdfinfo` for page counts, `mutool draw -F txt` as a fallback.
- Related skills: `kicad-happy-kicad`, `kicad-happy-spice`, `kicad-happy-datasheets`
  (pinned upstream, with a project header).
