#!/usr/bin/env python3
"""Thin, reproducible wrappers around the fome-mc EDA toolchain.

Every check runs the native tool (kicad-cli, KiBot, kicad-happy, ngspice) on a
*snapshot* of the project inside a fresh run directory, records the exact
command, exit status, log, input/output hashes and tool versions, and then
validates the tool's own output. Results are explicit:

    PASS         the tool ran and produced a complete, well-formed result
    FAIL         the tool is missing, crashed, produced malformed output, or
                 skipped part of its work
    NOT_RUN      a prerequisite failed, so the step was not attempted
    UNSUPPORTED  the requested operation cannot be done with this toolchain

PASS is about the *check*, not the design: a design with ERC/DRC violations
still yields PASS when KiCad ran to completion. Violations are reported
separately under `findings` and `design_clean`.

Usage (normally via the Makefile):
    eda.py doctor
    eda.py run --project fome-mc --steps erc,drc,netlist,export,analyze [--fill asis|refill]
    eda.py simulate DECK.cir [--expect EXPECT.json] [--out DIR]
    eda.py smoke
    eda.py baseline
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

TOOLCHAIN = Path(__file__).resolve().parent
REPO = TOOLCHAIN.parent
BUILD = REPO / "build"
VENV = TOOLCHAIN / ".venv"
VENDOR = TOOLCHAIN / "vendor" / "kicad-happy"
KIBOT_CONFIG = TOOLCHAIN / "kibot" / "export.kibot.yaml"
KICAD_CONFIG_HOME = BUILD / "kicad-config"
KICAD_SHARE = Path("/usr/share/kicad")
REPORTS = REPO / "reports" / "toolchain"
PASS, FAIL, NOT_RUN, UNSUPPORTED = "PASS", "FAIL", "NOT_RUN", "UNSUPPORTED"
ALL_STEPS = ["erc", "drc", "netlist", "export", "analyze"]
# Lines KiCad 10 prints on every start-up from a harmless wx property assert.
NOISE = re.compile(r'property\.h\(\d+\): assert "m_choices\.GetCount\(\) > 0"')


def load_pins():
    with open(TOOLCHAIN / "versions.toml", "rb") as f:
        return tomllib.load(f)


PINS = load_pins()


def expand(path):
    return Path(os.path.expanduser(str(path)))


def fome_lib_dir():
    return expand(os.environ.get("FOME_KICAD_LIBS", PINS["libraries"]["fome"]["path"]))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def rel(path):
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


# --------------------------------------------------------------------------- env

def ensure_kicad_config():
    """Hermetic KiCad config: stock global library tables, nothing from the GUI."""
    cfg = KICAD_CONFIG_HOME / "10.0"
    cfg.mkdir(parents=True, exist_ok=True)
    for table in ("sym-lib-table", "fp-lib-table"):
        src = KICAD_SHARE / "template" / table
        dst = cfg / table
        if src.exists() and (not dst.exists() or dst.read_bytes() != src.read_bytes()):
            shutil.copyfile(src, dst)
    return cfg


def tool_env():
    env = dict(os.environ)
    env["PATH"] = f"{VENV / 'bin'}:{env.get('PATH', '')}"
    env["KICAD_CONFIG_HOME"] = str(KICAD_CONFIG_HOME)
    env["KICAD10_SYMBOL_DIR"] = str(KICAD_SHARE / "symbols")
    env["KICAD10_FOOTPRINT_DIR"] = str(KICAD_SHARE / "footprints")
    env["KICAD10_TEMPLATE_DIR"] = str(KICAD_SHARE / "template")
    env["FOME_KICAD_LIBS"] = str(fome_lib_dir())
    env.pop("VIRTUAL_ENV", None)
    env.pop("PYTHONPATH", None)
    return env


def venv_python():
    return VENV / "bin" / "python"


def run_cmd(argv, cwd, log_path, timeout=1800):
    """Run one command, capture its combined output to a log, return a record."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    record = {"argv": [str(a) for a in argv], "cwd": rel(cwd), "log": rel(log_path)}
    try:
        proc = subprocess.run([str(a) for a in argv], cwd=cwd, env=tool_env(),
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=timeout)
        output = proc.stdout.decode("utf-8", "replace")
        record["exit_code"] = proc.returncode
    except FileNotFoundError as e:
        output = f"executable not found: {e}\n"
        record["exit_code"] = None
        record["error"] = "executable_not_found"
    except subprocess.TimeoutExpired as e:
        output = (e.stdout or b"").decode("utf-8", "replace") + f"\nTIMEOUT after {timeout}s\n"
        record["exit_code"] = None
        record["error"] = "timeout"
    record["duration_s"] = round(time.monotonic() - start, 3)
    log_path.write_text(output)
    record["output"] = "\n".join(l for l in output.splitlines() if not NOISE.search(l))
    return record


def public(record):
    return {k: v for k, v in record.items() if k != "output"}


# ---------------------------------------------------------------- tool versions

def tool_versions():
    v = {}
    r = subprocess.run(["kicad-cli", "version"], capture_output=True, text=True)
    v["kicad-cli"] = r.stdout.strip() if r.returncode == 0 else None
    r = subprocess.run(["ngspice", "--version"], capture_output=True, text=True)
    m = re.search(r"ngspice-(\S+)", r.stdout)
    v["ngspice"] = m.group(1) if m else None
    kibot = VENV / "bin" / "kibot"
    if kibot.exists():
        r = subprocess.run([str(kibot), "--version"], capture_output=True, text=True, env=tool_env())
        m = re.search(r"KiBot (\S+)", r.stdout + r.stderr)
        v["kibot"] = m.group(1) if m else None
    v["kicad-happy"] = git(VENDOR, "rev-parse", "HEAD")
    v["fome-kicad-libraries"] = git(fome_lib_dir(), "rev-parse", "HEAD")
    v["python"] = sys.version.split()[0]
    return v


# --------------------------------------------------------------------- snapshot

KICAD_SUFFIXES = {".kicad_sch", ".kicad_pcb", ".kicad_pro", ".kicad_dru", ".kicad_wks",
                  ".kicad_sym", ".lib", ".dcm", ".mod"}
LIB_DIR_SUFFIXES = {".pretty", ".3dshapes"}
URI_RE = re.compile(r'\(uri\s+"?([^")]+?)"?\)')
SHEETFILE_RE = re.compile(r'\(property\s+"Sheet ?file"\s+"([^"]+)"')


def project_config(name):
    try:
        cfg = dict(PINS["projects"][name])
    except KeyError:
        sys.exit(f"unknown project {name!r}; known: {', '.join(PINS['projects'])}")
    d = expand(cfg["dir"])
    cfg["name"] = name
    cfg["path"] = (REPO / d).resolve() if not d.is_absolute() else d.resolve()
    return cfg


def resolve_sheet(project_dir, name, by=None):
    """Exact sheet file, or a unique case-insensitive match (what KiCad sees on
    the case-insensitive filesystems it is often authored on)."""
    candidates = [Path(name)]
    if by and Path(by).parent != Path("."):
        candidates.insert(0, Path(by).parent / name)
    for cand in candidates:
        if (project_dir / cand).exists():
            return str(cand), None
        parent = (project_dir / cand).parent
        if parent.is_dir():
            hits = [p.name for p in parent.iterdir() if p.name.lower() == cand.name.lower()]
            if len(hits) == 1:
                rel_hit = str(cand.parent / hits[0]) if cand.parent != Path(".") else hits[0]
                return rel_hit, hits[0]
    return None, None


