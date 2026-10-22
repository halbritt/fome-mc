"""Regression probes for the blocks layer of pipeline.py (review-pod-capture-j5 H1/H2).

They execute pipeline.py's own block_obligations, compose_blocks, production_scope_obligations and
review_obligations (extracted unchanged from its source) on a scratch copy of a repack output. No
agent-ee import is needed: the review packet guard runs against a stub build_packet whose packet is the
nominal one with lines removed or duplicated; the real packet path is the pipeline's own stage.

Every tamper is applied consistently where an attacker could: when the obligation record changes,
repack.json's record hash and obligation lists are rewritten to match, so a refusal comes from the
expected obligation identities and source bytes, not from a stale digest.

Usage (fome-mc root): python3 telemetry-pod/expansion/production-capture/obligation_probes.py [REPACK_DIR]
REPACK_DIR defaults to evidence/repack-a9dac2f-j5.
"""
import ast
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = Path(sys.argv.pop(1)).resolve() if len(sys.argv) > 1 else HERE / 'evidence/repack-a9dac2f-j5'
RECORD = 'composition/block-obligations.json'
FUNCTIONS = ('block_obligations', 'block_obligation_ids', 'block_limitation_problems', 'compose_blocks',
             'production_scope_obligations', 'review_obligations')
BLOCKS = ('pre-6v3', 'buck-3v3')
OBLIGATIONS = [f'{b}-{kind}' for b in BLOCKS for kind in ('board-region-copper-native-check', 'witness-pose-equivalence')]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, doc):
    Path(path).write_text(json.dumps(doc, indent=1, sort_keys=True) + '\n')


def pipeline(repack):
    tree = ast.parse((HERE / 'pipeline.py').read_text())
    tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in FUNCTIONS]
    env = {'REPACK': repack, 'BLOCK_OBLIGATIONS': RECORD, 'sha': sha, 'json': json, 'copy': copy}
    exec(compile(tree, str(HERE / 'pipeline.py'), 'exec'), env)
    return env


def rebind(root):
    """Rewrite repack.json so it names the (tampered) record by hash and lists its obligations."""
    doc, repack = load(root / 'block-obligations.json'), load(root / 'repack.json')
    ids = {b['block']: [o.get('id') for o in b.get('obligations', [])] for b in doc['blocks']}
    for block, listed in ids.items():
        if block in repack['candidates']:
            repack['candidates'][block].update(unresolved_obligations=listed, obligations={
                'path': 'block-obligations.json', 'sha256': sha(root / 'block-obligations.json')})
    repack['unresolved_obligations'] = ids
    dump(root / 'repack.json', repack)


