#!/bin/bash
# The ONE j6b2 pod-preparation run (AGENTEE-207), in the AGENTEE-466 runtime image by its proximal config digest
# (c4 tag agent-ee:ci-b29cead1..., OCI index sha256:6dd73b15...), inside the native-admit lease that invokes it:
#   ~/.local/bin/native-admit run --class suite --weight 4 --label pod-capture-j6b2 -- bash production_run.sh RUN_DIR
# RUN_DIR holds fome/ (git archive of the fome-mc commit), export/ (git archive 7d5b0d4d), ae.git (a git clone of
# agent-ee holding 7d5b0d4d), source-cache/ (empty) and iter8n/ (the verified iter8n cache copy). No retry.
set -u
run=$(realpath -e "$1")
image=sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7
# AppArmor: always unconfined (owner ruling "remove the apparmor profiles like I asked"; AGENTEE-475). No profile is
# selected, loaded or tested, whatever the host AppArmor state.
# The image ENTRYPOINT is tini, so --init is omitted.
docker run --rm --name agent-ee-pod-capture-j6b2-prepare --label "native-admission.lease=$NATIVE_ADMISSION_LEASE" \
  --cpus "$NATIVE_ADMISSION_CPUS" --pids-limit "$NATIVE_ADMISSION_PIDS" --network none \
  --security-opt seccomp=unconfined --security-opt apparmor=unconfined --security-opt systempaths=unconfined \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -e AGENT_EE_REQUIRE_TOOLCHAIN=1 -e AGENT_EE_SKIP_VISUALS=1 \
  -e AGENT_EE_GIT=/work/ae.git -e AGENT_EE_TOOL_SOURCE_CACHE=/work/source-cache -e PYTHONDONTWRITEBYTECODE=1 \
  -e POD_BUILD_OPTIN="${POD_BUILD_OPTIN:-}" -e POD_RUNTIME="${POD_RUNTIME:-runtime/agentee-484r2.json}" \
  -v "$run:/work" -v "$run/iter8n:/home/halbritt/.cache/agent449-pod/iter8n:ro" -w /work/fome \
  "$image" timeout 5400 /usr/bin/python3 -B /work/fome/telemetry-pod/expansion/production-capture/production_steps.py
status=$?
printf '\nexit=%s\n' "$status"
exit "$status"
