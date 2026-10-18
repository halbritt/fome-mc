# fome-mc EDA toolchain

CLI-first, pinned tooling for the FOME-MC motorcycle ECU (this repo, `~/git/fome-mc`).
The Polygonus Universal 112 dual-WBO board
(`~/git/Polygonus-Universal-112`) is the electrical baseline and is checked read-only
alongside it.

Scope: tool installation and integration only. Native KiCad files stay
authoritative; nothing here edits, refills, upgrades or re-saves a design file.

PCB trace routing (KRT and Freerouting, `make route-*`) uses the standalone
[kicad-route](https://github.com/halbritt/kicad-route) tool, installed once per machine;
see [ROUTING.md](ROUTING.md). Unlike the pinned tools here, kicad-route and its backends
follow their latest upstream releases.

## Quick start

```bash
make bootstrap   # install/repair everything (uses sudo for apt), then doctor
make doctor      # verify versions, dependencies, libraries, capabilities, skills
make smoke       # integration checks on the RC fixture -> reports/toolchain/smoke/
make check       # ERC, DRC, netlist, exports, analysis on fome-mc (one snapshot)
make baseline    # read-only: committed HEAD of fome-mc + universal-112, and fome-mc's
                 # working tree -> reports/toolchain/baseline/
```

`toolchain/bootstrap.sh --no-apt` skips system packages (no sudo).

## What is installed (pins in `versions.toml`, `pyproject.toml`, `uv.lock`)

| Component | Version | Source / location |
|---|---|---|
| KiCad (`kicad-cli`, pcbnew bindings) | 10.0.7 stable | apt, `ppa:kicad/kicad-10.0-releases` (existing install) |
| KiCad stock symbols/footprints/templates | 10.0.7 | apt `kicad-symbols`, `kicad-footprints`, `kicad-templates` |
| ngspice (standalone CLI) | 42 (`42+ds-3build1`) | apt (Ubuntu noble) |
| KiBot | 1.9.1 (+ KiAuto 2.3.10) | `toolchain/.venv` via `uv.lock` |
| kicad-happy | v2.3.1 `06840467ad0f` | `toolchain/vendor/kicad-happy` (git, pinned commit) |
| Python | 3.12.3 (system interpreter, isolated venv) | `toolchain/.venv`: pytest 8.4.2, numpy 2.3.3, jsonschema 4.25.1, PyYAML 6.0.3, lxml 6.0.2 |
| PDF tools | poppler-utils 24.02.0, mupdf-tools 1.23.10, ghostscript 10.02.1 | apt |
| rsvg-convert | librsvg2-bin 2.58.0 | apt (KiBot `pcb_print` PDF) |

The venv is created from `/usr/bin/python3` and sees exactly three things from the
system: `pcbnew.py`, `_pcbnew.so` and `wx` (through `.venv/kicad-shim` and a `.pth`
file). KiBot needs KiCad's own bindings and the wxPython they were built against;
nothing else from system site-packages leaks in, and system Python is not modified.

KiBot runs with `-A` (no dependency auto-download). The stock 3D model library is
optional; `doctor` reports `UNSUPPORTED` when it is absent. The separate
[3D render workflow](#3d-board-renders) can use a persistent model cache.

## 3D board renders

`make render-3d` calls the installed `agent-ee render3d` command to render the
saved FOME board. It is separate from `make check`, `make export`, `make renders`
and `make smoke`; ordinary checks do not launch these expensive renders.

```sh
# First use: explicitly permit stock model downloads into a persistent cache:
make render-3d MODELS="$HOME/.cache/agent-ee/models" FETCH_MODELS=1
# Later runs can use the populated cache without downloads:
make render-3d
# Smaller preview using the same three native views:
make render-3d RENDER_WIDTH=800 RENDER_HEIGHT=600
# Inspect the images and model coverage, then publish the selected run:
make render-3d-publish RUN=build/runs/project/fome-mc/3d-renders-<stamp>
```

Install an agent-ee version with `render3d`, or select its launcher with
`AGENT_EE=/path/to/agent-ee/bin/agent-ee`. `MODELS` defaults to
`$HOME/.cache/agent-ee/models`; network model fetching requires `FETCH_MODELS=1`.
Populate that cache explicitly or select an existing model directory before an
offline run. A missing cache is an error; ordinary rendering does not download it.
`RENDER_WIDTH=4096`, `RENDER_HEIGHT=3072`, `RENDER_QUALITY=high`, `RENDER_JOBS=3`
and `RENDER_TIMEOUT=1200` set the defaults. The timeout is passed to agent-ee in
seconds. Native KiCad may produce dimensions slightly smaller than requested;
the manifest records the actual dimensions.

Each call creates a fresh `build/runs/project/fome-mc/3d-renders-<UTC stamp>/`
containing the native renderer's staged inputs, logs and `render-manifest.json`.
The adapter does not edit or refill the source board. Publication requires a
completed manifest with unchanged source, all three views with matching PNG dimensions and hashes,
and board/project hashes matching the current checkout. It replaces only
`fome-mc-3d-top.png`, `fome-mc-3d-bottom.png`, `fome-mc-3d-isometric.png` and
`render-manifest.json` in `docs/renders/3d/`. Invalid or partial runs leave the
published files untouched. Rerender after changing the source board or project.

Read `model_coverage` and the retained native logs before publishing. Stock
models cannot supply component bodies for footprints with no model reference
or unavailable custom models. A completed render is a visual preview and does
not establish mechanical clearance, ERC/DRC success or fabrication approval.

## Commands

The native check targets take `PROJECT=fome-mc|telemetry-pod|universal-112|fixture` (default `fome-mc`),
`FILL=asis|refill` (default `asis`) and `REV=<git revision>` (snapshot a committed
revision via `git archive` instead of the working tree; the run is labelled
`<project>@<rev>`).

| Target | Native command(s) |
|---|---|
| `erc` | `kicad-cli sch erc --format json --severity-all --units mm` |
| `drc` | `kicad-cli pcb drc --format json --severity-all --schematic-parity --units mm` |
| `netlist` | `kicad-cli sch export netlist --format kicadsexpr` → `connectivity.json` |
| `export` | DRC first, then `kicad-cli sch export pdf/svg/bom`, `kicad-cli pcb export pdf`, and `kibot -A -c toolchain/kibot/export.kibot.yaml` (Gerbers + job file, Excellon + report + map, positions, BOM CSV/HTML, schematic PDF, PCB print PDF) |
| `analyze` | kicad-happy `analyze_schematic.py` → `analyze_pcb.py --full --schematic schematic.json` → `cross_analysis.py` → `simulate_subcircuits.py --simulator ngspice` |
| `check` | all five steps on one snapshot |
| `renders` | `python3 scripts/render_docs.py` (regenerate 16 schematic SVGs/PDFs + 14 PCB SVGs/PDFs + composite renders) |
| `verify-io` | `python3 scripts/verify_io_map.py --project <PROJECT>` (default ECU audit or project-local I/O map and contracts; see below) |
| `fab-package [REV=HEAD]` | `python3 scripts/generate_fab_package.py --project <PROJECT>` (normalize Gerbers/drills and emit the project's `reports/toolchain/fab-manifest.json`) |
| `verify-fab-package [REV=HEAD]` | `python3 scripts/generate_fab_package.py --project <PROJECT> --verify` (verify `fab-manifest.json` SHA-256 parity and zero-diff reproducibility) |
| `simulate DECK=… [EXPECT=…]` | ngspice via a generated control script (below) |
| `smoke` | `pytest toolchain/tests` |
| `baseline` | `check` on the committed HEAD of fome-mc and universal-112, plus fome-mc's working tree (`fome-mc-worktree`); publishes reports |
| `doctor`, `bootstrap`, `skills` | environment check / install / regenerate agent skills |

Direct use: `python3 toolchain/eda.py --help`.

## Project I/O maps and fabrication packages

`make verify-io PROJECT=fome-mc` keeps the ECU audit, including its pin expectations,
firmware configuration in `~/git/fome-fw`, YAML connectors and sheet contracts.
`make verify-io PROJECT=telemetry-pod` reads `telemetry-pod/io-map.csv`, then
requires exactly `contracts/telemetry-pod.interface.json` at the repository root.
Until AGENTEE-188 generates that contract, it exits nonzero with
`missing interface contract: <repo>/contracts/telemetry-pod.interface.json`.
It does not accept the CSV alone or substitute the ECU's sheet contracts.

For projects other than `fome-mc`, the CSV header must match FOMEMC-30 exactly,
including column order:

```text
Connector_Pin,Signal_Name,Net,Direction_Class,Voltage_Current_Domain,MCU_Ref,MCU_Pin,External_Destination,Notes
```

Empty maps, duplicate `Connector_Pin` values, ragged rows and blank cells fail.
The reader preserves logical identifiers such as `AMPSEAL-1`, `BLE-RADIO` and
`DEBUG-UART-TX`. Reading those rows does not establish native pin bindings.
The landed pod map contains proposed net names, `N/C` cavities and an integrated
radio with `Net=N/A`; reconciling these with the generated design remains an
AGENTEE-188 obligation. See [the pod input notes](../telemetry-pod/IO_MAP.md).

The current native audit requires every pin of every `J<number>` connector to
appear exactly once as `<reference>-<pin>`, with its exact KiCad net name
(including any leading `/`) and a terminal declaration in a loaded
`agent-ee.interface/1` contract. It fails closed on unresolved logical identifiers;
it cannot yet bind the pod's logical rows to generated references or interpret
`N/C` and `N/A` as physical connectivity. Other projects load
`<project>/contracts/*.interface.json`; the pod loads only the root contract named
above. All contract invariants are evaluated against a fresh native XML netlist,
exported from a snapshot under `build/runs/verify-io/<project>/`. This verifier uses
the existing `agent-ee.hardware_interface` evaluator, not the planned generic
`io_map` capability. Its existing checkout is expected at `~/git/agent-ee`.
This command does not generate design content.

`make fab-package PROJECT=<name>` and `make verify-fab-package PROJECT=<name>` take
project directories and native filenames from `toolchain/versions.toml`. Packaging
is restricted to projects inside this repository. Outputs are isolated in that
project's `export/gerbers/` and `reports/toolchain/fab-manifest.json`; `fome-mc`
continues to use the repository-root paths and existing manifest schema. Schematic
exports use the schematic stem; positions use the PCB stem. Optional tracked BOM, CPL and netlist inputs
are `export/BOM-<stem>.csv`, `export/CPL-<stem>.csv` and `export/<stem>.net` within
the project. The script records their hashes; it does not perform a BOM/CPL parity
audit. An existing `--run-dir` must belong to the selected project.

The project-script regression tests can run without the toolchain venv:
`python3 -m unittest discover -s toolchain/tests -p test_project_scripts.py -v`.
They still require the existing agent-ee checkout and native KiCad CLI.

## Results

Each step writes `result.json` with `status`, `reasons`, the exact `commands`
(argv, cwd, exit code, duration, log path), input sha256s, output sha256s/sizes and
`findings`. Each run writes `snapshot.json`, `summary.json` and `SUMMARY.md`.

- `PASS` — the tool ran and produced a complete, well-formed result.
- `FAIL` — tool missing, crashed, timed out, malformed/missing output, or work was
  skipped (examples below).
- `NOT_RUN` — prerequisite failed (e.g. export without a DRC on the same snapshot).
- `UNSUPPORTED` — not possible with this toolchain (e.g. a SPICE deck with its own
  `.control` block, a project without a PCB).

Check status is separate from the design verdict. A design with violations gives
`PASS` + `design_clean: false` + counts by severity/type in `findings`.

Skipped work that is detected and turned into `FAIL`:

- DRC that could not load the schematic: kicad-cli prints "Failed to fetch schematic
  netlist for parity tests", reports **zero** parity issues and exits 0.
- ERC whose report covers fewer sheet instances than the hierarchy has.
- A referenced sheet file that does not exist, or components placed in the schematic
  files that are missing from the native netlist (a sheet KiCad silently did not load).
- kicad-happy PCB analysis that did not consume the `--schematic` cross-reference
  (`power_net_resolution.source` must be `schematic`).
- KiBot errors other than the documented non-critical one, or any expected bundle file
  missing/empty; PDFs with zero pages; a schematic PDF that contains none of the
  netlist references.
- ngspice: see below.

## Snapshots, libraries and zone fill

Every run copies the project's KiCad files (schematics reachable from the root, PCB,
project, library tables, project-local libraries) to
`build/runs/project/<project>/<UTC stamp>/snapshot/` and runs everything there.
KiCad writes `.kicad_prl` and other files into a project directory when it opens it;
that never reaches the source tree. `snapshot.json` records every file's sha256, the
source git HEAD and which snapshot files were uncommitted. A working-tree run is a
point-in-time record that includes uncommitted edits (other agents may be editing the
design); `REV=HEAD` (and `make baseline`) snapshot exactly what is committed.

KiCad configuration is hermetic: `KICAD_CONFIG_HOME=build/kicad-config` holds the stock
global library tables, `KICAD10_{SYMBOL,FOOTPRINT,TEMPLATE}_DIR` point at
`/usr/share/kicad`, so results do not depend on GUI preferences.

Custom libraries resolve through the shared repository `~/git/kicad-libraries`
(FOME-Tech/kicad-libraries; override with `FOME_KICAD_LIBS`):

- `${KIPRJMOD}/../<dir>` references are recreated in the snapshot as symlinks to the
  real sibling directory (fome-mc's tables use `../kicad-libraries`).
- universal-112's `fome-kicad-libs` submodule is not initialised; the snapshot links it
  to `~/git/kicad-libraries`, and doctor checks that the submodule pin
  (`ab9c5f8a1517`) equals the library repository's HEAD.
- Library-table entries that do not exist are listed under "Library resolution issues".

Zone fill: `FILL=asis` checks and exports the fill saved in the board. `FILL=refill`
runs `kicad-cli pcb drc --refill-zones --save-board` on the snapshot, then a normal DRC
on the saved file. `--refill-zones` without `--save-board` refills only in memory: DRC
looks clean but the file, and therefore every export, is unchanged (the smoke test
demonstrates this). Export records the board sha256 and refuses to run if it differs
from the one DRC checked; it also verifies no exporter modified the board.

## ngspice

Decks are plain netlists (analyses + `.meas`), without `.control`. The runner writes a
control script and runs `ngspice -n -b -o ngspice.log control.sp`:

```
.control
set ngbehavior=kicad
set num_threads=1
set noaskquit
source <deck>
run
write <out>/result.raw
quit
.endc
```

- `-n` keeps `~/.spiceinit` out; compatibility (`ngbehavior=kicad`) is explicit.
- Not `ngspice -b -r file`: in that mode ngspice writes the raw file but silently skips
  `.meas` (verified on ngspice 42), and exits 0 either way.
- Every `.meas` in the deck must appear in the log as a finite number. "failed!",
  `Error`, "Timestep too small", singular matrix, no convergence or aborted runs fail.
  The raw file is parsed (numpy) and must be complete and finite.
- Output goes to a fresh directory; `--out` refuses a non-empty directory.
- `EXPECT=file.json` adds assertions: `{"measurements": {"name": {"expected": x,
  "rel_tol": r, "abs_tol": a}}}`.

## Smoke fixture

`toolchain/fixtures/rc_filter/` is a 3-part RC low-pass (J1 header, R1 10k, C1 100n,
GND zone on B.Cu), separate from the ECU design. `generate.py` regenerates it from the
stock libraries through `kicad-cli sch upgrade` and the pcbnew API. `make smoke`
(18 tests) proves:

- native ERC/DRC/parity are clean on the fixture, and do report an injected fault
  (removed wire → `pin_not_connected`; removed track → unconnected; changed value →
  parity mismatch); DRC without its schematic is a FAIL, not a clean pass;
- the netlist has exactly the expected components and nets;
- schematic/PCB PDF/SVG, BOM and the full KiBot bundle exist and contain the design
  (B.Cu Gerber contains zone regions);
- kicad-happy schematic + PCB (+ `--schematic` cross-reference) + cross-analysis + SPICE
  run, and its RC detection matches 1/(2πRC);
- the in-memory vs saved zone-fill difference above;
- ngspice step response matches V = 1 − e^(−t/RC) at the `.meas` points and over the
  whole waveform, including a deck built from KiCad's own SPICE netlist export; a
  missing measurement, a `.control` deck, a wrong expectation and a reused output
  directory are all rejected;
- missing or case-mismatched sheets and unloaded sheet content are detected;
- pdftotext/pdftoppm/mutool read and render PDF pages;
- the agent skills are in sync with the pinned upstream and do not shadow skillpack.

## Agent skills

| Skill | Kind | Content |
|---|---|---|
| `fome-eda-toolchain` | project-owned | commands, paths, result semantics, fill/SPICE rules |
| `kicad-happy-kicad` | upstream, pinned | kicad-happy `kicad` skill |
| `kicad-happy-spice` | upstream, pinned | kicad-happy `spice` skill |
| `kicad-happy-datasheets` | upstream, pinned | kicad-happy `datasheets` skill |
| `fome-pcb-routing` | project-owned | fome-mc routing targets, paths and trial lessons ([ROUTING.md](ROUTING.md)) |

The generic routing skills (`kicad-route`, `krt-diagnose-routing-failures`,
`krt-review-routed-board`) are installed globally by kicad-route's `scripts/install.sh`
and `kicad-route update`, not kept in this repo.

They live in `.agents/skills/<name>/` (read by Codex, Antigravity `agy` and OpenCode)
with `.claude/skills/<name>` symlinks (Claude Code). This follows the repository-level
skill stores that `~/git/skillpack/check-repo-skills.py` recognises; skillpack itself is
reserved for graduated skills deployed to every harness, so these project-specific
skills are not added there. `make smoke` runs skillpack's shadow check. Hermes is not
used for this project and has no project-level skill store.

`toolchain/sync_skills.py` generates the `kicad-happy-*` skills from the pinned checkout:
upstream body verbatim, `name` prefixed (no generic `kicad`/`spice`/`datasheets` names),
a short house `description`, a marked project header (skill path, project overrides),
the upstream MIT `LICENSE` and `UPSTREAM.json` provenance. Scripts and references stay in
`toolchain/vendor/kicad-happy` because they import sibling skills by relative path.
Upstream's `emc`, `bom` and distributor/sourcing skills are deliberately not exposed.

Verified 2026-10-16 from the repo root: `opencode debug skill`, `codex debug
prompt-input`, `agy -p` and `claude -p` each list all five repo skills.

To move kicad-happy: change `[upstream.kicad-happy]` in `versions.toml`, run
`make bootstrap` (checks out the commit and regenerates the skills), review the diff of
`.agents/skills/`, run `make smoke`.

## Known limitations

- `fome-mc` schematics are KiCad 7/8 (`20211123`/`20230121`) and `fome-mc.kicad_pcb` is
  KiCad 10 (`20260206`); `universal-112` is KiCad 9, all checked with KiCad 10.0.7. Only
  snapshots are touched; `FILL=refill` saves the snapshot board in KiCad 10 format, never
  the source.
- KiBot logs `ERROR: Unable to expand REFERENCE in ${REFERENCE}` on boards whose stock
  footprints carry `${REFERENCE}` fab text (KiBot's `non_critical_error`; KiCad expands
  it when plotting). It is listed under `kibot_diagnostics.known_non_critical` and does
  not fail the export. Any other KiBot error does.
- KiBot warns `W181 Unable to map the SCH file to an UUID` for pre-KiCad-10 projects
  (no `schematic.top_level_sheets` in the `.kicad_pro`); harmless.
- kicad-happy's own findings include upstream policies (e.g. DS-001 "no datasheets
  directory / no MPNs"). They are reported as-is, not adopted as project rules.
- `make render-3d` handles optional native 3D images through agent-ee. STEP export
  is not configured by this toolchain.
- KiCad 10's IPC API, MCP servers, field solvers and editing helpers (akcli,
  kicad-tools) are not installed; no current project operation needs them.
