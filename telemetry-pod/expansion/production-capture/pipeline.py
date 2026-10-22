"""Phase B on the production capture: binding-fill, scaffold, envelope content, emitter and
annotation declarations, derived request policy and the real pod_driver dry run.

Every stage runs the owned agent-ee producer on a fresh copy of the capture root; a refusal is
kept verbatim and never substituted. Two clearly labelled DIAGNOSTICS run on scratch copies
only (they are never inputs): the envelope content without the uncaptured J3 fixed part, to
check the U1 retention and the D-PCB-6/7v2 rule areas against the corrected-policy board, and
the J3 back-side transform on its own. No placement, routing, campaign or model runs here.

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
CORRECTED = X / 'routing-diagnostic/corrected-policy-iter7/ca2.kicad_pcb'
ITER8N_SEED = Path('/home/halbritt/.cache/agent449-pod/iter8n/seed.kicad_pcb')
BOARD, SCHEMATIC = 'project/telemetry-pod.kicad_pcb', 'project/telemetry-pod.kicad_sch'


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
    print(f"{stages[name]['status']:9} {name}" + (f": {stages[name]['error']}" if 'error' in stages[name] else ''),
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
scope = {**compiled, 'inputs': [{'path': p.name, 'at': p.name} for p in sorted(planning.iterdir())]}
(planning / 'scope.json').write_text(text(scope))
intent, bound = 'composition/intent.json', 'composition/intent.bound.json'
inputs = {k: 'composition/' + v for k, v in (
    ('parts', 'parts.json'), ('refs', 'part-refs.json'), ('deviations', 'deviations.json'),
    ('envelope', 'envelope.json'), ('layout', 'emitter-layout.json'), ('footprints', 'footprints.json'),
    ('antenna', 'antenna-facts.json'), ('retention', 'captured-rule-areas.json'), ('planes', 'planes.json'),
    ('policy', 'placement-policy.json'))}
read = lambda rel: json.loads((planning / rel).read_text())  # noqa: E731

# 1. Binding-fill: a distinct produced bound projection; the writer intent keeps its valid bindings.
steps = {}
stage('binding_fill.configuration', lambda: steps.update(fill=binding_fill.configuration(
    A, intent=intent, manifest=inputs['parts'], part_refs=inputs['refs'], deviations=inputs['deviations'],
    captures='.', dependencies=[], output=bound, source_migration=True)) or {'writes': steps['fill']['writes']})


def run_fill():
    _, report = binding_fill.fill(planning, read(intent), read(inputs['parts']), read(inputs['refs']),
                                  read(inputs['deviations']), captures='.', source_migration=True)
    return {'components': len(report['components'])}
stage('binding_fill.fill', run_fill)

# 2. Scaffold (stage one, the driver's own call) and envelope content on its output.
scaffold_out = OUT / 'scaffold'
stage('scaffold.scaffold', lambda: {k: v for k, v in scaffold.scaffold(
    planning / inputs['envelope'], planning / inputs['parts'], scaffold_out,
    scope_path=planning / 'scope.json').items() if k in ('status', 'candidate_id', 'baseline_id')})
content_kwargs = dict(intent_rel=intent, layout_rel=inputs['layout'], antenna_facts_rel=inputs['antenna'],
                      captured_rule_areas_rel=inputs['retention'])


def content(root, envelope_rel):
    scaffold.write_envelope_content(root, envelope_rel, inputs['parts'], BOARD, **content_kwargs)
    return {'board_sha256': sha(root / BOARD)}


def production_content():
    if not scaffold_out.exists():
        raise ValueError('scaffold not available')
    work = OUT / 'content'
    shutil.copytree(scaffold_out / 'inputs', work)
    return content(work, inputs['envelope'])
stage('scaffold.write_envelope_content', production_content)
stage('scaffold.content_step', lambda: steps.update(content=scaffold.content_step(
    A, inputs['envelope'], inputs['parts'], BOARD, intent=intent, layout=inputs['layout'],
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


def envelope_reaches_placer():
    checks = [c for c in scope['checks'] if c['kind'] == 'placement' and 'envelope' in c.get('params', {})]
    if not checks:
        raise ValueError('the scope maps no placement check with params.envelope, so placement_adapter.envelope_fixed '
                         'passes no envelope overhangs, fixed references or provenance to the packer')
stage('placement.scope_envelope_binding', envelope_reaches_placer)


def iter8n_candidates():
    cache = Path('/home/halbritt/.cache/agent449-pod/iter8n/cand')
    bound_ids = sorted({json.loads(p.read_text())['sources'].get('policy_sha256')
                        for p in cache.glob('*.candidate.json')})
    raise ValueError(f'{len(list(cache.glob("*.candidate.json")))} iter8n block candidates bind policy {bound_ids}; '
                     f'the derived request policy is {identity(policy)}: repack with the released AGENTEE-439 '
                     'engine (not on agent-ee origin/main)')
stage('placement.block_candidates_repack', iter8n_candidates)


def engine_g1():
    placement_adapter.validate_declaration({'schema': 'agent-ee.placement-adapter/1', 'helper': 'agent-ee.placer/1',
                                            'policy': inputs['policy'], 'fixed_footprints': [], 'timeout_s': 1500,
                                            'blocks': 'composition/blocks.json'})
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
            writer_inputs={'intent': intent, 'deviations': inputs['deviations']}, implementation_steps=implementation,
            placement_adapter=adapter, routing_adapter=route,
            envelope_content={'intent': intent, 'layout': inputs['layout'], 'antenna_facts': inputs['antenna'],
                              'captured_rule_areas': inputs['retention']},
            review_profile=profile, implementation=profile['adjudicator'],
            routing_budget_s=budget, review_budget_s=review_budget)
(planning / 'plan.json').write_text(text(plan))
stage('pod_driver.validate_plan', lambda: dict(zip(('max_iterations', 'max_seconds'), pod_driver.validate_plan(plan))))
stage('pod_driver.build(dry_run)', lambda: {k: v for k, v in pod_driver.build(
    planning / 'plan.json', OUT / 'prepared', dry_run=True).items() if k in ('status', 'done')})
dry = OUT / 'prepared/dry-run-record.json'

# DIAGNOSTICS (scratch only, never inputs).
diagnostics = {}


def diagnostic_content():
    """Content without J3 only, to check retention and the native rule areas exactly."""
    import pcbnew
    work = OUT / 'diagnostic-content'
    shutil.copytree(scaffold_out / 'inputs', work)
    env = json.loads((work / inputs['envelope']).read_text())
    env['fixed_footprints'] = [f for f in env['fixed_footprints'] if f['reference'] != 'J3']
    env['constraint_provenance'] = {k: v for k, v in env['constraint_provenance'].items()
                                    if not k.startswith('/fixed_footprints/')}
    variant = 'composition/diagnostic-envelope-without-J3.json'
    (work / variant).write_text(text(env))
    retention = json.loads((work / inputs['retention']).read_text())
    retention['envelope'] = {'path': variant, 'sha256': sha(work / variant)}
    retention['items'][0]['pose'] = {k: v for k, v in retention['items'][0]['pose'].items()}
    (work / 'composition/diagnostic-retention.json').write_text(text(retention))
    scaffold.write_envelope_content(work, variant, inputs['parts'], BOARD,
                                    **{**content_kwargs, 'captured_rule_areas_rel': 'composition/diagnostic-retention.json'})
    board = pcbnew.LoadBoard(str(work / BOARD))
    corrected = pcbnew.LoadBoard(str(CORRECTED))

    def areas(b):
        found = {}
        for zone in b.Zones():
            if zone.GetIsRuleArea():
                outline = zone.Outline().Outline(0)
                found[zone.GetZoneName()] = {
                    'layers': sorted(pcbnew.LayerName(layer) for layer in zone.GetLayerSet().Seq()),
                    'polygon_nm': sorted((outline.CPoint(i).x, outline.CPoint(i).y) for i in range(outline.PointCount())),
                    'no_tracks': zone.GetDoNotAllowTracks(), 'no_vias': zone.GetDoNotAllowVias(),
                    'no_pads': zone.GetDoNotAllowPads(), 'no_pour': zone.GetDoNotAllowZoneFills(),
                    'no_footprints': zone.GetDoNotAllowFootprints()}
        return found
    produced, reference = areas(board), areas(corrected)
    pairs = {'D-PCB-7v2-In1-no-tracks': 'D-PCB-7v2 In1.Cu no tracks (board outline)',
             'D-PCB-6-RF-reference': 'D-PCB-6 RF reference keep-out'}
    comparison = {ours: {'produced': produced.get(ours), 'corrected_board': reference.get(theirs),
                         'identical': produced.get(ours) == reference.get(theirs)} for ours, theirs in pairs.items()}
    u1 = next(f for f in board.GetFootprints() if f.GetReference() == 'U1')
    return {'board_sha256': sha(work / BOARD), 'rule_areas': comparison,
            'u1': {'fpid': u1.GetFPIDAsString(), 'position_nm': [u1.GetPosition().x, u1.GetPosition().y],
                   'zones': len(list(u1.Zones())), 'retention_verified': 'verify_native_retention passed in the writer'},
            'footprints': sorted(f.GetReference() for f in board.GetFootprints())}


def diagnostic_j3():
    """The envelope's J3 pose through the writer's own native operations, versus the iter8n seed."""
    import pcbnew
    from agent_ee.symbol_library import nanometres
    record = board_envelope.validate((planning / inputs['envelope']).read_bytes())
    j3 = next(f for f in record['fixed_footprints'] if f['reference'] == 'J3')
    board = pcbnew.LoadBoard(str(scaffold_out / 'inputs' / BOARD))
    path = planning / 'footprints/Connector_Card.pretty/microSD_HC_Hirose_DM3AT-SF-PEJM5.kicad_mod'
    fp = pcbnew.FootprintLoad(str(path.parent), path.stem)
    board.Add(fp)
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetOrientationDegrees(float(j3['rotation_deg']))
    fp.SetPosition(pcbnew.VECTOR2I(*(nanometres(v) for v in j3['anchor_mm'])))
    box = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
    pads = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y) for p in fp.Pads())
    seed = pcbnew.LoadBoard(str(ITER8N_SEED))
    other = next(f for f in seed.GetFootprints() if f.GetReference() == 'J3')
    seed_pads = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y) for p in other.Pads())
    return {'anchor_mm': j3['anchor_mm'], 'side': j3['side'], 'rotation_deg': j3['rotation_deg'],
            'courtyard_bbox_mm': [box.GetLeft() / 1e6, box.GetTop() / 1e6, box.GetRight() / 1e6, box.GetBottom() / 1e6],
            'left_overhang_mm': -box.GetLeft() / 1e6, 'declared_max_mm': 20.3,
            'within_declared_overhang': -box.GetLeft() <= 20300000,
            'right_edge_inside_outline': box.GetRight() <= 90000000 and box.GetTop() >= 0 and box.GetBottom() <= 65000000,
            'pads_equal_iter8n_seed': pads == seed_pads, 'iter8n_seed_sha256': sha(ITER8N_SEED)}


def diagnostic_fill():
    """The genuine fill on an intent copy without J3 only: do the other 304 bindings revalidate?"""
    source = read(intent)
    j3 = next(c['id'] for c in source['components'] if c['reference'] == 'J3')
    variant = copy.deepcopy(source)
    variant['components'] = [c for c in variant['components'] if c['id'] != j3]
    for net in variant['nets']:
        net['terminals'] = [t for t in net['terminals'] if t['component'] != j3]
    variant['no_connects'] = [n for n in variant.get('no_connects', []) if n.get('component') != j3]
    # A net left with one terminal (/SD_CLK: U1 only) becomes that terminal's no-connect, here only.
    orphaned = [n for n in variant['nets'] if len(n['terminals']) == 1]
    variant['no_connects'] += [n['terminals'][0] for n in orphaned]
    variant['nets'] = [n for n in variant['nets'] if len(n['terminals']) > 1]
    args = (read(inputs['parts']), read(inputs['refs']), read(inputs['deviations']))
    try:
        binding_fill.fill(planning, variant, *args, captures='.', source_migration=True)
        as_is = 'ok'
    except ValueError as exc:
        as_is = f'ValueError: {exc}'
    # Second pass: set aside the fields binding-fill does not produce without --ratings (and never
    # produces: Qualification), to see whether every canonical identity binding revalidates.
    aside = ('Qualification', 'AGENT_EE_Ratings', 'Voltage', 'Power')
    counts = {k: sum(k in c.get('part_binding', {}) for c in variant['components']) for k in aside}
    for comp in variant['components']:
        for key in aside:
            comp.get('part_binding', {}).pop(key, None)
    output, report = binding_fill.fill(planning, variant, *args, captures='.', source_migration=True)
    before = {c['reference']: {k: v for k, v in c.get('part_binding', {}).items() if k not in aside}
              for c in source['components']}
    changed = {c['reference']: sorted(set(c.get('part_binding', {})) - set(before[c['reference']]))
               for c in output['components'] if c.get('part_binding', {}) != before[c['reference']]}
    return {'as_is': as_is, 'set_aside_field_counts': counts,
            'bound_components': len(report['components']), 'components_with_added_fields': changed,
            'assembly_deviations': {r['reference']: r['assembly_deviation'] for r in report['components']
                                    if r.get('assembly_deviation') is not None}}


for name, fn in (('diagnostic.binding_fill_without_J3', diagnostic_fill),
                 ('diagnostic.content_without_J3', diagnostic_content), ('diagnostic.J3_transform', diagnostic_j3)):
    try:
        diagnostics[name] = {'status': 'ok', **fn()}
    except Exception as exc:
        diagnostics[name] = {'status': 'failed', 'error': f'{type(exc).__name__}: {exc}'}
    print(name, json.dumps(diagnostics[name], sort_keys=True)[:600], flush=True)

result = dict(schema='pod-capture.pipeline/1', done=False, inference=False,
              authority='Producer execution and declarations on a fresh capture copy; no placement, routing, '
                        'campaign or model run. Diagnostics are scratch-only and never inputs.',
              agent_ee=str(A), router_checkout=str(R), scope={'path': str(SCOPE_DIR / 'scope.json'),
                                                             'sha256': sha(SCOPE_DIR / 'scope.json')},
              plan_sha256=sha(planning / 'plan.json'), derived_request_policy_identity=identity(policy),
              budgets={'routing_budget_s': budget, 'review_budget_s': review_budget, 'placement_timeout_s': 1500},
              stages=stages, diagnostics=diagnostics, prepared_output_exists=(OUT / 'prepared').exists(),
              dry_run_record=json.loads(dry.read_text()) if dry.exists() else None)
(OUT / 'pipeline.json').write_text(text(result))