class Probes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'repack'
        shutil.copytree(SOURCE, self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def reset(self):
        self.tearDown()
        self.setUp()

    def refuses(self, why):
        with self.assertRaises(SystemExit, msg=why) as caught:
            pipeline(self.root)['block_obligations']()
        return str(caught.exception)

    def edit_record(self, change, consistent=True):
        doc = load(self.root / 'block-obligations.json')
        change(doc)
        dump(self.root / 'block-obligations.json', doc)
        if consistent:
            rebind(self.root)

    def accepted(self):
        env = pipeline(self.root)
        doc, record = env['block_obligations']()
        env.update(obligation_doc=doc, obligation_record=record)
        env['scope'] = env['compose_blocks']({'limitations': ['UNRELATED'], 'schematic': 's', 'board': 'b'})
        return env

    # Nominal: the expected set is the source's four obligations and reaches the scope exactly once each.
    def test_nominal_accepts_expected_four(self):
        env = self.accepted()
        self.assertEqual(env['block_obligation_ids'](), OBLIGATIONS)
        out = env['production_scope_obligations']()
        self.assertEqual(out['obligations'], 4)
        self.assertEqual(sum('WITNESS-POSE' in l for l in env['scope']['limitations']), 2)

    # H1: each obligation removed individually, both pose obligations, and all of a block.
    def test_each_obligation_removed_refuses(self):
        for gone in OBLIGATIONS:
            with self.subTest(removed=gone):
                self.reset()
                self.edit_record(lambda d: [b.update(obligations=[o for o in b['obligations'] if o['id'] != gone])
                                            for b in d['blocks']])
                self.assertIn(gone, self.refuses(gone))

    def test_both_pose_obligations_removed_refuses(self):
        self.edit_record(lambda d: [b.update(obligations=[o for o in b['obligations'] if 'witness-pose' not in o['id']])
                                    for b in d['blocks']])
        self.assertIn('witness-pose-equivalence', self.refuses('both pose obligations removed'))

    def test_both_pose_obligations_removed_inconsistent_refuses(self):
        self.edit_record(lambda d: [b.update(obligations=[o for o in b['obligations'] if 'witness-pose' not in o['id']])
                                    for b in d['blocks']], consistent=False)
        self.refuses('both pose obligations removed, repack.json untouched')

    def test_empty_duplicate_substituted_extra_refuse(self):
        def empty(d): d['blocks'][0]['obligations'] = []
        def duplicate(d): d['blocks'][0]['obligations'].append(copy.deepcopy(d['blocks'][0]['obligations'][1]))
        def duplicate_for_missing(d): d['blocks'][0]['obligations'][1] = copy.deepcopy(d['blocks'][0]['obligations'][0])
        def substituted(d): d['blocks'][0]['obligations'][1]['id'] = 'pre-6v3-witness-pose-waived'
        def swapped_blocks(d): d['blocks'][0]['obligations'], d['blocks'][1]['obligations'] = (
            d['blocks'][1]['obligations'], d['blocks'][0]['obligations'])
        def extra(d): d['blocks'][0]['obligations'].append({'id': 'pre-6v3-extra', 'status': 'unresolved', 'statement': 'x'})
        for change in (empty, duplicate, duplicate_for_missing, substituted, swapped_blocks, extra):
            with self.subTest(change=change.__name__):
                self.reset()
                self.edit_record(change)
                self.refuses(change.__name__)

    def test_status_and_meaning_refuse(self):
        def resolved(d): d['blocks'][1]['obligations'][1]['status'] = 'resolved'
        def unknown_dropped(d): d['blocks'][0]['qualification'] = 'qualified'
        def block_resolved(d): d['blocks'][0]['status'] = 'resolved'
        def statement(d): d['blocks'][0]['obligations'][1]['statement'] = 'Witness pose equivalent.'
        def reasons(d): d['blocks'][0]['obligations'][0]['source_reasons'] = ['none']
        def reference(d): d['blocks'][0]['reference'] = 'U7'
        def placement(d): d['blocks'][0]['real_placement'] = 'Inherits the seed qualification.'
        def missing_block(d): d['blocks'].pop()
        def duplicate_block(d): d['blocks'].append(copy.deepcopy(d['blocks'][0]))
        def no_blocks(d): d['blocks'] = []
        for change in (resolved, unknown_dropped, block_resolved, statement, reasons, reference, placement,
                       missing_block, duplicate_block, no_blocks):
            with self.subTest(change=change.__name__):
                self.reset()
                self.edit_record(change)
                self.refuses(change.__name__)

    def test_refused_set_is_from_the_retained_refusals(self):
        # repack.json relabels a refused block as library-materialized (and drops it from the record).
        self.edit_record(lambda d: d['blocks'].pop())
        repack = load(self.root / 'repack.json')
        repack['packed']['buck-3v3']['path'] = 'library entry'
        repack['unresolved_obligations'].pop('buck-3v3', None)
        dump(self.root / 'repack.json', repack)
        self.refuses('relabelled refusal')
        (self.root / 'logs/buck-3v3.library.out').unlink()
        self.assertIn('missing', self.refuses('refusal output removed'))

    def test_refusal_log_tamper_refuses(self):
        log = self.root / 'logs/pre-6v3.library.out'
        doc = load(log)
        doc['problems'] = [{'kind': 'other', 'reason': 'changed'}]
        log.write_text(json.dumps(doc))
        self.refuses('refusal log changed')

    # H2: the cited library entry is checked by bytes, against the record and repack.json, at its expected path.
    def test_library_entry_tamper_refuses(self):
        (self.root / 'pre-6v3.v4.entry.json').write_text('{}')
        self.assertIn('pre-6v3.v4.entry.json', self.refuses('entry replaced with {}'))

    def test_library_entry_changed_bytes_refuses(self):
        path = self.root / 'buck-3v3.v4.entry.json'
        path.write_bytes(path.read_bytes() + b'\n')
        self.refuses('entry changed by one byte')

    def test_library_entry_missing_refuses(self):
        (self.root / 'pre-6v3.v4.entry.json').unlink()
        self.assertIn('missing', self.refuses('entry removed'))

    def test_library_entry_files_swapped_refuses(self):
        a, b = self.root / 'pre-6v3.v4.entry.json', self.root / 'buck-3v3.v4.entry.json'
        x, y = a.read_bytes(), b.read_bytes()
        a.write_bytes(y)
        b.write_bytes(x)
        self.refuses('entry files swapped')

    def test_library_entry_records_swapped_refuses(self):
        def swap(d): d['blocks'][0]['library_entry'], d['blocks'][1]['library_entry'] = (
            d['blocks'][1]['library_entry'], d['blocks'][0]['library_entry'])
        self.edit_record(swap)
        self.refuses('record entries swapped')

    def test_library_entry_swapped_with_all_hashes_rewritten_refuses(self):
        # Files swapped and every recorded entry hash (record and repack.json inputs) rewritten to match:
        # only the entry's own identity can refuse, and it must.
        a, b = self.root / 'pre-6v3.v4.entry.json', self.root / 'buck-3v3.v4.entry.json'
        x, y = a.read_bytes(), b.read_bytes()
        a.write_bytes(y)
        b.write_bytes(x)
        def rehash(d):
            for block in d['blocks']:
                block['library_entry']['sha256'] = sha(self.root / block['library_entry']['path'])
        self.edit_record(rehash)
        repack = load(self.root / 'repack.json')
        for block in BLOCKS:
            repack['inputs'][f'{block}.v4.entry.json']['sha256'] = sha(self.root / f'{block}.v4.entry.json')
        dump(self.root / 'repack.json', repack)
        self.assertIn('is not the pod-', self.refuses('swapped and rehashed'))

    def test_library_entry_source_elsewhere_refuses(self):
        self.edit_record(lambda d: d['blocks'][0]['library_entry'].update(source='/elsewhere/lib/pre-6v3.v4.entry.json'))
        self.refuses('entry source relocated')

    def test_candidate_and_seed_bindings_refuse(self):
        def board(root):
            path = root / 'cand/pre-6v3.candidate.json'
            doc = load(path)
            doc['sources']['board_sha256'] = '0' * 64
            dump(path, doc)
            def rehash(d): d['blocks'][0]['generic_candidate']['sha256'] = sha(path)
            self.edit_record(rehash)
            repack = load(root / 'repack.json')
            repack['candidates']['pre-6v3']['sha256'] = sha(path)
            dump(root / 'repack.json', repack)
        def policy(root):
            repack = load(root / 'repack.json')
            repack['candidates']['buck-3v3']['policy_sha256'] = '0' * 64
            dump(root / 'repack.json', repack)
        def seed(root):
            self.edit_record(lambda d: d.update(seed_board_sha256='0' * 64))
        def candidate_missing(root):
            (root / 'cand/buck-3v3.candidate.json').unlink()
        def candidate_changed(root):
            (root / 'cand/buck-3v3.candidate.json').write_text('{}')
        for change in (board, policy, seed, candidate_missing, candidate_changed):
            with self.subTest(change=change.__name__):
                self.reset()
                change(self.root)
                self.refuses(change.__name__)

    # The production-scope guard counts the expected set in the scope, never the record's own list.
    def test_production_scope_guard(self):
        for case in [*OBLIGATIONS, 'both-pose', 'duplicate', 'unexpected', 'packet-input']:
            with self.subTest(case=case):
                env = self.accepted()
                lines = env['scope']['limitations']
                if case in OBLIGATIONS:
                    lines[:] = [l for l in lines if not l.startswith(f'POD-DERIVED-BLOCK-{case.upper()}:')]
                elif case == 'both-pose':
                    lines[:] = [l for l in lines if 'WITNESS-POSE' not in l]
                elif case == 'duplicate':
                    lines.append(lines[-1])
                elif case == 'unexpected':
                    lines.append('POD-DERIVED-BLOCK-PRE-6V3-WAIVED: NOT CHECKED (unresolved; x)')
                else:
                    env['scope']['packet_inputs'].remove(RECORD)
                with self.assertRaises(ValueError):
                    env['production_scope_obligations']()

    def test_compose_blocks_uses_expected_set(self):
        # Even if the verified record object were altered after verification, composition follows the expected set.
        env = self.accepted()
        env['obligation_doc']['blocks'][0]['obligations'].pop()
        with self.assertRaises(ValueError):
            env['compose_blocks']({'limitations': [], 'schematic': 's', 'board': 'b'})

    # The candidate and actual-packet guard, on a stub dry run whose packet loses or repeats one line.
    def review(self, change_packet=None, change_candidate=None):
        env = self.accepted()
        out, planning = Path(self.tmp.name) / 'out', Path(self.tmp.name) / 'planning'
        run, probe = out / 'prepared-probe-scope/dry-run', planning / 'probe'
        for path in (run / 'inputs/composition', probe, planning / 'composition'):
            path.mkdir(parents=True, exist_ok=True)
        for target in (run / 'inputs' / RECORD, planning / RECORD):
            shutil.copyfile(self.root / 'block-obligations.json', target)
        dump(run / 'inputs/composition/binding-ledger.json', {'qualification': {f'R{i}': {} for i in range(174)}})
        scope = {**env['scope'], 'limitations': [*env['scope']['limitations'], 'copper_unknown']}
        dump(probe / 'scope.json', scope)
        dump(out / 'prepared-probe-scope/scope.json', scope)
        candidate = {'scope_sha256': sha(out / 'prepared-probe-scope/scope.json'), 'scope': copy.deepcopy(scope)}
        packet = {'declared_limitations': list(scope['limitations']), 'artifacts': [{'path': 'inputs/' + RECORD}],
                  'citation_files': [{'path': 'inputs/' + RECORD}, {'path': 'inputs/composition/binding-ledger.json'}]}
        (change_packet or (lambda p: None))(packet['declared_limitations'])
        (change_candidate or (lambda p: None))(candidate['scope']['limitations'])
        dump(run / 'candidate.json', candidate)
        dump(run / 'result.json', {'checks': [], 'run_id': 'probe'})
        stub = types.ModuleType('agent_ee.reviewers')
        stub.build_packet = lambda *_: packet
        sys.modules.update({'agent_ee': types.ModuleType('agent_ee'), 'agent_ee.reviewers': stub})
        env.update(OUT=out, planning=planning, probe=probe, inputs={'ledger': 'composition/binding-ledger.json'})
        try:
            return env['review_obligations']()
        finally:
            sys.modules.pop('agent_ee.reviewers')
            sys.modules.pop('agent_ee')

    def test_review_packet_guard(self):
        self.assertEqual(self.review()['packet_obligation_limitations'], 4)
        drop = lambda ids: (lambda lines: lines.__setitem__(slice(None), [
            l for l in lines if not any(l.startswith(f'POD-DERIVED-BLOCK-{i.upper()}:') for i in ids)]))
        cases = {**{f'packet-{i}': {'change_packet': drop([i])} for i in OBLIGATIONS},
                 'packet-both-pose': {'change_packet': drop([i for i in OBLIGATIONS if 'pose' in i])},
                 'packet-duplicate': {'change_packet': lambda lines: lines.append(
                     next(l for l in lines if 'WITNESS-POSE' in l))},
                 **{f'candidate-{i}': {'change_candidate': drop([i])} for i in OBLIGATIONS},
                 'candidate-both-pose': {'change_candidate': drop([i for i in OBLIGATIONS if 'pose' in i])}}
        for name, change in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(ValueError):
                    self.review(**change)


if __name__ == '__main__':
    unittest.main(verbosity=2)
