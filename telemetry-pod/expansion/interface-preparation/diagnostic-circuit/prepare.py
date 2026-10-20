"""Prepare diagnostics for eight present rails; reserve the future auxiliary rail channel."""
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
base_net_names = frozenset(nets)
added = []


def term(cid, pin):
    return {'component': cid, 'pin': {'number': str(pin)}}


def net(name, cid, pin):
    if name not in nets:
        nets[name] = {'id': 'diagnostic/'+name, 'name': name, 'terminals': []}
        d['nets'].append(nets[name])
    nets[name]['terminals'].append(term(cid, pin))


def add(ref, value, lib=None, footprint=None, donor=None):
    if ref in components:
        raise ValueError(f'Duplicate reference: {ref}')
    c = copy.deepcopy(components[donor]) if donor else {'units': [1]}
    c.pop('part_binding', None)
    c.update(id='diagnostic/'+ref, reference=ref, value=value)
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


raw = ('(kicad_symbol_lib (version 20231120) (generator "pod_diagnostic")\n'+
       symbol('ADS1119_PW', [(1,'A0','input'),(2,'A1','input'),(3,'RESET_N','input'),
              (4,'DGND','power_in'),(5,'AGND','power_in'),(6,'AIN3','input'),
              (7,'AIN2','input'),(8,'REFN','input'),(9,'REFP','input'),
              (10,'AIN1','input'),(11,'AIN0','input'),(12,'AVDD','power_in'),
              (13,'DVDD','power_in'),(14,'DRDY_N','open_collector'),
              (15,'SDA','bidirectional'),(16,'SCL','input')])+')\n').encode()
parse_library(raw)
path = 'authored-cad/PodDiagnostic.kicad_sym'
(args.out/path).write_bytes(raw)
d['libraries'].append({'name':'PodDiagnostic','path':path,'sha256':hashlib.sha256(raw).hexdigest()})
fp = Path('Package_SO.pretty/TSSOP-16_4.4x5mm_P0.65mm.kicad_mod')
(args.out/'footprints'/fp).parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(Path('/usr/share/kicad/footprints')/fp, args.out/'footprints'/fp)

for module_pin,name in [(22,'DIAG_I2C_SDA'),(23,'DIAG_I2C_SCL')]:
    terminal = term(components['U1']['id'],module_pin)
    d['no_connects'].remove(terminal)
    net(name,components['U1']['id'],module_pin)
for ref,name in [('R160','DIAG_I2C_SDA'),('R161','DIAG_I2C_SCL')]:
    cid=add(ref,'2.2 kohm 1% 100ppm/C',donor='R66')
    net('+3V3',cid,1)
    net(name,cid,2)

# Physical PW-package pin order, NOT the RTE/QFN package order.
# AIN2 on U28 stays NC until the allocated protected auxiliary 5 V supply exists.
channels = [
    ('U27','POD_12V_PROTECTED',11),('U27','PRE_6V3',10),('U27','+3V3',7),
    ('U28','EMMC_VCC_3V3',11),('U28','POD_5V_SENSOR',10),
    ('U29','POD_WHEEL_FRONT_SUPPLY',11),('U29','POD_WHEEL_REAR_SUPPLY',10),
    ('U29','POD_TIRE_SUPPLY',7)]
for ix,(ref,a1,a0) in enumerate([('U27','GND','GND'),('U28','GND','+3V3'),('U29','+3V3','GND')]):
    cid=add(ref,'ADS1119IPWR','PodDiagnostic:ADS1119_PW','Package_SO:TSSOP-16_4.4x5mm_P0.65mm')
    for pin,name in [(1,a0),(2,a1),(3,'+3V3'),(4,'GND'),(5,'GND'),(12,'+3V3'),
                     (13,'+3V3'),(15,'DIAG_I2C_SDA'),(16,'DIAG_I2C_SCL')]:
        net(name,cid,pin)
    for pin in [6,8,9,14]+([7] if ref=='U28' else []):
        d['no_connects'].append(term(cid,pin))
    for offset in (0,1):
        c=add(f'C{118+2*ix+offset}','1uF 50V X7R',donor='C79',footprint='Capacitor_SMD:C_0805_2012Metric')
        net('+3V3',c,1)
        net('GND',c,2)

for ix,(ref,rail,pin) in enumerate(channels):
    if rail not in base_net_names:
        raise ValueError(f'Monitored rail absent from base: {rail}')
    stem=f'DIAG_{ref}_AIN'+{11:'0',10:'1',7:'2'}[pin]
    nodes=[rail,stem+'_UPPER1',stem+'_UPPER2',stem,'GND']
    for k in range(4):
        value=('499 kohm' if k<3 else '4.99 kohm')+' 0.1% 25ppm/C'
        cid=add(f'R{128+4*ix+k}',value,donor='R66')
        net(nodes[k],cid,1)
        net(nodes[k+1],cid,2)
    c=add(f'C{110+ix}','100nF 50V X7R',donor='C79')
    net(stem,c,1)
    net('GND',c,2)
    net(stem,components[ref]['id'],pin)

layout['groups'].append({'id':'diagnostic','title':'Rail diagnostics - auxiliary channel reserved; qualification pending','components':added})
for name,data in [('intent.json',d),('emitter-layout.json',layout)]:
    (args.out/name).write_text(json.dumps(data,indent=2)+'\n')
print(args.out)
