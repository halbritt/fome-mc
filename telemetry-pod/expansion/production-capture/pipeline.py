"""Phase B on the production capture: binding-fill, scaffold, envelope content, emitter and
annotation declarations, the composed production scope, the derived request policy, the real
pod_driver dry run of the bounded two-iteration plan and its receipt (j6/j6b; agent-ee 7d5b0d4d since j6b2).

Every stage runs the owned agent-ee producer on a fresh copy of the capture root; a refusal is
kept verbatim and never substituted. The agent-ee export must be the exact tree of the pinned
commit AGENT_EE_PIN (checked blob by blob against AGENT_EE_GIT before anything runs). The
production scope is composed here from the compiled Rev-3 microSD scope in three layers:

- assembly: one assembly_readiness check over the day-of-generation JLC stock capture, the
  writer-owned deviations, the passive ratings and the J1 hand-fit citation (the declared
  owner_hand_fit chain, verified by the pinned agent-ee before it enters the scope), so the
  binding-fill --ratings receipt reaches the coordinator rating_provenance (AGENTEE-256). Every
  stock capture timestamp is graded against 24 hours at generation; a stale or missing id refuses
  (refresh it, never substitute). Captured bindings are not assembly qualification: POD-AC-5 stays
  NOT CHECKED until the native netlist and check run;
- blocks: the library refusals of the 18-block repack (repack.py block-obligations.json): the pre-6v3
  and buck-3v3 board-region copper/native-check and witness-pose obligations stay unresolved, as NOT
  CHECKED scope limitations and as a packet input, and the actual review packet of the prepared dry
  run is checked to expose them. The expected obligations come from the verified library refusals of
  both pinned library entries, not from the record; any other materialize output refuses. The record's
  seed board and library entries are verified by bytes against their captured iter8n digests, its
  refusals and candidates (schema and block identity included) against the record and repack.json,
  before it is copied (block_obligations). One validator, block_limitation_problems, compares every
  block limitation line of the composition, the candidate, the production scope and the actual packet
  with the canonical source-bound line of each expected obligation (obligation_probes.py);
- envelope: a scope envelope declaration over composition/envelope.json with one check per derived
  envelope obligation (connector-edge/1 for each fixed footprint, outline-containment/1 carrying the
  declared overhangs to the packer), the electrical-locality/1 check over the captured pad obligations
  the packing policy embeds, and the parts_subset membership check the J1 part-identity/1 witness
  reads. The five generic obligations are staged under agent-ee's reviewed source contract
  telemetry-pod-expanded/1 (build.py): candidate generation is admitted, and every open qualification
  item keeps blocking final acceptance (board_envelope.require_final).

The plan selects requirement_source telemetry-pod-rev3, whose pinned capture fome-mc keeps at
requirements/compiled/requirements-map; it is added to the scope as baseline sources
(requirements-source/). Against the pinned baseline the current spec may differ only by the accepted
revision (requirement_revision.py, requirements/rev3-microsd/revision-delta.json; checked here): the added
POD-CD-STORAGE decision row, and the POD-ME-1 cowl correction (owner relay a13a1ba8 v2: ~90 mm provisional
available HEIGHT for the full stack, an owner estimate and not a measured cap), text sha256 d865a76d... ->
09c89ce3... with id/kind/section/cells unchanged, REQUIREMENTS.md dd6555f7..., spec record 21288e01....
Any other difference refuses; the microSD spec itself is not a pinned source and its refusal is kept. The plan of record carries the authorized bound (max_iterations 2, routing backend
budget at most 900 s, placement timeout_s 900-1500 s; ROUTE.md R2): the driver's derived campaign wall
clock is checked never to change the routing budget, timeout or iteration count. There is no
driver-default plan and no compiled-only scope. No placement, routing, campaign or model runs here.

Producer declarations mount the export's src directory (the import root agent_ee's step builders
expect); every declared module is imported from its actual mount source before preparation.

j6b adds native checks on the prepared and emitted candidate (candidate_checks.py), each a stage that refuses on
any deviation: the J1 header STEP and U3 NEO-M9N visualization bound by composition/project-models.json resolve
through agent-ee's own model inventory at ${KIPRJMOD}/inputs/models/ with their recorded poses (FOMEMC-34); the
fab_package copper_features JP1-JP5 are on-board, normally-open copper, not BOM and not DNP, with agent-ee's
fab/parts cross-check kept (agent-509 ruling); the J1 drilling audit is rerun natively (AGENTEE-446); and the
initial candidate identity iteration 1 starts from is recomputed with agent-ee's candidate.capture and recorded
(initial_candidate). model_check.py adds the native STEP export checks on the host.

One clearly labelled DIAGNOSTIC runs on a scratch copy only (it is never an input): the J3
back-side transform.

Usage (fome-mc root, system python with pcbnew, inside the pinned agent-ee CI image):
  AGENT_EE_GIT=AGENT_EE_CHECKOUT AGENT_EE_TOOL_SOURCE_CACHE=/abs/cache /usr/bin/python3 \
      telemetry-pod/expansion/production-capture/pipeline.py \
      AGENT_EE_EXPORT ROUTER_CHECKOUT SCOPE_DIR CAPTURE_ROOT NEW_OUT_DIR [STOCK_CAPTURE_DIR [REPACK_DIR]]
SCOPE_DIR is a compiled Rev-3 scope directory (scope.json plus requirements-map/). STOCK_CAPTURE_DIR is
an agent-ee.jlc-catalog/1 producer capture (catalog.json plus responses/); it defaults to
sources/assembly-stock-20261022. REPACK_DIR is a repack.py output (repack.json, block-obligations.json,
cand/, logs/); it defaults to evidence/repack-a9dac2f-j5. AGENT_EE_GIT is a git checkout holding
AGENT_EE_PIN.
"""
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

A, R, SCOPE_DIR, CAPTURE, OUT = (Path(p).resolve() for p in sys.argv[1:6])
HERE = Path(__file__).resolve().parent
STOCK = Path(sys.argv[6]).resolve() if len(sys.argv) > 6 else HERE / 'sources/assembly-stock-20261023-491b'  # AGENTEE-491: 81 ids + C723587/C861219, one capture
REPACK = Path(sys.argv[7]).resolve() if len(sys.argv) > 7 else HERE / 'evidence/repack-a9dac2f-j5'
# agent-ee main 7d5b0d4d, the AGENTEE-466 qualified runtime (contains the AGENTEE-454 read-once fix, the AGENTEE-450
# router pin b5774496 and everything of the earlier 81e387ee pin): explicitly repinned by agent-449 for the j6b2
# preparation (coordinator decision relaying agent-521 a9cb03ad/2fbe5f08; not owner-stated). The preparation runs in
# that runtime's own image (runtime_receipt.py binds it). 81e387ee (j6, j6b) predates read-once.
AGENT_EE_PIN = '7d5b0d4de65a5b8e8f925ad6f366a46653aae563'


