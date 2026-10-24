"""Native negative controls for the complete production J2 identity."""
import importlib.util
import unittest
from pathlib import Path
import pcbnew

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('j2_verifier', HERE / 'verify_j2.py')
verify_j2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_j2)


class J2Identity(unittest.TestCase):
    def setUp(self):
        self.board = pcbnew.LoadBoard(str(HERE / 'diagnostics/ee485-J2b/scaffold/telemetry-pod.kicad_pcb'))
        self.fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'J2')

    def test_exact_native_identity(self):
        verify_j2.verify_identity(self.fp)

    def test_same_prefix_wrong_uuid_refuses(self):
        self.fp.SetUuidDirect(pcbnew.KIID('18c6ebf4-0000-0000-0000-000000000000'))
        with self.assertRaisesRegex(ValueError, 'wrong J2 native UUID'):
            verify_j2.verify_identity(self.fp)

class RuleAreaControls(J2Identity):
    def verify(self, binding=None):
        import json
        binding = binding or json.loads((HERE / 'composition/j2-rf-binding.json').read_text())
        return verify_j2.verify_rule_areas(self.board, binding, HERE / 'composition/envelope.json')

    def test_source_to_native_rules(self):
        self.assertEqual(len(self.verify()), 2)

    def test_all_prohibitions_are_checked(self):
        for setter, getter in (('SetDoNotAllowTracks', 'GetDoNotAllowTracks'),
                               ('SetDoNotAllowVias', 'GetDoNotAllowVias'),
                               ('SetDoNotAllowPads', 'GetDoNotAllowPads'),
                               ('SetDoNotAllowFootprints', 'GetDoNotAllowFootprints'),
                               ('SetDoNotAllowZoneFills', 'GetDoNotAllowZoneFills')):
            with self.subTest(prohibition=setter):
                self.setUp()
                zone = next(z for z in self.board.Zones() if z.GetIsRuleArea())
                getattr(zone, setter)(not getattr(zone, getter)())
                with self.assertRaisesRegex(ValueError, 'layers/prohibitions changed'):
                    self.verify()

    def test_wrong_layer_refuses(self):
        zone = next(z for z in self.board.Zones() if z.GetIsRuleArea())
        layers = pcbnew.LSET()
        layers.AddLayer(pcbnew.F_Cu)
        zone.SetLayerSet(layers)
        with self.assertRaisesRegex(ValueError, 'layers/prohibitions changed'):
            self.verify()

    def test_wrong_source_uuid_refuses(self):
        import json
        binding = json.loads((HERE / 'composition/j2-rf-binding.json').read_text())
        next(iter(binding['rule_area_bindings'].values()))['source_uuid'] = 'wrong-source'
        with self.assertRaisesRegex(ValueError, 'identity mapping differs'):
            self.verify(binding)


if __name__ == '__main__':
    unittest.main()
