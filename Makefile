# fome-mc EDA toolchain entry points. Thin wrappers over toolchain/eda.py;
# see toolchain/README.md. Every check runs on a snapshot under build/runs/.
#
#   make bootstrap | doctor | erc | drc | netlist | export | analyze | check
#   make renders | verify-io | fab-package [REV=HEAD] | verify-fab-package [REV=HEAD]
#   make simulate DECK=path.cir [EXPECT=path.expect.json]
#   make smoke | baseline
#   make route-doctor | route BACKEND=krt|freerouting [BUDGET=300] [ARGS='...']   (kicad-route)
#   make route-campaign BACKEND=krt|freerouting [BUDGET=300] [ROUNDS=2] [RACE=0] [TOTAL_BUDGET=s] [ARGS='...']
#   make route-validate RUN=dir [AGAINST=dir] [ARGS='...'] | route-compare RUNS='dir dir' | route-publish RUN=dir
#   make route-blocked RUN=dir [TOP=10] | route-spokes RUN=dir [VALIDATION=dir] | route-spokes BOARD=file [PER_PAD=n]
#   make route-audit OLD=rev [NEW=HEAD] | route-floor [SINCE=rev] [WRITE=1] [NETCLASS_SIZES=1]
#   make route-canary [BACKEND=all] | route-corpus-list | route-corpus-check [NAME=entry]
#   make route-corpus-add BACKEND=krt|freerouting [NAME=<PROJECT>] [BUDGET=300] [ARGS='...'] | route-update | route-smoke
#
# PROJECT=fome-mc|telemetry-pod|universal-112|fixture (see toolchain/versions.toml; route targets take
#         its dir, board, schematic and library_dirs from there)
# FILL=asis|refill  (asis: use the saved zone fill; refill: refill+save the snapshot first)
# REV=<git rev>     snapshot a committed revision instead of the working tree

PROJECT ?= fome-mc
FILL    ?= asis
PY      := /usr/bin/python3
EDA     := $(PY) toolchain/eda.py
EDA_RUN := $(EDA) run --project $(PROJECT) --fill $(FILL) $(if $(REV),--rev $(REV)) --steps

BUDGET  ?= 300
KICAD_ROUTE ?= kicad-route
ROUTE   := $(KICAD_ROUTE) --out build/route
ROUTE_OK = @command -v $(KICAD_ROUTE) >/dev/null || { echo "kicad-route is not installed: git clone \
https://github.com/halbritt/kicad-route ~/git/kicad-route && ~/git/kicad-route/scripts/install.sh"; exit 2; }
# kicad-route input options for PROJECT, from toolchain/versions.toml: --dir, --board,
# --schematic, --name (run directories go under build/route/runs/$(PROJECT)/) and one
# --library-dir per library_dirs entry ("fome" is $FOME_KICAD_LIBS or [libraries.fome],
# as in eda.py). Resolved once, on first use, so non-routing targets never pay for it.
ROUTE_PROJ_PY := import os, shlex, sys, tomllib; \
  t = tomllib.load(open('toolchain/versions.toml', 'rb')); n = sys.argv[1]; \
  c = t['projects'].get(n) or sys.exit('PROJECT=' + n + ' is not in toolchain/versions.toml; known: ' + ' '.join(t['projects'])); \
  lib = lambda v: os.environ.get('FOME_KICAD_LIBS', t['libraries']['fome']['path']) if v == 'fome' else v; \
  a = ['--dir', os.path.expanduser(c['dir']), '--board', c['pcb'], '--schematic', c['schematic'], '--name', n]; \
  [a.extend(['--library-dir', k + '=' + os.path.expanduser(lib(v))]) for k, v in c.get('library_dirs', {}).items()]; \
  print(shlex.join(a))
