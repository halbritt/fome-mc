"""Extend the retained 326-part declaration with the source-qualified J1 record."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from agent_ee.part_record import qualify_record
from agent_ee.parts_manifest import qualify_manifest
from agent_ee.parts_subset import evaluate

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = P.parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def build(out):
    spec = importlib.util.spec_from_file_location('partial_manifest', BASE / 'parts-manifest/build.py')
    partial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(partial)
    partial.build(out)
    reconstruction = read(out / 'reconstruction.json')
    path = BASE / 'j1-historical-source/C596198.json'
    record = read(path)
    deps = qualify_record(record, ROOT)
    for rel in [path.relative_to(ROOT).as_posix(), *deps]:
        source = ROOT / rel
        target = out / rel
        if target.exists():
            assert source.read_bytes() == target.read_bytes(), rel
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        reconstruction['copied'][rel] = {'source': rel, 'sha256': sha(source)}
    intent = read(out / 'intent.json')
    c = next(c for c in intent['components'] if c['reference'] == 'J1')
    binding = c['part_binding']
    sheet = json.loads(binding['PARAM_Datasheet'])
    assert (record['lcsc'], record['mpn'], record['manufacturer']) == (
        binding['LCSC'], binding['Partnumber'], binding['Manufacturer'])
    assert (record['artifact']['sha256'], record['datasheet_url']) == (
        sheet['sha256'], sheet['url'])
    doc = read(out / 'parts.json')
    part = {
        'id': c['id'], 'role': 'Expanded pod J1 ' + c['value'], 'required': True,
        'instances': [{'sheet': '/', 'reference': 'J1'}],
        'lib_id': c['lib_id'], 'footprint': c['footprint'], 'selection_id': c['id'],
        **{k: record[k] for k in ['lcsc', 'mpn', 'manufacturer', 'package', 'stock']},
        'datasheet': {'status': 'captured', 'required': True, 'artifact': record['artifact'],
                      'provenance': {**record['datasheets'], 'locator': 'parts[id=J1]'}},
        'selection': {'kind': 'named', 'lcsc': record['lcsc'],
                      'part_record': path.relative_to(ROOT).as_posix(),
                      'part_record_sha256': sha(path),
                      'decision_ref': {'path': 'intent.json', 'sha256': sha(out / 'intent.json'),
                                       'locator': 'components[reference=J1]'}},
    }
    from agent_ee.native_netlist import read_native_inventory
    native = read_native_inventory(out / 'native.xml')
    part['instances'][0]['sheet'] = native['components']['J1']['sheet']
    doc['parts'].append(part)
    assignments = read(out / 'assignments.json')
    assignments['components'].append({
        'reference': c['id'], 'lib_id': c['lib_id'], 'footprint': c['footprint'],
        'assembly': 'through_hole', 'connector': None})
    write(out / 'assignments.json', assignments)
    doc['cad']['assignments']['sha256'] = sha(out / 'assignments.json')
    write(out / 'parts.json', doc)
    reconstruction.update(omitted=[], scope='All 327 physical references declared; no source migration or approval inferred.')
    write(out / 'reconstruction.json', reconstruction)
    refs = [i['reference'] for p in doc['parts'] for i in p['instances']]
    assert len(refs) == len(set(refs)) == 327
    assert set(refs) == set(native['components'])
    qualify_manifest(doc, out)
    report = evaluate(out, 'parts.json', out / 'native.xml', ['project/telemetry-pod.kicad_sch'])
    write(out / 'report.json', report)
    print(json.dumps({'references': len(refs), **{k: report[k] for k in ['execution', 'outcome', 'coverage', 'findings']}}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    build(parser.parse_args().out)
