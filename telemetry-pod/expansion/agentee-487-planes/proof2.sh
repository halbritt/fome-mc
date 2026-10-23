#!/bin/bash
# AGENTEE-487 regression on the real placed R5 board: declared add-planes step, final plan (always), with a given producer mount.
set -u
run=$(realpath -e "$1"); plan=$2; tag=$3; mount=$4
docker run --rm --name agent-ee-487-planes-$tag --label "native-admission.lease=$NATIVE_ADMISSION_LEASE" \
  --cpus "$NATIVE_ADMISSION_CPUS" --pids-limit "$NATIVE_ADMISSION_PIDS" --network none \
  --security-opt seccomp=unconfined --security-opt apparmor=unconfined --security-opt systempaths=unconfined \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -e AGENT_EE_REQUIRE_TOOLCHAIN=1 -e PYTHONDONTWRITEBYTECODE=1 -e MOUNT_OVERRIDE=$mount \
  -v "$run:/work" -w /work sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7 \
  timeout 900 /usr/bin/python3 -B /work/planes_phase_proof.py /work/pipe484 /work/proof-$tag /work/proof-$tag.json /work/$plan \
  r5-placed=/work/r5.kicad_pcb
