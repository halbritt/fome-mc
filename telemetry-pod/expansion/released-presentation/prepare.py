"""Regenerate the series candidate with two corrected presentation headings."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
if args.out.exists():
    parser.error('Output must be fresh')
subprocess.run([sys.executable, str(ROOT.parent / 'series-divider/prepare.py'),
                '--source-only', '--out', str(args.out)], check=True)
inputs = args.out / 'inputs'
path = inputs / 'emitter-layout.json'
layout = json.loads(path.read_text())
changes = {
    'eMMC interface candidate - supplies pending':
        'eMMC interface - qualification pending',
    'Separate eMMC core supply - supervisor pending':
        'Separate eMMC core supply - qualification pending',
}
for old, new in changes.items():
    group, = [g for g in layout['groups'] if g['title'] == old]
    group['title'] = new
path.write_text(json.dumps(layout, indent=2) + '\n')
subprocess.run([sys.executable, '-m', 'agent_ee.schematic_emitter',
                str(inputs / 'intent.json'), '--layout', str(path),
                '--captures', str(inputs), '--out', str(args.out / 'project'),
                '--receipt', str(args.out / 'emission-receipt.json')], check=True)
for name in ['sym-lib-table', 'fp-lib-table']:
    shutil.copyfile(ROOT.parent / 'native-candidate/captured/project' / name,
                    args.out / 'project' / name)
