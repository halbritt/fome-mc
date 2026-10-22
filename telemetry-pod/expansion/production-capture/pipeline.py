"""Phase B on the production capture: binding-fill, scaffold, envelope content, emitter and
annotation declarations, the composed production scope, the derived request policy and the
real pod_driver dry run.

Every stage runs the owned agent-ee producer on a fresh copy of the capture root; a refusal is
kept verbatim and never substituted. The production scope is composed here from the compiled
Rev-3 scope in two layers:

- assembly: one assembly_readiness check over a captured JLC stock capture, the writer-owned
  deviations and the passive ratings, so the binding-fill --ratings receipt reaches the
  coordinator rating_provenance (AGENTEE-256). Captured bindings are not assembly qualification:
  the stock coverage and age, and the J1 hand-fit citation, are graded unknowns kept explicit;
- envelope: a scope envelope declaration over composition/envelope.json with one check per
  derived envelope obligation (connector-edge/1 for each fixed footprint, outline-containment/1
  carrying the declared overhangs to the packer) and the electrical-locality/1 check over the
  captured pad obligations the packing policy embeds.

The production scope is both layers. The PREPARATION PROBE scope is the compiled scope plus the
assembly layer only; it is never the production scope and exists to show what preparation does
without the envelope layer, which still refuses on obligations no agent-ee criterion binds.

The plan of record carries the authorized bounded budget (max_iterations 2, placement timeout_s
900-1500 s; ROUTE.md R2). The pod driver at this agent-ee pin refuses it; that refusal is kept. The
probe plan omits the budget fields and therefore prepares with the driver defaults; its campaign
is checked against the authorized budget, refused, and set aside as not launchable.

A third layer, blocks, carries the library refusals of the 18-block repack (repack.py
block-obligations.json): the pre-6v3 and buck-3v3 board-region copper/native-check and witness-pose
obligations stay unresolved, as NOT CHECKED scope limitations and as a packet input, and the actual
review packet of the prepared probe is checked to expose them. The J1 hand-fit source chain
(assembly/hand-fit-policy.json) is verified link by link and declared in the assembly check only when
the agent-ee export can express it; otherwise its refusal is kept.

Producer declarations mount the export's src directory (the import root agent_ee's step builders
expect); every declared module is imported from its actual mount source before preparation.

One clearly labelled DIAGNOSTIC runs on a scratch copy only (it is never an input): the J3
back-side transform. No placement, routing, campaign or model runs here.

Usage (fome-mc root, system python with pcbnew):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/pipeline.py \
      AGENT_EE_EXPORT ROUTER_CHECKOUT SCOPE_DIR CAPTURE_ROOT NEW_OUT_DIR [STOCK_CAPTURE_DIR [REPACK_DIR]]
SCOPE_DIR is a compiled Rev-3 scope directory (scope.json plus requirements-map/).
STOCK_CAPTURE_DIR is an agent-ee.jlc-catalog/1 producer capture (catalog.json plus responses/);
it defaults to the retained v9 pilot capture sources/pilot-assembly-stock. A day-of-generation
capture (POD-AC-5) replaces it at launch. REPACK_DIR is a repack.py output (repack.json,
block-obligations.json, cand/, logs/); it defaults to evidence/repack-a9dac2f-j5. Set
AGENT_EE_TOOL_SOURCE_CACHE to an absolute directory you own.
"""
import copy
from datetime import datetime, timezone
import hashlib
import json
import shutil
import sys
import traceback
from pathlib import Path

A, R, SCOPE_DIR, CAPTURE, OUT = (Path(p).resolve() for p in sys.argv[1:6])
HERE = Path(__file__).resolve().parent
STOCK = Path(sys.argv[6]).resolve() if len(sys.argv) > 6 else HERE / 'sources/pilot-assembly-stock'
REPACK = Path(sys.argv[7]).resolve() if len(sys.argv) > 7 else HERE / 'evidence/repack-a9dac2f-j5'
sys.path[:0] = [str(A / 'src')]
from agent_ee import (add_planes, assembly_readiness, binding_fill, board_envelope,  # noqa: E402
                      placement_adapter, pod_driver, routing_adapter, scaffold, schematic_stage)
