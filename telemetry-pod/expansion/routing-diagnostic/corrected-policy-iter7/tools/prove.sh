#!/bin/bash
# prove.sh WORK: rebuild the corrected board from source/ and re-run every proof under WORK
# (an empty scratch directory outside the repository). Nothing in this directory is written.
#   1. build_corrected.py on the archived input -> WORK/out/ca2.kicad_pcb (compared to ../ca2.kicad_pcb)
#   2. pcbnew reload inspection of the rule areas, plus a reload+resave byte-identity check
#   3. native DRC (kicad-cli, --refill-zones in memory, on copies) of the source, the corrected board
#      and 11 fixtures; WORK/fixtures.json summarises them (summarize_fixtures.py)
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
work=$(realpath -m "$1")
[ ! -e "$work" ] || [ -z "$(ls -A "$work")" ] || { echo "WORK must be empty or absent: $work" >&2; exit 2; }
mkdir -p "$work"/{src,cor,out,fx,drc}
py() { /usr/bin/python3 "$@" 2> >(grep -v 'property.h' >&2); }

zcat "$here/source/ca2.kicad_pcb.gz" > "$work/src/ca2.kicad_pcb"
cp "$here/ca2.kicad_pro" "$here/ca2.kicad_dru" "$work/src/"
cp "$here/ca2.kicad_pcb" "$here/ca2.kicad_pro" "$here/ca2.kicad_dru" "$work/cor/"   # tools only ever open copies
(cd "$here" && grep " ./source/" SHA256SUMS | sha256sum -c --quiet -)
echo "67782a5d8ff7ce3c21dbe90b6f50c2735e4827231f3f474c9db4522de43ca73f  $work/src/ca2.kicad_pcb" | sha256sum -c --quiet -

py "$here/tools/build_corrected.py" "$work/src/ca2.kicad_pcb" "$work/out/ca2.kicad_pcb" > "$work/out/build.log"
cmp "$work/out/ca2.kicad_pcb" "$work/cor/ca2.kicad_pcb"
diff "$work/src/ca2.kicad_pcb" "$work/out/ca2.kicad_pcb" > "$work/out/source-to-corrected.diff" || true
py "$here/tools/inspect_rule_areas.py" "$work/cor/ca2.kicad_pcb" "$work/out/resaved.kicad_pcb" > "$work/rule-area-inspection.json"
cmp "$work/cor/ca2.kicad_pcb" "$work/out/resaved.kicad_pcb"

export KICAD_CONFIG_HOME="$work/kicad-config" KICAD10_SYMBOL_DIR=/usr/share/kicad/symbols \
  KICAD10_FOOTPRINT_DIR=/usr/share/kicad/footprints KICAD10_TEMPLATE_DIR=/usr/share/kicad/template
drc() {  # drc NAME BOARD: native DRC on a private copy; the copy must not change
  local d="$work/drc/$1"; mkdir -p "$d"
  cp "$2" "$d/ca2.kicad_pcb"; cp "$work/src/ca2.kicad_pro" "$work/src/ca2.kicad_dru" "$d/"
  local before; before=$(sha256sum "$d/ca2.kicad_pcb" | cut -c1-64)
  kicad-cli pcb drc --format json --severity-all --units mm --refill-zones -o "$d/drc.json" "$d/ca2.kicad_pcb" > "$d/drc.log" 2>&1
  [ "$before" = "$(sha256sum "$d/ca2.kicad_pcb" | cut -c1-64)" ] || { echo "DRC changed $d" >&2; exit 3; }
}
src="$work/src/ca2.kicad_pcb"; cor="$work/cor/ca2.kicad_pcb"; fx="$here/tools/fixture.py"
drc base-source "$src"
drc base-corrected "$cor"
py "$fx" "$cor" "$work/fx/f01.kicad_pcb" track In1.Cu 15 50 20 50
py "$fx" "$cor" "$work/fx/f02.kicad_pcb" track In1.Cu 82.5 27.2 82.5 29.4
py "$fx" "$cor" "$work/fx/f03.kicad_pcb" track In2.Cu 82.5 27.2 82.5 29.4
py "$fx" "$cor" "$work/fx/f04.kicad_pcb" via - 82.5 28.4
py "$fx" "$cor" "$work/fx/f05.kicad_pcb" via - 20 55
py "$fx" "$cor" "$work/fx/f06.kicad_pcb" track In2.Cu 15 50 20 50
py "$fx" "$src" "$work/fx/f07.kicad_pcb" track In1.Cu 15 50 20 50
py "$fx" "$src" "$work/fx/f08.kicad_pcb" via - 82.5 28.4
py "$fx" "$src" "$work/fx/f09.kicad_pcb" track In2.Cu 82.5 27.2 82.5 29.4
py "$here/tools/drop_zone.py" "$work/fx/f02.kicad_pcb" "$work/fx/f10.kicad_pcb" "D-PCB-7v2 In1.Cu no tracks (board outline)"
py "$here/tools/drop_zone.py" "$work/fx/f02.kicad_pcb" "$work/fx/f11.kicad_pcb" "D-PCB-6 RF reference keep-out"
for f in "$work"/fx/f*.kicad_pcb; do drc "$(basename "$f" .kicad_pcb)" "$f"; done
py "$here/tools/summarize_fixtures.py" "$work" > "$work/fixtures.json"
echo "prove: PASS ($work)"
