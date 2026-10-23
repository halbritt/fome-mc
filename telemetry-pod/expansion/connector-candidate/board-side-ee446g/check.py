"""AGENTEE-446 ee446g packet self-check (host python, no pcbnew, no network).

    python3 -I check.py              # verify the packet
    python3 -I check.py --self-test  # verify, then require every negative control to be rejected

It also checks the source-capture addendum (agent-521 c13da285): the captured bytes against sources.json, every
quoted JLCPCB fact verbatim near its label in the retained page, the refusal status of the TE 403 capture, the
row-by-row comparison against evidence.json, and the tolerance arithmetic recomputed from the quoted values.

It checks that SHA256SUMS covers exactly the packet files; recomputes every binding and source hash from the
repository bytes; checks that the native facts are for the bound board, that J1/U3 are unchanged against the prior
board adfb7668, and that every row's board facts equal the values derived from logs/native-facts.json and
logs/boardlock-faces.json; and enforces the reporting rules: TE rows cite a page and section, verdicts come from a
fixed set, unknown rows name the missing source, relays carry the relay class, no text is labelled owner-stated,
(c) and (d) stay deferred, and every finding names its source.
"""
import copy
import hashlib
import html
import json
import re
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


ADD_VERDICTS = VERDICTS | {'documented-uncertainty', 'no-te-requirement'}
WINDOW = 600


def page_text(path):
    raw = Path(path).read_text(encoding='utf-8')
    raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', '\n', raw))


def addendum_problems(ev, add, man):
    out = []
    src = HERE / Path(add['manifest']).parent
    by = {m['key']: m for m in man}
    listed = {m['file'] for m in man} | {m['headers'] for m in man}
    present = {p.name for p in src.iterdir() if p.is_file()} - {'sources.json', 'NOTICE.md'}
    if listed != present:
        out.append(f'capture: sources.json and the directory differ: {sorted(listed ^ present)}')
    texts = {}
    for m in man:
        body, head = src / m['file'], src / m['headers']
        if not body.is_file() or not head.is_file():
            continue
        if sha(body) != m['sha256'] or body.stat().st_size != m['bytes']:
            out.append(f'capture: {m["file"]} is not {m["sha256"][:12]} / {m["bytes"]} B')
        status = head.read_text(encoding='utf-8', errors='replace').split('\n', 1)[0].split()
        if len(status) < 2 or status[1] != str(m['http_status']):
            out.append(f'capture: {m["headers"]} status line does not match {m["http_status"]}')
        if not m['url'].startswith(('https://jlcpcb.com/', 'https://www.te.com/')):
            out.append(f'capture: {m["url"]} is not an official JLCPCB or TE URL')
        if m['http_status'] == 200:
            texts[m['key']] = page_text(body)
    fids = {f['id']: f for f in add['facts']}
    for f in add['facts']:
        if f['source'] not in by:
            out.append(f'{f["id"]}: unknown capture {f["source"]}')
            continue
        if f['quote'] is None:
            if not f.get('unknown'):
                out.append(f'{f["id"]}: no quote and no stated retrieval limit')
            continue
        if by[f['source']]['http_status'] != 200:
            out.append(f'{f["id"]}: quotes a refused (HTTP {by[f["source"]]["http_status"]}) capture')
            continue
        text, anchor = texts.get(f['source'], ''), f['label'].split(' (')[0]
        starts = [m.start() for m in re.finditer(re.escape(anchor), text)]
        if not any(f['quote'] in text[i:i + WINDOW] for i in starts):
            out.append(f'{f["id"]}: quote not found verbatim after "{anchor}" in the captured page')
    rows = {r['id']: r for r in ev['rows']}
    arow = {}
    for r in add['rows']:
        if r['row'] in arow or r['row'] not in rows:
            out.append(f'addendum: row {r["row"]} duplicate or not in evidence.json')
            continue
        arow[r['row']] = r
        if r['previous'] is None:
            if r['now'] is not None or r['facts']:
                out.append(f'addendum {r["row"]}: an uninformed row cannot change')
            continue
        if r['previous'] != rows[r['row']]['verdict']:
            out.append(f'addendum {r["row"]}: previous {r["previous"]!r} is not the packet verdict {rows[r["row"]]["verdict"]!r}')
        if r['now'] not in ADD_VERDICTS:
            out.append(f'addendum {r["row"]}: verdict {r["now"]!r} not allowed')
        for fid in r['facts']:
            if fid not in fids:
                out.append(f'addendum {r["row"]}: unknown fact {fid}')
        if r['now'] == 'mismatch' and not any(c.get('row') == r['row'] for c in add['concrete_incompatibilities']):
            out.append(f'addendum {r["row"]}: mismatch not listed as a concrete incompatibility')
        if r['now'] == 'consistent' and any(fids.get(x, {}).get('quote') is None for x in r['facts']):
            out.append(f'addendum {r["row"]}: consistent on an unknown fact')
    if set(arow) != set(rows) - {'c', 'd'}:
        out.append('addendum: does not cover exactly rows a1-a14 and b1-b8')
    for f in add['facts']:
        for rid in f['informs']:
            if f['id'] not in arow.get(rid, {}).get('facts', []):
                out.append(f'{f["id"]}: informs {rid} but the row does not cite it')
    for c in add['concrete_incompatibilities']:
        if not c.get('source') or not c.get('feature') or not c.get('row'):
            out.append('addendum: concrete incompatibility without source, feature or row')
    # Tolerance arithmetic from the quoted values.
    try:
        plus, minus = map(float, re.search(r'\+([\d.]+) / -([\d.]+) mm', fids['F1']['quote']).groups())
        for rid, nom, tol, key in (('a2', 1.75, 0.10, 'jlc_on_1_75_mm'), ('a7', 2.85, 0.08, 'jlc_on_2_85_mm')):
            a = arow[rid]['arithmetic']
            if a['te_mm'] != [round(nom - tol, 4), round(nom + tol, 4)] or a[key] != [round(nom - minus, 4), round(nom + plus, 4)]:
                out.append(f'addendum {rid}: arithmetic does not follow from TE and the quoted F1')
        if arow['a9']['arithmetic']['board_nominal_annulus_mm'] != 0.325:
            out.append('addendum a9: annulus differs from the native 0.325')
    except (KeyError, AttributeError, TypeError) as exc:
        out.append(f'addendum: arithmetic not checkable ({exc!r})')
    text = json.dumps(add) + json.dumps(man)
    if 'owner-stated' in text.lower() or 'decided by the owner' in text.lower():
        out.append('provenance: addendum text labelled owner-stated')
    return out