def sheet_files(project_dir, root):
    """Schematic files reachable from the root, the sheet-instance count, and
    references whose exact filename does not exist."""
    files, instances, problems = [], 1, []
    seen = {}

    def walk(path, multiplicity):
        nonlocal instances
        if path not in seen:
            files.append(path)
            seen[path] = SHEETFILE_RE.findall((project_dir / path).read_text(errors="replace"))
        for child in seen[path]:
            instances += multiplicity
            actual, case_match = resolve_sheet(project_dir, child, by=path)
            if actual is None:
                problems.append({"referenced": child, "by": path, "resolved": None})
                continue
            if case_match:
                problems.append({"referenced": child, "by": path, "resolved": actual})
            walk(actual, multiplicity)

    walk(root, 1)
    return files, instances, problems


INSTANCE_PROJECT_RE = re.compile(r'\(project\s+"([^"]*)"')
INSTANCE_REF_RE = re.compile(r'\(reference\s+"([^"]+)"\)')


def expected_references(project_dir, sch_files, project_name):
    """Component references the schematic files assign within this project."""
    refs = set()
    for f in sch_files:
        text = (project_dir / f).read_text(errors="replace")
        parts = INSTANCE_PROJECT_RE.split(text)
        # parts = [prefix, name1, chunk1, name2, chunk2, ...]
        named = [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
        mine = [chunk for name, chunk in named if name == project_name]
        for chunk in (mine or [chunk for _, chunk in named]):
            refs.update(r for r in INSTANCE_REF_RE.findall(chunk) if not r.startswith("#"))
    return refs


def export_revision(cfg, run_dir):
    """Materialise the project directory as committed at cfg['rev'] (git archive)."""
    src = cfg["path"]
    top = Path(git(src, "rev-parse", "--show-toplevel"))
    prefix = src.relative_to(top)
    commit = git(top, "rev-parse", "--verify", f"{cfg['rev']}^{{commit}}")
    if not commit:
        sys.exit(f"{cfg['rev']!r} is not a commit in {top}")
    out = run_dir / "source" / src.name
    out.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(top), "archive", "--format=tar", commit, "--", str(prefix) if str(prefix) != "." else "."],
                             capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(out), *(["--strip-components", str(len(prefix.parts))] if prefix.parts else [])],
                   input=archive, check=True)
    return out, commit


def make_snapshot(cfg, run_dir):
    """Copy the KiCad-relevant project files; never touch the source tree."""
    src = cfg["path"]
    origin_parent = src.parent       # where ${KIPRJMOD}/../<dir> really lives
    rev_commit = None
    if cfg.get("rev"):
        src, rev_commit = export_revision(cfg, run_dir)
    snap_root = run_dir / "snapshot"
    dst = snap_root / src.name
    dst.mkdir(parents=True)
    issues = []

    def copy(relpath):
        s, d = src / relpath, dst / relpath
        if d.exists() or d.is_symlink():
            return
        d.parent.mkdir(parents=True, exist_ok=True)
        if s.is_dir():
            shutil.copytree(s, d, symlinks=True)
        elif s.exists():
            shutil.copy2(s, d)

    for entry in sorted(src.iterdir()):
        if entry.is_file() and (entry.suffix in KICAD_SUFFIXES or entry.name in ("sym-lib-table", "fp-lib-table")):
            copy(entry.name)
        elif entry.is_dir() and entry.suffix in LIB_DIR_SUFFIXES:
            copy(entry.name)
    sch_files, sheet_instances, sheet_problems = sheet_files(src, cfg["schematic"])
    for f in sch_files:
        copy(f)
    case_aliases = []
    for prob in sheet_problems:
        if prob["resolved"] is None:
            issues.append(f"sheet file {prob['referenced']!r} (referenced by {prob['by']}) does not exist")
            continue
        alias = dst / prob["referenced"]
        if not alias.exists():
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.symlink_to(Path(prob["resolved"]).name)
        case_aliases.append(prob)
        issues.append(f"sheet file {prob['referenced']!r} (referenced by {prob['by']}) exists only as "
                      f"{prob['resolved']!r}; a case-sensitive filesystem cannot open it. The snapshot "
                      "adds a case alias so the checks cover that sheet; the source repo is unchanged.")

    # Library directories mapped to the shared FOME library repository.
    library_links = []
    for dirname, lib in cfg.get("library_dirs", {}).items():
        target = fome_lib_dir() if lib == "fome" else expand(lib)
        here = src / dirname
        if here.is_dir() and any(here.iterdir()):
            copy(dirname)
            continue
        link = dst / dirname
        if link.exists():
            shutil.rmtree(link)
        link.symlink_to(target)
        pinned = None
        tree = git(cfg["path"], "ls-tree", rev_commit or "HEAD", dirname)
        if tree and " commit " in tree:
            pinned = tree.split()[2]
        actual = git(target, "rev-parse", "HEAD")
        entry = {"path": dirname, "target": str(target), "submodule_pin": pinned, "library_head": actual}
        if pinned and actual and pinned != actual:
            issues.append(f"{dirname}: submodule pins {pinned} but {target} is at {actual}")
        library_links.append(entry)

    # Resolve ${KIPRJMOD} references from the library tables.
    for table in ("sym-lib-table", "fp-lib-table"):
        tpath = src / table
        if not tpath.exists():
            continue
        for uri in URI_RE.findall(tpath.read_text()):
            if not uri.startswith("${KIPRJMOD}/"):
                if "${KIPRJMOD}" not in uri and not uri.startswith("${KICAD"):
                    if not expand(uri).exists():
                        issues.append(f"{table}: {uri} does not exist")
                continue
            relpath = Path(uri[len("${KIPRJMOD}/"):])
            original = Path(os.path.normpath(src / relpath))
            if not original.is_relative_to(src):
                original = Path(os.path.normpath(origin_parent / src.name / relpath))
            if original.is_relative_to(src):
                inner = original.relative_to(src)
                if not (src / inner).exists() and not (dst / inner).exists():
                    issues.append(f"{table}: {uri} does not exist")
                elif inner.parts and not (dst / inner.parts[0]).exists():
                    copy(inner.parts[0])
                continue
            up = 0
            for part in relpath.parts:
                if part != "..":
                    break
                up += 1
            if up != 1 or len(relpath.parts) < 2:
                issues.append(f"{table}: {uri} leaves the project more than one level; unsupported")
                continue
            first = relpath.parts[1]
            link, target = snap_root / first, origin_parent / first
            if not target.exists():
                issues.append(f"{table}: {uri} does not exist")
            elif not link.exists():
                link.symlink_to(target)
                library_links.append({"path": f"../{first}", "target": str(target),
                                      "library_head": git(target, "rev-parse", "HEAD")})
            if not original.exists():
                issues.append(f"{table}: {uri} does not exist")

    files = {}
    for root, dirs, names in os.walk(dst):  # does not descend into symlinked dirs
        for n in names:
            p = Path(root) / n
            if not p.is_symlink():
                files[str(p.relative_to(dst))] = sha256(p)
    files = dict(sorted(files.items()))
    if rev_commit:
        head, dirty = rev_commit, None
    else:
        head = git(src, "rev-parse", "HEAD")
        dirty = git(src, "status", "--porcelain", "--", *[f for f in files if (src / f).exists()]) if head else None
    manifest = {
        "project": cfg["name"],
        "source_dir": str(cfg["path"]),
        "source": f"git revision {cfg['rev']} ({rev_commit})" if rev_commit else "working tree",
        "source_git_head": head,
        "source_dirty_files": dirty.splitlines() if dirty else [],
        "schematic": cfg["schematic"],
        "pcb": cfg.get("pcb"),
        "schematic_files": sch_files,
        "sheet_instances": sheet_instances,
        "sheet_case_aliases": case_aliases,
        "missing_sheets": [p for p in sheet_problems if p["resolved"] is None],
        "library_links": library_links,
        "library_issues": issues,
        "files": files,
    }
    write_json(run_dir / "snapshot.json", manifest)
    return dst, manifest


