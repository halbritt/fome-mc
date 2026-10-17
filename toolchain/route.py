#!/usr/bin/env python3
"""Agent-facing PCB routing: run a routing backend on an isolated copy of a KiCad
project and grade the resulting native KiCad candidate against the unchanged
input constraints.

    route.py doctor                       readiness and capabilities of each backend
    route.py run --backend krt|freerouting [--project P | --dir D --board B.kicad_pcb]
                 [--nets PAT ...] [--netclass NAME ...] [--budget SECONDS]
                 [--protect locked|existing] [--label L] [--backend-arg ARG ...]
    route.py validate RUN_DIR             re-grade a candidate against its reference
    route.py compare RUN_DIR RUN_DIR ...  compare candidates routed from the same input
    route.py publish RUN_DIR              copy a run's structured evidence into reports/toolchain/routing/
    route.py update                       update both backends through their upstream channels
    route.py smoke                        integration tests on the routing fixture

Every attempt gets a fresh run directory under build/runs/route/<project>/:

    reference/<proj>/   untouched copy of the input project (board, .kicad_pro,
                        .kicad_dru, schematics, library tables, local libraries)
    candidate/<proj>/   the same project with the routed board; open it in KiCad
    work/               backend scratch: its own output files, DSN/SES, logs
    validate/           native DRC of the candidate, board facts, preservation diff
    result.json         everything below, machine-readable; RESULT.md for people

Three results are reported independently:

    process     did the backend run and hand back a board?         PASS | FAIL
    routing     are the in-scope connections complete?             COMPLETE | INCOMPLETE | NOT_RUN
    validation  does the candidate meet the unchanged constraints? PASS | FAIL | NOT_RUN

Validation always uses the input project's own .kicad_pro/.kicad_dru: whatever
the backend wrote to its project files is recorded and discarded. Zones are
refilled and saved into the candidate before native DRC (with schematic parity)
grades exactly the delivered file. Violations already present in the input
(graded the same way) are reported as pre-existing; only new ones fail.

Exit status: 0 complete and valid, 1 backend/process failure (no candidate),
2 candidate valid but routing incomplete, 3 candidate fails validation.
"""
import argparse
import collections
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eda  # noqa: E402  (shared snapshot, command and hashing helpers)

PASS, FAIL, NOT_RUN, UNSUPPORTED = eda.PASS, eda.FAIL, eda.NOT_RUN, eda.UNSUPPORTED
COMPLETE, INCOMPLETE = "COMPLETE", "INCOMPLETE"

TOOLCHAIN = eda.TOOLCHAIN
REPO = eda.REPO
BUILD = eda.BUILD
ROUTE_VENV = TOOLCHAIN / ".venv-route"
KRT_DIR = TOOLCHAIN / "vendor" / "krt"
FREEROUTING_DIR = TOOLCHAIN / "vendor" / "freerouting"
FIXTURE = TOOLCHAIN / "fixtures" / "route_demo"
BASELINE_CACHE = BUILD / "route-cache" / "baseline"
REPORTS = eda.REPORTS / "routing"
NM = 1_000_000  # nanometres per millimetre
NET_IN_ITEM = re.compile(r"\[([^\]]+)\]")


def log(msg):
    print(msg, flush=True)


def pcbnew_python():
    return eda.venv_python()  # toolchain venv: has KiCad's pcbnew via the shim


def route_python():
    return ROUTE_VENV / "bin" / "python"


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ------------------------------------------------------------------- the input

def resolve_input(args):
    """Project config in the same shape eda.make_snapshot expects."""
    if args.dir:
        d = Path(args.dir).resolve()
        boards = [args.board] if args.board else [p.name for p in d.glob("*.kicad_pcb")]
        if len(boards) != 1:
            sys.exit(f"{d}: pass --board (found {boards or 'no boards'})")
        board = boards[0]
        sch = Path(board).with_suffix(".kicad_sch").name
        return {"name": d.name, "path": d, "pcb": board,
                "schematic": sch if (d / sch).exists() else None, "library_dirs": {}}
    cfg = eda.project_config(args.project)
    if args.rev:
        cfg["rev"] = args.rev
    return cfg


def snapshot_input(cfg, run_dir):
    """reference/<proj>: eda's snapshot (sheets, rules, library tables, linked libraries)."""
    if cfg.get("schematic"):
        dst, manifest = eda.make_snapshot(cfg, run_dir)
        ref_root = run_dir / "reference"
        (run_dir / "snapshot").rename(ref_root)
        return ref_root / dst.name, manifest
    # No schematic: copy the board directory's KiCad files only (parity becomes UNSUPPORTED).
    dst = run_dir / "reference" / cfg["path"].name
    dst.mkdir(parents=True)
    for f in cfg["path"].iterdir():
        if f.is_file() and (f.suffix in eda.KICAD_SUFFIXES or f.name.endswith("-lib-table")):
            shutil.copy2(f, dst / f.name)
    return dst, {"project": cfg["name"], "source_dir": str(cfg["path"]), "files":
                 {p.name: eda.sha256(p) for p in sorted(dst.iterdir()) if p.is_file()}}


def input_fingerprint(manifest):
    """One hash over every input file, so candidates can be compared only within one input."""
    import hashlib
    h = hashlib.sha256()
    for name, digest in sorted(manifest.get("files", {}).items()):
        h.update(f"{name}\0{digest}\n".encode())
    return h.hexdigest()


def copy_project(src, dst):
    shutil.copytree(src, dst, symlinks=True)
    for stale in list(dst.glob("*.kicad_prl")) + list(dst.glob("fp-info-cache")):
        stale.unlink()


# --------------------------------------------------------------- nets and scope

def board_facts(board, out):
    """Engineering facts of a board via KiCad's own loader (route_facts.py)."""
    rec = eda.run_cmd([pcbnew_python(), TOOLCHAIN / "route_facts.py", board, out], board.parent,
                      out.with_suffix(".log"), timeout=1800)
    facts = load_json(out) if rec["exit_code"] == 0 else None
    return facts, eda.public(rec)


def select_nets(facts, patterns, netclasses):
    """Net names in scope. Patterns match net names (fnmatch, `!pat` excludes);
    net classes match the effective class KiCad resolved for each net. Exclusions
    alone (`--nets '!GND'`) start from every net."""
    names = sorted(facts["nets"])
    if not patterns and not netclasses:
        return names, {"mode": "all"}
    only_excludes = not netclasses and all(p.startswith("!") for p in patterns)
    chosen = set(names) if only_excludes else set()
    for pat in patterns or []:
        if pat.startswith("!"):
            continue
        chosen |= {n for n in names if fnmatch.fnmatchcase(n, pat)}
    for cls in netclasses or []:
        chosen |= {n for n in names if facts["nets"][n]["netclass"] == cls}
    for pat in patterns or []:
        if pat.startswith("!"):
            chosen -= {n for n in names if fnmatch.fnmatchcase(n, pat[1:])}
    return sorted(chosen), {"mode": "selected", "net_patterns": patterns or [], "netclasses": netclasses or []}


# ----------------------------------------------------------------- native DRC

