"""Independent source/native graph comparison. CLI: CANDIDATE THERMISTOR_INPUTS REPORT."""
import copy
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from agent_ee.symbol_library import parse_sexpr

candidate, baseline, report = map(Path, sys.argv[1:])
inputs = candidate / 'inputs'
checks = 0

def require(condition, message):
    global checks
    checks += 1
    if not condition:
        raise ValueError(message)

def children(node, name):
    return [x for x in node[1:] if isinstance(x, list) and x and x[0] == name]

def one(node, name):
    rows = children(node, name)
    require(len(rows) == 1, 'Expected one ' + name)
    return rows[0]

old = json.loads((baseline / 'intent.json').read_text())
new = json.loads((inputs / 'intent.json').read_text())
expected = copy.deepcopy(old)
adc_old, = [lib for lib in old['libraries'] if lib['name'] == 'Analog_ADC']
adc_new, = [lib for lib in new['libraries'] if lib['name'] == 'Analog_ADC']
oldbytes = (baseline / adc_old['path']).read_bytes()
newbytes = (inputs / adc_new['path']).read_bytes()
require(hashlib.sha256(oldbytes).hexdigest() == 'cfb2be046b87a769f2d36c0ff530ce34b766d08055c1bdffd1bf6daae0487c35', 'ADC baseline hash')
oldtree, newtree = parse_sexpr(oldbytes), parse_sexpr(newbytes)
def descendants(node):
    if isinstance(node, list):
        yield node
        for child in node:
            yield from descendants(child)
pins = [n for n in descendants(oldtree) if n and n[0] == 'pin' and children(n, 'number') and one(n, 'number')[1] == '12']
require(len(pins) == 1, 'exactly one captured ADC pin12')
require(pins[0][1] == 'output' and one(pins[0], 'name')[1] == 'Dout', 'ADC old output identity')
pins[0][1] = 'tri_state'
require(oldtree == newtree, 'ADC library delta must be only pin12 electrical type')
require(adc_new['sha256'] == hashlib.sha256(newbytes).hexdigest(), 'ADC revised source hash')
next(lib for lib in expected['libraries'] if lib['name'] == 'Analog_ADC')['sha256'] = adc_new['sha256']
for c in expected['components']:
    if c['reference'] in {'JP1', 'JP2', 'JP3', 'JP4', 'JP5'}:
        require(c['lib_id'] == 'CANJumper:SolderJumper_2_Open', 'jumper identity')
        c['in_bom'] = False
require(new == expected, 'Unexpected intent change')
layout = json.loads((baseline / 'emitter-layout.json').read_text())
for group in layout['groups']:
    if group['id'] == 'aux-power':
        require(group['title'] == 'Protected auxiliary power and ninth diagnostic - qualification pending', 'old title')
        group['title'] = 'Auxiliary power and diagnostic - qualification pending'
require(json.loads((inputs / 'emitter-layout.json').read_text()) == layout, 'Unexpected layout delta')
for path in baseline.rglob('*'):
    if path.is_file() and path.name not in {'intent.json', 'emitter-layout.json'} and str(path.relative_to(baseline)) != adc_old['path']:
        require((inputs/path.relative_to(baseline)).read_bytes() == path.read_bytes(), 'Changed capture ' + str(path))
oldfiles={str(p.relative_to(baseline)) for p in baseline.rglob('*') if p.is_file()}
newfiles={str(p.relative_to(inputs)) for p in inputs.rglob('*') if p.is_file()}
require(newfiles-oldfiles == {'footprints/Capacitor_SMD.pretty/C_1206_3216Metric.kicad_mod'}, 'Unexpected added captures')
require(hashlib.sha256((inputs/'footprints/Capacitor_SMD.pretty/C_1206_3216Metric.kicad_mod').read_bytes()).hexdigest() == 'b2e4a08e3aaf40bc587090190c0e3969e962d7ae962c172cce0581ae8327651c', 'C128 footprint hash')
byid = {c['id']:c for c in new['components']}
byref = {c['reference']:c for c in new['components']}
require(len(byid) == len(byref) == 332, 'source component identities')
flags={c['reference'] for c in new['components'] if c['lib_id']=='power:PWR_FLAG'}
require(len(flags)==6, 'six power flags')
xml=ET.parse(candidate/'native.xml').getroot()
require(next(n for n in xml.findall('./nets/net/node') if n.attrib['ref']=='U4' and n.attrib['pin']=='12').attrib['pintype']=='tri_state', 'native ADC DOUT tri-state')
comps=xml.findall('./components/comp')
require(len(comps)==326 and {c.attrib['ref'] for c in comps} == set(byref)-flags, 'native component membership')
for c in comps:
    ref=c.attrib['ref']
    require(c.findtext('value') == byref[ref]['value'], 'value '+ref)
    require((c.findtext('footprint') or '') == byref[ref].get('footprint',''), 'footprint '+ref)

