"""Toolchain integration checks (run with `make smoke`).

These prove that each tool actually executes and that the wrappers notice when
a tool skips its work. They are not an electrical test suite for the ECU.

Every test writes a small JSON record to build/smoke/<test>.json; `eda.py smoke`
collects them into reports/toolchain/smoke/summary.json.
"""
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

TOOLCHAIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLCHAIN))
import eda  # noqa: E402

FIXTURE = TOOLCHAIN / "fixtures" / "rc_filter"
SIM = FIXTURE / "sim"
SMOKE = eda.BUILD / "smoke"
R, C = 10e3, 100e-9           # fixture values, also asserted from the netlist below
TAU = R * C


def record(name, data):
    SMOKE.mkdir(parents=True, exist_ok=True)
    (SMOKE / f"{name}.json").write_text(json.dumps(data, indent=2, default=str) + "\n")


def remove_block(text, head, must_contain):
    """Remove the first top-level-ish s-expression `(head ...)` containing a marker."""
    start = 0
    while True:
        i = text.find(f"({head}", start)
        if i < 0:
            raise AssertionError(f"no ({head} ...) block containing {must_contain!r}")
        depth = 0
        for j in range(i, len(text)):
            depth += {"(": 1, ")": -1}.get(text[j], 0)
            if depth == 0:
                break
        if must_contain in text[i:j + 1]:
            return text[:i] + text[j + 1:]
        start = j + 1


def remove_all_blocks(text, head):
    while f"({head}" in text:
        i = text.find(f"({head}")
        depth = 0
        for j in range(i, len(text)):
            depth += {"(": 1, ")": -1}.get(text[j], 0)
            if depth == 0:
                break
        text = text[:i] + text[j + 1:]
    return text


def disposable(tmp_path, name):
    d = tmp_path / name
    shutil.copytree(FIXTURE, d, ignore=shutil.ignore_patterns("sim", "generate.py", "__pycache__"))
    return {"name": f"fixture-{name}", "path": d, "schematic": "rc_filter.kicad_sch",
            "pcb": "rc_filter.kicad_pcb", "description": f"disposable fixture copy: {name}"}


@pytest.fixture(scope="module")
def fixture_run():
    return eda.run_project("fixture", list(eda.ALL_STEPS))


def load_step(summary, step):
    return json.loads((eda.REPO / summary["run_dir"] / step / "result.json").read_text())


# ------------------------------------------------------------------ doctor

def test_doctor_passes():
    r = subprocess.run([sys.executable, str(TOOLCHAIN / "eda.py"), "doctor"], capture_output=True, text=True)
    doc = json.loads((eda.BUILD / "doctor" / "doctor.json").read_text())
    record("doctor", {"status": doc["status"], "failures": [c for c in doc["checks"] if c["status"] == "FAIL"]})
    assert r.returncode == 0, r.stdout[-3000:]


# ------------------------------------------------------- native KiCad checks

def test_fixture_pipeline_passes(fixture_run):
    record("fixture_pipeline", fixture_run)
    assert fixture_run["status"] == "PASS", fixture_run["steps"]
    for step in eda.ALL_STEPS:
        assert fixture_run["steps"][step]["status"] == "PASS", (step, fixture_run["steps"][step])


def test_native_erc_drc_clean_on_fixture(fixture_run):
    erc = fixture_run["steps"]["erc"]
    drc = fixture_run["steps"]["drc"]
    assert erc["design_clean"] and erc["findings"]["sheets_checked"] == 1
    assert drc["design_clean"]
    assert drc["findings"]["schematic_parity"] == 0


def test_netlist_has_expected_components_and_connectivity(fixture_run):
    conn = json.loads((eda.REPO / fixture_run["run_dir"] / "netlist" / "connectivity.json").read_text())
    record("fixture_connectivity", conn)
    assert conn["components"] == {"C1": "100n", "J1": "Conn_01x03", "R1": "10k"}
    assert conn["nets"] == {
        "/IN": ["J1.1", "R1.1"],
        "/OUT": ["C1.1", "J1.2", "R1.2"],
        "GND": ["C1.2", "J1.3"],
    }


