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
hist = subprocess.run([sys.executable, '-B', str(SCRIPT), '--evidence', str(HERE / 'evidence/emission-7d5b0d4d'), 'check'],
                      capture_output=True, text=True)
case('historical j6b receipt still checks against its own evidence', hist.returncode == 0 and 'runtime receipt OK' in hist.stdout)
print(f"{sum(ok for _, ok in results)}/{len(results)} passed")
sys.exit(0 if all(ok for _, ok in results) else 1)
