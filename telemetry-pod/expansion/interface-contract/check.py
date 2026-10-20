"""Check explicit expanded connector/GPIO contract against source and native XML."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--intent', type=Path, default=ROOT.parent/'series-divider/prepared/intent.json')
parser.add_argument('--native', type=Path, default=ROOT.parent/'series-divider/native-candidate/native.xml')
args = parser.parse_args()
contract = json.loads((ROOT/'contract.json').read_text())
allocation = json.loads((ROOT.parent/'allocation.json').read_text())
intent = json.loads(args.intent.read_text())
xml = ET.parse(args.native)

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def unique(rows, key):
    result = {}
    for row in rows:
        name = key(row)
        require(name not in result, 'Duplicate key: '+str(name))
        result[name] = row
    return result

components = unique(intent['components'], lambda c:c['reference'])
by_id = unique(intent['components'], lambda c:c['id'])
native_components = unique(xml.findall('./components/comp'), lambda c:c.get('ref'))
source_nets = {}
for net in intent['nets']:
    for t in net['terminals']:
        key = by_id[t['component']]['reference'], str(t['pin']['number'])
        require(key not in source_nets, 'Repeated source terminal')
        source_nets[key] = net['name']
source_nc = [(by_id[t['component']]['reference'],str(t['pin']['number']))
             for t in intent['no_connects']]
require(len(source_nc)==len(set(source_nc)), 'Repeated source NC')
require(not set(source_nc)&set(source_nets), 'Connected source NC')
native = {}
for net in xml.findall('./nets/net'):
    for node in net.findall('node'):
        key = node.get('ref'), node.get('pin')
        require(key not in native, 'Repeated native terminal')
        native[key] = net, node

for ref, mpn in [('J1',contract['connector_mpn']), ('U1',contract['module_mpn'])]:
    require(components[ref]['part_binding']['Partnumber']==mpn, 'Source identity '+ref)
    fields = unique(native_components[ref].findall('./fields/field'), lambda f:f.get('name'))
    require(fields['Partnumber'].text==mpn, 'Native identity '+ref)

def check_terminal(ref, pin, expected, mode):
    key = ref, str(pin)
    require(mode in ('connected','no_connect'), 'Unknown connection mode')
    net, node = native[key]
    if mode == 'no_connect':
        require(expected is None and key in source_nc, 'Missing explicit source NC '+str(key))
        require(net.get('name').startswith('unconnected-') and len(net.findall('node'))==1
                and 'no_connect' in node.get('pintype','').split('+'), 'Missing native NC '+str(key))
    else:
        require(expected is not None and source_nets.get(key)==expected, 'Source net mismatch '+str(key))
        require(net.get('name')=='/'+expected and 'no_connect' not in node.get('pintype','').split('+'),
                'Native net mismatch '+str(key))

j1 = unique(contract['j1'], lambda r:r['pin'])
allocated_j1 = unique(allocation['j1'], lambda r:r['pin'])
require(set(j1)==set(allocated_j1)==set(range(1,36)), 'All 35 cavities required')
require({p for ref,p in native if ref=='J1'}=={str(p) for p in j1}, 'Native J1 coverage')
require({p for ref,p in set(source_nets)|set(source_nc) if ref=='J1'}=={str(p) for p in j1},
        'Source J1 coverage')
for pin, row in j1.items():
    require(row['allocated_signal']==allocated_j1[pin]['net'], 'Allocation drift at J1')
    check_terminal('J1',pin,row['native_net'],row['mode'])

gpio = unique(contract['gpio'], lambda r:r['gpio'])
allocated_gpio = unique(allocation['gpio_reservations'], lambda r:r['gpio'])
require(set(gpio)==set(allocated_gpio), 'All allocated GPIOs required')
unique(contract['gpio'], lambda r:r['module_pin'])
libsource = native_components['U1'].find('libsource')
parts = [p for p in xml.findall('./libparts/libpart')
         if (p.get('lib'),p.get('part'))==(libsource.get('lib'),libsource.get('part'))]
require(len(parts)==1, 'One native module library')
pins = unique(parts[0].findall('./pins/pin'), lambda p:p.get('num'))
for number, row in gpio.items():
    old = allocated_gpio[number]
    require(row['module_pin']==old['module_pin'] and row['allocated_signal']==old['signal'],
            'GPIO allocation drift')
    require(number not in {0,3,45,46}, 'Expansion uses strapping GPIO')
    require(pins[str(row['module_pin'])].get('name')=='IO'+str(number), 'GPIO/module-pin mismatch')
    check_terminal('U1',row['module_pin'],row['native_net'],row['mode'])

report = {
    'status':'PASS', 'connector_cavities':len(j1), 'expansion_gpio_allocations':len(gpio),
    'optional_reset':'GPIO35/module pin28 explicitly unconnected',
    'j1':contract['j1'], 'gpio':contract['gpio'],
    'sha256':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in {
        'contract':ROOT/'contract.json','allocation':ROOT.parent/'allocation.json',
        'intent':args.intent,'native':args.native}.items()},
    'limits':['Source/native correspondence only; no firmware, timing, voltage or harness qualification.',
              'Does not replace the committed pilot io-map or full compiled interface contract.',
              'Native module pin labels are captured-library evidence; datasheet applicability was not requalified.']}
print(json.dumps(report,indent=2))
