"""Project selection and fail-closed I/O checks; runnable with unittest offline."""
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fab = load_script('generate_fab_package')
verify = load_script('verify_io_map')


class ProjectScripts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_fab_project_paths_and_unknown_project(self):
        pod = fab.project_config('telemetry-pod')
        self.assertEqual(pod.directory, REPO / 'telemetry-pod')
        self.assertEqual(pod.manifest_path, REPO / 'telemetry-pod/reports/toolchain/fab-manifest.json')
        self.assertIn('telemetry-pod/telemetry-pod.kicad_pcb', fab.design_input_paths(pod))
        self.assertNotIn('fome-mc.kicad_pcb', fab.design_input_paths(pod))
        with self.assertRaisesRegex(ValueError, 'unknown project'):
            fab.project_config('unknown')
        with self.assertRaisesRegex(ValueError, 'inside this repository'):
            fab.project_config('universal-112')

    def test_fab_renamed_project_artifacts_and_normalization(self):
        pod = fab.Project('pod', self.root / 'pod', 'sensor.kicad_sch', 'layout.kicad_pcb')
        run = self.root / 'run'
        for directory in ('export/kibot/gerbers', 'export/kibot/assembly', 'export/kibot/bom',
                          'export/native', 'netlist'):
            (run / directory).mkdir(parents=True)
        gerber = run / 'export/kibot/gerbers/sensor-F_Cu.gbr'
        gerber.write_text('%TF.CreationDate,volatile*%\n')
        for name in ('top', 'bottom'):
            (run / f'export/kibot/assembly/layout-{name}_pos.csv').write_text('fixture\n')
        (run / 'export/kibot/bom/sensor-bom.csv').write_text('fixture\n')
        (run / 'export/native/sensor-bom.csv').write_text('fixture\n')
        (run / 'netlist/sensor.net').write_text('(source "/volatile/sensor.kicad_sch")')
        (run / 'summary.json').write_text('{}')
        (run / 'snapshot.json').write_text(json.dumps({'project': 'pod', 'files': {
            'sensor.kicad_sch': 'sch-hash', 'layout.kicad_pcb': 'board-hash'}}))
        (run / 'export/result.json').write_text('{}')
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Fixture',
                        '--allow-empty'], check=True)
        with patch.object(fab, 'REPO', self.root):
            manifest = fab.build_manifest(run, 'HEAD', 'asis', pod)
            iso_dt = fab.git_commit_info('HEAD', pod)[1]
            pod.manifest_path.parent.mkdir(parents=True)
            pod.manifest_path.write_text(json.dumps(manifest))
            versions = self.root / 'toolchain/versions.toml'
            versions.parent.mkdir()
            versions.write_text('[projects.pod]\ndir="pod"\nschematic="sensor.kicad_sch"\npcb="layout.kicad_pcb"\n')
            with patch.object(sys, 'argv', ['fab', '--project', 'pod', '--run-dir', str(run), '--verify']), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(fab.main(), 0)
                (pod.gerbers_dir / gerber.name).write_text('corrupt')
                self.assertEqual(fab.main(), 1)
            (run / 'snapshot.json').write_text('{"project":"wrong"}')
            with self.assertRaisesRegex(ValueError, 'not for project'):
                fab.build_manifest(run, 'HEAD', 'asis', pod, update_gerbers=False)
        self.assertEqual(manifest['project'], 'pod')
        self.assertEqual(manifest['board_sha256'], 'board-hash')
        self.assertEqual(manifest['root_schematic_sha256'], 'sch-hash')
        self.assertEqual(len(manifest['artifacts']), 6)
        self.assertIn('pod/export/gerbers/sensor-F_Cu.gbr', manifest['artifacts'])
        self.assertEqual(manifest['artifacts']['pod/export/gerbers/sensor-F_Cu.gbr']['sha256'],
                         fab.sha256_bytes(f'%TF.CreationDate,{iso_dt}*%\n'.encode()))
        self.assertEqual(fab.normalize_fab_text('(source "/volatile/sensor.kicad_sch")', '', '', pod),
                         '(source "sensor.kicad_sch")')
        self.assertFalse((self.root / 'export').exists())

    def test_empty_duplicate_and_missing_io_inputs_fail(self):
        cfg = {'name': 'pod', 'path': self.root}
        with self.assertRaisesRegex(ValueError, 'no io-map for project pod'):
            verify.verify_project_io(cfg)
        path = self.root / 'io-map.csv'
        path.write_text('Connector_Pin,Net_Name\n')
        with self.assertRaisesRegex(ValueError, 'no connector pins'):
            verify.verify_project_io(cfg)
        path.write_text('Connector_Pin,Net_Name\nJ1-1,GND\nJ1-1,GND\n')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            verify.verify_project_io(cfg)
        path.write_text('Connector_Pin,Net_Name\nJ1-1,GND\n')
        with self.assertRaisesRegex(ValueError, 'no interface contracts'):
            verify.verify_project_io(cfg)

    def test_native_fixture_map_and_contract_detect_mutations(self):
        fixture = REPO / 'toolchain/fixtures/rc_filter'
        project = self.root / 'fixture'
        shutil.copytree(fixture, project)
        cfg = {'name': 'fixture-script-test', 'path': project,
               'schematic': 'rc_filter.kicad_sch', 'pcb': 'rc_filter.kicad_pcb'}
        (project / 'contracts').mkdir()
        contract = {
            'schema': 'agent-ee.interface/1',
            'components': {'connector': {'locations': [{'sheet': '/', 'reference': 'J1'}],
                                         'symbols': ['Connector_Generic:Conn_01x03']}},
            'terminals': {f'p{n}': {'component': 'connector', 'pin': str(n)} for n in (1, 2, 3)},
            'allowed_edits': [],
            'invariants': [{
                'id': f'pin-{n}', 'requirement': 'fixture-test',
                'source': {'path': 'io-map.csv', 'locator': f'J1-{n}'},
                'kind': 'named_net', 'terminal': f'p{n}', 'names': [net],
            } for n, net in ((1, '/IN'), (2, '/OUT'), (3, 'GND'))],
        }
        contract_path = project / 'contracts/fixture.interface.json'
        contract_path.write_text(json.dumps(contract))
        map_path = project / 'io-map.csv'
        map_text = 'Connector_Pin,Net_Name\nJ1-1,/IN\nJ1-2,/OUT\nJ1-3,GND\n'
        map_path.write_text(map_text)
        with patch.object(verify, 'REPO', self.root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(verify.verify_project_io(cfg), 0)
            map_path.write_text(map_text.replace('/IN', 'WRONG'))
            self.assertEqual(verify.verify_project_io(cfg), 1)
            map_path.write_text(map_text.replace('J1-3,GND\n', ''))
            with self.assertRaisesRegex(ValueError, 'coverage'):
                verify.verify_project_io(cfg)
            map_path.write_text(map_text)
            contract['invariants'][0]['names'] = ['WRONG']
            contract_path.write_text(json.dumps(contract))
            self.assertEqual(verify.verify_project_io(cfg), 1)
        self.assertEqual((project / cfg['schematic']).read_bytes(), (fixture / cfg['schematic']).read_bytes())
        self.assertTrue(list(self.root.glob('build/runs/verify-io/*/*/snapshot.json')))


if __name__ == '__main__':
    unittest.main()
