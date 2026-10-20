"""Compare native exports to the complete source intent and previous connectivity."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from agent_ee.symbol_library import parse_sexpr


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


def children(node, name):
    return [n for n in node[1:] if isinstance(n, list) and n and n[0] == name]


def one(node, name):
    matches = children(node, name)
    require(len(matches) == 1, 'Expected one schematic ' + name)
    return matches[0]


def schematic_symbols(tree):
    require(tree[0] == 'kicad_sch', 'Expected native schematic root')
    result = {}
    for symbol in children(tree, 'symbol'):
        properties = unique_map(children(symbol, 'property'), lambda p: p[1], 'schematic property')
        ref = properties['Reference'][2]
        result.setdefault(ref, []).append((symbol, {k: v[2] for k, v in properties.items()}))
    return result


def check_schematic(intent, path, baseline_path):
    tree = parse_sexpr(path.read_bytes())
    previous = parse_sexpr(baseline_path.read_bytes())
    placed, prior = schematic_symbols(tree), schematic_symbols(previous)
    expected = unique_map(intent['components'], lambda c: c['reference'], 'schematic intent reference')
    require(set(placed) == set(expected) == set(prior), 'Schematic symbol membership including power flags')
    probes = {f'TP{i}' for i in range(1, 7)}
    for ref, source in expected.items():
        records = placed[ref]
        require(sorted(int(one(s, 'unit')[1]) for s, _ in records) == sorted(source.get('units', [1])),
                'Schematic units mismatch: ' + ref)
        previous_units = unique_map(prior[ref], lambda row: str(one(row[0], 'unit')[1]), 'prior unit')
        flag = source['lib_id'] == 'power:PWR_FLAG'
        for symbol, fields in records:
            old = previous_units[str(one(symbol, 'unit')[1])][0]
            require(one(symbol, 'at') == one(old, 'at'), 'Schematic pose mismatch: ' + ref)
            for attribute in ('mirror', 'dnp', 'in_pos_files', 'exclude_from_sim'):
                values, previous_values = children(symbol, attribute), children(old, attribute)
                require(len(values) <= 1 and values == previous_values,
                        'Schematic attribute mismatch: ' + ref + '/' + attribute)
            require(one(symbol, 'lib_id')[1] == source['lib_id'], 'Schematic library mismatch: ' + ref)
            require(fields['Value'] == source['value'] and fields.get('Footprint', '') == source.get('footprint', ''),
                    'Schematic value/footprint mismatch: ' + ref)
            require(one(symbol, 'on_board')[1] == ('no' if flag else 'yes'), 'Schematic on_board mismatch: ' + ref)
            excluded = flag or ref in probes or source.get('in_bom') is False
            require(one(symbol, 'in_bom')[1] == ('no' if excluded else 'yes'), 'Schematic in_bom mismatch: ' + ref)
            for key, value in source.get('part_binding', {}).items():
                require(fields.get(key) == value, 'Schematic binding mismatch: ' + ref + '/' + key)
            require(set(fields) <= {'Reference', 'Value', 'Footprint', 'Datasheet', 'Description'} | set(source.get('part_binding', {})),
                    'Unexpected schematic property: ' + ref)
    def markers(schematic):
        return Counter(tuple(one(n, 'at')[1:]) for n in children(schematic, 'no_connect'))
    require(markers(tree) == markers(previous), 'Schematic explicit NC marker positions changed')
    require(sum(markers(tree).values()) == len(intent['no_connects']), 'Schematic NC marker count differs from intent')
    return {'schematic_components': len(placed), 'schematic_units': sum(map(len, placed.values())),
            'explicit_nc_markers': sum(markers(tree).values())}


def check_native(intent_path, candidate, baseline):
    candidate, baseline = Path(candidate), Path(baseline)
    intent = json.loads(Path(intent_path).read_text())
    expected = unique_map([c for c in intent['components'] if c['lib_id'] != 'power:PWR_FLAG'],
                          lambda c: c['reference'], 'intent reference')
    schematic_path = candidate / 'project/telemetry-pod.kicad_sch'
    schematic_result = check_schematic(intent, schematic_path, baseline / 'captured/project/telemetry-pod.kicad_sch')
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
    return {'status': 'PASS', **schematic_result, 'native_components': len(actual), 'native_nets': len(graph(after)),
            'binding_fields_checked': bindings, 'bom_components': len(bom),
            'inputs_sha256': {'schematic': hashlib.sha256(schematic_path.read_bytes()).hexdigest(),
                             'baseline_schematic': hashlib.sha256((baseline / 'captured/project/telemetry-pod.kicad_sch').read_bytes()).hexdigest(),
                             'intent': hashlib.sha256(Path(intent_path).read_bytes()).hexdigest(),
                             **{name: hashlib.sha256((candidate / name).read_bytes()).hexdigest()
                                for name in ['native.xml', 'native-bom.csv', 'erc.json']},
                             'baseline_xml': hashlib.sha256((baseline / 'native.xml').read_bytes()).hexdigest(),
                             'baseline_erc': hashlib.sha256((baseline / 'erc.json').read_bytes()).hexdigest()},
            'scope': 'Native schematic symbol/unit/attribute/binding/NC checks plus XML values/footprint identifiers/bindings/connectivity, BOM membership and ERC only. '
                     'Not board land-pattern, placement, routing, fabrication or operating qualification.'}
