"""AGENTEE-487 focused test of runtime_receipt.py parameterization (no docker, no network).
Run from the fome-mc root: /usr/bin/python3 -B telemetry-pod/expansion/production-capture/test_runtime_receipt_params.py"""
import importlib.util, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'runtime_receipt.py'
results = []


def load():
    spec = importlib.util.spec_from_file_location('runtime_receipt', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case(name, cond):
    results.append((name, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + name)


m = load()
dest = re.search(r"^DEST = HERE / '([^']+)'", (HERE / 'retain.py').read_text(), re.M).group(1)
case('default evidence is retain.py DEST', m.EVIDENCE == HERE / dest)
case('default receipt dir is the historical j6b receipt', m.OUT == HERE / 'evidence/production-runtime-j6b')
with tempfile.TemporaryDirectory() as tmp:
    ev, out = m.configure(evidence=str(HERE / 'evidence/emission-7d5b0d4d'), receipt_dir=tmp)
    case('configure resolves evidence and receipt dir', ev == HERE / 'evidence/emission-7d5b0d4d' and out == Path(tmp))
    (Path(tmp) / 'receipt.json').write_text('{}')
    try:
        m.write('/nonexistent/observation.json', '/nonexistent', '/nonexistent')
        refused = False
    except SystemExit as exc:
        refused = 'never overwritten' in str(exc)
    case('write refuses an existing receipt (history kept)', refused)
m = load()
rest = m.parse(['--contract', 'a.json', '--contract', 'b.json', '--authority', 'X', '--source-commit', 'abc', 'check'])
case('parse: repeated --contract, authority, source commit', rest == ['check'] and m.PARAMS['contracts'] == ['a.json', 'b.json']
     and m.PARAMS['authority'] == 'X' and m.PARAMS['source_commit'] == 'abc')
code = SCRIPT.read_text().split('"""', 2)[2]  # everything after the module docstring
case('no hard-coded retained-evidence or receipt binding paths remain',
     "'evidence/emission-7d5b0d4d/" not in code and "'evidence/production-runtime-j6b/" not in code)
case('receipt authority is the neutral parameter (no agent-521 text in the receipt body)',
     'agent-521' not in code.split('def write', 1)[1].split('def check', 1)[0])
import hashlib, json, shutil
m = load()
with tempfile.TemporaryDirectory() as tmp:
    binary = Path(tmp) / 'placement-engine'; binary.write_bytes(b'any actual binary bytes')
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    good = Path(tmp) / 'good.json'; good.write_text(json.dumps({'schema': m.RUST_RECEIPT_SCHEMA, 'binary_sha256': digest}))
    wrong = Path(tmp) / 'wrong-field.json'
    wrong.write_text(json.dumps({'schema': m.RUST_RECEIPT_SCHEMA, 'binary_sha256': '0' * 64, 'previous_binary_sha256': digest}))
    notjson = Path(tmp) / 'not-json.txt'; notjson.write_text('binary ' + digest)
    badschema = Path(tmp) / 'schema.json'; badschema.write_text(json.dumps({'schema': 'x', 'binary_sha256': digest}))
    case('H3 rust: any actual binary + its JSON install receipt is accepted', m.rust_pair(str(binary), str(good))['binary']['sha256'] == digest)
    for label, rec in (('wrong field (previous_binary_sha256 correct)', wrong), ('malformed non-JSON containing the digest', notjson),
                       ('wrong schema', badschema), ('missing receipt file', Path(tmp) / 'absent.json')):
        try:
            m.rust_pair(str(binary), str(rec)); rejected = False
        except SystemExit:
            rejected = True
        case(f'H3 rust: {label} is rejected', rejected)
    try:
        m.rust_pair(str(binary), None); rejected = False
    except SystemExit:
        rejected = True
    case('H3 rust: binary without receipt (missing input) is rejected', rejected)
    # full check() with a copied historical receipt whose run_bindings carry the pair
    rdir = Path(tmp) / 'receipt'; shutil.copytree(HERE / 'evidence/production-runtime-j6b', rdir)
    rec = json.loads((rdir / 'receipt.json').read_text())
    rec['run_bindings'] = {'rust': {'binary': {'path': str(binary), 'sha256': digest}, 'receipt': {'path': str(good), 'sha256': hashlib.sha256(good.read_bytes()).hexdigest()}}}
    (rdir / 'receipt.json').write_text(json.dumps(rec))
    def full_check():
        r = subprocess.run([sys.executable, '-B', str(SCRIPT), '--evidence', str(HERE / 'evidence/emission-7d5b0d4d'),
                            '--receipt-dir', str(rdir), '--runtime', 'historical-j6b', 'check'], capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
    rc, _ = full_check()
    case('H3 full check: good pair accepted', rc == 0)
    good.write_text(wrong.read_text())  # same path, now the wrong-field receipt
    rec['run_bindings']['rust']['receipt']['sha256'] = hashlib.sha256(good.read_bytes()).hexdigest()
    (rdir / 'receipt.json').write_text(json.dumps(rec))
    rc, out = full_check()
    case('H3 full check: wrong-field receipt rejected', rc != 0 and 'binary_sha256' in out)
    binary.write_bytes(b'a different binary')
    rc, out = full_check()
    case('H3 full check: binary mismatch rejected', rc != 0)
case('rust: no hard-coded 5261cb13 binary identity', '5261cb13' not in SCRIPT.read_text())
# H4: runtime selection
m = load()
try:
    m.runtime(); unselected = False
except SystemExit as exc:
    unselected = 'no runtime selected' in str(exc)
case('H4: no implicit runtime (selection required)', unselected)
cur = m.select_runtime('telemetry-pod/expansion/production-capture/runtime/agentee-484r2.json')
case('H4: current runtime manifest selected and hash-bound', cur['_selection']['kind'] == 'manifest' and len(cur['_selection']['sha256']) == 64)
with tempfile.TemporaryDirectory() as tmp:
    bad = Path(tmp) / 'bad.json'; bad.write_text('{"schema": "other"}')
    try:
        m.select_runtime(str(bad)); refused = False
    except SystemExit:
        refused = True
    case('H4: malformed runtime manifest refused', refused)
    try:
        m.validate_source_commit('0' * 40, tmp); refused = False
    except SystemExit:
        refused = True
    case('H4: --source-commit that is not a fome-mc commit refused', refused)
    head = subprocess.run(['git', '-C', str(HERE), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    try:
        m.validate_source_commit(head, tmp); refused = False
    except SystemExit as exc:
        refused = 'differs from source commit' in str(exc)
    case('H4: --source-commit validated against the run copy (empty run copy refused)', refused)
nosel = subprocess.run([sys.executable, '-B', str(SCRIPT), '--evidence', str(HERE / 'evidence/emission-7d5b0d4d'), 'check'],
                       capture_output=True, text=True)
case('H4: historical receipt without explicit selection is refused', nosel.returncode != 0 and 'historical-j6b' in (nosel.stdout + nosel.stderr))
# H4 re-fix: identity comparison, selection kinds, legacy rule, pre-launch selection
m = load()
H = m.HISTORICAL_J6B
with tempfile.TemporaryDirectory() as tmp:
    def bound_receipt(manifest_doc, kind='manifest'):
        rdir = Path(tempfile.mkdtemp(dir=tmp)); shutil.copytree(HERE / 'evidence/production-runtime-j6b', rdir / 'r')
        man = rdir / 'manifest.json'; man.write_text(json.dumps(manifest_doc))
        rec = json.loads((rdir / 'r/receipt.json').read_text())
        rec['runtime_selection'] = {'kind': kind, 'path': str(man), 'sha256': hashlib.sha256(man.read_bytes()).hexdigest()}
        (rdir / 'r/receipt.json').write_text(json.dumps(rec))
        r = subprocess.run([sys.executable, '-B', str(SCRIPT), '--evidence', str(HERE / 'evidence/emission-7d5b0d4d'),
                            '--receipt-dir', str(rdir / 'r'), 'check'], capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
    agreeing = {'schema': m.RUNTIME_SCHEMA, **{k: H[k] for k in m.RUNTIME_KEYS}}
    rc, out = bound_receipt(agreeing)
    case('H4: receipt bound to an AGREEING manifest checks OK', rc == 0)
    for key in ('agent_ee_commit', 'router_commit', 'source_sha256', 'extension_sha256', 'config'):
        bad = dict(agreeing); bad[key] = ('sha256:' + 'a' * 64) if key == 'config' else ('a' * len(H[key]))
        rc, out = bound_receipt(bad)
        case(f'H4: contradictory selected {key} vs unchanged receipt FAILS', rc != 0)
    rc, out = bound_receipt(agreeing, kind='mystery')
    case('H4: unknown selection kind rejected', rc != 0 and 'unknown runtime selection kind' in out)
    man = Path(tmp) / 'agree.json'; man.write_text(json.dumps(agreeing))
    r = subprocess.run([sys.executable, '-B', str(SCRIPT), '--evidence', str(HERE / 'evidence/emission-7d5b0d4d'),
                        '--runtime', str(man), 'check'], capture_output=True, text=True)
    case('H4: legacy receipt checked with a manifest selection is refused (explicit historical only)',
         r.returncode != 0 and 'historical-j6b' in (r.stdout + r.stderr))
m = load()
m.configure(runtime='telemetry-pod/expansion/production-capture/runtime/agentee-484r2.json')
inv = m.invocation('/run', '/tool/agent-ee')
pre = inv['pre_launch_identity_check']['argv']
case('H4: pre-launch command passes the selected runtime', pre[pre.index('--runtime') + 1] == '/pod/runtime-manifest.json')
case('H4: pre-launch container mounts the selected manifest', 'RUNTIME_MANIFEST:/pod/runtime-manifest.json:ro' in inv['container'])
case('H4: current runtime path names no historical c4 index', inv['image']['c4_index'] is None)
hist = subprocess.run([sys.executable, '-B', str(SCRIPT), '--evidence', str(HERE / 'evidence/emission-7d5b0d4d'), '--runtime', 'historical-j6b', 'check'],
                      capture_output=True, text=True)
case('historical j6b receipt checks with explicit --runtime historical-j6b', hist.returncode == 0 and 'runtime receipt OK' in hist.stdout)
print(f"{sum(ok for _, ok in results)}/{len(results)} passed")
sys.exit(0 if all(ok for _, ok in results) else 1)
