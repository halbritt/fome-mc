"""Recheck the candidate without modifying its native project or hiding ERC errors."""
from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

BASE = Path(__file__).resolve().parent
with TemporaryDirectory(prefix='pod-storage-check-') as directory:
    run = Path(directory)
    for name in ['telemetry-pod.kicad_sch', 'telemetry-pod.kicad_pro', 'sym-lib-table', 'fp-lib-table']:
        shutil.copyfile(BASE / name, run / name)
    (run / 'inputs').symlink_to(BASE / 'inputs', target_is_directory=True)
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(run/'native.xml'), str(run/'telemetry-pod.kicad_sch')], check=True)
    subprocess.run([sys.executable, str(BASE/'independent-review/check_power_independent.py'), str(run/'native.xml'), str(BASE/'previous-storage-native.xml'), str(BASE/'previous-adc-native.xml'), str(run/'review.json')], check=True)
    subprocess.run(['kicad-cli', 'sch', 'erc', '--format', 'json', '-o', str(run/'erc.json'), str(run/'telemetry-pod.kicad_sch')], check=True)
    report = json.loads((run/'erc.json').read_text())
    actual = Counter((v['type'],v['severity']) for sheet in report['sheets'] for v in sheet['violations'])
    expected = Counter({('footprint_link_issues','warning'): 1})
    if actual != expected:
        raise SystemExit('ERC findings changed: '+str(actual))
    print('Connectivity review passed. ERC has one open connector-footprint warning. Supervision and power qualification remain incomplete.')