from agent_ee.storage import identity  # noqa: E402

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
STOCK_AT = 'assembly-stock'
BLOCK_OBLIGATIONS = 'composition/block-obligations.json'
HAND_FIT = HERE / 'assembly/hand-fit-policy.json'
# agent-509 notes/509-j1-handfit-chain.txt: the four chain sources and their recorded SHA-256.
HAND_FIT_CHAIN = {
    'telemetry-pod/REQUIREMENTS.md': '0f52e0ae17f62be348525a5cfab2d9ea5c823df7bc5f580700ed7dd10cbcaae7',
    'telemetry-pod/expansion/design-rules/constraints.json': 'e7e095b3ca595fdfb3c73fc22ad87c326fbc1c152523e85f2da4df4d908ea2e4',
    'telemetry-pod/expansion/j1-historical-source/C596198.json': 'f07570cc3502c504acf520e0102dd516f06363589adda81c9c9fb34003641cb5',
    'telemetry-pod/expansion/complete-parts-manifest/parts.json': '759d3be5f3d96bc10b306763559afef94a2d901ccb164bc6a4161f24b662e0ff'}
# The bounded first run (agent-509 ruling 2026-10-22; ROUTE.md R2): two campaign iterations,
# iteration 2 one placement turn with the placement adapter timeout_s between 900 and 1500 s.
AUTHORIZED = {'max_iterations': 2, 'placement_timeout_s': [900, 1500]}
PLACEMENT_TIMEOUT_S = 1500


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
shutil.copytree(STOCK, planning / STOCK_AT, symlinks=False)
for rel in HAND_FIT_CHAIN:  # byte copies at their fome-mc paths; the capture already holds two of them
    target = planning / rel
    if target.exists() and target.read_bytes() != (ROOT / rel).read_bytes():
        raise SystemExit(f'capture copy of {rel} differs from fome-mc')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / rel, target)
shutil.copyfile(REPACK / 'block-obligations.json', planning / BLOCK_OBLIGATIONS)
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


def stock_coverage():
    """What the captured stock can and cannot show for the bound BOM; nothing here is graded as a pass."""
    from agent_ee.jlc_stock_capture import validate_capture
    doc = read(STOCK_AT + '/catalog.json')
    info = validate_capture(doc, lambda rel: (planning / STOCK_AT / rel).read_bytes())
    lcsc = {p['lcsc'] for p in read(inputs['parts'])['parts'] if p.get('lcsc')}
    observed = set(doc['parts']) | set(info['not_found'])
    deviated = sorted(d['original']['lcsc'] for d in read(inputs['deviations'])['deviations'])
    key = lambda c: int(c[1:])  # noqa: E731
    per_id = stock_status(doc, lcsc, deviated)
    return {'capture': {'path': STOCK_AT + '/catalog.json', 'sha256': sha(planning / STOCK_AT / 'catalog.json'),
                        'source': STOCK.relative_to(ROOT).as_posix() if STOCK.is_relative_to(ROOT) else str(STOCK), 'as_of': info['as_of'], 'completed_at': info['completed_at'],
                        'endpoint': doc['source']['endpoint'], 'method': doc['source']['method'],
                        'requested': len(info['requested']), 'not_found': info['not_found'], 'failed': info['failed']},
            'bom_lcsc': len(lcsc), 'observed': len(lcsc & observed),
            'unobserved': sorted(lcsc - observed, key=key), 'outside_bom': sorted(observed - lcsc, key=key),
            'deviated': deviated, 'evaluated_at': EVALUATED_AT, 'max_age_hours': 24,
            'status_counts': {k: sum(1 for r in per_id.values() if r['status'] == k)
                              for k in sorted({r['status'] for r in per_id.values()})},
            'stale': sorted((i for i, r in per_id.items() if r['stale']), key=key),
            'short_for_one_board': sorted((i for i, r in per_id.items() if r['status'] == 'in_stock'
                                           and r['stock'] < r['quantity_per_board']), key=key),
            'per_id': per_id}


EVALUATED_AT = datetime.now(timezone.utc).isoformat()


def stock_status(doc, lcsc, deviated):
    """Per BOM LCSC id: what this capture observed, when, from which source, and whether it is stale."""
    quantity = {}
    for p in read(inputs['parts'])['parts']:
        if p.get('lcsc'):
            quantity[p['lcsc']] = quantity.get(p['lcsc'], 0) + len(p['instances'])
    requests = {r['lcsc']: r for r in doc['requests']}
    now = datetime.fromisoformat(EVALUATED_AT)
    out = {}
    for i in sorted(lcsc, key=lambda c: int(c[1:])):
        r, row = requests.get(i), doc['parts'].get(i)
        if r is None:
            status = 'unobserved'
        elif r['status'] != 'found':
            status = r['status']  # not_found or failed (source unavailable); never read as in stock
        elif row is None or row.get('stock') is None:
            status = 'unknown_stock'
        else:
            status = 'in_stock' if row['stock'] > 0 else 'zero_stock'
        fetched = r['fetched_at'] if r else None
        age = round((now - datetime.fromisoformat(fetched)).total_seconds() / 3600, 3) if fetched else None
        out[i] = {'status': status, 'stock': row.get('stock') if row else None, 'mpn': row.get('mpn') if row else None,
                  'library_tier': row.get('library_tier') if row else None, 'quantity_per_board': quantity[i],
                  'fetched_at': fetched, 'http_status': r['http_status'] if r else None,
                  'reason': r['reason'] if r else 'not requested by this capture',
                  'response': r['response'] if r else None, 'age_hours': age,
                  'stale': age is None or age > 24, 'deviated': i in deviated}
    return out


