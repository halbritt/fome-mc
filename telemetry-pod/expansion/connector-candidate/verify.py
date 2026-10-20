"""Check source custody and native KiCad footprint/drill output, not pod acceptance."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pcbnew
from prepare import ROOT, NAME, footprint


def mm(v):
    return round(pcbnew.ToMM(v), 6)


def inspect(fp, expected):
    pads = list(fp.Pads())
    assert len(pads) == 37, '35 contacts and two locators required'
    numbered = {p.GetNumber(): p for p in pads if p.GetNumber()}
    assert len(numbered) == 35, 'unique contact numbers required'
    for want in expected['pads']:
        p = numbered[str(want['number'])]
        assert p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH, 'contact plating'
        assert (mm(p.GetPosition().x), mm(p.GetPosition().y)) == (want['x_mm'], want['y_mm']), 'contact position'
        assert (mm(p.GetDrillSize().x), mm(p.GetDrillSize().y)) == (1.75, 1.75), 'contact finished-hole target'
        assert (mm(p.GetSize().x), mm(p.GetSize().y)) == (2.4, 2.4), 'contact land'
    locators = [p for p in pads if not p.GetNumber()]
    assert sorted((mm(p.GetPosition().x), mm(p.GetPosition().y)) for p in locators) == [tuple(x) for x in expected['locator_centers_mm']], 'locator position'
    for p in locators:
        assert p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH, 'locator must be unplated'
        assert (mm(p.GetDrillSize().x), mm(p.GetDrillSize().y)) == (2.85, 2.85), 'locator diameter'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, help='Fresh directory for native fixture and exports')
    args = parser.parse_args()
    if args.out is not None and args.out.exists():
        raise ValueError('Evidence directory must be fresh')
    for row in json.loads((ROOT / 'sources.json').read_text()):
        assert hashlib.sha256((ROOT / row['file']).read_bytes()).hexdigest() == row['sha256'], 'source hash'
    with zipfile.ZipFile(ROOT / 'sources/1-776163-1-T.zip') as z:
        assert z.read('c-1-776163-1-t-3d.stp') == (ROOT / 'sources/c-1-776163-1-t-3d.stp').read_bytes(), 'STEP extraction'
    library = ROOT / 'PodConnector.pretty'
    assert (library / f'{NAME}.kicad_mod').read_text() == footprint(), 'generator reproduction'
    expected = json.loads((ROOT / 'review/coordinates.json').read_text())
    fp = pcbnew.FootprintLoad(str(library), NAME)
    assert fp is not None, 'native footprint load'
    inspect(fp, expected)
    probes = {}
    for name in ['panel_hole', 'wrong_locator_offset', 'reversed_numbering']:
        bad = pcbnew.FootprintLoad(str(library), NAME)
        p = next(p for p in bad.Pads() if p.GetNumber() == ('1' if name == 'reversed_numbering' else ''))
        if name == 'panel_hole':
            p.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(2), pcbnew.FromMM(2)))
        elif name == 'wrong_locator_offset':
            p.SetPosition(pcbnew.VECTOR2I(p.GetPosition().x, pcbnew.FromMM(-0.5)))
        else:
            p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(22), pcbnew.FromMM(4)))
        try:
            inspect(bad, expected)
        except AssertionError:
            probes[name] = 'REJECTED'
        else:
            raise AssertionError(f'negative probe accepted: {name}')
    with tempfile.TemporaryDirectory(prefix='pod-connector-native-') as temp:
        out = Path(temp)
        board = pcbnew.BOARD()
        fp.SetReference('J1')
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(45), pcbnew.FromMM(55.5)))
        board.Add(fp)
        points = [(0, 0), (90, 0), (90, 65), (0, 65)]
        for a, b in zip(points, points[1:] + points[:1]):
            edge = pcbnew.PCB_SHAPE()
            edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
            edge.SetLayer(pcbnew.Edge_Cuts)
            edge.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1])))
            edge.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(b[0]), pcbnew.FromMM(b[1])))
            edge.SetWidth(pcbnew.FromMM(0.05))
            board.Add(edge)
        board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.57))
        pcbnew.SaveBoard(str(out / 'connector.kicad_pcb'), board)
        (out / 'inputs/models').mkdir(parents=True)
        shutil.copyfile(ROOT / 'sources/c-1-776163-1-t-3d.stp', out / 'inputs/models/c-1-776163-1-t-3d.stp')
        subprocess.run(['kicad-cli', 'pcb', 'export', 'drill', '--excellon-separate-th', '--output', str(out / 'drills'), str(out / 'connector.kicad_pcb')], check=True, capture_output=True, text=True)
        drills = list((out / 'drills').glob('*.drl'))
        summary = {}
        for path in drills:
            text = path.read_text()
            hits = {(float(x), float(y)) for x, y in re.findall(r'^X([-\d.]+)Y([-\d.]+)$', text, re.M)}
            target = ({(r['x_mm'] + 45, -r['y_mm'] - 55.5) for r in expected['pads']}
                      if path.name == 'connector-PTH.drl' else {(x + 45, -y - 55.5) for x, y in expected['locator_centers_mm']})
            assert hits == target, 'native drill coordinates'
            summary[path.name] = {'diameters_mm': re.findall(r'^T\d+C([\d.]+)', text, re.M), 'hits': len(re.findall(r'^X[-\d.]+Y[-\d.]+$', text, re.M))}
        pth = summary['connector-PTH.drl']
        npth = summary['connector-NPTH.drl']
        assert pth == {'diameters_mm': ['1.750'], 'hits': 35}, pth
        assert npth == {'diameters_mm': ['2.850'], 'hits': 2}, npth
        result = subprocess.run(['kicad-cli', 'pcb', 'export', 'step', '--output', str(out / 'connector.step'), str(out / 'connector.kicad_pcb')], check=True, capture_output=True, text=True)
        (out / 'step-export.log').write_text(result.stdout + result.stderr)
        assert (out / 'connector.step').stat().st_size > 100000, 'STEP export absent or unexpectedly small'
        if args.out is not None:
            shutil.copytree(out, args.out)
    print(json.dumps({'status': 'PASS', 'native_version': pcbnew.GetBuildVersion(), 'drills': summary, 'negative_controls': probes, 'limits': 'Standalone footprint only; no complete pod DRC, assembled fit or fabrication acceptance'}, indent=2))


if __name__ == '__main__':
    main()
