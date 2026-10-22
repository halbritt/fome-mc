"""Probe pod_driver.validate_configuration on a compiled scope (no inference; no producer or KiCad runs).

Plan-side declarations are SYNTHETIC (the agent-ee test fixture's shape: /usr/bin/false steps,
stand-in router checkout with a mocked pin). They exercise the scope-dependent gates only; they are
not a production pod plan. The input tree holds the compiled requirements-map files, the current
microSD schematic/project and an empty native board placeholder written by this probe.
Usage: python3 -I probe_configuration.py AGENT_EE_CHECKOUT COMPILED_DIR NEW_WORK_DIR
"""
import hashlib, json, shutil, sys
from pathlib import Path
from unittest import mock
A, C, Wk = (Path(p) for p in sys.argv[1:4])
sys.path[:0] = [str(A / 'src'), str(A)]
from agent_ee import pod_driver as pod, kicad_route_attempt as attempt
from agent_ee.profiles import validate_profile
from agent_ee.rf_review import ROLE
from tests.kicad_route_fixture import make_checkout, FAKE_PIN
W = Path(__file__).resolve().parents[2] / 'storage-microsd/project'
scope = json.loads((C / 'scope.json').read_text())
Wk.mkdir(parents=True)
inputs = Wk / 'inputs'
shutil.copytree(C / 'requirements-map', inputs / 'requirements-map')
proj = inputs / 'project'; proj.mkdir()
stem = Path(scope['schematic']).stem
shutil.copyfile(W / 'telemetry-pod.kicad_sch', proj / f'{stem}.kicad_sch')
shutil.copyfile(W / 'telemetry-pod.kicad_pro', proj / f'{stem}.kicad_pro')
(proj / f'{stem}.kicad_pcb').write_text('(kicad_pcb (version 20260206) (generator "probe-placeholder"))\n')
for name, body in (('intent.json', {'probe': 'synthetic writer input'}), ('deviations.json', {'probe': 'synthetic'}),
                   ('bindings.json', {'probe': 'synthetic coordinator output'})):
    (inputs / name).write_text(json.dumps(body))
steps = []
for name, stage in pod.STEPS:
    out = 'bindings.json' if name == 'binding-fill' else scope['schematic'] if name == 'emit-schematic' else scope['board']
    steps.append(dict(schema='agent-ee.stage-step/1', step=name, stage=stage, argv=['/usr/bin/false'],
                      writes={out: 'design/' + out}, adoptable_exits=[0], timeout_s=600))
checkout, code = make_checkout(Wk / 'router', 'complete')
profile = scope.get('review_profile')
print('review_profile:', profile and profile['name'], 'roles', [r['role'] for r in profile['reviewers']] if profile else None)
if profile:
    validate_profile(profile)
    print('validate_profile ok; rf role present:', ROLE in [r['role'] for r in profile['reviewers']])
# The plan always carries the existing pod profile, so the scope's own declaration is what differs.
plan_profile = json.loads((A / 'profiles/pod-review.json').read_text())
roles = [r['role'] for r in scope.get('review_profile', {}).get('reviewers', [{'role': 'circuit'}, {'role': 'physical'}])]
from agent_ee.rf_review import gate
print('cli expected_review_roles from scope:', roles, '| rf_review.gate(required):',
      gate({'rf_review': {'required': True}, 'expected_review_roles': roles}))
route = dict(schema='agent-ee.routing-adapter/1', project='project', board=Path(scope['board']).name,
             schematic=Path(scope['schematic']).name, name='pod', label='campaign', checkout=str(checkout), budget=300, timeout=900)
plan = dict(schema=pod.SCHEMA, scope='scope.json', envelope='intent.json', parts='intent.json',
            spec='requirements-map/spec.md', spec_record='requirements-map/spec-record.json',
            writer_inputs={'intent': 'intent.json', 'deviations': 'deviations.json'}, implementation_steps=steps,
            review_profile=plan_profile, implementation=plan_profile['adjudicator'], routing_budget_s=300, review_budget_s=3600, routing_adapter=route)
final = pod._final_scope(scope, plan, inputs)
files = {p.relative_to(inputs).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(inputs.rglob('*')) if p.is_file()}
with mock.patch.object(attempt, 'PIN', FAKE_PIN), mock.patch.object(attempt, 'PINNED_CODE', code):
    try:
        v = pod.validate_configuration(plan, final, files, inputs)
    except (ValueError, KeyError, TypeError) as exc:
        print('validate_configuration REFUSED:', exc)
        sys.exit(1)
print('validate_configuration ACCEPTED: baseline_id', v['baseline_id'], 'stage_policy_id', v['stage_policy_id'],
      'max_iterations', v['max_iterations'], 'max_seconds', v['max_seconds'])