# ------------------------------------------------------------------------ steps

class Step:
    def __init__(self, name, run_dir):
        self.name = name
        self.dir = run_dir / name
        self.dir.mkdir(parents=True, exist_ok=True)
        self.result = {"step": name, "status": None, "reasons": [], "commands": [],
                       "inputs": {}, "outputs": {}, "findings": {}}

    def cmd(self, argv, cwd, label, timeout=1800):
        rec = run_cmd(argv, cwd, self.dir / f"{label}.log", timeout)
        self.result["commands"].append(public(rec))
        return rec

    def fail(self, reason):
        self.result["reasons"].append(reason)
        self.result["status"] = FAIL

    def inputs(self, *paths):
        for p in paths:
            self.result["inputs"][Path(p).name] = sha256(p)

    def outputs(self, *paths):
        for p in paths:
            p = Path(p)
            if p.is_file():
                self.result["outputs"][rel(p)] = {"sha256": sha256(p), "bytes": p.stat().st_size}

    def finish(self):
        if self.result["status"] is None:
            self.result["status"] = PASS
        write_json(self.dir / "result.json", self.result)
        return self.result


def ok_exit(step, rec, what):
    if rec.get("error") == "executable_not_found":
        step.fail(f"{what}: executable not found")
        return False
    if rec.get("error") == "timeout":
        step.fail(f"{what}: timed out")
        return False
    if rec["exit_code"] != 0:
        step.fail(f"{what}: exit code {rec['exit_code']}")
        return False
    return True


def load_json(step, path, what):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        step.fail(f"{what}: output {rel(path)} was not written")
    except json.JSONDecodeError as e:
        step.fail(f"{what}: output {rel(path)} is not valid JSON ({e})")
    return None


def check_kicad_version(step, report, what):
    want = PINS["tools"]["kicad_cli_version"]
    if report.get("kicad_version") != want:
        step.fail(f"{what}: report kicad_version {report.get('kicad_version')!r} != pinned {want}")


def count_by(items, key):
    out = {}
    for it in items:
        out[it.get(key, "?")] = out.get(it.get(key, "?"), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def step_erc(ctx):
    step = Step("erc", ctx["run_dir"])
    sch = ctx["snap"] / ctx["cfg"]["schematic"]
    step.inputs(sch)
    out = step.dir / "erc.json"
    rec = step.cmd(["kicad-cli", "sch", "erc", "--format", "json", "--severity-all",
                    "--units", "mm", "-o", out, sch], ctx["snap"], "kicad-cli-erc")
    if ok_exit(step, rec, "kicad-cli sch erc"):
        report = load_json(step, out, "ERC")
        if report is not None:
            check_kicad_version(step, report, "ERC")
            for prob in ctx["manifest"].get("missing_sheets", []):
                step.fail(f"sheet {prob['referenced']!r} is missing; ERC could not check it")
            sheets = report.get("sheets")
            if not isinstance(sheets, list):
                step.fail("ERC report has no sheets list")
            else:
                expected = ctx["manifest"]["sheet_instances"]
                if len(sheets) != expected:
                    step.fail(f"ERC covered {len(sheets)} sheet instances, hierarchy has {expected}")
                violations = [v for s in sheets for v in s.get("violations", [])]
                by_sev = count_by(violations, "severity")
                step.result["findings"] = {
                    "sheets_checked": len(sheets),
                    "violations": len(violations),
                    "by_severity": by_sev,
                    "by_type": count_by(violations, "type"),
                    "ignored_checks": [c["key"] for c in report.get("ignored_checks", [])],
                }
                step.result["design_clean"] = len(violations) == 0
            step.outputs(out)
    return step.finish()


def step_drc(ctx):
    step = Step("drc", ctx["run_dir"])
    pcb = ctx["snap"] / ctx["cfg"]["pcb"]
    step.inputs(pcb)
    step.result["fill_mode"] = ctx["fill"]
    if ctx["fill"] == "refill":
        before = sha256(pcb)
        rec = step.cmd(["kicad-cli", "pcb", "drc", "--refill-zones", "--save-board",
                        "--format", "json", "-o", step.dir / "drc-refill-pass.json", pcb],
                       ctx["snap"], "kicad-cli-drc-refill-save")
        if not ok_exit(step, rec, "kicad-cli pcb drc --refill-zones --save-board"):
            return step.finish()
        after = sha256(pcb)
        step.result["refill"] = {"board_sha256_before": before, "board_sha256_after": after,
                                 "board_changed": before != after}
    out = step.dir / "drc.json"
    rec = step.cmd(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all",
                    "--schematic-parity", "--units", "mm", "-o", out, pcb],
                   ctx["snap"], "kicad-cli-drc")
    step.result["board_sha256_checked"] = sha256(pcb)
    ctx["board_sha256_checked"] = step.result["board_sha256_checked"]
    if ok_exit(step, rec, "kicad-cli pcb drc"):
        report = load_json(step, out, "DRC")
        if report is not None:
            check_kicad_version(step, report, "DRC")
            for key in ("violations", "unconnected_items", "schematic_parity"):
                if not isinstance(report.get(key), list):
                    step.fail(f"DRC report is missing {key}")
            # kicad-cli exits 0 and reports zero parity issues when it could not
            # load the schematic; its console message is the only signal.
            m = re.search(r"(?i)failed to fetch schematic netlist[^\n]*|parity tests require[^\n]*", rec["output"])
            if m:
                step.fail(f"schematic parity was not performed: {m.group(0).strip()}")
            if step.result["status"] is None:
                v, u, p = report["violations"], report["unconnected_items"], report["schematic_parity"]
                step.result["findings"] = {
                    "violations": len(v), "unconnected_items": len(u), "schematic_parity": len(p),
                    "by_severity": count_by(v + u + p, "severity"),
                    "by_type": count_by(v + u + p, "type"),
                    "ignored_checks": [c["key"] for c in report.get("ignored_checks", [])],
                }
                step.result["design_clean"] = not (v or u or p)
            step.outputs(out)
    return step.finish()


def parse_sexpr_netlist(text):
    comps = re.findall(r'\(comp\s+\(ref\s+"([^"]+)"\)\s*\(value\s+"([^"]*)"\)', text)
    nets = {}
    for block in re.split(r"\n\t\t\(net\b", text.split("(nets", 1)[1] if "(nets" in text else "")[1:]:
        name = re.search(r'\(name\s+"([^"]*)"\)', block)
        nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s*\(pin\s+"([^"]+)"\)', block)
        if name:
            nets[name.group(1)] = sorted(f"{r}.{p}" for r, p in nodes)
    return {"components": dict(comps), "nets": nets}


