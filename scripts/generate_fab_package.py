#!/usr/bin/env python3
"""Generate and verify the committed fabrication-package manifest (FOMEMC-21).

Runs (or consumes the latest) `toolchain/eda.py` export run on `fome-mc`,
normalizes volatile creation-timestamp headers in Gerber/Excellon/job outputs to
the source git commit timestamp so re-exports at the same commit are byte-for-byte
reproducible, copies the normalized Gerber/drill/job files into `export/gerbers/`,
and writes `reports/toolchain/fab-manifest.json`.

Usage:
    python3 scripts/generate_fab_package.py [--rev HEAD] [--fill asis] [--verify]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO / "reports" / "toolchain" / "fab-manifest.json"
GERBERS_DIR = REPO / "export" / "gerbers"

# Patterns in Gerber / Excellon / drill-report / gbrjob files that carry wall-clock
# creation timestamps. Replacing them with the deterministic commit timestamp makes
# the exported fabrication files byte-for-byte reproducible for a given commit.
TIMESTAMP_PATTERNS = [
    (
        re.compile(r"^%TF\.CreationDate,[^*]+\*%", re.M),
        lambda iso_dt, space_dt: f"%TF.CreationDate,{iso_dt}*%",
    ),
    (
        re.compile(r"^(G04 Created by KiCad \([^)]+\) date )[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\*", re.M),
        lambda iso_dt, space_dt: rf"\g<1>{space_dt}*",
    ),
    (
        re.compile(r"^(; DRILL file KiCad [^\n]+ date )[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}", re.M),
        lambda iso_dt, space_dt: rf"\g<1>{iso_dt[:19]}",
    ),
    (
        re.compile(r"^(; #@! TF\.CreationDate,)[^\n]+", re.M),
        lambda iso_dt, space_dt: rf"\g<1>{iso_dt}",
    ),
    (
        re.compile(r"^(Created on )[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}", re.M),
        lambda iso_dt, space_dt: rf"\g<1>{iso_dt[:19]}",
    ),
    (
        re.compile(r'("CreationDate":\s*")"[^"]+"', re.M),
        lambda iso_dt, space_dt: f'"CreationDate": "{iso_dt}"',
    ),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


DESIGN_INPUT_PATHS = [
    "fome-mc.kicad_pcb",
    "fome-mc.kicad_pro",
    "fome-mc.kicad_sch",
    "sheets",
    "libs",
    "fp-lib-table",
    "sym-lib-table",
    "export/BOM-fome-mc.csv",
    "export/CPL-fome-mc.csv",
    "export/fome-mc.net",
]


def git_commit_info(rev: str) -> tuple[str, str, str]:
    commit = subprocess.check_output(
        ["git", "log", "-n", "1", "--format=%H", rev, "--", *DESIGN_INPUT_PATHS],
        cwd=REPO,
        text=True,
    ).strip()
    if not commit:
        commit = subprocess.check_output(
            ["git", "rev-parse", rev], cwd=REPO, text=True
        ).strip()
    ts_str = subprocess.check_output(
        ["git", "show", "-s", "--format=%ct", commit], cwd=REPO, text=True
    ).strip()
    dt = datetime.fromtimestamp(int(ts_str), tz=timezone.utc)
    iso_dt = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    space_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return commit, iso_dt, space_dt


def normalize_fab_text(text: str, iso_dt: str, space_dt: str) -> str:
    for regex, repl_fn in TIMESTAMP_PATTERNS:
        text = regex.sub(repl_fn(iso_dt, space_dt), text)
    # Also normalize `"CreationDate": "..."` in JSON gbrjob files
    text = re.sub(
        r'"CreationDate":\s*"[^"]+"',
        f'"CreationDate": "{iso_dt}"',
        text,
    )
    # Normalize volatile snapshot path and export date in kicadsexpr netlists
    text = re.sub(
        r'\(source\s+"[^"]*fome-mc\.kicad_sch"\)',
        '(source "fome-mc.kicad_sch")',
        text,
    )
    text = re.sub(
        r'\(date\s+"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[^"]*"\)',
        f'(date "{iso_dt[:19]}")',
        text,
    )
    return text


def run_export(rev: str | None, fill: str, steps: str = "drc,netlist,export") -> Path:
    cmd = [
        sys.executable,
        str(REPO / "toolchain" / "eda.py"),
        "run",
        "--project",
        "fome-mc",
        "--fill",
        fill,
        "--steps",
        steps,
    ]
    if rev:
        cmd.extend(["--rev", rev])
    subprocess.run(cmd, cwd=REPO, check=True)
    label = f"fome-mc@{rev}" if rev else "fome-mc"
    latest = REPO / "build" / "runs" / "project" / label / "latest"
    return latest.resolve()


def run_fast_verify_export(rev: str | None, fill: str) -> Path:
    """Create a fresh snapshot via toolchain/eda.py and re-export all fabrication artifacts."""
    sys.path.insert(0, str(REPO / "toolchain"))
    import eda  # type: ignore

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    label = f"fome-mc@{rev}" if rev else "fome-mc"
    run_dir = REPO / "build" / "runs" / "fab-verify" / label / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    cfg = eda.project_config("fome-mc")
    if rev:
        cfg["rev"] = rev
    snap, manifest = eda.make_snapshot(cfg, run_dir)
    sch = snap / cfg["schematic"]
    pcb = snap / cfg["pcb"]
    env = eda.tool_env()

    if fill == "refill":
        subprocess.run(
            [
                "kicad-cli",
                "pcb",
                "drc",
                "--refill-zones",
                "--save-board",
                "--format",
                "json",
                "-o",
                str(run_dir / "drc-refill.json"),
                str(pcb),
            ],
            cwd=snap,
            env=env,
            check=True,
        )

    netlist_dir = run_dir / "netlist"
    netlist_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "kicad-cli",
            "sch",
            "export",
            "netlist",
            "--format",
            "kicadsexpr",
            "-o",
            str(netlist_dir / "fome-mc.net"),
            str(sch),
        ],
        cwd=snap,
        env=env,
        check=True,
    )

    native_dir = run_dir / "export" / "native"
    native_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "kicad-cli",
            "sch",
            "export",
            "bom",
            "--fields",
            "Reference,Value,Footprint,${QUANTITY},${DNP}",
            "--labels",
            "Refs,Value,Footprint,Qty,DNP",
            "--group-by",
            "Value,Footprint",
            "--ref-range-delimiter",
            "",
            "-o",
            str(native_dir / "fome-mc-bom.csv"),
            str(sch),
        ],
        cwd=snap,
        env=env,
        check=True,
    )

    kibot_dir = run_dir / "export" / "kibot"
    kibot_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(eda.VENV / "bin" / "kibot"),
            "-c",
            str(eda.KIBOT_CONFIG),
            "-e",
            str(sch),
            "-b",
            str(pcb),
            "-d",
            str(kibot_dir),
            "gerbers",
            "drill",
            "position",
            "bom_csv",
        ],
        cwd=snap,
        env=env,
        check=True,
    )

    board_hash = sha256_file(pcb)
    (run_dir / "export" / "result.json").write_text(
        json.dumps({"board_sha256": board_hash}, indent=2) + "\n"
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "tool_versions": eda.tool_versions(),
                "steps": {},
            },
            indent=2,
        )
        + "\n"
    )
    return run_dir


def build_manifest(run_dir: Path, rev: str, fill: str, update_gerbers: bool = True) -> dict:
    commit, iso_dt, space_dt = git_commit_info(rev)
    summary = json.loads((run_dir / "summary.json").read_text())
    snap_meta = json.loads((run_dir / "snapshot.json").read_text())
    export_res = json.loads((run_dir / "export" / "result.json").read_text())

    kibot_dir = run_dir / "export" / "kibot"
    native_dir = run_dir / "export" / "native"

    if update_gerbers:
        GERBERS_DIR.mkdir(parents=True, exist_ok=True)
        for old in GERBERS_DIR.glob("*"):
            if old.is_file():
                old.unlink()

    files_manifest: dict[str, dict] = {}

    # 1. Gerber, Excellon drill, drill report, and job files
    gerber_srcs = sorted((kibot_dir / "gerbers").glob("*"))
    for src in gerber_srcs:
        if not src.is_file() or src.suffix == ".pdf":
            continue
        raw_text = src.read_text(encoding="utf-8", errors="replace")
        norm_text = normalize_fab_text(raw_text, iso_dt, space_dt)
        norm_bytes = norm_text.encode("utf-8")
        rel_key = f"export/gerbers/{src.name}"
        if update_gerbers:
            (GERBERS_DIR / src.name).write_bytes(norm_bytes)
        files_manifest[rel_key] = {
            "category": (
                "gerber_job"
                if src.suffix == ".gbrjob"
                else "drill"
                if src.suffix in (".drl", ".txt")
                else "gerber"
            ),
            "sha256": sha256_bytes(norm_bytes),
            "bytes": len(norm_bytes),
        }

    # 2. KiBot position & BOM files + native BOM & netlist
    extra_Run_files = [
        ("kibot_position_top", kibot_dir / "assembly" / "fome-mc-top_pos.csv"),
        ("kibot_position_bottom", kibot_dir / "assembly" / "fome-mc-bottom_pos.csv"),
        ("kibot_bom_csv", kibot_dir / "bom" / "fome-mc-bom.csv"),
        ("native_bom_csv", native_dir / "fome-mc-bom.csv"),
        ("native_netlist", run_dir / "netlist" / "fome-mc.net"),
    ]
    for category, path in extra_Run_files:
        if path.exists():
            raw_text = path.read_text(encoding="utf-8", errors="replace")
            norm_bytes = normalize_fab_text(raw_text, iso_dt, space_dt).encode("utf-8")
            rel_name = path.relative_to(run_dir).as_posix()
            files_manifest[rel_name] = {
                "category": category,
                "sha256": sha256_bytes(norm_bytes),
                "bytes": len(norm_bytes),
            }

    # 3. Canonical tracked JLCPCB BOM, CPL, and netlist in export/
    for category, rel_path in [
        ("jlcpcb_bom_csv", "export/BOM-fome-mc.csv"),
        ("jlcpcb_cpl_csv", "export/CPL-fome-mc.csv"),
        ("tracked_netlist", "export/fome-mc.net"),
    ]:
        p = REPO / rel_path
        if p.exists():
            data = p.read_bytes()
            files_manifest[rel_path] = {
                "category": category,
                "sha256": sha256_bytes(data),
                "bytes": len(data),
            }

    # Collect schematic and board sha256 from snapshot
    file_hashes = snap_meta.get("files", {})
    sch_hashes = {
        k: (v["sha256"] if isinstance(v, dict) else v)
        for k, v in sorted(file_hashes.items())
        if k.endswith(".kicad_sch")
    }
    board_hash = export_res.get("board_sha256") or (
        file_hashes.get("fome-mc.kicad_pcb", {}).get("sha256")
        if isinstance(file_hashes.get("fome-mc.kicad_pcb"), dict)
        else file_hashes.get("fome-mc.kicad_pcb")
    )

    manifest = {
        "schema": "fome-mc.fab-manifest/1",
        "project": "fome-mc",
        "source_commit": commit,
        "source_commit_timestamp_utc": iso_dt,
        "source_dirty_files": snap_meta.get("source_dirty_files", []),
        "fill_mode": fill,
        "board_sha256": board_hash,
        "root_schematic_sha256": sch_hashes.get("fome-mc.kicad_sch"),
        "schematic_files_sha256": sch_hashes,
        "tool_versions": summary.get("tool_versions", {}),
        "drc_status": summary.get("steps", {}).get("drc", {}).get("status"),
        "drc_design_clean": summary.get("steps", {}).get("drc", {}).get("design_clean"),
        "drc_findings": summary.get("steps", {}).get("drc", {}).get("findings"),
        "artifacts": files_manifest,
    }
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rev", help="Git revision to snapshot and export (default: working tree, records HEAD)")
    ap.add_argument("--fill", default="asis", choices=["asis", "refill"])
    ap.add_argument("--run-dir", type=Path, help="Existing run directory to consume instead of running eda.py")
    ap.add_argument("--verify", action="store_true", help="Verify existing manifest matches fresh export")
    args = ap.parse_args()

    rev_for_meta = args.rev or "HEAD"
    if args.run_dir:
        run_dir = args.run_dir.resolve()
    elif args.verify:
        run_dir = run_fast_verify_export(args.rev, args.fill)
    else:
        run_dir = run_export(args.rev, args.fill, steps="drc,netlist,export")

    if args.verify:
        if not MANIFEST_PATH.exists():
            print(f"ERROR: {MANIFEST_PATH} does not exist", file=sys.stderr)
            return 1
        recorded = json.loads(MANIFEST_PATH.read_text())
        fresh = build_manifest(run_dir, rev_for_meta, args.fill, update_gerbers=False)
        mismatches = []
        for key in (
            "source_commit",
            "source_commit_timestamp_utc",
            "fill_mode",
            "board_sha256",
            "root_schematic_sha256",
            "schematic_files_sha256",
            "tool_versions",
        ):
            if recorded.get(key) != fresh.get(key):
                mismatches.append(f"{key}: recorded={recorded.get(key)!r} != fresh={fresh.get(key)!r}")
        if fresh.get("drc_design_clean") is not None and recorded.get("drc_design_clean") != fresh.get("drc_design_clean"):
            mismatches.append(
                f"drc_design_clean: recorded={recorded.get('drc_design_clean')!r} != fresh={fresh.get('drc_design_clean')!r}"
            )
        rec_art = recorded.get("artifacts", {})
        fresh_art = fresh.get("artifacts", {})
        for k in sorted(set(rec_art) | set(fresh_art)):
            if rec_art.get(k) != fresh_art.get(k):
                mismatches.append(f"artifact {k}: recorded={rec_art.get(k)} != fresh={fresh_art.get(k)}")
            elif k.startswith("export/gerbers/"):
                disk_path = REPO / k
                if not disk_path.exists():
                    mismatches.append(f"tracked gerber {k} is missing on disk")
                elif sha256_file(disk_path) != rec_art[k]["sha256"]:
                    mismatches.append(
                        f"tracked gerber {k} on disk sha256={sha256_file(disk_path)} != manifest={rec_art[k]['sha256']}"
                    )
        if mismatches:
            print("FAIL: fab-manifest verification mismatches:", file=sys.stderr)
            for m in mismatches:
                print(f"  - {m}", file=sys.stderr)
            return 1
        print(
            f"PASS: fab-manifest verified ({len(fresh_art)} artifacts match recorded sha256 at board_sha256={fresh['board_sha256'][:12]})"
        )
        return 0

    manifest = build_manifest(run_dir, rev_for_meta, args.fill, update_gerbers=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Wrote {MANIFEST_PATH.relative_to(REPO)} and {GERBERS_DIR.relative_to(REPO)}/ "
        f"({len(manifest['artifacts'])} artifacts, board_sha256={manifest['board_sha256'][:12]})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
