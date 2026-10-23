"""The production runtime of the prepared pod campaign (AGENTEE-207 j6b2, review H1; AGENTEE-466).

agent-449 repinned the pod preparation explicitly to agent-ee main 7d5b0d4d, the AGENTEE-466 qualified runtime,
run in that runtime's own image: tag agent-ee:ci-b29cead1… (c4 OCI index sha256:6dd73b15…), which on proximal's
classic store is the image config sha256:d96f8e00…. That is a coordinator decision relaying agent-521 a9cb03ad and
2fbe5f08, not owner-stated. The producer and the runtime are therefore the same agent-ee and the same image.
This script records that selection in one immutable receipt. The receipt is bound to the prepared plan, scope,
campaign, driver receipt and initial candidate. It launches nothing.

- observe runs inside the production image, in the single preparation run, after pipeline.py:
  - the image's /opt/agent-ee must be file for file the `git archive` export of the pin;
  - the runtime agent-ee preflights the image's own router;
  - the router source digest is recomputed with the router's own engine.source_sha256;
  - the extension module and the interpreter are hashed;
  - the prepared campaign is validated by the runtime without launching: the routing declaration and tool
    qualification, the plan bounds, the scope, and a recapture of the initial candidate;
  - the producer source mount named by the campaign's steps is recomputed.
- write runs on the host. It composes the receipt from four inputs and records the exact invocation, refusing on
  any mismatch:
  - the observation;
  - the retained evidence;
  - the proximal image identity recomputed from a `docker save` stream (save_probe output): config blob digest,
    OCI manifest and layer diff_ids;
  - the c4 index -> manifest -> config relation from the AGENTEE-466 evidence and its independent review.
- check runs on the host and re-verifies every binding of a written receipt.

Usage:
  (inside the image) python3 runtime_receipt.py observe PREPARED OBSERVATION.json EXPORT
  /usr/bin/python3 telemetry-pod/expansion/production-capture/runtime_receipt.py write OBSERVATION.json IMAGE_DIR RUN_DIR
  /usr/bin/python3 telemetry-pod/expansion/production-capture/runtime_receipt.py check

Options before MODE (AGENTEE-487): --evidence DIR (default: retain.py DEST) --receipt-dir DIR (default: the
historical evidence/production-runtime-j6b; write refuses an existing receipt) --authority TEXT --source-commit SHA
--contract PATH (repeatable) --rust-binary PATH --rust-receipt PATH --native PATH.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
# AGENTEE-487 (agent-529 decision 783ad032): the retained candidate, the receipt directory, the authority text and
# the consumed bindings are PARAMETERS, not constants. The retained evidence defaults to retain.py's DEST (one source
# of truth); the receipt directory defaults to the historical j6b receipt, which `write` never overwrites.
def retained_default():
    m = re.search(r"^DEST = HERE / '([^']+)'", (HERE / 'retain.py').read_text(), re.M)
    if not m:
        raise SystemExit('retain.py declares no DEST')
    return HERE / m.group(1)
EVIDENCE = retained_default()
OUT = HERE / 'evidence/production-runtime-j6b'
RECEIPT = OUT / 'receipt.json'
PARAMS = {'authority': 'not stated: the coordinator supplies --authority for each run', 'source_commit': None,
          'contracts': [], 'rust_binary': None, 'rust_receipt': None, 'native': None}


def configure(evidence=None, receipt_dir=None, **params):
    """Bind the run being described: retained evidence dir, receipt dir and the PARAMS (paths are fome-mc-relative
    or absolute). Returns the resolved (EVIDENCE, OUT)."""
    global EVIDENCE, OUT, RECEIPT
    if evidence:
        EVIDENCE = (ROOT / evidence) if not Path(evidence).is_absolute() else Path(evidence)
    if receipt_dir:
        OUT = (ROOT / receipt_dir) if not Path(receipt_dir).is_absolute() else Path(receipt_dir)
    RECEIPT = OUT / 'receipt.json'
    for k, v in params.items():
        if k not in PARAMS:
            raise SystemExit(f'unknown parameter {k}')
        if v is not None:
            PARAMS[k] = v
    return EVIDENCE, OUT


def rel_here(path):
    return Path(path).resolve().relative_to(HERE.resolve()).as_posix()


def bound_file(path):
    path = Path(path) if Path(path).is_absolute() else ROOT / path
    return {'path': str(path), 'sha256': sha(path)}
# The coordinator's selection (agent-449, j6b2 corrected order; not owner-stated). Every value is recomputed from
# the actual artifacts and compared, never assumed.
REQUIRED = {
    'agent_ee_commit': '7d5b0d4de65a5b8e8f925ad6f366a46653aae563',
    'image_tag': 'agent-ee:ci-b29cead1c3bfdd8fb8938dcba77bb14956810c90',
    'c4_index': 'sha256:6dd73b1559920a8417ac51af6a148b134aff6ee7dacf8e93842156beabce2334',
    'amd64_manifest': 'sha256:85fc188c22fcb9d7f51b26e744a6f57acd60cc46c6db6e860c5f0ecd0f66111b',
    'config': 'sha256:d96f8e00a50a1bb6fab119ac8973a083af9373e2c9c235f3df20f655cfc3b5b7',
    'router_commit': 'b5774496d8466b67ffa0362b6665fee2108155a3',
    'source_sha256': '9cfc5d5e9369fd044ac6555afe57bdc4ccc829421e5496d42599c2d4a71951b2',
    'extension_sha256': 'ec5fb733d321343456917b2925ec275af233e3a44d34b2f332800d51352b2cd9'}
EE466 = Path('/tmp/agent-ee-burndown-20261017/workers/ee466-repin-runtime')
EE466_REVIEW = Path('/tmp/agent-ee-burndown-20261017/reviews/ee466-repin-runtime-sol.md')
CHECKOUT = Path('/opt/kicad-route')
PREPARED = ('plan.json', 'scope.json', 'campaign.json', 'driver-receipt.json', 'dry-run/candidate.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return json.dumps(value, indent=1, sort_keys=True) + '\n'


def tree(root):
    root, found = Path(root), {}
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != '__pycache__')
        for name in names:
            path = Path(current) / name
            if path.is_file() and not path.is_symlink():
                found[path.relative_to(root).as_posix()] = sha(path)
    return found


def observe(prepared, out, export):
    """Inside the production image; the runtime agent-ee is the image's /opt/agent-ee/src."""
    sys.path[:0] = ['/opt/agent-ee/src']
    from agent_ee import candidate, pod_driver, routing_adapter as adapter, kicad_route_attempt as attempt
    from agent_ee import tool_source
    prepared, problems = Path(prepared).resolve(), []
    image_tree, export_tree = tree('/opt/agent-ee'), tree(export)
    differ = sorted(k for k in set(image_tree) | set(export_tree) if image_tree.get(k) != export_tree.get(k))
    if differ:
        problems.append(f'image /opt/agent-ee differs from the {REQUIRED["agent_ee_commit"]} export: {differ[:10]}')
    preflight = adapter.preflight(CHECKOUT)
    manifest = json.loads((CHECKOUT / 'manifest.json').read_text())
    krt = manifest['krt']
    script = ('import sys; sys.path.insert(0, sys.argv[1] + "/src"); from kicad_route import engine; '
              'print(engine.source_sha256(sys.argv[2]))')
    source = subprocess.run(['/usr/bin/python3', '-I', '-B', '-c', script, str(CHECKOUT), str(CHECKOUT / krt['source_path'])],
                            capture_output=True, text=True, check=True).stdout.strip()
    module = CHECKOUT / krt['extension_module']['path']
    interpreter = CHECKOUT / '.venv-krt/bin/python'
    version = subprocess.run([str(interpreter), '-I', '-c', 'import sys; print(sys.version.split()[0])'],
                             capture_output=True, text=True, check=True).stdout.strip()
    campaign = json.loads((prepared / 'campaign.json').read_text())
    declaration = campaign['routing_adapter']
    adapter.validate_declaration(declaration)
    spec = adapter.step(checkout=CHECKOUT, **{k: declaration[k] for k in ('project', 'board', 'schematic', 'name', 'label')},
                        budget=declaration['budget'], timeout=declaration['timeout'])
    bounds = pod_driver.validate_plan(json.loads((prepared / 'plan.json').read_text()))
    pod_driver.validate_scope(json.loads((prepared / 'scope.json').read_text()))
    with tempfile.TemporaryDirectory(prefix='pod-runtime-capture-') as tmp:
        capture = candidate.capture(prepared / 'scope.json', Path(tmp))
    producer = {}
    for m in sorted({m['source'] for s in campaign['implementation_steps'] for m in s['mounts']}):
        files = tool_source._files(Path(m))
        export_src = tool_source._files(Path(export) / 'src')
        producer[m] = {'identity': tool_source.identity(files), 'files': len(files),
                       'name_is_identity': Path(m).name == tool_source.identity(files),
                       'equals_export_src': files == export_src}
    result = {
        'schema': 'pod-capture.runtime-observation/2',
        'runtime_agent_ee': {'path': '/opt/agent-ee', 'files': len(image_tree), 'equals_export': not differ,
                             'export': str(export), 'pinned_router': attempt.PIN},
        'router': {'checkout': str(CHECKOUT), 'preflight': preflight,
                   'manifest': {'path': str(CHECKOUT / 'manifest.json'), 'sha256': sha(CHECKOUT / 'manifest.json'),
                                'krt': {k: krt.get(k) for k in ('commit', 'generation', 'describe', 'source_sha256',
                                                               'source_path', 'extension_module')}},
                   'source_sha256_recomputed': source,
                   'extension': {'path': str(module), 'sha256_recomputed': sha(module)},
                   'interpreter': {'path': str(interpreter), 'resolved': str(interpreter.resolve()),
                                   'sha256': sha(interpreter.resolve()), 'version': version,
                                   'manifest_python': manifest.get('python')},
                   'install_record': ({'path': '/opt/kicad-route.install.json', 'sha256': sha('/opt/kicad-route.install.json')}
                                      if Path('/opt/kicad-route.install.json').is_file() else None)},
        'prepared': {name: sha(prepared / name) for name in PREPARED},
        'prepared_tree': tree(prepared),
        'runtime_validation': {'routing_declaration': 'accepted', 'routing_step': spec.get('step'),
                               'routing_step_sha256': hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest(),
                               'plan_bounds': dict(zip(('max_iterations', 'max_seconds'), bounds)),
                               'scope': 'accepted', 'initial_candidate_recaptured': capture['candidate_id']},
        'producer_mounts': producer}
    if preflight['problems'] or not preflight['commit'] == preflight['pin'] == attempt.PIN == REQUIRED['router_commit']:
        problems.append(f"router preflight {preflight['commit']}/{preflight['pin']} problems {preflight['problems']}")
    if krt['commit'] != REQUIRED['router_commit'] or not source == krt['source_sha256'] == REQUIRED['source_sha256']:
        problems.append(f'router {krt["commit"]} source digest {source} / manifest {krt["source_sha256"]}')
    if not sha(module) == krt['extension_module']['sha256'] == REQUIRED['extension_sha256']:
        problems.append(f'extension {sha(module)} / manifest {krt["extension_module"]["sha256"]}')
    if capture['candidate_id'] != json.loads((prepared / 'dry-run/candidate.json').read_text())['candidate_id']:
        problems.append('the runtime does not recapture the prepared initial candidate')
    if any(not (p['name_is_identity'] and p['equals_export_src']) for p in producer.values()):
        problems.append('a producer mount is not the export src at its content identity')
    result['problems'] = problems
    Path(out).write_text(text(result))
    print(json.dumps({'problems': problems, 'candidate': capture['candidate_id']}))
    return 1 if problems else 0