def verify_export(export, git):
    """The export must be exactly the pinned commit's tree: every blob by its git hash, nothing missing or extra."""
    listing = subprocess.run(['git', '-C', str(git), 'ls-tree', '-r', '-z', '--full-tree', AGENT_EE_PIN],
                             capture_output=True, check=True).stdout.split(b'\0')
    expected = {}
    for entry in filter(None, listing):
        meta, path = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind != 'blob':
            raise SystemExit(f'agent-ee {AGENT_EE_PIN} entry {path!r} is a {kind}; refusing')
        expected[path.decode()] = (mode, oid)
    found = {p.relative_to(export).as_posix() for p in export.rglob('*')
             if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts}
    differ = sorted(found ^ set(expected))
    for rel_path, (mode, oid) in expected.items():
        path = export / rel_path
        data = os.readlink(path).encode() if mode == '120000' else path.read_bytes() if path.is_file() else None
        if data is None or hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() != oid:
            differ.append(rel_path)
    if differ:
        raise SystemExit(f'agent-ee export {export} is not the tree of {AGENT_EE_PIN}: {sorted(set(differ))[:20]}')
    tree = subprocess.run(['git', '-C', str(git), 'rev-parse', AGENT_EE_PIN + '^{tree}'], capture_output=True,
                          check=True, text=True).stdout.strip()
    return {'commit': AGENT_EE_PIN, 'tree': tree, 'blobs': len(expected), 'export': str(export)}


AGENT_EE = verify_export(A, Path(os.environ['AGENT_EE_GIT']).resolve())
sys.path[:0] = [str(A / 'src')]
from agent_ee import (add_planes, assembly_readiness, binding_fill, board_envelope,  # noqa: E402
                      placement_adapter, pod_driver, routing_adapter, scaffold, schematic_stage)
from agent_ee.storage import identity  # noqa: E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('candidate_checks', Path(__file__).resolve().parent / 'candidate_checks.py')
candidate_checks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(candidate_checks)

ROOT = HERE.parents[2]
X = ROOT / 'telemetry-pod/expansion'
COMPOSED = HERE / 'composition'
ITER7_CAMPAIGN = X / 'routing-diagnostic/iteration-7/campaign.json'
ITER8N = Path('/home/halbritt/.cache/agent449-pod/iter8n')
BOARD, SCHEMATIC = 'project/telemetry-pod.kicad_pcb', 'project/telemetry-pod.kicad_sch'
LOCALITY = 'telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json'
PROFILE = 'composition/fab-profile.json'  # j6: the production relabel of sources/fab-profile.json (build.py)
CONSTRAINTS = 'telemetry-pod/expansion/design-rules/constraints.json'
CONTAINMENT_LOCATOR = 'D-PCB-13 microSD card envelope in the J3 courtyard (2026-10-21)'
STOCK_AT = 'assembly-stock'
BLOCK_OBLIGATIONS = 'composition/block-obligations.json'
HAND_FIT = HERE / 'assembly/hand-fit-policy.json'
# agent-509 notes/509-j1-handfit-chain.txt: the four chain sources and their recorded SHA-256.
HAND_FIT_CHAIN = {
    'telemetry-pod/REQUIREMENTS.md': 'dd6555f706d163709bccb3417d8c366c38de7d603fca8894d0c4a95a58928208',
    'telemetry-pod/expansion/design-rules/constraints.json': 'e7e095b3ca595fdfb3c73fc22ad87c326fbc1c152523e85f2da4df4d908ea2e4',
    'telemetry-pod/expansion/j1-historical-source/C596198.json': 'f07570cc3502c504acf520e0102dd516f06363589adda81c9c9fb34003641cb5',
    'telemetry-pod/expansion/complete-parts-manifest/parts.json': '759d3be5f3d96bc10b306763559afef94a2d901ccb164bc6a4161f24b662e0ff'}
