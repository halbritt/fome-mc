"""Trace every current purchased instance to committed catalog/PDF evidence.

This is an offline prerequisite inventory, not a parts/1 manifest or approval.
Only the repository's tracked telemetry-pod captures are searched.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import inspect
import json
from pathlib import Path
import subprocess

from agent_ee.jlc_stock_capture import validate_capture

ROOT = Path(__file__).resolve().parents[3]
INTENT = 'telemetry-pod/expansion/series-divider/native-candidate/inputs/intent.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(captured_paths=None):
    tracked = subprocess.check_output(
        ['git', '-C', str(ROOT), 'ls-files', '-z', '--', 'telemetry-pod'],
    ).decode().split('\0')
    if captured_paths is not None:
        if not set(captured_paths) <= set(tracked):
            raise ValueError('Retained dependency is no longer tracked')
        tracked = sorted(captured_paths)
    pdfs = defaultdict(list)
    catalogs = defaultdict(list)
    inspected = {}
    for name in sorted(filter(None, tracked)):
        path = ROOT / name
        if path.suffix.lower() == '.pdf':
            pdfs[sha(path)].append(name)
        elif path.name == 'catalog.json':
            doc = json.loads(path.read_text())
            if not isinstance(doc, dict) or doc.get('schema') != 'agent-ee.jlc-catalog/1':
                continue
            def read_response(relative):
                target = (path.parent / relative).resolve()
                target.relative_to(ROOT)
                if target.relative_to(ROOT).as_posix() not in tracked:
                    raise ValueError('Catalog depends on untracked response: ' + str(target))
                inspected[target.relative_to(ROOT).as_posix()] = sha(target)
                return target.read_bytes()
            validate_capture(doc, read_response)
            inspected[name] = sha(path)
            for lcsc, row in doc['parts'].items():
                request, = [r for r in doc['requests'] if r['lcsc'] == lcsc]
                catalogs[lcsc].append({'catalog': name, 'catalog_sha256': sha(path),
                    'mpn': row['mpn'], 'manufacturer': row['mfr'],
                    'package': row['package'], 'historical_stock': row['stock'],
                    'fetched_at': request['fetched_at'],
                    'response': (path.parent / request['response']['path']).relative_to(ROOT).as_posix(),
                    'response_sha256': request['response']['sha256']})
    source = json.loads((ROOT / INTENT).read_text())
    groups = {}
    exclusions = []
    for c in source['components']:
        b = c.get('part_binding', {})
        if 'LCSC' not in b:
            kind = ('probe' if 'AGENT_EE_Probe' in b else
                    'copper_jumper' if c['reference'].startswith('JP') and c.get('in_bom') is False else
                    'power_symbol' if c['reference'].startswith('#') else 'unbound')
            exclusions.append({'reference': c['reference'], 'kind': kind})
            continue
        key = (b['LCSC'], b['Partnumber'], b['Manufacturer'])
        group = groups.setdefault(key, {'lcsc': key[0], 'mpn': key[1], 'manufacturer': key[2],
                                       'instances': [], 'datasheets': {}})
        raw = json.loads(b['PARAM_Datasheet'])
        if raw['schema'] != 'agent-ee.datasheet-binding/1' or raw['url'] != b['Datasheet']:
            raise ValueError('Unexpected datasheet binding: ' + c['reference'])
        digest = raw['sha256']
        group['datasheets'].setdefault(digest, {'url': raw['url'], 'references': [],
            'matching_committed_pdfs': pdfs[digest]})['references'].append(c['reference'])
        for name in pdfs[digest]:
            inspected[name] = digest
        group['instances'].append({'id': c['id'], 'reference': c['reference'],
            'lib_id': c['lib_id'], 'footprint': c['footprint'], 'value': c['value'],
            'datasheet_sha256': digest})
    parts = []
    for key, group in sorted(groups.items()):
        group['instances'].sort(key=lambda c: c['reference'])
        group['matching_catalogs'] = [c for c in catalogs[key[0]]
            if c['mpn'] == key[1] and c['manufacturer'] == key[2]]
        group['conflicting_catalogs'] = [c for c in catalogs[key[0]]
            if c['mpn'] != key[1] or c['manufacturer'] != key[2]]
        group['missing'] = []
        if not group['matching_catalogs']:
            group['missing'].append('replayable exact-identity supplier capture')
        if any(not d['matching_committed_pdfs'] for d in group['datasheets'].values()):
            group['missing'].append('committed bytes matching bound datasheet SHA256')
        for instance in group['instances']:
            instance['has_both_sources'] = bool(group['matching_catalogs'] and
                group['datasheets'][instance['datasheet_sha256']]['matching_committed_pdfs'])
        parts.append(group)
    counts = Counter(e['kind'] for e in exclusions)
    return {'schema': 'pod-parts-source-trace/1', 'intent': {'path': INTENT, 'sha256': sha(ROOT / INTENT)},
        'search_scope': 'tracked telemetry-pod PDFs and agent-ee.jlc-catalog/1 catalogs only',
        'capture_validator_sha256': sha(Path(inspect.getfile(validate_capture))),
        'summary': {'source_components': len(source['components']),
            'purchased_instances': sum(len(p['instances']) for p in parts), 'identity_groups': len(parts),
            'groups_with_both_sources': sum(not p['missing'] for p in parts),
            'instances_in_fully_sourced_groups': sum(len(p['instances']) for p in parts if not p['missing']),
            'instances_with_both_sources': sum(i['has_both_sources'] for p in parts for i in p['instances']),
            'exclusions': dict(sorted(counts.items()))},
        'parts': parts, 'excluded_instances': sorted(exclusions, key=lambda e:e['reference']),
        'inspected_dependencies': dict(sorted(inspected.items())),
        'limits': ['Not a qualified parts manifest or approval receipt.',
            'PDF hash match does not establish applicability or acquisition provenance.',
            'Historical supplier stock is not live stock or assembly eligibility.',
            'No missing source is substituted from another MPN or datasheet revision.',
            'Full CAD assignments, datasheet acquisition records, decision sources and parts_subset remain required.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if bool(args.out) == bool(args.verify):
        parser.error('Choose exactly one of --out or --verify')
    retained = json.loads(args.verify.read_text()) if args.verify else None
    report = build(retained['inspected_dependencies'] if retained else None)
    if args.verify:
        assert report == retained, 'Trace differs from retained evidence'
    else:
        with args.out.open('x') as stream:
            json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps(report['summary'], sort_keys=True))
