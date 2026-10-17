# Agent-driven PCB routing

Local, headless trace routing for FOME-MC with two backends behind one command. An
agent (or a person) asks for an attempt; the wrapper routes an isolated copy of the
project, hands back a native KiCad candidate, and grades it with KiCad's own checks
against the input's unchanged rules. Agents read the structured result and plan the
next attempt. Agent-facing summary: the `fome-pcb-routing` skill.

```sh
make route-doctor                                    # readiness, versions, capabilities
make route BACKEND=krt                               # route fome-mc (copy), 300 s budget
make route BACKEND=freerouting PROJECT=route-fixture ARGS='--clearance-margin 0.01'
make route BACKEND=krt REV=HEAD ARGS='--nets "/CAN*" --budget 600'
make route-validate RUN=build/runs/route/<project>/<label>/<stamp>
make route-compare RUNS='<run_dir> <run_dir>'
make route-update                                    # newest upstream releases + route-smoke
make route-smoke                                     # integration tests on the fixture
```

All of these are thin wrappers over `toolchain/route.py` (`route.py --help`).

## Backends

| | KRT (KiCadRoutingTools) | Freerouting |
|---|---|---|
| Upstream | github.com/drandyhaas/KiCadRoutingTools (MIT) | github.com/freerouting/freerouting (GPL-3.0) |
| Channel used | latest GitHub release, git checkout `toolchain/vendor/krt` | latest GitHub release, executable jar `toolchain/vendor/freerouting/current/` |
| Runtime | `toolchain/.venv-route` (Python 3.12, numpy/scipy/shapely/Pillow from KRT's `requirements.txt` floors) + KRT's prebuilt Rust module | newest installed JVM that satisfies the jar (Java 25 for 2.5.x, apt `openjdk-25-jre-headless`) |
| KiCad interface | reads/writes `.kicad_pcb` directly | KiCad pcbnew SWIG: `ExportSpecctraDSN(board, dsn)` / `ImportSpecctraSES(board, ses)` (`toolchain/route_specctra.py`) |
| Needs a running KiCad editor | no | no (the two-argument SWIG functions work headless) |
| Net-name scope | `--nets` passed through | DSN rewrite: out-of-scope nets move to `<class>__skip` copies (same rules), ignored with `--router.autorouter.ignore_net_classes` |
| Net-class scope | wrapper expands classes to names | same DSN mechanism |
| Budget | wall clock: `KICAD_STOP_FILE` at the budget, kill after a grace period; `--max-iterations` | `--router.job_timeout`, kill after budget + 60 s; `--passes` → `--router.autorouter.max_passes` |
| Existing copper | locked copper never touched; with `--protect existing` (default) unlocked copper is kept too | all pre-existing copper is frozen by Freerouting |
| Custom `.kicad_dru` rules | reads only a subset (track-to-track class rules, layer clearances); logs the rest as skipped — surfaced in `unsupported` | not in Specctra; the bridge translates net-class-to-net-class `clearance` rules to `class_class` rules; others listed as untranslated |

MCP was not used: both backends have working local CLIs, and the existing agents
already drive the project through `make`. Neither backend contacts the network
during an attempt (below).

### What the adapters switch off

KRT relaxes by default. The adapter (`KRT_FLAGS` / `KRT_ENV` in `route.py`) passes
`--escalation off --fab-tier standard --strict-sizes --no-power-tap-neckdown
--no-fix-drc-settings`, plus `--keep-input-copper --no-stub-layer-swap` for
`--protect existing`, and sets `KICAD_INRUN_FLOOR_SYNC=0 KICAD_TERMINAL_ESCALATION=0
KICAD_IMPEDANCE_NECKDOWN=0 KICAD_RESCUE_CAP_MOVE=0 KICAD_DYNAMIC_ITERATIONS=0`
(and `KICAD_RIP_PREEXISTING=0 KICAD_FINALIZE_RIP=0` for `--protect existing`). Without
these, KRT steps down fab tiers, necks wide nets into pads, moves passives to rescue a
net, and writes lowered DRC minimums into its output `.kicad_pro` (seen on the fixture:
`min_hole_clearance` 0.25 → 0.2 with a "FAB FLOOR RELAXED" warning). Two behaviours
cannot be switched off from the CLI in v0.23.x and are caught by the grader instead: a
cleanup pass that may neck new wide segments near foreign pads
(`new_copper_netclass_geometry`), and moving copper text to silkscreen
(`copper_graphics`).

Freerouting is run with `-da` (analytics off), `--api_server.enabled=false`,
`--router.automatic_neckdown=false` (no narrowing into pins), a per-run
`--user_data_path`, and `HTTPS_PROXY/HTTP_PROXY=http://127.0.0.1:9`: Freerouting checks
GitHub for a newer version on every start and has no switch for it; the dead proxy
keeps attempts offline. The SES `(placement ...)` section is removed before import, so
a session can never move footprints.

## Attempts, candidates and results

`route.py run` creates `build/runs/route/<project>/<label>/<stamp>/`:

| Path | Contents |
|---|---|
| `reference/<project>/` | untouched copy of the input (board, `.kicad_pro`, `.kicad_dru`, every reachable schematic sheet, library tables, local libraries; shared libraries linked) — same snapshot code as `eda.py` |
| `work/` | backend scratch: its own output files and project writes (recorded, never used), `krt.log` / `freerouting.log`, `board.dsn` / `board.ses`, result JSON |
| `candidate/<project>/` | the reference project with the routed board; zones refilled and saved; open it in KiCad |
| `facts/reference-facts.json` | engineering facts of the input board (`route_facts.py`) |
| `validate/` | candidate DRC (`candidate-drc.json`), `new-findings.json`, `preservation.json`, `candidate-facts.json` |
| `attempt.json` | input identity, scope, settings, baseline location (used by `route.py validate`) |
| `result.json`, `RESULT.md` | the outcome |

`result.json` holds backend identity and observed version/build, the input fingerprint
(hash over every input file) and git revision, effective settings, every executed
command with exit code, duration and log path, the candidate location, and three
independent results:

- **process** — PASS when the backend ran and returned a board; FAIL with a reason
  (missing install, crash, budget exceeded, bridge failure) otherwise.
- **routing** — COMPLETE / INCOMPLETE from KiCad's unconnected items on in-scope nets in
  the refilled candidate, with `unrouted_nets` and route statistics (new tracks, vias,
  length per layer, removed copper). Backend self-reports are kept under
  `process.backend_report`, not used for the verdict.
- **validation** — PASS when native DRC has no new violations or parity issues relative
  to the input, parity actually ran, the graded file is the delivered file, and every
  preservation check passes.

Exit status: 0 complete and valid; 1 process failure; 2 valid but incomplete; 3 fails
validation (regardless of completion).

### Native grading

The candidate is graded with the installed `kicad-cli` (10.0.7):
`kicad-cli pcb drc --refill-zones --save-board` (fills are saved into the delivered
candidate), then `kicad-cli pcb drc --format json --severity-all --schematic-parity
--units mm` on that saved file. Its project files are the input's, byte for byte, so
KiCad applies the original net classes, custom rules and severities. If a candidate's
project files differ (for example after hand edits), `validate` restores them before
grading and fails the attempt, naming the files. The parity-skip message ("Failed to
fetch schematic netlist…") fails validation, as in `eda.py`.

Pre-existing findings: the untouched input is graded the same way (refill, then DRC)
and cached under `build/route-cache/baseline/<input fingerprint>/`. A candidate finding
is new unless the same type, severity and items (description and position) exist in
the baseline. Only new findings fail.

### Preservation checks

From `route_facts.py` (KiCad's own loader; serialisation differences do not count):

| Check | Compared |
|---|---|
| `project_files` | `.kicad_pro`, `.kicad_dru`, schematics, library tables, local libraries (bytes) |
| `board_outline` | every Edge.Cuts shape, board and footprint owned |
| `layers` | copper layer count and types, enabled layers |
| `stackup` | the `(setup (stackup …))` tree |
| `board_setup` | the rest of the board `(setup …)` tree (plot settings excluded) |
| `nets_and_netclasses` | net names and the effective net class KiCad resolves for each |
| `pad_connectivity` | every pad's net |
| `footprints` | library id, position, orientation, side, lock, pad geometry |
| `zones` | outline, net, layers, priority, clearance, thermal and fill settings (fill polygons are regenerated) |
| `keepouts` | rule-area outlines, layers and restrictions |
| `copper_graphics` | non-track copper shapes and text |
| `protected_copper` | designated tracks/vias still present with the same geometry (1 µm tolerance for Specctra quantisation); designated = locked items, or all input copper with `--protect existing` |
| `new_copper_netclass_geometry` | every new track at least its net class width, every new via at least its class diameter and drill |
| `routing_scope` | new copper only on in-scope nets |

Protected copper across formats: KiCad exports locked tracks/vias as Specctra
`(type fix)` and unlocked ones as `(type route)`; Freerouting freezes both (it reads
`fix` as system-fixed and never writes it back; `route` becomes user-fixed and returns as
`protect`). KiCad's SES import removes every unlocked track and via, keeps locked ones
untouched, and rebuilds the rest from the session — so unlocked copper comes back with
new UUIDs and quantised coordinates, which is why copper is matched by geometry.

### Tightening controls

Allowed because they only make routing stricter; grading is unchanged:
`--default-clearance MM` (Default class: KRT `--clearance`, DSN `kicad_default` class
and board rule), `--clearance-margin MM` (Freerouting: added to every DSN clearance),
plus any backend option through `--backend-arg` / `--backend-env` (recorded in the
result). A relaxing option passed through does not change the verdict; it can only
make the candidate fail.

## Installation and updates

Nothing here is pinned. The versions in use are recorded in every `result.json`,
`build/route-doctor/doctor.json` and `build/route-update/update.json` for diagnosis;
they are not install requirements.

- `make route-update` (`route.py update`):
  - KRT: `git fetch --tags`, check out the latest GitHub release tag, create
    `toolchain/.venv-route` if needed, `uv pip install --upgrade -r requirements.txt`,
    `build_router.py --tag <tag>` (downloads the release's prebuilt Rust module; KRT
    builds from source with cargo only when no prebuilt matches), KRT's
    `startup_checks.py`.
  - Freerouting: download the latest release's `freerouting-<v>.jar`, verify it against
    GitHub's published asset digest, record `release.json`, repoint `current`, remove
    the previous version.
  - Regenerate the `krt-*` skills from the new KRT, then run `make route-smoke`
    (round trips, constraint preservation, native validation, failure reporting).
    Compatibility problems surface there and in `make route-doctor` ("KRT controls used
    by the adapter" fails if a flag the adapter relies on disappears).
- Java: the jar states the Java release it was built for; the wrapper picks the newest
  JVM under `/usr/lib/jvm` that satisfies it. Install new majors with apt
  (`sudo apt install openjdk-<N>-jre-headless`); security updates arrive with normal
  `apt upgrade`. The system default `java` stays where it was (here 21:
  `sudo update-alternatives --set java /usr/lib/jvm/java-21-openjdk-amd64/bin/java`
  after installing 25, which apt otherwise makes the default).
- Following KRT `main` instead of releases: `git -C toolchain/vendor/krt checkout
  origin/main && toolchain/.venv-route/bin/python toolchain/vendor/krt/build_router.py`
  (needs a Rust toolchain when `main`'s crate is ahead of the latest release); then
  `make route-smoke`.
- Fresh clone: `make route-update` installs everything except the JVM.

### Observed at setup (2026-10-17)

| Component | Observed |
|---|---|
| KiCad / kicad-cli | 10.0.7 (`10.0.7~ubuntu24.04.1`) |
| KRT | v0.23.1 (`295f9ee`), grid_router 0.23.1 prebuilt |
| KRT Python deps | Python 3.12.3, numpy 2.5.4, scipy 1.18.1, shapely 2.2.0, Pillow 13.0.0 |
| Freerouting | v2.5.0 jar, sha256 `f6f51bb0…5de3c7`, build revision `b647a2f` |
| Java for Freerouting | OpenJDK 25.0.4.1 (`openjdk-25-jre-headless 25.0.4.1+1-1~24.04.4`) |

## Decisions

- **Freerouting jar, not the native CLI.** v2.5.0 introduced
  `freerouting-cli-<v>-linux-x64` (GraalVM native image). It crashes in
  `BoardSnapshotManager.serialize` as soon as routing starts and then hangs without
  writing a session (upstream issue #957, fixed on master by PR #966, not yet released).
  The jar has the same CLI and works. Revisit when a release contains the fix: the
  native binary needs no JVM.
- **Java 25 from apt.** The 2.5.0 jar is built for Java 25 (class file 69) and fails on
  the installed Java 21. apt's `openjdk-25-jre-headless` gets normal security updates;
  the system default `java` was left at 21.
- **KRT latest release, not `main`.** Releases carry the matching prebuilt Rust module
  (no Rust toolchain on this machine); `main` moves several times a day.
- **pcbnew SWIG for the Specctra bridge.** `kicad-cli` 10.0.7 has no DSN export or SES
  import (`kicad-cli pcb import` reads only foreign CAD formats). The one-argument SWIG
  functions need the PCB editor; the two-argument ones work headless. KiCad marks SWIG
  as deprecated in favour of the IPC API, which needs a running KiCad; when a KiCad
  release removes SWIG, the bridge and `route_facts.py` need an IPC-based replacement.
- **Grading is KiCad's, always.** Backend reports disagree with KiCad in both
  directions (below); only KiCad's DRC against the original project decides.

## Known limitations

- KRT honours only part of `.kicad_dru` (it logs skipped rules; they appear under
  `unsupported`). On the fixture, its default attempt violates a Power-to-signal 0.4 mm
  rule; `--default-clearance 0.4` produces a valid candidate.
- KRT's net rescue keeps searching unroutable nets and does not check the stop file
  inside that loop; on a blocked board it exceeds the budget and is killed (process
  FAIL, no candidate). `--backend-env KICAD_NET_RESCUE=0` returns a partial candidate.
- KRT exits 0 even when nets fail; the wrapper ignores its exit code for completion.
- Freerouting approximates pad shapes and can land a few micrometres inside a clearance
  (fixture: 0.3928 mm against a 0.4 mm rule); `--clearance-margin 0.01` resolved it.
- Specctra export rounds pad centres to 1 µm, so Freerouting can report a locked track
  that ends on a pad centre (e.g. 124.0875 mm) as unconnected; KiCad sees it connected.
  Recorded in `process.backend_report`, not used for the verdict.
- Freerouting leaves fanout vias on nets it cannot finish (`via_dangling` findings), and
  stops when its score stops improving; more `--passes` or another scope may help.
- Freerouting only places through vias and cannot see custom rules other than
  class-to-class clearances, diff pairs, or length tuning; arcs export as chords.
- Attempts route one scope at a time; chain scopes by routing from a previous candidate
  (`--dir <run>/candidate/<project>`), which keeps the original rules (the candidate's
  project files are the input's).
- Board facts and the bridge depend on KiCad's SWIG module (see Decisions).

## Fixture and evidence

`toolchain/fixtures/route_demo/` (project `route-fixture`, regenerate with
`toolchain/.venv/bin/python toolchain/fixtures/route_demo/generate.py`) is a 2-layer
50 × 30 mm board with KiCad's stock stackup, two net classes (Default 0.2/0.2 mm, Power
0.5/0.3 mm with 0.8/0.4 vias), a custom `.kicad_dru` rule (Power to non-Power ≥ 0.4 mm),
a keepout across the direct J1→J2 path, a GND zone on B.Cu, and a locked, pre-routed
`/SIG_B` (5 tracks, 2 vias). The input is ERC/DRC/parity clean with 6 unconnected items.

`make route-smoke` (11 tests, `toolchain/tests/test_routing.py`) publishes its evidence
to `reports/toolchain/routing/fixture/`: per-test records, junit, and for each attempt
`result.json`, `RESULT.md`, `preservation.json`, `new-findings.json`,
`candidate-drc.json`. It proves:

- KRT and Freerouting round trips that are complete and valid, with every preservation
  check passing and the candidate's rules byte-identical to the input's;
- the KRT default attempt fails validation on the custom rule, and the failure is the
  exit code (3), with the skipped rule named under `unsupported`;
- net-name (`--nets '/SIG_A*'`) and net-class (`--netclass Power`) scopes, with no
  copper outside scope;
- an unroutable variant (keepout wall) comes back INCOMPLETE from both backends, and a
  budget overrun is a process failure (exit 1);
- a tampered candidate (footprint moved 0.5 mm, a locked via deleted, a Power track
  narrowed to 0.3 mm, a project clearance lowered) fails `validate` on `footprints`,
  `protected_copper`, `new_copper_netclass_geometry` and `project_files`;
- `compare` refuses to call different inputs comparable;
- the source fixture is byte-identical after the whole run.

Real-board trials are in `reports/toolchain/routing/fome-mc/` (see below).
