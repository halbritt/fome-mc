#!/usr/bin/env python3
"""Operating-temperature rating inventory for the current microSD pod source.

Reads the selected parts from ../../storage-microsd/inputs/intent.json, the
captured LCSC catalog responses under ../../**/responses/, and the authored
datasheet citations in datasheet-ratings.json. Writes temperature-ratings.json
(or, with --check, compares against the committed file). It then re-hashes
each cited datasheet PDF and searches the cited page with pdftotext when the
bytes are available, printing one line per citation; an unavailable datasheet
is reported, never assumed. A hash mismatch or missing page text exits 1.

    python3 temperature_ratings.py [--check] [--pdf REF=PATH ...]
"""
import argparse
import glob
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPANSION = HERE.parents[1]
REPO = EXPANSION.parents[1]
INTENT = EXPANSION / 'storage-microsd/inputs/intent.json'
OUTPUT = HERE / 'temperature-ratings.json'
CRITERION_MAX_C = 105  # REQUIREMENTS.md POD-ME-3: "Parts rated to 105 °C or higher."
ATTRIBUTE = re.compile(r'"attribute_name_en":"Operating Temperature","attribute_value_name":"([^"]*)"')
RANGE = re.compile(r'^([+-]?\d+(?:\.\d+)?)℃~([+-]?\d+(?:\.\d+)?)℃$')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(text):
    value = float(text)
    return int(value) if value.is_integer() else value


def catalog_ratings():
    """First captured response (sorted path order) carrying an Operating Temperature attribute."""
    found = {}
    for path in sorted(glob.glob(str(EXPANSION / '**/responses/C*.json'), recursive=True)):
        lcsc = Path(path).stem
        if lcsc in found:
            continue
        match = ATTRIBUTE.search(Path(path).read_text(encoding='utf-8'))
        if match:
            found[lcsc] = (path, match.group(1))
    return found


def page_text(pdf, page):
    out = subprocess.run(['pdftotext', '-layout', '-f', str(page), '-l', str(page), str(pdf), '-'],
                         capture_output=True, text=True, check=True).stdout
    return ' '.join(out.split())


def datasheet_status(ref, cite, supplied):
    if cite is None:
        return {'status': 'not_captured'}
    candidates = [supplied.get(ref)] if ref in supplied else []
    if cite['repository_path']:
        candidates.append(REPO / cite['repository_path'])
    for pdf in candidates:
        if pdf and Path(pdf).is_file():
            if sha256(pdf) != cite['sha256']:
                return {'status': 'hash_mismatch'}
            text = page_text(pdf, cite['page'])
            missing = [m for m in cite['match'] if m not in text]
            return {'status': 'verified' if not missing else 'page_text_missing', **({'missing': missing} if missing else {})}
    return {'status': 'bytes_not_available_here'}


def build():
    intent = json.loads(INTENT.read_text(encoding='utf-8'))
    cited = json.loads((HERE / 'datasheet-ratings.json').read_text(encoding='utf-8'))['parts']
    catalog = catalog_ratings()
    below, covering, unknown, unbound = [], [], [], []
    for component in sorted(intent['components'], key=lambda c: c['reference']):
        ref = component['reference']
        if ref.startswith('#'):
            continue
        binding = component.get('part_binding') or {}
        lcsc = binding.get('LCSC')
        if not lcsc:
            unbound.append(ref)
            continue
        if lcsc not in catalog:
            unknown.append({'reference': ref, 'mpn': binding.get('Partnumber'), 'lcsc': lcsc})
            continue
        path, value = catalog[lcsc]
        match = RANGE.match(value)
        if not match:
            unknown.append({'reference': ref, 'mpn': binding.get('Partnumber'), 'lcsc': lcsc, 'unparsed': value})
            continue
        low, high = number(match.group(1)), number(match.group(2))
        if high >= CRITERION_MAX_C:
            covering.append(ref)
            continue
        entry = {'reference': ref, 'mpn': binding.get('Partnumber'), 'manufacturer': binding.get('Manufacturer'),
                 'lcsc': lcsc, 'footprint': component.get('footprint'),
                 'catalog': {'path': str(Path(path).relative_to(REPO)), 'sha256': sha256(path),
                             'value': value, 'min_c': low, 'max_c': high}}
        cite = cited.get(ref)
        if cite is None or cite['mpn'] != binding.get('Partnumber'):
            entry['datasheet'] = {'status': 'no_authored_citation'}
        else:
            entry['datasheet'] = ({k: v for k, v in cite['datasheet'].items() if k != 'match'}
                                  if cite['datasheet'] else {'gap': cite['datasheet_gap']})
            if cite['datasheet'] and (cite['datasheet']['min_c'], cite['datasheet']['max_c']) != (low, high):
                raise SystemExit(f'{ref}: datasheet citation disagrees with the captured catalog rating')
        below.append(entry)
    return {'schema': 'pod-temperature-ratings/1',
            'source': {'intent': str(INTENT.relative_to(REPO)), 'intent_sha256': sha256(INTENT)},
            'criterion': {'part_rating_max_c_at_least': CRITERION_MAX_C, 'requirement': 'POD-ME-3'},
            'counts': {'components': len(below) + len(covering) + len(unknown) + len(unbound),
                       'below_criterion': len(below), 'covering_criterion': len(covering),
                       'no_captured_rating': len(unknown), 'no_part_binding': len(unbound)},
            'below_criterion': below,
            'no_captured_rating': unknown,
            'no_part_binding': unbound}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='compare with the committed output; write nothing')
    parser.add_argument('--pdf', action='append', default=[], metavar='REF=PATH',
                        help='local datasheet bytes for a reference whose PDF is not in the repository')
    args = parser.parse_args(argv)
    supplied = dict(item.split('=', 1) for item in args.pdf)
    raw = (json.dumps(build(), indent=2, ensure_ascii=False, sort_keys=True) + '\n').encode('utf-8')
    if args.check:
        same = OUTPUT.read_bytes() == raw
        print('temperature-ratings.json ' + ('matches' if same else 'DIFFERS'))
        code = 0 if same else 1
    else:
        OUTPUT.write_bytes(raw)
        print(f'wrote {OUTPUT.name} sha256 {hashlib.sha256(raw).hexdigest()}')
        code = 0
    cited = json.loads((HERE / 'datasheet-ratings.json').read_text(encoding='utf-8'))['parts']
    for ref, cite in sorted(cited.items()):
        status = datasheet_status(ref, cite['datasheet'], supplied)
        print(f'datasheet {ref}: ' + ' '.join(f'{k}={v}' for k, v in status.items()))
        if status['status'] in ('hash_mismatch', 'page_text_missing'):
            code = 1
    return code


if __name__ == '__main__':
    sys.exit(main())