def test_exports_and_kibot_bundle(fixture_run):
    exp = load_step(fixture_run, "export")
    outputs = list(exp["outputs"])
    record("fixture_export", {"artifacts": exp["findings"]["artifacts"], "bom": exp.get("bom"),
                              "schematic_pdf_refs_found": exp.get("schematic_pdf_refs_found"),
                              "outputs": outputs})
    assert exp["schematic_pdf_refs_found"] == "3/3"
    assert exp["bom"]["netlist_refs_not_in_bom"] == [] and exp["bom"]["bom_refs_not_in_netlist"] == []
    for pattern in eda.KIBOT_EXPECTED.values():
        regex = re.compile(re.escape(pattern).replace(r"\*", ".*"))
        assert any(regex.search(o) for o in outputs), pattern
    # The KiBot BOM lists the same three parts.
    bom = next((eda.REPO / o) for o in outputs if o.endswith("-bom.csv") and "/kibot/" in o)
    text = bom.read_text()
    for ref in ("R1", "C1", "J1"):
        assert ref in text
    # Gerbers come from the board DRC checked: copper exists on B.Cu (the GND zone).
    bcu = next((eda.REPO / o) for o in outputs if o.endswith("-B_Cu.gbr"))
    assert "G36*" in bcu.read_text(), "B.Cu gerber has no region (zone fill) data"


def test_kicad_happy_schematic_and_pcb_analysis(fixture_run):
    run = eda.REPO / fixture_run["run_dir"] / "analyze"
    sch = json.loads((run / "schematic.json").read_text())
    pcb = json.loads((run / "pcb.json").read_text())
    spice = json.loads((run / "spice.json").read_text())
    refs = sorted(c["reference"] for c in sch["components"])
    rc = [r for r in spice["simulation_results"] if r["subcircuit_type"] == "rc_filter"]
    record("fixture_analysis", {"schematic_refs": refs, "pcb": pcb["statistics"],
                                "pcb_power_net_resolution": pcb.get("power_net_resolution"), "spice_rc": rc})
    assert refs == ["C1", "J1", "R1"]
    assert pcb["statistics"]["footprint_count"] == 3
    assert pcb["statistics"]["routing_complete"] is True
    # The documented cross-reference input (--schematic schematic.json) was consumed.
    # (kicad-happy marks power-net resolution as schematic-sourced, not heuristic).
    assert pcb["power_net_resolution"]["source"] == "schematic"
    # kicad-happy's spice skill found the RC filter and its cutoff matches 1/(2*pi*R*C).
    fc = 1 / (2 * math.pi * TAU)
    assert rc and rc[0]["status"] == "pass"
    assert abs(rc[0]["expected"]["cutoff_hz"] - fc) / fc < 0.001
    assert abs(rc[0]["simulated"]["cutoff_hz"] - fc) / fc < 0.01


# ------------------------------------------------ the checks really detect faults

def test_erc_detects_injected_fault(tmp_path):
    cfg = disposable(tmp_path, "erc-fault")
    sch = cfg["path"] / cfg["schematic"]
    sch.write_text(remove_block(sch.read_text(), "wire", "(xy 86.36 59.69)"))  # R1.1 stub
    s = eda.run_project(cfg["name"], ["erc"], cfg=cfg)
    erc = s["steps"]["erc"]
    record("negative_erc", erc)
    assert erc["status"] == "PASS" and erc["design_clean"] is False
    assert "pin_not_connected" in erc["findings"]["by_type"]


def test_drc_detects_unrouted_track_and_parity_mismatch(tmp_path):
    cfg = disposable(tmp_path, "drc-fault")
    pcb = cfg["path"] / cfg["pcb"]
    text = remove_block(pcb.read_text(), "segment", "(start 100 100)")      # J1.1 -> R1.1
    text = text.replace('(property "Value" "10k"', '(property "Value" "22k"', 1)  # R1 value
    pcb.write_text(text)
    s = eda.run_project(cfg["name"], ["drc"], cfg=cfg)
    drc = s["steps"]["drc"]
    record("negative_drc", drc)
    assert drc["status"] == "PASS" and drc["design_clean"] is False
    assert drc["findings"]["unconnected_items"] >= 1
    assert drc["findings"]["schematic_parity"] >= 1


