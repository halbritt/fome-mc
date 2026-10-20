"""Import the retained J1 drawing without inventing acquisition history."""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
import agent_ee
from agent_ee.datasheet_capture import import_historical_pdf
from agent_ee.part_record import prepare_record, qualify_record

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = P.parent


def blob(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run(verify):
    software = json.loads((P / 'software.json').read_text())
    modules = Path(agent_ee.__file__).parent
    for name, sha in software['modules'].items():
        assert hashlib.sha256((modules / name).read_bytes()).hexdigest() == sha, name
    source = BASE / 'connector-candidate'
    note = source / 'sources.json'
    locator = {'path': 'sources.json', 'sha256': blob(note)['sha256'], 'entry': 0}
    pdf = source / 'sources/776163-K1.pdf'
    # A replay always imports to a new disposable directory and compares bytes.
    with tempfile.TemporaryDirectory(prefix='pod-j1-import-') as temp:
        dest = Path(temp) / 'acquisition' if verify else P / 'acquisition'
        manifest = import_historical_pdf(pdf, source, locator, 'J1', dest)
        if verify:
            expected = {x.name: x.read_bytes() for x in (P / 'acquisition').iterdir()}
            actual = {x.name: x.read_bytes() for x in dest.iterdir()}
            assert actual == expected, 'Acquisition replay differs'
    acquired = manifest['parts'][0]
    assert acquired['final_url'] is None and acquired['fetched_at'] is None
    assert acquired['redirect_provenance'] == 'unknown'
    catalog = BASE / 'part-bindings/connector-stock/catalog.json'
    record = prepare_record(ROOT, 'C596198', blob(catalog),
                            blob(P / 'acquisition/manifest.json'), 'J1')
    dependencies = qualify_record(record, ROOT)
    intent = json.loads((BASE / 'source-revision/intent.json').read_text())
    component = next(c for c in intent['components'] if c['reference'] == 'J1')
    binding = component['part_binding']
    datasheet = json.loads(binding['PARAM_Datasheet'])
    assert (record['lcsc'], record['mpn'], record['manufacturer']) == (
        binding['LCSC'], binding['Partnumber'], binding['Manufacturer'])
    assert (record['artifact']['sha256'], record['datasheet_url']) == (
        datasheet['sha256'], datasheet['url'])
    assert record['stock'] == 0
    report = {
        'schema': 'pod-j1-historical-source/1',
        'source_pdf': blob(pdf), 'source_note': blob(note),
        'intent': blob(BASE / 'source-revision/intent.json'),
        'reference': 'J1', 'dependencies': dependencies,
        'identity_and_source_binding': 'pass',
        'acquisition_method': acquired['acquisition_method'],
        'redirect_provenance': acquired['redirect_provenance'],
        'final_url': acquired['final_url'], 'fetched_at': acquired['fetched_at'],
        'captured_at': acquired['captured_at'], 'historical_stock': record['stock'],
        'limits': [
            'Historical import does not establish live acquisition or redirect history.',
            'Exact identity and bytes do not establish suitability or owner approval.',
            'AGENTEE-271 release policy, stock, assembly and enclosure holds remain open.',
            'No native schematic, board, intent, or existing capture was changed.',
        ],
    }
    for name, doc in [('C596198.json', record), ('report.json', report)]:
        path = P / name
        if verify:
            assert json.loads(path.read_text()) == doc, name
        else:
            path.write_text(json.dumps(doc, indent=2) + '\n')
    print('PASS: J1 canonical record matches retained PDF and native intent; redirect/fetch unknown, historical stock zero')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    run(parser.parse_args().verify)