def kicad_drc(board, out_dir, label, refill_and_save):
    """Refill+save (optional) then the grading DRC. Returns (report, info)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    info = {"commands": [], "reasons": []}
    if refill_and_save:
        before = eda.sha256(board)
        rec = eda.run_cmd(["kicad-cli", "pcb", "drc", "--refill-zones", "--save-board", "--format", "json",
                           "-o", out_dir / f"{label}-refill.json", board], board.parent,
                          out_dir / f"{label}-refill.log")
        info["commands"].append(eda.public(rec))
        if rec["exit_code"] != 0:
            info["reasons"].append(f"zone refill failed (exit {rec['exit_code']})")
            return None, info
        info["refill"] = {"board_sha256_before": before, "board_sha256_after": eda.sha256(board)}
    out = out_dir / f"{label}-drc.json"
    rec = eda.run_cmd(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity",
                       "--units", "mm", "-o", out, board], board.parent, out_dir / f"{label}-drc.log")
    info["commands"].append(eda.public(rec))
    info["board_sha256_checked"] = eda.sha256(board)
    if rec["exit_code"] != 0:
        info["reasons"].append(f"kicad-cli pcb drc exited {rec['exit_code']}")
        return None, info
    report = load_json(out)
    if report is None or not all(isinstance(report.get(k), list)
                                 for k in ("violations", "unconnected_items", "schematic_parity")):
        info["reasons"].append("DRC report missing or malformed")
        return None, info
    m = re.search(r"(?i)failed to fetch schematic netlist[^\n]*|parity tests require[^\n]*", rec["output"])
    info["parity_performed"] = m is None
    if m:
        info["parity_skip_message"] = m.group(0).strip()
    info["report"] = eda.rel(out)
    return report, info


def item_key(v):
    """Identity of a DRC finding that survives unrelated edits elsewhere on the board."""
    items = tuple(sorted((i.get("description", ""), round(i.get("pos", {}).get("x", 0), 3),
                          round(i.get("pos", {}).get("y", 0), 3)) for i in v.get("items", [])))
    return (v.get("type"), v.get("severity"), items)


def drc_delta(base, cand, kind):
    b = collections.Counter(item_key(v) for v in base[kind])
    new, resolved = [], []
    remaining = collections.Counter(b)
    for v in cand[kind]:
        k = item_key(v)
        if remaining[k] > 0:
            remaining[k] -= 1
        else:
            new.append(v)
    c = collections.Counter(item_key(v) for v in cand[kind])
    for v in base[kind]:
        k = item_key(v)
        if c[k] > 0:
            c[k] -= 1
        else:
            resolved.append(v)
    return new, resolved


def item_nets(v):
    return {n for i in v.get("items", []) for n in NET_IN_ITEM.findall(i.get("description", ""))}


def summarize_findings(items):
    return {"count": len(items), "by_type": eda.count_by(items, "type"),
            "by_severity": eda.count_by(items, "severity")}


def baseline_drc(reference, board_name, fingerprint):
    """Native DRC of the untouched input, graded exactly like candidates (refill first).
    Cached by input fingerprint: the same input always has the same baseline."""
    cache = BASELINE_CACHE / fingerprint
    report = load_json(cache / "baseline-drc.json")
    info = load_json(cache / "baseline-info.json")
    if report and info:
        info["cached"] = True
        return report, info
    work = BUILD / "route-cache" / "tmp" / f"{fingerprint}-{os.getpid()}"
    shutil.rmtree(work, ignore_errors=True)
    copy_project(reference, work / reference.name)
    report, info = kicad_drc(work / reference.name / board_name, work / "drc", "baseline", refill_and_save=True)
    if report is not None:
        cache.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work / "drc" / "baseline-drc.json", cache / "baseline-drc.json")
        info["report"] = eda.rel(cache / "baseline-drc.json")
        eda.write_json(cache / "baseline-info.json", info)
    shutil.rmtree(work, ignore_errors=True)
    info["cached"] = False
    return report, info


# ---------------------------------------------------------------- preservation

GEOMETRY_TOLERANCE_NM = 1000  # 1 um: Specctra round trips quantise coordinates


def geometry_points(t):
    return [t[k] for k in ("start", "mid", "end", "position") if k in t]


def same_copper(a, b, tol):
    keys = ("kind", "layer", "net") if "layer" in a else ("net", "layers", "via_type")
    if any(a.get(k) != b.get(k) for k in keys):
        return False
    for k in ("width", "diameter", "drill"):
        if k in a and abs(a[k] - b.get(k, -10**12)) > tol:
            return False
    pa, pb = geometry_points(a), geometry_points(b)
    if len(pa) != len(pb):
        return False
    return all(abs(p[0] - q[0]) <= tol and abs(p[1] - q[1]) <= tol for p, q in zip(pa, pb))


def match_copper(ref_items, cand_items, tol=GEOMETRY_TOLERANCE_NM):
    """Pair reference copper with candidate copper by geometry (UUIDs do not survive
    every backend). Returns (matched pairs, unmatched reference, unmatched candidate)."""
    pool = collections.defaultdict(list)
    for i, c in enumerate(cand_items):
        pool[(c.get("net"), c.get("layer") or tuple(c.get("layers", [])))].append(i)
    used, pairs, missing = set(), [], []
    for r in ref_items:
        hit = None
        for i in pool[(r.get("net"), r.get("layer") or tuple(r.get("layers", [])))]:
            if i not in used and same_copper(r, cand_items[i], 0):
                hit = i
                break
        if hit is None:
            for i in pool[(r.get("net"), r.get("layer") or tuple(r.get("layers", [])))]:
                if i not in used and same_copper(r, cand_items[i], tol):
                    hit = i
                    break
        if hit is None:
            missing.append(r)
        else:
            used.add(hit)
            pairs.append((r, cand_items[hit]))
    extra = [c for i, c in enumerate(cand_items) if i not in used]
    return pairs, missing, extra


def max_deviation(pairs):
    dev = 0
    for a, b in pairs:
        for p, q in zip(geometry_points(a), geometry_points(b)):
            dev = max(dev, abs(p[0] - q[0]), abs(p[1] - q[1]))
    return dev


def strip(rec, *keys):
    return {k: v for k, v in rec.items() if k not in keys}


def dict_diff(a, b, limit=20):
    out = []
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            out.append({"key": k, "reference": a.get(k), "candidate": b.get(k)})
            if len(out) >= limit:
                break
    return out


def project_file_hashes(project_dir, board_name):
    out = {}
    for p in sorted(project_dir.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        r = str(p.relative_to(project_dir))
        if r == board_name or p.suffix == ".kicad_prl" or p.name == "fp-info-cache" or "-backups" in r:
            continue
        out[r] = eda.sha256(p)
    return out


def preservation(ref, cand, ref_dir, cand_dir, board_name, protect, scope, restored=()):
    checks = []

    def check(name, ok, detail="", differences=None, status=None):
        checks.append({"check": name, "status": status or (PASS if ok else FAIL), "detail": detail,
                       "differences": differences or []})

    rf, cf = project_file_hashes(ref_dir, board_name), project_file_hashes(cand_dir, board_name)
    diffs = dict_diff(rf, cf)
    check("project_files", not diffs and not restored,
          "rules (.kicad_pro/.kicad_dru), schematics, library tables and local libraries are byte-identical "
          "to the input" + (f"; restored before grading: {', '.join(restored)}" if restored else ""),
          diffs + [{"key": r, "restored": True} for r in restored])
    check("board_outline", ref["outline"] == cand["outline"], f"{len(ref['outline'])} Edge.Cuts shapes",
          [] if ref["outline"] == cand["outline"] else [{"reference": len(ref["outline"]), "candidate": len(cand["outline"])}])
    layer_keys = ("copper_layer_count", "enabled_layers", "copper_layers")
    lr, lc = {k: ref[k] for k in layer_keys}, {k: cand[k] for k in layer_keys}
    check("layers", lr == lc, f"{ref['copper_layer_count']} copper layers", dict_diff(lr, lc))
    check("stackup", ref["stackup"] == cand["stackup"],
          "explicit stackup" if ref["stackup"] else "no explicit stackup in the input (KiCad default)")
    check("board_setup", ref["setup"] == cand["setup"], "board-file (setup) settings other than the stackup")
    nets_r = {n: v["netclass"] for n, v in ref["nets"].items()}
    nets_c = {n: v["netclass"] for n, v in cand["nets"].items()}
    check("nets_and_netclasses", nets_r == nets_c, f"{len(nets_r)} nets with their effective net classes",
          dict_diff(nets_r, nets_c))
    pads_r = {f"{r}.{p}": v["net"] for r, fp in ref["footprints"].items() for p, v in fp["pads"].items()}
    pads_c = {f"{r}.{p}": v["net"] for r, fp in cand["footprints"].items() for p, v in fp["pads"].items()}
    check("pad_connectivity", pads_r == pads_c, f"{len(pads_r)} pad-to-net assignments", dict_diff(pads_r, pads_c))
    fps_r = {r: strip(v, "value") for r, v in ref["footprints"].items()}
    fps_c = {r: strip(v, "value") for r, v in cand["footprints"].items()}
    moved = [{"footprint": r, "reference": {k: fps_r[r].get(k) for k in ("position", "orientation", "layer")},
              "candidate": {k: fps_c.get(r, {}).get(k) for k in ("position", "orientation", "layer")}}
             for r in sorted(set(fps_r) | set(fps_c)) if fps_r.get(r) != fps_c.get(r)]
    check("footprints", not moved, f"{len(fps_r)} footprints: library id, position, orientation, side, "
          "lock state and pad geometry", moved[:20])
    zr = [strip(z, "filled") for z in ref["zones"]]
    zc = [strip(z, "filled") for z in cand["zones"]]
    check("zones", zr == zc, f"{len(zr)} copper zone definitions (outline, net, layers, priority, clearance, "
          "thermal and fill settings; fill polygons are regenerated)",
          [] if zr == zc else [{"reference": len(zr), "candidate": len(zc)}])
    check("keepouts", ref["rule_areas"] == cand["rule_areas"], f"{len(ref['rule_areas'])} rule areas")
    check("copper_graphics", ref["copper_graphics"] == cand["copper_graphics"],
          f"{len(ref['copper_graphics'])} non-track copper graphics")

    # Protected copper: locked items always; every pre-existing item with --protect existing.
    def designated(item):
        return item["locked"] or protect == "existing"

    out = {}
    for kind in ("tracks", "vias"):
        rp = [strip(t, "uuid", "locked") for t in ref[kind] if designated(t)]
        ru = [strip(t, "uuid", "locked") for t in ref[kind] if not designated(t)]
        cand_items = [strip(t, "uuid", "locked") for t in cand[kind]]
        pairs, missing, rest = match_copper(rp, cand_items)
        pairs_u, missing_u, extra = match_copper(ru, rest)
        unlocked_after = sum(1 for t in ref[kind] if t["locked"]) - sum(
            1 for t in cand[kind] if t["locked"])
        out[kind] = {"protected": len(rp), "protected_missing": missing, "protected_max_deviation_nm":
                     max_deviation(pairs), "unprotected_existing": len(ru),
                     "unprotected_removed_or_changed": len(missing_u), "new": extra,
                     "lock_flags_lost": max(unlocked_after, 0)}
    missing = out["tracks"]["protected_missing"] + out["vias"]["protected_missing"]
    lost_locks = out["tracks"]["lock_flags_lost"] + out["vias"]["lock_flags_lost"]
    check("protected_copper", not missing,
          f"{out['tracks']['protected']} tracks and {out['vias']['protected']} vias designated "
          f"({'locked items' if protect == 'locked' else 'all pre-existing copper'}); max deviation "
          f"{max(out['tracks']['protected_max_deviation_nm'], out['vias']['protected_max_deviation_nm'])} nm"
          + (f"; {lost_locks} lock flags dropped" if lost_locks else "")
          + (f"; {len(missing)} missing or altered" if missing else ""), missing[:20])
    if protect == "locked":
        check("existing_unlocked_copper", True,
              f"{out['tracks']['unprotected_removed_or_changed']} of {out['tracks']['unprotected_existing']} "
              f"unlocked tracks and {out['vias']['unprotected_removed_or_changed']} of "
              f"{out['vias']['unprotected_existing']} unlocked vias removed or changed (allowed: not protected)",
              status=PASS)

    # New copper must meet the net class of its net and stay inside the routing scope.
    under, outside = [], []
    nets = cand["nets"]
    tol = GEOMETRY_TOLERANCE_NM  # Specctra/KiCad quantisation, e.g. a 0.29972 mm drill read back as 0.299
    for t in out["tracks"]["new"]:
        nc = nets.get(t["net"], {})
        if nc.get("track_width") and t["width"] < nc["track_width"] - tol:
            under.append({"item": "track", "net": t["net"], "netclass": nc["netclass"], "layer": t["layer"],
                          "width_mm": t["width"] / NM, "required_mm": nc["track_width"] / NM,
                          "start_mm": [c / NM for c in t["start"]]})
        if t["net"] and t["net"] not in scope:
            outside.append({"item": "track", "net": t["net"]})
    for v in out["vias"]["new"]:
        nc = nets.get(v["net"], {})
        if (nc.get("via_diameter") and v["diameter"] < nc["via_diameter"] - tol) or \
                (nc.get("via_drill") and v["drill"] < nc["via_drill"] - tol):
            under.append({"item": "via", "net": v["net"], "netclass": nc["netclass"],
                          "diameter_mm": v["diameter"] / NM, "drill_mm": v["drill"] / NM,
                          "required_mm": [nc.get("via_diameter", 0) / NM, nc.get("via_drill", 0) / NM],
                          "position_mm": [c / NM for c in v["position"]]})
        if v["net"] and v["net"] not in scope:
            outside.append({"item": "via", "net": v["net"]})
    check("new_copper_netclass_geometry", not under,
          f"{len(out['tracks']['new'])} new tracks and {len(out['vias']['new'])} new vias checked against "
          f"their net class width / via diameter / drill (1 um quantisation tolerance)"
          + (f"; {len(under)} below" if under else ""), under[:20])
    outside_nets = sorted({o["net"] for o in outside})
    check("routing_scope", not outside, f"new copper only on the {len(scope)} in-scope nets"
          + (f"; outside scope: {', '.join(outside_nets[:10])}" if outside else ""), outside[:20])

    stats = route_stats(out["tracks"]["new"], out["vias"]["new"])
    stats["removed_existing_tracks"] = out["tracks"]["unprotected_removed_or_changed"] + len(out["tracks"]["protected_missing"])
    stats["removed_existing_vias"] = out["vias"]["unprotected_removed_or_changed"] + len(out["vias"]["protected_missing"])
    return checks, stats


def route_stats(tracks, vias):
    length = collections.Counter()
    for t in tracks:
        (x1, y1), (x2, y2) = t["start"], t["end"]
        length[t["layer"]] += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / NM
    return {"new_tracks": len(tracks), "new_vias": len(vias),
            "new_track_length_mm": round(sum(length.values()), 3),
            "new_track_length_mm_by_layer": {k: round(v, 3) for k, v in sorted(length.items())},
            "new_copper_nets": len({t["net"] for t in tracks} | {v["net"] for v in vias})}


# ------------------------------------------------------------------ validation

def validate(run_dir, out_dir=None, origin=None):
    """Grade run_dir/candidate against run_dir/reference. Re-runnable: an agent may
    edit the candidate and validate it again into a fresh directory. With origin (an
    earlier run whose candidate this run's input descends from through --dir steps),
    grade against the origin's input instead: its rules, baseline, facts and
    protection, with the union of every step's net scope, so a chain of attempts is
    judged against the original design."""
    attempt = load_json(run_dir / "attempt.json")
    if attempt is None:
        sys.exit(f"{run_dir}: not a routing run (attempt.json missing)")
    cand_dir = run_dir / attempt["candidate_dir"]
    scope = set(attempt["scope"]["nets"])
    chain = []
    if origin is not None:
        chain, step = [eda.rel(run_dir)], (run_dir, attempt)
        while step[0].resolve() != origin.resolve():
            src = Path(step[1]["source"].get("source_dir") or "/").resolve()
            prev = src.parent.parent
            prev_attempt = load_json(prev / "attempt.json")
            if prev_attempt is None or (prev / prev_attempt["candidate_dir"]).resolve() != src:
                sys.exit(f"{eda.rel(step[0])}: input is not a routing candidate, so it does not descend "
                         f"from {eda.rel(origin)}")
            if prev_attempt["board"] != attempt["board"]:
                sys.exit(f"{eda.rel(prev)}: board {prev_attempt['board']} is not {attempt['board']}")
            step = (prev, prev_attempt)
            chain.append(eda.rel(prev))
            scope |= set(prev_attempt["scope"]["nets"])
        attempt, run_dir = step[1], step[0]
    out_dir = out_dir or run_dir / "validate"
    out_dir.mkdir(parents=True, exist_ok=False)
    board_name = attempt["board"]
    ref_dir = run_dir / attempt["reference_dir"]
    board = cand_dir / board_name
    v = {"status": None, "reasons": [], "dir": eda.rel(out_dir)}
    if chain:
        v["chain"] = chain  # this run back to the origin; scope is the union of the steps' scopes
    if not board.exists():
        v.update(status=NOT_RUN, reasons=["no candidate board"])
        return v, {"status": NOT_RUN, "reasons": ["no candidate board"]}

    base = load_json(run_dir / attempt["baseline"]["report"]) if attempt["baseline"].get("report") else None
    # Grade against the input's own rules: project files that differ from the
    # reference are restored first, and the difference itself fails validation.
    restored = []
    ref_files, cand_files = project_file_hashes(ref_dir, board_name), project_file_hashes(cand_dir, board_name)
    for rel_path in sorted(set(ref_files) | set(cand_files)):
        if ref_files.get(rel_path) != cand_files.get(rel_path):
            restored.append(rel_path)
            target = cand_dir / rel_path
            if rel_path in ref_files:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ref_dir / rel_path, target)
            else:
                target.unlink()
    if restored:
        v["reasons"].append(f"candidate project files differed from the input and were restored before "
                            f"grading: {', '.join(restored)}")
    v["restored_project_files"] = restored
    cand, info = kicad_drc(board, out_dir, "candidate", refill_and_save=True)
    v["drc_commands"] = info["commands"]
    v["delivered_board_sha256"] = eda.sha256(board)
    v["validated_board_sha256"] = info.get("board_sha256_checked")
    if cand is None:
        v.update(status=FAIL, reasons=info["reasons"])
        return v, {"status": NOT_RUN, "reasons": ["candidate DRC did not run"]}
    if v["delivered_board_sha256"] != v["validated_board_sha256"]:
        v["reasons"].append("delivered board differs from the board DRC graded")
    if not info["parity_performed"] and attempt.get("schematic"):
        v["reasons"].append(f"schematic parity was not performed: {info.get('parity_skip_message')}")
    v["parity_performed"] = info["parity_performed"] if attempt.get("schematic") else None

    unconnected = cand["unconnected_items"]
    in_scope = [u for u in unconnected if item_nets(u) & scope]
    routing = {"status": COMPLETE if not in_scope else INCOMPLETE,
               "unconnected_in_scope": len(in_scope), "unconnected_total": len(unconnected),
               "baseline_unconnected_total": len(base["unconnected_items"]) if base else None,
               "unrouted_nets": sorted({n for u in in_scope for n in item_nets(u) & scope})}

    drc = {"violations_total": len(cand["violations"]), "parity_total": len(cand["schematic_parity"])}
    if base is not None:
        new_v, fixed_v = drc_delta(base, cand, "violations")
        new_p, fixed_p = drc_delta(base, cand, "schematic_parity")
        drc.update(new_violations=summarize_findings(new_v), preexisting_violations=len(cand["violations"]) - len(new_v),
                   resolved_violations=len(fixed_v), new_parity=summarize_findings(new_p),
                   resolved_parity=len(fixed_p))
        eda.write_json(out_dir / "new-findings.json", {"violations": new_v, "schematic_parity": new_p,
                                                        "resolved_violations": fixed_v})
        if new_v:
            v["reasons"].append(f"{len(new_v)} new DRC violations: " +
                                ", ".join(f"{k} {n}" for k, n in eda.count_by(new_v, 'type').items()))
        if new_p:
            v["reasons"].append(f"{len(new_p)} new schematic parity issues")
    else:
        v["reasons"].append("no baseline DRC: cannot separate new from pre-existing findings")
    v["drc"] = drc

    ref_facts = load_json(run_dir / attempt["reference_facts"])
    cand_facts, rec = board_facts(board, out_dir / "candidate-facts.json")
    if cand_facts is None or ref_facts is None:
        v["reasons"].append("board facts could not be extracted")
        v["status"] = FAIL
        return v, routing
    checks, stats = preservation(ref_facts, cand_facts, ref_dir, cand_dir, board_name,
                                 attempt["settings"]["protect"], scope, restored)
    eda.write_json(out_dir / "preservation.json", checks)
    v["preservation"] = {c["check"]: c["status"] for c in checks}
    for c in checks:
        if c["status"] == FAIL:
            v["reasons"].append(f"preservation {c['check']}: {c['detail']}")
    v["status"] = FAIL if v["reasons"] else PASS
    routing["stats"] = stats
    return v, routing


def overall_exit(process, routing, validation):
    if process["status"] != PASS:
        return 1
    if validation["status"] != PASS:
        return 3
    if routing["status"] != COMPLETE:
        return 2
    return 0


# ------------------------------------------------------------------- attempts

def run_attempt(args):
    eda.ensure_kicad_config()
    backend = BACKENDS[args.backend]
    cfg = resolve_input(args)
    project = cfg["name"]
    run_dir = eda.new_run_dir("route", f"{project}/{args.label or args.backend}")
    started = time.monotonic()
    log(f"[route] {args.backend} on {project} -> {eda.rel(run_dir)}")
    ref_dir, manifest = snapshot_input(cfg, run_dir)
    board_name = cfg["pcb"]
    fingerprint = input_fingerprint(manifest)
    (run_dir / "validate").mkdir()
    ref_facts, rec = board_facts(ref_dir / board_name, run_dir / "validate" / "reference-facts.json")
    (run_dir / "validate").rename(run_dir / "facts")
    if ref_facts is None:
        sys.exit(f"could not read the input board: see {rec['log']}")
    scope, scope_info = select_nets(ref_facts, args.nets, args.netclass)
    if not scope:
        sys.exit("the net selection matches no nets")
    settings = {"backend": args.backend, "budget_s": args.budget, "protect": args.protect,
                "max_iterations": args.max_iterations, "passes": args.passes,
                "default_clearance_mm": args.default_clearance, "clearance_margin_mm": args.clearance_margin,
                "backend_args": args.backend_arg or [], "backend_env": dict(e.split("=", 1) for e in args.backend_env or []),
                **scope_info}
    log(f"[route] scope: {scope_info['mode']} ({len(scope)} of {len(ref_facts['nets'])} nets)")

    log("[route] baseline: native DRC of the untouched input (refilled)")
    base, base_info = baseline_drc(ref_dir, board_name, fingerprint)
    attempt = {
        "backend": args.backend, "project": project, "board": board_name,
        "schematic": cfg.get("schematic"), "input_fingerprint": fingerprint,
        "source": {k: manifest.get(k) for k in ("source_dir", "source", "source_git_head", "source_dirty_files")},
        "reference_dir": str(ref_dir.relative_to(run_dir)),
        "candidate_dir": str((run_dir / "candidate" / ref_dir.name).relative_to(run_dir)),
        "reference_facts": "facts/reference-facts.json",
        "baseline": {"report": os.path.relpath(REPO / base_info["report"], run_dir) if base else None,
                     "cached": base_info.get("cached"), "reasons": base_info["reasons"]},
        "scope": {"nets": scope, **scope_info},
        "settings": settings,
    }
    eda.write_json(run_dir / "attempt.json", attempt)

    unsupported = backend["unsupported"](ref_facts, ref_dir, settings)
    work = run_dir / "work"
    copy_project(ref_dir, work / "input" / ref_dir.name)
    log(f"[route] routing with {args.backend} (budget {args.budget}s)")
    t0 = time.monotonic()
    proc = backend["route"](work, work / "input" / ref_dir.name / board_name, scope, ref_facts, settings)
    proc["runtime_s"] = round(time.monotonic() - t0, 3)
    unsupported += [f"backend reported: {u}" for u in proc.pop("unsupported_reported", [])]
    for u in (proc.get("bridge") or {}).get("export", {}).get("dru_untranslated", []):
        unsupported.append(f"custom rule '{u['rule']}' not given to the backend: {u['reason']}")
    log(f"[route] process: {proc['status']}" + (f" ({'; '.join(proc['reasons'])})" if proc["reasons"] else ""))

    cand_dir = run_dir / attempt["candidate_dir"]
    if proc["status"] == PASS:
        copy_project(ref_dir, cand_dir)
        shutil.copyfile(proc["output_board"], cand_dir / board_name)
        log("[route] validating the candidate (refill, DRC + parity, preservation)")
        validation, routing = validate(run_dir)
    else:
        validation = {"status": NOT_RUN, "reasons": ["backend produced no candidate"]}
        routing = {"status": NOT_RUN, "reasons": ["backend produced no candidate"]}
    result = {
        "kind": "route",
        "backend": {"name": args.backend, **backend["version"]()},
        "input": {"project": project, "board": board_name, "fingerprint": fingerprint,
                  **attempt["source"], "baseline": attempt["baseline"]},
        "settings": settings,
        "scope": {"mode": scope_info["mode"], "nets": len(scope), "nets_list": scope if len(scope) <= 50 else None},
        "unsupported": unsupported,
        "process": {k: v for k, v in proc.items() if k not in ("output_board",)},
        "routing": routing,
        "validation": validation,
        "candidate": {"dir": eda.rel(cand_dir), "board": eda.rel(cand_dir / board_name)} if proc["status"] == PASS else None,
        "run_dir": eda.rel(run_dir),
        "runtime_s": round(time.monotonic() - started, 3),
        "tool_versions": {"kicad-cli": eda.tool_versions()["kicad-cli"]},
        "finished_utc": eda.now_utc().isoformat(),
    }
    result["exit_code"] = overall_exit(proc, routing, validation)
    eda.write_json(run_dir / "result.json", result)
    (run_dir / "RESULT.md").write_text(render_result(result))
    print_result(result)
    return result


def print_result(r):
    rt = r["routing"]
    log(f"[route] routing: {rt['status']}" + (f" ({rt.get('unconnected_in_scope')} unconnected in scope)"
                                               if rt["status"] == INCOMPLETE else ""))
    val = r["validation"]
    log(f"[route] validation: {val['status']}" + (f" ({'; '.join(val['reasons'][:4])})" if val["reasons"] else ""))
    if r.get("candidate"):
        log(f"[route] candidate: {r['candidate']['board']}")
    log(f"[route] result: {r['run_dir']}/result.json  (exit {r['exit_code']})")


def render_result(r):
    lines = [f"# Routing attempt: {r['backend']['name']} on {r['input']['project']}", "",
             f"- Backend: {r['backend']['name']} {r['backend'].get('version')} ({r['backend'].get('build', '')})",
             f"- Input: `{r['input']['board']}` from {r['input'].get('source')} @ {r['input'].get('source_git_head')}"
             f" (fingerprint {r['input']['fingerprint'][:16]})",
             f"- Scope: {r['scope']['mode']}, {r['scope']['nets']} nets; protect: {r['settings']['protect']};"
             f" budget {r['settings']['budget_s']} s",
             f"- Candidate: `{r['candidate']['board']}`" if r.get("candidate") else "- Candidate: none",
             "", "| Result | Status | Detail |", "|---|---|---|",
             f"| process | {r['process']['status']} | exit {r['process'].get('exit_code')}, "
             f"{r['process'].get('runtime_s')} s{'; ' + '; '.join(r['process']['reasons']) if r['process']['reasons'] else ''} |",
             f"| routing | {r['routing']['status']} | {r['routing'].get('unconnected_in_scope', '-')} unconnected in scope, "
             f"{r['routing'].get('unconnected_total', '-')} total (input: {r['routing'].get('baseline_unconnected_total', '-')}) |",
             f"| validation | {r['validation']['status']} | {'; '.join(r['validation'].get('reasons', [])) or 'no new findings'} |",
             ""]
    if r["validation"].get("preservation"):
        lines += ["| Preservation check | Status |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in r["validation"]["preservation"].items()]
        lines.append("")
    if r["validation"].get("drc"):
        lines += ["Native DRC (original rules and severities):", "",
                  "```json", json.dumps(r["validation"]["drc"], indent=1), "```", ""]
    if r["unsupported"]:
        lines += ["Unsupported or approximated by this backend:", ""] + [f"- {u}" for u in r["unsupported"]] + [""]
    if r["routing"].get("stats"):
        lines += ["Route statistics:", "", "```json", json.dumps(r["routing"]["stats"], indent=1), "```"]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ processes

def run_budgeted(argv, cwd, log_path, budget, env_extra=None, stop_file=None, grace=None):
    """Run a backend with a wall-clock budget. At the budget the stop file (if the
    backend supports one) asks for a clean stop; after a grace period it is killed."""
    env = eda.tool_env()
    env.update(env_extra or {})
    grace = grace if grace is not None else max(30, budget // 5)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    rec = {"argv": [str(a) for a in argv], "cwd": eda.rel(cwd), "log": eda.rel(log_path),
           "env": {k: v for k, v in (env_extra or {}).items()}, "budget_s": budget}
    start = time.monotonic()
    with open(log_path, "wb") as out:
        try:
            proc = subprocess.Popen([str(a) for a in argv], cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT)
        except FileNotFoundError as e:
            rec.update(exit_code=None, error="executable_not_found", detail=str(e), duration_s=0)
            return rec
        try:
            proc.wait(timeout=budget)
        except subprocess.TimeoutExpired:
            rec["budget_reached"] = True
            if stop_file:
                Path(stop_file).touch()
                rec["stop_requested"] = True
            try:
                proc.wait(timeout=grace if stop_file else 5)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                rec["killed"] = True
    rec["exit_code"] = proc.returncode
    rec["duration_s"] = round(time.monotonic() - start, 3)
    rec["output_tail"] = log_path.read_text(errors="replace")[-4000:]
    return rec


def tagged_json(text, tag):
    """Last `TAG: {json}` line a backend printed."""
    found = None
    for line in text.splitlines():
        if line.startswith(tag + ":"):
            try:
                found = json.loads(line[len(tag) + 1:])
            except json.JSONDecodeError:
                pass
    return found


# ------------------------------------------------------------- KRT backend

# Every relaxation, fallback and writeback KRT offers is switched off: a failed
# connection must stay failed rather than be delivered below the input's rules.
KRT_FLAGS = [
    "--escalation", "off",          # no fab/board escalation ladders, net rescue or terminal escalation
    "--fab-tier", "standard",       # the fab floor is a hard floor
    "--strict-sizes",               # exit 3 if anything it tracked shipped below its requirement
    "--no-power-tap-neckdown",      # wide nets do not neck down into pads
    "--no-fix-drc-settings",        # no .kicad_pro writeback (the wrapper restores the originals anyway)
]
KRT_PROTECT_EXISTING_FLAGS = ["--keep-input-copper", "--no-stub-layer-swap"]
KRT_ENV = {
    "KICAD_INRUN_FLOOR_SYNC": "0",     # no mid-run floor writes to the output .kicad_pro
    "KICAD_TERMINAL_ESCALATION": "0",
    "KICAD_IMPEDANCE_NECKDOWN": "0",
    "KICAD_RESCUE_CAP_MOVE": "0",      # never move passives to rescue a net
    "KICAD_DYNAMIC_ITERATIONS": "0",   # --max-iterations is a hard cap
    "KICAD_CLI": "/usr/bin/kicad-cli",
}
KRT_PROTECT_EXISTING_ENV = {"KICAD_RIP_PREEXISTING": "0", "KICAD_FINALIZE_RIP": "0"}
KRT_REQUIRED_FLAGS = KRT_FLAGS[::2] + KRT_PROTECT_EXISTING_FLAGS + ["--json-out", "--nets", "--output",
                                                                     "--max-iterations"]


def krt_version():
    v = {"version": (KRT_DIR / "VERSION").read_text().strip() if (KRT_DIR / "VERSION").exists() else None,
         "build": eda.git(KRT_DIR, "describe", "--tags", "--always", "--dirty"),
         "commit": eda.git(KRT_DIR, "rev-parse", "HEAD"), "source": "https://github.com/drandyhaas/KiCadRoutingTools"}
    r = subprocess.run([str(route_python()), "-c", "import sys; sys.path.insert(0, 'rust_router'); "
                        "import grid_router; print(grid_router.__version__)"],
                       cwd=KRT_DIR, capture_output=True, text=True)
    v["rust_router"] = r.stdout.strip() if r.returncode == 0 else None
    return v


def krt_unsupported(facts, ref_dir, settings):
    notes = []
    if (ref_dir / Path(facts["board"]).with_suffix(".kicad_dru").name).exists():
        notes.append("KRT reads only a subset of .kicad_dru custom rules; every rule is still graded by KiCad DRC")
    if any(v["via_type"] != "through" for v in facts["vias"]):
        notes.append("blind/buried/micro vias are present; KRT routes with through vias")
    if any(t["kind"] == "arc" for t in facts["tracks"]):
        notes.append("existing arc tracks are kept as obstacles; KRT routes octilinear segments")
    if settings.get("clearance_margin_mm"):
        notes.append("--clearance-margin is not supported by KRT and was not applied (use --default-clearance)")
    notes.append("KRT moves copper gr_text and net-less copper graphics to silkscreen (not switchable on the CLI); "
                 "the copper_graphics preservation check reports it")
    notes.append("KRT's cleanup may neck wide new segments near foreign pads without a flag; the "
                 "new_copper_netclass_geometry check reports any new copper below its net class")
    return notes


def krt_route(work, board, scope, facts, settings):
    out_dir = work / "krt-out"
    out_dir.mkdir(parents=True)
    output = out_dir / board.name
    summary = out_dir / "summary.json"
    stop = work / "STOP"
    argv = [route_python(), KRT_DIR / "py_router" / "route.py", board, "--output", output,
            *KRT_FLAGS, "--json-out", summary]
    env = dict(KRT_ENV, KICAD_STOP_FILE=str(stop))
    if settings["protect"] == "existing":
        argv += KRT_PROTECT_EXISTING_FLAGS
        env.update(KRT_PROTECT_EXISTING_ENV)
    if settings.get("max_iterations"):
        argv += ["--max-iterations", str(settings["max_iterations"])]
    if settings.get("default_clearance_mm"):
        default = max((n["clearance"] for n in facts["nets"].values() if n["netclass"] == "Default"
                       and n["clearance"]), default=0) / NM
        # KRT's --clearance sets the Default class; never below the input's own value
        argv += ["--clearance", f"{max(settings['default_clearance_mm'], default):g}"]
    if settings["mode"] == "all":
        argv += ["--nets", "*"]
    else:
        argv += ["--nets", *scope]
    argv += settings["backend_args"]
    env.update(settings.get("backend_env") or {})
    locks = None
    if settings["protect"] == "existing":
        # KRT never touches locked copper, but its rescue path reworks unlocked input
        # copper despite --keep-input-copper: lock it for the run, restore flags after.
        lr = eda.run_cmd([pcbnew_python(), TOOLCHAIN / "route_locks.py", "lock", board, work / "locks.json"],
                         work, work / "lock-existing.log", timeout=600)
        locks = {"lock": tagged_json(lr["output"], "LOCKS_JSON"), "lock_exit": lr["exit_code"]}
        if lr["exit_code"] != 0:
            return {"status": FAIL, "reasons": [f"could not lock existing copper (see {lr['log']})"],
                    "commands": [eda.public(lr)], "exit_code": None, "output_board": None}
    rec = run_budgeted(argv, work, work / "krt.log", settings["budget_s"], env, stop_file=stop)
    text = Path(work / "krt.log").read_text(errors="replace")
    report = load_json(summary) or tagged_json(text, "JSON_SUMMARY")
    proc = {"status": PASS, "reasons": [], "exit_code": rec.get("exit_code"), "commands": [rec],
            "backend_report": None, "output_board": output,
            # rules KRT says it did not apply; KiCad DRC still grades them
            "unsupported_reported": sorted(set(re.findall(r"\.kicad_dru: rule [^\n]*skipped[^\n]*", text)))}
    if report:
        dr = report.get("design_rules", {})
        proc["backend_report"] = {k: report.get(k) for k in (
            "successful", "failed", "failed_single", "open_single", "failed_multipoint", "multipoint_deficit",
            "pad_pairs_connected", "pad_pairs_total", "total_vias", "total_iterations", "total_time",
            "protected_skipped", "scope")}
        proc["backend_report"]["relaxations"] = {k: dr.get(k) for k in (
            "escalation_policy", "fab_tier", "narrowed", "fab_tier_escalations", "min_delivered", "unsupported_rules")}
        proc["backend_report"]["improvement_gate"] = tagged_json(text, "JSON_IMPROVEMENT_GATE")
        proc["backend_report"]["project_writes"] = tagged_json(text, "PROJECT_WRITES_JSON")
    if rec.get("error"):
        proc.update(status=FAIL, reasons=[f"KRT could not start: {rec.get('detail')}"])
    elif rec.get("killed"):
        last = [l for l in text.splitlines() if l.strip()][-1:] or [""]
        proc.update(status=FAIL, reasons=[f"KRT exceeded the {settings['budget_s']} s budget, did not stop at the "
                                          f"stop file, and was killed (last output: {last[0].strip()[:120]!r}); "
                                          "retry with a larger --budget or --backend-env KICAD_NET_RESCUE=0"])
    elif rec["exit_code"] == 3:
        proc["reasons"].append("KRT --strict-sizes: it reports delivering geometry below a requirement "
                               "(candidate kept for grading)")
    elif rec["exit_code"] != 0:
        proc.update(status=FAIL, reasons=[f"KRT exited {rec['exit_code']}"])
    if rec.get("stop_requested") and not rec.get("killed"):
        proc["reasons"].append("budget reached: KRT stopped early and wrote the board as it stood")
    if proc["status"] == PASS and not output.exists():
        proc.update(status=FAIL, reasons=proc["reasons"] + ["KRT wrote no output board"])
    if locks is not None and proc["status"] == PASS:
        rr = eda.run_cmd([pcbnew_python(), TOOLCHAIN / "route_locks.py", "restore", output, work / "locks.json"],
                         work, work / "restore-locks.log", timeout=600)
        proc["commands"].append(eda.public(rr))
        locks["restore"] = tagged_json(rr["output"], "LOCKS_JSON")
        if rr["exit_code"] != 0:
            proc.update(status=FAIL, reasons=proc["reasons"] + [f"could not restore lock flags (see {rr['log']})"])
    proc["existing_copper_locks"] = locks
    # What KRT wrote beside its output is recorded, never used.
    writeback = []
    for sib in sorted(out_dir.glob("*")):
        if sib.suffix in (".kicad_pro", ".kicad_dru", ".kicad_prl"):
            orig = board.with_suffix(sib.suffix)
            same = orig.exists() and json_or_text(orig) == json_or_text(sib)
            writeback.append({"file": sib.name, "identical_to_input": same})
    proc["project_writeback"] = writeback
    return proc


def json_or_text(path):
    try:
        data = json.loads(path.read_text())
        data.get("meta", {}).pop("filename", None)
        return data
    except (json.JSONDecodeError, AttributeError):
        return path.read_text()


# ------------------------------------------------------ Freerouting backend

FREEROUTING_REPO = "freerouting/freerouting"
# Freerouting checks GitHub for new versions on every start and has no switch for
# it; a dead proxy keeps routing runs offline. Analytics are disabled with -da.
OFFLINE_ENV = {"HTTPS_PROXY": "http://127.0.0.1:9", "HTTP_PROXY": "http://127.0.0.1:9",
               "FREEROUTING__USAGE_AND_DIAGNOSTIC_DATA__DISABLE_ANALYTICS": "true"}


def freerouting_installed():
    cur = FREEROUTING_DIR / "current"
    rel = load_json(cur / "release.json") if cur.exists() else None
    if not rel:
        return None
    rel["jar"] = cur / rel["asset"]
    return rel if rel["jar"].exists() else None


def jar_java_major(jar):
    """Java feature release the jar was built for (its manifest's Created-By)."""
    import zipfile
    with zipfile.ZipFile(jar) as z:
        mf = z.read("META-INF/MANIFEST.MF").decode(errors="replace")
    m = re.search(r"Created-By:\s*(\d+)", mf) or re.search(r"Build-Jdk-Spec:\s*(\d+)", mf)
    return int(m.group(1)) if m else None


def find_java(min_major):
    """Newest installed JVM that satisfies min_major (the system default is left alone)."""
    best = None
    for java in sorted(Path("/usr/lib/jvm").glob("*/bin/java")) + [Path(shutil.which("java") or "/nonexistent")]:
        if not java.exists():
            continue
        r = subprocess.run([str(java), "-version"], capture_output=True, text=True)
        m = re.search(r'version "(\d+)', r.stderr)
        if m and int(m.group(1)) >= (min_major or 0) and (best is None or int(m.group(1)) > best[1]):
            best = (java.resolve(), int(m.group(1)))
    return best


def freerouting_version():
    rel = freerouting_installed()
    if not rel:
        return {"version": None, "build": "not installed"}
    need = jar_java_major(rel["jar"])
    java = find_java(need)
    return {"version": rel["tag"], "build": f"{rel['asset']} {rel.get('build_revision', '')}".strip(),
            "sha256": rel["sha256"], "java": f"{java[0]} ({java[1]})" if java else None,
            "java_required": need, "source": f"https://github.com/{FREEROUTING_REPO}"}


def freerouting_unsupported(facts, ref_dir, settings):
    notes = ["Freerouting never rips up pre-existing copper (KiCad exports it as fixed/protected); "
             "--protect locked behaves like --protect existing",
             "Specctra carries per-class width/clearance/via only: custom .kicad_dru rules, diff pairs and "
             "length tuning are not exported; KiCad DRC grades them",
             "rule areas export only their no-tracks/no-vias restrictions; zones export as plane outlines"]
    dru = ref_dir / Path(facts["board"]).with_suffix(".kicad_dru").name
    if dru.exists() and "(rule" in dru.read_text():
        notes.append(f"{dru.name}: net-class-to-net-class clearance rules are translated to Specctra "
                     "class_class rules; any other custom rule is listed as untranslated below")
    if any(t["kind"] == "arc" for t in facts["tracks"]):
        notes.append("existing arc tracks export as straight chords; unlocked arcs come back as segments")
    if any(v["via_type"] != "through" for v in facts["vias"]):
        notes.append("blind/buried/micro vias are present; Freerouting places through vias only")
    return notes


def freerouting_route(work, board, scope, facts, settings):
    proc = {"status": PASS, "reasons": [], "commands": [], "output_board": None, "exit_code": None}
    rel = freerouting_installed()
    if not rel:
        proc.update(status=FAIL, reasons=["Freerouting is not installed: run `make route-update`"])
        return proc
    need = jar_java_major(rel["jar"])
    java = find_java(need)
    if not java:
        proc.update(status=FAIL, reasons=[f"Freerouting {rel['tag']} needs Java {need}+; none installed "
                                          f"(apt install openjdk-{need}-jre-headless)"])
        return proc
    dsn, ses, res = work / "board.dsn", work / "board.ses", work / "freerouting-result.json"
    export = [pcbnew_python(), TOOLCHAIN / "route_specctra.py", "export", board, dsn]
    if settings["mode"] != "all":
        skip = work / "skip-nets.json"
        skip.write_text(json.dumps(sorted(set(facts["nets"]) - set(scope))))
        export += ["--skip-nets", skip]
    dru = board.with_suffix(".kicad_dru")
    if dru.exists():
        export += ["--dru", dru]
    if settings.get("clearance_margin_mm"):
        export += ["--clearance-margin", f"{settings['clearance_margin_mm'] * 1000:g}"]
    if settings.get("default_clearance_mm"):
        export += ["--default-clearance", f"{settings['default_clearance_mm'] * 1000:g}"]
    rec = eda.run_cmd(export, work, work / "export-dsn.log", timeout=600)
    proc["commands"].append(eda.public(rec))
    bridge = tagged_json(rec["output"], "BRIDGE_JSON") if rec["exit_code"] == 0 else None
    if not bridge or not dsn.exists():
        proc.update(status=FAIL, reasons=[f"DSN export failed (exit {rec['exit_code']}); see {rec['log']}"])
        return proc
    budget = settings["budget_s"]
    argv = [java[0], "-Djava.awt.headless=true", "-jar", rel["jar"], "-de", dsn, "-do", ses,
            "--gui.enabled=false", "-da", "--api_server.enabled=false",
            f"--user_data_path={work / 'freerouting-userdata'}", f"--router.result_json={res}",
            # no narrowing of traces into pins: deliver the net class width or nothing.
            # The fanout stage necks down to 3/4, 3/5 or 1/2 of the class width
            # regardless of automatic_neckdown (FoundConnectionInserter), so it is off too.
            "--router.automatic_neckdown=false", "--router.fanout.enabled=false",
            f"--router.job_timeout={budget // 3600:02d}:{budget % 3600 // 60:02d}:{budget % 60:02d}"]
    if settings.get("passes"):
        argv.append(f"--router.autorouter.max_passes={settings['passes']}")
    if bridge["ignored_classes"]:
        argv.append("--router.autorouter.ignore_net_classes=" + ",".join(bridge["ignored_classes"]))
    argv += settings["backend_args"]
    rec = run_budgeted(argv, work, work / "freerouting.log", budget + 60,
                       dict(OFFLINE_ENV, **(settings.get("backend_env") or {})), grace=30)
    proc["commands"].append(rec)
    proc["exit_code"] = rec.get("exit_code")
    report = load_json(res)
    if report:
        stats = report.get("board_statistics") or {}
        proc["backend_report"] = {
            "final_state": report.get("final_state"), "exit_code": report.get("exit_code"),
            "output_written": report.get("output_written"),
            "incomplete_connections": (stats.get("connections") or {}).get("incomplete_count"),
            "clearance_violations": (stats.get("clearance_violations") or {}).get("total_count")}
    unrouted = re.findall(r"The following connections could not be routed[^\n]*(?:\n[ \t]+[^\n]*)*",
                          Path(work / "freerouting.log").read_text(errors="replace"))
    if unrouted:  # the last report is the final state
        proc.setdefault("backend_report", {})["unrouted_log"] = unrouted[-1][:2000]
    if rec.get("error"):
        proc.update(status=FAIL, reasons=[f"Freerouting could not start: {rec.get('detail')}"])
        return proc
    if rec.get("killed"):
        proc.update(status=FAIL, reasons=[f"Freerouting exceeded the budget and was killed"])
        return proc
    if rec["exit_code"] != 0 or not ses.exists():
        proc.update(status=FAIL, reasons=[f"Freerouting exited {rec['exit_code']} without a session file"])
        return proc
    out = work / "freerouting-out" / board.name
    out.parent.mkdir()
    rec = eda.run_cmd([pcbnew_python(), TOOLCHAIN / "route_specctra.py", "import", board, ses, out], work,
                      work / "import-ses.log", timeout=600)
    proc["commands"].append(eda.public(rec))
    if rec["exit_code"] != 0 or not out.exists():
        proc.update(status=FAIL, reasons=[f"SES import failed (exit {rec['exit_code']}); see {rec['log']}"])
        return proc
    proc["bridge"] = {"export": {k: v for k, v in bridge.items() if k != "dsn"},
                      "import": tagged_json(rec["output"], "BRIDGE_JSON")}
    proc["output_board"] = out
    proc["project_writeback"] = []
    return proc


# --------------------------------------------------------- install / update

def github_latest(repo):
    import urllib.request
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "fome-mc-route"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def update_krt(steps):
    """KRT: latest GitHub release (it ships the matching prebuilt Rust module), deps by their floors."""
    tag = github_latest("drandyhaas/KiCadRoutingTools")["tag_name"]
    if not (KRT_DIR / ".git").exists():
        steps.append(eda.run_cmd(["git", "clone", "https://github.com/drandyhaas/KiCadRoutingTools.git", KRT_DIR],
                                 TOOLCHAIN, BUILD / "route-update" / "krt-clone.log"))
    steps.append(eda.run_cmd(["git", "fetch", "--tags", "--prune", "origin"], KRT_DIR,
                             BUILD / "route-update" / "krt-fetch.log"))
    steps.append(eda.run_cmd(["git", "checkout", "--detach", tag], KRT_DIR, BUILD / "route-update" / "krt-checkout.log"))
    if not route_python().exists():
        steps.append(eda.run_cmd(["uv", "venv", ROUTE_VENV, "--python", "/usr/bin/python3"], TOOLCHAIN,
                                 BUILD / "route-update" / "venv.log"))
    env_cmd = ["env", f"VIRTUAL_ENV={ROUTE_VENV}", "uv", "pip", "install", "--upgrade", "-r", KRT_DIR / "requirements.txt"]
    steps.append(eda.run_cmd(env_cmd, TOOLCHAIN, BUILD / "route-update" / "krt-deps.log"))
    steps.append(eda.run_cmd([route_python(), "build_router.py", "--tag", tag], KRT_DIR,
                             BUILD / "route-update" / "krt-build-router.log"))
    steps.append(eda.run_cmd([route_python(), "py_router/startup_checks.py"], KRT_DIR,
                             BUILD / "route-update" / "krt-startup-checks.log"))
    return tag


def update_freerouting(steps):
    """Freerouting: the latest release's executable jar, verified against GitHub's asset digest."""
    import hashlib
    import urllib.request
    rel = github_latest(FREEROUTING_REPO)
    tag = rel["tag_name"]
    assets = [a for a in rel["assets"] if re.fullmatch(r"freerouting-[\d.]+\.jar", a["name"])]
    if not assets:
        raise RuntimeError(f"release {tag} has no executable jar asset")
    asset = assets[0]
    dest_dir = FREEROUTING_DIR / tag
    jar = dest_dir / asset["name"]
    if not jar.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        tmp = jar.with_suffix(".part")
        with urllib.request.urlopen(asset["browser_download_url"], timeout=300) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
        want = (asset.get("digest") or "").removeprefix("sha256:")
        if want and want != digest:
            tmp.unlink()
            raise RuntimeError(f"{asset['name']}: sha256 {digest} does not match GitHub's digest {want}")
        tmp.rename(jar)
    import zipfile
    with zipfile.ZipFile(jar) as z:
        mf = z.read("META-INF/MANIFEST.MF").decode(errors="replace")
    build = re.search(r"Build-Revision:\s*(\S+)", mf)
    eda.write_json(dest_dir / "release.json", {
        "tag": tag, "asset": asset["name"], "sha256": eda.sha256(jar), "published_at": rel.get("published_at"),
        "build_revision": build.group(1) if build else None, "url": asset["browser_download_url"]})
    cur = FREEROUTING_DIR / "current"
    if cur.is_symlink() or cur.exists():
        cur.unlink()
    cur.symlink_to(tag)
    for old in FREEROUTING_DIR.iterdir():  # keep the current release only
        if old.is_dir() and not old.is_symlink() and old.name != tag:
            shutil.rmtree(old)
    return tag


def update():
    (BUILD / "route-update").mkdir(parents=True, exist_ok=True)
    before = {"krt": krt_version() if KRT_DIR.exists() else None, "freerouting": freerouting_version()}
    steps, errors = [], []
    for name, fn in (("krt", update_krt), ("freerouting", update_freerouting)):
        try:
            log(f"[update] {name}: latest release {fn(steps)}")
        except Exception as e:  # report and continue with the other backend
            errors.append(f"{name}: {e}")
            log(f"[update] {name}: FAILED: {e}")
    failed = [s for s in steps if s.get("exit_code") != 0]
    for s in failed:
        errors.append(f"command failed: {' '.join(s['argv'])} (exit {s.get('exit_code')}, log {s['log']})")
    after = {"krt": krt_version(), "freerouting": freerouting_version()}
    if after["freerouting"].get("version") and not after["freerouting"].get("java"):
        errors.append(f"Freerouting needs Java {after['freerouting']['java_required']}+: "
                      f"sudo apt install openjdk-{after['freerouting']['java_required']}-jre-headless")
    record = {"when": eda.now_utc().isoformat(), "before": before, "after": after,
              "commands": [eda.public(s) for s in steps], "errors": errors}
    eda.write_json(BUILD / "route-update" / "update.json", record)
    for name in ("krt", "freerouting"):
        b, a = (before[name] or {}).get("version"), after[name].get("version")
        log(f"[update] {name}: {b} -> {a}")
    if errors:
        log("[update] errors:\n  " + "\n  ".join(errors))
        return 1
    r = subprocess.run([sys.executable, str(TOOLCHAIN / "sync_skills.py")], capture_output=True, text=True)
    log(f"[update] {r.stdout.strip() or r.stderr.strip()}")  # krt-* skills follow the installed KRT
    log("[update] re-running the routing integration checks")
    return smoke()


# ------------------------------------------------------------------- doctor

def doctor():
    checks = []

    def add(name, status, detail="", required=True):
        checks.append({"check": name, "status": status, "detail": detail, "required": required})

    kv = eda.tool_versions()["kicad-cli"]
    add("kicad-cli", PASS if kv else FAIL, kv or "not found")
    r = subprocess.run(["kicad-cli", "pcb", "drc", "--help"], capture_output=True, text=True)
    for flag in ("--refill-zones", "--save-board", "--schematic-parity", "--severity-all", "--format"):
        add(f"kicad-cli pcb drc {flag}", PASS if flag in r.stdout else FAIL, "native grading")
    r = subprocess.run(["kicad-cli", "pcb", "export", "--help"], capture_output=True, text=True)
    add("kicad-cli DSN export", PASS if "dsn" in r.stdout.lower() else UNSUPPORTED,
        "not in kicad-cli: the Freerouting bridge uses pcbnew SWIG instead", required=False)
    r = subprocess.run([str(pcbnew_python()), "-c", "import pcbnew; print(pcbnew.GetBuildVersion()); "
                        "print(callable(pcbnew.ExportSpecctraDSN) and callable(pcbnew.ImportSpecctraSES))"],
                       capture_output=True, text=True, env=eda.tool_env())
    lines = r.stdout.split()
    add("pcbnew SWIG (facts, Specctra bridge)", PASS if r.returncode == 0 and lines[-1:] == ["True"] else FAIL,
        " ".join(lines[:1]) or r.stderr[-200:])

    # KRT
    v = krt_version() if KRT_DIR.exists() else {}
    add("KRT checkout", PASS if v.get("version") else FAIL, f"{v.get('version')} {v.get('build')}")
    add("KRT routing venv", PASS if route_python().exists() else FAIL, eda.rel(ROUTE_VENV))
    add("KRT Rust router module", PASS if v.get("rust_router") and v.get("rust_router") == v.get("version") else FAIL,
        f"grid_router {v.get('rust_router')} (checkout {v.get('version')})")
    if route_python().exists() and KRT_DIR.exists():
        r = subprocess.run([str(route_python()), "py_router/startup_checks.py"], cwd=KRT_DIR,
                           capture_output=True, text=True)
        add("KRT startup checks", PASS if r.returncode == 0 else FAIL, (r.stdout + r.stderr).strip().splitlines()[-1:])
        r = subprocess.run([str(route_python()), "py_router/route.py", "--help"], cwd=KRT_DIR,
                           capture_output=True, text=True)
        missing = [f for f in KRT_REQUIRED_FLAGS if f not in r.stdout]
        add("KRT controls used by the adapter", PASS if not missing else FAIL,
            "all present" if not missing else f"missing: {missing} (upstream changed; update the adapter)")
        latest = None
        try:
            latest = github_latest("drandyhaas/KiCadRoutingTools")["tag_name"]
        except Exception as e:
            add("KRT latest release", NOT_RUN, f"GitHub unreachable: {e}", required=False)
        if latest:
            add("KRT latest release", PASS if latest.lstrip("v") == v.get("version") else NOT_RUN,
                f"latest {latest}, installed {v.get('version')}" +
                ("" if latest.lstrip("v") == v.get("version") else ": run `make route-update`"), required=False)

    # Freerouting
    fv = freerouting_version()
    add("Freerouting jar", PASS if fv.get("version") else FAIL, f"{fv.get('version')} {fv.get('build')}")
    add("Java for Freerouting", PASS if fv.get("java") else FAIL,
        f"{fv.get('java')} (jar built for Java {fv.get('java_required')})")
    if fv.get("java"):
        rel = freerouting_installed()
        java = fv["java"].split(" (")[0]
        r = subprocess.run([java, "-Djava.awt.headless=true", "-jar", str(rel["jar"]), "--help"],
                           capture_output=True, text=True, env=dict(os.environ, **OFFLINE_ENV), timeout=120)
        out = r.stdout + r.stderr
        add("Freerouting headless CLI", PASS if r.returncode == 0 and "-de" in out and "-do" in out else FAIL,
            re.search(r"Freerouting v\S+[^\n]*", out).group(0) if re.search(r"Freerouting v\S+", out) else out[-200:])
        try:
            latest = github_latest(FREEROUTING_REPO)["tag_name"]
            add("Freerouting latest release", PASS if latest == fv["version"] else NOT_RUN,
                f"latest {latest}, installed {fv['version']}" +
                ("" if latest == fv["version"] else ": run `make route-update`"), required=False)
        except Exception as e:
            add("Freerouting latest release", NOT_RUN, f"GitHub unreachable: {e}", required=False)

    capabilities = {
        "krt": {"interface": "CLI (py_router/route.py), headless, no KiCad editor needed",
                "net_selection": "names (fnmatch, !exclude); classes expanded by the wrapper",
                "budget": "wall clock via KICAD_STOP_FILE + kill; --max-iterations",
                "relaxation_controls": "--escalation off --fab-tier standard --strict-sizes --no-power-tap-neckdown "
                                       "plus KICAD_* knobs (see route.py KRT_FLAGS/KRT_ENV)",
                "project_writeback": "disabled (--no-fix-drc-settings, KICAD_INRUN_FLOOR_SYNC=0); "
                                     "originals restored anyway",
                "existing_copper": "locked copper never touched; with --protect existing the wrapper locks all "
                                           "input copper for the run and restores the flags afterwards"},
        "freerouting": {"interface": "executable jar, headless (-de/-do), via KiCad pcbnew Specctra bridge",
                        "net_selection": "by DSN class: out-of-scope nets moved to ignored copies of their class",
                        "budget": "--router.job_timeout + kill; --router.autorouter.max_passes",
                        "relaxation_controls": "--router.automatic_neckdown=false",
                        "project_writeback": "none (Specctra session only)",
                        "existing_copper": "all pre-existing copper frozen; SES import keeps locked copper and "
                                           "re-creates unlocked copper from the session"},
    }
    required_fail = [c for c in checks if c["required"] and c["status"] != PASS]
    status = FAIL if required_fail else PASS
    out = BUILD / "route-doctor" / "doctor.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    eda.write_json(out, {"status": status, "checks": checks, "capabilities": capabilities,
                         "versions": {"krt": v, "freerouting": fv}})
    for c in checks:
        log(f"{c['status']:<12} {c['check']:<44} {c['detail'] if isinstance(c['detail'], str) else ' '.join(c['detail'])}")
    log(f"\nroute doctor: {status} ({len(checks)} checks) -> {eda.rel(out)}")
    return 0 if status == PASS else 1


