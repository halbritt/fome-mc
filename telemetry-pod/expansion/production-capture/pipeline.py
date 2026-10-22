"""Phase B on the production capture: binding-fill, scaffold, envelope content, emitter and
annotation declarations, the composed production scope, the derived request policy and the
real pod_driver dry run.

Every stage runs the owned agent-ee producer on a fresh copy of the capture root; a refusal is
kept verbatim and never substituted. The production scope is composed here from the compiled
Rev-3 scope: a scope envelope declaration over composition/envelope.json with one check per
derived envelope obligation (connector-edge/1 for each fixed footprint, outline-containment/1
carrying the declared overhangs to the packer) and the electrical-locality/1 check over the
captured pad obligations the packing policy embeds. The producers' own obligation coverage and
validate_configuration grade that composition. One clearly labelled DIAGNOSTIC runs on a scratch
copy only (it is never an input): the J3 back-side transform. No placement, routing, campaign or
model runs here.

Usage (fome-mc root, system python with pcbnew):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/pipeline.py \
      AGENT_EE_EXPORT ROUTER_CHECKOUT SCOPE_DIR CAPTURE_ROOT NEW_OUT_DIR
SCOPE_DIR is a compiled Rev-3 scope directory (scope.json plus requirements-map/). Set
AGENT_EE_TOOL_SOURCE_CACHE to an absolute directory you own.
"""
import copy
import hashlib
import json
import shutil
import sys
import traceback
from pathlib import Path

A, R, SCOPE_DIR, CAPTURE, OUT = (Path(p).resolve() for p in sys.argv[1:6])
sys.path[:0] = [str(A / 'src')]
from agent_ee import (add_planes, binding_fill, board_envelope, placement_adapter, pod_driver,  # noqa: E402
                      routing_adapter, scaffold, schematic_stage)
from agent_ee.storage import identity  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
X = ROOT / 'telemetry-pod/expansion'
COMPOSED = HERE / 'composition'
ITER7_CAMPAIGN = X / 'routing-diagnostic/iteration-7/campaign.json'
ITER8N = Path('/home/halbritt/.cache/agent449-pod/iter8n')
BOARD, SCHEMATIC = 'project/telemetry-pod.kicad_pcb', 'project/telemetry-pod.kicad_sch'
LOCALITY = 'telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json'
PROFILE = 'sources/fab-profile.json'
CONSTRAINTS = 'telemetry-pod/expansion/design-rules/constraints.json'
CONTAINMENT_LOCATOR = 'D-PCB-13 microSD card envelope in the J3 courtyard (2026-10-21)'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return json.dumps(value, indent=1, sort_keys=True) + '\n'


stages = {}


def stage(name, fn):
    try:
        value = fn()
        stages[name] = {'status': 'accepted', **({'detail': value} if value is not None else {})}
    except Exception as exc:  # retained verbatim, never converted into a pass
        stages[name] = {'status': 'refused', 'error': f'{type(exc).__name__}: {exc}',
                        'where': traceback.extract_tb(exc.__traceback__)[-1].name}
    print(f"{stages[name]['status']:9} {name}" + (f": {stages[name]['error'][:400]}" if 'error' in stages[name] else ''),
          flush=True)


OUT.mkdir(parents=True)
planning = OUT / 'planning'
shutil.copytree(CAPTURE, planning, symlinks=False)
(planning / 'reconstruction.json').unlink()
shutil.copyfile(X / 'design-rules/planes.json', planning / 'composition/planes.json')
shutil.copyfile(COMPOSED / 'placement-policy.json', planning / 'composition/placement-policy.json')
project = planning / 'project'
project.mkdir()
shutil.copyfile(X / 'design-rules/board-setup.kicad_pro', project / 'telemetry-pod.kicad_pro')
shutil.copyfile(X / 'design-rules/telemetry-pod.kicad_dru', project / 'telemetry-pod.kicad_dru')
shutil.copytree(SCOPE_DIR / 'requirements-map', planning / 'requirements-map')
compiled = json.loads((SCOPE_DIR / 'scope.json').read_text())
writer, bound = 'composition/intent.writer.json', 'composition/intent.bound.json'
inputs = {k: 'composition/' + v for k, v in (
    ('parts', 'parts.json'), ('refs', 'part-refs.json'), ('deviations', 'deviations.json'),
    ('envelope', 'envelope.json'), ('layout', 'emitter-layout.json'), ('footprints', 'footprints.json'),
    ('antenna', 'antenna-facts.json'), ('retention', 'captured-rule-areas.json'), ('planes', 'planes.json'),
    ('policy', 'placement-policy.json'), ('ratings', 'rating-sources.json'), ('facts', 'rating-facts.json'),
    ('selection', 'datasheet-source-selection.json'), ('ledger', 'binding-ledger.json'))}
