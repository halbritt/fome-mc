"""Read-only native pad geometry for explicitly assigned bypass capacitors.
Distances are geometric lower bounds, never electrical acceptance.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import pcbnew

ASSIGNMENTS = [('U26', 'C97', '/PRE_6V3'), ('U26', 'C98', '/PRE_6V3'),
               ('U14', 'C63', '/EMMC_VDDi'), ('U14', 'C64', '/EMMC_VCC_3V3'),
               ('U14', 'C65', '/EMMC_VCC_3V3'), ('U14', 'C66', '/+3V3'),
               ('U14', 'C67', '/+3V3')]

def inspect(path):
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    board = pcbnew.LoadBoard(str(path))
    indexed = {}
    for fp in board.GetFootprints():
        indexed.setdefault(fp.GetReference(), []).append(fp)
    def unique(ref):
        found = indexed.get(ref, [])
        if len(found) != 1:
            raise ValueError(f'{ref}: expected one footprint, found {len(found)}')
        return found[0]
    def distance(a, b):
        return math.hypot(a.x-b.x, a.y-b.y)/1e6
    rows = []
    for anchor, reference, rail in ASSIGNMENTS:
        chip, cap = unique(anchor), unique(reference)
        pads = list(cap.Pads())
        if len(pads) != 2 or {str(p.GetNetname()) for p in pads} != {rail, '/GND'}:
            raise ValueError(f'{reference}: unexpected two-pad bypass connectivity')
        endpoints = {}
        for net, label in [(rail, 'supply'), ('/GND', 'ground')]:
            cp = next(p for p in pads if p.GetNetname() == net)
            matches = [p for p in chip.Pads() if p.GetNetname() == net]
            if not matches:
                raise ValueError(f'{anchor}: missing {net} pads')
            endpoints[label] = {'capacitor_pad': str(cp.GetNumber()),
                'chip_pads': [{'pad': str(p.GetNumber()), 'distance_mm': distance(p.GetPosition(), cp.GetPosition())}
                              for p in sorted(matches, key=lambda p: str(p.GetNumber()))]}
        rows.append({'anchor': anchor, 'reference': reference, 'rail': rail,
                     'origin_distance_mm': distance(chip.GetPosition(), cap.GetPosition()),
                     'same_side': chip.IsFlipped() == cap.IsFlipped(), **endpoints})
    if hashlib.sha256(path.read_bytes()).hexdigest() != before:
        raise ValueError('board bytes changed during inspection')
    return {'schema': 'pod.bypass-geometry/1', 'board_sha256': before,
            'board_unchanged': True, 'measurements': rows,
            'scope': 'Explicit U26 and U14 capacitor assignments only. Pad-center straight-line distances; no routed connectivity, loop impedance, via, plane, orientation or electrical acceptance judgment.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.board), indent=2))
