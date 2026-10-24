"""The ONE local launch of the prepared production pod campaign (AGENTEE-485 R3). Preparation stays separate.

Preparation (production_run.sh) prepares and emits; runtime_receipt.py write records the immutable receipt. This
script launches the campaign that receipt binds, with the existing runner (`python3 -m agent_ee.cli campaign`, the
receipt's own invocation.campaign_command) in the receipt's image, and nothing else. Before anything runs it refuses
on any mismatch:

1. the receipt is the actual one committed in this tree (RECEIPT_DIR/receipt.json under evidence/), never a copy:
   every file of RECEIPT_DIR is byte-equal to its tracked blob at the selected integrated commit (--commit SHA,
   default HEAD) and nothing untracked sits beside it (AGENTEE-485 H5), the retained pipeline.json it binds is the
   active retain.py DEST and has no refused required stage (required_stages.py, X1), and
   `runtime_receipt.py --receipt-dir RECEIPT_DIR --runtime <its bound manifest> check` passes;
2. `retain.py --check` passes, then `retain.py --materialize-prepared` rebuilds the prepared tree into OUT/prepared,
   and its campaign.json, plan.json and driver-receipt.json hash to the receipt's bindings;
3. the mounted Rust planner and its build receipt (POD_RUST_DIR) hash to the receipt's run_bindings.rust;
4. the invocation image reference equals the bound runtime config digest and the receipt's proximal config digest,
   and the local image ID is exactly that digest (H5);
5. the receipt's recorded runner (invocation cwd and PYTHONPATH) is the selected runtime's (runtime_receipt.runner_paths:
   a mounted-export runtime runs /pod/export/src, never the image's /opt/agent-ee/src), and inside the SAME container
   argv, cwd and PYTHONPATH the campaign command uses, an import probe loads agent_ee from exactly that path and every
   loaded agent_ee/*.py file is byte-equal to the mounted EXPORT, whose cli.py equals the pin's git blob (H1);
6. inside the container, the receipt's pre_launch_identity_check (runtime_receipt.py observe of the materialized
   prepared tree against EXPORT) exits 0 with problems [].
--preflight stops after step 6 (no campaign, no placement). Without it, the campaign runs into OUT/campaign.

Usage (fome-mc root of the integrated commit; RUN as for production_run.sh: export/ = git archive of the receipt's
agent-ee pin, ae.git = a git clone holding it; OUT must not exist), inside ONE admitted lease:
  POD_RUST_DIR=DIR ~/.local/bin/native-admit run --class suite --weight 4 --label LANE -- \\
    /usr/bin/python3 -I -B telemetry-pod/expansion/production-capture/launch.py RECEIPT_DIR RUN OUT [--preflight] \\
    [--commit SHA]
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = ['/usr/bin/python3', '-I', '-B']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def refuse(why):
    print(f'\nlaunch refused: {why}', flush=True)
    sys.exit(2)


ROOT = HERE.parents[2]
# The import probe runs in the campaign's own container argv, cwd and PYTHONPATH (H1); it prints what it loaded.
IMPORT_PROBE = ('import hashlib, json, pathlib, agent_ee, agent_ee.cli; '
                'pkg = pathlib.Path(agent_ee.__file__).resolve().parent; '
                'print(json.dumps({"package": str(pkg), "cli": str(pathlib.Path(agent_ee.cli.__file__).resolve()), '
                '"files": {p.relative_to(pkg).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() '
                'for p in sorted(pkg.rglob("*.py"))}}))')


def load_module(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(*args, binary=False):
    out = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True)
    if out.returncode:
        refuse(f'git {" ".join(args)} failed: {out.stderr.decode(errors="replace").strip()}')
    return out.stdout if binary else out.stdout.decode().strip()


def committed_receipt_problems(receipt_dir, commit):
    """H5: every file of RECEIPT_DIR byte-equals its tracked blob at COMMIT; untracked or missing files refuse."""
    rel = receipt_dir.relative_to(ROOT).as_posix()
    tracked = set(git('ls-tree', '-r', '--name-only', commit, '--', rel + '/').splitlines())
    on_disk = {p.relative_to(ROOT).as_posix() for p in receipt_dir.rglob('*') if p.is_file() or p.is_symlink()}
    problems = [f'{path} is not tracked at {commit}' for path in sorted(on_disk - tracked)]
    problems += [f'{path} (tracked at {commit}) is missing' for path in sorted(tracked - on_disk)]
    if rel + '/receipt.json' not in tracked:
        problems.append(f'{rel}/receipt.json is not a tracked receipt at {commit}')
    for path in sorted(tracked & on_disk):
        if (ROOT / path).is_symlink() or (ROOT / path).read_bytes() != git('cat-file', 'blob', f'{commit}:{path}', binary=True):
            problems.append(f'{path} differs from its tracked blob at {commit}')
    return problems


def image_problems(receipt, manifest, image_id):
    """H5: the invocation image is the bound runtime digest, and the local image ID is exactly it."""
    image = receipt['invocation']['image']['reference']
    want = manifest['config']
    problems = []
    if image != want:
        problems.append(f'invocation image {image} is not the bound runtime config digest {want}')
    if receipt.get('image', {}).get('proximal_config_digest') != want:
        problems.append(f'receipt image digest {receipt.get("image", {}).get("proximal_config_digest")} is not {want}')
    if image_id != want:
        problems.append(f'local image ID {image_id!r} for {image} is not {want}')
    return problems


def runner(manifest):
    """H1: (PYTHONPATH, cwd) of the actual campaign interpreter for the selected runtime manifest."""
    mode = manifest.get('runtime_agent_ee', 'image')
    if mode == 'mounted-export':
        return '/pod/export/src', '/pod/export'
    if mode == 'image':
        return '/opt/agent-ee/src', '/opt/agent-ee'
    refuse(f'unknown runtime_agent_ee {mode!r}')


def runner_problems(receipt, manifest):
    pythonpath, cwd = runner(manifest)
    inv = receipt['invocation']
    recorded = next((a.split('=', 1)[1] for a in inv['container'] if a.startswith('PYTHONPATH=')), None)
    problems = []
    if inv.get('cwd') != cwd or recorded != pythonpath or inv.get('runner_pythonpath', pythonpath) != pythonpath:
        problems.append(f'the receipt records the campaign runner cwd {inv.get("cwd")!r} PYTHONPATH {recorded!r}; '
                        f'the selected {manifest.get("runtime_agent_ee", "image")} runtime runs cwd {cwd!r} '
                        f'PYTHONPATH {pythonpath!r}')
    return problems


def import_problems(probe, export, pythonpath, pin_cli):
    """H1: what the campaign interpreter actually imported is the mounted export of the pin, file for file."""
    problems = []
    container_pkg = pythonpath + '/agent_ee'
    if probe.get('package') != container_pkg or probe.get('cli') != container_pkg + '/cli.py':
        problems.append(f'the campaign interpreter imports agent_ee from {probe.get("package")!r}, not {container_pkg!r}')
    local = {p.relative_to(export / 'src/agent_ee').as_posix(): sha(p) for p in sorted((export / 'src/agent_ee').rglob('*.py'))}
    if probe.get('files') != local:
        differ = sorted(k for k in set(local) | set(probe.get('files') or {}) if local.get(k) != (probe.get('files') or {}).get(k))
        problems.append(f'imported agent_ee files differ from the mounted export: {differ[:10]}')
    if local.get('cli.py') != hashlib.sha256(pin_cli).hexdigest():
        problems.append('the mounted export cli.py is not the pin\'s git blob')
    return problems


def container_argv(receipt, manifest, runtime, prepared, export, run, out, rust_dir, image):
    """The ONE container argv of the pre-launch check, the H1 import probe and the campaign (same cwd/PYTHONPATH)."""
    source = next(v for v in receipt['invocation']['container'] if v.startswith('EXPORT_') and '/work/source-cache/' in v)
    source = str(export / 'src') + ':' + source.split(':', 1)[1]
    lease = os.environ['NATIVE_ADMISSION_LEASE']
    container = [
        'docker', 'run', '--rm', '--label', f'native-admission.lease={lease}',
        '--cpus', os.environ['NATIVE_ADMISSION_CPUS'], '--pids-limit', os.environ['NATIVE_ADMISSION_PIDS'],
        '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
        '--security-opt', 'systempaths=unconfined', '--user', f'{os.getuid()}:{os.getgid()}',
        '-e', 'HOME=/tmp', '-e', f'PYTHONPATH={runner(manifest)[0]}', '-e', 'PYTHONDONTWRITEBYTECODE=1',
        '-e', 'AGENT_EE_REQUIRE_TOOLCHAIN=1', '-e', 'AGENT_EE_GIT=/pod/ae.git',
        '-e', 'AGENT_EE_TOOL_SOURCE_CACHE=/work/source-cache',
        '-e', 'AGENT_EE_RUST_PLANNER=/usr/local/libexec/agent-ee/agent-ee-placement',
        '-w', runner(manifest)[1],
        '-v', f'{prepared}:/pod/prepared:ro', '-v', f'{export}:/pod/export:ro', '-v', source,
        '-v', f'{HERE / "runtime_receipt.py"}:/pod/runtime_receipt.py:ro', '-v', f'{out}:/pod/out',
        '-v', f'{runtime}:/pod/runtime-manifest.json:ro', '-v', f'{run / "ae.git"}:/pod/ae.git:ro',
        '-v', f'{rust_dir}:/usr/local/libexec/agent-ee:ro', image]
    return container


def step(name, argv):
    print(f'=== {name}: {" ".join(map(str, argv))}', flush=True)
    rc = subprocess.run([str(a) for a in argv]).returncode
    print(f'\n{name}-exit={rc}', flush=True)
    if rc:
        refuse(f'{name} exited {rc}')


def main(argv):
    preflight = '--preflight' in argv
    commit = argv[argv.index('--commit') + 1] if '--commit' in argv else 'HEAD'
    argv = [a for i, a in enumerate(argv) if a not in ('--preflight', '--commit') and (i == 0 or argv[i - 1] != '--commit')]
    receipt_dir, run, out = (Path(a) for a in argv[:3])
    receipt_dir, run, out = receipt_dir.resolve(strict=True), run.resolve(strict=True), out.resolve()
    receipt_path = receipt_dir / 'receipt.json'
    if receipt_dir.parent != HERE / 'evidence' or receipt_path.is_symlink() or not receipt_path.is_file():
        refuse(f'{receipt_path} is not a committed receipt under {HERE / "evidence"}')
    if out.exists():
        refuse(f'{out} exists; a launch writes a new, empty output')
    receipt = json.loads(receipt_path.read_text())
    selected = receipt['runtime_selection']
    runtime = HERE / 'runtime' / Path(selected['path']).name
    if selected['kind'] != 'manifest' or sha(runtime) != selected['sha256']:
        refuse(f'runtime manifest {runtime} is not the one the receipt binds ({selected["sha256"]})')
    commit = git('rev-parse', '--verify', commit + '^{commit}')
    problems = committed_receipt_problems(receipt_dir, commit)
    if problems:
        refuse(f'the receipt is not the committed one at {commit}: ' + '; '.join(problems))
    manifest = json.loads(runtime.read_text())
    problems = runner_problems(receipt, manifest)
    retain = load_module('retain')
    bound = HERE / receipt['binding']['pipeline']['path']
    if bound.parent != retain.DEST:
        problems.append(f'the receipt binds {bound.parent}, not the active retention {retain.DEST}')
    problems += load_module('required_stages').problems(json.loads(bound.read_text()).get('stages'))
    if problems:
        refuse('; '.join(problems))
    print(f'receipt {receipt_path} sha256 {sha(receipt_path)} committed at {commit}', flush=True)
    step('receipt-check', [*PY, HERE / 'runtime_receipt.py', '--receipt-dir', receipt_dir, '--runtime', runtime, 'check'])
    step('retain-check', [*PY, HERE / 'retain.py', '--check'])
    out.mkdir(parents=True)
    prepared = out / 'prepared'
    step('materialize', [*PY, HERE / 'retain.py', '--materialize-prepared', prepared])
    for key in ('campaign', 'plan', 'driver_receipt'):
        bound = receipt['binding'][key]
        if sha(prepared / Path(bound['path']).name) != bound['sha256']:
            refuse(f'materialized {key} differs from the receipt binding {bound["sha256"]}')
    rust_dir = Path(os.environ.get('POD_RUST_DIR', '')).resolve(strict=True)
    for key, name in (('binary', 'agent-ee-placement'), ('receipt', 'agent-ee-placement.json')):
        want = receipt['run_bindings']['rust'][key]['sha256']
        if sha(rust_dir / name) != want:
            refuse(f'mounted Rust {key} {rust_dir / name} is not the bound {want}')
    image = receipt['invocation']['image']['reference']
    inspect = subprocess.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', image], capture_output=True, text=True)
    problems = image_problems(receipt, manifest, inspect.stdout.strip() if inspect.returncode == 0 else None)
    if problems:
        refuse('; '.join(problems))
    export = run / 'export'
    pin = receipt['agent_ee']['commit']
    container = container_argv(receipt, manifest, runtime, prepared, export, run, out, rust_dir, image)
    check = receipt['invocation']['pre_launch_identity_check']['argv']
    rust = ['--rust-binary', '/usr/local/libexec/agent-ee/agent-ee-placement',
            '--rust-receipt', '/usr/local/libexec/agent-ee/agent-ee-placement.json']
    # Options precede MODE (runtime_receipt.parse); the observation is written into the new output, not the image.
    check = [a if a != '/pod/pre-launch.json' else '/pod/out/pre-launch.json' for a in check[:5] + rust + check[5:]]
    print(f'agent-ee pin {pin}; image {image}', flush=True)
    print(f'=== runtime-import: {runner(manifest)}', flush=True)
    probe = subprocess.run([*container, '/usr/bin/python3', '-B', '-c', IMPORT_PROBE], capture_output=True, text=True)
    print(f'\nruntime-import-exit={probe.returncode}', flush=True)
    if probe.returncode:
        refuse(f'runtime import probe exited {probe.returncode}: {probe.stderr[-2000:]}')
    pin_cli = subprocess.run(['git', '-C', str(run / 'ae.git'), 'cat-file', 'blob', f'{pin}:src/agent_ee/cli.py'],
                             capture_output=True).stdout
    problems = import_problems(json.loads(probe.stdout), export, runner(manifest)[0], pin_cli)
    if problems:
        refuse('; '.join(problems))
    print(f'runtime-import OK: agent_ee from {runner(manifest)[0]}, cli.py {sha(export / "src/agent_ee/cli.py")}', flush=True)
    step('pre-launch-identity', [*container, *check])
    observed = json.loads((out / 'pre-launch.json').read_text())
    if observed.get('problems') != []:
        refuse(f'pre-launch identity problems: {observed.get("problems")}')
    if preflight:
        print('\npreflight=ok (no campaign launched)', flush=True)
        return 0
    step('campaign', [*container, *receipt['invocation']['campaign_command']])
    return 0


if __name__ == '__main__':
    if len([a for i, a in enumerate(sys.argv[1:], 1) if a not in ('--preflight', '--commit')
            and sys.argv[i - 1] != '--commit']) != 3:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1:]))