def test_skipped_parity_is_a_failure(tmp_path):
    cfg = disposable(tmp_path, "no-schematic")
    (cfg["path"] / cfg["schematic"]).unlink()  # DRC parity looks for <board>.kicad_sch
    ctx_dir = eda.new_run_dir("project", cfg["name"])
    snap, manifest = cfg["path"], {"sheet_instances": 1}
    r = eda.step_drc({"cfg": cfg, "snap": snap, "manifest": manifest, "run_dir": ctx_dir, "fill": "asis"})
    record("negative_parity_skipped", r)
    assert r["status"] == "FAIL"
    assert any("parity was not performed" in reason for reason in r["reasons"])


def test_zone_fill_state_saved_vs_in_memory(tmp_path):
    """Refilling during DRC does not change the file unless --save-board is used."""
    cfg = disposable(tmp_path, "unfilled")
    pcb = cfg["path"] / cfg["pcb"]
    pcb.write_text(remove_all_blocks(pcb.read_text(), "filled_polygon"))
    unfilled_sha = eda.sha256(pcb)

    asis = eda.run_project(cfg["name"], ["drc"], cfg=cfg)
    asis_drc = load_step(asis, "drc")
    # As saved, the GND zone is empty, so J1.3 and C1.2 are not connected.
    assert asis["steps"]["drc"]["findings"]["unconnected_items"] >= 1

    # In-memory refill: DRC sees a filled zone, but the file is unchanged.
    work = tmp_path / "in-memory"
    shutil.copytree(cfg["path"], work)
    r = eda.run_cmd(["kicad-cli", "pcb", "drc", "--refill-zones", "--format", "json",
                     "-o", work / "drc.json", work / "rc_filter.kicad_pcb"], work, work / "drc.log")
    in_memory = json.loads((work / "drc.json").read_text())
    assert r["exit_code"] == 0
    assert len(in_memory["unconnected_items"]) == 0
    assert eda.sha256(work / "rc_filter.kicad_pcb") == unfilled_sha

    # Refill mode: refill + save the snapshot, then DRC and export the saved file.
    refill = eda.run_project(cfg["name"], ["drc", "export"], fill="refill", cfg=cfg)
    drc = load_step(refill, "drc")
    exp = load_step(refill, "export")
    record("zone_fill_state", {"unfilled_sha256": unfilled_sha, "asis_drc_board": asis_drc["board_sha256_checked"],
                               "in_memory_refill_unconnected": len(in_memory["unconnected_items"]),
                               "refill": drc.get("refill"), "refill_drc_board": drc["board_sha256_checked"],
                               "export_board": exp.get("board_sha256"),
                               "refill_drc_findings": drc["findings"]})
    assert drc["refill"]["board_changed"] is True
    assert drc["board_sha256_checked"] == drc["refill"]["board_sha256_after"] != unfilled_sha
    assert drc["findings"]["unconnected_items"] == 0
    assert exp["status"] == "PASS" and exp["board_sha256"] == drc["board_sha256_checked"]
    assert eda.sha256(pcb) == unfilled_sha  # the source copy was never written


# ---------------------------------------------------------------- simulation

def analytic():
    return {"v_at_tau": 1 - math.exp(-1), "t_half": TAU * math.log(2), "v_at_5tau": 1 - math.exp(-5)}


def test_ngspice_rc_step_matches_analytic():
    r = eda.simulate(SIM / "rc_step.cir", expect=SIM / "rc_step.expect.json")
    exp = analytic()
    names, data = eda.read_raw(eda.REPO / r["run_dir"] / "result.raw")
    t, vout = data[:, names.index("time")], data[:, names.index("v(out)")]
    wave_err = float(np.max(np.abs(vout - (1 - np.exp(-t / TAU)))))
    record("sim_rc_step", {"result": r, "analytic": exp, "waveform_max_abs_error_v": wave_err})
    assert r["status"] == "PASS", r["reasons"]
    for k, v in exp.items():
        assert r["measurements"][k] == pytest.approx(v, rel=2e-3), k
    # The whole waveform, not just the .meas points, follows 1 - exp(-t/tau).
    assert wave_err < 2e-3


