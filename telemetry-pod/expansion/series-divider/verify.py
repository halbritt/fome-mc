"""Reproduce source and optionally the pinned unreleased native candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-only', action='store_true')
parser.add_argument('--out', type=Path, help='Fresh directory retaining native evidence, including failures')
args = parser.parse_args()
if not args.source_only and args.out is None:
    parser.error('Native verification requires --out NEW_DIRECTORY')
if args.out is not None and args.out.exists():
    parser.error('Output directory must be fresh')

def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}

def netlist_content(path):
    tree = ET.parse(path).getroot()
    design = tree.find('design')
    for name in ['source', 'date']:
        element = design.find(name)
        if element is None:
            raise ValueError('Missing native metadata: ' + name)
        design.remove(element)
    return ET.tostring(tree)

with tempfile.TemporaryDirectory(prefix='pod-series-verify-') as td:
    run = Path(td)
    base = run / 'base'
    candidate = args.out.resolve() if args.out is not None else run / 'candidate'
    subprocess.run([sys.executable,str(ROOT.parent/'component-fit/prepare.py'),'--out',str(base),'--source-only'],check=True)
    command = [sys.executable,str(ROOT/'prepare.py'),'--out',str(candidate)]
    if args.source_only:
        command.append('--source-only')
    subprocess.run(command,check=True)
    for actual, retained in [('inputs/intent.json','intent.json'),('inputs/emitter-layout.json','emitter-layout.json'),('receipt.json','receipt.json')]:
        if (candidate/actual).read_bytes() != (ROOT/'prepared'/retained).read_bytes():
            raise ValueError('Retained source differs: '+actual)
    subprocess.run([sys.executable,str(ROOT/'review/check_series.py'),str(ROOT),str(base/'inputs'),
                    str(candidate),str(candidate/'source-review.json'),'--source-only'],check=True)
    if not args.source_only:
        retained = ROOT / 'native-candidate'
        provenance = json.loads((ROOT / 'native-provenance.json').read_text())
        if hashes(retained) != provenance['files_sha256']:
            raise ValueError('Retained native evidence changed')
        # Compare before native tools create their local project preferences.
        for name in ['inputs', 'project']:
            if hashes(candidate/name) != hashes(retained/name):
                raise ValueError('Candidate does not reproduce byte-for-byte: '+name)
        for name in ['receipt.json', 'emission-receipt.json']:
            if (candidate/name).read_bytes() != (retained/name).read_bytes():
                raise ValueError('Candidate receipt changed: '+name)
        schematic = candidate / 'project/telemetry-pod.kicad_sch'
        subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml',
                        '-o',str(candidate/'native.xml'),str(schematic)],check=True)
        subprocess.run(['kicad-cli','sch','erc','--format','json',
                        '-o',str(candidate/'erc.json'),str(schematic)],check=True)
        subprocess.run(['kicad-cli','sch','export','bom','--fields',
                        'Reference,Value,Footprint,EXCLUDE_FROM_BOM,EXCLUDE_FROM_BOARD',
                        '--labels','Reference,Value,Footprint,ExcludeBOM,ExcludeBoard',
                        '-o',str(candidate/'native-bom.csv'),str(schematic)],check=True)
        if netlist_content(candidate/'native.xml') != netlist_content(retained/'native.xml'):
            raise ValueError('Native XML differs beyond source path and date')
        if (candidate/'native-bom.csv').read_bytes() != (retained/'native-bom.csv').read_bytes():
            raise ValueError('Native BOM differs')
        actual_erc = json.loads((candidate/'erc.json').read_text())
        expected_erc = json.loads((retained/'erc.json').read_text())
        del actual_erc['date'], expected_erc['date']
        if actual_erc != expected_erc:
            raise ValueError('Native ERC differs beyond date')
        subprocess.run([sys.executable,str(ROOT/'review/check_native_series.py'),str(ROOT),
                        str(candidate),str(candidate/'native-review.json')],check=True)
print('PASS: series-divider source; ' + ('native verification NOT_RUN' if args.source_only else
      'exact native reproduction and independent checks; unreleased software candidate, board not qualified'))
