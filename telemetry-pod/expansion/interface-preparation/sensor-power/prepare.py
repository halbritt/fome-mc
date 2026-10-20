"""Prepare three isolated sensor-power branches; emit native KiCad separately."""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
if args.out.exists():
    raise SystemExit('Output must be a fresh directory')
shutil.copytree(args.base, args.out)
intent = json.loads((args.out / 'intent.json').read_text())
layout = json.loads((args.out / 'emitter-layout.json').read_text())
components = {c['reference']: c for c in intent['components']}
nets = {n['name']: n for n in intent['nets']}


def terminal(component, pin):
    return {'component': component, 'pin': {'number': str(pin)}}


def connect(name, component, pin):
    if name not in nets:
        nets[name] = {'id': 'sensor-power/' + name, 'name': name, 'terminals': []}
        intent['nets'].append(nets[name])
    nets[name]['terminals'].append(terminal(component, pin))


def clone(reference, donor, value):
    if reference in components:
        raise ValueError(f'Duplicate reference: {reference}')
    c = copy.deepcopy(components[donor])
    c.pop('part_binding', None)
    c.update(id='sensor-power/' + reference, reference=reference, value=value)
    components[reference] = c
    intent['components'].append(c)
    return c['id']


pins = [(1, 'IN', 'power_in'), (2, 'UVLO', 'input'), (3, 'OVP', 'input'),
        (4, 'SHDN', 'input'), (5, 'RTN', 'power_out'), (6, 'GND', 'power_in'),
        (7, 'ILIM', 'passive'), (8, 'dVdT', 'passive'),
        (9, 'FLT', 'open_collector'), (10, 'OUT', 'power_out'),
        (11, 'EP_RTN', 'passive')]
symbol = ['(kicad_symbol_lib (version 20231120) (generator "pod_sensor_power")',
          '(symbol "TPS26625_DRC" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)',
          '(property "Reference" "U" (at 0 12.7 0) (effects (font (size 1.27 1.27))))',
          '(property "Value" "TPS26625_DRC" (at 0 15.24 0) (effects (font (size 1.27 1.27))))',
          '(symbol "TPS26625_DRC_1_1" (rectangle (start -10.16 10.16) (end 10.16 -10.16)',
          '(stroke (width 0.254) (type default)) (fill (type background)))']
for i, (pin, label, kind) in enumerate(pins):
    x, angle = (-12.7, 0) if i < 6 else (12.7, 180)
    y = 7.62 - 2.54 * (i % 6)
    symbol.append(f'(pin {kind} line (at {x} {y:g} {angle}) (length 2.54) '
                  f'(name "{label}" (effects (font (size 1.016 1.016)))) '
                  f'(number "{pin}" (effects (font (size 1.016 1.016)))))')
symbol.append('))\n')
raw = '\n'.join(symbol).encode()
lib_path = 'authored-cad/PodSensorPower.kicad_sym'
(args.out / lib_path).write_bytes(raw)
intent['libraries'].append({'name': 'PodSensorPower', 'path': lib_path,
                            'sha256': hashlib.sha256(raw).hexdigest()})
fp = 'VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm'
fp_source = Path('/usr/share/kicad/footprints/Package_SON.pretty') / (fp + '.kicad_mod')
shutil.copyfile(fp_source, args.out / 'footprints/Package_SON.pretty' / fp_source.name)

for i, (name, jpin, limit) in enumerate([
        ('FRONT', 23, '44.2 kohm 0.1%'), ('REAR', 26, '44.2 kohm 0.1%'),
        ('TIRE', 31, '26.7 kohm 0.1%')]):
    prefix = 'SENSOR_POWER_' + name
    out_net = 'POD_TIRE_SUPPLY' if name == 'TIRE' else f'POD_WHEEL_{name}_SUPPLY'
    ref = f'U{23+i}'
    c = {'id': 'sensor-power/' + ref, 'reference': ref,
         'lib_id': 'PodSensorPower:TPS26625_DRC', 'value': 'TPS26625DRCR',
         'footprint': 'Package_SON:' + fp, 'units': [1]}
    assert ref not in components
    components[ref] = c
    intent['components'].append(c)
    group = [c['id']]
    for pin, net in {1: 'PRE_6V3', 2: prefix+'_UVLO', 3: prefix+'_OVP',
                     5: prefix+'_RTN', 6: 'GND', 7: prefix+'_ILIM',
                     8: prefix+'_DVDT', 10: out_net, 11: prefix+'_RTN'}.items():
        connect(net, c['id'], pin)
    intent['no_connects'].extend([terminal(c['id'], 4), terminal(c['id'], 9)])
    for k, (value, a, b) in enumerate([
            ('1.05 Mohm 0.1% 25ppm/K', 'PRE_6V3', prefix+'_UVLO'),
            ('68.1 kohm 0.1% 25ppm/K', prefix+'_UVLO', prefix+'_OVP'),
            ('215 kohm 0.1% 25ppm/K', prefix+'_OVP', prefix+'_RTN'),
            (limit, prefix+'_ILIM', prefix+'_RTN')]):
        cid = clone(f'R{73+i*4+k}', 'R66', value)
        group.append(cid)
        connect(a, cid, 1)
        connect(b, cid, 2)
    for k, (value, a, b) in enumerate([
            ('1uF 50V X7R', 'PRE_6V3', 'GND'),
            ('100nF 50V X7R', out_net, 'GND'),
            ('10nF 50V C0G 10%', prefix+'_DVDT', prefix+'_RTN')]):
        cid = clone(f'C{86+i*3+k}', 'C79', value)
        if k == 0:
            components[f'C{86+i*3+k}']['footprint'] = 'Capacitor_SMD:C_0805_2012Metric'
        group.append(cid)
        connect(a, cid, 1)
        connect(b, cid, 2)
    jt = terminal(components['J1']['id'], jpin)
    intent['no_connects'].remove(jt)
    connect(out_net, components['J1']['id'], jpin)
    layout['groups'].append({'id': prefix, 'title': name+' protected sensor power - validation pending',
                             'components': group})
for pin in (25, 28):
    jt = terminal(components['J1']['id'], pin)
    intent['no_connects'].remove(jt)
    connect('GND', components['J1']['id'], pin)
for name, data in [('intent.json', intent), ('emitter-layout.json', layout)]:
    (args.out / name).write_text(json.dumps(data, indent=2) + '\n')
print(args.out)
