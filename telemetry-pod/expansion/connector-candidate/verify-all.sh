#!/usr/bin/env bash
set -euo pipefail
connector_root="$(cd "$(dirname "$0")" && pwd)"
connector_temp="$(mktemp -d -t pod-connector-check-XXXXXXXX)"
trap 'rm -rf "$connector_temp"' EXIT
/usr/bin/python3 "$connector_root/verify.py" --out "$connector_temp/native"
uv run --no-project --python 3.12 --with cadquery==2.8.0 python "$connector_root/check_model.py" "$connector_temp/native/connector.step"
