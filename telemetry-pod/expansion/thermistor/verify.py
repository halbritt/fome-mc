"""Verify sources, whole CAD syntax, reproduction and independent circuit review."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from agent_ee.symbol_library import parse_library, parse_sexpr

root = Path(__file__).resolve().parent
inputs = root/'inputs'
for filename, expected in json.loads((root/'review/final-source-review-hashes.json').read_text()).items():
    if hashlib.sha256((root/filename).read_bytes()).hexdigest() != expected:
        raise ValueError('Independent review pin mismatch: '+filename)
for source in json.loads((root/'sources.json').read_text())['sources']:
    if hashlib.sha256((root/source['file']).read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('Source digest mismatch: '+source['file'])
d = json.loads((inputs/'intent.json').read_text())
for lib in d['libraries']:
    raw = (inputs/lib['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != lib['sha256']:
        raise ValueError('Library digest mismatch: '+lib['name'])
    parse_library(raw)
for footprint in (inputs/'footprints').rglob('*.kicad_mod'):
    parse_sexpr(footprint.read_bytes())


def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


with tempfile.TemporaryDirectory(prefix='pod-thermistor-verify-') as temp:
    out = Path(temp)/'inputs'
    subprocess.run([sys.executable, str(root/'prepare.py'), '--out', str(out)],
                   check=True, capture_output=True)
    if hashes(out) != hashes(inputs):
        raise ValueError('Frozen inputs do not reproduce byte-for-byte')
    base = Path(temp)/'base'
    subprocess.run([sys.executable, str(root.parent/'integration/prepare.py'),
                    '--out', str(base)], check=True, capture_output=True)
    subprocess.run([sys.executable, str(root/'review/check_prepared_thermistor.py'),
                    str(base), str(inputs), str(Path(temp)/'report.json')], check=True)
subprocess.run([sys.executable, str(root/'calculate.py'), '--check'], check=True)
print('PASS: source/CAD hashes, full parsing, reproduction and independent graph; native ERC pending')