# The bounded first run (agent-509 ruling 2026-10-22; ROUTE.md R2): two campaign iterations,
# iteration 2 one placement turn with the placement adapter timeout_s between 900 and 1500 s.
# The routing backend budget is at most 900 s (agent-509, 197u decisions); the derived campaign watchdog
# (max_seconds) never expands it, the routing timeout or the iteration count.
AUTHORIZED = {'max_iterations': 2, 'placement_timeout_s': [900, 1500], 'routing_budget_s_max': 900}
# The pinned Revision 3 requirement source (pod_driver.SOURCES) and its capture in fome-mc.
REQUIREMENT_SOURCE = 'telemetry-pod-rev3'
PINNED_SPEC = X / 'requirements/compiled/requirements-map'
REQUIREMENTS_AT = 'requirements-source'
PARTS_REQUIREMENT = 'POD-DERIVED-PARTS-MEMBERSHIP'
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
project.mkdir(exist_ok=True)  # the capture holds project/inputs/models/ (FOMEMC-34, build.py project_models)
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
    # The scope carries the declared citation, which the check validates again at run time; the validator's
    # normalized result (with the reviewed decision fields) is not a check parameter.
    return {'declared': {'path': HAND_FIT.relative_to(ROOT).as_posix(), 'sha256': sha(HAND_FIT)},
            'links': links, 'deviation_identity': deviation['original'], 'agent_ee': export,
            'declared_in_scope': validated is not None}, (copy.deepcopy(declared) if validated is not None else None)


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
    """Verify the repack's obligation record against the retained repack outputs before it is copied or used.

    The expected obligations are not read from the record. Every iter8n library block is expected: its
    captured entry is pinned by bytes, and both are board-region/1 entries, which the pinned engine refuses
    with copper_unknown after admission (block_library.materialize), so no output can exclude a block here.
    Each block's retained materialize output (logs/<block>.library.out) must be a JSON refusal naming its
    block, recorded by repack.json with a nonzero rc for a generic pack; unknown, malformed, missing-status,
    failed or materialized output refuses, whatever path label repack.json gives. For each block exactly two
    obligations are expected, rebuilt from that refusal exactly as repack.py writes them:
    <block>-board-region-copper-native-check and <block>-witness-pose-equivalence, status unresolved. The record
    must hold exactly those (missing, duplicate, substituted, changed, resolved or empty refuses). The retained
    seed board and library entries are read and hashed against their captured iter8n digests (not only the
    record and repack.json); the refusal log and the generic candidate are checked by hash against the record
    and repack.json, and the candidate must be a block candidate for this block, with its library reference,
    bound to the seed board, allocation, netlist and policy repack.json records. The returned record carries the
    canonical NOT CHECKED limitation line of every expected obligation (block_limitation_problems)."""
    library = {'pre-6v3': 'U5', 'buck-3v3': 'U7'}  # repack.py LIBRARY: the iter8n library blocks and references
    # The captured iter8n identities (/home/halbritt/.cache/agent449-pod/iter8n/SHA256SUMS: seed.kicad_pcb,
    # lib/<block>.v4.entry.json, native.xml, allocation.json; the repack copies them unchanged).
    captured = {'seed.kicad_pcb': '0365485efbac76fe77e6810baba0fd15077803289e184d1ff4069773a612907c',
                'pre-6v3.v4.entry.json': '1c913acb67d87af9b2b0e1be57cc6bae9e54b48248138a081f7453dc85a652d9',
                'buck-3v3.v4.entry.json': '146d735c22734a13c2b933a5008307b8c91a841e28aff5099223dd87fa0daa24',
                'native.xml': '7791d44380d40bb46b0dbe1cd7495ce59408e8691afe2bf360eaf70b3eab7556',
                'allocation.json': 'fbda9e28f8cada6fc26b9e9cdb8414650f85e1df8a44a694c82c019fb4e9ad47'}
    generic, real_placement = 'generic pack after library refusal', (
        'A real placement repacks this block against its own emitted board; it inherits neither the iter8n seed '
        'board identity nor any qualification from this candidate.')
    path = REPACK / 'block-obligations.json'
    doc, repack = json.loads(path.read_text()), json.loads((REPACK / 'repack.json').read_text())
    record_sha, seed = sha(path), captured['seed.kicad_pcb']
    iter8n_lib = repack['inputs']['seed.kicad_pcb']['source'].rsplit('/', 1)[0] + '/lib/'

    def refuse(block, why):
        raise SystemExit(f'block obligations for {block}: {why}')

    # H3: the seed board by its retained bytes against the captured digest, before anything is accepted.
    if not (REPACK / 'seed.kicad_pcb').is_file():
        refuse('seed.kicad_pcb', 'the retained seed board is missing; its captured bytes cannot be verified')
    if sha(REPACK / 'seed.kicad_pcb') != seed:
        refuse('seed.kicad_pcb', f'the retained seed board bytes ({sha(REPACK / "seed.kicad_pcb")}) are not the '
                                 f'captured iter8n seed {seed}')
    for name in ('seed.kicad_pcb', 'native.xml', 'allocation.json'):
        if repack['inputs'].get(name, {}).get('sha256') != captured[name]:
            refuse(name, 'repack.json does not record the captured iter8n input')

    refused, refusals = [], {}
    for block in library:
        log = REPACK / f'logs/{block}.library.out'
        if not log.is_file():
            refuse(block, f'the library materialize output {log.name} is missing; the refusal is not source-bound')
        raw = log.read_text()
        try:
            out = json.loads(raw)
        except ValueError:
            out = None
        packed = repack['packed'].get(block, {})
        if not isinstance(out, dict) or out.get('status') != 'refused':
            # H2: no output excludes a library block. A path label cannot establish success, and the pinned
            # board-region/1 entries never materialize at this engine; materialized output is unverifiable here.
            status = out.get('status') if isinstance(out, dict) else 'unknown (not a JSON record)'
            refuse(block, f'the library materialize output is not a verified refusal (status {status!r}, '
                          f'repack.json path {packed.get("path")!r}, rc {packed.get("rc")!r}); its obligations '
                          'cannot be excluded')
        problems = out.get('problems')
        if (out.get('block') != block or out.get('id') != f'pod-{block}' or not isinstance(problems, list) or not problems
                or not all(isinstance(p, dict) and p.get('kind') and p.get('reason') for p in problems)):
            refuse(block, 'the retained library refusal does not name this block with its refusal problems')
        library_run = packed.get('library', {})
        if (packed.get('path') != generic or not library_run.get('rc')
                or library_run.get('stdout') != raw.strip()[-300:]):
            refuse(block, 'repack.json does not record this retained library refusal for a generic pack')
        refused.append(block)
        refusals[block] = {'log': f'logs/{block}.library.out', 'sha256': sha(log), 'rc': library_run['rc'],
                           'status': 'refused', 'problems': problems}
    if refused != list(library) or sorted(refused) != sorted(
            b for b, r in repack['packed'].items() if r.get('path') == generic):
        raise SystemExit(f'library-refused blocks {sorted(refused)} and repack.json generic-after-refusal blocks differ')

    expected = {}
    for block in refused:
        reference, problems = library[block], refusals[block]['problems']
        expected[block] = [
            {'id': f'{block}-board-region-copper-native-check', 'status': 'unresolved',
             'refusal_kinds': sorted({p['kind'] for p in problems}),
             'statement': (f'The {block} library entry ({reference}) was refused by the released engine: '
                           + '; '.join(f'{p["kind"]}: {p["reason"]}' for p in problems)
                           + '. Its board-region copper application and the native checks over it are not '
                             'executed; the generic candidate is geometry only and closes neither.'),
             'source_reasons': [p['reason'] for p in problems]},
            {'id': f'{block}-witness-pose-equivalence', 'status': 'unresolved',
             'statement': (f'Witness-pose equivalence between the generic {block} candidate and the library '
                           'entry witness is not established; the generic pose is not the library pose.')}]

    names = [b.get('block') for b in doc.get('blocks', [])]
    if doc.get('schema') != 'pod-capture.block-obligations/1' or sorted(names) != sorted(expected):
        raise SystemExit(f'block obligation record blocks {names} differ from the library-refused blocks {sorted(expected)}')
    if doc.get('seed_board_sha256') != seed:
        raise SystemExit('block obligation record seed board differs from repack.json')
    for block in doc['blocks']:
        b = block['block']
        ids = [o.get('id') for o in block.get('obligations') or []]
        want = [o['id'] for o in expected[b]]
        if ids != want or block['obligations'] != expected[b]:
            refuse(b, f'obligations {ids} are not exactly the source-bound unresolved {want} '
                      f'(missing {sorted(set(want) - set(ids))}, duplicate {sorted({i for i in ids if ids.count(i) > 1})}, '
                      f'substituted {sorted(set(ids) - set(want))}, or changed status/meaning)')
        if (block.get('status') != 'unresolved' or block.get('qualification') != 'unknown'
                or block.get('reference') != library[b] or block.get('real_placement') != real_placement):
            refuse(b, 'the block is not unresolved/unknown at its library reference; only a native check may resolve it')
        # H2: the cited library entry, at its expected path, by bytes against the record and repack.json.
        entry, name = block.get('library_entry', {}), f'{b}.v4.entry.json'
        if entry.get('path') != name or entry.get('source') != iter8n_lib + name:
            refuse(b, f'library entry {entry.get("path")} ({entry.get("source")}) is not {name} from {iter8n_lib}')
        if not (REPACK / name).is_file():
            refuse(b, f'the retained library entry {name} is missing')
        entry_sha = sha(REPACK / name)
        if (entry_sha != captured[name] or entry_sha != entry.get('sha256')
                or entry_sha != repack['inputs'].get(name, {}).get('sha256')):
            refuse(b, f'library entry {name} bytes ({entry_sha}) are not the captured iter8n entry {captured[name]}, '
                      'or differ from the record or the repack.json input')
        try:
            entry_doc = json.loads((REPACK / name).read_text())
            entry_id, entry_import = entry_doc.get('id'), entry_doc['receipt']['import']
        except (ValueError, AttributeError, KeyError, TypeError):
            entry_id = entry_import = None
        if entry_id != f'pod-{b}' or entry_import != 'board-region/1':
            refuse(b, f'library entry {name} is not the pod-{b} board-region/1 entry ({entry_id}, {entry_import})')
        if block.get('library_refusal') != refusals[b]:
            refuse(b, 'the recorded library refusal differs from the retained refusal output')
        # The generic candidate: expected path, bytes, block, seed board and policy, as repack.json records them.
        cand, rel = block.get('generic_candidate', {}), f'cand/{b}.candidate.json'
        listed = repack['candidates'].get(b, {})
        if cand.get('path') != rel or not (REPACK / rel).is_file():
            refuse(b, f'generic candidate {cand.get("path")} is not the retained {rel}')
        cand_sha = sha(REPACK / rel)
        try:
            cand_doc = json.loads((REPACK / rel).read_text())
            members = {m['reference'] for m in cand_doc['members']}
        except (ValueError, KeyError, TypeError):
            cand_doc, members = {}, set()
        # H3: the candidate's own schema and block identity, not only its digest pointers.
        if (not isinstance(cand_doc, dict) or cand_doc.get('schema') != 'agent-ee.block-candidate/2'
                or cand_doc.get('block_id') != b or library[b] not in members):
            refuse(b, f'generic candidate {rel} is not an agent-ee.block-candidate/2 for block {b} with {library[b]} '
                      f'(block_id {cand_doc.get("block_id") if isinstance(cand_doc, dict) else None})')
        sources = cand_doc.get('sources', {})
        if (sources.get('allocation_sha256') != captured['allocation.json']
                or sources.get('inventory_sha256') != captured['native.xml']):
            refuse(b, 'the generic candidate does not bind the captured iter8n allocation and netlist')
        if (cand_sha != cand.get('sha256') or cand_sha != listed.get('sha256') or listed.get('path') != generic
                or cand_doc.get('status') != cand.get('status') or cand.get('status') != listed.get('status')
                or not {cand.get('board_sha256'), sources.get('board_sha256'), listed.get('board_sha256')} <= {seed}
                or not sources.get('policy_sha256') or sources.get('policy_sha256') != listed.get('policy_sha256')):
            refuse(b, 'the generic candidate differs from the record or repack.json, or binds another board or policy')
        if (listed.get('unresolved_obligations') != [o['id'] for o in expected[b]]
                or listed.get('obligations') != {'path': 'block-obligations.json', 'sha256': record_sha}
                or repack.get('unresolved_obligations', {}).get(b) != [o['id'] for o in expected[b]]):
            refuse(b, 'repack.json does not carry this obligation record and its expected obligations')
    if repack.get('qualified') is not False or sorted(repack.get('unresolved_obligations', {})) != sorted(expected):
        raise SystemExit('repack.json claims qualification or a different unresolved block set')
    policies = sorted({repack['candidates'][b]['policy_sha256'] for b in expected})
    # H1: the canonical limitation line of each expected obligation, rendered from the rebuilt obligation
    # (never the record's text) and bound to the verified record digest; every consumer compares against it.
    canonical = {o['id']: (f"POD-DERIVED-BLOCK-{o['id'].upper()}: NOT CHECKED (unresolved; {BLOCK_OBLIGATIONS} "
                           f"sha256 {record_sha}): {o['statement']} Generic packing is geometry only. {real_placement}")
                 for obligations in expected.values() for o in obligations}
    return doc, {'path': BLOCK_OBLIGATIONS, 'sha256': record_sha,
                 'repack': {'path': str(REPACK / 'repack.json'), 'sha256': sha(REPACK / 'repack.json')},
                 'seed_board_sha256': seed, 'candidate_policy_sha256': policies,
                 'library_entries': {b: sha(REPACK / f'{b}.v4.entry.json') for b in expected},
                 'blocks': {b: [o['id'] for o in obligations] for b, obligations in expected.items()},
                 'limitations': canonical}


