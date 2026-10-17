"""Independent check of a committed routing: native DRC (refill, all severities,
exclusions shown, parity) on NEW, and preservation of NEW vs its pre-routing parent OLD."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "git/fome-mc/toolchain"))
import eda, route

old_rev, new_rev = sys.argv[1], sys.argv[2]
out = eda.BUILD / "verify-routing" / f"{old_rev}-{new_rev}"
import shutil; shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
res = {}
dirs = {}
for label, rev in (("old", old_rev), ("new", new_rev)):
    cfg = eda.project_config("fome-mc"); cfg["rev"] = rev
    d = out / label; d.mkdir()
    ref, manifest = route.snapshot_input(cfg, d)
    dirs[label] = ref
    board = ref / cfg["pcb"]
    work = d / "graded" / ref.name
    route.copy_project(ref, work)
    rep, info = route.kicad_drc(work / cfg["pcb"], d / "drc", label, refill_and_save=True)
    facts, _ = route.board_facts(board, d / "facts.json")
    res[label] = {"rev": rev, "git_head": manifest.get("source_git_head"), "drc_info": {k: info.get(k) for k in ("parity_performed", "parity_skip_message", "reasons")},
                  "violations": len(rep["violations"]), "unconnected": len(rep["unconnected_items"]),
                  "parity": len(rep["schematic_parity"]),
                  "by_type": eda.count_by(rep["violations"], "type"),
                  "by_severity": eda.count_by(rep["violations"], "severity"),
                  "excluded": sum(1 for v in rep["violations"] if v.get("excluded")),
                  "parity_by_type": eda.count_by(rep["schematic_parity"], "type"),
                  "tracks": len(facts["tracks"]) if "tracks" in facts else None}
    res[label]["_rep"], res[label]["_facts"] = rep, facts
checks, stats = route.preservation(res["old"]["_facts"], res["new"]["_facts"], dirs["old"], dirs["new"],
                                   "fome-mc.kicad_pcb", "existing", set(res["old"]["_facts"]["nets"]))
res["preservation"] = [{k: c[k] for k in ("check", "status", "detail")} | {"n_diff": len(c["differences"]), "sample": c["differences"][:5]} for c in checks]
res["stats"] = stats
new_v, fixed_v = route.drc_delta(res["old"]["_rep"], res["new"]["_rep"], "violations")
res["new_vs_old"] = {"new_violations": eda.count_by(new_v, "type"), "resolved": len(fixed_v)}
for k in ("old", "new"):
    res[k].pop("_rep"); res[k].pop("_facts")
eda.write_json(out / "verify.json", res)
print(json.dumps(res, indent=1, default=str)[:12000])