def step_netlist(ctx):
    step = Step("netlist", ctx["run_dir"])
    sch = ctx["snap"] / ctx["cfg"]["schematic"]
    step.inputs(sch)
    out = step.dir / (Path(ctx["cfg"]["schematic"]).stem + ".net")
    rec = step.cmd(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out, sch],
                   ctx["snap"], "kicad-cli-netlist")
    if ok_exit(step, rec, "kicad-cli sch export netlist"):
        if not out.exists() or out.stat().st_size == 0:
            step.fail("netlist was not written")
        else:
            parsed = parse_sexpr_netlist(out.read_text())
            write_json(step.dir / "connectivity.json", parsed)
            if not parsed["components"] or not parsed["nets"]:
                step.fail("netlist has no components or no nets")
            pro = Path(ctx["cfg"]["schematic"]).stem
            expected = expected_references(ctx["snap"], ctx["manifest"]["schematic_files"], pro)
            missing = sorted(expected - set(parsed["components"]))
            step.result["coverage"] = {"schematic_references": len(expected),
                                       "missing_from_netlist": missing}
            if missing:
                step.fail(f"netlist is missing {len(missing)} component(s) placed in the schematic "
                          f"(e.g. {', '.join(missing[:8])}); a sheet was not loaded")
            for prob in ctx["manifest"].get("missing_sheets", []):
                step.fail(f"sheet {prob['referenced']!r} is missing; its content cannot be checked")
            step.result["findings"] = {"components": len(parsed["components"]), "nets": len(parsed["nets"])}
            ctx["netlist"] = parsed
            step.outputs(out, step.dir / "connectivity.json")
    return step.finish()


def pdf_pages(path):
    r = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
    m = re.search(r"^Pages:\s+(\d+)", r.stdout, re.M)
    return int(m.group(1)) if m else 0


KIBOT_EXPECTED = {
    "gerber F.Cu": "gerbers/*-F_Cu.gbr",
    "gerber B.Cu": "gerbers/*-B_Cu.gbr",
    "gerber Edge.Cuts": "gerbers/*-Edge_Cuts.gbr",
    "gerber job file": "gerbers/*-job.gbrjob",
    "excellon drill": "gerbers/*.drl",
    "drill report": "gerbers/*drill_report*",
    "position files": "assembly/*pos.csv",
    "BOM CSV": "bom/*-bom.csv",
    "BOM HTML": "bom/*-bom.html",
    "schematic PDF": "schematic/*.pdf",
    "PCB print PDF": "pcb/*.pdf",
}


# KiBot messages it emits through logger.non_critical_error that do not mean an
# output was skipped. Each entry is documented in toolchain/README.md.
KIBOT_KNOWN_NONCRITICAL = [
    # Stock KiCad footprints carry fab-layer text "${REFERENCE}". KiCad expands it
    # when plotting; KiBot's variable expander (kicad/config.py) does not know it
    # while loading BOM data and says so. The BOM and plots are unaffected.
    r"Unable to expand `REFERENCE` in `\$\{REFERENCE\}`",
]


def step_export(ctx):
    step = Step("export", ctx["run_dir"])
    sch = ctx["snap"] / ctx["cfg"]["schematic"]
    pcb = ctx["snap"] / ctx["cfg"]["pcb"]
    step.inputs(sch, pcb)
    checked = ctx.get("board_sha256_checked")
    if checked is None:
        step.result["status"] = NOT_RUN
        step.result["reasons"].append("export requires DRC on the same snapshot first")
        return step.finish()
    if sha256(pcb) != checked:
        step.fail("board changed after DRC; exports would not match the checked fill state")
        return step.finish()
    step.result["board_sha256"] = checked
    stem = Path(ctx["cfg"]["schematic"]).stem
    native = step.dir / "native"
    native.mkdir()

    jobs = [
        ("schematic PDF", ["kicad-cli", "sch", "export", "pdf", "-o", native / f"{stem}-schematic.pdf", sch],
         native / f"{stem}-schematic.pdf"),
        ("schematic SVG", ["kicad-cli", "sch", "export", "svg", "-o", native / "schematic-svg", sch],
         native / "schematic-svg"),
        ("PCB PDF", ["kicad-cli", "pcb", "export", "pdf", "--mode-multipage",
                     "-l", "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Fab,B.Fab", "--cl", "Edge.Cuts",
                     "-o", native / f"{Path(ctx['cfg']['pcb']).stem}-layers.pdf", pcb],
         native / f"{Path(ctx['cfg']['pcb']).stem}-layers.pdf"),
        ("BOM CSV", ["kicad-cli", "sch", "export", "bom", "--fields",
                     "Reference,Value,Footprint,${QUANTITY},${DNP}", "--labels",
                     "Refs,Value,Footprint,Qty,DNP", "--group-by", "Value,Footprint",
                     "--ref-range-delimiter", "",
                     "-o", native / f"{stem}-bom.csv", sch],
         native / f"{stem}-bom.csv"),
    ]
    produced = {}
    for label, argv, out in jobs:
        rec = step.cmd(argv, ctx["snap"], "kicad-cli-" + label.lower().replace(" ", "-"))
        if not ok_exit(step, rec, f"kicad-cli {label}"):
            continue
        if out.is_dir():
            svgs = sorted(out.glob("*.svg"))
            if not svgs:
                step.fail(f"{label}: no SVG files written")
            produced[label] = len(svgs)
            step.outputs(*svgs)
        elif not out.exists() or out.stat().st_size == 0:
            step.fail(f"{label}: {rel(out)} not written")
        else:
            if out.suffix == ".pdf":
                pages = pdf_pages(out)
                if pages < 1:
                    step.fail(f"{label}: {rel(out)} has no pages")
                produced[label] = pages
            else:
                produced[label] = out.stat().st_size
            step.outputs(out)

    # Rendered artifacts must actually contain the design.
    sch_pdf = native / f"{stem}-schematic.pdf"
    if sch_pdf.exists() and ctx.get("netlist"):
        text = subprocess.run(["pdftotext", str(sch_pdf), "-"], capture_output=True, text=True).stdout
        refs = [r for r in ctx["netlist"]["components"] if not r.startswith("#")]
        found = [r for r in refs if re.search(rf"\b{re.escape(r)}\b", text)]
        step.result["schematic_pdf_refs_found"] = f"{len(found)}/{len(refs)}"
        if refs and not found:
            step.fail("schematic PDF text contains none of the netlist references")
    bom = native / f"{stem}-bom.csv"
    if bom.exists():
        import csv
        with open(bom, newline="") as fh:
            rows = list(csv.DictReader(fh))
        bom_refs = {r.strip() for row in rows for r in (row.get("Refs") or "").split(",") if r.strip()}
        step.result["bom"] = {"lines": len(rows), "references": len(bom_refs)}
        if not bom_refs:
            step.fail("BOM lists no references")
        if ctx.get("netlist"):
            native_refs = {r for r in ctx["netlist"]["components"] if not r.startswith("#")}
            step.result["bom"]["netlist_refs_not_in_bom"] = sorted(native_refs - bom_refs)
            step.result["bom"]["bom_refs_not_in_netlist"] = sorted(bom_refs - native_refs)

    kibot_dir = step.dir / "kibot"
    rec = step.cmd([VENV / "bin" / "kibot", "-A", "-c", KIBOT_CONFIG, "-e", sch, "-b", pcb,
                    "-d", kibot_dir], ctx["snap"], "kibot")
    if ok_exit(step, rec, "kibot"):
        missing = []
        for label, pattern in KIBOT_EXPECTED.items():
            hits = [p for p in kibot_dir.glob(pattern) if p.is_file() and p.stat().st_size > 0]
            if not hits:
                missing.append(label)
            if label.endswith("PDF"):
                for p in hits:
                    if pdf_pages(p) < 1:
                        missing.append(f"{label} (empty)")
            produced[f"kibot {label}"] = len(hits)
        if missing:
            step.fail("KiBot bundle is missing: " + ", ".join(missing))
        errors = re.findall(r"(?m)^ERROR:(.*)$", rec["output"])
        known = [e for e in errors if any(re.search(p, e) for p in KIBOT_KNOWN_NONCRITICAL)]
        unknown = [e for e in errors if e not in known]
        step.result["kibot_diagnostics"] = {
            "errors": len(errors), "known_non_critical": sorted(set(known)),
            "warnings_by_code": count_by([{"c": c} for c in re.findall(r"(?m)^WARNING:\((W\d+)\)", rec["output"])], "c")}
        if unknown:
            step.fail("KiBot logged errors: " + "; ".join(sorted(set(u.strip() for u in unknown)))[:500])
        step.outputs(*sorted(p for p in kibot_dir.rglob("*") if p.is_file()))
    if sha256(pcb) != checked:
        step.fail("an export tool modified the board snapshot")
    step.result["findings"] = {"artifacts": produced}
    return step.finish()