def terminal(t):
    return (byid[t['component']]['reference'], str(t['pin']['number']))
expectednets={'/'+n['name']:{terminal(t) for t in n['terminals'] if byid[t['component']]['reference'] not in flags} for n in new['nets']}
require(len(expectednets)==193, 'source named net count')
expectednc={terminal(t) for t in new['no_connects']}
require(len(expectednc)==175, 'NC unique count')
seen=set(); actualnamed={}; actualnc=set()
for net in xml.findall('./nets/net'):
    nodes=net.findall('node')
    members={(n.attrib['ref'],n.attrib['pin']) for n in nodes}
    require(len(members)==len(nodes), 'duplicate terminal in net')
    require(not seen & members, 'terminal in multiple nets')
    seen |= members
    name=net.attrib['name']
    if name in expectednets:
        require(name not in actualnamed, 'duplicate named net')
        require(members==expectednets[name], 'Net mismatch '+name+' missing='+str(expectednets[name]-members)+' extra='+str(members-expectednets[name]))
        require(all('no_connect' not in n.attrib.get('pintype','') for n in nodes), 'NC on connected net '+name)
        actualnamed[name]=members
    else:
        require(len(nodes)==1 and name.startswith('unconnected-'), 'Unexpected net '+name)
        require('no_connect' in nodes[0].attrib.get('pintype','').split('+'), 'unmarked NC '+name)
        actualnc |= members
require(actualnamed==expectednets,'Missing named nets')
require(actualnc==expectednc,'Declared NC mismatch')
# Parse the complete native schematic independently of emitter helpers. XML omits PWR_FLAG.
sch=parse_sexpr((candidate/'project/telemetry-pod.kicad_sch').read_bytes())
require(sch[0]=='kicad_sch','native schematic root')
symbols=children(sch,'symbol'); placed={}
for s in symbols:
    props={p[1]:p[2] for p in children(s,'property')}
    placed.setdefault(props['Reference'],[]).append((s,props))
require(set(placed)==set(byref),'Native schematic component membership including flags')
for ref, source in byref.items():
    records=placed[ref]
    require(sorted(int(one(s,'unit')[1]) for s,_ in records)==sorted(source.get('units',[1])), 'native units '+ref)
    for s,p in records:
        require(p['Value']==source['value'] and p.get('Footprint','')==source.get('footprint',''),'native properties '+ref)
        require(one(s,'on_board')[1]==('no' if ref in flags else 'yes'),'on-board '+ref)
        require(one(s,'in_bom')[1]==('no' if ref in flags or ref in {'TP1','TP2','TP3','TP4','TP5','TP6'} or source.get('in_bom') is False else 'yes'),'BOM '+ref)
require(len(children(sch,'no_connect'))==175,'native explicit NC marker count')
result={'status':'PASS','checks':checks,'components_source':332,'components_xml':326,'power_flags_native_schematic':6,'named_nets':193,'explicit_nc_singletons':175,'copper_jumpers':'JP1..JP5 retained electrically/on-board, in_bom=no','sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [inputs/'intent.json',baseline/'intent.json',candidate/'native.xml',candidate/'project/telemetry-pod.kicad_sch']},'scope':'Graph and source-preservation evidence only; Shared-SPI operational qualification and prior electrical, assembly, thermal, placement, routing and qualification holds remain.'}
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