read = lambda rel: json.loads((planning / rel).read_text())  # noqa: E731
facts = read(inputs['facts'])['facts']
rating_dependencies = sorted({inputs['facts'], inputs['selection'], *(f['source']['path'] for f in facts)})


# 0. The production scope: compiled Rev-3 scope + envelope declaration, obligation checks and locality.
def compose_scope(base):
    """Add the scope envelope, one check per derived obligation, overhang containment and locality."""
    files = {p.relative_to(planning).as_posix(): sha(p) for p in planning.rglob('*') if p.is_file()}
    record = board_envelope.validate((planning / inputs['envelope']).read_bytes(),
                                     profile=(planning / PROFILE).read_bytes(), captured=(files, planning))
    derived = board_envelope.derive_requirements(record, inputs['envelope'])
    env, drc = inputs['envelope'], 'placement-drc'
    placement, routing, requirements, unmapped = [], [], [], []
    for item in derived['requirements']:
        field, suffix = board_envelope.field_of(item), item['id'].split(record['envelope_id'] + '-', 1)[1]
        cid = 'envelope-' + suffix.lower()  # scope check IDs are lowercase
        if field == 'outline':
            specs = [dict(id=cid, kind='board_envelope', stage='placement', params=dict(criterion='outline/1', envelope=env))]
        elif field == 'layer_count':
            specs = [dict(id=cid, kind='board_envelope', stage='placement', params=dict(criterion='layers/1', envelope=env))]
        elif field == 'stackup':
            specs = [dict(id=cid, kind='board_envelope', stage='placement', params=dict(criterion='stackup/1', envelope=env))]
        elif field == 'fab_profile':
            specs = [dict(id=cid, kind='fab_profile', stage='routing', params=dict(fab_profile=PROFILE))]
        elif field == 'mounting_holes':
            hole = record['mounting_holes'][int(item['source']['locator'].rsplit('/', 1)[1])]['id']
            specs = [dict(id=cid, kind='board_envelope', stage='placement',
                          params=dict(criterion='mounting-holes/1', envelope=env, id=hole))]
        elif field == 'keepouts':
            keepout = record['keepouts'][int(item['source']['locator'].rsplit('/', 1)[1])]['id']
            specs = [dict(id=cid, kind='board_envelope', stage='placement',
                          params=dict(criterion='keepouts/1', envelope=env, id=keepout))]
        elif field == 'fixed_footprints':
            reference = record['fixed_footprints'][int(item['source']['locator'].rsplit('/', 1)[1])]['reference']
            specs = [dict(id=cid, kind='placement', stage='placement',
                          params=dict(criterion='connector-edge/1', envelope=env, reference=reference, drc_check=drc))]
        else:  # no registered criterion binds this field; it stays visible as unmapped
            unmapped.append({'id': item['id'], 'field': field, 'reason': board_envelope.UNBOUND[field]})
            continue
        for spec in specs:
            (routing if spec['stage'] == 'routing' else placement).append(spec)
        requirements.append({k: item[k] for k in ('id', 'statement', 'source', 'intent')} |
                            {'checks': [s['id'] for s in specs]})
    # Courtyard containment with the envelope's declared overhangs; every requirement citing the
    # envelope must be one of its derived obligations, so this one cites the overhang decisions.
    placement.append(dict(id='envelope-containment', kind='placement', stage='placement',
                          params=dict(criterion='outline-containment/1', envelope=env, drc_check=drc)))
    requirements.append({'id': 'POD-DERIVED-OVERHANG-CONTAINMENT', 'intent': 'acceptance',
                         'statement': ('Every footprint courtyard lies inside the board outline except within the '
                                       f'courtyard_overhangs {env} declares for its fixed footprints (J3 card lane '
                                       'D-PCB-13 v3, U1 antenna D-PCB-16).'),
                         'source': {'path': CONSTRAINTS, 'locator': CONTAINMENT_LOCATOR}, 'checks': ['envelope-containment']})
    placement.append(dict(id='electrical-locality', kind='placement', stage='placement',
                          params=dict(criterion='electrical-locality/1', locality=LOCALITY, drc_check=drc)))
    requirements.append({'id': 'POD-DERIVED-ELECTRICAL-LOCALITY', 'intent': 'acceptance',
                         'statement': ('Every declared pad-centre electrical locality obligation of '
                                       f'{LOCALITY} holds on the placed board (bounds advisory per its README).'),
                         'source': {'path': LOCALITY, 'locator': '/obligations'}, 'checks': ['electrical-locality']})
    checks = list(base['checks'])
    at = max(i for i, c in enumerate(checks) if c['stage'] == 'placement') + 1
    checks[at:at] = placement
    at = max(i for i, c in enumerate(checks) if c['stage'] == 'routing') + 1
    checks[at:at] = routing
    if 'intent' not in base['baseline']['requirements'][0]:
        requirements = [{k: v for k, v in r.items() if k != 'intent'} for r in requirements]
    composed = copy.deepcopy(base)
    composed['envelope'] = {'path': env, 'profile': PROFILE, 'dialog': None}
    composed['checks'] = checks
    composed['baseline']['requirements'] = [*base['baseline']['requirements'], *requirements]
    composed['limitations'] = [*base['limitations'],
        'Composed by production-capture/pipeline.py: the scope envelope, one check per derived envelope '
        'obligation and the electrical-locality check. Structural envelope validity is not mechanical '
        'qualification; obligations no registered criterion binds stay unmapped and visible.']
    derivation = {'schema': 'pod-capture.scope-composition/1',
                  'base': {'path': str(SCOPE_DIR / 'scope.json'), 'sha256': sha(SCOPE_DIR / 'scope.json')},
                  'envelope': {'path': env, 'sha256': files[env], 'envelope_id': record['envelope_id'],
                               'complete': derived['complete'], 'unresolved': derived['unresolved']},
                  'added_checks': [c['id'] for c in placement + routing],
                  'added_requirements': [r['id'] for r in requirements], 'unmapped': unmapped}
    return composed, derivation, (derived, record, files)