def kicad_happy(script):
    return VENDOR / "skills" / script


def step_analyze(ctx):
    step = Step("analyze", ctx["run_dir"])
    sch = ctx["snap"] / ctx["cfg"]["schematic"]
    pcb = ctx["snap"] / ctx["cfg"]["pcb"]
    step.inputs(sch, pcb)
    if not VENDOR.exists():
        step.fail(f"kicad-happy is not installed at {rel(VENDOR)} (run make bootstrap)")
        return step.finish()
    py = [venv_python(), "-I"]
    d = step.dir
    runs = [
        ("schematic", [*py, kicad_happy("kicad/scripts/analyze_schematic.py"), sch, "-o", d / "schematic.json"],
         d / "schematic.json"),
        ("pcb", [*py, kicad_happy("kicad/scripts/analyze_pcb.py"), pcb, "--full",
                 "--schematic", d / "schematic.json", "-o", d / "pcb.json"], d / "pcb.json"),
        ("cross_analysis", [*py, kicad_happy("kicad/scripts/cross_analysis.py"),
                            "-s", d / "schematic.json", "-p", d / "pcb.json", "-o", d / "cross.json"],
         d / "cross.json"),
        ("spice", [*py, kicad_happy("spice/scripts/simulate_subcircuits.py"), d / "schematic.json",
                   "--simulator", "ngspice", "-w", d / "spice_work", "-o", d / "spice.json"],
         d / "spice.json"),
    ]
    reports = {}
    for kind, argv, out in runs:
        if kind != "schematic" and "schematic" not in reports:
            step.result["reasons"].append(f"{kind}: not run (schematic analysis failed)")
            continue
        rec = step.cmd(argv, d, f"kicad-happy-{kind}", timeout=3600)
        if not ok_exit(step, rec, f"kicad-happy {kind}"):
            continue
        report = load_json(step, out, f"kicad-happy {kind}")
        if report is None:
            continue
        if report.get("analyzer_type") != kind:
            step.fail(f"kicad-happy {kind}: analyzer_type is {report.get('analyzer_type')!r}")
            continue
        reports[kind] = report
        step.outputs(out)

    f = {}
    if "schematic" in reports:
        s = reports["schematic"]
        f["schematic"] = {"components": s.get("statistics", {}).get("total_components"),
                          "nets": s.get("statistics", {}).get("total_nets"),
                          "findings": s.get("summary", {}).get("by_severity")}
        if not s.get("statistics", {}).get("total_components"):
            step.fail("kicad-happy schematic analysis found no components")
        if ctx.get("netlist"):
            native = len([r for r in ctx["netlist"]["components"] if not r.startswith("#")])
            f["schematic"]["native_netlist_components"] = native
    if "pcb" in reports:
        p = reports["pcb"]
        f["pcb"] = {"footprints": p.get("statistics", {}).get("footprint_count"),
                    "nets": p.get("statistics", {}).get("net_count"),
                    "routing_complete": p.get("statistics", {}).get("routing_complete"),
                    "cross_reference_input": "schematic.json",
                    "power_net_resolution_source": (p.get("power_net_resolution") or {}).get("source"),
                    "findings": p.get("summary", {}).get("by_severity")}
        if not p.get("statistics", {}).get("footprint_count"):
            step.fail("kicad-happy PCB analysis found no footprints")
        if (p.get("power_net_resolution") or {}).get("source") != "schematic":
            step.fail("kicad-happy PCB analysis did not use the schematic cross-reference input")
    if "cross_analysis" in reports:
        c = reports["cross_analysis"]
        f["cross_analysis"] = {"checks_run": len(c.get("checks_run", [])),
                               "findings": c.get("summary", {}).get("by_severity")}
    if "spice" in reports:
        sp = reports["spice"]
        f["spice"] = {"simulator": sp.get("simulator"), "summary": {k: sp.get("summary", {}).get(k)
                      for k in ("total", "pass", "warn", "fail", "skip")}}
        if not sp.get("simulator"):
            step.fail("kicad-happy spice found no simulator")
    step.result["findings"] = f
    return step.finish()


STEP_FUNCS = {"erc": step_erc, "drc": step_drc, "netlist": step_netlist,
              "export": step_export, "analyze": step_analyze}


def new_run_dir(kind, name):
    stamp = now_utc().strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = BUILD / "runs" / kind / name / stamp
    run_dir.mkdir(parents=True)  # fresh: never reuse a previous run's outputs
    latest = run_dir.parent / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    latest.symlink_to(run_dir.name)
    return run_dir


def overall(results):
    statuses = [r["status"] for r in results]
    if not statuses:
        return NOT_RUN
    if FAIL in statuses:
        return FAIL
    if all(s == PASS for s in statuses):
        return PASS
    if UNSUPPORTED in statuses:
        return UNSUPPORTED
    return NOT_RUN


def run_project(name, steps, fill="asis", cfg=None, rev=None, label=None):
    """Run steps on a fresh snapshot of the working tree, or of git revision `rev`.
    `cfg` lets tests point at a disposable copy; `label` names the run directory."""
    ensure_kicad_config()
    cfg = dict(cfg or project_config(name))
    if rev:
        cfg["rev"] = rev
    if "export" in steps and "drc" not in steps:
        steps = ["drc"] + steps  # export must use the board state DRC checked
    if "export" in steps and "netlist" not in steps:
        steps = steps + ["netlist"]
    steps = [s for s in ALL_STEPS if s in steps]
    run_dir = new_run_dir("project", label or name)
    started = now_utc()
    snap, manifest = make_snapshot(cfg, run_dir)
    ctx = {"cfg": cfg, "snap": snap, "manifest": manifest, "run_dir": run_dir, "fill": fill}
    results = []
    for s in steps:
        if not cfg.get("pcb") and s in ("drc", "export"):
            results.append({"step": s, "status": UNSUPPORTED, "reasons": ["project has no PCB"]})
            continue
        print(f"[{name}] {s} ...", flush=True)
        r = STEP_FUNCS[s](ctx)
        print(f"[{name}] {s}: {r['status']}" + (f" ({'; '.join(r['reasons'])})" if r["reasons"] else ""), flush=True)
        results.append(r)
    summary = {
        "kind": "project",
        "project": name,
        "label": label or name,
        "description": cfg.get("description"),
        "status": overall(results),
        "started_utc": started.isoformat(),
        "finished_utc": now_utc().isoformat(),
        "run_dir": rel(run_dir),
        "fill_mode": fill,
        "tool_versions": tool_versions(),
        "snapshot": {k: v for k, v in manifest.items() if k != "files"},
        "steps": {r["step"]: {k: r.get(k) for k in ("status", "reasons", "design_clean", "findings")}
                  for r in results},
    }
    write_json(run_dir / "summary.json", summary)
    (run_dir / "SUMMARY.md").write_text(render_summary(summary))
    print(f"[{name}] overall: {summary['status']}  ->  {rel(run_dir)}/SUMMARY.md")
    return summary


