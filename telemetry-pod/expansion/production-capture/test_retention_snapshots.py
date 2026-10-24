"""Historical snapshots survive source evolution; check and materialize refuse corrupted bytes."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('retention_under_test', HERE / 'retain.py')
retain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retain)


def digest(data):
    return hashlib.sha256(data).hexdigest()


class HistoricalSnapshots(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=retain.ROOT / 'build')
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        here = root / 'telemetry-pod/expansion/production-capture'
        dest = here / 'evidence/historical'
        dest.mkdir(parents=True)
        self.patch = patch.multiple(retain, ROOT=root, HERE=here, DEST=dest, POD=root / 'telemetry-pod')
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.rel = 'telemetry-pod/composition/source.bin'
        self.original = b'historical\r\nopaque bytes\x00\xff\n'
        source = root / self.rel
        source.parent.mkdir(parents=True)
        source.write_bytes(self.original)
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        subprocess.run(['git', '-C', str(root), 'add', self.rel], check=True)
        subprocess.run(['git', '-C', str(root), '-c', 'user.name=test', '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'historical bytes'], check=True)
        self.commit = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                     check=True, capture_output=True, text=True).stdout.strip()
        self.item = {'sha256': digest(self.original), 'repository': self.rel}
        self.blob = b'retained prepared output\n'
        blob_path = dest / 'prepared-blobs' / digest(self.blob)
        blob_path.parent.mkdir()
        blob_path.write_bytes(self.blob)
        self.blob_path = blob_path
        tree = {'files': {'inputs/source.bin': self.item,
                         'output.bin': {'sha256': digest(self.blob), 'blob': 'prepared-blobs/' + digest(self.blob)}},
                'empty_directories': ['empty'], 'count': 2}
        (dest / 'prepared-tree.json').write_text(json.dumps(tree))
        for name in ('board', 'schematic'):
            p = dest / 'design' / name
            p.parent.mkdir(exist_ok=True)
            p.write_text(name)
        manifest = {'design': {self.rel: {'retained': 'repository path', 'sha256': digest(self.original)},
                              **{name: {'retained': 'design/' + name, 'sha256': digest(name.encode())}
                                 for name in ('board', 'schematic')}},
                    'emission': {name: {'path': name, 'sha256': digest(name.encode())}
                                 for name in ('board', 'schematic')},
                    'project_install': {},
                    'prepared_tree': {'sha256': retain.sha(dest / 'prepared-tree.json'), 'files': 2, 'blobs': 1}}
        (dest / 'MANIFEST.json').write_text(json.dumps(manifest))
        (dest / 'SHA256SUMS').write_text(''.join(f'{retain.sha(dest / p)}  {p}\n' for p in retain.files(dest)))
        self.historical = {p: (dest / p).read_bytes() for p in retain.files(dest)}
        retain.repair_repository_snapshots()
        source.write_bytes(b'live composition changed')

    def test_live_composition_change_and_exact_reconstruction(self):
        retain.check()
        out = retain.ROOT / 'reconstructed'
        retain.materialize(out)
        self.assertEqual((out / 'inputs/source.bin').read_bytes(), self.original)
        self.assertEqual((out / 'output.bin').read_bytes(), self.blob)
        self.assertTrue((out / 'empty').is_dir())
        for p, data in self.historical.items():
            self.assertEqual((retain.DEST / p).read_bytes(), data)
        record = json.loads((retain.repair_store() / 'RECOVERY.json').read_text())
        self.assertEqual(len(record['blobs']), 1)
        self.assertEqual(record['blobs'][self.item['sha256']]['recovery_commit'], self.commit)

    def assert_both_refuse(self):
        with self.assertRaises(SystemExit):
            retain.check()
        out = retain.ROOT / 'refused'
        with self.assertRaises(SystemExit):
            retain.materialize(out)
        self.assertFalse(out.exists())

    def test_tampered_recovery_blob_refuses(self):
        (retain.repair_store() / 'blobs' / self.item['sha256']).write_bytes(b'tampered')
        self.assert_both_refuse()

    def test_missing_recovery_blob_refuses(self):
        (retain.repair_store() / 'blobs' / self.item['sha256']).unlink()
        self.assert_both_refuse()

    def test_tampered_original_retained_blob_refuses(self):
        self.blob_path.write_bytes(b'tampered retained output')
        self.assert_both_refuse()

    def test_changed_prepared_manifest_refuses(self):
        path = retain.DEST / 'prepared-tree.json'
        path.write_bytes(path.read_bytes() + b' ')
        self.assert_both_refuse()

    def test_recorded_commit_is_immutable_and_verified(self):
        self.assertEqual(retain.resolve_snapshot(dict(self.item, commit=self.commit)), self.original)
        with self.assertRaises(ValueError):
            retain.resolve_snapshot(dict(self.item, commit=self.commit, sha256='0' * 64))
        with self.assertRaisesRegex(ValueError, 'complete immutable object ID'):
            retain.resolve_snapshot(dict(self.item, commit='HEAD'))


if __name__ == '__main__':
    unittest.main()
