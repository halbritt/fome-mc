"""placement-r5: R2's 287 poses + the 22 authorized B.Cu side changes (agent-521 81bf1861; plan rev 5). Runtime: 7d5b0d4d +
R5 side-transform patch (placer_runner.py only). No placer, scorer or search: each of the 22 gets ONE explicit pose,
the first pose found stepping outward from the centroid of its connected (non-ground) pads that is native-geometry clear
on B: courtyard (inflated by gap_nm) inside the outline inset min_courtyard_edge_mm, clear of every other B courtyard,
all B.Cu copper (THT pads included) and every rule area that forbids footprints on B. Then the WHOLE arrangement is
admitted by the patched placer_runner._evaluate_proposal on the ORIGINAL board under policy r1 plus the explicit
agent-ee.side-changes/1 authorization (bound to the original board sha256 and the exact 22 ref/UUIDs).
Usage: r5_place.py WORK   (WORK: inputs/ (candidate tree), r2/{placement-result,request}.json, netlist.xml)
"""
import copy, json, math, shutil, sys, traceback
from pathlib import Path
import pcbnew as k
from agent_ee import placer_runner as PR
from agent_ee.placement_probe import extract
from agent_ee.silkscreen import reserve_imu_markings
from agent_ee.storage import digest
W = Path(sys.argv[1])
SIDE = ['R7', *[f'R{n}' for n in range(70, 85)], *[f'TP{n}' for n in range(1, 7)]]
base = W / 'inputs/project/telemetry-pod.kicad_pcb'
r2 = json.loads((W / 'r2/placement-result.json').read_text())
req = json.loads((W / 'r2/request.json').read_text())
policy = {kk: v for kk, v in req['policy'].items() if kk != 'search_timeout_s'}
policy['step_budget'] = 200000  # policy r1 exactly
partial = {p['uuid']: p for p in r2['search']['partial']['placements']}
gap, edge = policy['gap_nm'], int(round(policy['min_courtyard_edge_mm'] * 1e6))
ground = set(policy.get('ground_nets', []))
report = {'side_refs': SIDE}
# scratch board for pose choice only (the baseline stays the original file)
board = k.LoadBoard(str(base))
fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
for uuid, p in partial.items():
    fp = next(f for f in board.GetFootprints() if f.m_Uuid.AsString() == uuid)
    fp.SetOrientationDegrees(p['rotation_deg']); fp.SetPosition(k.VECTOR2I(*p['position_nm']))
origin = {r: {'position_nm': [fps[r].GetPosition().x, fps[r].GetPosition().y], 'rotation_deg': fps[r].GetOrientationDegrees(),
              'side': 'B' if fps[r].IsFlipped() else 'F'} for r in SIDE}
edges = board.GetBoardEdgesBoundingBox()
inner = (edges.GetLeft() + edge, edges.GetTop() + edge, edges.GetRight() - edge, edges.GetBottom() - edge)
def box(b, pad=0):
    return (b.GetLeft() - pad, b.GetTop() - pad, b.GetRight() + pad, b.GetBottom() + pad)
def meets(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
blocked = []  # (bbox, what)
for ref, fp in fps.items():
    if ref in SIDE:
        continue
    cy = fp.GetCourtyard(k.B_CrtYd)
    if cy.OutlineCount():
        blocked.append((box(cy.BBox(), gap), f'{ref} B courtyard'))
    for pad in fp.Pads():
        if pad.IsOnLayer(k.B_Cu) or pad.GetAttribute() in (k.PAD_ATTRIB_PTH, k.PAD_ATTRIB_NPTH):
            blocked.append((box(pad.GetBoundingBox(), gap), f'{ref} pad {pad.GetNumber()} (B copper/hole)'))
for z in board.Zones():
    if z.GetIsRuleArea() and z.GetDoNotAllowFootprints() and (z.GetLayerSet().Contains(k.B_Cu) or z.GetLayerSet().Contains(k.B_CrtYd)):
        blocked.append((box(z.GetBoundingBox()), f'rule area {z.GetZoneName() or z.m_Uuid.AsString()} forbids footprints on B'))
report['blocking_items'] = len(blocked)
by_net = {}
for ref, fp in fps.items():
    for pad in fp.Pads():
        if pad.GetNetname() and pad.GetNetname() not in ground:
            by_net.setdefault(pad.GetNetname(), []).append((ref, pad.GetPosition()))
transforms = []
for ref in SIDE:
    fp = fps[ref]
    nets = sorted({p.GetNetname() for p in fp.Pads() if p.GetNetname() and p.GetNetname() not in ground})
    # Peers: pads already on the board -- every part outside the 22, and those of the 22 already placed.
    onboard = lambda r: r not in SIDE or r in {t['ref'] for t in transforms}  # noqa: E731
    per_net = {n: [pos for r, pos in by_net.get(n, []) if r != ref and onboard(r)] for n in nets}
    signal = [n for n in nets if 0 < len(per_net[n]) <= 20]  # rail-like nets (>20 peer pads) only as a fallback
    peers = [pos for n in (signal or nets) for pos in per_net[n]]
    cx = sum(p.x for p in peers) / len(peers) if peers else (inner[0] + inner[2]) / 2
    cy = sum(p.y for p in peers) / len(peers) if peers else (inner[1] + inner[3]) / 2
    cx, cy = min(max(cx, inner[0]), inner[2]), min(max(cy, inner[1]), inner[3])
    fp.Flip(fp.GetPosition(), k.FLIP_DIRECTION_LEFT_RIGHT)
    chosen = None
    for ring in range(0, 121):  # 0.5 mm rings out to 60 mm
        r_nm = ring * 500000
        steps = max(1, int(2 * math.pi * r_nm / 500000))
        for s in range(steps):
            a = 2 * math.pi * s / steps
            x, y = int(round(cx + r_nm * math.cos(a))), int(round(cy + r_nm * math.sin(a)))
            for rot in (0.0, 90.0):
                fp.SetOrientationDegrees(rot); fp.SetPosition(k.VECTOR2I(x, y))
                c = fp.GetCourtyard(k.B_CrtYd)
                if not c.OutlineCount():
                    raise ValueError(f'{ref}: no native B courtyard after flip')
                b = box(c.BBox())
                if not (b[0] >= inner[0] and b[1] >= inner[1] and b[2] <= inner[2] and b[3] <= inner[3]):
                    continue
                pads = [box(p.GetBoundingBox()) for p in fp.Pads()]
                if any(meets(b, o) or any(meets(pb, o) for pb in pads) for o, _ in blocked):
                    continue
                chosen = (x, y, rot, r_nm)
                break
            if chosen:
                break
        if chosen:
            break
    if chosen is None:
        report['unplaceable'] = ref
        break
    x, y, rot, dist = chosen
    fp.SetOrientationDegrees(rot); fp.SetPosition(k.VECTOR2I(x, y))
    blocked.append((box(fp.GetCourtyard(k.B_CrtYd).BBox(), gap), f'{ref} B courtyard'))
    transforms.append({'ref': ref, 'uuid': fp.m_Uuid.AsString(), 'from': origin[ref],
                       'to': {'position_nm': [x, y], 'rotation_deg': fp.GetOrientationDegrees(), 'side': 'B'},
                       'nets': nets, 'centroid_nets': signal or nets, 'net_centroid_nm': [int(cx), int(cy)], 'offset_from_centroid_mm': round(dist / 1e6, 2),
                       'peer_pads': len(peers)})
report['transforms'] = transforms
if 'unplaceable' in report:
    (W / 'r5-report.json').write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + '\n'); print(json.dumps(report, default=str)); sys.exit(1)
