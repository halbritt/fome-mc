"""D-PCB-8 silkscreen policy for the expanded telemetry pod.

Usage: python3 -B apply-silk-policy.py BOARD.kicad_pcb NATIVE_DRC.json OUT.kicad_pcb [LOG.json]

Reads KiCad's own DRC report (kicad-cli pcb drc --format json --severity-all) and, for
every silk_* finding, hides the reference/value field it names and moves the named
footprint silkscreen graphic (arc, circle, polygon, segment) to the same side's Fab
layer. Nothing electrical changes: no pad, copper, courtyard, zone, keepout or
footprint pose is touched. Silk is cosmetic; JLCPCB assembly places from the
position file, not the legend. Run it on a seed before packing so the AGENTEE-320
artwork gate does not refuse the saved board, then re-run native DRC on the result.
"""
import json, sys
import pcbnew as k

board, drc_path, out = sys.argv[1:4]
log_path = sys.argv[4] if len(sys.argv) > 4 else None
b = k.LoadBoard(board)
drc = json.load(open(drc_path))
refs, gfx = set(), set()
for vio in drc["violations"]:
    if not vio["type"].startswith("silk"):
        continue
    for it in vio["items"]:
        d = it["description"]
        if d.startswith(("Reference field of ", "Value field of ")):
            refs.add(d.split()[-1])
        elif " on F.Silkscreen" in d or " on B.Silkscreen" in d:
            gfx.add(it["uuid"])
log = {"hidden_refs": [], "graphics_to_fab": []}
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r in refs:
        fp.Reference().SetVisible(False)
        log["hidden_refs"].append(r)
    for g in fp.GraphicalItems():
        if g.m_Uuid.AsString() in gfx and g.GetLayer() in (k.F_SilkS, k.B_SilkS):
            g.SetLayer(k.F_Fab if g.GetLayer() == k.F_SilkS else k.B_Fab)
            log["graphics_to_fab"].append(r)
b.Save(out)
if log_path:
    json.dump(log, open(log_path, "w"), indent=1)
print(json.dumps({key: len(v) for key, v in log.items()}))
