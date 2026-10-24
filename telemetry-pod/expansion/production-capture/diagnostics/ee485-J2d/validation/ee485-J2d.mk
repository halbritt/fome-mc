# AGENTEE-485 J2d gate recipes (fome-gate.sh: MAKEFILES=telemetry-pod/expansion/production-capture/diagnostics/ee485-J2d/validation/ee485-J2d.mk).
PC = telemetry-pod/expansion/production-capture
J2D_RUN ?= build/ee485-J2d-run
j2d-tests:
	PYTHONPATH=/work/home/git/agent-ee/src python3 -B -m unittest discover -s $(PC) -p 'test_retention_snapshots.py' -v
	PYTHONPATH=/work/home/git/agent-ee/src python3 -B -m unittest discover -s $(PC) -p 'test_verify_j2.py' -v
	PYTHONPATH=/work/home/git/agent-ee/src python3 -B -m unittest discover -s $(PC) -p 'test_launch_preflight.py' -v
j2d-retain:
	python3 -B $(PC)/retain.py --check
j2d-f8:
	cd telemetry-pod/expansion/agentee-494-j2 && sha256sum -c SHA256SUMS
j2d-source-guards:
	git diff --exit-code 037fe6c274d25967cc214e22d27e939b9d628446 -- fome-mc.kicad_sch fome-mc.kicad_pcb fome-mc.kicad_pro fome-mc.kicad_dru toolchain/versions.toml sheets
	git diff --exit-code 5a1cb6f531141f22937d3b1da0b200b0af2ba247 -- $(PC)/evidence/emission-8ab3b0b9-agentee485 telemetry-pod/expansion/j2-historical-source telemetry-pod/telemetry-pod.kicad_pcb telemetry-pod/telemetry-pod.kicad_sch telemetry-pod/telemetry-pod.kicad_pro
	git diff --exit-code 037fe6c274d25967cc214e22d27e939b9d628446 -- telemetry-pod/expansion/agentee-494-j2
	git diff --exit-code 68c29ca28d5565c85f585059335175629823c960 -- $(PC)/diagnostics/ee485-J2c $(PC)/retention-repairs $(PC)/build.py $(PC)/sources $(PC)/runtime telemetry-pod/expansion/agentee-489-source
	cd $(PC)/diagnostics/ee485-J2c && sha256sum -c --quiet SHA256SUMS
j2d-verify:
	PYTHONPATH=/work/home/git/agent-ee/src timeout 300 python3 -B $(PC)/verify_j2.py $(J2D_RUN) > build/ee485-J2d-verify.json
j2d-conflicts:
	@if git grep -n -E '^(<<<<<<< |>>>>>>> |=======$$)'; then exit 2; else test $$? -eq 1; fi
