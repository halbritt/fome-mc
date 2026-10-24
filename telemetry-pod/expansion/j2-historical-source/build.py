"""Import the retained J2 Amphenol RF 132134 drawing and build its external part record (NO_LCSC, stock null).

Usage (fome-mc root on sys.path is not needed; agent_ee must be importable):
  python3 telemetry-pod/expansion/j2-historical-source/build.py [--verify]
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from agent_ee.datasheet_capture import import_historical_pdf
from agent_ee.part_decisions import validate_deviation
from agent_ee.part_record import prepare_external_record, qualify_external_record

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = P.parent
J2 = BASE / 'agentee-494-j2'
PDF = J2 / '132134-revC.pdf'
PDF_SHA256 = '1ec1d365bf5bf9e1598cf7cf2c90747ba11f06607f4c6a28ca6d30a0aab56034'
URL = 'https://www.amphenolrf.com/en-us/assets/file/4065789557/'
OWNER = P / 'owner-handfit-ccbe2294.md'
# Verbatim from the retained drawing (pdftotext -layout 132134-revC.pdf): "PART NO.132134", "Amphenol RF",
# "SMA P.C.B JACK". The identity is the manufacturer's own; no supplier row exists or is invented.
IDENTITY = {'mpn': '132134', 'manufacturer': 'Amphenol RF', 'package': 'SMA P.C.B JACK'}


def blob(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def declarations():
    identity = {'schema': 'agent-ee.external-part-identity/1', **IDENTITY,
                'evidence_refs': [{**blob(PDF), 'locator': 'sheet 3 of 3 title block: PART NO.132134, Amphenol RF, SMA P.C.B JACK'},
                                  {**blob(J2 / 'source-manifest.json'), 'locator': '/drawing_provenance'}]}
    deviation = {
        'requirement_id': 'POD-AC-5',
        'reason': ('J2 (Amphenol RF 132134 SMA PCB jack, through-hole) is hand-fitted after delivery on the owner '
                   'clarification relayed verbatim as Cairn ccbe2294@1; it is not JLC-assembled.'),
        'evidence_refs': [{'path': blob(OWNER)['path'], 'locator': 'lines 6-9 (owner words, verbatim)'},
                          {'path': blob(PDF)['path'], 'locator': 'sheet 3 of 3'}],
        'original': {'mpn': IDENTITY['mpn'], 'lcsc': None},
        'assembly': 'hand_soldered',
        'stock_deviation': {'reason': ('Manual through-hole assembly is the owner-approved choice; supplier stock is '
                                       'not a gate on it. No LCSC id or stock figure exists for this part, and none is claimed.')},
        'purchase_source': 'Amphenol RF 132134 from a distributor of the owner\'s choice (no supplier row captured)',
        'policy': 'owner_hand_fit'}
    validate_deviation(deviation)
    return identity, {'schema': 'agent-ee.part-deviations/1', 'deviations': [deviation]}


def run(verify):
    if blob(PDF)['sha256'] != PDF_SHA256:
        raise ValueError('retained 132134 drawing differs from its recorded sha256')
    manifest494 = json.loads((J2 / 'source-manifest.json').read_text())['drawing_provenance']
    if (manifest494['sha256'], manifest494['source_url']) != (PDF_SHA256, URL):
        raise ValueError('494 source manifest no longer binds the drawing hash and URL')
    note = P / 'sources.json'
    entry = json.loads(note.read_text())[0]
    if (entry['file'], entry['sha256'], entry['url']) != (PDF.name, PDF_SHA256, URL):
        raise ValueError('source note does not bind the retained drawing')
    locator = {'path': 'sources.json', 'sha256': blob(note)['sha256'], 'entry': 0}
    identity, deviations = declarations()
    outputs = {'identity.json': identity, 'deviations.json': deviations}
    with tempfile.TemporaryDirectory(prefix='pod-j2-import-') as temp:
        dest = Path(temp) / 'acquisition' if verify else P / 'acquisition'
        manifest = import_historical_pdf(PDF, P, locator, 'J2', dest)
        if verify:
            expected = {x.name: x.read_bytes() for x in (P / 'acquisition').iterdir()}
            actual = {x.name: x.read_bytes() for x in dest.iterdir()}
            assert actual == expected, 'Acquisition replay differs'
    acquired = manifest['parts'][0]
    assert acquired['final_url'] is None and acquired['fetched_at'] is None
    assert acquired['redirect_provenance'] == 'unknown' and acquired['sha256'] == PDF_SHA256
    for name, doc in outputs.items():
        path = P / name
        if verify:
            assert json.loads(path.read_text()) == doc, name
        else:
            path.write_text(json.dumps(doc, indent=2) + '\n')
    record = prepare_external_record(ROOT, {**blob(P / 'identity.json'), 'locator': '/'},
                                     blob(P / 'acquisition/manifest.json'), 'J2',
                                     {**blob(P / 'deviations.json'), 'index': 0})
    dependencies = qualify_external_record(record, ROOT)
    assert (record['lcsc'], record['stock']) == ('NO_LCSC', None)
    report = {'schema': 'pod-j2-historical-source/1', 'source_pdf': blob(PDF), 'source_note': blob(note),
              'capture_time_basis': blob(P / 'capture-time-basis.json'), 'reference': 'J2',
              'dependencies': dependencies, 'acquisition_method': acquired['acquisition_method'],
              'redirect_provenance': acquired['redirect_provenance'], 'final_url': acquired['final_url'],
              'fetched_at': acquired['fetched_at'], 'captured_at': acquired['captured_at'],
              'lcsc': record['lcsc'], 'stock': record['stock'],
              'limits': ['captured_at is filesystem-derived (file mtime), owner-accepted administrative provenance, '
                         'not a measured original HTTP fetch (capture-time-basis.json).',
                         'Historical import does not establish live acquisition or redirect history.',
                         'No native schematic, board, intent or existing capture is changed by this step.']}
    for name, doc in [('132134.json', record), ('report.json', report)]:
        path = P / name
        if verify:
            assert json.loads(path.read_text()) == doc, name
        else:
            path.write_text(json.dumps(doc, indent=2) + '\n')
    print('PASS: J2 132134 external record (NO_LCSC, stock null) replays from the retained drawing and pinned note')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    run(parser.parse_args().verify)
