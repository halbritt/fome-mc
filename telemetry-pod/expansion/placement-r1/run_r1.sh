#!/bin/bash
# placement-r1: ONE bounded placement attempt on the complete emitted pod board (agent-521 b8a43a9c v1; delivery plan rev 1).
# Host side, INSIDE one native-admit lease:
#   ~/.local/bin/native-admit run --class suite --weight 4 --label placement-r1 -- bash run_r1.sh RUN_DIR FOME_DIR
# RUN_DIR holds repo/ (git archive of fome-mc 881f6fc5) and ae/ (git archive of agent-ee 1b0637c7). Three containers of
# the qualified image d96f8e00 (tini entrypoint; --network none; no AppArmor/seccomp option given), each with the lease
# label/--cpus/--pids-limit: setup -> the declared placement stage step under `timeout 1500` -> checks. No retry.
# Attempt 1 (work/): AE_SRC unset = agent-ee 1b0637c7 (/ae/src). Attempt 1b (WORK_NAME=work-1b AE_SRC=/opt/agent-ee/src):
# the qualified image's own agent-ee 7d5b0d4d, which emitted the board (attempt 1 refused its provenance record).
# Attempt 1c (WORK_NAME=work-1c AE_SRC=/opt/agent-ee/src POLICY_OVERRIDE=/r1/repair/placement-policy.r1.json): 1b's
# fixed_conflict repaired -- the derived policy's four unsourced fixed refs C42/D3/L3/U3 lie outside the outline.
set -u
run=$(realpath -e "$1"); fome=$(realpath -e "$2"); D=$fome/telemetry-pod/expansion/placement-r1
image=sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7
w=$run/${WORK_NAME:-work}; mkdir "$w" || exit 2
base=(docker run --rm --label "native-admission.lease=$NATIVE_ADMISSION_LEASE" --cpus "$NATIVE_ADMISSION_CPUS"
      --pids-limit "$NATIVE_ADMISSION_PIDS" --network none --user "$(id -u):$(id -g)" -e HOME=/tmp
      -e PYTHONDONTWRITEBYTECODE=1 -e AGENT_EE_SKIP_VISUALS=1 -e "AE_SRC=${AE_SRC:-/ae/src}" -e "POLICY_OVERRIDE=${POLICY_OVERRIDE:-}")
stamp() { date -u +%FT%T.%NZ; }
echo "lease=$NATIVE_ADMISSION_LEASE cpus=$NATIVE_ADMISSION_CPUS start=$(stamp)"
echo "setup start $(stamp)"
"${base[@]}" --name placement-r1-setup -v "$run/repo:/repo:ro" -v "$run/ae:/ae:ro" -v "$D:/r1:ro" -v "$w:/work" -w /work \
  "$image" /usr/bin/python3 -B /r1/setup_r1.py /repo /work; rc=$?
echo "setup end $(stamp) exit=$rc"; [ "$rc" = 0 ] || exit "$rc"
# The step exactly as declared by prepare_step (argv, mounts, timeout_s), run directly in the container (no bwrap).
argv=$(python3 -c "import json,shlex,sys;s=json.load(open(sys.argv[1]));print(shlex.join(s['argv']))" "$w/step.json")
tmo=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['timeout_s'])" "$w/step.json")
echo "placement step: timeout $tmo $argv"
mkdir "$w/stepwork"
echo "placement start $(stamp)"
"${base[@]}" --name placement-r1-place -v "$w/inputs:/candidate:ro" -v "$w/step/tool:/placement-tool:ro" \
  -v "$w/step/request:/placement-request:ro" -v "$w/stepwork:/work" -w /work \
  "$image" bash -c "mkdir -p /work && exec timeout $tmo $argv" > "$w/placement.stdout.log" 2> "$w/placement.stderr.log"; rc=$?
echo "placement end $(stamp) exit=$rc"
echo "checks start $(stamp)"
[ -d "$w/stepwork/placement" ] && ln -sfn stepwork/placement "$w/placement"
"${base[@]}" --name placement-r1-checks -v "$D:/r1:ro" -v "$w:/work" -w /work "$image" /usr/bin/python3 -B /r1/checks_r1.py /work; crc=$?
echo "checks end $(stamp) exit=$crc"
exit "$rc"
