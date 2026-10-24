"""AGENTEE-485 H1 control: what the campaign interpreter ACTUALLY imports, through launch.py's own container argv.

Runs launch.container_argv (the one argv of the pre-launch check, the import probe and the campaign) with the bound
runtime manifest runtime/agentee-485d.json and the committed receipt production-runtime-485d (only for its source-cache
mount), then launch.IMPORT_PROBE and launch.import_problems:
  positive: the mounted export of the pin (RUN/export) is what agent_ee loads from, file for file;
  negative (altered runtime): a copy of the export with one byte appended to src/agent_ee/cli.py refuses;
  negative (image runner): the pre-fix runner (PYTHONPATH /opt/agent-ee/src, cwd /opt/agent-ee) loads the image's
  own agent-ee and refuses.
No campaign, no placement. '--network none' is added for the probe only (imports do not depend on the network).

Usage (fome-mc root), inside ONE admitted lease:
  ~/.local/bin/native-admit run --class test --weight 1 --label LANE -- \\
    /usr/bin/python3 -I -B telemetry-pod/expansion/production-capture/runtime_import_probe.py RUN SCRATCH
RUN/export = git archive of the pin, RUN/ae.git = a git repository holding it; SCRATCH is a new directory.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('launch', HERE / 'launch.py')
launch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch)


def load_with(receipt, runner_manifest, export, run, work, rust_dir):
    """agent_ee as loaded by launch.container_argv for RUNNER_MANIFEST's runner (the campaign's own argv)."""
    (work / 'prepared').mkdir(parents=True)
    (work / 'out').mkdir()
    argv = launch.container_argv(receipt, runner_manifest, HERE / 'runtime/agentee-485d.json', work / 'prepared',
                                 export, run, work / 'out', rust_dir, runner_manifest['config'])
    argv[2:2] = ['--network', 'none']
    out = subprocess.run([*argv, '/usr/bin/python3', '-B', '-c', launch.IMPORT_PROBE], capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f'{work.name}: probe exited {out.returncode}: {out.stderr[-2000:]}')
    return json.loads(out.stdout)


def judge(name, loaded, receipt, manifest, export, run):
    """launch.import_problems against the SELECTED runtime (mounted export of the pin)."""
    pin = receipt['agent_ee']['commit']
    pin_cli = subprocess.run(['git', '-C', str(run / 'ae.git'), 'cat-file', 'blob', f'{pin}:src/agent_ee/cli.py'],
                             capture_output=True, check=True).stdout
    problems = launch.import_problems(loaded, export, launch.runner(manifest)[0], pin_cli)
    print(json.dumps({'probe': name, 'package': loaded['package'], 'loaded_cli_sha256': loaded['files'].get('cli.py'),
                      'mounted_cli_sha256': launch.sha(export / 'src/agent_ee/cli.py'),
                      'pin_cli_blob_sha256': launch.hashlib.sha256(pin_cli).hexdigest(), 'problems': problems},
                     sort_keys=True), flush=True)
    return problems


def main(run, scratch):
    run, scratch = Path(run).resolve(strict=True), Path(scratch).resolve()
    scratch.mkdir(parents=True)
    receipt = json.loads((HERE / 'evidence/production-runtime-485d/receipt.json').read_text())
    manifest = json.loads((HERE / 'runtime/agentee-485d.json').read_text())
    rust_dir = Path(receipt['run_bindings']['rust']['binary']['path']).parent
    export = run / 'export'
    results = {'positive': judge('positive', load_with(receipt, manifest, export, run, scratch / 'positive', rust_dir),
                                 receipt, manifest, export, run) == []}
    altered = scratch / 'altered-export'
    shutil.copytree(export, altered, symlinks=True)
    with open(altered / 'src/agent_ee/cli.py', 'ab') as f:
        f.write(b'\n# altered runtime negative\n')
    results['altered_runtime_refused'] = bool(judge(
        'altered-runtime', load_with(receipt, manifest, altered, run, scratch / 'altered', rust_dir),
        receipt, manifest, altered, run))
    image_runner = dict(manifest, runtime_agent_ee='image')  # the pre-fix runner: /opt/agent-ee/src, cwd /opt/agent-ee
    results['image_runner_refused'] = bool(judge(
        'image-runner', load_with(receipt, image_runner, export, run, scratch / 'image-runner', rust_dir),
        receipt, manifest, export, run))
    print(json.dumps(results, sort_keys=True))
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    sys.exit(main(*sys.argv[1:]))