def write_scope(root, base):
    scope_ = {**base, 'inputs': [{'path': p.name, 'at': p.name} for p in sorted(root.iterdir()) if p.name != 'scope.json']}
    (root / 'scope.json').write_text(text(scope_))
    return scope_


composed, derivation, coverage_inputs = compose_scope(compiled)
(planning / 'composition/scope-composition.json').write_text(text(derivation))
scope = write_scope(planning, composed)


def obligations():
    derived, record, _ = coverage_inputs
    files = {p.relative_to(planning).as_posix(): sha(p) for p in planning.rglob('*') if p.is_file()}
    report = board_envelope.obligation_coverage(scope, derived, record, files)
    summary = {s: sorted(r['id'].split(record['envelope_id'] + '-', 1)[1] for r in report if r['status'] == s)
               for s in sorted({r['status'] for r in report})}
    reasons = {r['id'].split(record['envelope_id'] + '-', 1)[1]: r['reason'] for r in report if r['status'] not in ('bound',)}
    if any(r['status'] not in ('bound', 'soft') for r in report) or not derived['complete']:
        raise ValueError(f'envelope obligations not all bound: {json.dumps(summary)}; reasons {json.dumps(reasons)}; '
                         f"complete={derived['complete']} unresolved={derived['unresolved']}")
    return summary
stage('scope.envelope_obligation_coverage', obligations)


def envelope_reaches_placer():
    files = {p.relative_to(planning).as_posix(): sha(p) for p in planning.rglob('*') if p.is_file()}
    found = placement_adapter.envelope_fixed({'scope': scope, 'files': files}, planning, [])
    return [{k: e.get(k) for k in ('path', 'envelope_id', 'references')} |
            {'overhangs': [o['reference'] for o in e.get('overhangs', [])],
             'provenance_fixed': sorted(e.get('provenance', {}).get('fixed', {}))} for e in found]
stage('placement.scope_envelope_binding', envelope_reaches_placer)


def locality_reaches_placer():
    files = {p.relative_to(planning).as_posix(): sha(p) for p in planning.rglob('*') if p.is_file()}
    policy_ = read(inputs['policy'])
    source = placement_adapter.bind_locality(policy_, {'scope': scope, 'files': files}, planning, [])
    return {'binding': source, 'obligations': len(policy_['electrical_locality']['obligations'])}
