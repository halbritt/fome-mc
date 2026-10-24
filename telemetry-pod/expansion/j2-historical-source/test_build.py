"""AGENTEE-485 J2: the external 132134 record replays, and a stale source hash or a Molex identity refuses."""
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agent_ee.datasheet_capture import import_historical_pdf
from agent_ee.part_record import qualify_external_record

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location('j2_build', HERE / 'build.py')
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)


class J2Record(unittest.TestCase):
    def test_replay(self):
        build.run(verify=True)
        record = json.loads((HERE / '132134.json').read_text())
        self.assertEqual((record['mpn'], record['manufacturer'], record['lcsc'], record['stock']),
                         ('132134', 'Amphenol RF', 'NO_LCSC', None))
        self.assertTrue(qualify_external_record(record, ROOT))

    def test_stale_source_hash_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = json.loads((HERE / 'sources.json').read_text())
            note[0]['sha256'] = '0' * 64  # a note pinning other bytes than the retained drawing
            (Path(tmp) / 'sources.json').write_text(json.dumps(note))
            raw = (Path(tmp) / 'sources.json').read_bytes()
            locator = {'path': 'sources.json', 'sha256': build.hashlib.sha256(raw).hexdigest(), 'entry': 0}
            with self.assertRaisesRegex(ValueError, 'does not bind PDF hash'):
                import_historical_pdf(build.PDF, tmp, locator, 'J2', Path(tmp) / 'acquisition')
            self.assertFalse((Path(tmp) / 'acquisition').exists())

    def test_stale_artifact_hash_refuses(self):
        record = json.loads((HERE / '132134.json').read_text())
        stale = copy.deepcopy(record)
        stale['artifact']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            qualify_external_record(stale, ROOT)

    def test_molex_identity_refuses(self):
        record = json.loads((HERE / '132134.json').read_text())
        for field, value in (('mpn', '732511150'), ('manufacturer', 'MOLEX'), ('lcsc', 'C841205')):
            molex = {**copy.deepcopy(record), field: value}
            with self.assertRaises(ValueError, msg=field):
                qualify_external_record(molex, ROOT)

    def test_molex_declaration_refuses(self):
        # The identity declaration itself rewritten to the Molex part no longer matches the 132134 deviation.
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            identity = json.loads((HERE / 'identity.json').read_text())
            identity.update(mpn='732511150', manufacturer='MOLEX')
            path = Path(tmp) / 'identity.json'
            path.write_text(json.dumps(identity))
            record = json.loads((HERE / '132134.json').read_text())
            record['identity_source'] = {**build.blob(path), 'locator': '/'}
            with self.assertRaisesRegex(ValueError, 'differs from hand-fit deviation'):
                qualify_external_record(record, ROOT)


if __name__ == '__main__':
    unittest.main()
