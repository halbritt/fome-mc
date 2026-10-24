"""Corrupt in-memory copies of the saved candidate; every source mismatch must refuse."""
import importlib.util
import json
import unittest
from pathlib import Path
import pcbnew
from agent_ee.native_netlist import read_native_inventory

PACKET=Path(__file__).resolve().parents[1]
PRODUCER=PACKET.parents[1]
spec=importlib.util.spec_from_file_location('j2_verifier',PRODUCER/'verify_j2.py')
verifier=importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class InventoryRefusals(unittest.TestCase):
    def setUp(self):
        self.board=pcbnew.LoadBoard(str(PACKET/'pipe/emission/design/project/telemetry-pod.kicad_pcb'))
        self.native=read_native_inventory(PACKET/'pipe/emission/native.xml')
        self.intent=json.loads((PACKET/'cap/composition/intent.writer.json').read_text())
        self.j2=self.board.FindFootprintByReference('J2')

    def refuses(self,reason):
        with self.assertRaisesRegex(ValueError,reason):
            verifier.verify_inventory(self.board,self.native,self.intent,PACKET/'cap')

    def test_same_count_wrong_reference(self):
        self.j2.SetReference('X999')
        self.refuses('footprint inventory differs')

    def test_duplicate_reference(self):
        self.j2.SetReference('J1')
        self.refuses('footprint inventory differs')

    def test_pad_inventory_changed(self):
        next(p for p in self.j2.Pads() if p.GetNumber()=='1').SetNumber('99')
        self.refuses('physical pad inventory differs')

    def test_connected_pad_net_changed(self):
        ground=next(p for p in self.j2.Pads() if p.GetNumber()=='2')
        next(p for p in self.j2.Pads() if p.GetNumber()=='1').SetNetCode(ground.GetNetCode())
        self.refuses('frozen source pad/net mismatch')

    def test_native_identity_changed(self):
        self.native['components']['J2']['binding_fields']['Partnumber']='wrong-part'
        self.refuses('part identity differs')


if __name__=='__main__':
    unittest.main(verbosity=2)