def image_identity(image_dir):
    """The proximal image recomputed from its docker save stream, and the c4 relation from AGENTEE-466 evidence."""
    d = Path(image_dir)
    report = json.loads((d / 'save-report.json').read_text())
    config_blob = d / ('blobs__sha256__' + REQUIRED['config'].split(':')[1])
    config = json.loads(config_blob.read_text())
    save_manifest = json.loads((d / 'manifest.json').read_text())[0]
    index = json.loads((d / 'index.json').read_text())
    (oci,) = index['manifests']
    oci_manifest = json.loads((d / ('blobs__sha256__' + oci['digest'].split(':')[1])).read_text())
    layers = ['sha256:' + l.rsplit('/', 1)[1] for l in save_manifest['Layers']]
    c4 = (EE466 / 'scratch/image-c4-oci.txt').read_text()
    c4_index = json.loads(re.search(r'\{\s*"schemaVersion": 2,\s*"mediaType": "application/vnd\.oci\.image\.index\.v1\+json",'
                                    r'\s*"manifests": \[\s*\{\s*"mediaType": "application/vnd\.oci\.image\.manifest.*?\n\}',
                                    c4, re.S).group(0))
    c4_save = json.loads(re.search(r'\[\{"Config".*?\}\]', c4).group(0))[0]
    amd64 = [m['digest'] for m in c4_index['manifests'] if m.get('platform') == {'architecture': 'amd64', 'os': 'linux'}]
    sums = dict(reversed(l.split('  ', 1)) for l in (EE466 / 'scratch/SHA256SUMS').read_text().splitlines())
    review = EE466_REVIEW.read_text()
    found = {
        'config_blob_sha256': 'sha256:' + sha(config_blob),
        'oci_manifest_config': oci_manifest['config']['digest'],
        'layers_equal_diff_ids': layers == config['rootfs']['diff_ids'],
        'blobs_hash_to_names': report['large_blob_name_equals_sha256'], 'docker_save_rc': report['docker_save_rc'],
        'c4_amd64_manifest': amd64, 'c4_save_config': c4_save['Config'].replace('blobs/sha256/', 'sha256:'),
        'c4_index_in_save': REQUIRED['c4_index'].split(':')[1] in c4,
        'c4_evidence_sha256_listed': sums.get('image-c4-oci.txt') == sha(EE466 / 'scratch/image-c4-oci.txt'),
        'review_verdict': review.splitlines()[0]}
    problems = [k for k, ok in (
        ('config blob', found['config_blob_sha256'] == REQUIRED['config']),
        ('proximal OCI manifest', found['oci_manifest_config'] == REQUIRED['config']),
        ('diff_ids', found['layers_equal_diff_ids']), ('blobs', found['blobs_hash_to_names'] and report['docker_save_rc'] == 0),
        ('c4 manifest', amd64 == [REQUIRED['amd64_manifest']]), ('c4 config', found['c4_save_config'] == REQUIRED['config']),
        ('c4 index', found['c4_index_in_save']), ('c4 evidence hash', found['c4_evidence_sha256_listed'])) if not ok]
    if problems:
        raise SystemExit(f'image identity not established: {problems}: {found}')
    return found, config, [d / 'save-report.json', d / 'manifest.json', d / 'index.json', config_blob,
                           d / ('blobs__sha256__' + oci['digest'].split(':')[1])]


