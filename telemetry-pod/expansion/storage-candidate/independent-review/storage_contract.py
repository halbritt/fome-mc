#!/usr/bin/env python3
"""Independent wiring review of the unpowered FORESEE storage candidate.

Contract transcribed from FORESEE A-00093 v1.0 pp6-7,18 and the accepted
six-terminal host allocation. Does not read the generator's migration map.
Usage: check_storage_independent.py CURRENT.xml PREVIOUS.xml REPORT.json
No power, assembly, passive procurement, endurance, or hardware acceptance.
"""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    root = ET.parse(path).getroot()
    nets, pins, duplicates = {}, {}, []
    for net in root.findall('./nets/net'):
        name = net.attrib['name'].removeprefix('/')
        nodes = [(node.attrib['ref'], node.attrib['pin']) for node in net.findall('node')]
        if name in nets:
            duplicates.append(['net', name])
        nets[name] = set(nodes)
        for terminal in nodes:
            if terminal in pins:
                duplicates.append(['terminal', *terminal])
            pins[terminal] = name
    components = root.findall('./components/comp')
    return root, nets, pins, components, duplicates


def main():
    current, previous, output = map(Path, sys.argv[1:])
    root, nets, pins, components, duplicates = read(current)
    _, oldnets, oldpins, oldcomponents, oldduplicates = read(previous)
    checks, failures = [], []

    def check(name, condition, actual=None, expected=None):
        checks.append(name)
        if not condition:
            failures.append({'check': name, 'actual': actual, 'expected': expected})

    check('current unique nets and terminals', not duplicates, duplicates, [])
    check('previous unique nets and terminals', not oldduplicates, oldduplicates, [])

    # Physical populated-ball pattern from manufacturer top-through-package view.
    rows = {
        **{r: list(range(1, 15)) for r in 'ABCMNP'},
        'D': [1, 2, 3, 4, 12, 13, 14],
        **{r: [1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 14] for r in 'EK'},
        **{r: [1, 2, 3, 5, 10, 12, 13, 14] for r in 'FGHJ'},
        'L': [1, 2, 3, 12, 13, 14],
    }
    contract = {f'{r}{n}': ('NC', 'no_connect') for r, cols in rows.items() for n in cols}
    for index, ball in enumerate('A3 A4 A5 B2 B3 B4 B5 B6'.split()):
        contract[ball] = (f'DAT{index}', 'bidirectional')
    for name, kind, balls in [
        ('CMD', 'bidirectional', 'M5'), ('CLK', 'input', 'M6'),
        ('DS', 'output', 'H5'), ('RSTN', 'input', 'K5'), ('VDDi', 'passive', 'C2'),
        ('VCC', 'power_in', 'E6 F5 J10 K9'),
        ('VCCQ', 'power_in', 'C6 M4 N4 P3 P5'),
        ('VSS', 'power_in', 'A6 E7 G5 H10 J5 K8'),
        ('VSSQ', 'power_in', 'C4 N2 N5 P4 P6'),
        ('RFU', 'no_connect', 'A7 E5 G3 K6 K7'),
        ('VSF', 'no_connect', 'E8 E9 E10 F10 G10 K10 P10'),
    ]:
        for ball in balls.split():
            contract[ball] = (name, kind)
    check('independent contract has153 balls', len(contract) == 153, len(contract), 153)
    symbols = [s for s in root.findall('./libparts/libpart') if s.attrib.get('part') == 'FEMDME008G-A8A39']
    check('one exact storage symbol', len(symbols) == 1, len(symbols), 1)
    actualpins = symbols[0].findall('./pins/pin') if len(symbols) == 1 else []
    actual = {p.attrib['num']: (p.attrib.get('name'), p.attrib.get('type')) for p in actualpins}
    check('153 unique symbol balls', len(actualpins) == len(actual) == 153, [len(actualpins), len(actual)], [153, 153])
    check('complete ball membership', set(actual) == set(contract), sorted(set(actual) ^ set(contract)), [])
    for ball, function in sorted(contract.items()):
        check('ball function ' + ball, actual.get(ball) == function, actual.get(ball), function)
    exported_balls = {pin for ref, pin in pins if ref == 'U14'}
    check('all153 balls represented in native nets', exported_balls == set(contract), sorted(exported_balls ^ set(contract)), [])
    isolated = {ball for ball, (name, _) in contract.items() if name in {'NC', 'RFU', 'VSF', 'RSTN'}}
    check('121 intentionally isolated balls', len(isolated) == 121, len(isolated), 121)
    for ball in sorted(isolated):
        name = pins.get(('U14', ball))
        members = nets.get(name, set())
        check('isolated ' + ball, name is not None and name.startswith('unconnected-') and members == {('U14', ball)}, [name, sorted(members)], ['unconnected singleton', [('U14', ball)]])

    expected = {}
    host = [('CLK', 'M6', '31'), ('CMD', 'M5', '32'), ('DAT0', 'A3', '33'), ('DAT1', 'A4', '34'), ('DAT2', 'A5', '35'), ('DAT3', 'B2', '24')]
    for label, ball, terminal in host:
        expected['EMMC_' + label] = {('U14', ball), ('U1', terminal)}
    for index, ball in enumerate('B3 B4 B5 B6'.split(), 4):
        expected['EMMC_DAT' + str(index)] = {('U14', ball)}
    expected['EMMC_VCC_3V3'] = {('U14', b) for b in 'E6 F5 J10 K9'.split()}
    expected['EMMC_VCCQ_3V3'] = {('U14', b) for b in 'C6 M4 N4 P3 P5'.split()}
    for ref, label in zip(range(46, 55), ['CMD'] + [f'DAT{i}' for i in range(8)]):
        expected['EMMC_' + label].add((f'R{ref}', '2'))
        expected['EMMC_VCCQ_3V3'].add((f'R{ref}', '1'))
    expected['EMMC_DS'] = {('U14', 'H5'), ('R55', '1')}
    expected['EMMC_VDDi'] = {('U14', 'C2')}
    added_ground = {('U14', b) for b in 'A6 E7 G5 H10 J5 K8 C4 N2 N5 P4 P6'.split()} | {('R55', '2')}
    for ref, rail in [(63, 'VDDi'), (64, 'VCC_3V3'), (65, 'VCC_3V3'), (66, 'VCCQ_3V3'), (67, 'VCCQ_3V3')]:
        expected['EMMC_' + rail].add((f'C{ref}', '1'))
        added_ground.add((f'C{ref}', '2'))
    expected['GND'] = oldnets.get('GND', set()) | added_ground
    for name, members in sorted(expected.items()):
        check('exact net members ' + name, nets.get(name) == members, sorted(nets.get(name, set())), sorted(members))
    check('no additional EMMC nets', {n for n in nets if n.startswith('EMMC_')} == set(expected) - {'GND'}, sorted(n for n in nets if n.startswith('EMMC_')), sorted(set(expected) - {'GND'}))

    values = {f'R{i}': '10 kohm' for i in range(46, 56)}
    values.update({'C63': '1 uF/16 V', 'C64': '4.7 uF/16 V X7R', 'C65': '100nF', 'C66': '4.7 uF/16 V X7R', 'C67': '100nF', 'U14': 'FEMDME008G-A8A39'})
    component_map = {c.attrib['ref']: c for c in components}
    check('unique component references', len(component_map) == len(components), [len(component_map), len(components)], 'equal')
    oldrefs = {c.attrib['ref'] for c in oldcomponents}
    check('exact component additions', set(component_map) == oldrefs | set(values), sorted(set(component_map) ^ (oldrefs | set(values))), [])
    for ref, value in sorted(values.items()):
        found = component_map[ref].findtext('value') if ref in component_map else None
        check('nominal value ' + ref, found == value, found, value)
    storage = component_map.get('U14')
    check('exact footprint identity', storage is not None and storage.findtext('footprint') == 'Package_BGA:LFBGA-153_11.5x13mm_Layout14x14_P0.5mm', storage.findtext('footprint') if storage is not None else None, 'Package_BGA:LFBGA-153_11.5x13mm_Layout14x14_P0.5mm')
    changes = {key: (before, pins.get(key)) for key, before in oldpins.items() if pins.get(key) != before}
    expected_changes = {('U1', terminal): (oldpins.get(('U1', terminal)), 'EMMC_' + label) for label, _, terminal in host}
    check('only six intended existing terminals changed', changes == expected_changes, [[list(k), *v] for k, v in sorted(changes.items())], [[list(k), *v] for k, v in sorted(expected_changes.items())])
    for _, _, terminal in host:
        before = oldpins.get(('U1', terminal), '')
        check('host terminal previously isolated ' + terminal, before.startswith('unconnected-') and oldnets.get(before) == {('U1', terminal)}, before, 'isolated NC singleton')
    report = {
        'status': 'FAIL' if failures else 'PASS', 'check_count': len(checks),
        'checks': checks, 'failures': failures,
        'inputs': {'current': {'path': str(current), 'sha256': digest(current)}, 'previous': {'path': str(previous), 'sha256': digest(previous)}},
        'checker_sha256': digest(Path(__file__)),
        'contract_sources': ['FORESEE FEMDME008G-A8A39 A-00093 v1.0 pp6-7 Figure1/Table2; p18 Table11', 'Accepted GPIO allocation: six SDMMC terminals31/32/33/34/35/24'],
        'scope': 'Independent native connectivity, symbol membership/functions, nominal passive values, exact storage net members, preservation of previous terminals. No wiring defect if PASS.',
        'open_conditions': ['VCC and VCCQ intentionally undriven; two native ERC power-input errors remain open', 'Existing J1 missing-footprint warning remains open', 'RFU/VSF final manufacturer disposition and reset policy unresolved', 'Exact passive procurement/ratings, power/hold-up/SI/assembly/endurance/physical acceptance not established'],
    }
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'check_count': len(checks), 'failures': failures, 'report': str(output)}))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
