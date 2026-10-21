"""summarize_fixtures.py WORK: judge prove.sh's native DRC reports against the expected rule-area findings.

Prints JSON; exits 1 when any fixture misses its expectation. A fixture's delta is taken against the
DRC of the board it was made from (base-source or base-corrected), so only the added item counts.
"""
import collections, hashlib, json, sys
from pathlib import Path

work = Path(sys.argv[1])
FIX = {  # name: (base, added item, expected items_not_allowed delta, why)
    "f01": ("base-corrected", "In1.Cu track (15,50)-(20,50), outside the corridor", 1, "D-PCB-7 v2: In1 no tracks anywhere"),
    "f02": ("base-corrected", "In1.Cu track (82.5,27.2)-(82.5,29.4), inside the corridor", 2, "both rule areas cover it"),
    "f03": ("base-corrected", "In2.Cu track (82.5,27.2)-(82.5,29.4), inside the corridor", 1, "D-PCB-6 spatial no-tracks on In2"),
    "f04": ("base-corrected", "through via (82.5,28.4), inside the corridor", 1, "D-PCB-6 spatial no-vias"),
    "f05": ("base-corrected", "through via (20,55), outside the corridor", 0, "vias allowed on In1 outside D-PCB-6"),
    "f06": ("base-corrected", "In2.Cu track (15,50)-(20,50), outside the corridor", 0, "D-PCB-7 v2: In2 open to signals"),
    "f07": ("base-source", "In1.Cu track as f01, on the uncorrected source", 0, "control: the source has no rule areas"),
    "f08": ("base-source", "via as f04, on the uncorrected source", 0, "control"),
    "f09": ("base-source", "In2.Cu track as f03, on the uncorrected source", 0, "control"),
    "f10": ("base-corrected", "f02 with the D-PCB-7v2 area removed", 1, "attribution: D-PCB-6 alone flags an In1 corridor track"),
    "f11": ("base-corrected", "f02 with the D-PCB-6 area removed", 1, "attribution: D-PCB-7v2 alone flags it"),
}


def load(name):
    p = work / "drc" / name / "drc.json"
    d = json.loads(p.read_text())
    board = work / "drc" / name / "ca2.kicad_pcb"
    return {
        "kicad_version": d.get("kicad_version"),
        "board_sha256": hashlib.sha256(board.read_bytes()).hexdigest(),
        "violations": collections.Counter(v["type"] for v in d["violations"]),
        "unconnected": len(d["unconnected_items"]),
        "rule_area": [{"description": v["description"], "severity": v["severity"],
                       "items": [i["description"] for i in v["items"]]}
                      for v in d["violations"] if v["type"] == "items_not_allowed"],
    }


bases = {b: load(b) for b in ("base-source", "base-corrected")}
ok = bases["base-source"]["violations"] == bases["base-corrected"]["violations"] \
    and bases["base-source"]["unconnected"] == bases["base-corrected"]["unconnected"]
out = {"schema": "corrected-policy-iter7/fixtures/1",
       "drc_command": "kicad-cli pcb drc --format json --severity-all --units mm --refill-zones (in memory, on a copy)",
       "bases": {k: {**v, "violations": dict(v["violations"])} for k, v in bases.items()},
       "bases_identical": ok, "fixtures": {}}
for name, (base, item, want, why) in FIX.items():
    r, b = load(name), bases[base]
    delta = {k: r["violations"][k] - b["violations"][k]
             for k in sorted(set(r["violations"]) | set(b["violations"])) if r["violations"][k] != b["violations"][k]}
    got = delta.get("items_not_allowed", 0)
    passed = got == want and r["unconnected"] == b["unconnected"]
    ok &= passed
    out["fixtures"][name] = {"base": base, "added": item, "expect_items_not_allowed": want, "why": why,
                             "got_items_not_allowed": got, "delta_vs_base": delta,
                             "rule_area_findings": r["rule_area"], "board_sha256": r["board_sha256"],
                             "kicad_version": r["kicad_version"], "verdict": "PASS" if passed else "FAIL"}
out["verdict"] = "PASS" if ok else "FAIL"
print(json.dumps(out, indent=1, sort_keys=False))
sys.exit(0 if ok else 1)
