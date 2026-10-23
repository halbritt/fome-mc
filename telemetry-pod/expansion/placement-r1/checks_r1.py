"""placement-r1 result checks, INSIDE the qualified runtime container (native tools; nothing re-saved in place).
- the native 'after' DRC on a copy of the candidate tree with ONLY project/telemetry-pod.kicad_pcb replaced by the
  placed board (kicad-cli pcb drc --severity-all --schematic-parity), when a placed board exists;
- preservation, before vs after, with pcbnew: footprint count (electrical + board-only mounting holes), every
  reference's FPID and value, every pad's net, the net set, J1's position/orientation/side/FPID, copper layer count,
  board thickness and stackup, track/via/zone counts, and the project .kicad_pro/.kicad_dru bytes.
Usage: checks_r1.py WORK
"""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
import pcbnew
work = Path(sys.argv[1])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
placed = work / 'placement/placed/candidate.kicad_pcb'
before_board = work / 'before/project/telemetry-pod.kicad_pcb'


def facts(path):
    b = pcbnew.LoadBoard(str(path))
    fps = {}
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        pads = sorted((p.GetNumber(), p.GetNetname()) for p in fp.Pads())
        fps[ref] = {'fpid': fp.GetFPIDAsString(), 'value': fp.GetValue(), 'pads': pads,
                    'pos': [fp.GetPosition().x, fp.GetPosition().y], 'orient': fp.GetOrientationDegrees(),
                    'side': 'B' if fp.IsFlipped() else 'F', 'netted': any(n for _, n in pads)}
    ds = b.GetDesignSettings()
    tracks = list(b.GetTracks())
    return {'footprints': fps, 'nets': sorted(str(n) for n in b.GetNetsByName().keys() if str(n)),
            'copper_layers': b.GetCopperLayerCount(), 'thickness_nm': ds.GetBoardThickness(),
            'tracks': sum(t.Type() == pcbnew.PCB_TRACE_T for t in tracks), 'vias': sum(t.Type() == pcbnew.PCB_VIA_T for t in tracks),
            'zones': b.GetAreaCount()}


def text_block(path, head):
    s = Path(path).read_text()
    i = s.find(head)
    if i < 0:
        return None
    depth, j = 0, i
    while True:
        c = s[j]
        depth += c == '('
        depth -= c == ')'
        j += 1
        if depth == 0:
            return hashlib.sha256(s[i:j].encode()).hexdigest()


report = {'placed_board_exists': placed.is_file()}
b = facts(before_board)
holes = sorted(r for r, f in b['footprints'].items() if not f['netted'] and r.startswith('H'))
report['before'] = {'footprints': len(b['footprints']), 'mounting_holes': holes,
                    'electrical': len(b['footprints']) - len(holes), 'nets': len(b['nets']),
                    **{k: b[k] for k in ('copper_layers', 'thickness_nm', 'tracks', 'vias', 'zones')}}
if placed.is_file():
    a = facts(placed)
    after_tree = work / 'after'
    shutil.copytree(work / 'inputs', after_tree)
    shutil.copyfile(placed, after_tree / 'project/telemetry-pod.kicad_pcb')
    drc = subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity',
                          '-o', str(work / 'drc-after.json'), str(after_tree / 'project/telemetry-pod.kicad_pcb')],
                         capture_output=True, text=True)
    report['drc_after_exit'] = drc.returncode
    moved = sorted(r for r in b['footprints'] if r in a['footprints'] and
                   (b['footprints'][r]['pos'], b['footprints'][r]['orient'], b['footprints'][r]['side']) !=
                   (a['footprints'][r]['pos'], a['footprints'][r]['orient'], a['footprints'][r]['side']))
    report['after'] = {'footprints': len(a['footprints']), 'nets': len(a['nets']),
                       **{k: a[k] for k in ('copper_layers', 'thickness_nm', 'tracks', 'vias', 'zones')}}
    report['preservation'] = {
        'same_reference_set': set(a['footprints']) == set(b['footprints']),
        'same_fpid_and_value': all(a['footprints'][r]['fpid'] == f['fpid'] and a['footprints'][r]['value'] == f['value']
                                   for r, f in b['footprints'].items() if r in a['footprints']),
        'same_pad_nets': all(a['footprints'][r]['pads'] == f['pads'] for r, f in b['footprints'].items() if r in a['footprints']),
        'same_net_set': a['nets'] == b['nets'],
        'j1_unchanged': a['footprints'].get('J1', {}).get('pos') == b['footprints']['J1']['pos'] and
                        a['footprints']['J1']['orient'] == b['footprints']['J1']['orient'] and
                        a['footprints']['J1']['side'] == b['footprints']['J1']['side'] and
                        a['footprints']['J1']['fpid'] == b['footprints']['J1']['fpid'],
        'j1_fpid': b['footprints']['J1']['fpid'], 'j1_value': b['footprints']['J1']['value'],
        'mounting_holes_unchanged': all(a['footprints'][h]['pos'] == b['footprints'][h]['pos'] for h in holes),
        'same_copper_layers_and_thickness': (a['copper_layers'], a['thickness_nm']) == (b['copper_layers'], b['thickness_nm']),
        'stackup_block_equal': text_block(placed, '(stackup') == text_block(before_board, '(stackup'),
        'setup_block_equal_sha256': [text_block(before_board, '(setup'), text_block(placed, '(setup')],
        'moved_footprints': len(moved)}
    for name in ('telemetry-pod.kicad_pro', 'telemetry-pod.kicad_dru'):
        src, out = work / 'inputs/project' / name, work / 'placement/placed' / name.replace('telemetry-pod', 'candidate')
        report['preservation'][f'{name}_bytes_equal_in_output'] = (sha(src) == sha(out)) if out.is_file() else 'not in output'
for tag in ('before', 'after'):
    p = work / f'drc-{tag}.json'
    if p.is_file():
        d = json.loads(p.read_text())
        from collections import Counter
        report[f'drc_{tag}'] = {'violations': len(d.get('violations', [])), 'unconnected': len(d.get('unconnected_items', [])),
                                'schematic_parity': len(d.get('schematic_parity', [])),
                                'by_type': dict(Counter(v['type'] for v in d.get('violations', []))), 'sha256': sha(p)}
(work / 'checks.json').write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'setup_block_equal_sha256'}, sort_keys=True))
