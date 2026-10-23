"""AGENTEE-478 D1 member justification: every block member must be reachable from its block on non-rail
nets, bound to a device pin by a D3 rail relationship, or linked on a non-rail net to the block's fixed
anchor. Usage: d1_verify.py <prep dir> <out.json>"""
import json, sys
from pathlib import Path
D = Path(sys.argv[1])
alloc = json.loads((D / 'allocation-v2.json').read_text())
rels = json.loads((D / 'relationship-bounds.json').read_text())['relationships']
nl = json.loads((D / 'extract/emitted-schematic-netlist.json').read_text())
C, N = nl['components'], nl['nets']
RAIL = {'/GND', '/+3V3', '/PRE_6V3', '/POD_12V_PROTECTED', '/+5V_CAN', '/POD_5V_SENSOR'}
bound = {}
for r in rels:
    if r['support']:
        bound.setdefault(r['support']['ref'], []).append(r['id'])
out, bad = {}, []
for b in alloc['blocks']:
    m = set(b['references'])
    adj = {r: set() for r in m}
    for net, nodes in N.items():
        if net in RAIL:
            continue
        rs = {r for r, _, _ in nodes} & m
        for r in rs:
            adj[r] |= rs - {r}
    comps, left = [], set(m)
    while left:
        s = left.pop(); comp = {s}; st = [s]
        while st:
            x = st.pop()
            for y in adj[x] - comp:
                comp.add(y); st.append(y)
        left -= comp; comps.append(comp)
    big = max(comps, key=len)
    fixed = b['anchor'].get('fixed') or b.get('interfaces_to_fixed')
    rows = {}
    for r in sorted(m):
        why = []
        if r in big and len(big) > 1:
            why.append('non-rail connected to the block core')
        if r in bound:
            why.append('D3 relationship: ' + ', '.join(bound[r][:3]))
        if fixed and any(net not in RAIL and any(rr == fixed for rr, _, _ in N[net]) for net, _ in C[r]['pins'].values()):
            why.append(f'non-rail net to fixed anchor {fixed}')
        if len(m) == 1:
            why.append('single-member block')
        rows[r] = why or ['UNJUSTIFIED']
        if not why:
            bad.append((b['id'], r))
    out[b['id']] = {'non_rail_components': [sorted(c) for c in comps], 'members': rows}
json.dump({'blocks': out, 'unjustified': bad}, open(sys.argv[2], 'w'), indent=1)
print('unjustified', bad)
