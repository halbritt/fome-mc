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
- JP custom-pad access uses the qualified native copper outer bound plus the existing chisel
  rectangle in the pad-local frame, plus the explicitly selected finite tool/approach/feed.
  Missing height or incomplete declared access coverage remains unknown.
Usage (native KiCad environment, via native-admit):
  PYTHONPATH=<frozen-agent-ee>/src python3 -B materialize.py <repo-root>
"""
import argparse, hashlib, json, math, re, shutil, sys, tempfile
from decimal import Decimal
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
parser.add_argument('--board', type=Path, help='fresh emitted candidate; source design is never changed')
parser.add_argument('--out', type=Path, help='isolated materialization output directory')
args = parser.parse_args()
ROOT = args.root.resolve()
POD = ROOT / 'telemetry-pod'
SRC = POD / 'expansion/agentee-490-mechanical-inputs/bound-reservations.json'
BOARD = args.board.resolve() if args.board else POD / 'telemetry-pod.kicad_pcb'
OUT = args.out.resolve() if args.out else POD / 'expansion/agentee-489-source'
OUT.mkdir(parents=True, exist_ok=True)
# Candidate-relative paths at which the production capture must place the bytes (see RESULT.md gap G1).
BOARD_REL = 'mechanics/original-board.kicad_pcb'
SRC_REL = 'mechanics/agentee-490-bound-reservations.json'
NM = 1_000_000
AUTHOR = 'AGENT engineering: original486/490 recipe by agent-507; ten-row485 board-side closure by agent-535;489 materialization;JP producer carriage by agent-534'
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



def native_capture():
    """Use the same board-only native binding as the production mechanical source."""
    from agent_ee.placement_probe import extract
    before = sha(BOARD)
    with tempfile.TemporaryDirectory(prefix='ee489-native-') as tmp:
        board = Path(tmp) / BOARD.name
        shutil.copyfile(BOARD, board)
        capture = extract(board)
    if capture['board_sha256'] != before or sha(BOARD) != before:
        raise ValueError('mechanical source board changed during native capture')
    return capture


def iron_row(r, capture):
    """Conservative pad-copper landing locus plus selected nominal tool/operation."""
    from agent_ee.mechanical_reservations import _custom_geometry
    from agent_ee.placer import rotate
    g = r['geometry']
    owners = [f for f in capture['footprints'] if f['ref'] == r['reference'] and f['uuid'] == r['uuid']]
    if len(owners) != 1:
        raise ValueError('iron owner reference/UUID differs from native capture: ' + r['id'])
    fp = owners[0]
    pads = [p for p in fp['pads'] if p['uuid'] == g['pad_uuid'] and p['number'] == g['pad_number']]
    if len(pads) != 1 or r['relative'] != {'origin': 'pad', 'number': g['pad_number'], 'follows_pose': True}:
        raise ValueError('iron pad number/UUID/frame differs from native capture: ' + r['id'])
    pad = pads[0]
    if pad['shape'] != g['captured_pad_shape'] or pad['size_nm'] != [round(v * NM) for v in g['captured_pad_size_mm']]:
        raise ValueError('iron pad shape/anchor size differs from recipe: ' + r['id'])
    box = _custom_geometry(pad)['bbox_nm']
    angle = pad['rotation_deg']
    if not math.isfinite(angle) or angle % 90:
        raise ValueError('iron pad requires an exact quarter-turn native angle')
    local = [rotate([x - pad['position_nm'][0], y - pad['position_nm'][1]], -int(angle) // 90)
             for x in (box[0], box[2]) for y in (box[1], box[3])]
    tip = [Decimal(str(v)) * NM / 2 for v in g['tip_width_thickness_mm']]
    if len(tip) != 2 or any(not v.is_finite() or v <= 0 for v in tip):
        raise ValueError('iron chisel needs two positive finite dimensions')
    lower, upper = [-v for v in tip], list(tip)
    access = g.get('soldering_access')
    if access is not None:
        # This selected nominal operation is an engineering declaration. Derive
        # its conservative projection from the actual declared body/feed bounds.
        if access['classification'] != 'AGENT engineering default':
            raise ValueError('soldering operation must retain engineering-default classification')
        sections = access['tool_sections']
        if not sections:
            raise ValueError('soldering operation needs tool sections')
        bounds = [(Decimal(str(section['radius_mm'])),
                   [Decimal(str(v)) for v in section['z_mm']]) for section in sections]
        if any(not radius.is_finite() or radius <= 0 or len(z) != 2
               or any(not v.is_finite() for v in z) or z[0] < 0 or z[1] <= z[0]
               for radius, z in bounds):
            raise ValueError('soldering tool sections need positive finite ordered bounds')
        radius = max(radius for radius, z in bounds)
        travel = Decimal(str(access['withdrawal_travel_mm']))
        feed = access['solder_feed']
        feed_radius = Decimal(str(feed['radius_mm']))
        centres = [[Decimal(str(v)) for v in p] for p in feed['centreline_mm']]
        if (not radius.is_finite() or radius <= 0 or not travel.is_finite() or travel < 0
                or not feed_radius.is_finite() or feed_radius <= 0
                or len(centres) != 2 or any(len(p) != 3 or any(not v.is_finite() for v in p) for p in centres)):
            raise ValueError('soldering operation needs finite positive body/feed dimensions')
        ceiling = max(Decimal(str(section['z_mm'][1])) for section in sections) + travel
        floor = min(Decimal(str(section['z_mm'][0])) for section in sections)
        feed_low = min(p[2] for p in centres) - feed_radius
        feed_high = max(p[2] for p in centres) + feed_radius
        z = [Decimal(str(v)) if v is not None else None for v in g['z_outward_from_face_mm']]
        if z[1] is not None and (z[0] > min(floor, feed_low) or z[1] < max(ceiling, feed_high)):
            raise ValueError('soldering height does not cover the declared tool/approach/feed')
        for i in (0, 1):
            lower[i] = min(lower[i], -radius * NM, (min(p[i] for p in centres) - feed_radius) * NM)
            upper[i] = max(upper[i], radius * NM, (max(p[i] for p in centres) + feed_radius) * NM)
    x0, y0 = [math.floor(min(v[i] for v in local) + lower[i]) for i in (0, 1)]
    x1, y1 = [math.ceil(max(v[i] for v in local) + upper[i]) for i in (0, 1)]
    h = interval(g['z_outward_from_face_mm'])
    covered = h is not None and access is not None and access['coverage'] == 'complete'
    return {'id': r['id'], 'required': True, 'kind': 'access', 'frame': 'pad',
            'owner': {'ref': r['reference'], 'uuid': r['uuid'],
                      'pad': {'number': pad['number'], 'uuid': pad['uuid']}},
            'geometry': {'polygons_nm': [[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]]},
            'faces': ['same'], 'height_nm': h, 'phases': [PHASE[r['phase']]], 'self_exclusion': True,
            'coverage': {'projection': 'conservative-per-face', 'height': 'covered' if h else 'unknown',
                         'access': 'covered' if covered else 'unknown',
                         'basis': 'Qualified native custom-pad copper bounding box, inverse native pad rotation, '
                                  'Minkowski sum with source chisel rectangle '
                                  + str(g['tip_width_thickness_mm']) + ' mm; outward integer-nm rounding; '
                                  + ('selected nominal normal-head/carrier/withdrawal/feed projection; AGENT default, '
                                     'not a manufacturer maximum or physical access acceptance. '
                                     + json.dumps(access, sort_keys=True) if access is not None else
                                     'tip-only projection, incomplete soldering operation.')},
            'uncertainty': [r['unknown'], r['qualification'], r['phase_gate'],
                            'one-time bare-board soldering per ' + OWNER_CITE]}


def require_coverage(recipe, rows):
    expected = [r['id'] for r in recipe['base_486_items'] + recipe['board_side_access_closure']['rows']]
    actual = [r['id'] for r in rows]
    if len(set(expected)) != len(expected) or sorted(actual) != sorted(expected):
        raise ValueError('materialized reservation IDs differ from complete source recipe inventory')


def main():
    recipe = json.loads(SRC.read_text())
    if recipe['schema'] != 'agentee-490.bound-reservations/1':
        raise SystemExit('unexpected recipe schema')
    text = BOARD.read_text()
    side = sides(text)
    capture = native_capture()
    rows, skipped = [], []
    for r in recipe['base_486_items']:
        uuid, ref = r['uuid'], r['reference']
        if uuid not in side:
            raise SystemExit(f'{ref} {uuid} not in snapshot')
        g = r['geometry']
        if g['kind'] == 'native_pad_bound_minkowski_chisel_rectangle_recipe':
            rows.append(iron_row(r, capture))
            continue
        if g['kind'] != 'axial_cylinder':
            raise ValueError('unsupported mechanical recipe: ' + g['kind'])
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
    require_coverage(recipe, rows)
    doc = {'schema': 'agent-ee.mechanical-reservations/1', 'original_board_path': BOARD_REL,
           'original_board_sha256': capture['board_sha256'],
           'source': {'path': SRC_REL, 'sha256': sha(SRC), 'locator': 'base_486_items + board_side_access_closure.rows',
                      'classification': 'engineering', 'author': AUTHOR},
           'reservations': rows}
    from agent_ee.mechanical_reservations import bind
    bind(doc, capture)  # Validate every declared pad frame before publishing either file.
    if sha(BOARD) != capture['board_sha256']:
        raise ValueError('mechanical source board changed before publication')
    (OUT / 'reservations.json').write_text(json.dumps(doc, indent=1) + '\n')
    (OUT / 'unmaterialized.json').write_text(json.dumps(
        {'schema': 'agentee-489.unmaterialized/1', 'rows': skipped,
         'note': 'Producer carriage inventory only. Empty rows means all source recipes were emitted; '
                 'unknown height/access remains in reservations.json and is not acceptance.'}, indent=1) + '\n')
    print(len(rows), 'rows;', len(skipped), 'unmaterialized')


if __name__ == '__main__':
    main()