# the whole arrangement, admitted on the ORIGINAL board
orig = k.LoadBoard(str(base))
sourced = set(policy['fixed_refs'])
side_uuid = {t['uuid']: t for t in transforms}
placements = []
for fp in orig.GetFootprints():
    u, r = fp.m_Uuid.AsString(), fp.GetReference()
    if u in side_uuid:
        t = side_uuid[u]['to']; pos, rot = t['position_nm'], t['rotation_deg']
    elif u in partial:
        pos, rot = partial[u]['position_nm'], partial[u]['rotation_deg']
    else:
        pos, rot = [fp.GetPosition().x, fp.GetPosition().y], fp.GetOrientationDegrees()
    entry = {'ref': r, 'uuid': u, 'position_nm': pos, 'rotation_deg': rot, 'fixed': r in sourced}
    if u in side_uuid:
        entry['side'] = 'B'
    placements.append(entry)
assert len(placements) == 309 and sum(1 for p in placements if p['fixed']) == 9
plan = {'schema': 'agent-ee.packing-plan/1', 'status': 'planned', 'board_sha256': digest(base),
        'min_courtyard_edge_mm': policy['min_courtyard_edge_mm'],
        'policy': reserve_imu_markings(k.LoadBoard(str(base)), PR._effective_policy({'policy': policy})), 'placements': placements}
side_changes = {'schema': 'agent-ee.side-changes/1', 'source_sha256': digest(base),
                'changes': [{'ref': t['ref'], 'uuid': t['uuid'], 'side': 'B'} for t in transforms]}
(W / 'side-changes.json').write_text(json.dumps(side_changes, indent=1, sort_keys=True) + '\n')
(W / 'plan.json').write_text(json.dumps(plan, indent=1, sort_keys=True, default=str) + '\n')
final = W / 'final'; final.mkdir()
try:
    full = PR._evaluate_proposal(k.LoadBoard(str(base)), final / 'candidate.kicad_pcb', plan, (W / 'netlist.xml').read_bytes(),
                                 extract(base), base, side_changes)
    (final / 'evaluate-proposal.json').write_text(json.dumps(full, indent=1, sort_keys=True, default=str) + '\n')
    report['evaluate_proposal'] = {'status': full['status'], 'verdict': full['verdict'], 'open_defects': len(full['open_defects']),
                                   'judge': full['judgment'].get('verdict'), 'locality': full['judgment'].get('locality_grading', {}).get('status'),
                                   'native_courtyard_overlaps': full['native_courtyard_overlaps'], 'board_sha256': full['board_sha256']}
except Exception as exc:
    report['evaluate_proposal'] = {'status': 'refused', 'error': f'{type(exc).__name__}: {exc}', 'trace': traceback.format_exc()[-2500:]}
(W / 'r5-report.json').write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + '\n')
print(json.dumps({'transforms': [(t['ref'], t['offset_from_centroid_mm']) for t in transforms], 'evaluate_proposal': {kk: v for kk, v in report['evaluate_proposal'].items() if kk != 'trace'}}, default=str))
sys.exit(0 if report['evaluate_proposal'].get('status') == 'placed' else 2)