def hand_fit_chain():
    """The J1 source chain (agent-509): recompute every link; ask the pinned export whether it can express it."""
    declared = json.loads(HAND_FIT.read_text())['hand_fit_policy']
    links = {}
    for rel, expected in HAND_FIT_CHAIN.items():
        links[rel] = {'sha256': sha(planning / rel), 'recorded_by_agent_509': expected,
                      'equals_fome_mc': (planning / rel).read_bytes() == (ROOT / rel).read_bytes()}
        if links[rel]['sha256'] != expected or not links[rel]['equals_fome_mc']:
            raise ValueError(f'hand-fit chain source {rel} is not the recorded bytes')
    cited = [declared, declared['selection'], *declared['selection']['records']]
    for c in cited:
        if sha(planning / c['source']) != c['sha256']:
            raise ValueError(f"declared hand-fit citation {c['source']} differs from its sha256")
    line = (planning / declared['source']).read_text().split('\n')[declared['line'] - 1]
    chosen = (planning / declared['selection']['source']).read_text().split('\n')[declared['selection']['line'] - 1]
    if declared['quote'] not in line or declared['selection']['quote'] not in chosen:
        raise ValueError('a hand-fit quote is not on its cited line')
    record = sha(planning / 'telemetry-pod/expansion/j1-historical-source/C596198.json')
    for r in declared['selection']['records']:
        obj = json.loads((planning / r['source']).read_text())
        for token in [t for t in r['pointer'].split('/')[1:]]:
            obj = obj[int(token)] if isinstance(obj, list) else obj[token]
        if (obj['mpn'], obj['lcsc']) != ('1-776163-1', 'C596198'):
            raise ValueError(f"{r['source']}{r['pointer']} is not the selected J1 identity")
        if 'selection' in obj and obj['selection'].get('part_record_sha256') != record:
            raise ValueError(f"{r['source']}{r['pointer']} names another part record")
    deviation = next(d for d in read(inputs['deviations'])['deviations'] if d.get('policy') == 'owner_hand_fit')
    if deviation['original'] not in declared['identities']:
        raise ValueError('the owner_hand_fit deviation identity is not the chain identity')
    try:
        validated = assembly_readiness._validate_hand_fit_policy(copy.deepcopy(declared), inputs['deviations'])
        verified = assembly_readiness._verify_hand_fit_policy(planning, validated)
        export = {'status': 'expressible', 'class': verified['class'],
                  'association': verified.get('selection', {}).get('association'),
                  'part_record_links': verified.get('selection', {}).get('part_record_links')}
    except Exception as exc:  # the pinned validator's own refusal, kept verbatim
        validated, export = None, {'status': 'refused by this agent-ee export', 'error': f'{type(exc).__name__}: {exc}'}
    return {'declared': {'path': HAND_FIT.relative_to(ROOT).as_posix(), 'sha256': sha(HAND_FIT)},
            'links': links, 'deviation_identity': deviation['original'], 'agent_ee': export,
            'declared_in_scope': validated is not None}, validated


# 0a. The assembly layer: one assembly_readiness check, so --ratings reaches rating_provenance.


