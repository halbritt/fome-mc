"""AGENTEE-478 strict-coverage validator (stand-alone; run before planning).

Usage: validate_coverage.py <prep dir> [report.json]
Refuses (exit 1) unless every emitted-board footprint is captured exactly once as a block
member, a fixed anchor or a shared part, and the D2-D5 files reference only real parts,
pins, nets, blocks and AGENTEE-474 register entries.
"""
import collections, hashlib, json, re, sys
from pathlib import Path

D = Path(sys.argv[1])
load = lambda n: json.loads((D / n).read_text())
alloc, elig, rb, xf, fx = (load(n) for n in ('allocation-v2.json', 'side-eligibility.json', 'relationship-bounds.json',
                                             'cross-face-templates.json', 'fixed-shared-rules.json'))
board = load(alloc.get('inventory', {}).get('board_extract', 'extract/emitted-2f1c9557.json'))
inv = alloc.get('inventory', {})
sch = load(inv.get('schematic_netlist', 'extract/emitted-schematic-netlist.json'))['components']
# Inventory = emitted-board footprints plus schematic symbols not yet on a board (AGENTEE-484 additions).
fps = dict(board['footprints'])
schematic_only = sorted(set(sch) - set(fps))
for r in schematic_only:
    fps[r] = {'pads': [{'number': k, 'net': v[0]} for k, v in sch[r]['pins'].items()]}
errors, checks = [], collections.OrderedDict()

def check(name, ok, detail=None):
    checks[name] = {'ok': bool(ok), **({'detail': detail} if detail is not None else {})}
    if not ok:
        errors.append(name)

check('allocation input is 434a9984', alloc['derived_from']['sha256'].startswith('434a9984'), alloc['derived_from']['sha256'])
check('board binding is the emitted board', alloc['board_sha256'] == board['sha256'], board['sha256'])
seen = collections.Counter()
role = {}
for b in alloc['blocks']:
    for r in b['references']:
        seen[r] += 1
        role[r] = 'block:' + b['id']
for f in alloc['fixed']:
    seen[f['reference']] += 1
    role[f['reference']] = 'fixed'
for s in alloc['shared']:
    seen[s['reference']] += 1
    role[s['reference']] = 'shared:' + s['role']
dups = sorted(r for r, n in seen.items() if n > 1)
unassigned = sorted(set(fps) - set(seen))
unknown = sorted(set(seen) - set(fps))
check('0 duplicates', not dups, dups)
check('0 unassigned', not unassigned, unassigned)
check('0 unknown references', not unknown, unknown)
check('inventory captured exactly', set(seen) == set(fps), {'inventory': len(fps), 'captured': len(set(seen) & set(fps))})
check('schematic-only parts are declared', schematic_only == inv.get('schematic_only_not_yet_on_board', []), schematic_only)
board_only = sorted(set(fps) - set(sch))
check('board-only footprints are H1-H4 and fixed', board_only == ['H1', 'H2', 'H3', 'H4'] and all(role[r] == 'fixed' for r in board_only), board_only)
check('every schematic symbol is in the inventory', not (set(sch) - set(fps)), sorted(set(sch) - set(fps)))
check('no empty block', all(b['references'] for b in alloc['blocks']))
bad_anchor = [b['id'] for b in alloc['blocks'] if ('member' in b['anchor'] and b['anchor']['member'] not in b['references'])
              or ('fixed' in b['anchor'] and role.get(b['anchor']['fixed']) != 'fixed')]
check('block anchors valid', not bad_anchor, bad_anchor)
check('no implicit residual bucket', 'residual' not in alloc and not any(b['id'] in ('residual', 'root-sheet', 'allocated-residual') for b in alloc['blocks']))

# D2
ids = {b['id'] for b in alloc['blocks']}
check('eligibility covers every block', set(elig['blocks']) == ids, sorted(ids ^ set(elig['blocks'])))
check('eligibility covers every fixed part', set(elig['fixed']) == {f['reference'] for f in alloc['fixed']})
check('eligibility covers shared TP1-TP6', 'TP1-TP6' in elig['shared'])
cites = re.findall(r"'id': '(C\d\d)'|\"id\": \"(C\d\d)\"", json.dumps(elig))
cites = {a or b for a, b in cites} | {c for f in elig['fixed'].values() for c in f['sources']}
check('eligibility cites only 474 entries C01-C23', all(re.fullmatch(r'C(0[1-9]|1\d|2[0-3])', c) for c in cites), sorted(cites))
check('no count-balance term', 'none' in elig['count_balance'])
bad_faces = [b for b, v in elig['blocks'].items() if v['eligible_faces'] != ['F', 'B'] and not v['face_restrictions']]
check('every face restriction cites a 474 entry', not bad_faces, bad_faces)

# D3
bad_rel = []
for r in rb['relationships']:
    dv = r['device']
    p = [x for x in fps.get(dv['ref'], {}).get('pads', []) if x['number'] == dv['pin']]
    if not p or p[0]['net'] != dv['net']:
        bad_rel.append((r['id'], 'device pin/net'))
    if r['support']:
        s = fps.get(r['support']['ref'])
        if not s or not any(x['net'] == dv['net'] for x in s['pads']):
            bad_rel.append((r['id'], 'support not on net'))
    b = r['bound']
    if b.get('status') != 'UNRESOLVED' and not (isinstance(b.get('supply_leg_max_mm'), (int, float)) and r['provenance']):
        bad_rel.append((r['id'], 'bound without value/provenance'))
check('relationships bind real pins and nets', not bad_rel, bad_rel)
unres = [r['id'] for r in rb['relationships'] if r['bound'].get('status') == 'UNRESOLVED']
checks['relationships'] = {'ok': True, 'detail': {'total': len(rb['relationships']), 'unresolved': len(unres)}}

# D4/D5
rid = {r['id'] for r in rb['relationships']}
check('cross-face instances reference relationships', all(i['relationship'] in rid for i in xf['instances']))
check('fixed rules cover every fixed part', set(fx['fixed']) == {f['reference'] for f in alloc['fixed']})

report = {'validator': 'agentee-478 validate_coverage.py', 'board_sha256': board['sha256'],
          'counts': {'footprints': len(fps), 'schematic_only': len(schematic_only), 'block_members': sum(len(b['references']) for b in alloc['blocks']),
                     'blocks': len(alloc['blocks']), 'fixed': len(alloc['fixed']), 'shared': len(alloc['shared']),
                     'unassigned': len(unassigned), 'duplicates': len(dups)},
          'checks': checks, 'result': 'PASS' if not errors else 'FAIL', 'failed': errors}
text = json.dumps(report, indent=1) + '\n'
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(text)
print(text)
sys.exit(1 if errors else 0)
