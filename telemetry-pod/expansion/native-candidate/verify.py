"""Reproduce candidate and run native checks on a fresh snapshot."""
import hashlib
import csv
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parent
for source in json.loads((root / 'spi-sources.json').read_text())['sources']:
    if hashlib.sha256((root / source['path']).read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('SPI source capture changed: ' + source['path'])

def hashes(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}

def netlist_content(path):
    tree = ET.parse(path).getroot()
    design = tree.find('design')
    for name in ['source', 'date']:
        element = design.find(name)
        if element is None:
            raise ValueError('Missing native netlist metadata: ' + name)
        design.remove(element)
    return ET.tostring(tree)

with tempfile.TemporaryDirectory(prefix='pod-expanded-native-') as temporary:
    run = Path(temporary) / 'candidate'
    subprocess.run([sys.executable, str(root / 'prepare.py'), '--out', str(run)], check=True)
    if hashes(run) != hashes(root / 'captured'):
        raise ValueError('Candidate does not reproduce byte-for-byte')
    schematic = run / 'project/telemetry-pod.kicad_sch'
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml',
                    '-o', str(run / 'native.xml'), str(schematic)], check=True)
    if netlist_content(run / 'native.xml') != netlist_content(root / 'native.xml'):
        raise ValueError('Retained native netlist differs beyond source path and timestamp')
    subprocess.run(['kicad-cli', 'sch', 'erc', '--format', 'json',
                    '-o', str(run / 'erc.json'), str(schematic)], check=True)
    subprocess.run(['kicad-cli', 'sch', 'export', 'bom', '--fields',
                    'Reference,Value,Footprint,EXCLUDE_FROM_BOM,EXCLUDE_FROM_BOARD',
                    '--labels', 'Reference,Value,Footprint,ExcludeBOM,ExcludeBoard',
                    '-o', str(run / 'native-bom.csv'), str(schematic)], check=True)
    with (run / 'native-bom.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    with (root / 'native-bom.csv').open() as stream:
        if rows != list(csv.DictReader(stream)):
            raise ValueError('Native BOM changed')
    intent = json.loads((run / 'inputs/intent.json').read_text())
    omitted = {f'JP{i}' for i in range(1, 6)} | {f'TP{i}' for i in range(1, 7)}
    expected = {c['reference'] for c in intent['components']
                if c['lib_id'] != 'power:PWR_FLAG' and c['reference'] not in omitted}
    if {row['Reference'] for row in rows} != expected or len(rows) != len(expected):
        raise ValueError('BOM component coverage changed')
    erc = json.loads((run / 'erc.json').read_text())
    retained = json.loads((root / 'erc.json').read_text())
    for field in ['sheets', 'ignored_checks', 'included_severities', 'kicad_version']:
        if erc[field] != retained[field]:
            raise ValueError('Native ERC changed: ' + field)
    subprocess.run([sys.executable, str(root / 'review/check_native.py'),
                    str(run), str(root.parent / 'thermistor/inputs'),
                    str(run / 'review.json')], check=True)
print('PASS: exact reproduction and native graph/ERC checks; shared-SPI operational qualification remains open')