def invocation(run_dir, producer_mount):
    """The exact pod campaign command in the production image (agent-ee docs/pod-driver.md), with the container options
    of this preparation run (run.sh). Not executed here."""
    pre = ['/usr/bin/python3', '-B', '/pod/runtime_receipt.py', 'observe', '/pod/prepared', '/pod/pre-launch.json',
           '/pod/export']
    argv = ['/usr/bin/python3', '-B', '-m', 'agent_ee.cli', 'campaign', '/pod/prepared/campaign.json', '--out',
            '/pod/out/campaign']
    container = ['docker', 'run', '--rm', '--label', 'native-admission.lease=$NATIVE_ADMISSION_LEASE',
                 '--cpus', '$NATIVE_ADMISSION_CPUS', '--pids-limit', '$NATIVE_ADMISSION_PIDS',
                 '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
                 '--security-opt', 'systempaths=unconfined', '--user', 'UID:GID', '-e', 'HOME=/tmp',
                 '-e', 'PYTHONPATH=/opt/agent-ee/src', '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'AGENT_EE_REQUIRE_TOOLCHAIN=1',
                 '-w', '/opt/agent-ee', '-v', 'PREPARED_DIR:/pod/prepared:ro', '-v', 'EXPORT_7D5B0D4D:/pod/export:ro',
                 '-v', f'EXPORT_7D5B0D4D/src:{producer_mount}:ro', '-v', 'RUNTIME_RECEIPT_PY:/pod/runtime_receipt.py:ro',
                 '-v', 'NEW_OUTPUT_PARENT:/pod/out', REQUIRED['config']]
    return {'image': {'by': 'config digest (proximal classic store)', 'reference': REQUIRED['config'],
                      'tag_on_c4': REQUIRED['image_tag'], 'c4_index': REQUIRED['c4_index']},
            'pre_launch_identity_check': {'argv': pre, 'requires': 'exit 0 and problems []'},
            'campaign_command': argv, 'container': container, 'cwd': '/opt/agent-ee',
            'placeholders': {
                'PREPARED_DIR': '`retain.py --materialize-prepared OUT` (prepared-tree.json), byte-equal to the observed tree',
                'EXPORT_7D5B0D4D': f'`git archive {REQUIRED["agent_ee_commit"]}`; its src is the producer mount at the exact '
                                   'container path the campaign steps name',
                'RUNTIME_RECEIPT_PY': 'this script at the integrated fome-mc commit',
                'NEW_OUTPUT_PARENT': 'a new, empty directory', 'UID:GID': 'the launching user',
                '$NATIVE_ADMISSION_*': 'the admitted native-admit lease the launch runs in'},
            'preparation_run': {'script': rel_here(OUT / 'production_run.sh'),
                                'steps': rel_here(OUT / 'production_steps.py'), 'run_dir': str(run_dir)},
            'router': "the image's own /opt/kicad-route (no override, no legacy /tool/kicad-route mount)",
            'open': ("Network and inference-provider credentials for the review profile belong to the launcher's "
                     'environment (launch authority: the --authority parameter of this receipt); this receipt does not choose them. '
                     'The preparation ran with --network none.')}


