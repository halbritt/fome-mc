# fome-mc EDA toolchain entry points. Thin wrappers over toolchain/eda.py;
# see toolchain/README.md. Every check runs on a snapshot under build/runs/.
#
#   make bootstrap | doctor | erc | drc | netlist | export | analyze | check
#   make simulate DECK=path.cir [EXPECT=path.expect.json]
#   make smoke | baseline
#   make route-doctor | route BACKEND=krt|freerouting [BUDGET=300] [ARGS='...']   (kicad-route)
#   make route-validate RUN=dir [AGAINST=dir] | route-compare RUNS='dir dir' | route-publish RUN=dir
#   make route-audit OLD=rev [NEW=HEAD] | route-update | route-smoke
#
# PROJECT=fome-mc|universal-112|fixture (see toolchain/versions.toml)
# FILL=asis|refill  (asis: use the saved zone fill; refill: refill+save the snapshot first)
# REV=<git rev>     snapshot a committed revision instead of the working tree

PROJECT ?= fome-mc
FILL    ?= asis
PY      := /usr/bin/python3
EDA     := $(PY) toolchain/eda.py
RUN     := $(EDA) run --project $(PROJECT) --fill $(FILL) $(if $(REV),--rev $(REV)) --steps

BUDGET  ?= 300
KICAD_ROUTE ?= kicad-route
ROUTE   := $(KICAD_ROUTE) --out build/route
ROUTE_OK = @command -v $(KICAD_ROUTE) >/dev/null || { echo "kicad-route is not installed: git clone \
https://github.com/halbritt/kicad-route ~/git/kicad-route && ~/git/kicad-route/scripts/install.sh"; exit 2; }

.PHONY: help bootstrap doctor erc drc netlist export analyze check renders verify-io simulate smoke baseline skills clean \
        route-doctor route route-validate route-compare route-publish route-audit route-update route-smoke

help:
	@sed -n '1,16p' Makefile

bootstrap:
	toolchain/bootstrap.sh

doctor:
	$(EDA) doctor

erc:
	$(RUN) erc

drc:
	$(RUN) drc

netlist:
	$(RUN) netlist

export:
	$(RUN) drc,netlist,export

analyze:
	$(RUN) netlist,analyze

check:
	$(RUN) erc,drc,netlist,export,analyze

renders:
	$(PY) scripts/render_docs.py

verify-io:
	$(PY) scripts/verify_io_map.py

simulate:
	@test -n "$(DECK)" || { echo "usage: make simulate DECK=path.cir [EXPECT=path.json]"; exit 2; }
	$(EDA) simulate $(DECK) $(if $(EXPECT),--expect $(EXPECT))

smoke:
	$(EDA) smoke

baseline:
	$(EDA) baseline --fill $(FILL)

skills:
	$(PY) toolchain/sync_skills.py

# Routing with kicad-route (toolchain/ROUTING.md). Attempts route copies of the board
# under build/route/runs/fome-mc/; the design is never modified.
route-doctor:
	$(ROUTE_OK)
	$(ROUTE) doctor

route:
	$(ROUTE_OK)
	@test -n "$(BACKEND)" || { echo "usage: make route BACKEND=krt|freerouting [BUDGET=s] [REV=HEAD] [ARGS='...']"; exit 2; }
	$(ROUTE) run --backend $(BACKEND) --dir . --board fome-mc.kicad_pcb --budget $(BUDGET) $(if $(REV),--rev $(REV)) $(ARGS)

route-validate:
	$(ROUTE_OK)
	@test -n "$(RUN)" || { echo "usage: make route-validate RUN=build/route/runs/fome-mc/<label>/<stamp> [AGAINST=<first run>]"; exit 2; }
	$(ROUTE) validate $(RUN) $(if $(AGAINST),--against $(AGAINST))

route-compare:
	$(ROUTE_OK)
	@test -n "$(RUNS)" || { echo "usage: make route-compare RUNS='run_dir run_dir ...'"; exit 2; }
	$(ROUTE) compare $(RUNS)

route-publish:
	$(ROUTE_OK)
	@test -n "$(RUN)" || { echo "usage: make route-publish RUN=build/route/runs/fome-mc/<label>/<stamp>"; exit 2; }
	$(ROUTE) publish $(RUN) --to reports/toolchain/routing

route-audit:
	$(ROUTE_OK)
	@test -n "$(OLD)" || { echo "usage: make route-audit OLD=<parent rev> [NEW=HEAD]"; exit 2; }
	$(ROUTE) audit --dir . --board fome-mc.kicad_pcb --old $(OLD) --new $(or $(NEW),HEAD)

route-update:
	$(ROUTE_OK)
	$(ROUTE) update

route-smoke:
	$(ROUTE_OK)
	$(ROUTE) smoke

clean:
	rm -rf build/runs build/smoke build/doctor
