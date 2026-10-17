"""Routing integration checks (run with `make route-smoke`; `make route-update` runs them too).

They prove, on the route_demo fixture, that each backend completes the KiCad
round trip, that the candidate is graded by KiCad against the unchanged input
rules, and that routing and validation failures reach the caller. They are not
a routing-quality benchmark.

Each test writes a small JSON record to build/route-smoke/<test>.json;
`route.py smoke` collects them into reports/toolchain/routing/fixture/.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLCHAIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLCHAIN))
import eda  # noqa: E402
import route  # noqa: E402

FIXTURE = TOOLCHAIN / "fixtures" / "route_demo"
OUT = eda.BUILD / "route-smoke"
PROTECTED = {"tracks": 5, "vias": 2}  # the locked /SIG_B route in the fixture


def record(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(data, indent=2, default=str) + "\n")


def tree_hash(path):
    h = hashlib.sha256()
    for p in sorted(Path(path).rglob("*")):
        if p.is_file():
            h.update(p.relative_to(path).as_posix().encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def run(*args, timeout=900):
    r = subprocess.run([sys.executable, str(TOOLCHAIN / "route.py"), *args], capture_output=True, text=True,
                       timeout=timeout, cwd=eda.REPO)
    run_dir = None
    for line in r.stdout.splitlines():
        if line.startswith("[route] result: "):
            run_dir = eda.REPO / line.split()[2].rsplit("/result.json", 1)[0]
    result = json.loads((run_dir / "result.json").read_text()) if run_dir else None
    return r, run_dir, result


def summary(result):
    return {k: result[k] for k in ("backend", "settings", "scope", "unsupported", "routing", "exit_code")} | {
        "process": {k: result["process"].get(k) for k in ("status", "reasons", "exit_code", "runtime_s",
                                                         "backend_report", "bridge", "project_writeback")},
        "validation": result["validation"], "run_dir": result["run_dir"]}


@pytest.fixture(scope="session", autouse=True)
def source_untouched():
    """The authoritative fixture project must be byte-identical after every attempt."""
    before = tree_hash(FIXTURE)
    yield
    after = tree_hash(FIXTURE)
    record("source_untouched", {"fixture": eda.rel(FIXTURE), "before": before, "after": after})
    assert before == after, "a routing run modified the source project"


@pytest.fixture(scope="session")
def blocked_dir(tmp_path_factory):
    """The fixture with a keepout wall that cuts J2 off from every other part."""
    import pcbnew
    d = tmp_path_factory.mktemp("blocked") / "route_demo"
    shutil.copytree(FIXTURE, d, ignore=shutil.ignore_patterns("generate.py", "__pycache__"))
    board = pcbnew.LoadBoard(str(d / "route_demo.kicad_pcb"))
    wall = pcbnew.ZONE(board)
    wall.SetIsRuleArea(True)
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.B_Cu)
    wall.SetLayerSet(layers)
    wall.SetDoNotAllowTracks(True)
    wall.SetDoNotAllowVias(True)
    wall.SetDoNotAllowZoneFills(True)
    wall.SetDoNotAllowPads(False)
    wall.SetDoNotAllowFootprints(False)
    wall.SetZoneName("wall")
    o = wall.Outline()
    o.NewOutline()
    for x, y in [(138, 99), (140, 99), (140, 131), (138, 131)]:
        o.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    board.Add(wall)
    board.Save(str(d / "route_demo.kicad_pcb"))
    return d


def assert_clean_candidate(result, run_dir):
    assert result["process"]["status"] == route.PASS, result["process"]
    assert result["routing"]["status"] == route.COMPLETE, result["routing"]
    assert result["validation"]["status"] == route.PASS, result["validation"]["reasons"]
    assert all(v == route.PASS for v in result["validation"]["preservation"].values())
    assert result["validation"]["parity_performed"] is True
    assert result["validation"]["delivered_board_sha256"] == result["validation"]["validated_board_sha256"]
    assert result["exit_code"] == 0
    board = eda.REPO / result["candidate"]["board"]
    assert board.exists()
    # the candidate carries the input's own rules and schematic, byte for byte
    for name in ("route_demo.kicad_pro", "route_demo.kicad_dru", "route_demo.kicad_sch"):
        assert (board.parent / name).read_bytes() == (FIXTURE / name).read_bytes(), name
    checks = json.loads((run_dir / "validate" / "preservation.json").read_text())
    prot = next(c for c in checks if c["check"] == "protected_copper")
    assert f"{PROTECTED['tracks']} tracks and {PROTECTED['vias']} vias designated" in prot["detail"]


def test_route_doctor():
    r = subprocess.run([sys.executable, str(TOOLCHAIN / "route.py"), "doctor"], capture_output=True, text=True,
                       timeout=600, cwd=eda.REPO)
    doc = json.loads((eda.BUILD / "route-doctor" / "doctor.json").read_text())
    record("doctor", {"exit_code": r.returncode, "status": doc["status"], "versions": doc["versions"],
                      "checks": doc["checks"]})
    assert r.returncode == 0, r.stdout


def test_krt_custom_rule_failure_is_reported():
    """KRT cannot read the fixture's Power-to-signal .kicad_dru rule. Its candidate is
    complete, but KiCad grades it against that rule and the failure reaches the caller."""
    r, run_dir, result = run("run", "--backend", "krt", "--budget", "180", "--label", "smoke-krt-default")
    record("krt_default", summary(result))
    assert r.returncode == 3 and result["exit_code"] == 3
    assert result["routing"]["status"] == route.COMPLETE
    assert result["validation"]["status"] == route.FAIL
    new = json.loads((run_dir / "validate" / "new-findings.json").read_text())["violations"]
    assert new and all("power_to_signal_clearance" in v["description"] for v in new)
    assert any("power_to_signal_clearance" in u and "skipped" in u for u in result["unsupported"])


def test_krt_round_trip():
    """The retry the failure above suggests: Default class at 0.4 mm (tighter, never looser)."""
    r, run_dir, result = run("run", "--backend", "krt", "--budget", "180", "--default-clearance", "0.4",
                             "--label", "smoke-krt")
    record("krt_round_trip", summary(result))
    assert_clean_candidate(result, run_dir)
    rel = result["process"]["backend_report"]["relaxations"]
    assert rel["escalation_policy"] == "off" and rel["fab_tier"] == "standard" and not rel["narrowed"]
    argv = result["process"]["commands"][0]["argv"]
    assert "--no-fix-drc-settings" in argv and "--escalation" in argv


def test_freerouting_round_trip():
    r, run_dir, result = run("run", "--backend", "freerouting", "--budget", "180", "--clearance-margin", "0.01",
                             "--passes", "100", "--label", "smoke-freerouting")
    record("freerouting_round_trip", summary(result))
    assert_clean_candidate(result, run_dir)
    bridge = result["process"]["bridge"]
    assert bridge["import"]["placement_dropped"] is True
    assert [t["rule"] for t in bridge["export"]["dru_translated"]] == ["power_to_signal_clearance"]
    assert "Power" in (run_dir / "work" / "board.dsn").read_text().split("(class_class", 1)[1][:80]


def test_net_name_selection():
    r, run_dir, result = run("run", "--backend", "krt", "--budget", "180", "--nets", "/SIG_A*",
                             "--default-clearance", "0.4", "--label", "smoke-krt-nets")
    record("krt_net_selection", summary(result))
    assert result["scope"]["nets_list"] == ["/SIG_A", "/SIG_A_OUT"]
    assert result["routing"]["status"] == route.COMPLETE          # in scope
    assert result["routing"]["unconnected_total"] > 0             # other nets left alone
    assert result["validation"]["preservation"]["routing_scope"] == route.PASS
    assert result["exit_code"] == 0


def test_net_class_selection():
    r, run_dir, result = run("run", "--backend", "freerouting", "--budget", "180", "--netclass", "Power",
                             "--clearance-margin", "0.01", "--label", "smoke-freerouting-netclass")
    record("freerouting_netclass_selection", summary(result))
    assert result["scope"]["nets_list"] == ["/VIN", "GND"]
    assert "kicad_default__skip" in result["process"]["bridge"]["export"]["ignored_classes"]
    assert result["validation"]["preservation"]["routing_scope"] == route.PASS
    assert result["routing"]["status"] == route.COMPLETE
    assert result["routing"]["unconnected_total"] > 0


@pytest.mark.parametrize("backend", ["krt", "freerouting"])
def test_unroutable_board_fails(backend, blocked_dir):
    """A keepout wall makes J2 unreachable: the candidate must come back incomplete.
    (KRT's net rescue retries unroutable nets at length; switched off here so the
    attempt returns a candidate -- the budget test below covers the other path.)"""
    before = tree_hash(blocked_dir)
    extra = ["--backend-env", "KICAD_NET_RESCUE=0"] if backend == "krt" else []
    r, run_dir, result = run("run", "--backend", backend, "--budget", "180", "--dir", str(blocked_dir),
                             *extra, "--label", f"smoke-blocked-{backend}")
    record(f"blocked_{backend}", summary(result))
    assert tree_hash(blocked_dir) == before
    assert r.returncode in (2, 3) and result["exit_code"] == r.returncode
    assert result["routing"]["status"] == route.INCOMPLETE
    assert result["routing"]["unconnected_in_scope"] > 0
    assert result["validation"]["preservation"]["keepouts"] == route.PASS


def test_budget_overrun_is_a_process_failure(blocked_dir):
    """With rescue on, KRT keeps searching the unroutable nets past the budget:
    the wrapper stops it and reports a process failure, not a candidate."""
    r, run_dir, result = run("run", "--backend", "krt", "--budget", "15", "--dir", str(blocked_dir),
                             "--label", "smoke-budget-krt")
    record("budget_krt", summary(result))
    assert r.returncode == 1 and result["process"]["status"] == route.FAIL
    assert "budget" in " ".join(result["process"]["reasons"])
    assert result["routing"]["status"] == route.NOT_RUN and result["candidate"] is None


def test_validation_detects_tampering(tmp_path):
    """Edit a passing candidate the ways a router must not, then re-validate it."""
    import pcbnew
    src = eda.BUILD / "runs" / "route" / "route-fixture" / "smoke-krt" / "latest"
    run_dir = tmp_path / "run"
    shutil.copytree(src.resolve(), run_dir, symlinks=True)
    shutil.rmtree(run_dir / "validate")
    # rewrite paths in attempt.json relative to the copy (they are relative already)
    cand = run_dir / json.loads((run_dir / "attempt.json").read_text())["candidate_dir"]
    board_path = cand / "route_demo.kicad_pcb"
    board = pcbnew.LoadBoard(str(board_path))
    board.FindFootprintByReference("R1").Move(pcbnew.VECTOR2I(pcbnew.FromMM(0.5), 0))
    locked_via = next(t for t in board.GetTracks() if isinstance(t, pcbnew.PCB_VIA) and t.IsLocked())
    board.Remove(locked_via)
    vin = next(t for t in board.GetTracks() if not isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "/VIN")
    vin.SetWidth(pcbnew.FromMM(0.3))
    board.Save(str(board_path))
    pro = cand / "route_demo.kicad_pro"
    data = json.loads(pro.read_text())
    data["net_settings"]["classes"][0]["clearance"] = 0.1   # a router lowering a rule
    pro.write_text(json.dumps(data, indent=2))
    # the baseline report path is relative to the original run directory
    attempt = json.loads((run_dir / "attempt.json").read_text())
    attempt["baseline"]["report"] = str((src.resolve() / attempt["baseline"]["report"]).resolve())
    (run_dir / "attempt.json").write_text(json.dumps(attempt))
    r = subprocess.run([sys.executable, str(TOOLCHAIN / "route.py"), "validate", str(run_dir)],
                       capture_output=True, text=True, timeout=600, cwd=eda.REPO)
    out = sorted((run_dir / "revalidate").iterdir())[-1]
    res = json.loads((out / "result.json").read_text())
    record("tampering", {"exit_code": r.returncode, "validation": res["validation"], "routing": res["routing"]})
    assert r.returncode == 3
    p = res["validation"]["preservation"]
    for check in ("footprints", "protected_copper", "new_copper_netclass_geometry", "project_files"):
        assert p[check] == route.FAIL, check


def test_compare_same_and_different_inputs(blocked_dir):
    base = eda.BUILD / "runs" / "route" / "route-fixture"
    same = [str(base / "smoke-krt" / "latest"), str(base / "smoke-freerouting" / "latest")]
    r1 = subprocess.run([sys.executable, str(TOOLCHAIN / "route.py"), "compare", *same],
                        capture_output=True, text=True, cwd=eda.REPO)
    blocked = sorted((eda.BUILD / "runs" / "route" / "route_demo" / "smoke-blocked-krt").glob("2*"))[-1]
    r2 = subprocess.run([sys.executable, str(TOOLCHAIN / "route.py"), "compare", same[0], str(blocked)],
                        capture_output=True, text=True, cwd=eda.REPO)
    record("compare", {"same_input": {"exit_code": r1.returncode, "table": r1.stdout},
                       "different_input": {"exit_code": r2.returncode, "table": r2.stdout}})
    assert r1.returncode == 0 and "| krt" in r1.stdout and "| freerouting" in r1.stdout
    assert r2.returncode == 1 and "different inputs" in r2.stdout
