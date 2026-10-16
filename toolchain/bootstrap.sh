#!/usr/bin/env bash
# Reproduce or repair the fome-mc EDA toolchain. Idempotent; safe to re-run.
#
#   toolchain/bootstrap.sh            install/repair everything, then run doctor
#   toolchain/bootstrap.sh --no-apt   skip system packages (no sudo needed)
#
# Pins live in toolchain/versions.toml (system packages, upstream commits) and
# toolchain/uv.lock (Python packages). System Python is never modified: Python
# tools live in toolchain/.venv, which sees only KiCad's own pcbnew + wx bindings
# from the system through a narrow shim directory.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$HERE")"
VENV="$HERE/.venv"
SYS_PY=/usr/bin/python3
NO_APT=0
[ "${1:-}" = "--no-apt" ] && NO_APT=1

pin() {  # pin <toml.dotted.key>
  "$SYS_PY" -c 'import sys,tomllib; d=tomllib.load(open(sys.argv[1],"rb"))
for k in sys.argv[2].split("."): d=d[k]
print(d if not isinstance(d,list) else " ".join(d))' "$HERE/versions.toml" "$1"
}

echo "== system packages"
if [ "$NO_APT" -eq 0 ]; then
  if ! grep -rqs "kicad/kicad-10.0-releases" /etc/apt/sources.list /etc/apt/sources.list.d/; then
    echo "adding ppa:kicad/kicad-10.0-releases"
    sudo add-apt-repository -y ppa:kicad/kicad-10.0-releases
    sudo apt-get update
  fi
  pkgs=$("$SYS_PY" -c 'import tomllib; d=tomllib.load(open("'"$HERE"'/versions.toml","rb"))["apt"]
print(" ".join(f"{k}={v}" for k,v in d.items()))')
  missing=""
  for kv in $pkgs; do
    name="${kv%%=*}"; want="${kv#*=}"
    have=$(dpkg-query -W -f='${Version}' "$name" 2>/dev/null || true)
    [ "$have" = "$want" ] || missing="$missing $kv"
  done
  if [ -n "$missing" ]; then
    echo "installing:$missing"
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends $missing
  else
    echo "all pinned system packages present"
  fi
else
  echo "skipped (--no-apt)"
fi

echo "== python environment ($VENV)"
command -v uv >/dev/null || { echo "uv is required (https://docs.astral.sh/uv/)"; exit 1; }
(cd "$HERE" && UV_PROJECT_ENVIRONMENT="$VENV" uv sync --frozen --python "$SYS_PY")
SITE=$("$VENV/bin/python" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
SHIM="$VENV/kicad-shim"
mkdir -p "$SHIM"
for item in pcbnew.py _pcbnew.so wx; do
  [ -e "/usr/lib/python3/dist-packages/$item" ] || { echo "missing system $item (is kicad installed?)"; exit 1; }
  ln -sfn "/usr/lib/python3/dist-packages/$item" "$SHIM/$item"
done
echo "$SHIM" > "$SITE/kicad_pcbnew_shim.pth"

echo "== kicad-happy (pinned)"
KH="$HERE/vendor/kicad-happy"
KH_URL=$(pin upstream.kicad-happy.url)
KH_COMMIT=$(pin upstream.kicad-happy.commit)
if [ ! -d "$KH/.git" ]; then
  mkdir -p "$HERE/vendor"
  git clone --quiet "$KH_URL" "$KH"
fi
if [ "$(git -C "$KH" rev-parse HEAD)" != "$KH_COMMIT" ]; then
  git -C "$KH" fetch --quiet --tags origin
  git -C "$KH" -c advice.detachedHead=false checkout --quiet "$KH_COMMIT"
fi
echo "kicad-happy @ $(git -C "$KH" rev-parse HEAD)"

echo "== agent skills"
"$SYS_PY" "$HERE/sync_skills.py"

echo "== doctor"
"$SYS_PY" "$HERE/eda.py" doctor
