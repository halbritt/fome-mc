"""Repack the 18 iter8n placement blocks with the released AGENTEE-439 engine and the derived
request policy (composition/placement-policy.json), after the production dry run prepared.

The iter8n seed board, its native netlist, allocation and the two library block entries are the
only full-footprint inputs that exist before a campaign's schematic stage, so every candidate binds
that seed board's hash. This is preparation evidence for the bounded first placement run, not a
placement: nothing is written to a design, and no campaign runs.

When the released library engine refuses a library block entry (pre-6v3, buck-3v3: copper_unknown), the
block is packed by the generic packer, which is geometry only. The refusal does not disappear: each such
block gets a source-bound record in block-obligations.json (the library entry, the complete refusal
output and the generic candidate, by hash) whose board-region copper/native-check and witness-pose
obligations stay unresolved. pipeline.py carries that file into the scope limitations and the review
packet inputs. A real placement repacks against its own emitted board and inherits neither the iter8n
seed identity nor any qualification from these candidates.

Usage (fome-mc root, system python with pcbnew):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/repack.py AGENT_EE_EXPORT ITER8N_DIR NEW_OUT_DIR
"""
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

A, ITER8N, OUT = (Path(p).resolve() for p in sys.argv[1:4])
HERE = Path(__file__).resolve().parent
POLICY = HERE / 'composition/placement-policy.json'
LIBRARY = {'pre-6v3': 'U5', 'buck-3v3': 'U7'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args, log):
    started = time.monotonic()
    done = subprocess.run(['/usr/bin/python3', '-B', '-m', *args], cwd=A, capture_output=True, text=True,
                          env={'PYTHONPATH': str(A / 'src'), 'PATH': '/usr/bin:/bin', 'HOME': str(OUT)})
    (OUT / 'logs' / (log + '.out')).write_text(done.stdout)
    (OUT / 'logs' / (log + '.err')).write_text(done.stderr)
    return {'rc': done.returncode, 'seconds': round(time.monotonic() - started, 1),
            'stdout': done.stdout.strip()[-300:], 'stderr': done.stderr.strip()[-300:]}


OUT.mkdir(parents=True)
(OUT / 'logs').mkdir()
(OUT / 'cand').mkdir()
inputs = {name: OUT / name for name in ('seed.kicad_pcb', 'native.xml', 'allocation.json')}
for name, path in inputs.items():
    shutil.copyfile(ITER8N / name, path)
shutil.copyfile(POLICY, OUT / 'policy.json')
for block in LIBRARY:
    shutil.copyfile(ITER8N / f'lib/{block}.v4.entry.json', OUT / f'{block}.v4.entry.json')
steps = {'probe': run('agent_ee.placement_probe', '--out', str(OUT / 'probe.json'), str(inputs['seed.kicad_pcb']),
                      log='probe')}
common = ['--probe', str(OUT / 'probe.json'), '--netlist', str(inputs['native.xml']),
          '--allocation', str(inputs['allocation.json']), '--policy', str(OUT / 'policy.json')]
steps['derive'] = run('agent_ee.blocks', 'derive', *common[:4], '--allocation', str(inputs['allocation.json']),
                      '--out', str(OUT / 'derived.json'), log='derive')
derived = json.loads((OUT / 'derived.json').read_text())
blocks = [b['id'] for b in derived['blocks']]


def pack(block):
    out = OUT / 'cand' / f'{block}.candidate.json'
    if block in LIBRARY:
        library = run('agent_ee.block_library', 'materialize', '--entry', str(OUT / f'{block}.v4.entry.json'),
                      *common, '--block', block, '--out', str(out), log=block + '.library')
        if library['rc'] == 0:
            return block, {**library, 'path': 'library entry'}
        # The released engine refuses the iteration-5 board-region entry (its refusal is kept); the
        # block is packed by the same generic packer as the other blocks instead (README decision).
        generic = run('agent_ee.blocks', 'pack', *common, '--block', block, '--out', str(out), log=block)
        return block, {**generic, 'path': 'generic pack after library refusal', 'library': library}
    return block, {**run('agent_ee.blocks', 'pack', *common, '--block', block, '--out', str(out), log=block),
                   'path': 'generic pack'}


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    packed = dict(pool.map(pack, blocks))
candidates = {}
for block in blocks:
    path = OUT / 'cand' / f'{block}.candidate.json'
    if path.exists():
        doc = json.loads(path.read_text())
        candidates[block] = {'sha256': sha(path), 'status': doc.get('status'), 'members': len(doc.get('members', [])),
                             'path': packed[block]['path'],
                             'policy_sha256': doc['sources'].get('policy_sha256'),
                             'board_sha256': doc['sources'].get('board_sha256')}