def block_obligation_ids():
    """The expected obligation ids, from the verified library-refused block set (never the record's own list)."""
    return [i for ids in obligation_record['blocks'].values() for i in ids]


def block_limitation_problems(lines):
    """The one validator of block limitations, shared by composition, the candidate, the production scope and the
    actual packet. Every line naming a reserved obligation id (any case, any status prefix) is an occurrence of
    it; each expected obligation must occur exactly once, as its canonical source-bound line (same disposition,
    record digest and statement), and no other POD-DERIVED-BLOCK line may exist. 'ok' is false otherwise, and
    when nothing is expected."""
    lines, expected = list(lines), obligation_record['limitations']
    occurrences = {i: [l for l in lines if i.lower() in l.lower()] for i in block_obligation_ids()}
    problems = {'missing': [i for i, found in occurrences.items() if not found],
                'duplicate': [i for i, found in occurrences.items() if len(found) > 1],
                'changed': [i for i, found in occurrences.items() if len(found) == 1 and found[0] != expected[i]],
                'unexpected': [l[:120] for l in lines if 'pod-derived-block' in l.lower()
                               and l not in expected.values()]}
    return {**problems, 'expected': len(expected),
            'ok': bool(expected) and set(expected) == set(occurrences) and not any(problems.values())}


def compose_blocks(base):
    """NOT CHECKED limitations per unresolved obligation, and the record as a review packet input."""
    composed = copy.deepcopy(base)
    canonical = obligation_record['limitations']
    if not canonical or set(canonical) != set(block_obligation_ids()):
        raise ValueError('no canonical limitation for every expected block obligation')
    lines = [canonical[i] for i in block_obligation_ids()]  # rendered from the expected set, never the record text
    composed['limitations'] = [*base['limitations'], *lines]
    composed['packet_inputs'] = [*base.get('packet_inputs', [base['schematic'], base['board']]), BLOCK_OBLIGATIONS]
    problems = block_limitation_problems(composed['limitations'])  # an inherited block line is refused too
    if not problems['ok'] or composed['packet_inputs'].count(BLOCK_OBLIGATIONS) != 1:
        raise ValueError(f'composed scope block limitations differ from the expected obligations: {json.dumps(problems)}')
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
    # Native membership over the captured manifest (agent-ee parts_subset). The J1 part-identity/1 witness of the
    # staged harness-edge obligation is bound only through this check (board_envelope.identity_witness); its
    # requirement points at the manifest's captured declaration source, as parts_subset requires.
    manifest = read(inputs['parts'])
    parts_check = dict(id='parts', kind='parts_subset', stage='schematic',
                       params=dict(manifest=inputs['parts'], netlist_check='netlist', requirement_id=PARTS_REQUIREMENT))
    requirements.append({'id': PARTS_REQUIREMENT, 'intent': 'acceptance',
                         'statement': ('Every populated purchased instance matches its declared symbol, footprint and '
                                       f"supplier identity in {inputs['parts']}, and every required reference is present "
                                       '(captured membership, not approval or suitability).'),
                         'source': {k: manifest['declaration_source'][k] for k in ('path', 'locator')}, 'checks': ['parts']})
    # The radio-antenna keepout's legacy ESP32 declaration names an earlier datasheet_facts check
    # (antenna.facts_check); agent-ee grades that dynamic keepout unknown, never pass (board-envelope.md).
    facts_checks = sorted({k['antenna']['facts_check'] for k in record['keepouts'] if 'antenna' in k})
    if facts_checks != ['antenna-facts']:
        raise ValueError(f'expected the one antenna facts check, found {facts_checks}')
    extractor = read(inputs['ratings'])['extractor']  # the pinned pdftotext the rating facts already declare
    facts_check = dict(id='antenna-facts', kind='datasheet_facts', stage='schematic',
                       params=dict(facts=inputs['antenna'], extractor=extractor))
    # Informational: citation occurrence is no acceptance predicate (agent-ee datasheet_facts).
    requirements.append({'id': 'POD-DERIVED-ANTENNA-FACTS', 'intent': 'informational',
                         'statement': (f"The ESP32-S3-WROOM-1 datasheet facts of {inputs['antenna']} occur verbatim on "
                                       'their cited pages (text occurrence only, not applicability or clearance).'),
                         'source': {'path': inputs['antenna'], 'locator': '/facts'}, 'checks': ['antenna-facts']})
    checks = list(base['checks'])
    if any(c['id'] in ('parts', 'antenna-facts') for c in checks):
        raise ValueError('the compiled scope already declares a parts or antenna-facts check')
    at = next(i for i, c in enumerate(checks) if c['id'] == 'netlist') + 1
    checks[at:at] = [parts_check, facts_check]
    # With a parts manifest in the scope, the fab_package done check must declare exactly its on-board copper
    # features and admit its bare-copper probes from the same manifest (agent-ee copper_features and
    # probe_features); binding-fill marks the J1 owner_hand_fit part JLCPCB_Assembly=not_assembled, which the
    # export honours only under the declared assembly_exclusion rule. Declarations, not acceptance.
    done = base['generation']['done_check']
    fab = next(c for c in checks if c['id'] == done)
    copper = sorted(i['reference'] for x in manifest['parts'] if x.get('kind') == 'copper_feature' for i in x['instances'])
    probes = sorted(i['reference'] for x in manifest['parts'] if x.get('kind') == 'bare_copper_probe' for i in x['instances'])
    hand_fit = sorted({(d['original']['mpn'], d['original']['lcsc']) for d in read(inputs['deviations'])['deviations']
                       if d.get('assembly') == 'hand_soldered'})
    hand_fit_refs = sorted(i['reference'] for x in manifest['parts'] if (x.get('mpn'), x.get('lcsc')) in hand_fit
                           for i in x['instances'])
    if hand_fit_refs != ['J1']:
        raise ValueError(f'expected J1 as the only hand-soldered part, found {hand_fit_refs}')
    if set(fab['params']) != {'netlist_check'} or not copper or not probes:
        raise ValueError(f"unexpected fab_package params {fab['params']} or empty copper/probe declarations")
    checks[checks.index(fab)] = {**fab, 'params': {**fab['params'], 'copper_features': copper,
                                                   'probe_manifest': inputs['parts'],
                                                   'assembly_exclusion': 'JLCPCB_Assembly=not_assembled'}}
    fab_declarations = {'copper_features': copper, 'probes': probes, 'probe_manifest': inputs['parts'],
                        'assembly_exclusion': 'JLCPCB_Assembly=not_assembled', 'hand_fit_deviation_references': hand_fit_refs}
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
        'obligation, the electrical-locality check and the parts membership check. The five generic envelope '
        'obligations are staged under agent-ee source contract telemetry-pod-expanded/1: candidate generation is '
        'admitted and every open qualification item (enclosure and harness fit among them, open design '
        'deliverables) keeps blocking final acceptance. Structural envelope validity is not mechanical '
        'qualification.']
    derivation = {'schema': 'pod-capture.scope-composition/1',
                  'base': {'path': str(SCOPE_DIR / 'scope.json'), 'sha256': sha(SCOPE_DIR / 'scope.json')},
                  'envelope': {'path': env, 'sha256': files[env], 'envelope_id': record['envelope_id'],
                               'complete': derived['complete'], 'unresolved': derived['unresolved']},
                  'added_checks': ['parts', 'antenna-facts', *(c['id'] for c in placement + routing)],
                  'added_requirements': [r['id'] for r in requirements], 'unmapped': unmapped,
                  'fab_package_declarations': fab_declarations}
    return composed, derivation, (derived, record, files)


