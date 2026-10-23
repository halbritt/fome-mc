"""AGENTEE-489: materialize the AGENTEE-490 recipe into agent-ee.mechanical-reservations/1.

Source: ../agentee-490-mechanical-inputs/bound-reservations.json (agentee-490.bound-reservations/1,
a RECIPE contract). Output: reservations.json, bound to the immutable native board snapshot
(telemetry-pod/telemetry-pod.kicad_pcb at the commit that carries this file).

Rules kept here (agent-ee docs/mechanical-reservations.md):
- every row stays classification engineering (AGENT), never manufacturer or owner;
- an UNKNOWN height or access bound is height_nm null / coverage "unknown", never zero;
- unresolved conditional geometry (J2 132134 before the 485 footprint rebind, J1 internal mate,
  J3 card/blade Z) is polygons_nm null with required true, so it cannot pass;
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
AUTHOR = 'agent-ee writer lane ee489-source (AGENT engineering); recipe by agent-507 (AGENTEE-486/490)'
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
        if ref.startswith('TP'):
            unc.append('bench-only pogo access per ' + OWNER_CITE)
        rows.append({
            'id': r['id'], 'required': True, 'kind': 'access' if access else 'solid',
            'frame': 'footprint', 'owner': {'ref': ref, 'uuid': uuid},
            'geometry': {'polygons_nm': [ngon(g['radius_mm'])]}, 'faces': [rel], 'height_nm': h,
            'phases': [PHASE[r['phase']]], 'self_exclusion': True,
            'coverage': {'projection': 'conservative-per-face', 'height': 'covered' if h else 'unknown',
                         'access': ('unknown' if 'UNKNOWN' in r.get('note', '') or h is None else 'covered')
                         if access else 'covered',
                         'basis': f"axial cylinder r={g['radius_mm']} mm about the footprint centre, circumscribed "
                                  f"16-gon rounded outward; class: {r['class']} (engineering)"},
            'uncertainty': [u for u in unc if u]})
    j1 = re.search(r'\(uuid "([0-9a-f-]+)"\)\s*\(at [^)]*\)\s*(?:\(descr[^\n]*\)\s*)?(?:\(tags[^\n]*\)\s*)?\(property "Reference" "J1"', text)
    cond = {
        'J2/132134-part-optionA': ('J2', '18c6ebf4-5f6a-5227-b278-be0fa33a91c9', 'solid', ['same', 'opposite'], ['installed'],
            'J2 = Amphenol 132134 (agent-529 82f08e7a v1; owner "keep the vertical SMA" relayed by agent-519). Snapshot J2 '
            'still carries the Molex 73251-1153 edge footprint; the box (xy +-3.6 about RF pad1, above F 0..9.73, below B 2.90) '
            'is materialized only after the AGENTEE-485 rebind to Agentee494.pretty/SMA_Amphenol_132134_Manufacturer (2b65c583).'),
        'J2/132134-assembly-expansion': ('J2', '18c6ebf4-5f6a-5227-b278-be0fa33a91c9', 'access', ['same', 'opposite'], ['installed', 'bench-sma-attach'],
            'Chosen reserves +0.1 above F / +0.5 below B and the 7.25 mm, 115 mm tool sweep are AGENT assembly choices, not '
            'manufacturer limits; actual tool orientation on the vertical SMA and joint torque remain required.'),
        'J3/card-and-flat-tool': ('J3', 'c4f5153d-f022-576c-a234-98fe27f874d1', 'access', ['same'], ['bare-board-sd-access'],
            'J3 plain-edge B (9.1,40,90) bare-board blade access selected, no notch (agent-529 82f08e7a v1); actual card/socket '
            'Z unknown; the 490 J3 study used an idealised 110x80 rectangle, not the saved Edge.Cuts; card/tool tolerance open.'),
    }
    if j1:
        cond['J1/internal-mate-and-tail'] = ('J1', j1.group(1), 'access', ['same', 'opposite'], ['installed'],
            'J1 external-mating direction selected (agent-529 82f08e7a v1); mated plug envelope and K1 4.75+-0.15 panel vs the '
            'application spec 2..5 are unreconciled; 35-tail grid registration is not a mating-stop proof (486 J1-registration).')
    for rid, (ref, uuid, kind, faces, phases, note) in cond.items():
        if uuid not in side:
            raise SystemExit(f'{ref} {uuid} not in snapshot')
        rows.append({'id': rid, 'required': True, 'kind': kind, 'frame': 'footprint', 'owner': {'ref': ref, 'uuid': uuid},
                     'geometry': {'polygons_nm': None}, 'faces': faces, 'height_nm': None, 'phases': phases,
                     'self_exclusion': True,
                     'coverage': {'projection': 'conservative-per-face', 'height': 'unknown', 'access': 'unknown',
                                  'basis': 'CONDITIONAL: geometry unresolved at this snapshot; cannot pass until regenerated'},
                     'uncertainty': [note]})
    doc = {'schema': 'agent-ee.mechanical-reservations/1', 'original_board_path': BOARD_REL,
           'original_board_sha256': sha(BOARD),
           'source': {'path': SRC_REL, 'sha256': sha(SRC), 'locator': 'base_486_items + new_or_clarified',
                      'classification': 'engineering', 'author': AUTHOR},
           'reservations': rows}
    (OUT / 'reservations.json').write_text(json.dumps(doc, indent=1) + '\n')
    (OUT / 'unmaterialized.json').write_text(json.dumps(
        {'schema': 'agentee-489.unmaterialized/1', 'rows': skipped,
         'note': 'Required reservations the consumer cannot bind; they are NOT satisfied and block acceptance.'}, indent=1) + '\n')
    print(len(rows), 'rows;', len(skipped), 'unmaterialized')


main()
