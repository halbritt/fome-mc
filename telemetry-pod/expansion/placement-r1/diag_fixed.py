"""placement-r1 fixed-reference diagnostic (no placement; nothing written to a design). Replicates place_candidate's
preparation with the step's own agent-ee snapshot (extract, _effective_policy, reserve_imu_markings, then the placer's
outline/keepout/band qualification), and evaluates EVERY fixed reference independently with the placer's own
predicates (_fits against outline/bands, _near against declared obstacles within gap_nm, _keepout_blocked), reporting
which predicate fails and which obstacle. Usage: diag_fixed.py BOARD REQUEST OUT_JSON  (PYTHONPATH = the step snapshot)
"""
import json, sys
from pathlib import Path
import pcbnew
from agent_ee import placer as P
from agent_ee.placement_probe import extract
from agent_ee.placer_runner import _effective_policy
from agent_ee.silkscreen import reserve_imu_markings
board, request, out = sys.argv[1:4]
req = json.loads(Path(request).read_text())
facts = extract(board)
policy = reserve_imu_markings(pcbnew.LoadBoard(board), _effective_policy(req))
outline = P._qualified(facts)
labels, pad_keepouts = {}, []
obstacles = P._keepouts(facts, labels, pad_keepouts)
bands = P.overhang_bands(policy.get('fixed_overhangs', []), outline)
fixed = P._fixed_refs(facts, policy)
envelope_refs = set()
for e in policy.get('constraint_provenance', {}).values() if isinstance(policy.get('constraint_provenance'), dict) else []:
    pass
exact = [P._exact(o['side'], P._obstacle_polygons(o['polygons'])) for o in policy['obstacles']]
gap = policy['gap_nm']
rows, placed = [], []
for fp in [f for f in facts['footprints'] if f['ref'] in fixed]:
    fits = P._fits(fp, outline, 0, bands.get(fp['ref'], ()))
    near = [i for i, e in enumerate(exact) if P._near(fp, [e], gap)]
    near0 = [i for i, e in enumerate(exact) if P._near(fp, [e], 0)]
    keep = P._keepout_blocked(fp, placed, obstacles)
    rows.append({'ref': fp['ref'], 'fits_outline_bands': fits, 'obstacles_within_gap': near, 'obstacles_overlapping': near0,
                 'keepout_blocked_vs_earlier_fixed': bool(keep), 'position_nm': fp.get('position') or fp.get('pos') or fp.get('at'),
                 'sides': sorted(fp.get('courtyards', {}))})
    placed.append(fp)
doc = {'fixed_refs': sorted(fixed), 'gap_nm': gap, 'obstacles': [{'index': i, 'side': o['side'], 'polygons': o['polygons']}
       for i, o in enumerate(policy['obstacles'])], 'rows': rows,
       'conflicting': [r['ref'] for r in rows if not r['fits_outline_bands'] or r['obstacles_within_gap'] or r['keepout_blocked_vs_earlier_fixed']]}
Path(out).write_text(json.dumps(doc, indent=1, sort_keys=True, default=str) + '\n')
print(json.dumps({'conflicting': doc['conflicting'], 'rows': [{k: r[k] for k in ('ref', 'fits_outline_bands', 'obstacles_within_gap', 'obstacles_overlapping', 'keepout_blocked_vs_earlier_fixed')} for r in rows]}))
