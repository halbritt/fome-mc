"""Replay retained evidence and the independent selection review without network."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from agent_ee.jlc_stock_capture import validate_capture

root = Path(__file__).resolve().parent
for source in json.loads((root / 'sources.json').read_text())['sources']:
    if hashlib.sha256((root / source['path']).read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('Source hash mismatch: ' + source['path'])
catalog = json.loads((root / 'stock/catalog.json').read_text())
result = validate_capture(catalog, lambda path: (root / 'stock' / path).read_bytes())
if result['failed'] or result['not_found'] or set(result['requested']) != {'C515607', 'C723532'}:
    raise ValueError('Expected two successful exact-ID observations')
subprocess.run([sys.executable, str(root / 'inventory.py'), '--check'], check=True)
with tempfile.TemporaryDirectory(prefix='pod-selection-review-') as temporary:
    report = Path(temporary) / 'report.json'
    subprocess.run([sys.executable, str(root / 'review/check_selection.py'), str(root), str(report)], check=True)
    if json.loads(report.read_text()) != json.loads((root / 'review/report.json').read_text()):
        raise ValueError('Independent review differs from retained report')
print('PASS: source hashes, stock capture replay, inventory and independent selection review')