ROUTE_PROJ = $(eval ROUTE_PROJ := $(shell $(PY) -c "$(ROUTE_PROJ_PY)" '$(PROJECT)'))$(ROUTE_PROJ)
ROUTE_PROJ_OK = $(if $(ROUTE_PROJ),@true,@echo "no routable board for PROJECT=$(PROJECT)" >&2; exit 2)
RUNS_DIR = build/route/runs/$(PROJECT)

.PHONY: help bootstrap doctor erc drc netlist export analyze check renders verify-io fab-package verify-fab-package simulate smoke baseline skills clean \
        route-doctor route route-campaign route-validate route-compare route-publish route-blocked route-spokes \
        route-audit route-floor route-canary route-corpus-list route-corpus-check route-corpus-add \
        route-update route-smoke

help:
	@sed -n '/^#/!q;p' Makefile

bootstrap:
	toolchain/bootstrap.sh

doctor:
	$(EDA) doctor

erc:
	$(EDA_RUN) erc

drc:
	$(EDA_RUN) drc

netlist:
	$(EDA_RUN) netlist

export:
	$(EDA_RUN) drc,netlist,export

analyze:
	$(EDA_RUN) netlist,analyze

check:
	$(EDA_RUN) erc,drc,netlist,export,analyze

renders:
	$(PY) scripts/render_docs.py

verify-io:
	$(PY) scripts/verify_io_map.py$(if $(filter-out fome-mc,$(PROJECT)), --project $(PROJECT))

fab-package:
	$(PY) scripts/generate_fab_package.py --project $(PROJECT) --fill $(FILL) $(if $(REV),--rev $(REV))

verify-fab-package:
	$(PY) scripts/generate_fab_package.py --project $(PROJECT) --fill $(FILL) $(if $(REV),--rev $(REV)) --verify

simulate:
	@test -n "$(DECK)" || { echo "usage: make simulate DECK=path.cir [EXPECT=path.json]"; exit 2; }
	$(EDA) simulate $(DECK) $(if $(EXPECT),--expect $(EXPECT))

smoke:
	$(EDA) smoke

baseline:
	$(EDA) baseline --fill $(FILL)

skills:
	$(PY) toolchain/sync_skills.py

# Routing with kicad-route (toolchain/ROUTING.md). Attempts route copies of PROJECT's
# board under build/route/runs/$(PROJECT)/; the design is never modified.
route-doctor:
	$(ROUTE_OK)
	$(ROUTE) doctor

route:
	$(ROUTE_OK)
	@test -n "$(BACKEND)" || { echo "usage: make route BACKEND=krt|freerouting [BUDGET=s] [REV=HEAD] [ARGS='...']"; exit 2; }
	$(ROUTE_PROJ_OK)
	$(ROUTE) run --backend $(BACKEND) $(ROUTE_PROJ) --budget $(BUDGET) $(if $(REV),--rev $(REV)) $(ARGS)

# Hard-nets-first campaign: several runs, the best chain graded against the original input.
route-campaign:
	$(ROUTE_OK)
	@test -n "$(BACKEND)" || { echo "usage: make route-campaign BACKEND=krt|freerouting [BUDGET=s per run] [REV=HEAD] [ROUNDS=2] [RACE=0] [TOTAL_BUDGET=s] [ARGS='...']"; exit 2; }
	$(ROUTE_PROJ_OK)
	$(ROUTE) campaign --backend $(BACKEND) $(ROUTE_PROJ) --budget $(BUDGET) $(if $(REV),--rev $(REV)) \
	  $(if $(ROUNDS),--rounds $(ROUNDS)) $(if $(RACE),--race $(RACE)) $(if $(TOTAL_BUDGET),--total-budget $(TOTAL_BUDGET)) $(ARGS)

route-validate:
	$(ROUTE_OK)
	@test -n "$(RUN)" || { echo "usage: make route-validate RUN=$(RUNS_DIR)/<label>/<stamp> [AGAINST=<first run>] [ARGS='--pour-area-loss PCT ...']"; exit 2; }
	$(ROUTE) validate $(RUN) $(if $(AGAINST),--against $(AGAINST)) $(ARGS)

