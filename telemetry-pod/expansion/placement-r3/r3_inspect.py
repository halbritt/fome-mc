"""placement-r3 free-space inspection (diagnostic; no design written). On the 287-pose copy: per side, a 0.1 mm occupancy
grid of every placed/fixed courtyard inflated by gap_nm, the outline inset by min_courtyard_edge_mm, and the declared
obstacles; the free cells, their connected regions (area, bbox), each missing part's courtyard size and allowed sides,
and which R2 parts border the largest free regions. Writes free-space.json and an occupancy PNG per side.
Usage: r3_inspect.py BOARD287 POLICY_REQUEST_JSON MISSING_JSON OUTDIR
"""
import json, struct, sys, zlib
from pathlib import Path
from agent_ee.placement_probe import extract
board, reqp, missp, outd = sys.argv[1:5]
out = Path(outd); out.mkdir(exist_ok=True)
policy = json.loads(Path(reqp).read_text())['policy']
missing = set(json.loads(Path(missp).read_text())['missing'])
facts = extract(board)
G = 100000  # 0.1 mm
gap, edge = policy['gap_nm'], int(round(policy['min_courtyard_edge_mm'] * 1e6))
xs = [p[0] for poly in facts['outline']['polygons'] for p in poly]; ys = [p[1] for poly in facts['outline']['polygons'] for p in poly]
x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
nx, ny = (x1 - x0) // G, (y1 - y0) // G
def bbox(polys):
    if isinstance(polys, dict):
        polys = polys.get('polygons') or polys.get('outline') or []
    if polys and isinstance(polys[0], (list, tuple)) and polys[0] and isinstance(polys[0][0], int):
        polys = [polys]
    px = [p[0] for poly in polys for p in poly]; py = [p[1] for poly in polys for p in poly]
    return min(px), min(py), max(px), max(py)
report = {'outline_bbox_mm': [x0/1e6, y0/1e6, x1/1e6, y1/1e6], 'gap_nm': gap, 'edge_nm': edge, 'sides': {}, 'missing_parts': {}}
for fp in facts['footprints']:
    if fp['ref'] in missing:
        report['missing_parts'][fp['ref']] = {s: [round((b[2]-b[0])/1e6, 3), round((b[3]-b[1])/1e6, 3)] for s, polys in fp.get('courtyards', {}).items() for b in [bbox(polys)]}
for side in ('F', 'B'):
    occ = bytearray(nx * ny)
    def mark(b, pad, val=1):
        a, c = max(0, (b[0] - pad - x0) // G), min(nx, -(-(b[2] + pad - x0) // G))
        d, e = max(0, (b[1] - pad - y0) // G), min(ny, -(-(b[3] + pad - y0) // G))
        for j in range(d, e):
            occ[j*nx + a: j*nx + c] = bytes([val]) * max(0, c - a)
    # edge margin band
    m = -(-edge // G)
    for j in range(ny):
        for i in range(nx):
            if i < m or j < m or i >= nx - m or j >= ny - m:
                occ[j*nx + i] = 2
    owners = {}
    for fp in facts['footprints']:
        if fp['ref'] in missing or side not in fp.get('courtyards', {}):
            continue
        b = bbox(fp['courtyards'][side]); owners[fp['ref']] = b
        mark(b, gap, 1)
    for o in policy['obstacles']:
        if o['side'] == side:
            for poly in o['polygons']:
                mark(bbox([poly]), 0, 3)
    # connected free regions
    seen = bytearray(nx * ny); regions = []
    for start in range(nx * ny):
        if occ[start] or seen[start]:
            continue
        stack, cells, bx = [start], 0, [nx, ny, 0, 0]
        seen[start] = 1
        while stack:
            k = stack.pop(); cells += 1; i, j = k % nx, k // nx
            bx = [min(bx[0], i), min(bx[1], j), max(bx[2], i), max(bx[3], j)]
            for q in (k-1 if i else -1, k+1 if i < nx-1 else -1, k-nx if j else -1, k+nx if j < ny-1 else -1):
                if q >= 0 and not occ[q] and not seen[q]:
                    seen[q] = 1; stack.append(q)
        regions.append({'area_mm2': round(cells * (G/1e6)**2, 2), 'bbox_mm': [round(x0/1e6 + bx[0]*G/1e6, 1), round(y0/1e6 + bx[1]*G/1e6, 1), round(x0/1e6 + (bx[2]+1)*G/1e6, 1), round(y0/1e6 + (bx[3]+1)*G/1e6, 1)]})
    regions.sort(key=lambda r: -r['area_mm2'])
    for r in regions[:8]:
        bb = [v * 1e6 for v in r['bbox_mm']]
        r['bordering_refs'] = sorted(ref for ref, b in owners.items() if b[0] - 1.5e6 <= bb[2] and b[2] + 1.5e6 >= bb[0] and b[1] - 1.5e6 <= bb[3] and b[3] + 1.5e6 >= bb[1])
    report['sides'][side] = {'free_mm2': round(sum(r['area_mm2'] for r in regions), 2), 'regions': len(regions), 'largest': regions[:8]}
    # PNG: free white, courtyards grey, edge band dark, obstacles red
    pal = {0: (255, 255, 255), 1: (150, 150, 150), 2: (60, 60, 60), 3: (220, 60, 60)}
    raw = b''.join(b'\x00' + b''.join(bytes(pal[occ[j*nx+i]]) for i in range(nx)) for j in range(ny))
    chunk = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)  # noqa: E731
    (out / f'INCOMPLETE-r2-287-free-space-{side}.png').write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', nx, ny, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
(out / 'free-space.json').write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
print(json.dumps({'missing_parts': report['missing_parts'], 'sides': {s: {'free_mm2': v['free_mm2'], 'regions': v['regions'], 'largest': [(r['area_mm2'], r['bbox_mm'], len(r['bordering_refs'])) for r in v['largest'][:6]]} for s, v in report['sides'].items()}}))