stage('placement.scope_locality_binding', locality_reaches_placer)

# 1. Binding-fill: a distinct produced bound projection from the writer intent, with ratings.
steps = {}
stage('binding_fill.configuration', lambda: steps.update(fill=binding_fill.configuration(
    A, intent=writer, manifest=inputs['parts'], part_refs=inputs['refs'], deviations=inputs['deviations'],
    captures='.', dependencies=rating_dependencies, output=bound, ratings=inputs['ratings'],
    source_migration=True)) or {'writes': steps['fill']['writes'], 'argv_ratings': '--ratings' in steps['fill']['argv']})


def run_fill():
    output, report = binding_fill.fill(planning, read(writer), read(inputs['parts']), read(inputs['refs']),
                                       read(inputs['deviations']), captures='.', ratings=read(inputs['ratings']),
                                       source_migration=True)
    ledger = read(inputs['ledger'])
    missing = sorted(c for c in ledger['qualification'] if not any(x['id'] == c for x in output['components']))
    if missing:
        raise ValueError('ledger names components absent from the bound intent: ' + ', '.join(missing))
    return {'components': len(report['components']), 'ratings_derived': len(report['ratings']['derived']),
            'ratings_missing': report['ratings']['missing'], 'probe_migrations': len(report['probe_migrations']),
            'output_identity': identity(output), 'ledger_qualification': len(ledger['qualification'])}
stage('binding_fill.fill', run_fill)

# 2. Scaffold (stage one, the driver's own call) and envelope content on its output.
content_kwargs = dict(intent_rel=writer, layout_rel=inputs['layout'], antenna_facts_rel=inputs['antenna'],
                      captured_rule_areas_rel=inputs['retention'])


def run_scaffold(root, out):
    return {k: v for k, v in scaffold.scaffold(root / inputs['envelope'], root / inputs['parts'], out,
                                               scope_path=root / 'scope.json').items()
            if k in ('status', 'candidate_id', 'baseline_id')}


def production_content(scaffold_out, work):
    if not scaffold_out.exists():
        raise ValueError('scaffold not available')
    shutil.copytree(scaffold_out / 'inputs', work)
    scaffold.write_envelope_content(work, inputs['envelope'], inputs['parts'], BOARD, **content_kwargs)
    import pcbnew
    board = pcbnew.LoadBoard(str(work / BOARD))
    return {'board_sha256': sha(work / BOARD), 'footprints': len(board.GetFootprints()),
            'fixed': sorted(f.GetReference() for f in board.GetFootprints()
                            if f.GetReference() in {'J1', 'J2', 'J3', 'U1', 'U2', 'H1', 'H2', 'H3', 'H4'})}
stage('scaffold.scaffold composed scope', lambda: run_scaffold(planning, OUT / 'scaffold'))
stage('scaffold.write_envelope_content composed scope', lambda: production_content(OUT / 'scaffold', OUT / 'content'))
stage('scaffold.content_step', lambda: steps.update(content=scaffold.content_step(
    A, inputs['envelope'], inputs['parts'], BOARD, intent=writer, layout=inputs['layout'],
    antenna_facts=inputs['antenna'], captured_rule_areas=inputs['retention'])) or None)

# 3. Emitter, annotation and planes: owned declarations over the bound projection.
stage('schematic_stage.configuration', lambda: steps.update(schematic=schematic_stage.configuration(
    A, board=BOARD, schematic=SCHEMATIC, intent=bound, layout=inputs['layout'], captures='footprints',
    footprints=inputs['footprints'])) or [s['step'] for s in steps['schematic']['implementation_steps']])
stage('add_planes.step', lambda: steps.update(planes=add_planes.step(A, board=BOARD, plan=inputs['planes'])) or None)

# 4. The final derived request policy (captured policy minus caller-authored overhangs).
policy = read(inputs['policy'])
envelope_record = board_envelope.validate((planning / inputs['envelope']).read_bytes())
stage('placement.refuse_policy_sources', lambda: placement_adapter.refuse_policy_sources(policy))
stage('placement.envelope_overhangs', lambda: placement_adapter.envelope_overhangs(envelope_record))


