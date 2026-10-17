# fome-mc EDA toolchain entry points. Thin wrappers over toolchain/eda.py;
# see toolchain/README.md. Every check runs on a snapshot under build/runs/.
#
#   make bootstrap | doctor | erc | drc | netlist | export | analyze | check
#   make simulate DECK=path.cir [EXPECT=path.expect.json]
#   make smoke | baseline
#
# PROJECT=fome-mc|universal-112|fixture (see toolchain/versions.toml)
# FILL=asis|refill  (asis: use the saved zone fill; refill: refill+save the snapshot first)
# REV=<git rev>     snapshot a committed revision instead of the working tree

PROJECT ?= fome-mc
FILL    ?= asis
PY      := /usr/bin/python3
EDA     := $(PY) toolchain/eda.py
RUN     := $(EDA) run --project $(PROJECT) --fill $(FILL) $(if $(REV),--rev $(REV)) --steps

.PHONY: help bootstrap doctor erc drc netlist export analyze check renders verify-io simulate smoke baseline skills clean

help:
	@sed -n '1,12p' Makefile

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

clean:
	rm -rf build/runs build/smoke build/doctor