def library_refusal(block):
    """The complete library refusal (its retained stdout), never the 300-character summary tail."""
    out = OUT / 'logs' / (block + '.library.out')
    try:
        doc = json.loads(out.read_text())
    except ValueError:
        doc = None
    problems = doc.get('problems') if isinstance(doc, dict) and isinstance(doc.get('problems'), list) else None
    return {'log': out.relative_to(OUT).as_posix(), 'sha256': sha(out), 'rc': packed[block]['library']['rc'],
            'status': doc.get('status') if isinstance(doc, dict) else None,
            'problems': problems if problems is not None else [{'kind': 'unparsed', 'reason': 'library refusal output '
                                                                'is not a JSON refusal record; nothing is resolved'}]}


obligations = []
for block, reference in LIBRARY.items():
    if packed.get(block, {}).get('path') != 'generic pack after library refusal':
        continue
    refusal = library_refusal(block)
    candidate = OUT / 'cand' / f'{block}.candidate.json'
    kinds = sorted({p.get('kind') for p in refusal['problems']})
    reasons = [p.get('reason') for p in refusal['problems']]
    obligations.append({
        'block': block, 'reference': reference, 'status': 'unresolved', 'qualification': 'unknown',
        'library_entry': {'path': f'{block}.v4.entry.json', 'sha256': sha(OUT / f'{block}.v4.entry.json'),
                          'source': str(ITER8N / f'lib/{block}.v4.entry.json')},
        'library_refusal': refusal,
        'generic_candidate': {'path': candidate.relative_to(OUT).as_posix(),
                              'sha256': sha(candidate) if candidate.exists() else None,
                              'status': json.loads(candidate.read_text()).get('status') if candidate.exists() else None,
                              'evidence': 'geometry only under the derived request policy',
                              'board_sha256': sha(inputs['seed.kicad_pcb'])},
        'obligations': [
            {'id': f'{block}-board-region-copper-native-check', 'status': 'unresolved', 'refusal_kinds': kinds,
             'statement': (f'The {block} library entry ({reference}) was refused by the released engine: '
                           + '; '.join(f'{p.get("kind")}: {p.get("reason")}' for p in refusal['problems'])
                           + '. Its board-region copper application and the native checks over it are not '
                             'executed; the generic candidate is geometry only and closes neither.'),
             'source_reasons': reasons},
            {'id': f'{block}-witness-pose-equivalence', 'status': 'unresolved',
             'statement': (f'Witness-pose equivalence between the generic {block} candidate and the library '
                           'entry witness is not established; the generic pose is not the library pose.')}],
        'real_placement': ('A real placement repacks this block against its own emitted board; it inherits neither '
                           'the iter8n seed board identity nor any qualification from this candidate.')})
(OUT / 'block-obligations.json').write_text(json.dumps({
    'schema': 'pod-capture.block-obligations/1', 'agent_ee': str(A),
    'seed_board_sha256': sha(inputs['seed.kicad_pcb']), 'blocks': obligations}, indent=1, sort_keys=True) + '\n')
unresolved = {o['block']: [x['id'] for x in o['obligations']] for o in obligations}
for block, ids in unresolved.items():
    if block in candidates:
        candidates[block].update(unresolved_obligations=ids, qualification='unknown',
                                 obligations={'path': 'block-obligations.json',
                                              'sha256': sha(OUT / 'block-obligations.json')})
summary = {
    'schema': 'pod-capture.block-repack/2', 'agent_ee': str(A),
    'authority': 'Block packing on the iter8n seed with the derived request policy; preparation only, no placement.',
    'inputs': {name: {'source': str(ITER8N / name), 'sha256': sha(path)} for name, path in inputs.items()} |
              {'policy': {'source': str(POLICY), 'sha256': sha(POLICY)},
               **{f'{b}.v4.entry.json': {'sha256': sha(OUT / f'{b}.v4.entry.json')} for b in LIBRARY}},
    'steps': steps, 'blocks': len(blocks), 'packed': packed,
    'iter8n_policy_sha256': sorted({json.loads(p.read_text())['sources'].get('policy_sha256')
                                    for p in (ITER8N / 'cand').glob('*.candidate.json')}),
    'candidates': candidates, 'all_packed': len(candidates) == len(blocks) and all(
        r['rc'] == 0 for r in packed.values()),
    'limitations': [
        'Every candidate binds the iter8n seed board; the campaign placement step needs candidates bound to its own '
        'placement source board, so they are repacked there in the bounded first run (agent-509 go required).',
        'Packing is geometry under the policy; it is not electrical, DRC or mechanical acceptance.',
        'all_packed counts geometry candidates only. Blocks in unresolved_obligations had their library entry '
        'refused; their copper/native-check and witness-pose obligations stay unresolved (block-obligations.json).'],
    'unresolved_obligations': unresolved, 'qualified': False}
(OUT / 'repack.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
print(json.dumps({k: summary[k] for k in ('blocks', 'all_packed')} |
                 {'failed': sorted(b for b, r in packed.items() if r['rc'] != 0), 'unresolved': sorted(unresolved)}))
