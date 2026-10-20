"""Project selection and fail-closed I/O checks; runnable with unittest offline."""
import contextlib
import copy
import csv
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
        run_root = REPO / 'build/runs'
        run_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=run_root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_map(self, path, pins):
        with path.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=verify.PROJECT_MAP_COLUMNS)
            writer.writeheader()
            for identity, net in pins:
                row = dict.fromkeys(verify.PROJECT_MAP_COLUMNS, 'N/A')
                row.update(Connector_Pin=identity, Net=net)
                writer.writerow(row)

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
        self.write_map(path, [])
        with self.assertRaisesRegex(ValueError, 'no connector pins'):
            verify.verify_project_io(cfg)
        self.write_map(path, [('J1-1', 'GND'), ('J1-1', 'GND')])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            verify.verify_project_io(cfg)
        self.write_map(path, [('J1-1', 'GND')])
        with self.assertRaisesRegex(ValueError, 'no interface contracts'):
            verify.verify_project_io(cfg)

    def test_project_map_requires_exact_header(self):
        path = self.root / 'io-map.csv'
        good = ','.join(verify.PROJECT_MAP_COLUMNS)
        for header in ('Connector_Pin,Net_Name', good.replace(',Net,', ',Net_Name,'),
                       good + ',Extra', ','.join(reversed(verify.PROJECT_MAP_COLUMNS))):
            with self.subTest(header=header):
                path.write_text(header + '\n')
                with self.assertRaisesRegex(ValueError, 'header must be exactly'):
                    verify.read_project_map(path)
        self.write_map(path, [('J1-1', 'GND')])
        with path.open('a') as stream:
            stream.write('J1-2,GND\n')
        with self.assertRaisesRegex(ValueError, 'invalid io-map row'):
            verify.read_project_map(path)

    def test_landed_pod_map_reads_before_missing_root_contract(self):
        source = REPO / 'telemetry-pod/io-map.csv'
        pins = verify.read_project_map(source)
        self.assertEqual(len(pins), 32)
        self.assertEqual(pins['AMPSEAL-1'], '/POD_CAN_P')
        self.assertEqual(pins['BLE-RADIO'], 'N/A')
        project = self.root / 'telemetry-pod'
        project.mkdir()
        shutil.copyfile(source, project / 'io-map.csv')
        (project / 'contracts').mkdir()
        (project / 'contracts/telemetry-pod.interface.json').write_text('{}')
        (self.root / 'contracts').mkdir()
        (self.root / 'contracts/ecu.interface.json').write_text('{}')
        with patch.object(verify, 'REPO', self.root):
            with self.assertRaisesRegex(ValueError, f'missing interface contract: {self.root}/contracts/telemetry-pod.interface.json'):
                verify.verify_project_io({'name': 'telemetry-pod', 'path': project})

    def test_native_fixture_map_and_contract_detect_mutations(self):
        fixture = REPO / 'toolchain/fixtures/rc_filter'
        project = self.root / 'fixture'
        shutil.copytree(fixture, project)
        cfg = {'name': 'telemetry-pod', 'path': project,
               'schematic': 'rc_filter.kicad_sch', 'pcb': 'rc_filter.kicad_pcb'}
        (self.root / 'contracts').mkdir()
        (self.root / 'contracts/unrelated.interface.json').write_text('{}')
        (project / 'contracts').mkdir()
        (project / 'contracts/wrong-location.interface.json').write_text('{}')
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
        contract_path = self.root / 'contracts/telemetry-pod.interface.json'
        contract_path.write_text(json.dumps(contract))
        map_path = project / 'io-map.csv'
        self.write_map(map_path, [('J1-1', '/IN'), ('J1-2', '/OUT'), ('J1-3', 'GND')])
        map_text = map_path.read_text()
        with patch.object(verify, 'REPO', self.root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(verify.verify_project_io(cfg), 0)
            map_path.write_text(map_text.replace('/IN', 'WRONG'))
            self.assertEqual(verify.verify_project_io(cfg), 1)
            self.write_map(map_path, [('J1-1', '/IN'), ('J1-2', '/OUT')])
            self.assertEqual(verify.verify_project_io(cfg), 1)
            map_path.write_text(map_text)
            contract['invariants'][0]['names'] = ['WRONG']
            contract_path.write_text(json.dumps(contract))
            self.assertEqual(verify.verify_project_io(cfg), 1)
        self.assertEqual((project / cfg['schematic']).read_bytes(), (fixture / cfg['schematic']).read_bytes())
        self.assertTrue(list(self.root.glob('build/runs/verify-io/*/*/snapshot.json')))


    def test_real_pod_bindings_and_fail_closed_mutations(self):
        project = self.root / 'telemetry-pod'
        shutil.copytree(REPO / 'telemetry-pod', project)
        (self.root / 'contracts').mkdir()
        contract_path = self.root / 'contracts/telemetry-pod.interface.json'
        original = json.loads((REPO / 'contracts/telemetry-pod.interface.json').read_text())
        cfg = dict(verify.eda.project_config('telemetry-pod'), path=project)

        def run(contract):
            contract_path.write_text(json.dumps(contract))
            output = io.StringIO()
            with patch.object(verify, 'REPO', self.root), contextlib.redirect_stdout(output):
                result = verify.verify_project_io(cfg)
            return result, output.getvalue()

        result, output = run(original)
        self.assertEqual(result, 0, output)
        self.assertIn('NOT_EVALUATED: BLE-RADIO', output)
        self.assertIn('81/82 invariants satisfied', output)
        for mutation in ('net', 'pin', 'nc', 'unresolved', 'unknown', 'missing'):
            with self.subTest(mutation=mutation):
                contract = copy.deepcopy(original)
                terminals = contract['terminals']
                if mutation == 'net':
                    contract['invariants'][0]['names'] = ['WRONG']
                elif mutation == 'pin':
                    terminals['AMPSEAL-1'], terminals['AMPSEAL-2'] = terminals['AMPSEAL-2'], terminals['AMPSEAL-1']
                elif mutation == 'nc':
                    terminals['AMPSEAL-17'], terminals['AMPSEAL-3'] = terminals['AMPSEAL-3'], terminals['AMPSEAL-17']
                elif mutation == 'unresolved':
                    terminals['AMPSEAL-1'] = {'unresolved': 'deliberate scratch mutation'}
                elif mutation == 'unknown':
                    inv = contract['invariants'][0]
                    inv.pop('terminal'); inv.pop('names')
                    inv.update(kind='unresolved', reason='deliberate scratch unknown')
                elif mutation == 'missing':
                    del terminals['AMPSEAL-23']
                    contract['invariants'] = [i for i in contract['invariants'] if i.get('terminal') != 'AMPSEAL-23']
                result, output = run(contract)
                self.assertEqual(result, 1, output)
                self.assertIn('FAIL:', output)
        for source in (REPO / 'telemetry-pod').glob('*.kicad_*'):
            self.assertEqual(source.read_bytes(), (project / source.name).read_bytes())

        # CSV net and MCU pin changes must refuse a stale compiled contract.
        map_path = project / 'io-map.csv'
        raw = map_path.read_bytes()
        for old, new in ((b'/POD_CAN_P', b'/WRONG'), (b'U1,4;5,', b'U1,4;6,')):
            with self.subTest(stale_map=new):
                self.assertIn(old, raw)
                map_path.write_bytes(raw.replace(old, new))
                result, output = run(original)
                self.assertEqual(result, 1, output)
                self.assertIn('stale io-map citation', output)
                map_path.write_bytes(raw)


if __name__ == '__main__':
    unittest.main()