def problems(ev, facts, faces, sums_text, files, add=None, man=None):
    out = [] if add is None else addendum_problems(ev, add, man)
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
    add = json.loads((HERE / 'addendum-c13da285.json').read_text())
    return (json.loads((HERE / 'evidence.json').read_text()), json.loads((HERE / 'logs/native-facts.json').read_text()),
            json.loads((HERE / 'logs/boardlock-faces.json').read_text()), (HERE / 'SHA256SUMS').read_text(), files,
            add, json.loads((HERE / add['manifest']).read_text()))


def controls(ev, facts, faces, sums, files, add, man):
    """Each mutation must be rejected."""
    def mut(fn, target='ev'):
        e, f, g, s, a, m = copy.deepcopy(ev), copy.deepcopy(facts), copy.deepcopy(faces), sums, copy.deepcopy(add), copy.deepcopy(man)
        if target == 'ev':
            fn(e)
        elif target == 'facts':
            fn(f)
        elif target == 'faces':
            fn(g)
        elif target == 'add':
            fn(a)
        elif target == 'man':
            fn(m)
        else:
            s = fn(s)
        return e, f, g, s, files, a, m
    fact = lambda a, i: next(x for x in a['facts'] if x['id'] == i)
    arow = lambda a, i: next(x for x in a['rows'] if x['row'] == i)
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
        'capture hash altered': mut(lambda m: m[0].update(sha256='6' * 64), 'man'),
        'capture status altered': mut(lambda m: m[1].update(http_status=200), 'man'),
        'non-official capture URL': mut(lambda m: m[0].update(url='https://example.com/jlc'), 'man'),
        'quote not in the page': mut(lambda a: fact(a, 'F1').update(quote='Through-holes: +0.10 / -0.10 mm'), 'add'),
        'quote under the wrong label': mut(lambda a: fact(a, 'F3').update(label='Hole Position Tolerance', quote='18μm'), 'add'),
        'quote from the 403 capture': mut(lambda a: fact(a, 'U2').update(quote='Access Denied'), 'add'),
        'unknown without retrieval limit': mut(lambda a: fact(a, 'U1').pop('unknown'), 'add'),
        'previous verdict misquoted': mut(lambda a: arow(a, 'a2').update(previous='consistent'), 'add'),
        'verdict outside the addendum set': mut(lambda a: arow(a, 'a2').update(now='compliant'), 'add'),
        'consistent on an unknown fact': mut(lambda a: arow(a, 'b1').update(now='consistent'), 'add'),
        'mismatch not flagged': mut(lambda a: arow(a, 'a7').update(now='mismatch'), 'add'),
        'informed row not citing its fact': mut(lambda a: arow(a, 'a11').update(facts=[]), 'add'),
        'row dropped from the comparison': mut(lambda a: a['rows'].remove(arow(a, 'b8')), 'add'),
        'arithmetic altered': mut(lambda a: arow(a, 'a2')['arithmetic'].update(jlc_on_1_75_mm=[1.67, 1.85]), 'add'),
        'incompatibility without source': mut(lambda a: a['concrete_incompatibilities'].append({'row': 'a2'}), 'add'),
        'addendum owner-stated label': mut(lambda a: a.update(decision='owner-stated'), 'add'),
    }


def main():
    loaded = load()
    found = problems(*loaded)
    for p in found:
        print('FAIL', p)
    if found:
        return 1
    if '--self-test' in sys.argv:
        cases = controls(*loaded)
        bad = [name for name, args in cases.items() if not problems(*args)]
        for name in bad:
            print('FAIL control accepted:', name)
        if bad:
            return 1
        print(f'board-side-ee446g: PASS ({len(cases)} controls rejected)')
    else:
        print('board-side-ee446g: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