def subjects():
    from agent_ee.placer import _validate_policy
    subject = set(scope['stages']['subjects']['placement']['references'])
    named = set(policy['fixed_refs']) | set(policy['priority_refs']) | {
        r for g in policy['groups'] for r in [*g['references'], g['anchor']['reference']]}
    try:
        _validate_policy(copy.deepcopy(policy), subject)
    except ValueError as exc:
        raise ValueError(f'{exc}; policy references outside the placement subject: {sorted(named - subject)}') from None
stage('placement.policy_vs_subjects', subjects)


def engine_g1():
    return placement_adapter.validate_declaration({
        'schema': 'agent-ee.placement-adapter/1', 'helper': 'agent-ee.placer/1', 'policy': inputs['policy'],
        'fixed_footprints': [], 'timeout_s': 1500,
        'blocks': {'netlist': 'composition/blocks/native.xml', 'arrangement': 'composition/blocks/arrangement.json',
                   'candidates': ['composition/blocks/adc.candidate.json']}}) and 'declaration shape accepted (paths not captured)'
stage('engine.placement_adapter.blocks_request (AGENTEE-439 G1)', engine_g1)

# 5. The plan and the real dry run.
profile = json.loads((A / 'profiles/pod-review.json').read_text())
iter7 = json.loads(ITER7_CAMPAIGN.read_text())
budget = int(iter7['settings']['per_run'][iter7['settings']['per_run'].index('--budget') + 1])
review_budget = sum(r['timeout_s'] for r in profile['reviewers']) + profile['adjudicator']['timeout_s']
adapter = {'schema': 'agent-ee.placement-adapter/1', 'helper': 'agent-ee.placer/1', 'policy': inputs['policy'],
           'fixed_footprints': [], 'timeout_s': 1500}
route = {'schema': 'agent-ee.routing-adapter/1', 'project': 'project', 'board': 'telemetry-pod.kicad_pcb',
         'schematic': 'telemetry-pod.kicad_sch', 'name': 'telemetry-pod', 'label': 'campaign',
         'checkout': str(R), 'budget': budget, 'timeout': 2 * budget + 300}
stage('routing_adapter.preflight', lambda: (lambda p: p['problems'] and (_ for _ in ()).throw(
    ValueError('; '.join(p['problems']))) or {k: p[k] for k in ('commit', 'pin')})(routing_adapter.preflight(R)))
implementation = [s for s in (steps.get('fill'), *(steps.get('schematic', {}).get('implementation_steps', [])),
                              steps.get('planes')) if s is not None]
plan = dict(schema=pod_driver.SCHEMA, scope='scope.json', envelope=inputs['envelope'], parts=inputs['parts'],
            spec='requirements-map/spec.md', spec_record='requirements-map/spec-record.json',
            writer_inputs={'intent': writer, 'deviations': inputs['deviations']}, implementation_steps=implementation,
            placement_adapter=adapter, routing_adapter=route,
            envelope_content={'intent': writer, 'layout': inputs['layout'], 'antenna_facts': inputs['antenna'],
                              'captured_rule_areas': inputs['retention']},
            review_profile=profile, implementation=profile['adjudicator'],
            routing_budget_s=budget, review_budget_s=review_budget)
stage('pod_driver.validate_plan', lambda: dict(zip(('max_iterations', 'max_seconds'), pod_driver.validate_plan(plan))))
(planning / 'plan.json').write_text(text(plan))
stage('pod_driver.build(dry_run) composed scope', lambda: {k: v for k, v in pod_driver.build(
    planning / 'plan.json', OUT / 'prepared', dry_run=True).items() if k in ('status', 'done')})

# The same plan on the compiled scope as-is (no envelope declaration, no added checks): shows which
# refusal the composition itself adds. Its own copy; never an input to the composed run.
plain = OUT / 'planning-compiled-scope'
shutil.copytree(planning, plain)
(plain / 'composition/scope-composition.json').unlink()
write_scope(plain, compiled)
(plain / 'plan.json').write_text(text(plan))
stage('scaffold.scaffold compiled scope', lambda: run_scaffold(plain, OUT / 'scaffold-compiled-scope'))
stage('scaffold.write_envelope_content compiled scope', lambda: production_content(
    OUT / 'scaffold-compiled-scope', OUT / 'content-compiled-scope'))
stage('pod_driver.build(dry_run) compiled scope', lambda: {k: v for k, v in pod_driver.build(
    plain / 'plan.json', OUT / 'prepared-compiled-scope', dry_run=True).items() if k in ('status', 'done')})


