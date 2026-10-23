"""AGENTEE-485 slice A controls for launch.py preflight (H1, H5) and the required-stage set (X1).

Pure controls (no container): run with
  /usr/bin/python3 -I -B -m unittest telemetry-pod/expansion/production-capture/test_launch_preflight.py
They use the real committed receipt evidence/production-runtime-485d and the real delivered retention's pipeline.json;
the stale-receipt negative copies that receipt into a scratch git repository. The live H1 import probe (the campaign
container itself) is runtime_import_probe.sh.
"""
import copy
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


launch, required_stages = load('launch'), load('required_stages')
RECEIPT_DIR = HERE / 'evidence/production-runtime-485d'
RECEIPT = json.loads((RECEIPT_DIR / 'receipt.json').read_text())
MANIFEST = json.loads((HERE / 'runtime/agentee-485d.json').read_text())
DELIVERED = json.loads((HERE / 'evidence/emission-8ab3b0b9-agentee485/pipeline.json').read_text())


class Refused(Exception):
    pass


class LaunchPreflight(unittest.TestCase):
    def setUp(self):
        self._refuse = launch.refuse
        launch.refuse = lambda why: (_ for _ in ()).throw(Refused(why))

    def tearDown(self):
        launch.refuse = self._refuse

    # H5: committed receipt bytes.
    def test_committed_receipt_positive(self):
        self.assertEqual(launch.committed_receipt_problems(RECEIPT_DIR, launch.git('rev-parse', 'HEAD')), [])

    def test_stale_or_copied_receipt_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = RECEIPT_DIR.relative_to(launch.ROOT)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            shutil.copytree(RECEIPT_DIR, root / rel)
            subprocess.run(['git', '-C', str(root), 'add', '-A'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'r'],
                           check=True)
            saved = launch.ROOT
            launch.ROOT = root
            try:
                head = launch.git('rev-parse', 'HEAD')
                self.assertEqual(launch.committed_receipt_problems(root / rel, head), [])
                # an accidentally copied/stale receipt: same path, other bytes than the tracked blob
                (root / rel / 'receipt.json').write_bytes((RECEIPT_DIR / 'receipt.json').read_bytes() + b' ')
                problems = launch.committed_receipt_problems(root / rel, head)
                self.assertTrue(any('receipt.json differs from its tracked blob' in p for p in problems), problems)
                # an untracked file beside the receipt
                (root / rel / 'receipt.json').write_bytes((RECEIPT_DIR / 'receipt.json').read_bytes())
                (root / rel / 'copy.json').write_text('{}')
                problems = launch.committed_receipt_problems(root / rel, head)
                self.assertTrue(any('copy.json is not tracked' in p for p in problems), problems)
                # a receipt directory that was never committed
                shutil.copytree(root / rel, root / (str(rel) + '-copy'))
                problems = launch.committed_receipt_problems(root / (str(rel) + '-copy'), head)
                self.assertTrue(any('is not a tracked receipt' in p for p in problems), problems)
            finally:
                launch.ROOT = saved

    # H5: invocation image equals the bound runtime digest.
    def test_image_positive(self):
        self.assertEqual(launch.image_problems(RECEIPT, MANIFEST, MANIFEST['config']), [])

    def test_mismatched_image_refuses(self):
        other = 'sha256:' + '0' * 64
        receipt = copy.deepcopy(RECEIPT)
        receipt['invocation']['image']['reference'] = other
        self.assertTrue(any('is not the bound runtime config digest' in p
                            for p in launch.image_problems(receipt, MANIFEST, MANIFEST['config'])))
        self.assertTrue(any('local image ID' in p for p in launch.image_problems(RECEIPT, MANIFEST, other)))
        self.assertTrue(any('local image ID' in p for p in launch.image_problems(RECEIPT, MANIFEST, None)))

    # H1: the receipt's recorded runner must be the selected runtime's.
    def test_485d_receipt_records_the_image_runner_and_refuses(self):
        self.assertEqual(launch.runner(MANIFEST), ('/pod/export/src', '/pod/export'))
        problems = launch.runner_problems(RECEIPT, MANIFEST)
        self.assertTrue(problems and "'/opt/agent-ee'" in problems[0], problems)

    def test_mounted_runner_receipt_positive(self):
        receipt = copy.deepcopy(RECEIPT)
        receipt['invocation']['cwd'] = '/pod/export'
        receipt['invocation']['container'] = [('PYTHONPATH=/pod/export/src' if a.startswith('PYTHONPATH=') else a)
                                              for a in receipt['invocation']['container']]
        self.assertEqual(launch.runner_problems(receipt, MANIFEST), [])

    def test_import_problems_altered_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp)
            (export / 'src/agent_ee').mkdir(parents=True)
            (export / 'src/agent_ee/cli.py').write_bytes(b'pin\n')
            (export / 'src/agent_ee/__init__.py').write_bytes(b'')
            files = {'__init__.py': launch.sha(export / 'src/agent_ee/__init__.py'), 'cli.py': launch.sha(export / 'src/agent_ee/cli.py')}
            good = {'package': '/pod/export/src/agent_ee', 'cli': '/pod/export/src/agent_ee/cli.py', 'files': files}
            self.assertEqual(launch.import_problems(good, export, '/pod/export/src', b'pin\n'), [])
            image = dict(good, package='/opt/agent-ee/src/agent_ee', cli='/opt/agent-ee/src/agent_ee/cli.py')
            self.assertTrue(launch.import_problems(image, export, '/pod/export/src', b'pin\n'))
            altered = dict(good, files=dict(files, **{'cli.py': '1' * 64}))
            self.assertTrue(launch.import_problems(altered, export, '/pod/export/src', b'pin\n'))
            self.assertTrue(launch.import_problems(good, export, '/pod/export/src', b'other\n'))


