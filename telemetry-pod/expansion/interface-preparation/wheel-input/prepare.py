"""Prepare two Hall input channels on the protected sensor-power candidate."""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path
from agent_ee.symbol_library import parse_library

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
if args.out.exists():
    raise SystemExit('Output must be a fresh directory')
shutil.copytree(args.base, args.out)
d = json.loads((args.out/'intent.json').read_text())
layout = json.loads((args.out/'emitter-layout.json').read_text())
components = {c['reference']: c for c in d['components']}
nets = {n['name']: n for n in d['nets']}
added = []


def term(cid, pin):
    return {'component': cid, 'pin': {'number': str(pin)}}


def net(name, cid, pin):
    if name not in nets:
        nets[name] = {'id': 'wheel-input/'+name, 'name': name, 'terminals': []}
        d['nets'].append(nets[name])
    nets[name]['terminals'].append(term(cid, pin))


def add(ref, value, lib=None, footprint=None, donor=None):
    assert ref not in components, ref
    c = copy.deepcopy(components[donor]) if donor else {'units': [1]}
    c.pop('part_binding', None)
    c.update(id='wheel-input/'+ref, reference=ref, value=value)
    if lib:
        c['lib_id'] = lib
    if footprint:
        c['footprint'] = footprint
    components[ref] = c
    d['components'].append(c)
    added.append(c['id'])
    return c['id']


def symbol(name, pins):
    rows = (len(pins)+1)//2
    height = (rows+1)*1.27
    out = [f'(symbol "{name}" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)',
           f'(property "Reference" "U" (at 0 {height+2.54:g} 0) (effects (font (size 1.27 1.27))))',
           f'(property "Value" "{name}" (at 0 {height+5.08:g} 0) (effects (font (size 1.27 1.27))))',
           f'(symbol "{name}_1_1" (rectangle (start -10.16 {height:g}) (end 10.16 {-height:g})',
           '(stroke (width 0.254) (type default)) (fill (type background)))']
    for i, (number, label, kind) in enumerate(pins):
        x, angle = (-12.7, 0) if i < rows else (12.7, 180)
        y = height-2.54*((i % rows)+1)
        out.append(f'(pin {kind} line (at {x} {y:g} {angle}) (length 2.54) '
                   f'(name "{label}" (effects (font (size 1.016 1.016)))) '
                   f'(number "{number}" (effects (font (size 1.016 1.016)))))')
    return '\n'.join(out)+'))'


raw = ('(kicad_symbol_lib (version 20231120) (generator "pod_wheel")\n'+
       symbol('LM2903BQ_D', [(1,'OUT1','open_collector'),(2,'IN1-','input'),
              (3,'IN1+','input'),(4,'GND','power_in'),(5,'IN2+','input'),
              (6,'IN2-','input'),(7,'OUT2','open_collector'),(8,'VCC','power_in')])+ '\n'+
       symbol('BAV199', [(1,'A1','passive'),(2,'K2','passive'),(3,'K1_A2','passive')])+')\n').encode()
parse_library(raw)
path = 'authored-cad/PodWheel.kicad_sym'
(args.out/path).write_bytes(raw)
d['libraries'].append({'name': 'PodWheel', 'path': path, 'sha256': hashlib.sha256(raw).hexdigest()})
fp = Path('Resistor_SMD.pretty/R_2512_6332Metric.kicad_mod')
shutil.copyfile(Path('/usr/share/kicad/footprints')/fp, args.out/'footprints'/fp)
u = add('U26','LM2903BQDRQ1','PodWheel:LM2903BQ_D','Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
net('PRE_6V3',u,8)
net('GND',u,4)
for i, (side, jpin, modulepin, minus, plus, output) in enumerate([
        ('FRONT',24,39,2,3,1),('REAR',27,38,6,5,7)]):
    stem = 'WHEEL_'+side
    signal = 'POD_WHEEL_'+side+'_SIGNAL'
    supply = 'POD_WHEEL_'+side+'_SUPPLY'
    diode = add(f'D{102+i}','BAV199,215','PodWheel:BAV199','Package_TO_SOT_SMD:SOT-23')
    net(stem+'_PULLUP',diode,1)
    net(stem+'_DIODE_OUT',diode,2)
    net(signal,diode,3)
    jt = term(components['J1']['id'],jpin)
    d['no_connects'].remove(jt)
    net(signal,components['J1']['id'],jpin)
    mt = term(components['U1']['id'],modulepin)
    d['no_connects'].remove(mt)
    net(stem+'_CAPTURE',components['U1']['id'],modulepin)
    net(stem+'_FILTERED',u,minus)
    net(stem+'_THRESHOLD',u,plus)
    net(stem+'_OUT',u,output)
    resistors = [
        ('620 ohm',supply,stem+'_PULLUP_MID'),
        ('620 ohm',stem+'_PULLUP_MID',stem+'_PULLUP'),
        ('10 kohm 0.1%',stem+'_DIODE_OUT',stem+'_FILTERED'),
        ('10 kohm 0.1%',stem+'_FILTERED','GND'),
        ('56 kohm 0.1%','+3V3',stem+'_THRESHOLD'),
        ('10 kohm 0.1%',stem+'_THRESHOLD','GND'),
        ('100 kohm 0.1%',stem+'_OUT',stem+'_THRESHOLD'),
        ('4.7 kohm 1%','+3V3',stem+'_OUT'),
        ('100 ohm',stem+'_OUT',stem+'_CAPTURE')]
    for k,(value,a,b) in enumerate(resistors):
        cid = add(f'R{110+9*i+k}',value,donor='R66',
                  footprint='Resistor_SMD:R_2512_6332Metric' if k<2 else None)
        net(a,cid,1)
        net(b,cid,2)
    c = add(f'C{95+i}','220pF C0G',donor='C79')
    net(stem+'_FILTERED',c,1)
    net('GND',c,2)
for ref,value in [('C97','100nF 50V X7R'),('C98','1uF 50V X7R')]:
    c=add(ref,value,donor='C79',footprint='Capacitor_SMD:C_0805_2012Metric' if ref=='C98' else None)
    net('PRE_6V3',c,1)
    net('GND',c,2)
tvs=add('D104','PESD2CANFD24V-TR',donor='D101')
net('POD_WHEEL_FRONT_SIGNAL',tvs,1)
net('POD_WHEEL_REAR_SIGNAL',tvs,2)
net('GND',tvs,3)
layout['groups'].append({'id':'wheel-input','title':'Hall input conditioning - qualification pending','components':added})
for name,data in [('intent.json',d),('emitter-layout.json',layout)]:
    (args.out/name).write_text(json.dumps(data,indent=2)+'\n')
print(args.out)