# ------------------------------------------------------------------- compare

def compare(run_dirs):
    rows, fps = [], set()
    for d in run_dirs:
        r = load_json(Path(d) / "result.json")
        if r is None:
            sys.exit(f"{d}: no result.json")
        fps.add(r["input"]["fingerprint"])
        st = r["routing"].get("stats", {})
        rows.append({"run": r["run_dir"], "backend": f"{r['backend']['name']} {r['backend'].get('version')}",
                     "exit": r["exit_code"], "process": r["process"]["status"], "routing": r["routing"]["status"],
                     "unconnected": r["routing"].get("unconnected_in_scope"),
                     "validation": r["validation"]["status"],
                     "new_violations": (r["validation"].get("drc", {}).get("new_violations") or {}).get("count"),
                     "new_parity": (r["validation"].get("drc", {}).get("new_parity") or {}).get("count"),
                     "preservation_fail": [k for k, v in (r["validation"].get("preservation") or {}).items() if v != PASS],
                     "new_vias": st.get("new_vias"), "new_length_mm": st.get("new_track_length_mm"),
                     "backend_s": r["process"].get("runtime_s"), "scope": r["scope"]["mode"],
                     "args": r["settings"].get("backend_args")})
    same = len(fps) == 1
    out = {"same_input": same, "input_fingerprints": sorted(fps), "candidates": rows}
    dest = BUILD / "runs" / "route" / "compare" / eda.now_utc().strftime("%Y%m%dT%H%M%S.%fZ")
    dest.mkdir(parents=True)
    eda.write_json(dest / "compare.json", out)
    hdr = ["backend", "exit", "routing", "unconnected", "validation", "new_violations", "new_vias",
           "new_length_mm", "backend_s"]
    log("| " + " | ".join(hdr) + " | run |")
    log("|" + "---|" * (len(hdr) + 1))
    for row in rows:
        log("| " + " | ".join(str(row[h]) for h in hdr) + f" | {row['run']} |")
    if not same:
        log("WARNING: these candidates come from different inputs; the comparison is not like for like")
    log(f"[compare] {eda.rel(dest)}/compare.json")
    return 0 if same else 1


