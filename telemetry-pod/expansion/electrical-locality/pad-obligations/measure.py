#!/usr/bin/env python3
"""Independent pad-centre measurement of an agent-ee.electrical-locality/1 document
against a placement probe (footprints with pads: number, net, position_nm).
Uses no agent-ee code. Prints JSON: one row per pair with pass/defect/unknown."""
import json, math, sys
probe = json.load(open(sys.argv[1])); doc = json.load(open(sys.argv[2]))
fps = {}
for f in probe['footprints']:
    fps.setdefault(f['ref'], []).append(f)
def pos(e):
    fl = fps.get(e['reference'], [])
    if len(fl) != 1: return None, 'reference missing or duplicated'
    pads = [p for p in fl[0]['pads'] if p['number'] == e['pad']]
    if len(pads) != 1: return None, f'pad {e["pad"]} count {len(pads)}'
    if pads[0]['net'] != e['net']: return None, f'net {pads[0]["net"]} != {e["net"]}'
    return pads[0]['position_nm'], None
rows = []
for o in doc['obligations']:
    for role in ('supply', 'return', 'switch'):
        if role not in o: continue
        pr = o[role]; a, ea = pos(pr['from']); b, eb = pos(pr['to'])
        row = {'obligation': o['id'], 'role': role, 'from': f"{pr['from']['reference']}.{pr['from']['pad']}", 'to': f"{pr['to']['reference']}.{pr['to']['pad']}", 'limit_mm': pr['max_distance_nm'] / 1e6}
        if ea or eb:
            row.update(status='unknown', reason=ea or eb)
        else:
            sq = (a[0]-b[0])**2 + (a[1]-b[1])**2
            row.update(distance_mm=round(math.sqrt(sq)/1e6, 6), status='defect' if sq > pr['max_distance_nm']**2 else 'pass')
        rows.append(row)
json.dump({'board_sha256': probe.get('board_sha256'), 'rows': rows}, sys.stdout, indent=1); print()
