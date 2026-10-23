#!/bin/bash
# placement-r3 runner, host side INSIDE one native-admit lease (fome-mc root):
#   ~/.local/bin/native-admit run --class suite --weight 4 --label placement-r3 -- bash r3_run.sh R2_WORK OUT_WORK FOME
# Containers of the qualified image d96f8e00 (--network none, no AppArmor/seccomp option), agent-ee 7d5b0d4d = the R2
# step's tool snapshot. 1) r3_local.py  2) checks_r1.py (unchanged) on the final board  3) kicad-cli render (PNG).
set -u
r2=$(realpath -e "$1"); w=$2; fome=$(realpath -e "$3"); D=$fome/telemetry-pod/expansion/placement-r3
image=sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7
mkdir "$w" || exit 2; w=$(realpath -e "$w")
cp -a "$r2/inputs" "$w/inputs"; mkdir "$w/r2"
cp "$fome/telemetry-pod/expansion/placement-r2/run/placement-result.json" "$fome/telemetry-pod/expansion/placement-r2/run/request.json" "$w/r2/"
cp "$r2/stepwork/placement/netlist.xml" "$w/netlist.xml"
base=(docker run --rm --label "native-admission.lease=$NATIVE_ADMISSION_LEASE" --cpus "$NATIVE_ADMISSION_CPUS"
      --pids-limit "$NATIVE_ADMISSION_PIDS" --network none --user "$(id -u):$(id -g)" -e HOME=/tmp
      -e PYTHONDONTWRITEBYTECODE=1 -e AGENT_EE_SKIP_VISUALS=1 -v "$w:/work" -w /work)
stamp() { date -u +%FT%T.%NZ; }
echo "lease=$NATIVE_ADMISSION_LEASE start=$(stamp)"
"${base[@]}" --name placement-r3-local -v "$r2/step/tool:/placement-tool:ro" -v "$D:/r3:ro" -e PYTHONPATH=/placement-tool -e "RELEASE=${RELEASE:-}" \
  "$image" timeout 1200 /usr/bin/python3 -B /r3/r3_local.py /work; rc=$?
echo "r3_local end $(stamp) exit=$rc"
if [ -f "$w/final/candidate.kicad_pcb" ]; then
  cp -a "$w/inputs" "$w/before"; mkdir -p "$w/placement/placed"; cp "$w/final/candidate.kicad_pcb" "$w/placement/placed/candidate.kicad_pcb"
  "${base[@]}" --name placement-r3-checks -v "$fome/telemetry-pod/expansion/placement-r1:/r1:ro" "$image" /usr/bin/python3 -B /r1/checks_r1.py /work; echo "checks exit=$?"
  tag=$([ "$rc" = 0 ] && echo candidate || echo INCOMPLETE-candidate)
  "${base[@]}" --name placement-r3-render "$image" bash -c "kicad-cli pcb render --output /work/$tag-top.png --width 1600 --height 1200 --side top --quality basic /work/after/project/telemetry-pod.kicad_pcb > /work/render.log 2>&1; echo render-exit=\$?; kicad-cli pcb export svg --mode-single --layers F.Cu,B.Cu,F.Courtyard,B.Courtyard,Edge.Cuts,F.Fab --output /work/$tag-layers.svg /work/after/project/telemetry-pod.kicad_pcb >> /work/render.log 2>&1; echo svg-exit=\$?"
fi
echo "end $(stamp)"; exit "$rc"
