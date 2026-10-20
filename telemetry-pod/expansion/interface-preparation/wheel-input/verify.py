"""Verify prepared sources, reproduction and independent graph; no native ERC."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from agent_ee.symbol_library import parse_library, parse_sexpr

root = Path(__file__).resolve().parent
inputs = root / 'inputs'
intent = json.loads((inputs / 'intent.json').read_text())
for lib in intent['libraries']:
    raw = (inputs / lib['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != lib['sha256']:
        raise ValueError(f"Library digest mismatch: {lib['name']}")
    parse_library(raw)
for footprint in (inputs / 'footprints').rglob('*.kicad_mod'):
    parse_sexpr(footprint.read_bytes())


def hashes(directory):
    return {str(f.relative_to(directory)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in directory.rglob('*') if f.is_file()}


with tempfile.TemporaryDirectory(prefix='pod-wheel-sources-') as temp:
    out = Path(temp) / 'inputs'
    subprocess.run([sys.executable, str(root / 'prepare.py'), '--base',
                    str(root.parent / 'sensor-power/inputs'), '--out', str(out)], check=True,
                   capture_output=True, text=True)
    if hashes(out) != hashes(inputs):
        raise ValueError('Prepared inputs do not reproduce byte-for-byte')
    subprocess.run([sys.executable, str(root / 'review/check_prepared_wheel.py'),
                    str(root.parent / 'sensor-power/inputs'), str(inputs),
                    str(Path(temp) / 'report.json')], check=True)
print('PASS: library/footprint syntax and hashes, byte reproduction, independent graph; native ERC pending')