def compose_assembly(base):
    """Add one assembly_readiness check (verification stage) and its POD-AC-5-derived requirement."""
    record = next(r for r in read('requirements-map/spec-record.json')['requirements'] if r['id'] == 'POD-AC-5')
    check = dict(id='assembly', kind='assembly_readiness', stage='verification',
                 params=dict(catalog=STOCK_AT + '/catalog.json', boards=1, deviations=inputs['deviations'],
                             require_passive_ratings=True, max_age_hours=24,
                             **({'hand_fit_policy': hand_fit_policy} if hand_fit_policy is not None else {})))
    requirement = {'id': 'POD-DERIVED-AC-5-ASSEMBLY', 'intent': 'acceptance',
                   'statement': ('Purchased BOM components carry LCSC binding and BOM properties, captured passive '
                                 'ratings with the binding-fill receipt as rating provenance, and JLC stock captured '
                                 'within 24 hours of generation for one board (POD-AC-5 "on the day of generation"). '
                                 'Hand-fit exclusions and owner obligations stay separate.'),
                   'source': {'path': 'requirements-map/spec.md', 'locator': json.dumps(record['locator'], sort_keys=True)},
                   'checks': ['assembly']}
    if 'intent' not in base['baseline']['requirements'][0]:
        requirement.pop('intent')
    done = base['generation']['done_check']
    checks = list(base['checks'])
    checks.insert(next(i for i, c in enumerate(checks) if c['id'] == done), check)
    composed = copy.deepcopy(base)
    composed['checks'] = checks
    composed['baseline']['requirements'] = [*base['baseline']['requirements'], requirement]
    counts = ', '.join(f'{k} {v}' for k, v in coverage['status_counts'].items())
    composed['limitations'] = [*base['limitations'],
        'Composed by production-capture/pipeline.py: assembly_readiness over ' + STOCK_AT + '/catalog.json (the '
        f"captured stock named in scope-composition.json, as_of {coverage['capture']['as_of']}). It carries the "
        f"binding-fill --ratings receipt into rating_provenance. Of {coverage['bom_lcsc']} BOM LCSC ids: {counts}; "
        f"{len(coverage['stale'])} are older than 24 hours at composition ({EVALUATED_AT}) and the check re-grades "
        'age at its own run. ' + (
            'The J1 owner_hand_fit deviation is cited by hand_fit_policy: the unchanged POD-AC-5 owner statement '
            '(REQUIREMENTS.md line 139, "the AMPSEAL header") with its category selection chain (D-PCB-10, the '
            'C596198 part record and both manifests). That is an assembly disposition only, not mating, enclosure '
            'or purchase qualification. ' if hand_fit_policy is not None else
            'The J1 owner_hand_fit deviation has no hand_fit_policy: this agent-ee export cannot express the '
            'POD-AC-5 category-to-1-776163-1 source chain (scope-composition.json assembly.hand_fit). ') +
        'Captured stock and bindings are not assembly qualification. POD-AC-5 remains NOT CHECKED.']
    return composed


# 0c. The blocks layer: library refusals of the repack stay unresolved obligations, never acceptance.
def block_obligations():
    """Re-verify the repack's obligation record against the repack outputs it names."""
    doc = read(BLOCK_OBLIGATIONS)
    for block in doc['blocks']:
        cand = REPACK / block['generic_candidate']['path']
        refusal = REPACK / block['library_refusal']['log']
        if sha(cand) != block['generic_candidate']['sha256'] or sha(refusal) != block['library_refusal']['sha256']:
            raise SystemExit(f"block obligations for {block['block']} do not match the repack outputs")
        if block['status'] != 'unresolved' or any(o['status'] != 'unresolved' for o in block['obligations']):
            raise SystemExit('a library-refused block obligation is marked resolved; only a native check may do that')
    repack = json.loads((REPACK / 'repack.json').read_text())
    refused = sorted(b for b, r in repack['packed'].items() if r['path'] == 'generic pack after library refusal')
    if refused != sorted(b['block'] for b in doc['blocks']):
        raise SystemExit(f'library-refused blocks {refused} and block obligations differ')
    return doc, {'path': BLOCK_OBLIGATIONS, 'sha256': sha(planning / BLOCK_OBLIGATIONS),
                 'repack': {'path': str(REPACK / 'repack.json'), 'sha256': sha(REPACK / 'repack.json')},
                 'blocks': {b['block']: [o['id'] for o in b['obligations']] for b in doc['blocks']}}


def compose_blocks(base):
    """NOT CHECKED limitations per unresolved obligation, and the record as a review packet input."""
    composed = copy.deepcopy(base)
    lines = []
    for block in obligation_doc['blocks']:
        for o in block['obligations']:
            lines.append(f"POD-DERIVED-BLOCK-{o['id'].upper()}: NOT CHECKED (unresolved; {BLOCK_OBLIGATIONS} sha256 "
                         f"{obligation_record['sha256']}): {o['statement']} Generic packing is geometry only. "
                         f"{block['real_placement']}")
    composed['limitations'] = [*base['limitations'], *lines]
    composed['packet_inputs'] = [*base.get('packet_inputs', [base['schematic'], base['board']]), BLOCK_OBLIGATIONS]
    return composed


# 0b. The production scope: assembly layer + envelope declaration, obligation checks and locality.
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


