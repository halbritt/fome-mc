# fome-mc EDA toolchain entry points. Thin wrappers over toolchain/eda.py;
# see toolchain/README.md. Every check runs on a snapshot under build/runs/.
#
#   make bootstrap | doctor | erc | drc | netlist | export | analyze | check
#   make simulate DECK=path.cir [EXPECT=path.expect.json]
#   make smoke | baseline
#   make route-doctor | route BACKEND=krt|freerouting [BUDGET=300] [ARGS='...']
#   make route-validate RUN=dir | route-compare RUNS='dir dir' | route-update | route-smoke
#
# PROJECT=fome-mc|universal-112|fixture|route-fixture (see toolchain/versions.toml)
# FILL=asis|refill  (asis: use the saved zone fill; refill: refill+save the snapshot first)
# REV=<git rev>     snapshot a committed revision instead of the working tree

PROJECT ?= fome-mc
FILL    ?= asis
PY      := /usr/bin/python3
EDA     := $(PY) toolchain/eda.py
RUN     := $(EDA) run --project $(PROJECT) --fill $(FILL) $(if $(REV),--rev $(REV)) --steps

BUDGET  ?= 300
ROUTE   := $(PY) toolchain/route.py

.PHONY: help bootstrap doctor erc drc netlist export analyze check renders verify-io simulate smoke baseline skills clean \
        route-doctor route route-validate route-compare route-update route-smoke

help:
	@sed -n '1,15p' Makefile

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

# Routing (toolchain/ROUTING.md). Attempts run on copies under build/runs/route/.
route-doctor:
	$(ROUTE) doctor

route:
	@test -n "$(BACKEND)" || { echo "usage: make route BACKEND=krt|freerouting [PROJECT=..] [BUDGET=s] [ARGS='...']"; exit 2; }
	$(ROUTE) run --backend $(BACKEND) --project $(PROJECT) --budget $(BUDGET) $(if $(REV),--rev $(REV)) $(ARGS)

route-validate:
	@test -n "$(RUN)" || { echo "usage: make route-validate RUN=build/runs/route/<project>/<label>/<stamp>"; exit 2; }
	$(ROUTE) validate $(RUN)

route-compare:
	@test -n "$(RUNS)" || { echo "usage: make route-compare RUNS='run_dir run_dir ...'"; exit 2; }
	$(ROUTE) compare $(RUNS)

route-update:
	$(ROUTE) update

route-smoke:
	$(ROUTE) smoke

clean:
	rm -rf build/runs build/smoke build/doctor
