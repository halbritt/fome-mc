"""Replay the released copper-feature predicate on the captured pod jumper.

This creates a native board fixture, not a placed or routed pod candidate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import pcbnew
from agent_ee.fab_export import copper_feature_problems, declared_copper_features
from agent_ee.symbol_library import parse_sexpr

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
if args.out.exists():
    raise SystemExit('Output must be fresh')
root = Path(__file__).resolve().parent
source = root.parent / 'part-bindings/prepared/inputs/footprints/Jumper.pretty/SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm.kicad_mod'
intent = json.loads((root.parent / 'component-fit/prepared/intent.json').read_text())
refs = ['JP1', 'JP2', 'JP3', 'JP4', 'JP5']
params = {'copper_features': refs}
declared_copper_features(params)
components = {c['reference']: c for c in intent['components']}
for ref in refs:
    c = components[ref]
    assert c['footprint'] == 'Jumper:' + source.stem
    assert not c.get('part_binding')
    assert c['in_bom'] is False
args.out.mkdir(parents=True)
board = pcbnew.BOARD()
for i, ref in enumerate(refs):
    fp = pcbnew.FootprintLoad(str(source.parent), source.stem)
    if fp is None:
        raise RuntimeError('Native footprint load failed')
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(10 + 5*i), pcbnew.FromMM(10)))
    board.Add(fp)
board_path = args.out / 'jumper-fixture.kicad_pcb'
pcbnew.SaveBoard(str(board_path), board)
data = board_path.read_bytes()
issues = copper_feature_problems(data, set(refs))
ast = parse_sexpr(data)
layer_nodes = []
for fp in ast[1:]:
    if not isinstance(fp, list) or not fp or fp[0] != 'footprint':
        continue
    ref = next(n[2] for n in fp if isinstance(n, list) and n[:2] == ['property', 'Reference'])
    graphics = []
    for node in fp:
        if isinstance(node, list) and node and node[0].startswith('fp_'):
            layers = [n[1] for n in node if isinstance(n, list) and n and n[0] == 'layer']
            if layers and layers[0] not in {'F.SilkS','B.SilkS','F.Fab','B.Fab'}:
                graphics.append({'kind': node[0], 'layer': layers[0]})
    layer_nodes.append({'reference': ref, 'rejected_graphics': graphics})
import agent_ee.fab_export as gate
repo = Path(gate.__file__).resolve().parents[2]
report = {'schema': 'pod-copper-gate-reproduction/1',
    'agent_ee_commit': subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'], text=True).strip(),
    'gate_source_sha256': hashlib.sha256(Path(gate.__file__).read_bytes()).hexdigest(),
    'kicad_version': pcbnew.Version(), 'footprint_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'params_fragment': params, 'predicate_problems': issues, 'graphics': layer_nodes,
    'scope': 'Native footprint fixture and released predicate only; no full fab export, netlist, BOM, CPL, placement or routing acceptance.'}
(args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'predicate_problems': issues, 'report': str(args.out / 'report.json')}))