def compose_requirement_source(base):
    """The pinned Revision 3 source the plan selects, added as immutable baseline sources of the scope.

    The pod driver binds the campaign baseline to a pinned registry source (pod_driver.SOURCES); the microSD
    spec the scope is compiled from is not one. The pinned capture (fome-mc requirements/compiled) must equal
    the registry pins (the historical telemetry-pod-rev3 source is kept unchanged). The microSD spec may differ from it
    ONLY by the explicit accepted revision delta in requirement_revision.py (AGENTEE-488c): the adopted POD-CD-STORAGE
    addition and the exact accepted POD-ME-1 height-estimate correction, bound to the accepted REQUIREMENTS.md and
    spec-record identities. Anything else refuses. The microSD spec's own refusal is kept verbatim."""
    from agent_ee.spec_record import sha256 as record_digest, verify
    rule = pod_driver.SOURCES[REQUIREMENT_SOURCE]
    (planning / REQUIREMENTS_AT).mkdir()
    for name in ('spec.md', 'spec-record.json'):
        shutil.copyfile(PINNED_SPEC / name, planning / REQUIREMENTS_AT / name)
    spec_rel, record_rel = REQUIREMENTS_AT + '/spec.md', REQUIREMENTS_AT + '/spec-record.json'
    if (sha(planning / spec_rel), sha(planning / record_rel)) != (rule['spec_sha256'], rule['record_sha256']):
        raise SystemExit(f'{PINNED_SPEC} is not the pinned {REQUIREMENT_SOURCE} capture')
    pinned = verify((planning / record_rel).read_bytes(), (planning / spec_rel).read_bytes())
    current_raw = (planning / 'requirements-map/spec-record.json').read_bytes()
    current = verify(current_raw, (planning / 'requirements-map/spec.md').read_bytes())

    def entries(doc):
        return {r['id']: {k: v for k, v in r.items() if k != 'locator'} for r in doc['requirements']}
    a, b = entries(pinned), entries(current)
    prose = sorted({p['id'] for p in pinned['prose']} ^ {p['id'] for p in current['prose']} | {
        p['id'] for p in pinned['prose'] for q in current['prose'] if p['id'] == q['id'] and p['text'] != q['text']})
    delta = {'added': sorted(set(b) - set(a)), 'removed': sorted(set(a) - set(b)),
             'changed': sorted(i for i in set(a) & set(b) if a[i] != b[i]), 'prose_differ': prose,
             'acceptance_equal': sorted(i for i, r in a.items() if r['kind'] == 'acceptance') ==
                                 sorted(i for i, r in b.items() if r['kind'] == 'acceptance')}
    _rs = importlib.util.spec_from_file_location('requirement_revision', Path(__file__).resolve().parent / 'requirement_revision.py')
    revision = importlib.util.module_from_spec(_rs)
    _rs.loader.exec_module(revision)
    refused = revision.problems(pinned, current, sha(planning / 'requirements-map/spec.md'), sha(planning / 'requirements-map/spec-record.json'))
    if refused:
        raise SystemExit(f'the microSD spec differs from {REQUIREMENT_SOURCE} beyond the accepted revision delta: {refused}; {delta}')
    try:
        pod_driver.requirement_set(REQUIREMENT_SOURCE, current, record_digest(current_raw), base)
        microsd = {'status': 'accepted'}
    except ValueError as exc:  # kept verbatim: the microSD spec is not a pinned source
        microsd = {'status': 'refused', 'reason': getattr(exc, 'reason', None), 'error': f'{type(exc).__name__}: {exc}'}
    composed = copy.deepcopy(base)
    composed['baseline']['reference_architectures'] = [*base['baseline']['reference_architectures'], spec_rel]
    composed['baseline']['targets'] = [*base['baseline']['targets'], record_rel]
    composed['limitations'] = [*base['limitations'],
        f'Composed by production-capture/pipeline.py: the plan selects requirement_source {REQUIREMENT_SOURCE}, the '
        f'pinned Revision 3 capture ({spec_rel} sha256 {rule["spec_sha256"]}, {record_rel} sha256 '
        f'{rule["record_sha256"]}). The scope is compiled from the microSD spec (requirements-map/spec.md sha256 '
        f'{sha(planning / "requirements-map/spec.md")}), which differs from it ONLY by the explicit accepted revision '
        'delta (requirement_revision.py): the adopted POD-CD-STORAGE decision row and the accepted POD-ME-1 height-'
        'ESTIMATE correction (owner-relayed a13a1ba8@2, accepted AGENTEE-486 / 27c51f73; not a measured 90 mm cap). '
        'The current POD-ME-1 text is the governing mechanical obligation; the same ID transfers no earlier acceptance. '
        'The microSD spec is not a pinned source. Carrying every criterion is not acceptance.']
    return composed, {'source': REQUIREMENT_SOURCE, 'spec': {'path': spec_rel, 'sha256': rule['spec_sha256']},
                      'record': {'path': record_rel, 'sha256': rule['record_sha256']},
                      'captured_from': PINNED_SPEC.relative_to(ROOT).as_posix(),
                      'scope_spec': {'path': 'requirements-map/spec.md', 'sha256': sha(planning / 'requirements-map/spec.md'),
                                     'record_sha256': hashlib.sha256(current_raw).hexdigest()},
                      'delta': delta, 'microsd_spec_as_source': microsd}


def write_scope(root, base):
    scope_ = {**base, 'inputs': [{'path': p.name, 'at': p.name} for p in sorted(root.iterdir()) if p.name != 'scope.json']}
    (root / 'scope.json').write_text(text(scope_))
    return scope_


