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
        self.assertEqual(len(pins), 55)
        self.assertEqual(pins['J1-1'], '/POD_CAN_P')
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
        cfg = {'name': 'fixture', 'path': project,
               'schematic': 'rc_filter.kicad_sch', 'pcb': 'rc_filter.kicad_pcb'}
        (self.root / 'contracts').mkdir()
        (self.root / 'contracts/unrelated.interface.json').write_text('{}')
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
        self.write_map(map_path, [('J1-1', '/IN'), ('J1-2', '/OUT'), ('J1-3', 'GND')])
        map_text = map_path.read_text()
        output = io.StringIO()
        with patch.object(verify, 'REPO', self.root), contextlib.redirect_stdout(output):
            self.assertEqual(verify.verify_project_io(cfg), 0)
            map_path.write_text(map_text.replace('/IN', 'WRONG'))
            self.assertEqual(verify.verify_project_io(cfg), 1)
            self.write_map(map_path, [('J1-1', '/IN'), ('J1-2', '/OUT')])
            output.truncate(0)
            output.seek(0)
            self.assertEqual(verify.verify_project_io(cfg), 1)
            self.assertIn("io-map connector coverage: missing=[('J1', '3')]", output.getvalue())
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
        original_bytes = (REPO / 'contracts/telemetry-pod.interface.json').read_bytes()
        original = json.loads(original_bytes)
        cfg = dict(verify.eda.project_config('telemetry-pod'), path=project)
        for rel in (verify.POD_RECORD,):
            shutil.copyfile(REPO / rel, self.root / rel)
        # The candidate is a committed revision of the real repository.
        candidate = verify.pod_candidate_config(verify.eda.project_config('telemetry-pod'))

        def run(contract):
            contract_path.write_bytes(original_bytes if contract == original else json.dumps(contract).encode())
            output = io.StringIO()
            with patch.object(verify, 'REPO', self.root), patch.object(verify, 'pod_candidate_config',
                                                                       lambda _: candidate), \
                    contextlib.redirect_stdout(output):
                result = verify.verify_project_io(cfg)
            return result, output.getvalue()

        result, output = run(original)
        self.assertEqual(result, 0, output)
        self.assertIn('NOT_EVALUATED: BLE-RADIO', output)
        self.assertIn('193/194 invariants satisfied', output)
        self.assertIn('PASS: candidate 3688390f4b30506f2c32af4550c10c53bd9f0205433d8126b012702939704928', output)
        self.assertIn('REQUIREMENT_AUTHORITY: sourced: none;', output)
        for mutation in ('net', 'pin', 'nc', 'unresolved', 'unknown', 'missing', 'same-net-swap', 'drop-wireless'):
            with self.subTest(mutation=mutation):
                contract = copy.deepcopy(original)
                terminals = contract['terminals']
                if mutation == 'net':
                    contract['invariants'][0]['names'] = ['WRONG']
                elif mutation == 'pin':
                    terminals['J1-1'], terminals['J1-2'] = terminals['J1-2'], terminals['J1-1']
                elif mutation == 'nc':
                    terminals['J1-35'], terminals['J1-3'] = terminals['J1-3'], terminals['J1-35']
                elif mutation == 'unresolved':
                    terminals['J1-1'] = {'unresolved': 'deliberate scratch mutation'}
                elif mutation == 'unknown':
                    inv = contract['invariants'][0]
                    inv.pop('terminal'); inv.pop('names')
                    inv.update(kind='unresolved', reason='deliberate scratch unknown')
                elif mutation == 'missing':
                    del terminals['J1-35']
                    contract['invariants'] = [i for i in contract['invariants'] if i.get('terminal') != 'J1-35']
                elif mutation == 'same-net-swap':
                    terminals['J1-5'], terminals['J1-8'] = terminals['J1-8'], terminals['J1-5']
                elif mutation == 'drop-wireless':
                    contract['invariants'] = [i for i in contract['invariants'] if i['id'] != 'BLE-RADIO:net']
                result, output = run(contract)
                self.assertEqual(result, 1, output)
                self.assertIn('FAIL:', output)
                if mutation == 'same-net-swap':
                    self.assertIn('differs from fresh AGENTEE-188 compile', output)
                if mutation in ('drop-wireless', 'missing'):
                    # Every record row must stay cited; agent-ee's loader refuses first.
                    self.assertIn('qualification record rows are not all cited', output)
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
                self.assertIn('io_map CSV must be captured with matching sha256', output)
                map_path.write_bytes(raw)

        # Bindings and indirect paths are compiler inputs too, even if the
        # committed contract still evaluates against the unchanged native board.
        bindings_path = project / 'pinout-checks/bindings.json'
        raw_bindings = bindings_path.read_bytes()
        bindings = json.loads(raw_bindings)
        terminals = bindings['terminals']
        terminals['J1-5'], terminals['J1-8'] = terminals['J1-8'], terminals['J1-5']
        bindings_path.write_text(json.dumps(bindings))
        result, output = run(original)
        self.assertEqual(result, 1, output)
        self.assertIn('differs from fresh AGENTEE-188 compile', output)
        bindings_path.write_bytes(raw_bindings)

        paths_path = project / 'pinout-checks/paths.json'
        raw_paths = paths_path.read_bytes()
        paths_path.write_text('{"schema":"invalid","paths":{}}')
        result, output = run(original)
        self.assertEqual(result, 1, output)
        self.assertIn('pod contract compile failed (rc=2)', output)
        paths_path.write_bytes(raw_paths)

    def pod_inputs(self):
        """The captured files the pod scope reads, copied under self.root (REPO is patched to it)."""
        for rel in (verify.POD_CONTRACT, verify.POD_RECORD, verify.POD_CSV, verify.POD_V9_ORIGIN,
                    verify.POD_REQUIREMENTS):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / rel, self.root / rel)
        return (json.loads((self.root / verify.POD_CONTRACT).read_bytes()),
                json.loads((self.root / verify.POD_RECORD).read_bytes()))

    def write_bundle(self, contract, record):
        """Write a record and re-pin it in the contract, as a consistent tamperer would."""
        raw = json.dumps(record, indent=2).encode()
        contract = copy.deepcopy(contract)
        if 'qualification_record' in contract:
            contract['qualification_record']['sha256'] = verify.hashlib.sha256(raw).hexdigest()
        (self.root / verify.POD_RECORD).write_bytes(raw)
        (self.root / verify.POD_CONTRACT).write_text(json.dumps(contract))

    def capability(self):
        with patch.object(verify, 'REPO', self.root):
            descriptor = verify.pod_capability()
            rows = verify.read_project_rows(self.root / verify.POD_CSV)
            return descriptor, verify.check_pod_history(descriptor, rows)

    def test_pod_carried_citations_stay_unqualified_through_agent_ee(self):
        contract, record = self.pod_inputs()
        descriptor, errors = self.capability()
        self.assertEqual(errors, [])
        authority, history = descriptor['requirement_authority'], descriptor['requirement_history']
        self.assertEqual(authority['sourced'], [])
        self.assertIn('POD-IF-CAN1', authority['unqualified-carryover'])
        self.assertEqual(history['origin_verification'], {verify.POD_V9_ORIGIN: 'verified'})
        j1 = next(r for r in history['rows'] if r['row'] == 2)
        self.assertEqual(j1['requirements'], {'POD-IF-CAN1': 'unqualified historical assertion',
                                              'POD-IF-HARNESS-CONNECTOR': 'unqualified historical assertion'})
        self.assertEqual(j1['origin'], 'verified')
        carried = [r for r in record['rows'] if r['origin']['locator'].startswith('row ')]
        self.assertEqual(len(carried), 25)
        self.assertTrue(all(q['qualification'] == 'unqualified-carryover' for r in record['rows']
                            for q in r['requirements']))

        # Regression: a consistent bundle that promotes J1-1's citation to `sourced`
        # (contract, record and pin all agree, the cited source is a captured file).
        # agent-ee's loader accepts it and its authority would count POD-IF-CAN1 as
        # sourced; this verifier refuses it.
        sha = verify.hashlib.sha256((self.root / verify.POD_REQUIREMENTS).read_bytes()).hexdigest()
        promoted = {'id': 'POD-IF-CAN1', 'qualification': 'sourced',
                    'source': {'path': verify.POD_REQUIREMENTS, 'sha256': sha, 'locator': 'Interfaces / CAN1'}}
        upgraded_record, upgraded_contract = copy.deepcopy(record), copy.deepcopy(contract)
        for row in upgraded_record['rows']:
            if row['connector_pin'] in ('J1-1', 'J1-2'):
                row['requirements'][0] = promoted
        for inv in upgraded_contract['invariants']:
            if inv['io_map']['connector_pin'] in ('J1-1', 'J1-2'):
                inv['io_map']['requirements'][0] = promoted
        self.write_bundle(upgraded_contract, upgraded_record)
        descriptor, errors = self.capability()
        self.assertEqual(descriptor['requirement_authority']['sourced'], ['POD-IF-CAN1'])
        self.assertIn("sourced requirement in the pod contract: ['POD-IF-CAN1']", '\n'.join(errors))

        # The rev3c contract (bare IDs, no record) cannot stand in for the bound one.
        legacy = subprocess.run(['git', '-C', str(REPO), 'show', 'bb58520:contracts/telemetry-pod.interface.json'],
                                capture_output=True, check=True).stdout
        (self.root / verify.POD_CONTRACT).write_bytes(legacy)
        with self.assertRaisesRegex(ValueError, 'contract must declare the qualification record pinned by the scope'):
            self.capability()

        def refused(change, message):
            c, r = copy.deepcopy(contract), copy.deepcopy(record)
            change(c, r)
            self.write_bundle(c, r)
            with self.assertRaisesRegex(ValueError, message):
                self.capability()

        cases = {
            'citation status lost': (lambda c, r: c['invariants'][0]['io_map']['requirements'].pop(),
                                     'differs from qualification record'),
            'record status upgraded alone': (lambda c, r: r['rows'][0]['requirements'][0].update(
                qualification='sourced'), 'expected fields'),
            'record row stripped': (lambda c, r: r['rows'].pop(0), 'differs from qualification record'),
            'declaration stripped': (lambda c, r: c.pop('qualification_record'),
                                     'contract must declare the qualification record'),
            'origin digest rewritten': (lambda c, r: [row['origin'].update(sha256='0' * 64) for row in r['rows']],
                                        'differs from its declared sha256'),
        }
        for name, (change, message) in cases.items():
            with self.subTest(mutation=name):
                refused(change, message)
        with self.subTest(mutation='contract upgraded, record unchanged'):
            c = copy.deepcopy(contract)
            c['invariants'][0]['io_map']['requirements'][0] = promoted
            (self.root / verify.POD_RECORD).write_text(json.dumps(record, indent=2))
            c['qualification_record']['sha256'] = verify.hashlib.sha256(
                (self.root / verify.POD_RECORD).read_bytes()).hexdigest()
            (self.root / verify.POD_CONTRACT).write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError, 'differs from qualification record'):
                self.capability()
        with self.subTest(mutation='record deleted'):
            (self.root / verify.POD_RECORD).unlink()
            with self.assertRaisesRegex(ValueError, 'missing qualification record'):
                self.capability()

        # What the loader does not prove: the located v9 row really holds the carried values.
        with self.subTest(mutation='v9 locator moved to another row'):
            r = copy.deepcopy(record)
            r['rows'][0]['origin']['locator'] = r['rows'][0]['origin']['locator'].replace(
                'row 2 (AMPSEAL-1)', 'row 4 (AMPSEAL-3)')
            self.write_bundle(contract, r)
            _, errors = self.capability()
            self.assertIn('J1-1: carried values differ from v9 row AMPSEAL-3', errors)
        with self.subTest(mutation='carried row relabelled uncarried'):
            r = copy.deepcopy(record)
            r['rows'][0]['origin']['locator'] = 'none'
            self.write_bundle(contract, r)
            _, errors = self.capability()
            self.assertIn('without a located v9 origin row', '\n'.join(errors))


if __name__ == '__main__':
    unittest.main()
