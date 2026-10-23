#!/bin/bash
# AGENTEE-484 regeneration: the production_run.sh invocation with apparmor=unconfined (AGENTEE-475 rule) instead of
# its host-dependent profile selection. Same image, mounts, env, network none, and production_steps.py.
set -u
run=$(realpath -e "$1")
image=sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7
docker run --rm --name agent-ee-pod-capture-484 --label "native-admission.lease=$NATIVE_ADMISSION_LEASE" \
  --cpus "$NATIVE_ADMISSION_CPUS" --pids-limit "$NATIVE_ADMISSION_PIDS" --network none \
  --security-opt seccomp=unconfined --security-opt apparmor=unconfined --security-opt systempaths=unconfined \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -e AGENT_EE_REQUIRE_TOOLCHAIN=1 -e AGENT_EE_SKIP_VISUALS=1 \
  -e AGENT_EE_GIT=/work/ae.git -e AGENT_EE_TOOL_SOURCE_CACHE=/work/source-cache -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$run:/work" -v "$run/iter8n:/home/halbritt/.cache/agent449-pod/iter8n:ro" -w /work/fome \
  "$image" timeout 2400 /usr/bin/python3 -B /work/fome/telemetry-pod/expansion/production-capture/production_steps.py
status=$?
printf '\nexit=%s\n' "$status"
exit "$status"
