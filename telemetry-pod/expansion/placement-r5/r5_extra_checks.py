"""placement-r5 extra whole-board checks (read-only): every sourced-fixed pose unchanged vs the input; every movable part
inside the outline less min_courtyard_edge_mm by the placer's own _fits; footprint sides (only the 22 flipped).
Usage: r5_extra_checks.py INPUT_BOARD FINAL_BOARD REQUEST_JSON OUT_JSON
"""
import json, sys
from pathlib import Path
from agent_ee import placer as P
from agent_ee.placement_probe import extract
inp, fin, reqp, out = sys.argv[1:5]
policy = json.loads(Path(reqp).read_text())['policy']
a, b = extract(inp), extract(fin)
ia, ib = {f['ref']: f for f in a['footprints']}, {f['ref']: f for f in b['footprints']}
fixed = sorted(policy['fixed_refs'])
outline, margin = P._qualified(b), P._edge_margin_nm(policy)
side = {r: sorted(f.get('courtyards', {})) for r, f in ib.items()}
doc = {'fixed_pose_unchanged': {r: (ia[r]['position_nm'], ia[r]['rotation_deg'], sorted(ia[r].get('courtyards', {}))) ==
                                (ib[r]['position_nm'], ib[r]['rotation_deg'], sorted(ib[r].get('courtyards', {}))) for r in fixed},
       'edge_margin_nm': margin,
       'edge_violations': sorted(r for r, f in ib.items() if r not in fixed and not P._fits(f, outline, margin)),
       'b_side_refs': sorted(r for r, s in side.items() if s == ['B']),
       'side_changed_refs': sorted(r for r in ia if sorted(ia[r].get('courtyards', {})) != side[r])}
Path(out).write_text(json.dumps(doc, indent=1, sort_keys=True) + '\n')
print(json.dumps(doc))
