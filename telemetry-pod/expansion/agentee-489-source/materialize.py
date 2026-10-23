"""AGENTEE-489: materialize the AGENTEE-490 recipe into agent-ee.mechanical-reservations/1.

Source: ../agentee-490-mechanical-inputs/bound-reservations.json (agentee-490.bound-reservations/1,
a RECIPE contract). Output: reservations.json, bound to the immutable native board snapshot
(telemetry-pod/telemetry-pod.kicad_pcb at the commit that carries this file).

Rules kept here (agent-ee docs/mechanical-reservations.md):
- every row stays classification engineering (AGENT), never manufacturer or owner;
- an UNKNOWN height or access bound is height_nm null / coverage "unknown", never zero;
- AGENTEE-485 item 5 (chief agent-531 3dfa0a5f, relayed by integrator agent-530; coordinator decision, not owner
  text): a driver tolerance stated as UNKNOWN alone is NOT a worst-case-stack gate. A driver row with concrete nominal
  geometry (radius and z interval) keeps a concrete nominal board/tool access check (access "covered" on the nominal
  sweep, the unknown tolerance kept in uncertainty); only truly missing geometry (height_nm null) stays "unknown";
- J2 follows the 494-j2 correction (OWNER-CORRECTION.md, agent-drafted, applying owner-relayed direction): the published
  Amphenol 132134 Rev C pattern and the Manufacturer footprint; the old J2 slot/thickness ambiguity is NOT a gate;
- selected connector geometry is declared in source-fixed library-front coordinates before generation;
  reflect local Y on a captured B owner, then let the consumer follow final native pose/side;
- final part substitution changes native FPID/pad inventory and requires a fresh binding after source adoption,
  not a circular pre-generation geometry-completeness requirement;
- cylinders become circumscribed regular 16-gons, vertices rounded outward to integer nm, so the
  per-face projection covers the cylinder (conservative-per-face);
- owners with custom pads (JP1..JP5, shape 6) are refused by the consumer binding and are listed
  in UNMATERIALIZED rather than silently dropped or bound to a fake frame.
Usage: python3 -I materialize.py <repo-root>
"""
import hashlib, json, math, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
POD = ROOT / 'telemetry-pod'
SRC = POD / 'expansion/agentee-490-mechanical-inputs/bound-reservations.json'
BOARD = POD / 'telemetry-pod.kicad_pcb'
OUT = POD / 'expansion/agentee-489-source'
# Candidate-relative paths at which the production capture must place the bytes (see RESULT.md gap G1).
BOARD_REL = 'mechanics/original-board.kicad_pcb'
SRC_REL = 'mechanics/agentee-490-bound-reservations.json'
NM = 1_000_000
AUTHOR = 'AGENT engineering: original486/490 recipe by agent-507; ten-row485 board-side closure by agent-535;489 materialization'
OWNER_CITE = ('owner answers a13a1ba8@2 / 842b3689@1, relayed via AGENTEE-486 (agent-449), class owner-relayed')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sides(text):
    out = {}
    for m in re.finditer(r'\(footprint "[^"]*"\s*(?:\(locked yes\)\s*)?\(layer "([FB])\.Cu"\)\s*\(uuid "([0-9a-f-]+)"\)', text):
        out[m.group(2)] = m.group(1)
    return out


def ngon(radius_mm, n=16):
    rc = radius_mm / math.cos(math.pi / n) * NM
    pts = []
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        x, y = rc * math.cos(a), rc * math.sin(a)
        pts.append([math.ceil(x) if x > 0 else math.floor(x), math.ceil(y) if y > 0 else math.floor(y)])
    return pts


def interval(z):
    lo, hi = z
    if hi is None:
        return None
    return [round(lo * NM), math.ceil(hi * NM)]


PHASE = {'installed': 'installed', 'bench-fastening-before-lid': 'bench-fastening',
         'bare-board-bench-only': 'bare-board-bench', 'bare-board-one-time-soldering': 'bare-board-soldering'}


