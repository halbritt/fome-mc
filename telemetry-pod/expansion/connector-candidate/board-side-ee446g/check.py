"""AGENTEE-446 ee446g packet self-check (host python, no pcbnew, no network).

    python3 -I check.py              # verify the packet
    python3 -I check.py --self-test  # verify, then require every negative control to be rejected

It checks that SHA256SUMS covers exactly the packet files; recomputes every binding and source hash from the
repository bytes; checks that the native facts are for the bound board, that J1/U3 are unchanged against the prior
board adfb7668, and that every row's board facts equal the values derived from logs/native-facts.json and
logs/boardlock-faces.json; and enforces the reporting rules: TE rows cite a page and section, verdicts come from a
fixed set, unknown rows name the missing source, relays carry the relay class, no text is labelled owner-stated,
(c) and (d) stay deferred, and every finding names its source.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RELAY = 'owner-relayed (agent-drafted, unconfirmed)'
VERDICTS = {'consistent', 'mismatch', 'unknown', 'settled', 'open-bench', 'open-design', 'deferred'}
TE_DOCS = {'AS114S3', 'K1', 'D2293782E5'}
CURRENT = '2f1c955704ab1fb38217c24cbaf5a45f4219a74a6a2309be710452c54db3b673'
PRIOR = 'adfb7668ac0c80dc1b4f1d2f97afa86b193f630c545bf43cbc0de8f49f351a40'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def derived(facts, faces):
    """The board values the rows may cite, computed from the native probe and the model-face output."""
    boards = {b['sha256']: b for b in facts['boards']}
    j1 = boards[CURRENT]['footprints']['J1']
    pads = j1['geometry']['pads']
    pth = [p for p in pads if p['attrib'] == 'PTH']
    npth = [p for p in pads if p['attrib'] == 'NPTH']
    shoulders = [f['y'] for f in faces['faces'] if f['normal_y'] == 1.0]
    return {
        'pth_count': len(pth),
        'pth_drill_mm': sorted({max(p['drill']) for p in pth}),
        'pth_land_mm': sorted({min(p['size']) for p in pth}),
        'pth_nominal_annulus_mm': sorted({p['nominal_radial_annulus_mm'] for p in pth}),
        'npth': sorted([p['at'], p['drill']] for p in npth),
        'npth_drill_mm': sorted({max(p['drill']) for p in npth}),
        'npth_copper_free': all(p['size'] == p['drill'] for p in npth),
        'pth_matches_coordinates_json': j1['pth_matches_coordinates_json'],
        'locator_centreline_to_edge_mm': j1['locator_centreline_to_edge_mm'],
        'min_hole_wall_gap_mm': j1['min_hole_wall_gap_mm']['value'],
        'min_pth_land_to_edge_mm': j1['min_pth_land_to_edge_mm'],
        'board_thickness_mm': boards[CURRENT]['board_thickness_mm'],
        'copper_layers': boards[CURRENT]['copper_layers'],
        'u3_on_board': boards[CURRENT]['footprints']['U3']['bbox_inside_edge_cuts_bbox'],
        'shoulder_y': shoulders[0] if len(set(shoulders)) == 1 else None,
        'support_flat_y': faces['support_flat_y'],
    }


def problems(ev, facts, faces, sums_text, files):
    out = []
    # SHA256SUMS: exactly the packet files, each digest correct.
    listed = {}
    for line in sums_text.splitlines():
        digest, _, name = line.partition('  ')
        if len(digest) != 64 or not name or name in listed:
            out.append(f'SHA256SUMS: malformed or duplicate line {line!r}')
            continue
        listed[name] = digest
    if set(listed) != files:
        out.append(f'SHA256SUMS: lists {sorted(set(listed) ^ files)} wrongly')
    for name, digest in listed.items():
        if name in files and sha(HERE / name) != digest:
            out.append(f'SHA256SUMS: {name} digest differs')
    # Binding and sources, recomputed from the repository bytes.
    b = ev['binding']
    if b['candidate_id'] != '5504a022417b5bf49ad6b1cec7f39f65bd3f8a566e46a286bb656904bef837ba':
        out.append('binding: wrong candidate id')
    for f in b['files'] + list(ev['sources'].values()):
        if sha(ROOT / f['path']) != f['sha256']:
            out.append(f'binding/source: {f["path"]} is not {f["sha256"][:12]}')
    boards = [x for x in b['files'] if x['role'].startswith('board (')]
    if {x['sha256'] for x in boards} != {CURRENT}:
        out.append('binding: board is not the candidate board 2f1c9557')
    # Native facts: the bound board, the prior board, unchanged J1/U3.
    by = {x['sha256']: x for x in facts['boards']}
    if set(by) != {CURRENT, PRIOR}:
        out.append('facts: boards are not exactly the candidate and the prior adfb7668')
    else:
        for ref in ('J1', 'U3'):
            p, c = by[PRIOR]['footprints'][ref], by[CURRENT]['footprints'][ref]
            for key in ('geometry_sha256', 'text_block_sha256', 'position_mm', 'rotation_deg', 'layer'):
                if p[key] != c[key]:
                    out.append(f'facts: {ref} {key} changed since adfb7668 but reuse is claimed')
        pose = b['native_pose']
        for ref in ('J1', 'U3'):
            c = by[CURRENT]['footprints'][ref]
            for key in ('fpid', 'position_mm', 'rotation_deg', 'layer', 'locked'):
                if pose[ref][key] != c[key]:
                    out.append(f'binding: native_pose {ref} {key} differs from the facts')
        if not by[CURRENT]['footprints']['J1']['pads_equal_library']:
            out.append('facts: J1 pads differ from the captured library footprint')
    if faces['step_sha256'] != ev['sources']['HEADERSTEP']['sha256']:
        out.append('faces: not computed on the bound header STEP')
    try:
        values = derived(facts, faces)
    except (KeyError, IndexError, TypeError) as exc:
        return out + [f'facts: cannot derive board values ({exc!r})']
    # Rows.
    ids = [r['id'] for r in ev['rows']]
    if len(ids) != len(set(ids)):
        out.append('rows: duplicate id')
    for item in 'abcd':
        if not any(r['item'] == item for r in ev['rows']):
            out.append(f'rows: no row for item ({item})')
    reuse = {r['id'] for r in ev['reuse']}
    for r in ev['rows']:
        rid = r['id']
        if r['verdict'] not in VERDICTS:
            out.append(f'{rid}: verdict {r["verdict"]!r} not allowed')
        if r['item'] in 'cd':
            if r['verdict'] != 'deferred' or 'needs the placed candidate' not in r.get('note', ''):
                out.append(f'{rid}: items (c) and (d) must stay deferred to the placed candidate')
            continue
        if not r['sources']:
            out.append(f'{rid}: no source')
        for s in r['sources']:
            if s['key'] not in ev['sources']:
                out.append(f'{rid}: unknown source {s["key"]}')
                continue
            if s['key'] in TE_DOCS and (not s.get('page') or not s.get('section')):
                out.append(f'{rid}: TE source {s["key"]} without page and section')
            if not s.get('quote'):
                out.append(f'{rid}: source {s["key"]} without a quote')
            if ev['sources'][s['key']]['class'] == RELAY and s.get('class') != RELAY:
                out.append(f'{rid}: relay quoted without the relay class')
        if r['verdict'] == 'unknown' and not r.get('missing_source'):
            out.append(f'{rid}: unknown without the missing source')
        if r['verdict'] == 'mismatch' and not any(f.get('row') == rid for f in ev['findings']):
            out.append(f'{rid}: mismatch without a finding')
        for key, want in r['board'].get('facts', {}).items():
            if key not in values:
                out.append(f'{rid}: board fact {key} is not derivable from the native facts')
            elif values[key] != want:
                out.append(f'{rid}: board fact {key} is {want!r} in evidence but {values[key]!r} natively')
        for ref in r.get('reuse', []):
            if ref not in reuse:
                out.append(f'{rid}: unknown reuse {ref}')
    for f in ev['findings']:
        if not f.get('source') or not f.get('row'):
            out.append('findings: a finding without a source or row')
    text = json.dumps(ev)
    if 'owner-stated' in text.lower() or 'decided by the owner' in text.lower():
        out.append('provenance: text labelled owner-stated')
    return out


def load():
    files = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name != 'SHA256SUMS'
             and '__pycache__' not in p.parts}
    return (json.loads((HERE / 'evidence.json').read_text()), json.loads((HERE / 'logs/native-facts.json').read_text()),
            json.loads((HERE / 'logs/boardlock-faces.json').read_text()), (HERE / 'SHA256SUMS').read_text(), files)


def controls(ev, facts, faces, sums, files):
    """Each mutation must be rejected."""
    def mut(fn, target='ev'):
        e, f, g, s = copy.deepcopy(ev), copy.deepcopy(facts), copy.deepcopy(faces), sums
        if target == 'ev':
            fn(e)
        elif target == 'facts':
            fn(f)
        elif target == 'faces':
            fn(g)
        else:
            s = fn(s)
        return e, f, g, s, files
    row = lambda e, i: next(r for r in e['rows'] if r['id'] == i)
    return {
        'wrong board hash in binding': mut(lambda e: e['binding']['files'][3].update(sha256='0' * 64)),
        'wrong candidate id': mut(lambda e: e['binding'].update(candidate_id='1' * 64)),
        'wrong TE source hash': mut(lambda e: e['sources']['AS114S3'].update(sha256='2' * 64)),
        'verdict outside the set': mut(lambda e: row(e, 'a1').update(verdict='compliant')),
        'TE row without page': mut(lambda e: row(e, 'a1')['sources'][0].update(page=None)),
        'unknown without missing source': mut(lambda e: row(e, 'a2').pop('missing_source')),
        'mismatch without finding': mut(lambda e: row(e, 'a12').update(verdict='mismatch')),
        'finding without source': mut(lambda e: e['findings'].append({'row': 'a1'})),
        'board value differs from native': mut(lambda e: row(e, 'a8')['board']['facts'].update(locator_centreline_to_edge_mm=[9.5, 9.5])),
        'item (c) not deferred': mut(lambda e: row(e, 'c').update(verdict='consistent')),
        'item (d) dropped': mut(lambda e: e['rows'].remove(row(e, 'd'))),
        'owner-stated label': mut(lambda e: row(e, 'b6')['sources'][0].update(**{'class': 'owner-stated'})),
        'relay without relay class': mut(lambda e: row(e, 'a14')['sources'][1].pop('class')),
        'J1 geometry changed': mut(lambda f: f['boards'][0]['footprints']['J1'].update(geometry_sha256='3' * 64), 'facts'),
        'facts for another board': mut(lambda f: f['boards'][1].update(sha256='4' * 64), 'facts'),
        'faces from another STEP': mut(lambda g: g.update(step_sha256='5' * 64), 'faces'),
        'SHA256SUMS line removed': mut(lambda s: ''.join(s.splitlines(True)[1:]), 'sums'),
        'SHA256SUMS duplicate line': mut(lambda s: s + s.splitlines(True)[0], 'sums'),
    }


def main():
    ev, facts, faces, sums, files = load()
    found = problems(ev, facts, faces, sums, files)
    for p in found:
        print('FAIL', p)
    if found:
        return 1
    if '--self-test' in sys.argv:
        bad = [name for name, args in controls(ev, facts, faces, sums, files).items() if not problems(*args)]
        for name in bad:
            print('FAIL control accepted:', name)
        if bad:
            return 1
        print(f'board-side-ee446g: PASS ({len(controls(ev, facts, faces, sums, files))} controls rejected)')
    else:
        print('board-side-ee446g: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
