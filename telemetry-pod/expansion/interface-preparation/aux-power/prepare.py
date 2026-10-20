"""Prepare protected auxiliary sensor power and the ninth rail monitor."""
import argparse
import copy
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
        nets[name] = {'id': 'aux-power/'+name, 'name': name, 'terminals': []}
        d['nets'].append(nets[name])
    nets[name]['terminals'].append(term(cid, pin))


def add(ref, value, lib=None, footprint=None, donor=None):
    if ref in components:
        raise ValueError(f'Duplicate reference: {ref}')
    c = copy.deepcopy(components[donor]) if donor else {'units': [1]}
    c.pop('part_binding', None)
    c.update(id='aux-power/'+ref, reference=ref, value=value)
    if lib:
        c['lib_id'] = lib
    if footprint:
        c['footprint'] = footprint
    components[ref] = c
    d['components'].append(c)
    added.append(c['id'])
    return c['id']


if 'POD_5V_SENSOR' not in base_net_names:
    raise ValueError('Shared sensor rail must already exist')
u=add('U30','TPS26625DRCR',donor='U23')
stem='SENSOR_POWER_AUX'
for pin,name in [(1,'POD_5V_SENSOR'),(2,stem+'_UVLO'),(3,stem+'_OVP'),
                 (5,stem+'_RTN'),(6,'GND'),(7,stem+'_ILIM'),(8,stem+'_DVDT'),
                 (10,'POD_5V_AUX'),(11,stem+'_RTN')]:
    net(name,u,pin)
for pin in (4,9):
    d['no_connects'].append(term(u,pin))
for ref,value,a,b in [
        ('R162','1.05 Mohm 0.1% 25ppm/K','POD_5V_SENSOR',stem+'_UVLO'),
        ('R163','95.3 kohm 0.1% 25ppm/K',stem+'_UVLO',stem+'_OVP'),
        ('R164','287 kohm 0.1% 25ppm/K',stem+'_OVP',stem+'_RTN'),
        ('R165','44.2 kohm 0.1% 25ppm/K',stem+'_ILIM',stem+'_RTN')]:
    c=add(ref,value,donor='R66')
    net(a,c,1)
    net(b,c,2)
for ref,value,a,b,donor in [
        ('C124','1uF 50V X7R','POD_5V_SENSOR','GND','C86'),
        ('C125','100nF 50V X7R','POD_5V_AUX','GND','C87'),
        ('C126','10nF 50V C0G 10%',stem+'_DVDT',stem+'_RTN','C88')]:
    c=add(ref,value,donor=donor)
    net(a,c,1)
    net(b,c,2)
for pin,name in [(21,'POD_5V_AUX'),(22,'GND')]:
    t=term(components['J1']['id'],pin)
    d['no_connects'].remove(t)
    net(name,components['J1']['id'],pin)

# Same input treatment as the other eight diagnostics; no alternate reference.
stem='DIAG_U28_AIN2'
nodes=['POD_5V_AUX',stem+'_UPPER1',stem+'_UPPER2',stem,'GND']
for k in range(4):
    value=('499 kohm' if k<3 else '4.99 kohm')+' 0.1% 25ppm/C'
    c=add(f'R{166+k}',value,donor='R128')
    net(nodes[k],c,1)
    net(nodes[k+1],c,2)
c=add('C127','100nF 50V X7R',donor='C110')
net(stem,c,1)
net('GND',c,2)
t=term(components['U28']['id'],7)
d['no_connects'].remove(t)
net(stem,components['U28']['id'],7)
for group in layout['groups']:
    if group['id'] == 'diagnostic':
        group['title'] = 'Rail diagnostics - qualification pending'
layout['groups'].append({'id':'aux-power','title':'Protected auxiliary power and ninth diagnostic - qualification pending','components':added})
for name,data in [('intent.json',d),('emitter-layout.json',layout)]:
    (args.out/name).write_text(json.dumps(data,indent=2)+'\n')
print(args.out)
