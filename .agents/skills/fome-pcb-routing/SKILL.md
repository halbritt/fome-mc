---
name: fome-pcb-routing
description: "Use for any fome-mc PCB trace-routing task: run KRT or Freerouting on an isolated copy, read the structured result (process / routing / validation), and plan the next attempt without relaxing the design's constraints."
---

# fome-mc PCB routing

Agent-driven routing for the FOME-MC board (repo `~/git/fome-mc`). Two backends sit
behind one command: **KRT** (KiCadRoutingTools, native KiCad in/out) and
**Freerouting** (via KiCad's Specctra DSN/SES bridge). Full documentation, install and
update notes, and the decision record: `toolchain/ROUTING.md`.

## Ground rules

- The real project is never routed in place. Every attempt copies the project into
  `build/runs/route/<project>/<label>/<stamp>/` and routes the copy. Native KiCad files
  stay authoritative; a candidate becomes design work only when a person adopts it.
- The input's constraints are fixed. Never lower clearances, narrow net-class widths or
  vias, add layers, change connectivity, move footprints, edit zones/keepouts, or relax
  DRC severities to make an attempt pass. Tightening (e.g. `--default-clearance`) is fine.
- The verdict is the wrapper's `result.json`: KiCad's own DRC (zones refilled, schematic
  parity, the input's own `.kicad_pro`/`.kicad_dru`) plus preservation checks. Backend
  self-reports (KRT `JSON_SUMMARY`, Freerouting's result JSON) are diagnostics only.

## Commands (repo root)

| Command | What it does |
|---|---|
| `make route-doctor` | Readiness, versions, capabilities of both backends (`build/route-doctor/doctor.json`) |
| `make route BACKEND=krt\|freerouting [PROJECT=…] [BUDGET=300] [ARGS='…']` | One attempt; prints the run directory |
| `make route-validate RUN=<run_dir>` | Re-grade a candidate (e.g. after hand edits) into `<run_dir>/revalidate/<stamp>/` |
| `make route-compare RUNS='<run_dir> <run_dir> …'` | Side-by-side table; refuses to call different inputs comparable |
| `make route-update` | Move both backends to their latest upstream release, then `route-smoke` |
| `make route-smoke` | Integration tests on the `route-fixture` project |

`ARGS` are `toolchain/route.py run` options:

- Scope: `--nets PAT …` selects by **net name** (fnmatch, `!PAT` excludes);
  `--netclass CLASS …` selects by **effective KiCad net class**. Default: all nets.
- Budget: `--budget SECONDS` (wall clock, default 300); `--max-iterations N` (KRT);
  `--passes N` (Freerouting).
- Protection: `--protect existing` (default: all input copper must survive) or
  `--protect locked` (only locked copper; KRT may rip up unlocked copper).
- Tightening: `--default-clearance MM` (Default net class, both backends);
  `--clearance-margin MM` (Freerouting only).
- Pass-through: `--backend-arg ARG` (repeat), `--backend-env KEY=VALUE` (e.g. KRT `KICAD_*`
  knobs). Recorded in the result; grading is unaffected.
- Input: `--project NAME` (from `toolchain/versions.toml`; `--rev HEAD` routes the
  committed state, recommended while others edit the tree) or `--dir DIR [--board B]`.
- `--label NAME` names the run directory.

## Reading a result

`result.json` reports three independent statuses:

| Field | Values | Meaning |
|---|---|---|
| `process.status` | PASS / FAIL | backend ran and handed back a board (`process.reasons` says why not) |
| `routing.status` | COMPLETE / INCOMPLETE / NOT_RUN | KiCad's unconnected items on in-scope nets after refill |
| `validation.status` | PASS / FAIL / NOT_RUN | no new DRC violations or parity issues vs the input, and every preservation check PASS |

Exit code: 0 complete and valid, 1 process failure (no candidate), 2 valid but incomplete,
3 fails validation. Also read:

- `validation.reasons`, `validation.drc.new_violations.by_type`, and
  `validate/new-findings.json` (each new violation with positions). Pre-existing input
  violations are counted separately and never fail an attempt.
- `validation.preservation`: `project_files`, `board_outline`, `layers`, `stackup`,
  `board_setup`, `nets_and_netclasses`, `pad_connectivity`, `footprints`, `zones`,
  `keepouts`, `copper_graphics`, `protected_copper`, `new_copper_netclass_geometry`,
  `routing_scope`. Details in `validate/preservation.json`.
- `routing.unrouted_nets`, `routing.stats` (new tracks/vias/length), `unsupported`
  (constraints the backend could not see; KiCad still grades them),
  `process.backend_report` (KRT relaxations ledger, Freerouting incomplete count).
- The candidate opens in KiCad: `candidate/<project>/<board>.kicad_pcb` (zones refilled,
  exactly the file that was graded).

## Planning the next attempt

| Evidence | Next attempt |
|---|---|
| new `clearance` violations naming a `.kicad_dru` rule, rule listed in `unsupported` | `--default-clearance <rule value>`; for Freerouting class-to-class rules are already translated, add `--clearance-margin 0.01` for micrometre misses |
| `routing INCOMPLETE`, `unrouted_nets` few | larger `--budget`; Freerouting `--passes 100`; route the hard nets first with `--nets`, then continue from that candidate with `--dir <run>/candidate/<project>` |
| `process FAIL` "exceeded the … budget" (KRT) | larger `--budget`, or `--backend-env KICAD_NET_RESCUE=0` to skip the long rescue search |
| `via_dangling` / `track_dangling` new | Freerouting left fanout stubs on a net it could not finish: treat as incomplete routing; retry as above or with the other backend |
| `protected_copper` / `footprints` / `zones` FAIL | backend or bridge defect: report it (with the run directory); do not adopt the candidate |
| `new_copper_netclass_geometry` FAIL | backend narrowed a conductor below its net class: do not adopt; report the KRT/Freerouting version |
| same failure twice with no new evidence | change approach: other backend, different scope, or inspect the board (load `krt-diagnose-routing-failures`) |

Compare attempts from the same input with `make route-compare`. Deeper diagnosis:
`krt-diagnose-routing-failures`, `krt-review-routed-board` (KRT's own skills, adapted).

## Paths

- Wrapper: `toolchain/route.py`; board facts: `toolchain/route_facts.py`; Specctra
  bridge: `toolchain/route_specctra.py`; fixture: `toolchain/fixtures/route_demo/`.
- KRT: `toolchain/vendor/krt` (latest release checkout) with `toolchain/.venv-route`.
- Freerouting: `toolchain/vendor/freerouting/current/freerouting-*.jar`, run with the
  newest installed JVM that satisfies the jar (Java 25 for 2.5.x).
- Reports: `reports/toolchain/routing/` (fixture evidence, real-board trials).
