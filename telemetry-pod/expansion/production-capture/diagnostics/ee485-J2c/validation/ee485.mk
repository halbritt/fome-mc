ee485-repair:
	python3 telemetry-pod/expansion/production-capture/retain.py --repair-repository-snapshots
ee485-retain:
	python3 telemetry-pod/expansion/production-capture/retain.py --check
ee485-f8:
	cd telemetry-pod/expansion/agentee-494-j2 && sha256sum -c SHA256SUMS
ee485-tests:
	PYTHONPATH=/work/home/git/agent-ee/src python3 -B -m unittest discover -s telemetry-pod/expansion/production-capture -p 'test_retention_snapshots.py' -v
	PYTHONPATH=/work/home/git/agent-ee/src python3 -B -m unittest discover -s telemetry-pod/expansion/production-capture -p 'test_verify_j2.py' -v
	PYTHONPATH=/work/home/git/agent-ee/src python3 -B -m unittest discover -s telemetry-pod/expansion/production-capture -p 'test_launch_preflight.py' -v
ee485-materialize:
	python3 telemetry-pod/expansion/production-capture/retain.py --materialize-prepared build/ee485-history-prepared
ee485-repair-sums:
	cd telemetry-pod/expansion/production-capture/retention-repairs/emission-8ab3b0b9-agentee485 && sha256sum RECOVERY.json blobs/* > SHA256SUMS
	cd telemetry-pod/expansion/production-capture/retention-repairs/emission-8ab3b0b9-agentee485 && sha256sum -c SHA256SUMS > /work/fome-mc/build/ee485-repair-sums-check.log
ee485-native:
	timeout 450 python3 -B build/ee485-native.py
ee485-verify:
	PYTHONPATH=/work/home/git/agent-ee/src timeout 180 python3 -B telemetry-pod/expansion/production-capture/verify_j2.py build/ee485-J2c-run > build/ee485-J2c-verify.json
ee485-retention-final-tests:
	python3 -B -m unittest discover -s telemetry-pod/expansion/production-capture -p 'test_retention_snapshots.py' -v
ee485-source-guards:
	git diff --exit-code 037fe6c274d25967cc214e22d27e939b9d628446 -- fome-mc.kicad_sch fome-mc.kicad_pcb fome-mc.kicad_pro fome-mc.kicad_dru toolchain/versions.toml
	git diff --exit-code 5a1cb6f531141f22937d3b1da0b200b0af2ba247 -- telemetry-pod/expansion/production-capture/evidence/emission-8ab3b0b9-agentee485 telemetry-pod/expansion/j2-historical-source telemetry-pod/telemetry-pod.kicad_pcb telemetry-pod/telemetry-pod.kicad_sch telemetry-pod/telemetry-pod.kicad_pro
	git diff --exit-code 037fe6c274d25967cc214e22d27e939b9d628446 -- telemetry-pod/expansion/agentee-494-j2/SHA256SUMS telemetry-pod/expansion/agentee-494-j2/board-side-correction.json
	git diff --check -- . ':(exclude)**/sources-*/*' ':(exclude)telemetry-pod/expansion/production-capture/retention-repairs/*/blobs/*'
	git diff --cached --check -- . ':(exclude)**/sources-*/*' ':(exclude)telemetry-pod/expansion/production-capture/retention-repairs/*/blobs/*'
ee485-compare-ecu:
	python3 -B build/ee485-compare-ecu.py
ee485-conflicts:
	@if git grep -n -E '^(<<<<<<< |>>>>>>> |=======$$)'; then exit 2; else test $$? -eq 1; fi
ee485-inventory-controls:
	PYTHONPATH=/work/home/git/agent-ee/src python3 -B telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/validation/inventory-negative-controls.py
ee485-packet:
	cd telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c && sha256sum -c SHA256SUMS > /work/fome-mc/build/ee485-packet-sums.log
	git diff --cached --check -- . ':(exclude)**/sources-*/*' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/cap/**' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/pipe/emission/design/**' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/logs/**'
ee485-final-input-guards:
	git diff --exit-code 037fe6c274d25967cc214e22d27e939b9d628446 -- fome-mc.kicad_sch fome-mc.kicad_pcb fome-mc.kicad_pro fome-mc.kicad_dru toolchain/versions.toml sheets
	git diff --exit-code 5a1cb6f531141f22937d3b1da0b200b0af2ba247 -- telemetry-pod/expansion/production-capture/evidence/emission-8ab3b0b9-agentee485 telemetry-pod/expansion/j2-historical-source telemetry-pod/telemetry-pod.kicad_pcb telemetry-pod/telemetry-pod.kicad_sch telemetry-pod/telemetry-pod.kicad_pro
	git diff --exit-code 037fe6c274d25967cc214e22d27e939b9d628446 -- telemetry-pod/expansion/agentee-494-j2/SHA256SUMS telemetry-pod/expansion/agentee-494-j2/board-side-correction.json
	git diff --check -- . ':(exclude)**/sources-*/*' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/cap/**' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/pipe/emission/design/**' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/logs/**'
	git diff --cached --check -- . ':(exclude)**/sources-*/*' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/cap/**' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/pipe/emission/design/**' ':(exclude)telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/logs/**'