def render_summary(s):
    lines = [f"# {s.get('label', s['project'])}: toolchain run {s['status']}", "",
             f"- Description: {s.get('description')}",
             f"- Run: `{s['run_dir']}` ({s['started_utc']} → {s['finished_utc']})",
             f"- Source: `{s['snapshot']['source_dir']}` — {s['snapshot'].get('source', 'working tree')}"
             f" @ `{s['snapshot']['source_git_head']}`"
             f" ({len(s['snapshot']['source_dirty_files'])} uncommitted file(s) in snapshot)",
             f"- Fill mode: `{s['fill_mode']}`",
             f"- Tools: " + ", ".join(f"{k} {v}" for k, v in s["tool_versions"].items()), ""]
    if s["snapshot"]["library_issues"]:
        lines += ["## Library resolution issues", ""] + [f"- {i}" for i in s["snapshot"]["library_issues"]] + [""]
    lines += ["| Step | Check status | Design clean | Findings |", "|---|---|---|---|"]
    for name, st in s["steps"].items():
        f = json.dumps(st.get("findings") or {}, sort_keys=False)
        if len(f) > 400:
            f = f[:400] + "…"
        lines.append(f"| {name} | {st['status']} | {st.get('design_clean', 'n/a')} | `{f}` |")
        for r in st.get("reasons") or []:
            lines.append(f"|  | ↳ {r} |  |  |")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------- simulation

FAIL_PATTERNS = [
    r"(?i)timestep too small", r"(?i)simulation\(s\) aborted", r"(?i)singular matrix",
    r"(?i)no convergence", r"(?i)iteration limit reached", r"(?i)run simulation\(s\) aborted",
    r"(?i)^\s*error\b", r"(?i)fatal", r"(?i)\bfailed!",
]
MEAS_DEF = re.compile(r"(?im)^\s*\.meas(?:ure)?\s+\w+\s+(\w+)")
MEAS_OUT = re.compile(r"(?m)^\s*([A-Za-z_]\w*)\s*=\s*(\S+)")


def read_raw(path):
    """Parse an ngspice binary raw file (real or complex). Returns (names, ndarray)."""
    import numpy as np
    data = Path(path).read_bytes()
    marker = b"Binary:\n"
    idx = data.find(marker)
    if idx < 0:
        raise ValueError("not a binary raw file")
    header = data[:idx].decode("latin-1")
    nvars = int(re.search(r"No\. Variables:\s*(\d+)", header).group(1))
    npts = int(re.search(r"No\. Points:\s*(\d+)", header).group(1))
    complex_ = "complex" in re.search(r"Flags:\s*(.*)", header).group(1)
    names = re.findall(r"^[ \t]+\d+[ \t]+(\S+)[ \t]+\S+", header.split("\nVariables:", 1)[1], re.M)[:nvars]
    if len(names) != nvars:
        raise ValueError(f"raw header lists {len(names)} variables, expected {nvars}")
    dtype = np.complex128 if complex_ else np.float64
    arr = np.frombuffer(data[idx + len(marker):], dtype=dtype)
    if arr.size != nvars * npts:
        raise ValueError(f"raw data has {arr.size} values, header promises {nvars}x{npts}")
    return names, arr.reshape(npts, nvars)


def simulate(deck, expect=None, out=None):
    deck = Path(deck).resolve()
    run_dir = Path(out).resolve() if out else new_run_dir("sim", deck.stem)
    if out:
        if run_dir.exists() and any(run_dir.iterdir()):
            sys.exit(f"output directory {run_dir} is not empty; refusing to reuse old results")
        run_dir.mkdir(parents=True, exist_ok=True)
    step = Step("simulate", run_dir)
    step.result["run_dir"] = rel(step.dir)
    step.inputs(deck)
    text = deck.read_text()
    if re.search(r"(?im)^\s*\.control\b", text):
        step.result["status"] = UNSUPPORTED
        step.result["reasons"].append("decks must not contain a .control block; the runner supplies one")
        return step.finish()
    wanted = [m.lower() for m in MEAS_DEF.findall(text)]
    raw = step.dir / "result.raw"
    control = step.dir / "control.sp"
    # One consistent method: a generated control script sets compatibility
    # explicitly, sources the deck, runs it (which evaluates .meas), and writes
    # the raw file. `-b -r` is NOT used: in that mode ngspice writes the raw file
    # but silently skips .meas. `-n` keeps ~/.spiceinit out of the run.
    control.write_text(
        "* fome-mc toolchain ngspice control script (generated)\n"
        ".control\n"
        "set ngbehavior=kicad\n"
        "set num_threads=1\n"
        "set noaskquit\n"
        f"source {deck}\n"
        "run\n"
        f"write {raw}\n"
        "quit\n"
        ".endc\n"
        ".end\n")
    log = step.dir / "ngspice.log"
    rec = step.cmd(["ngspice", "-n", "-b", "-o", log, control], deck.parent, "ngspice-console", timeout=600)
    step.result["method"] = "ngspice -n -b -o <log> <control.sp>; control: set ngbehavior=kicad, source, run, write"
    if ok_exit(step, rec, "ngspice"):
        log_text = log.read_text(errors="replace") if log.exists() else ""
        for pat in FAIL_PATTERNS:
            m = re.search(pat, log_text, re.M)
            if m:
                step.fail(f"ngspice log reports a problem: {m.group(0).strip()!r}")
        if "measurements for" not in log_text.lower() and wanted:
            step.fail("ngspice ran no measurements")
        measured = {}
        section = log_text.lower().split("measurements for", 1)[-1] if wanted else ""
        for name, value in MEAS_OUT.findall(section):
            try:
                measured[name.lower()] = float(value)
            except ValueError:
                measured[name.lower()] = value
        meas = {}
        for name in wanted:
            v = measured.get(name)
            if v is None:
                step.fail(f"measurement {name} missing from ngspice output")
            elif not isinstance(v, float) or not math.isfinite(v):
                step.fail(f"measurement {name} is not a finite number: {v!r}")
            meas[name] = v
        step.result["measurements"] = meas
        if not wanted:
            step.result["reasons"].append("deck has no .meas statements; only completion was checked")
        try:
            names, arr = read_raw(raw)
            import numpy as np
            if arr.shape[0] < 2:
                step.fail("raw file has fewer than 2 points")
            if not np.all(np.isfinite(arr)):
                step.fail("raw file contains non-finite values")
            step.result["raw"] = {"variables": names, "points": int(arr.shape[0])}
            step.outputs(raw)
        except (OSError, ValueError, AttributeError) as e:
            step.fail(f"raw file unreadable: {e}")
        if expect:
            spec = json.loads(Path(expect).read_text())
            step.inputs(expect)
            checks = {}
            for name, c in spec.get("measurements", {}).items():
                got = meas.get(name.lower())
                exp = c["expected"]
                tol = c.get("rel_tol", 0.01) * abs(exp) + c.get("abs_tol", 0.0)
                okv = isinstance(got, float) and abs(got - exp) <= tol
                checks[name] = {"expected": exp, "measured": got, "tolerance": tol, "ok": okv}
                if not okv:
                    step.fail(f"{name}: measured {got} vs expected {exp} ± {tol:g}")
            step.result["assertions"] = checks
        step.outputs(log)
    r = step.finish()
    print(f"[sim {deck.name}] {r['status']}  measurements={r.get('measurements')}  -> {rel(run_dir)}")
    for reason in r["reasons"]:
        print(f"  - {reason}")
    return r


