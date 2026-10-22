"""Repack the 18 iter8n placement blocks with the released AGENTEE-439 engine and the derived
request policy (composition/placement-policy.json), after the production dry run prepared.

The iter8n seed board, its native netlist, allocation and the two library block entries are the
only full-footprint inputs that exist before a campaign's schematic stage, so every candidate binds
that seed board's hash. This is preparation evidence for the bounded first placement run, not a
placement: nothing is written to a design, and no campaign runs.

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
summary = {
    'schema': 'pod-capture.block-repack/1', 'agent_ee': str(A),
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
        'Packing is geometry under the policy; it is not electrical, DRC or mechanical acceptance.']}
(OUT / 'repack.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
print(json.dumps({k: summary[k] for k in ('blocks', 'all_packed')} |
                 {'failed': sorted(b for b, r in packed.items() if r['rc'] != 0)}))
