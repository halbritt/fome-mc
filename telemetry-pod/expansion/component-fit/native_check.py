"""Compare native exports to the complete source intent and previous connectivity."""
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_map(rows, key, label):
    result = {}
    for row in rows:
        name = key(row)
        require(name not in result, 'Duplicate ' + label + ': ' + name)
        result[name] = row
    return result


def graph(tree):
    nets = unique_map(tree.findall('./nets/net'), lambda n: n.attrib['name'], 'net')
    return {name: sorted(tuple(sorted(node.attrib.items())) for node in net.findall('node'))
            for name, net in nets.items()}


def check_native(intent_path, candidate, baseline):
    candidate, baseline = Path(candidate), Path(baseline)
    intent = json.loads(Path(intent_path).read_text())
    expected = unique_map([c for c in intent['components'] if c['lib_id'] != 'power:PWR_FLAG'],
                          lambda c: c['reference'], 'intent reference')
    before = ET.parse(baseline / 'native.xml')
    after = ET.parse(candidate / 'native.xml')
    require(graph(after) == graph(before), 'Native graph or pin functions changed')
    actual = unique_map(after.findall('./components/comp'), lambda c: c.attrib['ref'], 'native reference')
    require(set(actual) == set(expected), 'Native component membership differs from intent')
    bindings = 0
    for ref, component in expected.items():
        native = actual[ref]
        for name in ('value', 'footprint'):
            require(native.findtext(name) == component[name], 'Native ' + name + ' mismatch: ' + ref)
        fields = unique_map(native.findall('./fields/field'), lambda f: f.attrib['name'], 'field at ' + ref)
        require(set(fields) == set(component.get('part_binding', {})) | {'Footprint', 'Datasheet', 'Description'},
                'Unexpected or missing native fields: ' + ref)
        for name, value in component.get('part_binding', {}).items():
            require(name in fields and (fields[name].text or '') == value,
                    'Native binding mismatch: ' + ref + '/' + name)
            if name == 'Datasheet':
                require(native.findtext('datasheet') == value, 'Native datasheet mismatch: ' + ref)
            bindings += 1
    with (candidate / 'native-bom.csv').open() as stream:
        bom = unique_map(list(csv.DictReader(stream)), lambda r: r['Reference'], 'BOM reference')
    # The six captured PogoPad symbols inherit in_bom=no from their library.
    probes = {f'TP{i}' for i in range(1, 7)}
    require(all(expected[ref]['lib_id'] == 'PodFeatures:PogoPad' for ref in probes),
            'Captured probe identity changed')
    included = {ref: c for ref, c in expected.items() if c.get('in_bom', True) and ref not in probes}
    require(set(bom) == set(included), 'Native BOM membership differs from intent')
    for ref, c in included.items():
        require(bom[ref]['ExcludeBOM'] == '' and bom[ref]['ExcludeBoard'] == '',
                'Native BOM exclusion policy mismatch: ' + ref)
        require(bom[ref]['Value'] == c['value'] and bom[ref]['Footprint'] == c['footprint'],
                'Native BOM value/footprint mismatch: ' + ref)
    erc = json.loads((candidate / 'erc.json').read_text())
    prior = json.loads((baseline / 'erc.json').read_text())
    for name in ('ignored_checks', 'included_severities', 'kicad_version'):
        require(erc[name] == prior[name], 'ERC policy/version changed: ' + name)
    require(bool(erc['sheets']), 'ERC has no checked sheets')
    require([{k: v for k, v in sheet.items() if k != 'violations'} for sheet in erc['sheets']] ==
            [{k: v for k, v in sheet.items() if k != 'violations'} for sheet in prior['sheets']],
            'ERC checked sheet coverage changed')
    require(not any(sheet['violations'] for sheet in erc['sheets']), 'Native ERC violations')
    return {'status': 'PASS', 'native_components': len(actual), 'native_nets': len(graph(after)),
            'binding_fields_checked': bindings, 'bom_components': len(bom),
            'inputs_sha256': {'intent': hashlib.sha256(Path(intent_path).read_bytes()).hexdigest(),
                             **{name: hashlib.sha256((candidate / name).read_bytes()).hexdigest()
                                for name in ['native.xml', 'native-bom.csv', 'erc.json']},
                             'baseline_xml': hashlib.sha256((baseline / 'native.xml').read_bytes()).hexdigest(),
                             'baseline_erc': hashlib.sha256((baseline / 'erc.json').read_bytes()).hexdigest()},
            'scope': 'Native XML values/footprint identifiers/bindings/connectivity, BOM membership and ERC only. '
                     'Not board land-pattern, placement, routing, fabrication or operating qualification.'}
