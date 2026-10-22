"""Retain the j6 production emission durably and install it as the telemetry-pod project (AGENTEE-445).

The emission is pipeline.py's stage 'emission.schematic_stage production (AGENTEE-445)': the prepared
campaign's own binding-fill, emit-schematic and forward-annotate steps, each with an agent-ee stage receipt.
This script copies, never regenerates or edits:

- evidence/emission-81e387ee/design/: the complete emitted candidate tree (every emitter input and output:
  bound intent, layout, captured symbol and footprint libraries, scaffold project). Files under telemetry-pod/
  are byte copies of this repository's files at the same paths; they are pinned by sha256 in MANIFEST.json and
  checked against the repository instead of being duplicated;
- evidence/emission-81e387ee/receipts/: each step's receipt.json with its execution record, console and
  outputs (the receipts' own input copies are the design tree above);
- evidence/emission-81e387ee/prepared/: the driver receipt, campaign, plan, scope, dry-run record and result of
  the bounded two-iteration preparation the emission ran from, and pipeline.json;
- MANIFEST.json and SHA256SUMS.

--install writes telemetry-pod/telemetry-pod.kicad_sch, .kicad_pcb, .kicad_pro and .kicad_dru as byte copies of
the retained design/project files, and the project's sym-lib-table and fp-lib-table as the emitted candidate's
tables with only their ${KIPRJMOD}/../ prefix relocated to the retained design root. --check verifies all of it.

Usage (fome-mc root):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py PIPELINE_OUT [--install]
  /usr/bin/python3 telemetry-pod/expansion/production-capture/retain.py --check
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEST = HERE / 'evidence/emission-81e387ee'
POD = ROOT / 'telemetry-pod'
REPO_SUBTREE = 'telemetry-pod/'
PROJECT = {'telemetry-pod.kicad_sch', 'telemetry-pod.kicad_pcb', 'telemetry-pod.kicad_pro', 'telemetry-pod.kicad_dru'}
TABLES = ('sym-lib-table', 'fp-lib-table')
RELOCATE = ('${KIPRJMOD}/../', '${KIPRJMOD}/' + DEST.relative_to(POD).as_posix() + '/design/')
PREPARED = ('driver-receipt.json', 'campaign.json', 'plan.json', 'scope.json', 'dry-run-record.json',
            'dry-run/result.json', 'dry-run/REPORT.md', 'dry-run/candidate.json')
RECEIPT_SKIP = ('inputs', 'run/design', 'run/home')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def files(root):
    return sorted(p.relative_to(root).as_posix() for p in Path(root).rglob('*') if p.is_file() and not p.is_symlink())


def relocated(table):
    text = table.decode()
    if RELOCATE[0] not in text or '${KIPRJMOD}' in text.replace(RELOCATE[0], ''):
        raise SystemExit('library table has an unexpected project-relative path')
    return text.replace(RELOCATE[0], RELOCATE[1]).encode()


def retain(out):
    out = Path(out).resolve()
    stage = json.loads((out / 'pipeline.json').read_text())['stages']['emission.schematic_stage production (AGENTEE-445)']
    if stage['status'] != 'accepted':
        raise SystemExit(f'emission stage not accepted: {stage}')
    emitted = stage['detail']
    if DEST.exists():
        raise SystemExit(f'{DEST} exists; retained evidence is never overwritten')
    design = out / 'emission/design'
    manifest = {'schema': 'pod-capture.emission-retention/1', 'emission': emitted, 'design': {}, 'receipts': {},
                'prepared': {}}
    for rel in files(design):
        digest = sha(design / rel)
        if rel.startswith(REPO_SUBTREE):
            if not (ROOT / rel).is_file() or sha(ROOT / rel) != digest:
                raise SystemExit(f'design file {rel} is not the repository file at that path')
            manifest['design'][rel] = {'sha256': digest, 'retained': 'repository path'}
            continue
        (DEST / 'design' / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(design / rel, DEST / 'design' / rel)
        manifest['design'][rel] = {'sha256': digest, 'retained': 'design/' + rel}
    for receipt in emitted['receipts']:
        source = out / receipt['receipt']
        name = Path(receipt['receipt']).name
        for rel in files(source):
            if any(rel == s or rel.startswith(s + '/') for s in RECEIPT_SKIP):
                continue
            (DEST / 'receipts' / name / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / rel, DEST / 'receipts' / name / rel)
            manifest['receipts'][f'{name}/{rel}'] = sha(source / rel)
        if sha(source / 'receipt.json') != receipt['receipt_sha256']:
            raise SystemExit(f'receipt {name} differs from the pipeline record')
    for rel in PREPARED:
        source = out / 'prepared' / rel
        (DEST / 'prepared' / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, DEST / 'prepared' / rel)
        manifest['prepared'][rel] = sha(source)
    shutil.copyfile(out / 'pipeline.json', DEST / 'pipeline.json')
    shutil.copyfile(out / 'emission/native.xml', DEST / 'native.xml')
    manifest['pipeline_sha256'], manifest['native_xml_sha256'] = sha(out / 'pipeline.json'), sha(out / 'emission/native.xml')
    manifest['project_install'] = {
        **{name: {'source': 'design/project/' + name, 'sha256': sha(design / 'project' / name)} for name in sorted(PROJECT)},
        **{name: {'source': 'design/project/' + name, 'relocation': list(RELOCATE),
                  'sha256': hashlib.sha256(relocated((design / 'project' / name).read_bytes())).hexdigest()}
           for name in TABLES}}
    (DEST / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n')
    sums = ''.join(f'{sha(DEST / rel)}  {rel}\n' for rel in files(DEST) if rel != 'SHA256SUMS')
    (DEST / 'SHA256SUMS').write_text(sums)
    return manifest


def install():
    manifest = json.loads((DEST / 'MANIFEST.json').read_text())
    for name, item in manifest['project_install'].items():
        data = (DEST / item['source']).read_bytes()
        (POD / name).write_bytes(relocated(data) if name in TABLES else data)


def check():
    problems = []
    for line in (DEST / 'SHA256SUMS').read_text().splitlines():
        digest, rel = line.split('  ', 1)
        if not (DEST / rel).is_file() or sha(DEST / rel) != digest:
            problems.append(f'SHA256SUMS: {rel}')
    listed = {line.split('  ', 1)[1] for line in (DEST / 'SHA256SUMS').read_text().splitlines()}
    problems += [f'unlisted: {rel}' for rel in files(DEST) if rel != 'SHA256SUMS' and rel not in listed]
    manifest = json.loads((DEST / 'MANIFEST.json').read_text())
    for rel, item in manifest['design'].items():
        path = ROOT / rel if item['retained'] == 'repository path' else DEST / item['retained']
        if not path.is_file() or sha(path) != item['sha256']:
            problems.append(f'design input {rel} ({item["retained"]})')
    for name, item in manifest['project_install'].items():
        if not (POD / name).is_file() or sha(POD / name) != item['sha256']:
            problems.append(f'installed telemetry-pod/{name} differs from the retained emission')
    emitted = manifest['emission']
    for key in ('schematic', 'board'):
        if manifest['design'][emitted[key]['path']]['sha256'] != emitted[key]['sha256']:
            problems.append(f'emitted {key} differs from the emission stage record')
    if problems:
        raise SystemExit('retained emission check failed:\n  ' + '\n  '.join(problems))
    print(f"retained emission OK: {len(listed)} retained files, {len(manifest['design'])} design inputs "
          f"({sum(i['retained'] == 'repository path' for i in manifest['design'].values())} repository paths), "
          f"{len(manifest['project_install'])} installed project files")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('pipeline_out', nargs='?')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        check()
        sys.exit(0)
    if not args.pipeline_out:
        parser.error('PIPELINE_OUT required')
    retain(args.pipeline_out)
    if args.install:
        install()
    check() if args.install else print('retained; not installed')