def test_ngspice_simulates_kicad_exported_netlist(tmp_path):
    cfg = disposable(tmp_path, "spice-export")
    work = tmp_path / "sim"
    work.mkdir()
    rec = eda.run_cmd(["kicad-cli", "sch", "export", "netlist", "--format", "spice", "-o",
                       work / "rc_filter.cir", cfg["path"] / cfg["schematic"]], work, work / "export.log")
    assert rec["exit_code"] == 0
    netlist = (work / "rc_filter.cir").read_text()
    assert re.search(r"(?m)^R1 /IN /OUT 10k$", netlist) and re.search(r"(?m)^C1 /OUT GND 100n$", netlist)
    shutil.copy(SIM / "rc_from_schematic.cir", work / "deck.cir")
    r = eda.simulate(work / "deck.cir", out=tmp_path / "out")
    record("sim_from_schematic", {"exported_netlist": netlist, "result": r, "analytic": analytic()})
    assert r["status"] == "PASS", r["reasons"]
    assert r["measurements"]["v_at_tau"] == pytest.approx(analytic()["v_at_tau"], rel=2e-3)
    assert r["measurements"]["t_half"] == pytest.approx(analytic()["t_half"], rel=2e-3)


def test_ngspice_failures_are_not_passes(tmp_path):
    bad = tmp_path / "bad_meas.cir"
    bad.write_text((SIM / "rc_step.cir").read_text().replace(
        ".end", ".meas tran bogus FIND v(nonexistent) AT=1m\n.end"))
    r1 = eda.simulate(bad, out=tmp_path / "bad")
    ctl = tmp_path / "has_control.cir"
    ctl.write_text((SIM / "rc_step.cir").read_text().replace(".end", ".control\nrun\n.endc\n.end"))
    r2 = eda.simulate(ctl, out=tmp_path / "ctl")
    wrong = tmp_path / "wrong.expect.json"
    wrong.write_text(json.dumps({"measurements": {"v_at_tau": {"expected": 0.5, "rel_tol": 0.001}}}))
    r3 = eda.simulate(SIM / "rc_step.cir", expect=wrong, out=tmp_path / "wrong")
    nonempty = tmp_path / "bad"  # already holds results from r1
    with pytest.raises(SystemExit):
        eda.simulate(SIM / "rc_step.cir", out=nonempty)
    record("sim_negative", {"missing_measurement": r1, "control_block": r2, "wrong_expectation": r3})
    assert r1["status"] == "FAIL" and any("bogus" in x for x in r1["reasons"])
    assert r2["status"] == "UNSUPPORTED"
    assert r3["status"] == "FAIL"


# --------------------------------------------------------- PDF / datasheet tools

def test_pdf_text_and_page_render(fixture_run, tmp_path):
    pdf = eda.REPO / fixture_run["run_dir"] / "export" / "native" / "rc_filter-schematic.pdf"
    text = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", "1", str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout
    subprocess.run(["pdftoppm", "-png", "-r", "100", "-f", "1", "-l", "1", str(pdf), str(tmp_path / "page")],
                   check=True)
    png = sorted(tmp_path.glob("page*.png"))
    mutool = subprocess.run(["mutool", "draw", "-F", "txt", str(pdf), "1"], capture_output=True, text=True)
    record("pdf_tools", {"pdftotext_has_refs": all(r in text for r in ("R1", "C1", "J1")),
                         "png": [p.name for p in png], "png_bytes": png[0].stat().st_size if png else 0,
                         "mutool_exit": mutool.returncode})
    assert all(r in text for r in ("R1", "C1", "J1"))
    assert png and png[0].stat().st_size > 1000 and png[0].read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert mutool.returncode == 0 and "R1" in mutool.stdout


# --------------------------------------------------------------- agent skills