coverage = stock_coverage()
# Day-of-generation stock (POD-AC-5): each id's own capture time against 24 hours, now. A stale, missing or
# unobserved id refuses before composition; it is refreshed (read-only capture), never substituted.
_unusable = sorted((i for i, r in coverage['per_id'].items() if r['stale'] or r['status'] in ('unobserved', 'failed')),
                   key=lambda c: int(c[1:]))
if _unusable:
    raise SystemExit(f'stock capture needs a refresh for {_unusable} (older than 24 h at {EVALUATED_AT}, or not '
                     'observed); no generation on stale stock')
hand_fit, hand_fit_policy = hand_fit_chain()
if hand_fit_policy is None:
    raise SystemExit(f"the pinned agent-ee refuses the J1 hand-fit chain: {hand_fit['agent_ee']}")
obligation_doc, obligation_record = block_obligations()
# Copied only after verification; the copy, the derived request policy and the repack policy input must agree.
shutil.copyfile(REPACK / 'block-obligations.json', planning / BLOCK_OBLIGATIONS)
if sha(planning / BLOCK_OBLIGATIONS) != obligation_record['sha256']:
    raise SystemExit('the copied block obligation record differs from the verified record')
repack_policy = json.loads((REPACK / 'repack.json').read_text())['inputs']['policy']['sha256']
if (repack_policy != sha(planning / inputs['policy'])
        or set(obligation_record['candidate_policy_sha256']) - {identity(read(inputs['policy']))}):
    raise SystemExit('the repack policy input or the refused-block candidates do not bind the derived request policy')
assembled = compose_blocks(compose_assembly(compiled))
composed, derivation, coverage_inputs = compose_scope(assembled)
composed, requirement_source = compose_requirement_source(composed)
derivation = {**derivation, 'schema': 'pod-capture.scope-composition/4',
              'layers': ['assembly', 'blocks', 'envelope', 'requirement-source'],
              'requirement_source': requirement_source, 'added_checks': ['assembly', *derivation['added_checks']],
              'added_requirements': ['POD-DERIVED-AC-5-ASSEMBLY', *derivation['added_requirements']],
              'assembly': {'check': next(c for c in assembled['checks'] if c['id'] == 'assembly'),
                           'stock': coverage, 'hand_fit': hand_fit},
              'blocks': obligation_record}
(planning / 'composition/scope-composition.json').write_text(text(derivation))
scope = write_scope(planning, composed)


