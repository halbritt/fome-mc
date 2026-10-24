#!/bin/bash
# AGENTEE-485 J2d: runs materialize-env-probe.py in the production_run.sh image with the same mounts and limits.
# Invoke inside a native-admit lease: native-admit run --class test --weight 1 -- bash probe-run.sh RUN_DIR
set -u
run=$(realpath -e "$1")
image=sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7
board=/work/fome/telemetry-pod/expansion/production-capture/diagnostics/ee485-J2c/pipe/emission/design/project/telemetry-pod.kicad_pcb
docker run --rm --label "native-admission.lease=$NATIVE_ADMISSION_LEASE" \
  --cpus "$NATIVE_ADMISSION_CPUS" --pids-limit "$NATIVE_ADMISSION_PIDS" --memory 12g --memory-swap 12g --network none \
  --security-opt seccomp=unconfined --security-opt apparmor=unconfined --security-opt systempaths=unconfined \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -e AGENT_EE_REQUIRE_TOOLCHAIN=1 -e AGENT_EE_SKIP_VISUALS=1 \
  -e AGENT_EE_GIT=/work/ae.git -e PYTHONDONTWRITEBYTECODE=1 -v "$run:/work" -w /work/fome \
  "$image" timeout 600 /usr/bin/python3 -B \
  /work/fome/telemetry-pod/expansion/production-capture/diagnostics/ee485-J2d/validation/materialize-env-probe.py \
  "$board" /work/probe-out
status=$?
printf '\nexit=%s\n' "$status"
exit "$status"
