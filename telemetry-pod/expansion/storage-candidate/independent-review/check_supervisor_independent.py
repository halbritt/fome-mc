#!/usr/bin/env python3
"""Independent TPS389001 native delta and footprint review.
Usage: CURRENT_XML PRIOR_POWER_XML PRIOR_STORAGE_XML PRIOR_ADC_XML INPUTS REPORT
All previous native nets must remain identical except two designated MCU NC
terminals, exact new component memberships, and R29/C47 nominal values.
The preserved power/storage checkers are replayed after removing only this
independently verified delta on a temporary copy. No producer helper imported.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    root = ET.parse(path).getroot()
    nets, terminals = {}, {}
    for n in root.findall('./nets/net'):
        name = n.get('name').removeprefix('/')
        if name in nets:
            raise ValueError('duplicate net ' + name)
        nets[name] = set()
        for node in n.findall('node'):
            key = (node.get('ref'), node.get('pin'))
            if key in terminals:
                raise ValueError('duplicate terminal ' + str(key))
            terminals[key] = name
            nets[name].add(key)
    return root, nets, terminals


def sexpr(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack, root = [], []
    for token in tokens:
        if token == '(':
            node = []
            (stack[-1] if stack else root).append(node)
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if stack or len(root) != 1:
        raise ValueError('malformed footprint')
    return root[0]


def item(node, key):
    return next((x for x in node if isinstance(x, list) and x and x[0] == key), None)


def number(node, key):
    value = item(node, key)
    return float(value[1]) if value else None


def nominal(value):
    value = value or ''
    match = re.match(r'^\s*([0-9.]+)\s*(kohm|kΩ|kOhm|k|ohm|Ω|nF|uF|µF|mF|F)\b', value)
    if not match:
        return None
    factor = {'kohm': 1e3, 'kΩ': 1e3, 'kOhm': 1e3, 'k': 1e3, 'ohm': 1, 'Ω': 1, 'nF': 1e-9, 'uF': 1e-6, 'µF': 1e-6, 'mF': 1e-3, 'F': 1}[match[2]]
    return float(match[1]) * factor


def main():
    current, prior, prior_storage, prior_adc, inputs, output = map(Path, sys.argv[1:])
    here = Path(__file__).resolve().parent
    root, nets, terminals = read(current)
    oldroot, oldnets, oldterm = read(prior)
    checks, failures = [], []

    def check(label, condition, actual=None, expected=None):
        checks.append(label)
        if not condition:
            failures.append({'check': label, 'actual': actual, 'expected': expected})

    added = {f'U{i}' for i in range(16, 20)} | {f'R{i}' for i in range(56, 66)} | {f'C{i}' for i in range(71, 79)}
    expected = copy.deepcopy(oldnets)
    for terminal in [('U1', '25'), ('U1', '12')]:
        name = oldterm.get(terminal)
        check('reassigned host was isolated ' + str(terminal), name is not None and name.startswith('unconnected-') and oldnets.get(name) == {terminal}, name, 'NC singleton')
        if name in expected:
            del expected[name]
    expected.setdefault('SENSOR_FAULT_N', set()).update({('U1', '25'), ('R64', '2'), ('U18', '6')})
    expected.setdefault('POWER_FAIL_N', set()).update({('U1', '12'), ('R65', '2'), ('U19', '6')})
    expected['+3V3'].update({('R64', '1'), ('R65', '1')})
    expected['MCU_EN'].update({('U16', '6'), ('U17', '6')})
    channel_sources = ['+3V3', 'EMMC_VCC_3V3', 'POD_5V_SENSOR', 'POD_12V_PROTECTED']
    new_internal = []
    for index, source in enumerate(channel_sources):
        u, rt, rb = f'U{16+index}', f'R{56+2*index}', f'R{57+2*index}'
        ct, bypass = f'C{71+2*index}', f'C{72+2*index}'
        expected[source].add((rt, '1'))
        expected['+3V3'].update({(u, '3'), (u, '4'), (bypass, '1')})
        expected['GND'].update({(u, '2'), (rb, '2'), (ct, '2'), (bypass, '2')})
        for pin, members in [('1', {(u, '1'), (rt, '2'), (rb, '1')}), ('5', {(u, '5'), (ct, '1')})]:
            name = terminals.get((u, pin))
            check('new isolated internal node ' + u + '.' + pin, name is not None and name not in oldnets and name not in new_internal, name, 'unique new sense or CT net')
            if name is not None:
                expected[name] = members
                new_internal.append(name)
    check('exact complete net set', set(nets) == set(expected), sorted(set(nets) ^ set(expected)), [])
    for name in sorted(set(nets) | set(expected)):
        check('exact members ' + name, nets.get(name) == expected.get(name), sorted(nets.get(name, set())), sorted(expected.get(name, set())))
    changes = {key: (before, terminals.get(key)) for key, before in oldterm.items() if terminals.get(key) != before}
    allowed = {('U1', '25'): (oldterm.get(('U1', '25')), 'SENSOR_FAULT_N'), ('U1', '12'): (oldterm.get(('U1', '12')), 'POWER_FAIL_N')}
    check('only two prior NC reassignments', changes == allowed, [[list(k), *v] for k, v in sorted(changes.items())], [[list(k), *v] for k, v in sorted(allowed.items())])
    c_list = root.findall('./components/comp')
    comps = {c.get('ref'): c for c in c_list}
    oldcomps = {c.get('ref'): c for c in oldroot.findall('./components/comp')}
    check('unique component refs', len(comps) == len(c_list), len(comps), len(c_list))
    check('exact22 component additions', set(comps) == set(oldcomps) | added, sorted(set(comps) ^ (set(oldcomps) | added)), [])
    values = {'R29': 100e3, 'C47': 10e-9, 'R64': 10e3, 'R65': 10e3}
    for index, top in enumerate([16900., 15200., 31300., 64900.]):
        values.update({f'R{56+2*index}': top, f'R{57+2*index}': 10e3, f'C{71+2*index}': 22e-9, f'C{72+2*index}': 100e-9})
    for ref, value in values.items():
        printed = comps[ref].findtext('value') if ref in comps else None
        parsed = nominal(printed)
        check('nominal value ' + ref, parsed is not None and math.isclose(parsed, value, rel_tol=1e-9), printed, value)
    for ref, old in oldcomps.items():
        for field in ['footprint'] + ([] if ref in {'R29', 'C47'} else ['value']):
            actual = comps[ref].findtext(field) if ref in comps else None
            check('preserve ' + ref + ' ' + field, actual == old.findtext(field), actual, old.findtext(field))
    libparts = {(x.get('lib'), x.get('part')): x for x in root.findall('./libparts/libpart')}
    for ref in [f'U{i}' for i in range(16, 20)]:
        c = comps.get(ref)
        check('exact supervisor part ' + ref, c is not None and c.findtext('value') == 'TPS389001DSER', c.findtext('value') if c is not None else None, 'TPS389001DSER')
        libsource = c.find('libsource') if c is not None else None
        lib = libparts.get((libsource.get('lib'), libsource.get('part'))) if libsource is not None else None
        pinlist = lib.findall('./pins/pin') if lib is not None else []
        pmap = {p.get('num'): re.sub(r'[~{}]', '', p.get('name', '')) for p in pinlist}
        check('six pins no EP ' + ref, len(pinlist) == 6 and pmap == {'1': 'SENSE', '2': 'GND', '3': 'MR', '4': 'VDD', '5': 'CT', '6': 'RESET'}, pmap, 'SENSE1 GND2 MR3 VDD4 CT5 RESET6')
        check('supervisor footprint ' + ref, c is not None and c.findtext('footprint') == 'PodSupervisor:DSE0006A', c.findtext('footprint') if c is not None else None, 'PodSupervisor:DSE0006A')

    fp = inputs / 'footprints/PodSupervisor.pretty/DSE0006A.kicad_mod'
    footprint = sexpr(fp.read_text())
    pads = [x for x in footprint if isinstance(x, list) and x and x[0] == 'pad']
    pmap = {p[1]: p for p in pads}
    check('six physical pads no EP', len(pads) == 6 and set(pmap) == set('123456'), sorted(pmap), list('123456'))
    for n, x, y, w, h, margin, paste, radius in [
        ('1', -.55, -.5, .9, .35, -.05, -.05, .1),
        ('2', -.6, 0., .8, .35, -.05, -.05, .1),
        ('3', -.6, .5, .8, .35, -.05, -.05, .1),
        ('4', .6, .5, .7, .25, .05, 0., .05),
        ('5', .6, 0., .7, .25, .05, 0., .05),
        ('6', .6, -.5, .7, .25, .05, 0., .05),
    ]:
        p = pmap.get(n, [])
        at, size = item(p, 'at'), item(p, 'size')
        actual = tuple(map(float, at[1:])) if at else ()
        check('pad position ' + n, actual in [(x, y), (x, y, 0.)], actual, (x, y))
        actual_size = tuple(map(float, size[1:])) if size else ()
        check('pad copper ' + n, actual_size == (w, h), actual_size, (w, h))
        for field, value in [('solder_mask_margin', margin), ('solder_paste_margin', paste)]:
            actual_margin = number(p, field)
            if actual_margin is None and value == 0.:
                actual_margin = 0.
            check('pad ' + field + ' ' + n, actual_margin == value, actual_margin, value)
        ratio = number(p, 'roundrect_rratio')
        actual_radius = ratio * min(w, h) if ratio is not None else None
        check('pad copper radius ' + n, actual_radius is not None and math.isclose(actual_radius, radius, abs_tol=1e-6), actual_radius, radius)
    # Geometry remains an explicit interpretation of the mixed-mask source.
    corners = []
    for node in footprint:
        if isinstance(node, list) and node and node[0] in {'fp_rect', 'fp_line'} and item(node, 'layer') == ['layer', 'F.CrtYd']:
            for key in ['start', 'end']:
                found = item(node, key)
                if found:
                    corners.append(tuple(map(float, found[1:])))
    extents = (min(x for x, y in corners), max(x for x, y in corners), min(y for x, y in corners), max(y for x, y in corners)) if corners else None
    check('candidate courtyard', extents == (-1.25, 1.25, -1.05, 1.05), extents, (-1.25, 1.25, -1.05, 1.05))

    normalized = copy.deepcopy(root)
    cp = normalized.find('components')
    for c in list(cp):
        if c.get('ref') in added:
            cp.remove(c)
        elif c.get('ref') in {'R29', 'C47'}:
            c.find('value').text = oldcomps[c.get('ref')].findtext('value')
    np = normalized.find('nets')
    reassigned = set(allowed)
    restore_nodes = {}
    for net in list(np):
        for node in list(net):
            key = (node.get('ref'), node.get('pin'))
            if key[0] in added or key in reassigned:
                net.remove(node)
                if key in reassigned:
                    restore_nodes[key] = node
        if not list(net):
            np.remove(net)
    for key, node in restore_nodes.items():
        n = ET.SubElement(np, 'net', {'name': oldterm[key], 'code': 'restored-supervisor-review-only-' + key[1]})
        n.append(node)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='replay-') as tmp:
        temp = Path(tmp)
        scripts = temp / 'independent-review'
        scripts.mkdir()
        for name in ['check_power_independent.py', 'storage_contract.py']:
            shutil.copyfile(here / name, scripts / name)
        (temp / 'inputs').symlink_to(inputs.resolve(), target_is_directory=True)
        xml, report = temp / 'normalized.xml', temp / 'power.json'
        ET.ElementTree(normalized).write(xml)
        p = subprocess.run([sys.executable, str(scripts / 'check_power_independent.py'), str(xml), str(prior_storage), str(prior_adc), str(report)], text=True, capture_output=True)
        replay = json.loads(report.read_text()) if report.exists() else {'status': 'ERROR', 'stderr': p.stderr}
        check('full previous power/storage contract replay', p.returncode == 0 and replay.get('status') == 'PASS', replay.get('failures', replay), 'PASS')
    result = {'status': 'FAIL' if failures else 'PASS', 'check_count': len(checks), 'checks': checks, 'failures': failures,
              'previous_contract_replay': replay,
              'inputs': {label: {'path': str(path), 'sha256': sha(path)} for label, path in [('current', current), ('prior_power', prior), ('prior_storage', prior_storage), ('prior_adc', prior_adc), ('footprint', fp), ('power_contract', here / 'check_power_independent.py'), ('storage_contract', here / 'storage_contract.py')]},
              'checker_sha256': sha(Path(__file__)),
              'replay_scope_note': 'Nested power/storage reports describe a normalized historical predecessor with verified supervisor additions removed. Their open conditions do not describe the current supervisor candidate.',
              'scope': 'Independent complete native graph delta, nominal components, six-pin supervisor identity and explicit candidate footprint geometry; previous power and complete storage contracts replayed.',
              'limitations': ['Footprint left copper growth/mask opening is an explicit interpretation of ambiguous TI drawing, not literal manufacturer copper qualification', 'Resistor0.1% assumption, TCR, capacitor leakage/effective capacitance and passive procurement remain unqualified', 'No transient, startup waveform, hold-up, thermal, SI, assembly, firmware fault response or physical acceptance claim']}
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'check_count': len(checks), 'failures': failures, 'prior_replay': replay.get('check_count')}))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
