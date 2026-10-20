"""Add optional thermistor excitation to the integrated expanded-pod sources."""
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
if args.out.exists():
    raise SystemExit('Output must be a fresh directory')
# Always start with the reviewed connector and latest frozen auxiliary circuit.
subprocess.run([sys.executable, str(root.parent/'integration/prepare.py'),
                '--out', str(args.out)], check=True, capture_output=True)
# This receipt describes the baseline, not the additions made below.
(args.out/'integration-receipt.json').rename(args.out/'pre-thermistor-integration-receipt.json')
d = json.loads((args.out/'intent.json').read_text())
layout = json.loads((args.out/'emitter-layout.json').read_text())
cs = {c['reference']: c for c in d['components']}
ns = {n['name']: n for n in d['nets']}
added = []


def term(cid, pin):
    return {'component': cid, 'pin': {'number': str(pin)}}


def net(name, cid, pin):
    if name not in ns:
        ns[name] = {'id': 'thermistor/'+name, 'name': name, 'terminals': []}
        d['nets'].append(ns[name])
    ns[name]['terminals'].append(term(cid, pin))


def add(ref, value, donor=None, lib=None, footprint=None):
    if ref in cs:
        raise ValueError('Duplicate reference: '+ref)
    c = copy.deepcopy(cs[donor]) if donor else {'units': [1]}
    c.pop('part_binding', None)
    c.update(id='thermistor/'+ref, reference=ref, value=value)
    if lib:
        c['lib_id'] = lib
    if footprint:
        c['footprint'] = footprint
    cs[ref] = c
    d['components'].append(c)
    added.append(c['id'])
    return c['id']


shutil.copyfile(root/'sources/PodThermistor.kicad_sym',
                args.out/'authored-cad/PodThermistor.kicad_sym')
raw = (args.out/'authored-cad/PodThermistor.kicad_sym').read_bytes()
d['libraries'].append({'name': 'PodThermistor',
                      'path': 'authored-cad/PodThermistor.kicad_sym',
                      'sha256': hashlib.sha256(raw).hexdigest()})
exc = 'THERM_EXC_2V495'
u = add('U31', 'TL431BQDBZR', lib='PodThermistor:TL431DBZ',
        footprint='Package_TO_SOT_SMD:SOT-23')
for pin, name in [(1, exc), (2, exc), (3, 'GND')]:
    net(name, u, pin)
# BAV199 is a series pair: 1=A1, 3=K1/A2, 2=K2. Use only D1.
diode = add('D105', 'BAV199,215', donor='D102')
net('POD_5V_AUX', diode, 1)
net('THERM_BIAS_IN', diode, 3)
d['no_connects'].append(term(diode, 2))
for ref, a, b in [('R174', 'THERM_BIAS_IN', 'THERM_BIAS_MID'),
                  ('R175', 'THERM_BIAS_MID', exc)]:
    c = add(ref, '200 ohm 1% 100ppm/K 1.5W CRCW2512-HP', donor='R110')
    net(a, c, 1)
    net(b, c, 2)
# Default copper is OPEN. Firmware configuration alone cannot enable a pullup.
for i in range(4):
    r = add(f'R{170+i}', '10 kohm 0.1% 25ppm/K', donor='R34')
    j = add(f'JP{2+i}', f'AUX{i+1}_THERM_PULLUP_CLOSE_TO_ENABLE', donor='JP1')
    net(exc, r, 1)
    net(f'THERM_AUX{i+1}_SELECT', r, 2)
    net(f'THERM_AUX{i+1}_SELECT', j, 1)
    net(f'POD_AUX{i+1}_SIGNAL', j, 2)
c = add('C128', '10uF 16V X7R', donor='C86',
        footprint='Capacitor_SMD:C_1206_3216Metric')
net(exc, c, 1)
net('GND', c, 2)
# Bleed defines an off-state sink for the blocking diode's static leakage.
r = add('R180', '100 kohm 1% 100ppm/K', donor='R34')
net('POD_5V_AUX', r, 1)
net('GND', r, 2)
# Reuse the already reviewed diagnostic input treatment, on unused AIN3.
stem = 'DIAG_U28_AIN3'
nodes = [exc, stem+'_UPPER1', stem+'_UPPER2', stem, 'GND']
for i in range(4):
    r = add(f'R{176+i}', ('499 kohm' if i < 3 else '4.99 kohm')+' 0.1% 25ppm/K', donor='R128')
    net(nodes[i], r, 1)
    net(nodes[i+1], r, 2)
c = add('C129', '100nF 50V X7R', donor='C110')
net(stem, c, 1)
net('GND', c, 2)
t = term(cs['U28']['id'], 6)
d['no_connects'].remove(t)
net(stem, cs['U28']['id'], 6)
layout['groups'].append({'id': 'thermistor',
    'title': 'Optional thermistor excitation - qualification pending', 'components': added})
for filename, data in [('intent.json', d), ('emitter-layout.json', layout)]:
    (args.out/filename).write_text(json.dumps(data, indent=2)+'\n')
print(args.out)