coverage = stock_coverage()
hand_fit, hand_fit_policy = hand_fit_chain()
obligation_doc, obligation_record = block_obligations()
assembled = compose_blocks(compose_assembly(compiled))
composed, derivation, coverage_inputs = compose_scope(assembled)
derivation = {**derivation, 'schema': 'pod-capture.scope-composition/3',
              'layers': ['assembly', 'blocks', 'envelope'], 'added_checks': ['assembly', *derivation['added_checks']],
              'added_requirements': ['POD-DERIVED-AC-5-ASSEMBLY', *derivation['added_requirements']],
              'assembly': {'check': next(c for c in assembled['checks'] if c['id'] == 'assembly'),
                           'stock': coverage, 'hand_fit': hand_fit},
              'blocks': obligation_record}
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
# binding_fill, schematic_stage and add_planes mount their source root at /tool/agent-ee with
# PYTHONPATH=/tool/agent-ee, so they take the export's src directory (as agent-ee's own tests do);
# scaffold.content_step takes the export root and appends src itself.
SRC = A / 'src'
steps = {}
stage('binding_fill.configuration', lambda: steps.update(fill=binding_fill.configuration(
    SRC, intent=writer, manifest=inputs['parts'], part_refs=inputs['refs'], deviations=inputs['deviations'],
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
stage('scaffold.scaffold production scope', lambda: run_scaffold(planning, OUT / 'scaffold'))
stage('scaffold.write_envelope_content production scope', lambda: production_content(OUT / 'scaffold', OUT / 'content'))
stage('scaffold.content_step', lambda: steps.update(content=scaffold.content_step(
    A, inputs['envelope'], inputs['parts'], BOARD, intent=writer, layout=inputs['layout'],
    antenna_facts=inputs['antenna'], captured_rule_areas=inputs['retention'])) or None)

# 3. Emitter, annotation and planes: owned declarations over the bound projection.
stage('schematic_stage.configuration', lambda: steps.update(schematic=schematic_stage.configuration(
    SRC, board=BOARD, schematic=SCHEMATIC, intent=bound, layout=inputs['layout'], captures='footprints',
    footprints=inputs['footprints'])) or [s['step'] for s in steps['schematic']['implementation_steps']])
stage('add_planes.step', lambda: steps.update(planes=add_planes.step(SRC, board=BOARD, plan=inputs['planes'])) or None)


def declared_imports():
    """Import every declared producer module from its actual mount source, as the step's argv does.

    Each step mounts one source at /tool/agent-ee and puts it on the import path (PYTHONPATH or
    sys.path.insert). The same import runs here in an empty working directory with that source as
    the only path entry (-P: no script directory), and the module must load from inside the mount.
    The export root (the pre-fix declaration) is the control and must fail. Import is not execution."""
    import re
    import subprocess
    import tempfile
    declared = [s for s in (steps.get('fill'), *(steps.get('schematic', {}).get('implementation_steps', [])),
                            steps.get('planes'), steps.get('content')) if s is not None]
    report = {}
    for step in declared:
        mount = next(m for m in step['mounts'] if m['at'] == '/tool/agent-ee')
        argv = step['argv']
        root = ('PYTHONPATH=/tool/agent-ee' in argv or
                any("sys.path.insert(0, '/tool/agent-ee')" in a for a in argv))
        module = (argv[argv.index('-m') + 1] if '-m' in argv else
                  next(re.search(r"run_module\('([^']+)'", a).group(1) for a in argv if 'run_module(' in a))
        source = Path(mount['source']).resolve()

        def load(path):
            with tempfile.TemporaryDirectory() as tmp:
                done = subprocess.run(['/usr/bin/python3', '-B', '-P', '-c',
                                       f'import importlib; print(importlib.import_module({module!r}).__file__)'],
                                      cwd=tmp, capture_output=True, text=True, timeout=300,
                                      env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': str(path), 'HOME': tmp})
            return done.returncode, done.stdout.strip(), done.stderr.strip()[-300:]
        rc, file, err = load(source)
        control = load(A)
        entry = {'module': module, 'mount': str(source), 'import_root_is_mount': root, 'rc': rc,
                 'loaded_from': file, 'within_mount': rc == 0 and Path(file).resolve().is_relative_to(source),
                 'export_root_control_rc': control[0],
                 'export_root_control_error': control[2].splitlines()[-1] if control[2] else ''}
        report[step['step']] = entry
        if not (root and entry['within_mount']):
            raise ValueError(f"{step['step']}: {module} does not load from its mount {source}: rc {rc} {err}")
    return report
stage('producers.import_from_declared_mount', declared_imports)

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

# 5. The plans and the real dry run.
profile = json.loads((A / 'profiles/pod-review.json').read_text())
iter7 = json.loads(ITER7_CAMPAIGN.read_text())
budget = int(iter7['settings']['per_run'][iter7['settings']['per_run'].index('--budget') + 1])
review_budget = sum(r['timeout_s'] for r in profile['reviewers']) + profile['adjudicator']['timeout_s']
adapter = {'schema': 'agent-ee.placement-adapter/1', 'helper': 'agent-ee.placer/1', 'policy': inputs['policy'],
           'fixed_footprints': [], 'timeout_s': PLACEMENT_TIMEOUT_S}
route = {'schema': 'agent-ee.routing-adapter/1', 'project': 'project', 'board': 'telemetry-pod.kicad_pcb',
         'schematic': 'telemetry-pod.kicad_sch', 'name': 'telemetry-pod', 'label': 'campaign',
         'checkout': str(R), 'budget': budget, 'timeout': 2 * budget + 300}
stage('routing_adapter.preflight', lambda: (lambda p: p['problems'] and (_ for _ in ()).throw(
    ValueError('; '.join(p['problems']))) or {k: p[k] for k in ('commit', 'pin')})(routing_adapter.preflight(R)))
implementation = [s for s in (steps.get('fill'), *(steps.get('schematic', {}).get('implementation_steps', [])),
                              steps.get('planes')) if s is not None]
# The probe plan carries no budget fields, so the driver applies its own defaults (max_iterations 10;
# max_seconds its minimum, two routing receipts plus review). It is a preparation probe only.
probe_plan = dict(schema=pod_driver.SCHEMA, scope='scope.json', envelope=inputs['envelope'], parts=inputs['parts'],
                  spec='requirements-map/spec.md', spec_record='requirements-map/spec-record.json',
                  writer_inputs={'intent': writer, 'deviations': inputs['deviations']},
                  implementation_steps=implementation, placement_adapter=adapter, routing_adapter=route,
                  envelope_content={'intent': writer, 'layout': inputs['layout'], 'antenna_facts': inputs['antenna'],
                                    'captured_rule_areas': inputs['retention']},
                  review_profile=profile, implementation=profile['adjudicator'],
                  routing_budget_s=budget, review_budget_s=review_budget)
# The plan of record carries the authorized bound explicitly; it is never raised to the driver floor.
plan = {**probe_plan, 'max_iterations': AUTHORIZED['max_iterations']}
if not AUTHORIZED['placement_timeout_s'][0] <= adapter['timeout_s'] <= AUTHORIZED['placement_timeout_s'][1]:
    raise SystemExit('placement timeout_s outside the authorized 900-1500 s')
(planning / 'plan.json').write_text(text(plan))
(planning / 'plan.probe-driver-defaults.json').write_text(text(probe_plan))
stage('pod_driver.validate_plan bounded plan', lambda: dict(zip(('max_iterations', 'max_seconds'),
                                                                pod_driver.validate_plan(plan))))
stage('pod_driver.validate_plan probe plan (driver defaults)', lambda: dict(zip(
    ('max_iterations', 'max_seconds'), pod_driver.validate_plan(probe_plan))))
stage('pod_driver.build(dry_run) production scope, bounded plan', lambda: {k: v for k, v in pod_driver.build(
    planning / 'plan.json', OUT / 'prepared', dry_run=True).items() if k in ('status', 'done')})
stage('pod_driver.build(dry_run) production scope, probe plan', lambda: {k: v for k, v in pod_driver.build(
    planning / 'plan.probe-driver-defaults.json', OUT / 'prepared-production-probe-plan', dry_run=True).items()
    if k in ('status', 'done')})


def rating_provenance():
    """Which scope lets pod_driver hand the binding-fill --ratings receipt to assembly_readiness."""
    from agent_ee import stage_receipts
    normalized = [stage_receipts.validate_step(s) for s in implementation]
    return {'production scope': pod_driver._rating_provenance(scope, normalized),
            'probe scope (compiled + assembly)': pod_driver._rating_provenance(assembled, normalized),
            'compiled scope as-is': pod_driver._rating_provenance(compiled, normalized),
            'binding_fill_ratings_step': any('--ratings' in s['argv'] for s in normalized if s['step'] == 'binding-fill')}
stage('pod_driver.rating_provenance', rating_provenance)

# PREPARATION PROBE: the compiled scope plus the assembly layer only (no envelope layer). It shows
# which refusal the envelope layer adds and lets preparation run; it is NOT the production scope.
# Its own copy; never an input to the production run.
probe = OUT / 'planning-probe-scope'
shutil.copytree(planning, probe)
(probe / 'composition/scope-composition.json').unlink()
write_scope(probe, assembled)
stage('scaffold.scaffold probe scope', lambda: run_scaffold(probe, OUT / 'scaffold-probe-scope'))
stage('scaffold.write_envelope_content probe scope', lambda: production_content(
    OUT / 'scaffold-probe-scope', OUT / 'content-probe-scope'))
stage('pod_driver.build(dry_run) probe scope, probe plan', lambda: {k: v for k, v in pod_driver.build(
    probe / 'plan.probe-driver-defaults.json', OUT / 'prepared-probe-scope', dry_run=True).items()
    if k in ('status', 'done')})


def review_obligations():
    """The actual review packet of the prepared probe exposes the unresolved block obligations and the ledger.

    Built with agent-ee's own reviewers.build_packet over the dry-run candidate; no model runs. Absence of any
    obligation, of the record bytes, or of the ledger refuses: absence never becomes acceptance."""
    from agent_ee.reviewers import build_packet
    run = OUT / 'prepared-probe-scope/dry-run'
    result = json.loads((run / 'result.json').read_text())
    packet = build_packet(run, result['checks'], result['run_id'])
    candidate = json.loads((run / 'candidate.json').read_text())
    paths = {c['path'] for c in packet['citation_files']}
    record, ledger = 'inputs/' + BLOCK_OBLIGATIONS, 'inputs/' + inputs['ledger']
    limitations = '\n'.join(packet['declared_limitations'])
    ids = [o['id'] for b in obligation_doc['blocks'] for o in b['obligations']]
    missing = [i for i in ids if f'POD-DERIVED-BLOCK-{i.upper()}: NOT CHECKED' not in limitations]
    excerpt = any(a.get('path') == record for a in packet['artifacts'])
    # The driver writes the campaign scope (prepared-probe-scope/scope.json); it owns only inputs and
    # mutable_inputs. Every other field, limitations and packet_inputs included, must be the probe scope's.
    driver_scope = OUT / 'prepared-probe-scope/scope.json'
    ours, theirs = json.loads((probe / 'scope.json').read_text()), json.loads(driver_scope.read_text())
    differ = sorted(k for k in set(ours) | set(theirs) if ours.get(k) != theirs.get(k))
    found = {'candidate_scope_sha256': candidate['scope_sha256'], 'driver_scope_sha256': sha(driver_scope),
             'probe_scope_sha256': sha(probe / 'scope.json'), 'driver_scope_differs_in': differ,
             'candidate_carries_limitations': all(f'POD-DERIVED-BLOCK-{i.upper()}' in l for i in ids
                                                  for l in [' '.join(candidate['scope']['limitations'])]),
             'packet_obligation_limitations': len(ids) - len(missing), 'obligations': len(ids),
             'packet_copper_unknown': 'copper_unknown' in limitations,
             'record_in_citation_files': record in paths,
             'record_bytes_equal': (run / record).read_bytes() == (planning / BLOCK_OBLIGATIONS).read_bytes(),
             'record_in_packet_artifacts': excerpt,
             'ledger_in_citation_files': ledger in paths,
             'ledger_qualification': len(json.loads((run / ledger).read_text())['qualification'])}
    if (missing or not found['packet_copper_unknown'] or not found['record_in_citation_files'] or not excerpt
            or not found['record_bytes_equal'] or not found['candidate_carries_limitations']
            or found['candidate_scope_sha256'] != found['driver_scope_sha256']
            or not set(differ) <= {'inputs', 'mutable_inputs'} or not found['ledger_in_citation_files']
            or found['ledger_qualification'] != 174):
        raise ValueError(f'review packet loses obligations or ledger: missing {missing}; {json.dumps(found)}')
    return found
stage('review.packet_obligations probe scope', review_obligations)


def production_scope_obligations():
    """The production scope (which still refuses preparation) declares the same obligations and packet input."""
    ids = [o['id'] for b in obligation_doc['blocks'] for o in b['obligations']]
    text_ = '\n'.join(scope['limitations'])
    missing = [i for i in ids if f'POD-DERIVED-BLOCK-{i.upper()}: NOT CHECKED' not in text_]
    if missing or BLOCK_OBLIGATIONS not in scope.get('packet_inputs', []):
        raise ValueError(f'production scope omits block obligations {missing}')
    return {'obligations': len(ids), 'packet_inputs': scope['packet_inputs']}
stage('scope.block_obligations production scope', production_scope_obligations)


def authorized_budget():
    """The prepared campaign against the authorized bound. A campaign outside it is set aside unlaunchable."""
    out = OUT / 'prepared-probe-scope'
    receipt = json.loads((out / 'driver-receipt.json').read_text())
    config = json.loads((out / 'campaign.json').read_text())
    held = {'max_iterations': config['max_iterations'], 'max_seconds': config['max_seconds'],
            'placement_timeout_s': config['placement_adapter']['timeout_s'],
            'rating_provenance': config.get('rating_provenance')}
    within = (held['max_iterations'] == AUTHORIZED['max_iterations'] and
              AUTHORIZED['placement_timeout_s'][0] <= held['placement_timeout_s'] <= AUTHORIZED['placement_timeout_s'][1])
    if within:
        return held
    if sha(out / 'campaign.json') != receipt['campaign_sha256']:
        raise ValueError('prepared campaign differs from its driver receipt')
    (out / 'campaign.json').rename(out / 'campaign.NOT-AUTHORIZED.json')
    raise ValueError(f'prepared campaign {json.dumps(held, sort_keys=True)} is outside the authorized bound '
                     f'{json.dumps(AUTHORIZED, sort_keys=True)}; renamed to campaign.NOT-AUTHORIZED.json '
                     f"(sha256 {receipt['campaign_sha256']}, equal to the driver receipt) and not launchable")
stage('campaign.authorized_budget probe scope', authorized_budget)


def block_candidates():
    """The repack gate. 'preparation_not_refused' names the pod_driver.build(dry_run) calls that returned
    status prepared: the scaffold and content receipts ran and the campaign configuration validated. It is
    NOT a native check pass: every dry-run check record is kept verbatim in dry_run_records."""
    cache = ITER8N / 'cand'
    bound_ids = sorted({json.loads(p.read_text())['sources'].get('policy_sha256') for p in cache.glob('*.candidate.json')})
    names = [n for n in stages if n.startswith('pod_driver.build(dry_run)')]
    prepared = [n for n in names if stages[n]['status'] == 'accepted']
    if not prepared:
        raise ValueError(f'{len(list(cache.glob("*.candidate.json")))} iter8n block candidates bind policy {bound_ids}; '
                         f'the derived request policy is {identity(policy)}. The repack waits on a preparation '
                         'that is not refused (none), per the coordinator instruction; nothing was repacked.')
    return {'preparation_not_refused': prepared,
            'meaning': 'pod_driver.build(dry_run) returned status prepared; not a native check pass',
            'preparation_refused': [n for n in names if n not in prepared],
            'iter8n_candidates_bind': bound_ids, 'derived_policy': identity(policy),
            'repack': f'production-capture/repack.py ({REPACK / "repack.json"})',
            'unresolved_obligations': obligation_record['blocks']}
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


result = dict(schema='pod-capture.pipeline/4', done=False, inference=False,
              authority='Producer execution and declarations on a fresh capture copy; no placement, routing, '
                        'campaign or model run. The diagnostic is scratch-only and never an input.',
              agent_ee=str(A), router_checkout=str(R), scope={'path': str(SCOPE_DIR / 'scope.json'),
                                                             'sha256': sha(SCOPE_DIR / 'scope.json')},
              composed_scope_sha256=sha(planning / 'scope.json'), probe_scope_sha256=sha(probe / 'scope.json'),
              scope_composition=derivation, repack={'path': str(REPACK), 'sha256': sha(REPACK / 'repack.json')},
              evaluated_at=EVALUATED_AT,
              plan_sha256=sha(planning / 'plan.json'), probe_plan_sha256=sha(planning / 'plan.probe-driver-defaults.json'),
              derived_request_policy_identity=identity(policy),
              budgets={'authorized': AUTHORIZED, 'plan_of_record': {'max_iterations': plan['max_iterations'],
                                                                    'placement_timeout_s': adapter['timeout_s']},
                       'routing_budget_s': budget, 'routing_timeout_s': route['timeout'], 'review_budget_s': review_budget,
                       'driver_max_seconds_minimum': 2 * (route['timeout'] + routing_adapter.STEP_MARGIN_S) + review_budget},
              stages=stages, diagnostics=diagnostics,
              dry_run_records={'production (bounded plan)': record_of('prepared'),
                               'production (probe plan)': record_of('prepared-production-probe-plan'),
                               'probe scope (probe plan)': record_of('prepared-probe-scope')})
(OUT / 'pipeline.json').write_text(text(result))
