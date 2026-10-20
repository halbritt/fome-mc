"""Compare a regenerated presentation candidate with the retained series design."""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from agent_ee.symbol_library import parse_sexpr

ROOT = Path(__file__).resolve().parent
old = ROOT.parent / 'series-divider/native-candidate'
new, report = map(Path, sys.argv[1:])
a = json.loads((old / 'inputs/emitter-layout.json').read_text())
b = json.loads((new / 'inputs/emitter-layout.json').read_text())
expected = {
    'eMMC interface candidate - supplies pending': 'eMMC interface - qualification pending',
    'Separate eMMC core supply - supervisor pending': 'Separate eMMC core supply - qualification pending',
}
changes = {}
for x, y in zip(a['groups'], b['groups'], strict=True):
    if x != y:
        changes[x['title']] = y['title']
        x['title'] = y['title']
if a != b or changes != expected:
    raise ValueError('Changes exceed two declared headings')
def files(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
x, y = files(old / 'inputs'), files(new / 'inputs')
x.pop(Path('emitter-layout.json')); y.pop(Path('emitter-layout.json'))
if x != y:
    raise ValueError('Other captured inputs changed')
def identities(path):
    tree = parse_sexpr(path.read_bytes())
    symbols = [x for x in tree if isinstance(x, list) and x and x[0] == 'symbol']
    result = {}
    for s in symbols:
        props = {x[1]: x[2] for x in s if isinstance(x, list) and x and x[0] == 'property'}
        unit, = [x[1] for x in s if isinstance(x, list) and x and x[0] == 'unit']
        identity, = [x[1] for x in s if isinstance(x, list) and x and x[0] == 'uuid']
        key = (props['Reference'], unit)
        if key in result:
            raise ValueError('Duplicate instance')
        result[key] = identity
    return result
if identities(old / 'project/telemetry-pod.kicad_sch') != identities(new / 'project/telemetry-pod.kicad_sch'):
    raise ValueError('Native instance identities changed')
def normalized_xml(path):
    tree = ET.parse(path).getroot()
    design = tree.find('design')
    for name in ['source', 'date']:
        element = design.find(name)
        if element is None:
            raise ValueError('Missing XML metadata')
        design.remove(element)
    # KiCad may reorder the same multi-unit U14 UUID list. Preserve multiplicity.
    component, = [c for c in tree.findall('./components/comp') if c.attrib['ref'] == 'U14']
    stamps = component.find('tstamps')
    if stamps is None or stamps.text is None:
        raise ValueError('Missing U14 instance list')
    stamps.text = ' '.join(sorted(stamps.text.split()))
    return ET.tostring(tree)
if normalized_xml(old / 'native.xml') != normalized_xml(new / 'native.xml'):
    raise ValueError('Native XML changed beyond metadata and U14 list order')
if (old / 'native-bom.csv').read_bytes() != (new / 'native-bom.csv').read_bytes():
    raise ValueError('BOM changed')
erc = json.loads((new / 'erc.json').read_text())
if not erc['sheets'] or any(s['violations'] for s in erc['sheets']):
    raise ValueError('ERC missing sheets or has findings')
report.write_text(json.dumps({
    'status': 'PASS', 'layout_changes': changes,
    'other_inputs': 'byte-identical', 'instance_identities': 'unchanged',
    'native_xml': 'identical except source path/date and order of U14 instance UUID list',
    'bom': 'byte-identical', 'erc_violations': 0,
    'scope': 'Presentation and released-emitter regression only. Group positions reflow; full-sheet readability remains open.'
}, indent=2) + '\n')
print('PASS: two heading changes; inputs, instance identities, native graph and BOM preserved; ERC zero')