def test_agent_skills_discoverable():
    r = subprocess.run([sys.executable, str(TOOLCHAIN / "sync_skills.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
    found = {}
    for d in sorted((eda.REPO / ".agents" / "skills").iterdir()):
        text = (d / "SKILL.md").read_text()
        name = re.search(r"(?m)^name:\s*(\S+)", text).group(1)
        desc = re.search(r'(?m)^description:\s*"?(.*?)"?$', text).group(1)
        found[d.name] = {"name": name, "description_chars": len(desc),
                         "claude_link": (eda.REPO / ".claude" / "skills" / d.name / "SKILL.md").exists()}
        assert name == d.name                 # Codex/Copilot require dir == name
        assert len(desc) <= 1024              # Codex description limit
        assert found[d.name]["claude_link"]
    assert {"fome-eda-toolchain", "kicad-happy-kicad", "kicad-happy-spice", "kicad-happy-datasheets"} <= set(found)
    skillpack = Path.home() / "git" / "skillpack" / "check-repo-skills.py"
    shadow = None
    if skillpack.exists():
        s = subprocess.run([sys.executable, str(skillpack), str(eda.REPO)], capture_output=True, text=True)
        shadow = s.stdout.strip()
        assert s.returncode == 0, s.stdout
    record("agent_skills", {"skills": found, "skillpack_shadow_check": shadow})


# ------------------------------------------- hierarchy: sheets KiCad cannot open

SUBSHEET_BLOCK = """
\t(sheet (at 120 50) (size 20 10) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
\t\t(uuid "0b6c3c55-1d2e-4c1b-9a4e-6d8b2f1e0a01")
\t\t(property "Sheetname" "sub" (at 120 49 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
\t\t(property "Sheetfile" "Sub_Sheet.kicad_sch" (at 120 61 0) (effects (font (size 1.27 1.27)) (justify left top)))
\t\t(instances (project "rc_filter" (path "/ROOT" (page "2"))))
\t)
"""
EMPTY_SHEET = ('(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0")\n'
               '\t(uuid "0b6c3c55-1d2e-4c1b-9a4e-6d8b2f1e0a02") (paper "A4") (lib_symbols)\n'
               '\t(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n')


def with_subsheet(tmp_path, name):
    cfg = disposable(tmp_path, name)
    sch = cfg["path"] / cfg["schematic"]
    text = sch.read_text()
    root = re.search(r'\(uuid "([^"]+)"\)', text).group(1)
    i = text.rindex("\t(sheet_instances")
    sch.write_text(text[:i] + SUBSHEET_BLOCK.replace("ROOT", root).lstrip("\n") + text[i:])
    return cfg


def test_missing_sheet_is_a_failure(tmp_path):
    cfg = with_subsheet(tmp_path, "missing-sheet")
    s = eda.run_project(cfg["name"], ["erc", "netlist"], cfg=cfg)
    record("negative_missing_sheet", s)
    assert s["snapshot"]["missing_sheets"][0]["referenced"] == "Sub_Sheet.kicad_sch"
    assert s["steps"]["erc"]["status"] == "FAIL"
    assert s["steps"]["netlist"]["status"] == "FAIL"


def test_case_mismatched_sheet_is_aliased_and_reported(tmp_path):
    cfg = with_subsheet(tmp_path, "case-sheet")
    (cfg["path"] / "sub_sheet.kicad_sch").write_text(EMPTY_SHEET)  # wrong case on disk
    s = eda.run_project(cfg["name"], ["erc", "netlist"], cfg=cfg)
    record("sheet_case_alias", s)
    assert s["snapshot"]["sheet_case_aliases"][0]["resolved"] == "sub_sheet.kicad_sch"
    assert any("case-sensitive" in i for i in s["snapshot"]["library_issues"])
    assert s["steps"]["erc"]["status"] == "PASS" and s["steps"]["erc"]["findings"]["sheets_checked"] == 2
    assert s["steps"]["netlist"]["status"] == "PASS"
    assert not (cfg["path"] / "Sub_Sheet.kicad_sch").exists()  # source untouched


def test_netlist_coverage_detects_unloaded_sheet_content(tmp_path):
    """If a sheet's components never reach the netlist, the netlist step fails."""
    cfg = disposable(tmp_path, "coverage")
    extra = cfg["path"] / "unloaded.kicad_sch"
    extra.write_text(re.sub(r'\(reference "(R1|C1)"\)', lambda m: f'(reference "{m.group(1)}99")',
                            (cfg["path"] / cfg["schematic"]).read_text()))
    run_dir = eda.new_run_dir("project", cfg["name"])
    manifest = {"schematic_files": [cfg["schematic"], "unloaded.kicad_sch"], "missing_sheets": []}
    r = eda.step_netlist({"cfg": cfg, "snap": cfg["path"], "manifest": manifest, "run_dir": run_dir, "fill": "asis"})
    record("negative_netlist_coverage", r)
    assert r["status"] == "FAIL"
    assert r["coverage"]["missing_from_netlist"] == ["C199", "R199"]