def main():
    recipe = json.loads(SRC.read_text())
    if recipe['schema'] != 'agentee-490.bound-reservations/1':
        raise SystemExit('unexpected recipe schema')
    text = BOARD.read_text()
    side = sides(text)
    rows, skipped = [], []
    for r in recipe['base_486_items']:
        uuid, ref = r['uuid'], r['reference']
        if uuid not in side:
            raise SystemExit(f'{ref} {uuid} not in snapshot')
        g = r['geometry']
        if g['kind'] != 'axial_cylinder':
            skipped.append({'id': r['id'], 'owner': {'ref': ref, 'uuid': uuid},
                            'reason': 'owner has custom pads (shape 6); agent-ee mechanical binding refuses '
                                      'custom-pad owners, so no attached frame is available',
                            'recipe': g['kind'], 'status': 'UNMATERIALIZED_REQUIRED'})
            continue
        face = r['face'][0]
        rel = 'same' if (r['id'].endswith('@actual-face') or face == side[uuid]) else 'opposite'
        h = interval(g['z_outward_from_face_mm'])
        access = r['source'].startswith('driver') or ref.startswith('TP')
        unc = [r.get('note', '')] + ([r['phase_gate']] if r.get('phase_gate') else [])
        if access and h and 'UNKNOWN' in r.get('note', ''):
            unc.append('nominal access check on the concrete nominal sweep; the UNKNOWN driver tolerance is recorded, '
                       'not a worst-case-stack gate (AGENTEE-485 item 5, chief agent-531 3dfa0a5f relayed by agent-530; '
                       'coordinator decision, not owner text)')
        if ref.startswith('TP'):
            unc.append('bench-only pogo access per ' + OWNER_CITE)
        rows.append({
            'id': r['id'], 'required': True, 'kind': 'access' if access else 'solid',
            'frame': 'footprint', 'owner': {'ref': ref, 'uuid': uuid},
            'geometry': {'polygons_nm': [ngon(g['radius_mm'])]}, 'faces': [rel], 'height_nm': h,
            'phases': [PHASE[r['phase']]], 'self_exclusion': True,
            'coverage': {'projection': 'conservative-per-face', 'height': 'covered' if h else 'unknown',
                         'access': ('unknown' if h is None else 'covered') if access else 'covered',
                         'basis': f"axial cylinder r={g['radius_mm']} mm about the footprint centre, circumscribed "
                                  f"16-gon rounded outward; class: {r['class']} (engineering)"},
            'uncertainty': [u for u in unc if u]})
    # These selected-part declarations exist before a final native pose. In particular,
    # waiting for the 132134 replacement before declaring its body would prevent the
    # scaffold that performs that replacement from preparing at all.
    closure = recipe['board_side_access_closure']
    for r in closure['rows']:
        ref, uuid = r['reference'], r['uuid']
        if uuid not in side:
            raise SystemExit(f'{ref} {uuid} not in snapshot')
        if r['frame'] != 'library-front-footprint':
            raise SystemExit(f"unsupported source frame for {r['id']}")
        g = r['geometry']
        if 'polygons_mm' in g:
            polygons = [[[round(x * NM), round(y * NM)] for x, y in poly]
                        for poly in g['polygons_mm']]
        else:
            polygons = [ngon(g['cylinder_radius_mm'])]
        # Consumer-local coordinates are on the captured side, with the native
        # angle removed. Convert library-front geometry once; later native flips
        # are handled by agent-ee's bound-owner transform.
        if side[uuid] == 'B':
            polygons = [[[x, -y] for x, y in poly] for poly in polygons]
        h = interval(r['height_mm'])
        if not polygons or h is None:
            raise SystemExit(f"source-fixed declaration is incomplete: {r['id']}")
        citations = '; '.join(f"{s['classification']}: {s['path']} sha256 {s['sha256']} ({s['locator']})"
                              for s in r['sources'])
        rows.append({'id': r['id'], 'required': True, 'kind': r['kind'],
                     'frame': 'footprint', 'owner': {'ref': ref, 'uuid': uuid},
                     'geometry': {'polygons_nm': polygons}, 'faces': r['faces'],
                     'height_nm': h, 'phases': r['phases'], 'self_exclusion': True,
                     'coverage': {'projection': 'conservative-per-face', 'height': 'covered',
                                  'access': 'covered',
                                  'basis': r['basis'] + ' Dimension class: ' + r['dimension_class'] + '. ' + citations},
                     'uncertainty': r['uncertainty']})
    doc = {'schema': 'agent-ee.mechanical-reservations/1', 'original_board_path': BOARD_REL,
           'original_board_sha256': sha(BOARD),
           'source': {'path': SRC_REL, 'sha256': sha(SRC), 'locator': 'base_486_items + board_side_access_closure.rows',
                      'classification': 'engineering', 'author': AUTHOR},
           'reservations': rows}
    (OUT / 'reservations.json').write_text(json.dumps(doc, indent=1) + '\n')
    (OUT / 'unmaterialized.json').write_text(json.dumps(
        {'schema': 'agentee-489.unmaterialized/1', 'rows': skipped,
         'note': 'Required reservations the consumer cannot bind; they are NOT satisfied and block acceptance.'}, indent=1) + '\n')
    print(len(rows), 'rows;', len(skipped), 'unmaterialized')


main()
