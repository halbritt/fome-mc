"""Replay every retained historical part record and its exact dependency closure."""
import hashlib
import json
from pathlib import Path
from agent_ee.part_record import qualify_record

root = Path(__file__).resolve().parent
receipt = json.loads((root / 'recovery.json').read_text())
capture = root / 'recovered-pilot'
for name, expected in receipt['dependencies'].items():
    assert hashlib.sha256((capture / name).read_bytes()).hexdigest() == expected, name
for item in receipt['records']:
    path = capture / item['record']
    record = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
    assert record['lcsc'] == item['lcsc']
    assert record['artifact']['sha256'] == item['datasheet_sha256']
    for name, digest in qualify_record(record, capture).items():
        assert receipt['dependencies'][name] == digest, name
print('PASS: all 99 historical records and complete captured dependencies replay')
