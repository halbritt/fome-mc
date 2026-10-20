"""Checker controls on retained native evidence, not expanded-candidate acceptance."""
import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from native_check import check_native, children, one
from agent_ee.symbol_library import parse_sexpr

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'native-candidate'

class NativeCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)
        for name in ['native.xml', 'native-bom.csv', 'erc.json']:
            shutil.copyfile(BASE / name, self.out / name)
        (self.out / 'project').mkdir()
        shutil.copyfile(BASE / 'captured/project/telemetry-pod.kicad_sch', self.out / 'project/telemetry-pod.kicad_sch')
        self.intent = BASE / 'captured/inputs/intent.json'

    def check(self):
        return check_native(self.intent, self.out, BASE)

    def xml_failure(self, mutate, message):
        tree = ET.parse(self.out / 'native.xml')
        mutate(tree)
        tree.write(self.out / 'native.xml')
        with self.assertRaisesRegex(ValueError, message):
            self.check()

    def schematic_failure(self, mutate, message):
        path = self.out / 'project/telemetry-pod.kicad_sch'
        tree = parse_sexpr(path.read_bytes())
        mutate(tree)
        # Parser-level damaged evidence; these copies are never native candidates.
        def serialize(node):
            return '(' + ' '.join(serialize(x) for x in node) + ')' if isinstance(node, list) else json.dumps(node)
        path.write_text(serialize(tree))
        with self.assertRaisesRegex(ValueError, message):
            self.check()

    def test_schematic_missing_flag(self):
        def mutate(tree):
            flag = next(s for s in children(tree, 'symbol') if one(s, 'lib_id')[1] == 'power:PWR_FLAG')
            tree.remove(flag)
        self.schematic_failure(mutate, 'symbol membership')

    def test_schematic_mirror(self):
        self.schematic_failure(lambda t: children(t, 'symbol')[0].append(['mirror', 'x']), 'attribute mismatch')

    def test_schematic_dnp(self):
        self.schematic_failure(lambda t: one(children(t, 'symbol')[0], 'dnp').__setitem__(1, 'yes'), 'attribute mismatch')

    def test_schematic_wrong_unit(self):
        self.schematic_failure(lambda t: one(children(t, 'symbol')[0], 'unit').__setitem__(1, '99'), 'units mismatch')

    def test_schematic_excluded_from_board(self):
        def mutate(tree):
            symbol = next(s for s in children(tree, 'symbol') if one(s, 'on_board')[1] == 'yes')
            one(symbol, 'on_board')[1] = 'no'
        self.schematic_failure(mutate, 'on_board mismatch')

    def test_schematic_included_jumper_bom(self):
        def mutate(tree):
            symbol = next(s for s in children(tree, 'symbol') if any(p[1:3] == ['Reference', 'JP1'] for p in children(s, 'property')))
            one(symbol, 'in_bom')[1] = 'yes'
        self.schematic_failure(mutate, 'in_bom mismatch')

    def test_schematic_moved_nc(self):
        self.schematic_failure(lambda t: one(children(t, 'no_connect')[0], 'at').__setitem__(1, '999'), 'NC marker positions')

    def test_schematic_duplicate_nc(self):
        self.schematic_failure(lambda t: t.append(children(t, 'no_connect')[0]), 'NC marker positions')

    def test_schematic_missing_binding(self):
        def mutate(tree):
            symbol = next(s for s in children(tree, 'symbol') if any(p[1] == 'PARAM_Datasheet' for p in children(s, 'property')))
            symbol.remove(next(p for p in children(symbol, 'property') if p[1] == 'PARAM_Datasheet'))
        self.schematic_failure(mutate, 'binding mismatch')

    def test_retained_native_passes(self):
        self.assertEqual(self.check()['native_components'], 326)

    def test_corrupted_binding(self):
        self.xml_failure(lambda t: setattr(t.find('./components/comp/fields/field[@name="PARAM_Datasheet"]'), 'text', 'truncated'), 'binding mismatch')

    def test_wrong_footprint(self):
        self.xml_failure(lambda t: setattr(t.find('./components/comp/footprint'), 'text', 'wrong'), 'footprint mismatch')

    def test_wrong_value(self):
        self.xml_failure(lambda t: setattr(t.find('./components/comp/value'), 'text', 'wrong'), 'value mismatch')

    def test_missing_component(self):
        self.xml_failure(lambda t: t.find('./components').remove(t.find('./components/comp')), 'membership')

    def test_duplicate_component(self):
        self.xml_failure(lambda t: t.find('./components').append(t.find('./components/comp')), 'Duplicate native')

    def test_wrong_pin(self):
        self.xml_failure(lambda t: t.find('./nets/net/node').set('pin', '999'), 'graph')

    def test_missing_net(self):
        self.xml_failure(lambda t: t.find('./nets').remove(t.find('./nets/net')), 'graph')

    def test_duplicate_field(self):
        self.xml_failure(lambda t: t.find('./components/comp/fields').append(t.find('./components/comp/fields/field')), 'Duplicate field')

    def test_missing_bom_row(self):
        path = self.out / 'native-bom.csv'
        lines = path.read_text().splitlines(keepends=True)
        path.write_text(''.join(lines[:1] + lines[2:]))
        with self.assertRaisesRegex(ValueError, 'BOM membership'):
            self.check()

    def test_extra_identity(self):
        def mutate(tree):
            ET.SubElement(tree.find('./components/comp[@ref="R60"]/fields'), 'field', name='LCSC').text = 'C123'
        self.xml_failure(mutate, 'Unexpected or missing')

    def test_bom_exclusion(self):
        path = self.out / 'native-bom.csv'
        with path.open() as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        rows[0]['ExcludeBoard'] = 'yes'
        with path.open('w') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(ValueError, 'exclusion policy'):
            self.check()

    def test_erc_sheet_coverage(self):
        path = self.out / 'erc.json'
        data = json.loads(path.read_text())
        data['sheets'] = [{'path': '/invented/', 'uuid': 'invented', 'violations': []}]
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'sheet coverage'):
            self.check()

    def test_erc_violation(self):
        path = self.out / 'erc.json'
        data = json.loads(path.read_text())
        data['sheets'][0]['violations'].append({'severity': 'error'})
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'ERC violations'):
            self.check()

    def test_relaxed_erc_policy(self):
        path = self.out / 'erc.json'
        data = json.loads(path.read_text())
        data['ignored_checks'].append('newly_ignored')
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'ERC policy'):
            self.check()

if __name__ == '__main__':
    unittest.main()
