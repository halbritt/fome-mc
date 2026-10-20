"""Produce exact-identity records from retained captures; missing sources stay gaps."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from agent_ee.part_record import prepare_record, qualify_record

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).resolve().parent

def blob(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def build(out):
    if out.exists():
        raise ValueError('Output must be fresh')
    out.mkdir(parents=True)
    inventory = json.loads((PACKET.parent / 'parts-closure/inventory.json').read_text())
    tracked = subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z','--','telemetry-pod']).decode().split('\0')
    acquired = {}
    for rel in sorted(filter(None, tracked)):
        if not rel.endswith('/manifest.json'):
            continue
        path = ROOT / rel
        doc = json.loads(path.read_text())
        if not isinstance(doc, dict) or doc.get('schema') != 'agent-ee.datasheet-capture/1':
            continue
        for p in doc['parts']:
            if not p['missing']:
                acquired.setdefault((p['sha256'],p['url']), []).append((path,p['id']))
    records, gaps = [], []
    for part in inventory['parts']:
        for digest, sheet in part['datasheets'].items():
            key = part['lcsc']+'-'+digest[:12]
            sources = acquired.get((digest,sheet['url']), [])
            if not sources:
                gaps.append({'id':key,'lcsc':part['lcsc'],'mpn':part['mpn'],
                    'bound_sha256':digest,'url':sheet['url'],'references':sheet['references'],
                    'reason':'No canonical acquisition matches both bound PDF bytes and URL'})
                continue
            acquisition, acquired_id = sources[0]
            # Retain selection explicitly: newest exact-identity captured catalog,
            # deterministic path tie-break; this is historical stock, not live stock.
            catalog = max(part['matching_catalogs'], key=lambda c:(c['fetched_at'],c['catalog']))
            record = prepare_record(ROOT,part['lcsc'],blob(ROOT/catalog['catalog']),blob(acquisition),acquired_id)
            assert (record['mpn'],record['manufacturer'],record['artifact']['sha256'],record['datasheet_url']) == (
                part['mpn'],part['manufacturer'],digest,sheet['url'])
            dependencies = qualify_record(record,ROOT)
            filename = key+'.json'
            raw=(json.dumps(record,indent=2)+'\n').encode();(out/filename).write_bytes(raw)
            records.append({'id':key,'file':filename,'sha256':hashlib.sha256(raw).hexdigest(),
                'references':sheet['references'],'identity':{k:record[k] for k in ['lcsc','mpn','manufacturer']},
                'dependencies':dependencies})
    report={'schema':'pod-canonical-parts/1','records':records,'gaps':gaps,
        'summary':{'records':len(records),'record_instances':sum(len(r['references']) for r in records),
            'gap_groups':len(gaps),'gap_instances':sum(len(r['references']) for r in gaps)},
        'limits':['Exact identity and source replay only; no CAD, assembly or operating qualification.',
            'No binding source bytes or URLs changed; unmatched fresh PDFs are not adopted.',
            'Expanded parts/1 and native parts_subset not yet complete.']}
    (out/'index.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['summary'],sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    build(p.parse_args().out)
