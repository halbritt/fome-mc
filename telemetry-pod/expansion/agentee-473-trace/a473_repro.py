"""AGENTEE-473 minimal reproduction (read-only; no design written). agent-ee 39924b46 (PYTHONPATH), image d96f8e00.
1. blocks.derive on the EMITTED board + its native netlist WITHOUT an allocation (what the flat emitted schematic
   yields) and WITH fome-mc blocks/allocation.json (434a9984...): block count, residual count and reasons.
2. For each board (emitted input, R5 placed, ROUTE-3 routed), final-coordinate per-block report from the captured
   probe: member count, side split, footprint-origin spread (bounding-box diagonal of footprint origins, mm; not courtyard centres, not internal connection length), whether the block is split across
   sides, and the board-level side counts.
Usage: a473_repro.py NETLIST ALLOCATION OUT_JSON BOARD_LABEL=PATH ...
"""
import hashlib, json, math, sys
from pathlib import Path
from agent_ee import blocks
from agent_ee.native_netlist import read_native_inventory, read_sheet_names
from agent_ee.placement_probe import extract
netlist, allocation, out = sys.argv[1:4]
boards = dict(a.split('=', 1) for a in sys.argv[4:])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
inv = read_native_inventory(netlist)
names = read_sheet_names(netlist)
doc = {'netlist_sha256': sha(netlist), 'allocation_sha256': sha(allocation), 'boards': {}}
first = next(iter(boards))
cap0 = extract(boards[first])
none = blocks.derive(inv, names, cap0, inventory_sha256=sha(netlist))
alloc = blocks.derive(inv, names, cap0, inventory_sha256=sha(netlist), allocation_raw=Path(allocation).read_bytes())
reasons = lambda d: {r: sum(1 for x in d['residual'] if x['reason'] == r) for r in sorted({x['reason'] for x in d['residual']})}  # noqa: E731
doc['derive_without_allocation'] = {'blocks': len(none['blocks']), 'residual': len(none['residual']), 'residual_reasons': reasons(none),
                                    'sheets': len(names)}
doc['derive_with_allocation'] = {'blocks': len(alloc['blocks']), 'members': sum(len(b['references']) for b in alloc['blocks']),
                                 'residual': len(alloc['residual']), 'residual_reasons': reasons(alloc),
                                 'block_ids': [b['id'] for b in alloc['blocks']]}
for label, path in boards.items():
    cap = extract(path)
    fps = {f['ref']: f for f in cap['footprints']}
    sides = {r: f['side'] for r, f in fps.items()}
    rows = {}
    for b in alloc['blocks']:
        refs = b['references']
        pts = [fps[r]['position_nm'] for r in refs]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        split = {s: sum(1 for r in refs if sides[r] == s) for s in ('F', 'B')}
        rows[b['id']] = {'members': len(refs), 'F': split['F'], 'B': split['B'], 'split_across_sides': split['F'] > 0 and split['B'] > 0,
                         'spread_mm': round(math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 1e6, 2)}
    doc['boards'][label] = {'sha256': sha(path), 'footprints': len(fps),
                            'F': sum(1 for s in sides.values() if s == 'F'), 'B': sum(1 for s in sides.values() if s == 'B'),
                            'blocks': rows,
                            'blocks_split_across_sides': sorted(k for k, v in rows.items() if v['split_across_sides'])}
Path(out).write_text(json.dumps(doc, indent=1, sort_keys=True) + '\n')
print(json.dumps({'derive_without_allocation': doc['derive_without_allocation'], 'derive_with_allocation': {k: v for k, v in doc['derive_with_allocation'].items() if k != 'block_ids'},
                  'boards': {k: {kk: v[kk] for kk in ('sha256', 'F', 'B', 'blocks_split_across_sides')} for k, v in doc['boards'].items()}}))
for k, v in doc['boards'].items():
    print(k, {b: (r['F'], r['B'], r['spread_mm']) for b, r in v['blocks'].items()})
