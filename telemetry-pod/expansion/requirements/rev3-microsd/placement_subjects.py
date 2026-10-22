#!/usr/bin/env python3
"""Check the placement-stage subject of requirement-map.json against its sources.

The placement subject must be exactly the schematic subject (the 305 microSD schematic
references) plus the envelope's board-only mounting holes, and the POD-ME-HOLES limitation
must state each hole's declared position, drill, plating and tolerance and the envelope hash,
recomputed from ../../placement-inputs/envelope.json. Exits 1 on any difference.

With --agent-ee CHECKOUT the schematic subject is also compared with
agent_ee.stages.native_references on the current microSD schematic. Each --board PCB is read
with the same reader and the stage-subject rule (expected minus observed) is printed, so a
board without the holes shows them missing. Nothing is written.

    python3 placement_subjects.py [--agent-ee CHECKOUT] [--board PCB ...]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPANSION = HERE.parents[1]
MAP = HERE / 'requirement-map.json'
ENVELOPE = EXPANSION / 'placement-inputs/envelope.json'
SCHEMATIC = EXPANSION / 'storage-microsd/project/telemetry-pod.kicad_sch'


def num(value):
    return str(int(value)) if float(value).is_integer() else str(value)


def hole_statement(hole):
    plating = 'plated' if hole['plated'] else 'non-plated (NPTH)'
    return (f"{hole['id']} centred at ({num(hole['at'][0])}, {num(hole['at'][1])}) mm, "
            f"{num(hole['drill_mm'])} mm round drill, {plating}, position tolerance {num(hole['tolerance_mm'])} mm")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--agent-ee', type=Path)
    parser.add_argument('--board', type=Path, action='append', default=[])
    args = parser.parse_args()
    scope = json.loads(MAP.read_text())['scope']
    subjects = scope['stages']['subjects']
    symbols = subjects['schematic']['references']
    placement = subjects['placement']['references']
    raw = ENVELOPE.read_bytes()
    holes = json.loads(raw)['mounting_holes']
    ids = [h['id'] for h in holes]
    failures = []
    if subjects['verification']['references'] != symbols:
        failures.append('verification subject differs from the schematic subject')
    if set(ids) & set(symbols):
        failures.append(f'mounting holes collide with schematic references: {sorted(set(ids) & set(symbols))}')
    if sorted(placement) != sorted(symbols + ids):
        failures.append('placement subject is not schematic references plus envelope holes: extra '
                        f'{sorted(set(placement) - set(symbols) - set(ids))}, missing '
                        f'{sorted(set(symbols + ids) - set(placement))}')
    holes_text = [t for t in scope['limitations'] if t.startswith('POD-ME-HOLES:')]
    if len(holes_text) != 1:
        failures.append('expected exactly one POD-ME-HOLES limitation')
    else:
        text = holes_text[0]
        for needle in [f'(sha256 {hashlib.sha256(raw).hexdigest()}, mounting_holes)',
                       f'expects {len(symbols) + len(ids)} footprints', *map(hole_statement, holes)]:
            if needle not in text:
                failures.append(f'POD-ME-HOLES does not state: {needle}')
    print(f'schematic subject {len(symbols)}; envelope holes {ids}; placement subject {len(placement)}')
    for hole in holes:
        print('  ' + hole_statement(hole))
    if args.agent_ee:
        sys.path.insert(0, str(args.agent_ee / 'src'))
        from agent_ee.stages import native_references
        native = native_references(SCHEMATIC, 'symbols')
        same = native == sorted(symbols)
        print(f'native schematic references {len(native)}: {"match" if same else "DIFFER"}')
        if not same:
            failures.append('schematic subject differs from native_references on the microSD schematic')
        for board in args.board:
            observed = native_references(board, 'footprints')
            missing = sorted(set(placement) - set(observed))
            extra = sorted(set(observed) - set(placement))
            print(f'board {board}: {len(observed)} footprints; missing expected {len(missing)} {missing}; '
                  f'unexpected (not graded) {len(extra)}')
    elif args.board:
        failures.append('--board requires --agent-ee')
    for failure in failures:
        print('FAIL:', failure)
    print('placement subjects match' if not failures else 'placement subjects DIFFER')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