# --------------------------------------------------------------------- smoke

PUBLISH_FROM_RUN = ["result.json", "RESULT.md", "attempt.json", "validate/preservation.json",
                    "validate/new-findings.json", "validate/candidate-drc.json"]


def publish_run(run_dir, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for name in PUBLISH_FROM_RUN:
        src = run_dir / name
        if src.exists():
            (dest / Path(name).name).write_bytes(src.read_bytes())


def smoke():
    out = BUILD / "route-smoke"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    junit = out / "junit.xml"
    r = subprocess.run([str(eda.venv_python()), "-m", "pytest", "-v", "-p", "no:cacheprovider",
                        f"--junitxml={junit}", str(TOOLCHAIN / "tests" / "test_routing.py")],
                       cwd=REPO, env=eda.tool_env())
    status = PASS if r.returncode == 0 else FAIL
    records = {p.stem: load_json(p) for p in sorted(out.glob("*.json")) if p.name != "summary.json"}
    summary = {"kind": "route-smoke", "status": status, "pytest_exit_code": r.returncode,
               "time_utc": eda.now_utc().isoformat(),
               "versions": {"krt": krt_version(), "freerouting": freerouting_version(),
                            "kicad-cli": eda.tool_versions()["kicad-cli"]},
               "junit": eda.rel(junit), "tests": sorted(records)}
    eda.write_json(out / "summary.json", summary)
    dest = REPORTS / "fixture"
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    for p in [*out.glob("*.json"), junit]:
        (dest / p.name).write_bytes(p.read_bytes())
    for rec in records.values():
        run_dir = (rec or {}).get("run_dir")
        if run_dir:
            publish_run(REPO / run_dir, dest / "runs" / Path(run_dir).parent.name)
    log(f"route smoke: {status} -> {eda.rel(dest)}")
    return 0 if status == PASS else 1


# ------------------------------------------------------------------------ CLI

BACKENDS = {
    "krt": {"route": krt_route, "version": krt_version, "unsupported": krt_unsupported},
    "freerouting": {"route": freerouting_route, "version": freerouting_version,
                    "unsupported": freerouting_unsupported},
}


def cmd_validate(args):
    run_dir = Path(args.run_dir).resolve()
    origin = Path(args.against).resolve() if args.against else None
    out = run_dir / ("revalidate-origin" if origin else "revalidate") / eda.now_utc().strftime("%Y%m%dT%H%M%S.%fZ")
    validation, routing = validate(run_dir, out, origin)
    result = load_json(run_dir / "result.json") or {}
    proc = result.get("process", {"status": PASS})
    rec = {"kind": "route-validate", "run_dir": eda.rel(run_dir), "against": eda.rel(origin) if origin else None,
           "routing": routing, "validation": validation,
           "exit_code": overall_exit(proc, routing, validation)}
    eda.write_json(out / "result.json", rec)
    log(f"[validate] routing: {routing['status']}  validation: {validation['status']}"
        + (f" ({'; '.join(validation['reasons'][:4])})" if validation.get("reasons") else ""))
    log(f"[validate] {eda.rel(out)}/result.json  (exit {rec['exit_code']})")
    return rec["exit_code"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="routing readiness and capabilities")
    rp = sub.add_parser("run", help="route an isolated copy and grade the candidate")
    rp.add_argument("--backend", required=True, choices=sorted(BACKENDS))
    src = rp.add_mutually_exclusive_group()
    src.add_argument("--project", default="route-fixture", help="project from toolchain/versions.toml")
    src.add_argument("--dir", help="any KiCad project directory instead of a configured project")
    rp.add_argument("--board", help="board file name inside --dir")
    rp.add_argument("--rev", help="route a committed git revision of --project")
    rp.add_argument("--nets", nargs="+", metavar="PATTERN",
                    help="net-NAME selection: fnmatch patterns, !PATTERN excludes (default: all nets)")
    rp.add_argument("--netclass", nargs="+", metavar="CLASS",
                    help="net-CLASS selection: nets whose effective KiCad net class is CLASS")
    rp.add_argument("--budget", type=int, default=300, help="wall-clock seconds for the backend (default 300)")
    rp.add_argument("--max-iterations", type=int, help="KRT A* iteration cap per search")
    rp.add_argument("--passes", type=int, help="Freerouting maximum routing passes")
    rp.add_argument("--default-clearance", type=float, metavar="MM",
                    help="route the Default net class with at least MM clearance (tighten only; same meaning "
                         "for both backends). Use when the input has custom rules a backend cannot read")
    rp.add_argument("--clearance-margin", type=float, metavar="MM",
                    help="Freerouting only: add MM to every clearance it plans with (tighten only)")
    rp.add_argument("--protect", choices=["existing", "locked"], default="existing",
                    help="existing (default): all input copper must survive; locked: only locked copper, "
                         "the backend may rip up unlocked copper")
    rp.add_argument("--label", help="run directory name under build/runs/route/<project>/")
    rp.add_argument("--backend-arg", action="append", metavar="ARG",
                    help="extra argument passed to the backend verbatim (recorded; grading is unaffected)")
    rp.add_argument("--backend-env", action="append", metavar="KEY=VALUE",
                    help="extra environment variable for the backend, e.g. a KRT KICAD_* knob (recorded)")
    vp = sub.add_parser("validate", help="re-grade a run's candidate against its reference")
    vp.add_argument("run_dir")
    vp.add_argument("--against", metavar="ORIGIN_RUN",
                    help="grade against an earlier run's input (the start of a --dir chain) instead of this run's")
    cp = sub.add_parser("compare", help="compare candidates routed from the same input")
    cp.add_argument("run_dirs", nargs="+")
    pp = sub.add_parser("publish", help="copy a run's structured evidence to reports/toolchain/routing/")
    pp.add_argument("run_dir")
    sub.add_parser("update", help="update both backends through their upstream channels, then smoke")
    sub.add_parser("smoke", help="routing integration tests on the fixture")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        if a.rev and a.dir:
            ap.error("--rev applies to --project")
        a.backend_arg = a.backend_arg or []
        if any("=" not in e for e in a.backend_env or []):
            ap.error("--backend-env takes KEY=VALUE")
        return run_attempt(a)["exit_code"]
    if a.cmd == "validate":
        return cmd_validate(a)
    if a.cmd == "publish":
        run_dir = Path(a.run_dir).resolve()
        r = load_json(run_dir / "result.json")
        if r is None:
            sys.exit(f"{run_dir}: no result.json")
        dest = REPORTS / r["input"]["project"] / run_dir.parent.name
        shutil.rmtree(dest, ignore_errors=True)
        publish_run(run_dir, dest)
        log(f"[publish] {eda.rel(dest)} (candidate stays in {r['run_dir']})")
        return 0
    return {"doctor": lambda: doctor(), "compare": lambda: compare(a.run_dirs),
            "update": lambda: update(), "smoke": lambda: smoke()}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