class RequiredStages(unittest.TestCase):
    def test_dispatch_five_are_required(self):
        for name in ('placement.scope_locality_binding', 'pod_driver.validate_plan', 'placement.block_candidates_repack',
                     'blocks.stage_owned_variants C1 (AGENTEE-485 R2)', 'campaign.authorized_budget production scope'):
            self.assertIn(name, required_stages.REQUIRED)

    def test_every_pipeline_stage_is_classified(self):
        import re
        names = re.findall(r"^stage\('([^']+)'", (HERE / 'pipeline.py').read_text(), re.M)
        self.assertEqual(sorted(names), sorted(required_stages.REQUIRED))
        self.assertEqual(sorted(set(DELIVERED['stages']) | {'blocks.stage_owned_variants C1 (AGENTEE-485 R2)'}),
                         sorted(required_stages.REQUIRED))

    def test_delivered_retention_has_a_refused_required_stage(self):
        problems = required_stages.problems(DELIVERED['stages'])
        self.assertTrue(any("'placement.scope_locality_binding' is 'refused'" in p for p in problems), problems)

    def test_all_accepted_positive_and_refused_c1_negative(self):
        stages = {name: {'status': 'accepted'} for name in required_stages.REQUIRED}
        self.assertEqual(required_stages.problems(stages), [])
        stages['blocks.stage_owned_variants C1 (AGENTEE-485 R2)'] = {
            'status': 'refused', 'error': 'ValueError: stage step block-variants timeout; no output adopted or substituted'}
        self.assertTrue(required_stages.problems(stages))
        del stages['blocks.stage_owned_variants C1 (AGENTEE-485 R2)']
        self.assertTrue(any('missing' in p for p in required_stages.problems(stages)))
        stages = {name: {'status': 'accepted'} for name in required_stages.REQUIRED}
        stages['new.unclassified'] = {'status': 'accepted'}
        self.assertTrue(any('not classified' in p for p in required_stages.problems(stages)))

    def test_receipt_write_and_retain_refuse_a_refused_required_stage(self):
        runtime_receipt = load('runtime_receipt')
        self.assertTrue(runtime_receipt.required_stage_problems(DELIVERED))
        retain = load('retain')
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'pipeline.json').write_text(json.dumps(DELIVERED))
            with self.assertRaises(SystemExit) as raised:
                retain.retain(tmp)
            self.assertIn('required stages refused; not retained', str(raised.exception))

    def test_launch_refuses_the_delivered_receipt(self):
        """The full launch preflight on the real committed 485d receipt refuses before any container (H1 runner, X1)."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'export').mkdir()
            out = subprocess.run(['/usr/bin/python3', '-I', '-B', str(HERE / 'launch.py'), str(RECEIPT_DIR), tmp,
                                  str(Path(tmp) / 'out'), '--preflight'], capture_output=True, text=True)
        self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
        self.assertIn('launch refused', out.stdout)
        self.assertIn("required stage 'placement.scope_locality_binding' is 'refused'", out.stdout)
        self.assertIn("the receipt records the campaign runner cwd '/opt/agent-ee'", out.stdout)


def pipeline_functions(*names):
    """Selected pure helpers of pipeline.py (which runs the preparation on import), compiled from its own source."""
    import ast
    tree = ast.parse((HERE / 'pipeline.py').read_text())
    module = ast.Module([n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names], [])
    scope = {}
    exec(compile(module, str(HERE / 'pipeline.py'), 'exec'), scope)
    return [scope[n] for n in names]


class AdvisoriesAndUnderside(unittest.TestCase):
    def test_f3_exceeded_advisories_are_surfaced_from_the_real_repack(self):
        exceeded_advisories, = pipeline_functions('exceeded_advisories')
        total = 0
        for path in sorted((HERE / 'evidence/repack-8ab3b0b9-485c/cand').glob('*.candidate.json')):
            doc = json.loads(path.read_text())
            found = exceeded_advisories(doc)
            total += len(found)
            self.assertTrue(all(row['at'].startswith('/') for row in found))
        self.assertEqual(total, 67)  # every '"exceeded": true' row of the retained repack candidates
        self.assertEqual(exceeded_advisories({'status': 'pass', 'advisories': [{'kind': 'engineering_target',
                                              'relationship': 'r', 'exceeded': True}]}),
                         [{'at': '/advisories/0', 'kind': 'engineering_target', 'relationship': 'r'}])

    def test_h3_relationship_references_cover_from_and_to(self):
        references, = pipeline_functions('references')
        contract = json.loads((HERE.parent / 'agentee-485-blocks/block-contract-template.json').read_text())
        first = contract['relationships']['obligations'][0]  # per-role legs (supply/return/switch), each from/to
        legs = [v for v in first.values() if isinstance(v, dict) and 'from' in v]
        self.assertTrue(legs)
        self.assertEqual(references(first), {leg[end]['reference'] for leg in legs for end in ('from', 'to')})

    def test_c1_timeout_is_explicit_and_pending(self):
        source = (HERE / 'pipeline.py').read_text()
        self.assertIn('timeout_s=BLOCK_VARIANTS_TIMEOUT_S)', source)
        self.assertIn("BLOCK_VARIANTS_TIMEOUT_S = 600", source)
        self.assertIn("'status': 'PENDING slice B'", source)


class ActiveRetention(unittest.TestCase):
    def test_active_default_is_the_delivered_retention_and_pending_is_explicit(self):
        retain, runtime_receipt = load('retain'), load('runtime_receipt')
        self.assertEqual(retain.DEST.name, 'emission-8ab3b0b9-agentee485')
        self.assertTrue((retain.DEST / 'SHA256SUMS').is_file())
        self.assertEqual(retain.PENDING_DEST.name, 'emission-8ab3b0b9-agentee485c')
        self.assertFalse(retain.PENDING_DEST.exists())
        self.assertEqual(runtime_receipt.EVIDENCE, retain.DEST)


if __name__ == '__main__':
    unittest.main()
