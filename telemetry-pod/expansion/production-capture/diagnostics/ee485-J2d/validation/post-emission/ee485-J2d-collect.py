"""Retain the single J2d diagnostic's bytes. The saved design/capture are bound by a full sha256 manifest; the
J2c packet already retains byte-identical copies of every file except the listed differences, which are copied."""
from collections import Counter
import hashlib, json, shutil, subprocess
from pathlib import Path
root = Path.cwd()
run = root / 'build/ee485-J2d-run'
pc = root / 'telemetry-pod/expansion/production-capture'
j2c = pc / 'diagnostics/ee485-J2c'
out = pc / 'diagnostics/ee485-J2d'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src, rel):
    dst = out / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
manifest, differs = {}, []
for tree, rel in [(run / 'cap', 'cap'), (run / 'pipe/emission/design', 'pipe/emission/design')]:
    for p in sorted(x for x in tree.rglob('*') if x.is_file()):
        name = rel + '/' + p.relative_to(tree).as_posix()
        manifest[name] = sha(p)
        old = j2c / name
        if not old.is_file() or sha(old) != manifest[name]:
            differs.append(name)
            copy(p, name)
(out / 'design-manifest.json').write_text(json.dumps({
    'scope': 'sha256 of every saved capture/design file of the J2d emission; files equal to the J2c retained copy are '
             'not duplicated', 'same_as_j2c_except': differs, 'files': manifest}, indent=1) + '\n')
copy(run / 'pipe/emission/native.xml', 'pipe/emission/native.xml')
copy(run / 'pipe/pipeline.json', 'pipeline.json')
for src in sorted((run / 'pipe/emission/receipts').glob('*/receipt.json')):
    copy(src, 'receipt-metadata/' + src.parent.name + '/receipt.json')
shutil.copytree(run / 'pipe/access-rebound', out / 'pipe/access-rebound')
shutil.copytree(run / 'j2-verification', out / 'j2-verification')
copy(run / 'native-positions.csv', 'native-positions.csv')
copy(root / 'build/ee485-J2d-verify.json', 'j2-verification/verify_j2-output.json')
check = Path((run / 'native-check-path.txt').read_text().strip().replace('/work/fome-mc', str(root)))
for name in ['summary.json', 'source.json', 'positions-command.json', 'erc/erc.json', 'erc/result.json',
             'erc/kicad-cli-erc.log', 'drc/drc.json', 'drc/result.json', 'drc/kicad-cli-drc.log']:
    copy(check / name, 'native/' + name)
for name in ['probe.log', 'pre-gates.log', 'emission.log', 'post-gates.log', 'ecu-gates.log']:
    copy(root / 'build' / name, 'logs/' + name)
for name in ['ee485-J2d-native.py', 'ee485-J2d-post.mk', 'ee485-J2d-collect.py']:
    copy(root / 'build' / name, 'validation/post-emission/' + name)
pipeline = json.loads((out / 'pipeline.json').read_text())
stages = {n: {'status': r['status'], **({'error': r['error']} if 'error' in r else {})} for n, r in pipeline['stages'].items()}
(out / 'stage-status.json').write_text(json.dumps({'counts': dict(Counter(r['status'] for r in stages.values())),
                                                  'stages': stages}, indent=1) + '\n')
(out / 'STAGES.md').write_text('Actual pipeline.json.stages; pipeline exit 3 (C1 REQUIRED_NOT_RUN only).\n\n'
                               '| Stage | Status |\n|---|---|\n' + ''.join(f'| `{n}` | {r["status"]} |\n' for n, r in stages.items()))
git = lambda rev: subprocess.run(['git', 'rev-parse', rev], check=True, capture_output=True, text=True).stdout.strip()
S = Path('/tmp/agent-ee-burndown-20261017/workers/ee485-J2d/scratch')
source = {'schema': 'agentee485.j2d-diagnostic/1',
          'verdict': 'J2 input/diagnostic closure only; C1 REQUIRED_NOT_RUN; no candidate, receipt or placement acceptance',
          'assigned_base': git('68c29ca28d5565c85f585059335175629823c960'),
          'emission_source': git((S / 'emission-source-head.txt').read_text().strip()),
          'agent_ee': pipeline['agent_ee'],
          'runtime_manifest': 'telemetry-pod/expansion/production-capture/runtime/agentee-485j2c.json',
          'runtime_manifest_sha256': sha(pc / 'runtime/agentee-485j2c.json'),
          'limits': {'class': 'test', 'weight': 1, 'cpus': 3, 'memory': '12g', 'timeout_s': 1800, 'jobs': 1},
          'c1': 'validation-only-c1-not-in-scope', 'pipeline_exit': 3, 'emission_invocations': 1,
          'start': (S / 'emission-start.txt').read_text().strip(), 'stop': (S / 'emission-stop.txt').read_text().strip(),
          'board_sha256': sha(run / 'pipe/emission/design/project/telemetry-pod.kicad_pcb'),
          'access_reservations_sha256': sha(run / 'pipe/access-rebound/reservations.json'),
          'post_emission_files': 'Only validation/post-emission/* (verification and packaging, not pipeline source) '
                                 'were written after the emission; no pipeline/verifier source changed.',
          'worker_model': 'claude-opus-5-5 (Opus 5.5), HIGH; no subagents'}
(out / 'source.json').write_text(json.dumps(source, indent=1) + '\n')
print('retained', out, 'differs', differs)