# ----------------------------------------------------------------------- doctor

def doctor():
    checks = []

    def add(name, status, detail="", required=True):
        checks.append({"check": name, "status": status, "detail": detail, "required": required})

    def which(exe):
        return shutil.which(exe, path=f"{VENV / 'bin'}:{os.environ.get('PATH', '')}")

    import platform
    add("os", PASS, f"{platform.platform()} {platform.machine()}")
    for pkg, want in PINS["apt"].items():
        r = subprocess.run(["dpkg-query", "-W", "-f=${Version}", pkg], capture_output=True, text=True)
        got = r.stdout.strip() if r.returncode == 0 else None
        add(f"apt {pkg}", PASS if got == want else FAIL, f"installed {got}, pinned {want}")
    for exe in ("kicad-cli", "ngspice", "pdftotext", "pdftoppm", "pdfinfo", "mutool", "rsvg-convert", "git", "uv"):
        add(f"exe {exe}", PASS if which(exe) else FAIL, which(exe) or "not found")
    tv = tool_versions()
    add("kicad-cli version", PASS if tv["kicad-cli"] == PINS["tools"]["kicad_cli_version"] else FAIL,
        f"{tv['kicad-cli']} (pinned {PINS['tools']['kicad_cli_version']})")
    add("ngspice version", PASS if tv["ngspice"] == PINS["tools"]["ngspice_version"] else FAIL,
        f"{tv['ngspice']} (pinned {PINS['tools']['ngspice_version']})")

    help_checks = {
        "kicad-cli sch erc --format json": (["kicad-cli", "sch", "erc", "--help"], "--format"),
        "kicad-cli pcb drc --schematic-parity": (["kicad-cli", "pcb", "drc", "--help"], "--schematic-parity"),
        "kicad-cli pcb drc --refill-zones --save-board": (["kicad-cli", "pcb", "drc", "--help"], "--save-board"),
        "kicad-cli sch export netlist (spice format)": (["kicad-cli", "sch", "export", "netlist", "--help"], "spice"),
        "kicad-cli pcb export gerbers": (["kicad-cli", "pcb", "export", "gerbers", "--help"], "Usage"),
        "kicad-cli sch export bom": (["kicad-cli", "sch", "export", "bom", "--help"], "--group-by"),
    }
    for name, (argv, needle) in help_checks.items():
        r = subprocess.run(argv, capture_output=True, text=True)
        add(f"capability {name}", PASS if needle in (r.stdout + r.stderr) else UNSUPPORTED)

    py = venv_python()
    if not py.exists():
        add("python venv", FAIL, f"{rel(VENV)} missing (run make bootstrap)")
    else:
        r = subprocess.run([str(py), "-c", "import sys,pcbnew,wx,numpy,pytest,jsonschema,yaml;"
                            "print(sys.version.split()[0], pcbnew.Version(), wx.version().split()[0],"
                            " numpy.__version__, pytest.__version__)"],
                           capture_output=True, text=True, env=tool_env())
        out = r.stdout.strip().split()
        add("python venv imports (pcbnew, wx, numpy, pytest, jsonschema, yaml)",
            PASS if r.returncode == 0 else FAIL, " ".join(out) if r.returncode == 0 else r.stderr[-300:])
        if r.returncode == 0:
            add("venv python", PASS if out[0].startswith(PINS["tools"]["python"]) else FAIL, out[0])
            add("pcbnew bindings match kicad-cli", PASS if out[1] == tv["kicad-cli"] else FAIL, out[1])
        r = subprocess.run(["uv", "sync", "--frozen", "--check", "--python", "/usr/bin/python3"],
                           cwd=TOOLCHAIN, capture_output=True, text=True,
                           env={**os.environ, "UV_PROJECT_ENVIRONMENT": str(VENV)})
        add("venv matches uv.lock", PASS if r.returncode == 0 else FAIL,
            (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "")
        add("kibot version", PASS if tv.get("kibot") == PINS["tools"]["kibot_version"] else FAIL,
            f"{tv.get('kibot')} (pinned {PINS['tools']['kibot_version']})")
        r = subprocess.run([str(py), "-c", "import importlib.metadata as m; print(m.version('kiauto'))"],
                           capture_output=True, text=True)
        add("kiauto version", PASS if r.stdout.strip() == PINS["tools"]["kiauto_version"] else FAIL, r.stdout.strip())
        add("KiAuto eeschema_do on PATH", PASS if which("eeschema_do") else FAIL, which("eeschema_do") or "")

    kh = PINS["upstream"]["kicad-happy"]
    head = git(VENDOR, "rev-parse", "HEAD")
    add("kicad-happy checkout", PASS if head == kh["commit"] else FAIL,
        f"{rel(VENDOR)} @ {head} (pinned {kh['tag']} {kh['commit'][:12]})")
    if head:
        dirty = git(VENDOR, "status", "--porcelain")
        add("kicad-happy checkout unmodified", PASS if not dirty else FAIL, dirty or "clean")
    r = subprocess.run([sys.executable, str(TOOLCHAIN / "sync_skills.py"), "--check"], capture_output=True, text=True)
    add("agent skills in sync with pinned upstream", PASS if r.returncode == 0 else FAIL,
        (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "")
    for d in (REPO / ".agents" / "skills").glob("*"):
        link = REPO / ".claude" / "skills" / d.name
        add(f"skill {d.name} visible to Claude Code", PASS if (link / "SKILL.md").exists() else FAIL, rel(link))

    sym = KICAD_SHARE / "symbols" / "Device.kicad_sym"
    add("stock symbol library", PASS if sym.exists() else FAIL, str(sym.parent))
    fp = KICAD_SHARE / "footprints" / "Resistor_SMD.pretty"
    add("stock footprint library", PASS if fp.exists() else FAIL, str(fp.parent))
    add("stock 3D models", PASS if (KICAD_SHARE / "3dmodels").exists() else UNSUPPORTED,
        "Stock model library is optional; make render-3d can use a separate persistent model cache", required=False)
    cfg = ensure_kicad_config()
    add("hermetic KiCad config (global lib tables)",
        PASS if (cfg / "sym-lib-table").exists() and (cfg / "fp-lib-table").exists() else FAIL, rel(cfg))
    fome = fome_lib_dir()
    fhead = git(fome, "rev-parse", "HEAD")
    add("FOME library repository", PASS if fhead else FAIL, f"{fome} @ {fhead}")
    if fhead:
        dirty = git(fome, "status", "--porcelain")
        add("FOME library repository clean", PASS if not dirty else FAIL, dirty or "clean", required=False)
    for name in PINS["projects"]:
        cfgp = project_config(name)
        sch, pcb = cfgp["path"] / cfgp["schematic"], cfgp["path"] / cfgp.get("pcb", "")
        add(f"project {name} files", PASS if sch.exists() and pcb.exists() else FAIL, str(cfgp["path"]))
        for dirname, lib in cfgp.get("library_dirs", {}).items():
            tree = git(cfgp["path"], "ls-tree", "HEAD", dirname)
            pin = tree.split()[2] if tree and " commit " in tree else None
            add(f"project {name} {dirname} pin matches FOME libs",
                PASS if pin and pin == fhead else FAIL, f"submodule {pin}, library {fhead}")

    width = max(len(c["check"]) for c in checks)
    for c in checks:
        print(f"{c['status']:<12} {c['check']:<{width}}  {c['detail']}")
    failed = [c for c in checks if c["status"] == FAIL and c["required"]]
    verdict = FAIL if failed else PASS
    print(f"\ndoctor: {verdict} ({len(checks)} checks, {len(failed)} required failures)")
    write_json(BUILD / "doctor" / "doctor.json",
               {"status": verdict, "time_utc": now_utc().isoformat(), "checks": checks})
    return 0 if verdict == PASS else 1


# ------------------------------------------------------------ smoke / baseline

def smoke():
    out = BUILD / "smoke"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    junit = out / "junit.xml"
    r = subprocess.run([str(venv_python()), "-m", "pytest", "-v", "-p", "no:cacheprovider",
                        f"--junitxml={junit}", str(TOOLCHAIN / "tests" / "test_smoke.py")], cwd=REPO, env=tool_env())
    status = PASS if r.returncode == 0 else FAIL
    collected = {}
    for p in sorted(out.glob("*.json")):
        if p.name != "summary.json":
            collected[p.stem] = json.loads(p.read_text())
    summary = {"kind": "smoke", "status": status, "pytest_exit_code": r.returncode,
               "time_utc": now_utc().isoformat(), "tool_versions": tool_versions(),
               "junit": rel(junit), "results": collected}
    write_json(out / "summary.json", summary)
    publish_report(out, REPORTS / "smoke")
    print(f"smoke: {status} -> {rel(REPORTS / 'smoke')}")
    return 0 if status == PASS else 1


REPORT_KEEP = re.compile(r"(summary\.json|SUMMARY\.md|snapshot\.json|result\.json|erc\.json|drc\.json|"
                         r"connectivity\.json|\.net$|bom\.csv$|schematic\.json|pcb\.json|cross\.json|spice\.json|"
                         r"junit\.xml|\.log$|\.pdf$)")


LIGHT_SKIP = re.compile(r"(schematic|pcb|cross|spice)\.json$|\.pdf$")


def publish_report(src, dst, light=False):
    """Copy the machine-readable results (and PDFs) of a run into reports/.
    `light` drops the large analyzer JSON and PDFs (they stay under build/)."""
    if dst.exists():
        shutil.rmtree(dst)
    for p in sorted(src.rglob("*")):
        # snapshot/ and source/ (the git-archive input of --rev runs) are inputs, not results
        if p.is_file() and not p.is_symlink() and p.relative_to(src).parts[0] not in ("snapshot", "source") \
                and REPORT_KEEP.search(p.name) and "spice_work" not in p.parts \
                and not (p.suffix == ".pdf" and "kibot" in p.parts) \
                and not (light and LIGHT_SKIP.search(p.name)):  # kibot PDFs duplicate the native ones
            target = dst / p.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            if p.suffix == ".log":
                target.write_text("\n".join(l for l in p.read_text(errors="replace").splitlines()
                                            if not NOISE.search(l)) + "\n")
            else:
                shutil.copy2(p, target)


def baseline(projects, fill, worktree=True):
    """Committed HEAD of each project, plus fome-mc's working tree when it is dirty."""
    rc = 0
    index = []
    plans = [(name, "HEAD", name) for name in projects]
    if worktree and "fome-mc" in projects:
        plans.append(("fome-mc", None, "fome-mc-worktree"))
    for name, rev, label in plans:
        s = run_project(name, list(ALL_STEPS), fill, rev=rev, label=label)
        # The working tree may hold other agents' unfinished edits: publish it light.
        publish_report(REPO / s["run_dir"], REPORTS / "baseline" / label, light=rev is None)
        index.append((label, s))
        if s["status"] != PASS:
            rc = 1
    lines = ["# Read-only baseline", "",
             "Check status is about whether each native tool ran to completion; design",
             "findings are listed separately and are baseline facts, not setup failures.", "",
             "| Run | Source | Overall | ERC | DRC | Netlist | Export | Analyze |", "|---|---|---|---|---|---|---|---|"]
    for label, s in index:
        cells = [s["steps"].get(k, {}).get("status", "NOT_RUN") for k in ALL_STEPS]
        src = s["snapshot"].get("source", "working tree")
        if src == "working tree":
            src += f" @ {s['snapshot']['source_git_head'][:10]} + {len(s['snapshot']['source_dirty_files'])} uncommitted"
        lines.append(f"| [{label}]({label}/SUMMARY.md) | {src} | {s['status']} | " + " | ".join(cells) + " |")
    lines += ["", "Working-tree runs are published without analyzer JSON and PDFs; the full run",
              "stays under `build/runs/project/<label>/`. Re-run with `make baseline`."]
    (REPORTS / "baseline" / "INDEX.md").write_text("\n".join(lines) + "\n")
    return rc


# -------------------------------------------------------------------------- cli

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="check executables, versions, dependencies, libraries, capabilities")
    rp = sub.add_parser("run", help="run native checks/exports/analysis on a project snapshot")
    rp.add_argument("--project", default="fome-mc", choices=sorted(PINS["projects"]))
    rp.add_argument("--steps", default=",".join(ALL_STEPS), help=f"comma list from {','.join(ALL_STEPS)}")
    rp.add_argument("--fill", choices=["asis", "refill"], default="asis",
                    help="asis: check/export the saved zone fill; refill: refill+save the snapshot first")
    rp.add_argument("--rev", help="snapshot this git revision (git archive) instead of the working tree")
    sp = sub.add_parser("simulate", help="run a SPICE deck with ngspice and validate its .meas results")
    sp.add_argument("deck")
    sp.add_argument("--expect", help="JSON with expected measurement values and tolerances")
    sp.add_argument("--out", help="fresh output directory (default: build/runs/sim/<deck>/<stamp>)")
    sub.add_parser("smoke", help="run the toolchain integration checks on the fixture")
    bp = sub.add_parser("baseline", help="run all steps read-only on the real projects; publish reports")
    bp.add_argument("--projects", default="fome-mc,universal-112")
    bp.add_argument("--fill", choices=["asis", "refill"], default="asis")
    a = ap.parse_args(argv)
    if a.cmd == "doctor":
        return doctor()
    if a.cmd == "run":
        steps = [s.strip() for s in a.steps.split(",") if s.strip()]
        bad = [s for s in steps if s not in ALL_STEPS]
        if bad:
            ap.error(f"unknown steps: {bad}")
        label = f"{a.project}@{a.rev}" if a.rev else None
        return 0 if run_project(a.project, steps, a.fill, rev=a.rev, label=label)["status"] == PASS else 1
    if a.cmd == "simulate":
        return 0 if simulate(a.deck, a.expect, a.out)["status"] == PASS else 1
    if a.cmd == "smoke":
        return smoke()
    if a.cmd == "baseline":
        return baseline([p.strip() for p in a.projects.split(",")], a.fill)


if __name__ == "__main__":
    sys.exit(main())
