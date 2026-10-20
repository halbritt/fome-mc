"""Reproduce and independently check the series-divider source selection."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-only', action='store_true')
args = parser.parse_args()
if not args.source_only:
    parser.error('Native verification is pending; use --source-only for preparation checks')
with tempfile.TemporaryDirectory(prefix='pod-series-verify-') as td:
    run = Path(td)
    base, candidate = run / 'base', run / 'candidate'
    subprocess.run([sys.executable,str(ROOT.parent/'component-fit/prepare.py'),'--out',str(base),'--source-only'],check=True)
    subprocess.run([sys.executable,str(ROOT/'prepare.py'),'--out',str(candidate),'--source-only'],check=True)
    for actual, retained in [('inputs/intent.json','intent.json'),('inputs/emitter-layout.json','emitter-layout.json'),('receipt.json','receipt.json')]:
        if (candidate/actual).read_bytes() != (ROOT/'prepared'/retained).read_bytes():
            raise ValueError('Retained source differs: '+actual)
    subprocess.run([sys.executable,str(ROOT/'review/check_series.py'),str(ROOT),str(base/'inputs'),
                    str(candidate),str(run/'review.json'),'--source-only'],check=True)
print('PASS: series-divider source; native verification NOT_RUN')