def obligations():
    derived, record, _ = coverage_inputs
    files = {p.relative_to(planning).as_posix(): sha(p) for p in planning.rglob('*') if p.is_file()}
    report = board_envelope.obligation_coverage(scope, derived, record, files, planning)
    short = lambda r: r['id'].split(record['envelope_id'] + '-', 1)[1]  # noqa: E731
    summary = {s: sorted(short(r) for r in report if r['status'] == s) for s in sorted({r['status'] for r in report})}
    reasons = {short(r): r['reason'] for r in report if r['status'] not in ('bound',)}
    # Generation admission (bound, soft or staged), exactly the agent-ee require_obligations rule.
    if any(r['status'] not in ('bound', 'soft', 'staged') for r in report) or not derived['complete']:
        raise ValueError(f'envelope obligations not all admitted: {json.dumps(summary)}; reasons {json.dumps(reasons)}; '
                         f"complete={derived['complete']} unresolved={derived['unresolved']}")
    staged = {short(r): {'witnesses': [{k: w.get(k) for k in ('locator', 'criterion', 'requirement', 'checks', 'status')}
                                       for w in r['witnesses']], 'open': [e['id'] for e in r['open']]}
              for r in report if r['status'] == 'staged'}
    if sorted(staged) != sorted(f'obligation-{o}' for o in
                                ('corner-holes', 'height', 'harness-edge', 'antenna', 'imu-separation')):
        raise ValueError(f'expected the five contracted obligations staged, found {sorted(staged)}')
    try:  # final physical qualification must refuse while any open item stands; it is never closed here
        board_envelope.require_qualified(report)
        final = {'status': 'accepted'}
    except ValueError as exc:
        final = {'status': 'refused (expected: open qualification items)', 'error': str(exc)}
    if final['status'] == 'accepted':
        raise ValueError('final qualification unexpectedly accepted with staged obligations')
    return {'summary': summary, 'staged': staged, 'final_qualification': final,
            'qualification_open': len(derived.get('qualification_open', []))}
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
# captures is the candidate root: the bound intent's library paths (symbols/, core/symbols/, authored-cad/,
# libraries/) and footprints.json members (footprints/...) are root-relative. The pre-j6 'footprints' made
# emit-schematic fail with resolution_library_coverage on every library (found by the j6 emission stage).
stage('schematic_stage.configuration', lambda: steps.update(schematic=schematic_stage.configuration(
    SRC, board=BOARD, schematic=SCHEMATIC, intent=bound, layout=inputs['layout'], captures='.',
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

# 5. The plan of record and the real dry run (no driver-default plan, no compiled-only scope).
profile = json.loads((A / 'profiles/pod-review.json').read_text())
iter7 = json.loads(ITER7_CAMPAIGN.read_text())
budget = int(iter7['settings']['per_run'][iter7['settings']['per_run'].index('--budget') + 1])
if not 1 <= budget <= AUTHORIZED['routing_budget_s_max']:
    raise SystemExit(f"routing backend budget {budget} s exceeds the authorized {AUTHORIZED['routing_budget_s_max']} s")
review_budget = sum(r['timeout_s'] for r in profile['reviewers']) + profile['adjudicator']['timeout_s']
adapter = {'schema': 'agent-ee.placement-adapter/1', 'helper': 'agent-ee.placer/1', 'policy': inputs['policy'],
           'fixed_footprints': [], 'timeout_s': PLACEMENT_TIMEOUT_S}
route = {'schema': 'agent-ee.routing-adapter/1', 'project': 'project', 'board': 'telemetry-pod.kicad_pcb',
         'schematic': 'telemetry-pod.kicad_sch', 'name': 'telemetry-pod', 'label': 'campaign',
         'checkout': str(R), 'budget': budget, 'timeout': 2 * budget + 300}
# The pinned agent-ee's preflight of ROUTER_CHECKOUT (the image's own /opt/kicad-route when run as runtime_receipt.py
# records). The image, router source/extension/interpreter identities and the exact invocation are bound by the
# separate immutable receipt (runtime_receipt.py); this stage alone qualifies nothing.
stage('routing_adapter.preflight (agent-ee 7d5b0d4d, ROUTER_CHECKOUT)',
      lambda: (lambda p: p['problems'] and (_ for _ in ()).throw(ValueError('; '.join(p['problems']))) or
               {k: p[k] for k in ('commit', 'pin', 'checkout')})(routing_adapter.preflight(R)))
implementation = [s for s in (steps.get('fill'), *(steps.get('schematic', {}).get('implementation_steps', [])),
                              steps.get('planes')) if s is not None]
if not AUTHORIZED['placement_timeout_s'][0] <= adapter['timeout_s'] <= AUTHORIZED['placement_timeout_s'][1]:
    raise SystemExit('placement timeout_s outside the authorized 900-1500 s')
# The bound is explicit; max_seconds is left to the driver's derivation (two routing receipts plus review).
plan = dict(schema=pod_driver.SCHEMA, scope='scope.json', envelope=inputs['envelope'], parts=inputs['parts'],
            spec=REQUIREMENTS_AT + '/spec.md', spec_record=REQUIREMENTS_AT + '/spec-record.json',
            requirement_source=REQUIREMENT_SOURCE,
            writer_inputs={'intent': writer, 'deviations': inputs['deviations']},
            implementation_steps=implementation, placement_adapter=adapter, routing_adapter=route,
            envelope_content={'intent': writer, 'layout': inputs['layout'], 'antenna_facts': inputs['antenna'],
                              'captured_rule_areas': inputs['retention']},
            review_profile=profile, implementation=profile['adjudicator'],
            routing_budget_s=budget, review_budget_s=review_budget, max_iterations=AUTHORIZED['max_iterations'])
(planning / 'plan.json').write_text(text(plan))
stage('pod_driver.validate_plan', lambda: dict(zip(('max_iterations', 'max_seconds'), pod_driver.validate_plan(plan))))
PREPARED = 'prepared'
stage('pod_driver.build(dry_run) production scope', lambda: {k: v for k, v in pod_driver.build(
    planning / 'plan.json', OUT / PREPARED, dry_run=True).items() if k in ('status', 'done')})


def rating_provenance():
    """pod_driver hands the binding-fill --ratings receipt to assembly_readiness on the production scope."""
    from agent_ee import stage_receipts
    normalized = [stage_receipts.validate_step(s) for s in implementation]
    found = {'production scope': pod_driver._rating_provenance(scope, normalized),
             'binding_fill_ratings_step': any('--ratings' in s['argv'] for s in normalized if s['step'] == 'binding-fill')}
    if found['production scope'] is None or not found['binding_fill_ratings_step']:
        raise ValueError(f'rating provenance does not reach the assembly check: {found}')
    return found
stage('pod_driver.rating_provenance', rating_provenance)


def receipt_budget():
    """The prepared campaign and its driver receipt against the authorized bound (never edited, never raised)."""
    out = OUT / PREPARED
    receipt = json.loads((out / 'driver-receipt.json').read_text())
    config = json.loads((out / 'campaign.json').read_text())
    if sha(out / 'campaign.json') != receipt['campaign_sha256']:
        raise ValueError('prepared campaign differs from its driver receipt')
    derivation = receipt['budget_derivation']
    route_step = config['routing_adapter'] if 'routing_adapter' in config else None
    held = {'max_iterations': config['max_iterations'], 'max_seconds': config['max_seconds'],
            'placement_timeout_s': config['placement_adapter']['timeout_s'],
            'routing_budget_s': derivation['routing']['budget_s'], 'routing_timeout_s': derivation['routing']['timeout_s'],
            'routing_step_margin_s': derivation['routing']['step_margin_s'],
            'review_budget_s': derivation['review_budget_s'],
            'max_iterations_source': derivation['max_iterations']['source'],
            'max_seconds_source': derivation['max_seconds']['source'],
            'max_seconds_minimum_s': derivation['max_seconds']['minimum_s'],
            'rating_provenance': config.get('rating_provenance'),
            'requirement_set': {k: receipt['validation']['requirement_set'][k]
                                for k in ('source', 'revision', 'spec_sha256', 'record_sha256', 'bench')}}
    problems = []
    if held['max_iterations'] != AUTHORIZED['max_iterations'] or held['max_iterations_source'] != 'plan':
        problems.append('max_iterations is not the plan bound 2')
    if not AUTHORIZED['placement_timeout_s'][0] <= held['placement_timeout_s'] <= AUTHORIZED['placement_timeout_s'][1]:
        problems.append('placement timeout outside 900-1500 s')
    if held['routing_budget_s'] != budget or budget > AUTHORIZED['routing_budget_s_max']:
        problems.append('routing backend budget is not the declared one within 900 s')
    if held['routing_timeout_s'] != 2 * budget + 300:
        problems.append('routing timeout is not 2 x budget + 300 s')
    # The watchdog is derived from the routing and review budgets and changes none of them.
    if (held['max_seconds_source'] != 'derived' or held['max_seconds'] != held['max_seconds_minimum_s'] or
            held['max_seconds'] != 2 * (held['routing_timeout_s'] + held['routing_step_margin_s']) + held['review_budget_s']):
        problems.append('max_seconds is not the derived watchdog')
    if held['requirement_set']['source'] != REQUIREMENT_SOURCE or held['rating_provenance'] is None:
        problems.append('requirement source or rating provenance missing from the prepared campaign')
    if problems:
        raise ValueError(f'prepared campaign {json.dumps(held, sort_keys=True)} is outside the authorized bound '
                         f'{json.dumps(AUTHORIZED, sort_keys=True)}: {problems}')
    return {**held, 'campaign_sha256': receipt['campaign_sha256'], 'driver_receipt_sha256': sha(out / 'driver-receipt.json'),
            'routing_adapter_in_campaign': route_step is not None}
stage('campaign.authorized_budget production scope', receipt_budget)


EMISSION = 'emission'


def emit_schematic():
    """AGENTEE-445: native emission and forward annotation of the production pod from its bound intent.

    The prepared campaign's own schematic-stage implementation steps (binding-fill --ratings, emit-schematic,
    forward-annotate) run in order through agent-ee's stage receipts on a copy of the prepared candidate, each
    adopted only on its declared exit; no placement, routing, campaign iteration or model runs. The emitted
    schematic and annotated board (fixed footprints posed by the envelope content, the rest unplaced) are the
    re-emission AGENTEE-445 asks for; the receipts bind every input and output by sha256."""
    from agent_ee import stage_receipts
    prepared = OUT / PREPARED
    config = json.loads((prepared / 'campaign.json').read_text())
    candidate = json.loads((prepared / 'dry-run/candidate.json').read_text())
    specs = [s for s in config['implementation_steps'] if s['stage'] == 'schematic']
    if [s['step'] for s in specs] != ['binding-fill', 'emit-schematic', 'forward-annotate']:
        raise ValueError(f"unexpected schematic-stage steps {[s['step'] for s in specs]}")
    design = OUT / EMISSION / 'design'
    shutil.copytree(prepared / 'inputs', design)
    before = stage_receipts.file_tree(design)[0]
    receipts = []
    for k, spec in enumerate(specs, 1):
        receipt_dir = OUT / EMISSION / 'receipts' / f"{k}-{spec['step']}"
        binding = {'emission': 'AGENTEE-445', 'source_candidate_id': candidate['candidate_id'], 'receipt_index': k}
        receipt = stage_receipts.run_step(receipt_dir, design, spec, binding)
        stage_receipts.adopt(receipt_dir, receipt, design)
        receipts.append({'step': spec['step'], 'receipt': receipt_dir.relative_to(OUT).as_posix(),
                         'receipt_sha256': sha(receipt_dir / 'receipt.json'), 'spec_sha256': receipt['spec_sha256'],
                         'exit': (receipt.get('execution') or {}).get('exit_code', receipt.get('status'))})
    after = stage_receipts.file_tree(design)[0]
    changed = sorted(p for p in after if before.get(p) != after[p])
    netlist = OUT / EMISSION / 'native.xml'
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(netlist),
                    str(design / scope['schematic'])], check=True, capture_output=True)
    from agent_ee.native_netlist import read_native_inventory
    native = read_native_inventory(netlist)
    refs = sorted(native['components'])
    expected = sorted(scope['stages']['subjects']['schematic']['references'])
    if refs != expected:
        raise ValueError(f'emitted schematic references differ from the 305 subjects: '
                         f'missing {sorted(set(expected) - set(refs))[:10]}, extra {sorted(set(refs) - set(expected))[:10]}')
    return {'candidate_id': candidate['candidate_id'], 'receipts': receipts, 'changed': changed,
            'schematic': {'path': scope['schematic'], 'sha256': after[scope['schematic']]},
            'board': {'path': scope['board'], 'sha256': after[scope['board']]},
            'native_components': len(refs), 'native_nets': len(native.get('nets', {})),
            'intent': {'path': bound, 'sha256': after.get(bound)}}
stage('emission.schematic_stage production (AGENTEE-445)', emit_schematic)
MODELS = 'composition/project-models.json'


def candidate_models():
    """FOMEMC-34: the initial (scaffold) and emitted candidate boards resolve the bound J1 and U3 models."""
    record = read(MODELS)
    prepared, design = OUT / PREPARED / 'inputs', OUT / EMISSION / 'design'
    for root in (prepared, design):
        for m in record['models']:
            if sha(root / m['candidate']['path']) != m['candidate']['sha256'] or sha(root / m['member']['path']) != m['member']['sha256']:
                raise ValueError(f"{root.name}: {m['reference']} model or footprint member differs from {MODELS}")
    return {'record': {'path': MODELS, 'sha256': sha(planning / MODELS)},
            'initial_board': candidate_checks.model_resolution(prepared / scope['board'], record, ('J1',)),
            'emitted_board': candidate_checks.model_resolution(design / scope['board'], record),
            'emitted_native_pose': candidate_checks.native_pose(design / scope['board'], record),
            'not_bound': record['not_bound'], 'open': record['open']}
stage('models.candidate_resolution (FOMEMC-34)', candidate_models)


def copper_contract():
    """agent-509 JP1-JP5 ruling on the prepared scope and the emitted native design."""
    prepared_scope = json.loads((OUT / PREPARED / 'scope.json').read_text())
    files = json.loads((OUT / PREPARED / 'dry-run/candidate.json').read_text())['files']
    return candidate_checks.copper_features(OUT / EMISSION / 'design', prepared_scope, files, inputs['parts'],
                                            scope['board'], scope['schematic'], OUT / EMISSION / 'native.xml')
stage('fab.copper_features JP1-JP5 (agent-509 ruling)', copper_contract)
stage('j1.native_inspection (agent-509 iter8t audit, AGENTEE-446)',
      lambda: candidate_checks.j1_inspection(OUT / EMISSION / 'design' / scope['board']))
stage('campaign.initial_candidate', lambda: candidate_checks.initial_candidate(
    OUT / PREPARED, OUT / PREPARED / 'dry-run/candidate.json'))


def review_obligations():
    """The actual review packet of the prepared dry run exposes the unresolved block obligations and the ledger.

    Built with agent-ee's own reviewers.build_packet over the dry-run candidate; no model runs. Absence of any
    obligation, of the record bytes, or of the ledger refuses: absence never becomes acceptance."""
    from agent_ee.reviewers import build_packet
    run = OUT / PREPARED / 'dry-run'
    result = json.loads((run / 'result.json').read_text())
    packet = build_packet(run, result['checks'], result['run_id'])
    candidate = json.loads((run / 'candidate.json').read_text())
    paths = {c['path'] for c in packet['citation_files']}
    record, ledger = 'inputs/' + BLOCK_OBLIGATIONS, 'inputs/' + inputs['ledger']
    limitations = '\n'.join(packet['declared_limitations'])
    ids = block_obligation_ids()  # expected from the verified library-refused blocks, not the record's list
    in_packet = block_limitation_problems(packet['declared_limitations'])
    in_candidate = block_limitation_problems(candidate['scope']['limitations'])
    missing = sorted({*in_packet['missing'], *in_packet['changed']})  # an expected line not present canonically
    excerpt = any(a.get('path') == record for a in packet['artifacts'])
    # The driver writes the campaign scope (<prepared>/scope.json); it owns only inputs and mutable_inputs.
    # Every other field, limitations and packet_inputs included, must be the production scope's.
    driver_scope = OUT / PREPARED / 'scope.json'
    ours, theirs = json.loads((planning / 'scope.json').read_text()), json.loads(driver_scope.read_text())
    differ = sorted(k for k in set(ours) | set(theirs) if ours.get(k) != theirs.get(k))
    found = {'candidate_scope_sha256': candidate['scope_sha256'], 'driver_scope_sha256': sha(driver_scope),
             'production_scope_sha256': sha(planning / 'scope.json'), 'driver_scope_differs_in': differ,
             'candidate_carries_limitations': in_candidate['ok'],
             'candidate_block_limitations': in_candidate, 'packet_block_limitations': in_packet,
             'packet_obligation_limitations': len(ids) - len(missing), 'obligations': len(ids),
             'expected_obligations': obligation_record['blocks'],
             'packet_copper_unknown': 'copper_unknown' in limitations,
             'record_in_citation_files': record in paths,
             'record_bytes_equal': ((run / record).read_bytes() == (planning / BLOCK_OBLIGATIONS).read_bytes()
                                    and sha(run / record) == obligation_record['sha256']),
             'record_in_packet_artifacts': excerpt,
             'ledger_in_citation_files': ledger in paths,
             'ledger_qualification': len(json.loads((run / ledger).read_text())['qualification'])}
    if (not in_packet['ok'] or not ids or not found['packet_copper_unknown'] or not found['record_in_citation_files'] or not excerpt
            or not found['record_bytes_equal'] or not found['candidate_carries_limitations']
            or found['candidate_scope_sha256'] != found['driver_scope_sha256']
            or not set(differ) <= {'inputs', 'mutable_inputs'} or not found['ledger_in_citation_files']
            or found['ledger_qualification'] != 174):
        raise ValueError(f'review packet loses obligations or ledger: missing {missing}; {json.dumps(found)}')
    return found
stage('review.packet_obligations production scope', review_obligations)


def production_scope_obligations():
    """The production scope (which still refuses preparation) declares the same obligations and packet input."""
    ids = block_obligation_ids()  # expected from the verified library-refused blocks, not the record's list
    found = block_limitation_problems(scope['limitations'])
    if not ids or not found['ok'] or scope.get('packet_inputs', []).count(BLOCK_OBLIGATIONS) != 1:
        raise ValueError(f'production scope block obligations differ from the expected set: {json.dumps(found)}')
    return {'obligations': len(ids), 'expected_obligations': obligation_record['blocks'],
            'packet_inputs': scope['packet_inputs']}
stage('scope.block_obligations production scope', production_scope_obligations)




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


result = dict(schema='pod-capture.pipeline/6', done=False, inference=False,
              authority='Producer execution and declarations on a fresh capture copy and the real pod_driver dry run '
                        'of the bounded plan; no placement, routing, campaign or model run. The diagnostic is '
                        'scratch-only and never an input.',
              agent_ee=AGENT_EE, router_checkout=str(R), scope={'path': str(SCOPE_DIR / 'scope.json'),
                                                                'sha256': sha(SCOPE_DIR / 'scope.json')},
              composed_scope_sha256=sha(planning / 'scope.json'),
              scope_composition=derivation, repack={'path': str(REPACK), 'sha256': sha(REPACK / 'repack.json')},
              evaluated_at=EVALUATED_AT, plan_sha256=sha(planning / 'plan.json'),
              derived_request_policy_identity=identity(policy),
              budgets={'authorized': AUTHORIZED, 'plan_of_record': {'max_iterations': plan['max_iterations'],
                                                                    'placement_timeout_s': adapter['timeout_s'],
                                                                    'routing_budget_s': budget},
                       'routing_timeout_s': route['timeout'], 'review_budget_s': review_budget,
                       'driver_max_seconds_minimum': 2 * (route['timeout'] + routing_adapter.STEP_MARGIN_S) + review_budget},
              initial_candidate=stages['campaign.initial_candidate'].get('detail'),
              stages=stages, diagnostics=diagnostics,
              dry_run_records={'production (bounded plan)': record_of(PREPARED)})
(OUT / 'pipeline.json').write_text(text(result))
