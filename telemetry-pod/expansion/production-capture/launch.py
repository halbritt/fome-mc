"""The ONE local launch of the prepared production pod campaign (AGENTEE-485 R3). Preparation stays separate.

Preparation (production_run.sh) prepares and emits; runtime_receipt.py write records the immutable receipt. This
script launches the campaign that receipt binds, with the existing runner (`python3 -m agent_ee.cli campaign`, the
receipt's own invocation.campaign_command) in the receipt's image, and nothing else. Before anything runs it refuses
on any mismatch:

1. the receipt is the actual one committed in this tree (RECEIPT_DIR/receipt.json under evidence/), never a copy,
   and `runtime_receipt.py --receipt-dir RECEIPT_DIR --runtime <its bound manifest> check` passes;
2. `retain.py --check` passes, then `retain.py --materialize-prepared` rebuilds the prepared tree into OUT/prepared,
   and its campaign.json, plan.json and driver-receipt.json hash to the receipt's bindings;
3. the mounted Rust planner and its build receipt (POD_RUST_DIR) hash to the receipt's run_bindings.rust;
4. the image exists by the receipt's config digest;
5. inside the container, the receipt's pre_launch_identity_check (runtime_receipt.py observe of the materialized
   prepared tree against EXPORT) exits 0 with problems [].
--preflight stops after step 5 (no campaign, no placement). Without it, the campaign runs into OUT/campaign.

Usage (fome-mc root of the integrated commit; RUN as for production_run.sh: export/ = git archive of the receipt's
agent-ee pin, ae.git = a git clone holding it; OUT must not exist), inside ONE admitted lease:
  POD_RUST_DIR=DIR ~/.local/bin/native-admit run --class suite --weight 4 --label LANE -- \\
    /usr/bin/python3 -I -B telemetry-pod/expansion/production-capture/launch.py RECEIPT_DIR RUN OUT [--preflight]
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


def step(name, argv):
    print(f'=== {name}: {" ".join(map(str, argv))}', flush=True)
    rc = subprocess.run([str(a) for a in argv]).returncode
    print(f'\n{name}-exit={rc}', flush=True)
    if rc:
        refuse(f'{name} exited {rc}')


def main(argv):
    preflight = '--preflight' in argv
    receipt_dir, run, out = (Path(a) for a in [a for a in argv if a != '--preflight'][:3])
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
    print(f'receipt {receipt_path} sha256 {sha(receipt_path)}', flush=True)
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
    if subprocess.run(['docker', 'image', 'inspect', image], capture_output=True).returncode:
        refuse(f'image {image} is not present')
    export = run / 'export'
    pin = receipt['agent_ee']['commit']
    source = next(v for v in receipt['invocation']['container'] if v.startswith('EXPORT_') and '/work/source-cache/' in v)
    source = str(export / 'src') + ':' + source.split(':', 1)[1]
    lease = os.environ['NATIVE_ADMISSION_LEASE']
    container = [
        'docker', 'run', '--rm', '--label', f'native-admission.lease={lease}',
        '--cpus', os.environ['NATIVE_ADMISSION_CPUS'], '--pids-limit', os.environ['NATIVE_ADMISSION_PIDS'],
        '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
        '--security-opt', 'systempaths=unconfined', '--user', f'{os.getuid()}:{os.getgid()}',
        '-e', 'HOME=/tmp', '-e', 'PYTHONPATH=/opt/agent-ee/src', '-e', 'PYTHONDONTWRITEBYTECODE=1',
        '-e', 'AGENT_EE_REQUIRE_TOOLCHAIN=1', '-e', 'AGENT_EE_GIT=/pod/ae.git',
        '-e', 'AGENT_EE_TOOL_SOURCE_CACHE=/work/source-cache',
        '-e', 'AGENT_EE_RUST_PLANNER=/usr/local/libexec/agent-ee/agent-ee-placement',
        '-w', receipt['invocation']['cwd'],
        '-v', f'{prepared}:/pod/prepared:ro', '-v', f'{export}:/pod/export:ro', '-v', source,
        '-v', f'{HERE / "runtime_receipt.py"}:/pod/runtime_receipt.py:ro', '-v', f'{out}:/pod/out',
        '-v', f'{runtime}:/pod/runtime-manifest.json:ro', '-v', f'{run / "ae.git"}:/pod/ae.git:ro',
        '-v', f'{rust_dir}:/usr/local/libexec/agent-ee:ro', image]
    check = receipt['invocation']['pre_launch_identity_check']['argv']
    rust = ['--rust-binary', '/usr/local/libexec/agent-ee/agent-ee-placement',
            '--rust-receipt', '/usr/local/libexec/agent-ee/agent-ee-placement.json']
    # Options precede MODE (runtime_receipt.parse); the observation is written into the new output, not the image.
    check = [a if a != '/pod/pre-launch.json' else '/pod/out/pre-launch.json' for a in check[:5] + rust + check[5:]]
    print(f'agent-ee pin {pin}; image {image}', flush=True)
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
    if len([a for a in sys.argv[1:] if a != '--preflight']) != 3:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1:]))
