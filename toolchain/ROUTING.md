# PCB routing for FOME-MC

Routing uses [kicad-route](https://github.com/halbritt/kicad-route), a standalone tool
(source checkout `~/git/kicad-route`). It runs KRT or Freerouting on an isolated copy of
the board and grades the candidate with KiCad's own DRC and parity against the board's
unchanged rules. Its design, backends, result semantics, preservation checks, install and
update notes, decisions and limitations are documented in
[kicad-route `docs/routing.md`](https://github.com/halbritt/kicad-route/blob/main/docs/routing.md);
agents load the global `kicad-route` skill and this project's `fome-pcb-routing` skill.

Install once per machine (the backends follow their latest upstream releases; nothing is
pinned):

```sh
git clone https://github.com/halbritt/kicad-route ~/git/kicad-route
~/git/kicad-route/scripts/install.sh       # kicad-route on PATH, skills linked, backends installed
make route-doctor
```

## Commands (repo root)

| Command | What it does |
|---|---|
| `make route-doctor` | readiness, versions, capabilities of both backends |
| `make route BACKEND=krt\|freerouting [BUDGET=300] [REV=HEAD] [ARGS='…']` | one attempt on a copy of the board (`REV=HEAD` routes the committed state, recommended while others edit the tree) |
| `make route-campaign BACKEND=krt\|freerouting [BUDGET=300] [REV=HEAD] [ROUNDS=2] [RACE=0] [TOTAL_BUDGET=s] [ARGS='…']` | hard-nets-first campaign: several runs (`BUDGET` is per run), the best chain graded against the original input |
| `make route-validate RUN=<run> [AGAINST=<first run>] [ARGS='…']` | re-grade a candidate, or the end of a `--dir` chain against its first input (`ARGS`: `--pour-area-loss PCT`, `--pour-min-spokes N`) |
| `make route-compare RUNS='<run> <run>'` | side-by-side table of attempts from the same input |
| `make route-blocked RUN=<run> [TOP=10]` | which obstacles lie across the connections an incomplete run left open |
| `make route-spokes RUN=<run> [VALIDATION=<dir>]` | which new copper starved which thermal pad (writes `<run>/spokes.json`) |
| `make route-spokes BOARD=<file> [PER_PAD=n]` | plan thermal-spoke corridors for a board file (read, not saved; point it at a run's `reference/` copy) |
| `make route-publish RUN=<run>` | copy an attempt's structured evidence to `reports/toolchain/routing/<project>/<label>/` |
| `make route-audit OLD=<rev> [NEW=HEAD]` | grade a committed board change against its parent (DRC, parity, rule changes and what they hide, design edits) |
| `make route-floor [SINCE=<rev>] [WRITE=1] [NETCLASS_SIZES=1]` | rule high-water mark of the board's history against its declared floor; `WRITE=1` drafts a `rules-floor.json` under `build/route` for review |
| `make route-canary [BACKEND=all\|krt\|freerouting]` | awkward net names through each backend's round trip (on kicad-route's fixture) |
| `make route-corpus-list` / `route-corpus-check [NAME=<entry>]` | list kicad-route's real-board regression corpus / re-run it against the baselines |
| `make route-corpus-add BACKEND=krt\|freerouting [NAME=<project>] [BUDGET=300] [REV=HEAD] [ARGS='…']` | snapshot the board into that corpus with one baseline attempt |
| `make route-update` | update both backends and kicad-route's generated skills, then its integration tests |
| `make route-smoke` | kicad-route's integration tests on its fixture board |

The targets route `PROJECT` (default `fome-mc`; also `universal-112`, `fixture`). Its
directory, board, schematic and `library_dirs` come from `toolchain/versions.toml`, and
the project name names the run directory. `ARGS` are `kicad-route run` options
(`kicad-route run --help`; `campaign` takes the same ones, `corpus add` a subset): `--nets`,
`--netclass`, `--protect`, `--default-clearance`, `--clearance-margin`, `--passes`,
`--max-iterations`, `--backend-arg`, `--backend-env`, `--reserve-spokes`, `--stall`,
`--label`. Runs land in `build/route/runs/<project>/<label>/<stamp>/` (ignored); for
fome-mc the candidate is `candidate/fome-mc/fome-mc.kicad_pcb` and the verdict
`result.json`. The corpus lives in kicad-route's state (`STATE/corpus` or
`$KICAD_ROUTE_CORPUS`), not in this repo; `make route-update` re-checks it.

Project rules for routing: never route the design in place, never relax rules,
severities, widths or clearances to make an attempt pass (see `AGENTS.md`), and adopt a
candidate only by a deliberate design change after review. Board commits made by hand or
by other agents can be checked the same way with `make route-audit`; the first such audit
(`216eb9a`, FOMEMC-10) is in `reports/toolchain/routing/fome-mc/verify-216eb9a/`.

## FOME-MC real-board trials (2026-10-17)

Bounded trials on an isolated copy of the committed board (`--rev HEAD` at `e763e31` and
`351339c`; every trial has the same input fingerprint `e1bfff18…`, the board last
changed in `f3b0f47`): 475 footprints, 4 copper layers, placed and partly routed
(2899 tracks, 879 vias, none locked). The untouched input already has 228 DRC violations,
235 unconnected items and 382 parity issues (graded the same way: refill, then DRC);
they are counted as pre-existing. All nets in scope unless noted, `--protect existing`. Evidence in
`reports/toolchain/routing/fome-mc/<label>/`. These ran on the in-repo predecessor of kicad-route
(`toolchain/route.py`, removed in the move), whose candidates went under `build/runs/route/fome-mc/`.

| Attempt | Result | What it showed |
|---|---|---|
| `trial-krt-initial` (1200 s) | process FAIL, exit 1 | KRT routed in minutes, then its in-run plane finalize on `+3V3`/`+5V`/`GND` ran past the budget and ignored the stop file; killed, no candidate |
| `trial-freerouting-initial` (1200 s) | INCOMPLETE 199, validation FAIL | led to two adapter fixes: the SES rebuild altered 7 existing segments (bridge now locks existing copper), and fanout micro-neckdown delivered 0.1904 mm tracks on 0.254 mm nets (fanout now off) |
| `trial-krt-nofinalize-before-locking` (`KICAD_PLANE_FINALIZE=0`) | INCOMPLETE 14, validation FAIL | KRT's rescue reworked 138 existing items despite its keep-copper flags (wrapper now locks them) |
| `trial-freerouting` (1200 s, fixed bridge) | INCOMPLETE 188 (from 235), validation FAIL | every preservation check PASS (3778 existing items locked and restored); 3 new findings: a `/LS7` track shorting a GND pad of U1102, two `/CAN2+` clearance misses (0.148 and 0.113 mm vs 0.1524); one autorouting pass in 20 min; Freerouting's own model starts with 700 clearance violations |
| `trial-krt-nofinalize` (1500 s budget, 767 s used) | INCOMPLETE 26 (from 235) on 17 nets, validation FAIL | every preservation check PASS, no existing copper removed, no conductor below its class; 18 new warnings: 14 `starved_thermal`, 2 `track_dangling`, 2 `via_dangling` |
| `trial-krt-continue` (`--dir` the candidate above, the 16 open signal nets) | 0 of 16 routed in 406 s, validation PASS | with all copper locked (including KRT's own from the step before) there is no room left for these nets |
| `trial-fr-on-krt` (same input and scope, Freerouting) | 0 of 16 (one 5 µm stub), validation PASS | same conclusion from the other backend. Its first two attempts exposed a bridge defect (scope split cut a class header at the `(` in `"Net-(BT1-+)"`, unparsable DSN; fixed) and a timeout case (session saved at the job timeout, process kept running; the adapter now grades a session reported saved before the kill) |
| `trial-krt-hardfirst` (the 16 nets first, on the original input) | 11 of 16 routed in 160 s; 2 new `starved_thermal` | routing order matters: the nets that fail last route when the board is still open |
| `trial-krt-hardfirst-rest` (`--dir` that candidate, all nets, 1086 s) | **INCOMPLETE 20 on 14 nets** (`+3V3` and `GND` among them); graded against the original input with `validate --against`: 10 new warnings (9 `starved_thermal` on GND pads of small passives on F.Cu, 1 `track_dangling` of 0.026 mm on `+3V3_WBO1`), 10 input violations resolved, every preservation check PASS | best result so far. KRT reports 18 vias at 0.599 mm where the class asks 0.5994 mm ("last-resort via-in-pad", 0.4 µm under); KiCad DRC raises nothing and `new_copper_netclass_geometry` accepts it inside its 1 µm quantisation tolerance |

No real-board candidate from the 2026-10-17 autorouter trials was adopted directly; every verdict comes from KiCad
against the board's own rules. Best autorouter trial: `trial-krt-hardfirst-rest`. Lessons from those trials:

- Open nets: continuing from `trial-krt-hardfirst-rest` with only its 12 open signal
  nets would fail the same way `trial-krt-continue` did. Route them first instead (the
  union of both open sets on the original input, then the rest), or by hand.
- Starved thermals: the new F.Cu tracks crowd thermal spokes of GND pads; a design call
  (GND stitching vias next to those pads, or keep signal tracks off F.Cu there) before
  adopting.
- The plane nets need a plan: KRT's plane finalize is the step that ran away. Try it
  alone on the KRT candidate with a longer budget, or route `GND`/`+3V3`/`+5V` taps by
  hand.
- The 2026-10-17 trial input (`e763e31`) carried 228 violations and 382 parity issues
  (footprint/library mismatches, shorting items, clearance); fixing those in the design is
  outside routing but limits every backend.
- Freerouting is not competitive on this partly routed board within 20 minutes; revisit
  after the parity and clearance findings in the input are resolved, or for a fresh
  layout.
- **Current `HEAD` Status (`FOMEMC-10..27`)**: All 235 open nets, 24 single-spoke thermals
  (`FOMEMC-11`), teardrop/track/via geometry (`FOMEMC-12`), and footprint/silkscreen/parity
  findings (`FOMEMC-16..27`) were subsequently resolved in `fome-mc.kicad_pcb` (`514`
  footprints, `0` ERC violations, `0` DRC errors, `0` DRC warnings, `0` unconnected nets,
  `0` schematic-parity mismatches with unrelaxed `fome-mc.kicad_pro` rules).
