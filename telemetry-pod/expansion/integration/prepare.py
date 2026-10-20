"""Combine reviewed electrical inputs and the exact AMPSEAL connector capture."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'interface-preparation/aux-power/inputs'
CONNECTOR = ROOT.parent / 'connector-candidate'
FOOTPRINT = 'PodConnector.pretty/AMPSEAL_35_1-776163-1.kicad_mod'
MODEL = 'c-1-776163-1-t-3d.stp'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root):
    return {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}


def prepare(out):
    if out.exists():
        raise ValueError('Output must be fresh')
    intent = json.loads((BASE / 'intent.json').read_text())
    j1s = [c for c in intent['components'] if c['reference'] == 'J1']
    if len(j1s) != 1:
        raise ValueError('Exactly one J1 is required')
    j1 = j1s[0]
    if j1 != {'footprint': 'ampseal:ampseal-35', 'id': 'connector/J1',
              'lib_id': 'Connector_Generic:Conn_01x35', 'reference': 'J1',
              'units': [1], 'value': '776163-1'}:
        raise ValueError('J1 baseline changed; reconcile identity and bindings before integration')
    # Verify the precise candidate reviewed upstream before incorporating it.
    reviewed = json.loads((CONNECTOR / 'review/candidate-source-hashes.json').read_text())
    if digest(CONNECTOR / FOOTPRINT) != reviewed[FOOTPRINT]:
        raise ValueError('Connector footprint differs from independent review pin')
    sources = json.loads((CONNECTOR / 'sources.json').read_text())
    for source in sources:
        if digest(CONNECTOR / source['file']) != source['sha256']:
            raise ValueError(f"Connector source changed: {source['file']}")
    j1['footprint'] = 'PodConnector:AMPSEAL_35_1-776163-1'
    j1['value'] = '1-776163-1'
    shutil.copytree(BASE, out)
    (out / 'footprints/PodConnector.pretty').mkdir()
    shutil.copyfile(CONNECTOR / FOOTPRINT, out / 'footprints' / FOOTPRINT)
    (out / 'models').mkdir(exist_ok=True)
    shutil.copyfile(CONNECTOR / 'sources' / MODEL, out / 'models' / MODEL)
    (out / 'intent.json').write_text(json.dumps(intent, indent=2, sort_keys=True) + '\n')
    receipt = {
        'schema': 'telemetry-pod.source-integration/1',
        'stage': 'prepared-only',
        'baseline': '../interface-preparation/aux-power/inputs',
        'baseline_files_sha256': files(BASE),
        'outputs_sha256': files(out),
        'connector_review_sha256': digest(CONNECTOR / 'review/candidate-source-hashes.json'),
        'changes': {'J1.value': ['776163-1', '1-776163-1'],
                    'J1.footprint': ['ampseal:ampseal-35', 'PodConnector:AMPSEAL_35_1-776163-1']},
        'native_verification': 'pending released emitter and assembly-policy support'
    }
    (out / 'integration-receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    receipt = prepare(args.out)
    print(json.dumps({'status': 'PREPARED', 'files': len(receipt['outputs_sha256']), 'out': str(args.out)}))
