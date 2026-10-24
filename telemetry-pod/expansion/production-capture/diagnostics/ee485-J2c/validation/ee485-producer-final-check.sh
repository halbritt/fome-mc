#!/usr/bin/env bash
set -euo pipefail
wt=$1
ae=$2
exec docker run --rm --network none --label native-admission.lease="$NATIVE_ADMISSION_LEASE" \
 --cpus "$NATIVE_ADMISSION_CPUS" --pids-limit "$NATIVE_ADMISSION_PIDS" --memory 12g --memory-swap 12g \
 --security-opt seccomp=unconfined --security-opt apparmor=unconfined --security-opt systempaths=unconfined \
 --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 \
 -v "$wt:/work/fome" -v "$ae:/work/export:ro" -w /work/fome \
 sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7 \
 timeout 600 /usr/bin/python3 -B telemetry-pod/expansion/production-capture/build.py /work/export --check
