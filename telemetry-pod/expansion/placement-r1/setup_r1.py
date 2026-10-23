"""placement-r1 setup, INSIDE the qualified runtime container (no provider call; no design file re-saved).
1. materialize the retained emitted candidate tree (evidence/emission-7d5b0d4d/MANIFEST.json `design`, 559 files) from
   the git archive of fome-mc 881f6fc5 into /work/inputs, verifying every sha256;
2. confirm identity({scope, files}) == the emission's candidate_id and the board/project are the assigned input bytes;
3. bind the campaign's own placement declaration with agent-ee 1b0637c7 placement_adapter.binding (envelopes, locality,
   edge margin) and write the exact stage step (prepare_step: tool snapshot, request, argv, mounts, timeout_s);
4. native 'before' diagnostics on a scratch copy: kicad-cli pcb drc --severity-all --schematic-parity.
Usage: setup_r1.py REPO_ARCHIVE WORK
"""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
# Attempt 1 used agent-ee 1b0637c7 at /ae/src (the default); attempt 1b sets AE_SRC=/opt/agent-ee/src (the image's 7d5b0d4d).
sys.path.insert(0, os.environ.get('AE_SRC', '/ae/src'))
from agent_ee import placement_adapter as pa
from agent_ee.storage import identity
repo, work = Path(sys.argv[1]), Path(sys.argv[2])
E = repo / 'telemetry-pod/expansion/production-capture/evidence/emission-7d5b0d4d'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
manifest = json.loads((E / 'MANIFEST.json').read_text())
inputs = work / 'inputs'
files = {}
for rel, item in sorted(manifest['design'].items()):
    src = E / item['retained'] if item['retained'] != 'repository path' else repo / rel
    dst = inputs / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    assert sha(dst) == item['sha256'], rel
    files[rel] = item['sha256']
scope = json.loads((E / 'prepared/scope.json').read_text())
override = os.environ.get('POLICY_OVERRIDE')  # attempt 1c: the repaired derived policy (placement-r1/repair/)
if override:
    rel = 'composition/placement-policy.json'
    shutil.copyfile(override, inputs / rel)
    files[rel] = sha(inputs / rel)
cand = {'scope': scope, 'files': files, 'candidate_id': identity({'scope': scope, 'files': files})}
import agent_ee
report = {'policy_override': override, 'policy_sha256': files['composition/placement-policy.json'], 'agent_ee_source': os.path.dirname(agent_ee.__file__), 'materialized_files': len(files), 'candidate_id': cand['candidate_id'],
          'emission_candidate_id': manifest['emission']['candidate_id'],
          'board_sha256': files[scope['board']], 'project_sha256': files['project/telemetry-pod.kicad_pro'],
          'schematic_sha256': files[scope['schematic']]}
assert report['board_sha256'] == '2f1c955704ab1fb38217c24cbaf5a45f4219a74a6a2309be710452c54db3b673'
assert report['project_sha256'] == '10002b987995765415313fa89da32ba9011160853596f1a78ff8fba24ac9b175'
config = json.loads((E / 'prepared/campaign.json').read_text())
declaration = config['placement_adapter']
mutable = {scope['board'], scope['schematic'], *config.get('writer_editable', []),
           *(w for s in config.get('implementation_steps', []) for w in s.get('writes', {}))}
record, bound, policy, protected, protected_refs = pa.binding(declaration, cand, inputs, mutable)
step_dir = work / 'step'
spec, request = pa.prepare_step(step_dir, (inputs / bound['board']).read_bytes(), policy, bound, protected_refs)
(work / 'step.json').write_text(json.dumps(spec, indent=1, sort_keys=True) + '\n')
(work / 'binding.json').write_text(json.dumps({'record': record, 'bound': bound, 'protected': protected,
                                               'protected_refs': protected_refs}, indent=1, sort_keys=True, default=str) + '\n')
report.update(identity_matches_emission=cand['candidate_id'] == report['emission_candidate_id'],
              declaration=declaration, protected_refs=protected_refs, policy_fixed_refs=sorted(policy['fixed_refs']),
              min_courtyard_edge_mm=policy.get('min_courtyard_edge_mm'), envelopes=[e.get('path') for e in record['envelopes']],
              electrical_locality=record.get('electrical_locality'), fixed_overhangs=policy.get('fixed_overhangs'),
              constraint_provenance_keys=sorted(policy.get('constraint_provenance', {})), step_argv=spec['argv'],
              step_timeout_s=spec['timeout_s'], request_sha256=sha(step_dir / 'request/request.json'))
before = work / 'before'
shutil.copytree(inputs, before)  # the whole candidate tree, so library paths resolve as in the sandbox
drc = subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity',
                      '-o', str(work / 'drc-before.json'), str(before / 'project/telemetry-pod.kicad_pcb')], capture_output=True, text=True)
report['drc_before_exit'] = drc.returncode
(work / 'setup.json').write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + '\n')
print(json.dumps({k: report[k] for k in ('materialized_files', 'candidate_id', 'identity_matches_emission', 'protected_refs',
                                         'min_courtyard_edge_mm', 'envelopes', 'step_timeout_s', 'drc_before_exit')}, default=str))
