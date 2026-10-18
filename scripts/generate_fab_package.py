#!/usr/bin/env python3
"""Generate and verify the committed fabrication-package manifest (FOMEMC-21).

Runs (or consumes the latest) `toolchain/eda.py` export run on the selected project,
normalizes volatile creation-timestamp headers in Gerber/Excellon/job outputs to
the source git commit timestamp so re-exports at the same commit are byte-for-byte
reproducible, copies the normalized Gerber/drill/job files into the project's `export/gerbers/`,
and writes its `reports/toolchain/fab-manifest.json`.

Usage:
    python3 scripts/generate_fab_package.py [--project fome-mc] [--rev HEAD] [--fill asis] [--verify]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).resolve().parent, text=True
).strip())


@dataclass(frozen=True)
class Project:
    name: str
    directory: Path
    schematic: str
    pcb: str

    @property
    def stem(self) -> str:
        return Path(self.schematic).stem

    @property
    def manifest_path(self) -> Path:
        return self.directory / "reports" / "toolchain" / "fab-manifest.json"

    @property
    def gerbers_dir(self) -> Path:
        return self.directory / "export" / "gerbers"

    def relative(self, path: str) -> str:
        return (self.directory / path).relative_to(REPO).as_posix()


def project_config(name: str) -> Project:
    with (REPO / "toolchain" / "versions.toml").open("rb") as stream:
        projects = tomllib.load(stream)["projects"]
    if name not in projects:
        raise ValueError(f"unknown project {name!r}; known: {', '.join(projects)}")
    cfg = projects[name]
    directory = (REPO / Path(cfg["dir"]).expanduser()).resolve()
    if not directory.is_relative_to(REPO):
        raise ValueError(f"fab-package project {name!r} must be inside this repository")
    return Project(name, directory, cfg["schematic"], cfg["pcb"])

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


def design_input_paths(project: Project) -> list[str]:
    return [project.relative(path) for path in (
        project.pcb, str(Path(project.pcb).with_suffix(".kicad_pro")), project.schematic,
        "sheets", "libs", "fp-lib-table", "sym-lib-table",
        f"export/BOM-{project.stem}.csv", f"export/CPL-{project.stem}.csv",
        f"export/{project.stem}.net",
    )]


def git_commit_info(rev: str, project: Project) -> tuple[str, str, str]:
    commit = subprocess.check_output(
        ["git", "log", "-n", "1", "--format=%H", rev, "--", *design_input_paths(project)],
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


def normalize_fab_text(text: str, iso_dt: str, space_dt: str, project: Project) -> str:
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
        rf'\(source\s+"[^"]*{re.escape(project.schematic)}"\)',
        lambda _: f'(source "{project.schematic}")',
        text,
    )
    text = re.sub(
        r'\(date\s+"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[^"]*"\)',
        f'(date "{iso_dt[:19]}")',
        text,
    )
    return text


def run_export(rev: str | None, fill: str, project: Project) -> Path:
    cmd = [
        sys.executable,
        str(REPO / "toolchain" / "eda.py"),
        "run",
        "--project",
        project.name,
        "--fill",
        fill,
        "--steps",
        "drc,netlist,export",
    ]
    if rev:
        cmd.extend(["--rev", rev])
    subprocess.run(cmd, cwd=REPO, check=True)
    label = f"{project.name}@{rev}" if rev else project.name
    latest = REPO / "build" / "runs" / "project" / label / "latest"
    return latest.resolve()


def run_fast_verify_export(rev: str | None, fill: str, project: Project) -> Path:
    """Create a fresh snapshot via toolchain/eda.py and re-export all fabrication artifacts."""
    sys.path.insert(0, str(REPO / "toolchain"))
    import eda  # type: ignore

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    label = f"{project.name}@{rev}" if rev else project.name
    run_dir = REPO / "build" / "runs" / "fab-verify" / label / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    cfg = eda.project_config(project.name)
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
            str(netlist_dir / f"{project.stem}.net"),
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
            str(native_dir / f"{project.stem}-bom.csv"),
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
            "-A",
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


def build_manifest(run_dir: Path, rev: str, fill: str, project: Project, *, update_gerbers: bool = True) -> dict:
    commit, iso_dt, space_dt = git_commit_info(rev, project)
    summary = json.loads((run_dir / "summary.json").read_text())
    snap_meta = json.loads((run_dir / "snapshot.json").read_text())
    export_res = json.loads((run_dir / "export" / "result.json").read_text())
    if snap_meta.get("project") != project.name:
        raise ValueError(f"run directory is not for project {project.name!r}")

    kibot_dir = run_dir / "export" / "kibot"
    native_dir = run_dir / "export" / "native"

    if update_gerbers:
        project.gerbers_dir.mkdir(parents=True, exist_ok=True)
        for old in project.gerbers_dir.glob("*"):
            if old.is_file():
                old.unlink()

    files_manifest: dict[str, dict] = {}

    # 1. Gerber, Excellon drill, drill report, and job files
    gerber_srcs = sorted((kibot_dir / "gerbers").glob("*"))
    for src in gerber_srcs:
        if not src.is_file() or src.suffix == ".pdf":
            continue
        raw_text = src.read_text(encoding="utf-8", errors="replace")
        norm_text = normalize_fab_text(raw_text, iso_dt, space_dt, project)
        norm_bytes = norm_text.encode("utf-8")
        rel_key = project.relative(f"export/gerbers/{src.name}")
        if update_gerbers:
            (project.gerbers_dir / src.name).write_bytes(norm_bytes)
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
        ("kibot_position_top", kibot_dir / "assembly" / f"{Path(project.pcb).stem}-top_pos.csv"),
        ("kibot_position_bottom", kibot_dir / "assembly" / f"{Path(project.pcb).stem}-bottom_pos.csv"),
        ("kibot_bom_csv", kibot_dir / "bom" / f"{project.stem}-bom.csv"),
        ("native_bom_csv", native_dir / f"{project.stem}-bom.csv"),
        ("native_netlist", run_dir / "netlist" / f"{project.stem}.net"),
    ]
    for category, path in extra_Run_files:
        if path.exists():
            raw_text = path.read_text(encoding="utf-8", errors="replace")
            norm_bytes = normalize_fab_text(raw_text, iso_dt, space_dt, project).encode("utf-8")
            rel_name = path.relative_to(run_dir).as_posix()
            files_manifest[rel_name] = {
                "category": category,
                "sha256": sha256_bytes(norm_bytes),
                "bytes": len(norm_bytes),
            }

    # 3. Canonical tracked JLCPCB BOM, CPL, and netlist in export/
    for category, rel_path in [
        ("jlcpcb_bom_csv", project.relative(f"export/BOM-{project.stem}.csv")),
        ("jlcpcb_cpl_csv", project.relative(f"export/CPL-{project.stem}.csv")),
        ("tracked_netlist", project.relative(f"export/{project.stem}.net")),
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
        file_hashes.get(project.pcb, {}).get("sha256")
        if isinstance(file_hashes.get(project.pcb), dict)
        else file_hashes.get(project.pcb)
    )

    manifest = {
        "schema": "fome-mc.fab-manifest/1",
        "project": project.name,
        "source_commit": commit,
        "source_commit_timestamp_utc": iso_dt,
        "source_dirty_files": snap_meta.get("source_dirty_files", []),
        "fill_mode": fill,
        "board_sha256": board_hash,
        "root_schematic_sha256": sch_hashes.get(project.schematic),
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
    ap.add_argument("--project", default="fome-mc", help="Project from toolchain/versions.toml")
    ap.add_argument("--rev", help="Git revision to snapshot and export (default: working tree, records HEAD)")
    ap.add_argument("--fill", default="asis", choices=["asis", "refill"])
    ap.add_argument("--run-dir", type=Path, help="Existing run directory to consume instead of running eda.py")
    ap.add_argument("--verify", action="store_true", help="Verify existing manifest matches fresh export")
    args = ap.parse_args()

    try:
        project = project_config(args.project)
    except ValueError as exc:
        ap.error(str(exc))
    rev_for_meta = args.rev or "HEAD"
    if args.run_dir:
        run_dir = args.run_dir.resolve()
    elif args.verify:
        run_dir = run_fast_verify_export(args.rev, args.fill, project)
    else:
        run_dir = run_export(args.rev, args.fill, project)

    if args.verify:
        if not project.manifest_path.exists():
            print(f"ERROR: {project.manifest_path} does not exist", file=sys.stderr)
            return 1
        recorded = json.loads(project.manifest_path.read_text())
        fresh = build_manifest(run_dir, rev_for_meta, args.fill, project, update_gerbers=False)
        mismatches = []
        for key in (
            "project",
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
            elif k.startswith(project.relative("export/gerbers") + "/"):
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

    manifest = build_manifest(run_dir, rev_for_meta, args.fill, project, update_gerbers=True)
    project.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    project.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Wrote {project.manifest_path.relative_to(REPO)} and {project.gerbers_dir.relative_to(REPO)}/ "
        f"({len(manifest['artifacts'])} artifacts, board_sha256={manifest['board_sha256'][:12]})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
