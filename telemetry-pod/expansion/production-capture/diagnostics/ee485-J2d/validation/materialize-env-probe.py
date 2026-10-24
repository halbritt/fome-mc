"""AGENTEE-485 J2d: subprocess-boundary probe for the access-materialization child, run in the pod runtime image.

argv: BOARD OUT. ROOT is /work/fome (this fome-mc archive), A is /work/export (the pinned agent-ee export).
1. The pre-J2d call (no env) must reproduce ModuleNotFoundError for agent_ee.
2. The child env is evaluated from the committed AGENT_EE_ENV expression in pipeline.py itself; with it, the child
   must import agent_ee.placement_probe from A/src, and the real materialize.py must complete on a board copy.
Exit 0 only when all three hold. A diagnostic only: no candidate or access acceptance.
"""
import ast, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT, A = Path('/work/fome'), Path('/work/export').resolve()
M = ROOT / 'telemetry-pod/expansion/agentee-489-source/materialize.py'
board, out = Path(sys.argv[1]), Path(sys.argv[2])
source = (ROOT / 'telemetry-pod/expansion/production-capture/pipeline.py').read_text()
node = next(n for n in ast.parse(source).body if isinstance(n, ast.Assign)
            and any(getattr(t, 'id', None) == 'AGENT_EE_ENV' for t in n.targets))
env = eval(compile(ast.Expression(node.value), 'pipeline.py:AGENT_EE_ENV', 'eval'), {'os': os, 'A': A})
report = {'python': sys.executable, 'pythonpath_parent': os.environ.get('PYTHONPATH'),
          'pythonpath_child': env['PYTHONPATH'],
          'env_unchanged_except_pythonpath': {k: v for k, v in env.items() if k != 'PYTHONPATH'} ==
          {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}}
with tempfile.TemporaryDirectory() as tmp:
    copy = Path(tmp) / 'board' / board.name
    copy.parent.mkdir()
    shutil.copyfile(board, copy)
    old = subprocess.run([sys.executable, '-B', str(M), str(ROOT), '--board', str(copy), '--out', str(Path(tmp) / 'old')],
                         capture_output=True, text=True)
    report['old'] = {'rc': old.returncode, 'stderr_tail': old.stderr.strip().splitlines()[-1:]}
    imp = subprocess.run([sys.executable, '-B', '-c', 'import agent_ee.placement_probe as m; print(m.__file__)'],
                         capture_output=True, text=True, env=env, cwd=tmp)
    report['new_import'] = {'rc': imp.returncode, 'file': imp.stdout.strip(), 'stderr_tail': imp.stderr.strip()[-300:]}
    new = subprocess.run([sys.executable, '-B', str(M), str(ROOT), '--board', str(copy), '--out', str(out)],
                         capture_output=True, text=True, env=env)
    report['new_materialize'] = {'rc': new.returncode, 'stdout': new.stdout.strip()[-300:],
                                 'stderr_tail': new.stderr.strip()[-600:]}
    if new.returncode == 0:
        report['new_materialize']['rows'] = len(json.loads((out / 'reservations.json').read_text())['reservations'])
checks = {'old_reproduces_missing_import': report['old']['rc'] != 0 and
          "ModuleNotFoundError: No module named 'agent_ee'" in ''.join(report['old']['stderr_tail']),
          'new_imports_pinned_export': report['new_import']['rc'] == 0 and
          Path(report['new_import']['file']).resolve().is_relative_to(A / 'src'),
          'new_materialize_completes': report['new_materialize']['rc'] == 0,
          'env_preserved': report['env_unchanged_except_pythonpath']}
report['checks'] = checks
print(json.dumps(report, indent=1))
sys.exit(0 if all(checks.values()) else 1)
