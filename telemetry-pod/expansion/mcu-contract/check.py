"""Check all MCU terminals and direct signal peers against source and native XML."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--contract', type=Path, default=ROOT/'contract.json')
p.add_argument('--intent', type=Path, default=ROOT.parent/'series-divider/prepared/intent.json')
p.add_argument('--native', type=Path, default=ROOT.parent/'released-presentation/candidate/native.xml')
a = p.parse_args()
c = json.loads(a.contract.read_text())
i = json.loads(a.intent.read_text())
x = ET.parse(a.native)

def need(ok, message):
    if not ok:
        raise ValueError(message)

def unique(rows, key):
    result = {}
    for row in rows:
        k = key(row)
        need(k not in result, 'Duplicate identity '+str(k))
        result[k] = row
    return result

components = unique(i['components'], lambda v: v['id'])
refs = unique(i['components'], lambda v: v['reference'])
need(c['reference']=='U1' and c['mpn']=='ESP32-S3-WROOM-1-N8', 'Expected selected MCU identity')
need(refs['U1']['part_binding']['Partnumber']==c['mpn'], 'Source MCU identity')
nc = unique(x.findall('./components/comp'), lambda v:v.get('ref'))['U1']
fields = unique(nc.findall('./fields/field'), lambda v:v.get('name'))
need(fields['Partnumber'].text==c['mpn'], 'Native MCU identity')
lib = nc.find('libsource')
part, = [v for v in x.findall('./libparts/libpart') if (v.get('lib'),v.get('part'))==(lib.get('lib'),lib.get('part'))]
labels = unique(part.findall('./pins/pin'), lambda v:int(v.get('num')))
rows = unique(c['pins'], lambda v:v['module_pin'])
need(set(rows)==set(labels)==set(range(1,42)), 'All 41 module pins required')

def terminal(t):
    return components[t['component']]['reference'], str(t['pin']['number'])
source, source_members = {}, {}
for net in i['nets']:
    members = [terminal(t) for t in net['terminals']]
    need(len(members)==len(set(members)), 'Repeated source net member')
    need(net['name'] not in source_members, 'Duplicate source net name')
    source_members[net['name']] = set(members)
    for key in members:
        need(key not in source, 'Repeated source terminal')
        source[key] = net['name']
source_nc = [terminal(t) for t in i['no_connects']]
need(len(source_nc)==len(set(source_nc)) and not set(source_nc)&set(source), 'Invalid source NCs')
native = {}
for net in x.findall('./nets/net'):
    for node in net.findall('node'):
        key = node.get('ref'), node.get('pin')
        need(key not in native, 'Repeated native terminal')
        native[key] = (net,node)
expected = {('U1',str(pin)) for pin in rows}
need({k for k in set(source)|set(source_nc) if k[0]=='U1'}==expected, 'Source MCU coverage')
need({k for k in native if k[0]=='U1'}==expected, 'Native MCU coverage')
flags = {v['reference'] for v in i['components'] if v['lib_id']=='power:PWR_FLAG'}
for pin,row in rows.items():
    key = 'U1', str(pin)
    need(labels[pin].get('name')==row['library_label'], 'Pin label '+str(pin))
    net,node = native[key]
    need(row['mode'] in ('signal','power','no_connect'), 'Unknown mode')
    if row['mode']=='no_connect':
        need(row['net'] is None and not row['direct_peers'], 'NC contract '+str(pin))
        need(key in source_nc and net.get('name').startswith('unconnected-')
             and len(net.findall('node'))==1 and 'no_connect' in node.get('pintype','').split('+'),
             'Explicit NC '+str(pin))
        continue
    need(row['net'] is not None and source.get(key)==row['net'], 'Source net '+str(pin))
    need(net.get('name')=='/'+row['net'] and 'no_connect' not in node.get('pintype','').split('+'), 'Native net '+str(pin))
    actual = {(v.get('ref'),v.get('pin')) for v in net.findall('node')}
    need(actual=={k for k in source_members[row['net']] if k[0] not in flags}, 'Source/native membership '+str(pin))
    if row['mode']=='power':
        need(row['net'] in ('GND','+3V3') and pin in (1,2,40,41) and not row['direct_peers'], 'Power contract '+str(pin))
    else:
        need(pin not in (1,2,40,41), 'Power pin treated as signal')
        peers = [(v['reference'],v['pin']) for v in row['direct_peers']]
        need(len(peers)==len(set(peers)) and set(peers)==actual-{key}, 'Direct signal peers '+str(pin))
report = {'status':'PASS','module_terminals':len(rows),'modes':dict(Counter(v['mode'] for v in rows.values())),
          'pins':c['pins'],'limits':c['limits'],
          'sha256':{k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in
                    {'contract':a.contract,'intent':a.intent,'native':a.native}.items()}}
print(json.dumps(report,indent=2))