route-compare:
	$(ROUTE_OK)
	@test -n "$(RUNS)" || { echo "usage: make route-compare RUNS='run_dir run_dir ...'"; exit 2; }
	$(ROUTE) compare $(RUNS)

route-publish:
	$(ROUTE_OK)
	@test -n "$(RUN)" || { echo "usage: make route-publish RUN=$(RUNS_DIR)/<label>/<stamp>"; exit 2; }
	$(ROUTE) publish $(RUN) --to reports/toolchain/routing

# Which obstacles lie across the connections an incomplete run left open.
route-blocked:
	$(ROUTE_OK)
	@test -n "$(RUN)" || { echo "usage: make route-blocked RUN=$(RUNS_DIR)/<label>/<stamp> [TOP=10]"; exit 2; }
	$(ROUTE) blocked $(RUN) $(if $(TOP),--top $(TOP))

# Thermal spokes: RUN= attributes starved pads to new copper; BOARD= plans corridors for a
# board file (it is read, not saved; prefer a run's reference/ copy over the live design).
route-spokes:
	$(ROUTE_OK)
	@test -n "$(RUN)$(BOARD)" || { echo "usage: make route-spokes RUN=$(RUNS_DIR)/<label>/<stamp> [VALIDATION=dir] | BOARD=<file.kicad_pcb> [PER_PAD=n]"; exit 2; }
	$(ROUTE) spokes $(if $(BOARD),--board $(BOARD) $(if $(PER_PAD),--per-pad $(PER_PAD)),$(RUN) $(if $(VALIDATION),--validation $(VALIDATION)))

route-audit:
	$(ROUTE_OK)
	@test -n "$(OLD)" || { echo "usage: make route-audit OLD=<parent rev> [NEW=HEAD]"; exit 2; }
	$(ROUTE_PROJ_OK)
	$(ROUTE) audit $(ROUTE_PROJ) --old $(OLD) --new $(or $(NEW),HEAD)

# Rule high-water mark of the board's git history and its declared floor (read-only;
# WRITE=1 drafts <board>.rules-floor.json under build/route for review).
route-floor:
	$(ROUTE_OK)
	$(ROUTE_PROJ_OK)
	$(ROUTE) floor $(ROUTE_PROJ) $(if $(SINCE),--since $(SINCE)) $(if $(WRITE),--write-declared) $(if $(NETCLASS_SIZES),--netclass-sizes)

# Awkward-net-name round trip through each backend (on kicad-route's fixture, not this board).
route-canary:
	$(ROUTE_OK)
	$(ROUTE) canary --backend $(or $(BACKEND),all)

# Real-board regression corpus, kept in kicad-route's state (STATE/corpus or
# $KICAD_ROUTE_CORPUS); `kicad-route update` runs the check.
route-corpus-list:
	$(ROUTE_OK)
	$(ROUTE) corpus list

route-corpus-check:
	$(ROUTE_OK)
	$(ROUTE) corpus check $(if $(NAME),--name $(NAME))

route-corpus-add:
	$(ROUTE_OK)
	@test -n "$(BACKEND)" || { echo "usage: make route-corpus-add BACKEND=krt|freerouting [NAME=$(PROJECT)] [BUDGET=s] [REV=HEAD] [ARGS='...']"; exit 2; }
	$(ROUTE_PROJ_OK)
	$(ROUTE) corpus add --backend $(BACKEND) $(ROUTE_PROJ) $(if $(NAME),--name $(NAME)) --budget $(BUDGET) $(if $(REV),--rev $(REV)) $(ARGS)

route-update:
	$(ROUTE_OK)
	$(ROUTE) update

route-smoke:
	$(ROUTE_OK)
	$(ROUTE) smoke

clean:
	rm -rf build/runs build/smoke build/doctor