def block_candidates():
    cache = ITER8N / 'cand'
    bound_ids = sorted({json.loads(p.read_text())['sources'].get('policy_sha256') for p in cache.glob('*.candidate.json')})
    passed = [n for n in ('pod_driver.build(dry_run) composed scope', 'pod_driver.build(dry_run) compiled scope')
              if stages[n]['status'] == 'accepted']
    if not passed:
        raise ValueError(f'{len(list(cache.glob("*.candidate.json")))} iter8n block candidates bind policy {bound_ids}; '
                         f'the derived request policy is {identity(policy)}. The repack waits on a passing dry run '
                         '(none passed), per the coordinator instruction; nothing was repacked.')
    return {'dry_runs_passed': passed, 'iter8n_candidates_bind': bound_ids, 'derived_policy': identity(policy),
            'repack': 'production-capture/repack.py (evidence/repack-a9dac2f/repack.json)'}
stage('placement.block_candidates_repack', block_candidates)

# DIAGNOSTIC (scratch only, never an input).
diagnostics = {}


def diagnostic_j3():
    """The envelope's J3 pose through the writer's own native operations, versus the iter8n seed."""
    import pcbnew
    from agent_ee.symbol_library import nanometres
    j3 = next(f for f in envelope_record['fixed_footprints'] if f['reference'] == 'J3')
    board = pcbnew.BOARD()
    path = planning / 'footprints/Connector_Card.pretty/microSD_HC_Hirose_DM3AT-SF-PEJM5.kicad_mod'
    fp = pcbnew.FootprintLoad(str(path.parent), path.stem)
    board.Add(fp)
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetOrientationDegrees(float(j3['rotation_deg']))
    fp.SetPosition(pcbnew.VECTOR2I(*(nanometres(v) for v in j3['anchor_mm'])))
    box = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
    pads = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y) for p in fp.Pads())
    seed = pcbnew.LoadBoard(str(ITER8N / 'seed.kicad_pcb'))
    other = next(f for f in seed.GetFootprints() if f.GetReference() == 'J3')
    seed_pads = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y) for p in other.Pads())
    return {'anchor_mm': j3['anchor_mm'], 'side': j3['side'], 'rotation_deg': j3['rotation_deg'],
            'courtyard_bbox_mm': [box.GetLeft() / 1e6, box.GetTop() / 1e6, box.GetRight() / 1e6, box.GetBottom() / 1e6],
            'left_overhang_mm': -box.GetLeft() / 1e6, 'declared_max_mm': 20.3,
            'within_declared_overhang': -box.GetLeft() <= 20300000,
            'right_edge_inside_outline': box.GetRight() <= 90000000 and box.GetTop() >= 0 and box.GetBottom() <= 65000000,
            'pads_equal_iter8n_seed': pads == seed_pads, 'iter8n_seed_sha256': sha(ITER8N / 'seed.kicad_pcb')}


try:
    diagnostics['diagnostic.J3_transform'] = {'status': 'ok', **diagnostic_j3()}
except Exception as exc:
    diagnostics['diagnostic.J3_transform'] = {'status': 'failed', 'error': f'{type(exc).__name__}: {exc}'}
print('diagnostic.J3_transform', json.dumps(diagnostics['diagnostic.J3_transform'], sort_keys=True)[:600], flush=True)


def record_of(directory):
    path = OUT / directory / 'dry-run-record.json'
    return json.loads(path.read_text()) if path.exists() else None


result = dict(schema='pod-capture.pipeline/2', done=False, inference=False,
              authority='Producer execution and declarations on a fresh capture copy; no placement, routing, '
                        'campaign or model run. The diagnostic is scratch-only and never an input.',
              agent_ee=str(A), router_checkout=str(R), scope={'path': str(SCOPE_DIR / 'scope.json'),
                                                             'sha256': sha(SCOPE_DIR / 'scope.json')},
              composed_scope_sha256=sha(planning / 'scope.json'), scope_composition=derivation,
              plan_sha256=sha(planning / 'plan.json'), derived_request_policy_identity=identity(policy),
              budgets={'routing_budget_s': budget, 'review_budget_s': review_budget, 'placement_timeout_s': 1500,
                       'max_iterations': 2},
              stages=stages, diagnostics=diagnostics,
              dry_run_records={'composed': record_of('prepared'), 'compiled': record_of('prepared-compiled-scope')})
(OUT / 'pipeline.json').write_text(text(result))