def write(observation, image_dir, run_dir):
    if RECEIPT.exists():
        raise SystemExit(f'{RECEIPT} exists; receipts are history and are never overwritten (use --receipt-dir)')
    obs = json.loads(Path(observation).read_text())
    if obs['problems']:
        raise SystemExit(f'observation has problems: {obs["problems"]}')
    pipeline = json.loads((EVIDENCE / 'pipeline.json').read_text())
    retained = {name: sha(EVIDENCE / 'prepared' / name) for name in PREPARED}
    if retained != obs['prepared']:
        raise SystemExit('observed prepared files differ from the retained evidence')
    tree_record = json.loads((EVIDENCE / 'prepared-tree.json').read_text())
    if {k: v['sha256'] for k, v in tree_record['files'].items()} != obs['prepared_tree']:
        raise SystemExit('the retained prepared tree differs from the tree the runtime observed')
    initial = pipeline['initial_candidate']
    if (initial['candidate_id'] != obs['runtime_validation']['initial_candidate_recaptured']
            or initial['scope_sha256'] != retained['scope.json'] or initial['campaign_sha256'] != retained['campaign.json']
            or pipeline['plan_sha256'] != retained['plan.json'] or pipeline['agent_ee']['commit'] != REQUIRED['agent_ee_commit']):
        raise SystemExit('pipeline initial candidate / plan / producer pin differ from the observation')
    found, config, identity_files = image_identity(image_dir)
    router = obs['router']
    OUT.mkdir(parents=True, exist_ok=True)
    if RECEIPT.exists():
        raise SystemExit(f'{RECEIPT} exists; the receipt is immutable')
    (OUT / 'image').mkdir(exist_ok=True)
    kept = {}
    for f in [*identity_files, EE466 / 'scratch/image-c4-oci.txt']:
        shutil.copyfile(f, OUT / 'image' / f.name)
        kept['image/' + f.name] = sha(f)
    shutil.copyfile(observation, OUT / 'observation.json')
    for name in ('production_run.sh', 'production_steps.py'):  # the committed harness of the single run
        if sha(HERE / name) != sha(Path(run_dir) / 'fome' / HERE.relative_to(ROOT) / name):
            raise SystemExit(f'{name} differs from the copy the run executed')
        shutil.copyfile(HERE / name, OUT / name)
    receipt = {
        'schema': 'pod-capture.production-runtime-receipt/2',
        'authority': PARAMS['authority'],
        'launch': 'NOT launched by this receipt. Launch authority is the authority parameter above, not this script.',
        'binding': {
            'plan': {'path': rel_here(EVIDENCE / 'prepared/plan.json'), 'sha256': retained['plan.json']},
            'scope': {'path': rel_here(EVIDENCE / 'prepared/scope.json'), 'sha256': retained['scope.json']},
            'campaign': {'path': rel_here(EVIDENCE / 'prepared/campaign.json'), 'sha256': retained['campaign.json']},
            'driver_receipt': {'path': rel_here(EVIDENCE / 'prepared/driver-receipt.json'),
                               'sha256': retained['driver-receipt.json']},
            'prepared_tree': {'path': rel_here(EVIDENCE / 'prepared-tree.json'),
                              'sha256': sha(EVIDENCE / 'prepared-tree.json'), 'files': len(tree_record['files'])},
            'initial_candidate': {'candidate_id': initial['candidate_id'], 'files': initial['files'],
                                  'dry_run_candidate_sha256': retained['dry-run/candidate.json']},
            'pipeline': {'path': rel_here(EVIDENCE / 'pipeline.json'), 'sha256': sha(EVIDENCE / 'pipeline.json')},
            'retained_manifest': {'path': rel_here(EVIDENCE / 'MANIFEST.json'), 'sha256': sha(EVIDENCE / 'MANIFEST.json')}},
        'run_bindings': {
            'source_commit': PARAMS['source_commit'],
            'contracts': [bound_file(c) for c in PARAMS['contracts']],
            'mounted_python_source': obs['producer_mounts'],
            'rust_binary': bound_file(PARAMS['rust_binary']) if PARAMS['rust_binary'] else None,
            'rust_receipt': bound_file(PARAMS['rust_receipt']) if PARAMS['rust_receipt'] else None,
            'native_artifact': bound_file(PARAMS['native']) if PARAMS['native'] else None},
        'agent_ee': {**pipeline['agent_ee'], 'image_equals_export': obs['runtime_agent_ee']['equals_export'],
                     'image_files': obs['runtime_agent_ee']['files'], 'producer_mounts': obs['producer_mounts'],
                     'same_for_producer_and_runtime': True},
        'image': {
            'proximal_config_digest': REQUIRED['config'], 'tag_on_c4': REQUIRED['image_tag'],
            'c4_oci_index': REQUIRED['c4_index'], 'c4_amd64_manifest': REQUIRED['amd64_manifest'],
            'relation': ('c4 OCI index -> linux/amd64 manifest -> config blob, which equals the proximal image config '
                         '(AGENTEE-466 evidence image-c4-oci.txt, verified by its independent review; c4 itself is not '
                         'contacted by this lane)'),
            'recomputed_on_proximal': found, 'created': config.get('created'),
            'entrypoint': config['config'].get('Entrypoint'), 'files': kept,
            'ee466_review': {'path': str(EE466_REVIEW), 'sha256': sha(EE466_REVIEW), 'verdict': found['review_verdict']}},
        'router': {'checkout': router['checkout'], 'commit': router['preflight']['commit'],
                   'source_sha256': router['source_sha256_recomputed'],
                   'extension': router['extension'], 'interpreter': router['interpreter'],
                   'manifest': router['manifest'], 'install_record': router['install_record'],
                   'preflight_problems': router['preflight']['problems']},
        'runtime_validation': obs['runtime_validation'],
        'observation': {'path': rel_here(OUT / 'observation.json'), 'sha256': sha(observation)},
        'invocation': invocation(run_dir, next(iter(obs['producer_mounts'])))}
    checks = {'agent_ee_commit': receipt['agent_ee']['commit'], 'router_commit': receipt['router']['commit'],
              'source_sha256': receipt['router']['source_sha256'],
              'extension_sha256': receipt['router']['extension']['sha256_recomputed'],
              'config': found['config_blob_sha256']}
    for key, value in checks.items():
        if value != REQUIRED[key]:
            raise SystemExit(f'{key} {value} is not the required {REQUIRED[key]}')
    RECEIPT.write_text(text(receipt))
    print(RECEIPT, sha(RECEIPT))


