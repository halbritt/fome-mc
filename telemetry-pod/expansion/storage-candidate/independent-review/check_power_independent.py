#!/usr/bin/env python3
"""Check actual power delta, then replay complete independent storage checks.
Args: CURRENT PRIOR_STORAGE PRIOR_ADC REPORT
Uses sibling storage_contract.py and ../inputs/footprints/PodStoragePower.pretty/
SRP4020TA.kicad_mod (scratch preparation fallback: ../storage-power-inputs).
Writes scratch only beside REPORT; normalized temporary XML is deleted.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path):
    root = ET.parse(path).getroot()
    nets = {}
    pins = {}
    for n in root.findall('./nets/net'):
        name = n.get('name').removeprefix('/')
        if name in nets:
            raise ValueError('duplicate net ' + name)
        nets[name] = set()
        for z in n.findall('node'):
            key = (z.get('ref'), z.get('pin'))
            if key in pins:
                raise ValueError('duplicate terminal ' + str(key))
            pins[key] = name
            nets[name].add(key)
    return root, nets, pins


def main():
    current, previous, adc, output = map(Path, sys.argv[1:])
    here = Path(__file__).resolve().parent
    checker = here / 'storage_contract.py'
    inputs = here.parent / 'inputs'
    if not inputs.is_dir():
        inputs = here.parent / 'storage-power-inputs'
    footprint = inputs / 'footprints/PodStoragePower.pretty/SRP4020TA.kicad_mod'
    root, nets, pins = parse(current)
    oldroot, oldnets, oldpins = parse(previous)
    failures, checks = [], []

    def check(label, ok, actual=None, expected=None):
        checks.append(label)
        if not ok:
            failures.append({'check': label, 'actual': actual, 'expected': expected})

    added_refs = {'U15', 'L4', 'C68', 'C69', 'C70'}
    expected = copy.deepcopy(oldnets)
    old_io = expected.pop('EMMC_VCCQ_3V3')
    expected['+3V3'] |= old_io
    expected['PRE_6V3'] |= {('U15', '2'), ('U15', '3'), ('C70', '1')}
    expected['EMMC_VCC_3V3'] |= {('U15', '6'), ('L4', '2'), ('C68', '1'), ('C69', '1')}
    expected['GND'] |= {('U15', p) for p in ('1', '4', '5', '9')} | {(c, '2') for c in ('C68', 'C69', 'C70')}
    expected['EMMC_CORE_SW'] = {('U15', '7'), ('L4', '1')}
    pg = pins.get(('U15', '8'))
    check('PG explicit isolated NC', pg is not None and pg.startswith('unconnected-') and nets.get(pg) == {('U15', '8')}, pg, 'singleton NC')
    if pg is not None:
        expected[pg] = {('U15', '8')}
    check('exact full native net names', set(nets) == set(expected), sorted(set(nets) ^ set(expected)), [])
    for name in sorted(set(nets) | set(expected)):
        check('complete members ' + name, nets.get(name) == expected.get(name), sorted(nets.get(name, set())), sorted(expected.get(name, set())))
    changed = {terminal: (name, pins.get(terminal)) for terminal, name in oldpins.items() if pins.get(terminal) != name}
    changes_expected = {terminal: ('EMMC_VCCQ_3V3', '+3V3') for terminal in old_io}
    check('only prior VCCQ terminals renamed', changed == changes_expected, [[list(k), *v] for k, v in sorted(changed.items())], [[list(k), *v] for k, v in sorted(changes_expected.items())])
    components = root.findall('./components/comp')
    comps = {c.get('ref'): c for c in components}
    oldcomps = {c.get('ref'): c for c in oldroot.findall('./components/comp')}
    check('unique refs', len(comps) == len(components), len(comps), len(components))
    check('exact five new refs', set(comps) == set(oldcomps) | added_refs, sorted(set(comps) ^ (set(oldcomps) | added_refs)), [])
    for ref in oldcomps:
        for field in ('value', 'footprint'):
            check('preserved ' + ref + ' ' + field, ref in comps and comps[ref].findtext(field) == oldcomps[ref].findtext(field), comps[ref].findtext(field) if ref in comps else None, oldcomps[ref].findtext(field))
    for ref, value in {'U15': 'TPS62162QDSGRQ1', 'L4': '2.2 uH', 'C68': '22 uF/25 V', 'C69': '22 uF/25 V', 'C70': '22 uF/25 V'}.items():
        actual = comps[ref].findtext('value') if ref in comps else None
        check('new nominal value ' + ref, actual == value, actual, value)
    u15 = next((s for s in root.findall('./libparts/libpart') if s.get('part') == 'TPS62162DSG'), None)
    mapping = {p.get('num'): p.get('name') for p in u15.findall('./pins/pin')} if u15 is not None else {}
    pinmap = {'1': 'PGND', '2': 'VIN', '3': 'EN', '4': 'AGND', '5': 'FB', '6': 'VOS', '7': 'SW', '8': 'PG', '9': 'PAD'}
    check('TPS62162 complete pinmap', mapping == pinmap, mapping, pinmap)
    text = footprint.read_text()
    pads = re.findall(r'\(pad "(\d+)" smd rect \(at ([-\d.]+) ([-\d.]+)\) \(size ([-\d.]+) ([-\d.]+)\)', text)
    padmap = {num: tuple(map(float, (x, y, w, h))) for num, x, y, w, h in pads}
    check('Bourns recommended copper', len(pads) == 2 and padmap == {'1': (-1.85, 0., 1.5, 2.4), '2': (1.85, 0., 1.5, 2.4)}, padmap, '5.2mm outer width,2.2mm gap,2.4mm height')
    check('Bourns maxbody courtyard', '(start -2.85 -2.405) (end 2.85 2.405)' in text, 'source courtyard', '5.7x4.81mm; copper and max body plus0.25mm')

    # Restore only the separately verified power delta on a temporary XML copy.
    # This lets the prior independently-transcribed324-check contract inspect
    # all storage ball functions, isolated pins, values, and pre-storage wiring.
    normalized = copy.deepcopy(root)
    comp_parent = normalized.find('components')
    for c in list(comp_parent):
        if c.get('ref') in added_refs:
            comp_parent.remove(c)
    net_parent = normalized.find('nets')
    restored = ET.Element('net', {'name': '/EMMC_VCCQ_3V3', 'code': 'restored-review-only'})
    for net in list(net_parent):
        for node in list(net):
            terminal = (node.get('ref'), node.get('pin'))
            if terminal[0] in added_refs:
                net.remove(node)
            elif terminal in old_io:
                net.remove(node)
                restored.append(node)
        if not list(net):
            net_parent.remove(net)
    net_parent.append(restored)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='normalized-review-') as folder:
        xml = Path(folder) / 'normalized.xml'
        report = Path(folder) / 'storage.json'
        ET.ElementTree(normalized).write(xml)
        result = subprocess.run([sys.executable, str(checker), str(xml), str(adc), str(report)], capture_output=True, text=True)
        inherited = json.loads(report.read_text()) if report.exists() else {'status': 'ERROR', 'stderr': result.stderr}
        check('complete storage contract replay', result.returncode == 0 and inherited.get('status') == 'PASS', inherited.get('failures', inherited), 'PASS')
    payload = {'status': 'FAIL' if failures else 'PASS', 'check_count': len(checks), 'checks': checks, 'failures': failures,
               'storage_contract_replay': inherited,
               'inputs': {label: {'path': str(path), 'sha256': sha(path)} for label, path in [('current', current), ('previous_storage', previous), ('previous_adc', adc), ('storage_checker', checker), ('inductor_footprint', footprint)]},
               'checker_sha256': sha(Path(__file__)),
               'scope': 'Independent full native graph delta, nominal component values, regulator pinmap, Bourns copper and previous complete storage contract replay. Not power/thermal/assembly acceptance.',
               'open_conditions': ['No supervisor or hold-up implemented', 'Exact passive bindings and effective capacitance unresolved', 'Power sequencing, whole power budget, thermal, SI and assembly qualification remain open']}
    output.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({'status': payload['status'], 'check_count': len(checks), 'failures': failures, 'storage_replay': inherited.get('check_count')}))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