def check():
    receipt = json.loads(RECEIPT.read_text())
    problems = [f'{name}: {item["path"]}' for name, item in receipt['binding'].items()
                if 'path' in item and sha(HERE / item['path']) != item['sha256']]
    pipeline = json.loads((EVIDENCE / 'pipeline.json').read_text())
    if pipeline['initial_candidate']['candidate_id'] != receipt['binding']['initial_candidate']['candidate_id']:
        problems.append('initial candidate differs from the retained pipeline')
    if sha(HERE / receipt['observation']['path']) != receipt['observation']['sha256']:
        problems.append('observation differs')
    for key, item in (receipt.get('run_bindings') or {}).items():  # AGENTEE-487 bindings (absent in older receipts)
        for entry in (item if isinstance(item, list) else [item]):
            if isinstance(entry, dict) and 'path' in entry and 'sha256' in entry and sha(entry['path']) != entry['sha256']:
                problems.append(f'{key}: {entry["path"]} differs')
    problems += [f'image file {rel}' for rel, digest in receipt['image']['files'].items() if sha(OUT / rel) != digest]
    config = OUT / 'image' / ('blobs__sha256__' + REQUIRED['config'].split(':')[1])
    if 'sha256:' + sha(config) != receipt['image']['proximal_config_digest']:
        problems.append('retained image config does not hash to the bound config digest')
    if problems:
        raise SystemExit('runtime receipt check failed: ' + '; '.join(problems))
    print(f"runtime receipt OK: image {receipt['image']['proximal_config_digest']} (c4 {receipt['image']['c4_oci_index']}), "
          f"agent-ee {receipt['agent_ee']['commit']}, router {receipt['router']['commit']}, "
          f"candidate {receipt['binding']['initial_candidate']['candidate_id']}")


def parse(argv):
    """Leading --name value options configure the run; the rest is MODE ARGS. --contract may repeat."""
    opts, contracts = {}, []
    while argv and argv[0].startswith('--'):
        key, value, argv = argv[0][2:].replace('-', '_'), argv[1], argv[2:]
        if key == 'contract':
            contracts.append(value)
        else:
            opts[key] = value
    configure(contracts=contracts or None, **opts)
    return argv


if __name__ == '__main__':
    mode, *args = parse(sys.argv[1:])
    if mode == 'observe':
        sys.exit(observe(*args))
    elif mode == 'write':
        write(*args)
    elif mode == 'check':
        check()
    else:
        raise SystemExit(__doc__)
