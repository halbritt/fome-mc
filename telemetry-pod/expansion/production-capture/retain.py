"""Retain the production emission durably and install it as the telemetry-pod project (AGENTEE-445).

The retained evidence directory is named after the producer pin: evidence/emission-7d5b0d4d/ since j6b2 (the
AGENTEE-466 runtime); evidence/emission-81e387ee/ is the superseded j6/j6b retention, kept in git history only.

The emission is pipeline.py's stage 'emission.schematic_stage production (AGENTEE-445)': the prepared
campaign's own binding-fill, emit-schematic and forward-annotate steps, each with an agent-ee stage receipt.
This script copies, never regenerates or edits:

- evidence/emission-7d5b0d4d/design/: the complete emitted candidate tree (every emitter input and output:
  bound intent, layout, captured symbol and footprint libraries, scaffold project). Files under telemetry-pod/
  are byte copies of this repository's files at the same paths; they are pinned by sha256 in MANIFEST.json and
  checked against the repository instead of being duplicated;
- evidence/emission-7d5b0d4d/receipts/: each step's receipt.json with its execution record, console and
  outputs (the receipts' own input copies are the design tree above);
- evidence/emission-7d5b0d4d/prepared/: the driver receipt, campaign, plan, scope, dry-run record and result of
  the bounded two-iteration preparation the emission ran from, and pipeline.json;
- MANIFEST.json and SHA256SUMS.

--install writes telemetry-pod/telemetry-pod.kicad_sch, .kicad_pcb, .kicad_pro and .kicad_dru as byte copies of
the retained design/project files, and the project's sym-lib-table and fp-lib-table as the emitted candidate's
tables with only their ${KIPRJMOD}/../ prefix relocated to the retained design root, and the bound project-local
3D models (FOMEMC-34) at telemetry-pod/inputs/models/, where the installed board's ${KIPRJMOD}/inputs/models/
references resolve. --check verifies all of it.

j6b (review H1): the complete prepared directory the campaign launches from (inputs/, the scaffold and content
pre-receipts, dry-run/) is retained exactly as prepared-tree.json (every relative path with its sha256, and the
empty directories), its bytes either a repository file outside this evidence (by path) or a content-addressed
blob under prepared-blobs/. --materialize-prepared OUT rebuilds it byte for byte for the runtime check and launch.

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
# AGENTEE-484: the decoupling-repair emission (same producer pin) is a NEW retention; evidence/emission-7d5b0d4d/
# is the superseded pre-repair retention, kept unchanged.
DEST = HERE / 'evidence/emission-7d5b0d4d-agentee484'
SUPERSEDED = HERE / 'evidence/emission-81e387ee'  # j6/j6b retention (producer 81e387ee); removed at j6b2
POD = ROOT / 'telemetry-pod'
REPO_SUBTREE = 'telemetry-pod/'
PROJECT = {'telemetry-pod.kicad_sch', 'telemetry-pod.kicad_pcb', 'telemetry-pod.kicad_pro', 'telemetry-pod.kicad_dru'}
TABLES = ('sym-lib-table', 'fp-lib-table')
RELOCATE = ('${KIPRJMOD}/../', '${KIPRJMOD}/' + DEST.relative_to(POD).as_posix() + '/design/')
PREPARED = ('driver-receipt.json', 'campaign.json', 'plan.json', 'scope.json', 'dry-run-record.json',
            'dry-run/result.json', 'dry-run/REPORT.md', 'dry-run/candidate.json')
RECEIPT_SKIP = ('inputs', 'run/design', 'run/home')
MODELS = 'inputs/models/'  # relative to the candidate project directory (composition/project-models.json)
PREPARED_TREE, BLOBS = 'prepared-tree.json', 'prepared-blobs'
# Repository bytes a prepared file may be recorded by: tracked or unignored files outside the retained evidence.
EXCLUDE = tuple(d.relative_to(ROOT).as_posix() + '/' for d in (DEST, SUPERSEDED, HERE / 'evidence/production-runtime-j6b'))


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
    manifest['prepared_tree'] = retain_prepared(out / 'prepared')
    shutil.copyfile(out / 'emission/native.xml', DEST / 'native.xml')
    manifest['pipeline_sha256'], manifest['native_xml_sha256'] = sha(out / 'pipeline.json'), sha(out / 'emission/native.xml')
    manifest['project_install'] = {
        **{name: {'source': 'design/project/' + name, 'sha256': sha(design / 'project' / name)} for name in sorted(PROJECT)},
        **{name: {'source': 'design/project/' + name, 'relocation': list(RELOCATE),
                  'sha256': hashlib.sha256(relocated((design / 'project' / name).read_bytes())).hexdigest()}
           for name in TABLES},
        **{MODELS + p.name: {'source': f'design/project/{MODELS}{p.name}', 'sha256': sha(p)}
           for p in sorted((design / 'project' / MODELS).iterdir())}}
    (DEST / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n')
    sums = ''.join(f'{sha(DEST / rel)}  {rel}\n' for rel in files(DEST) if rel != 'SHA256SUMS')
    (DEST / 'SHA256SUMS').write_text(sums)
    return manifest


def repository_index():
    import subprocess
    listed = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                            capture_output=True, check=True).stdout.split(b'\0')
    index = {}
    for rel in sorted(r.decode() for r in listed if r):
        path = ROOT / rel
        if rel.startswith(EXCLUDE) or path.is_symlink() or not path.is_file():
            continue
        index.setdefault(sha(path), rel)
    return index


def retain_prepared(prepared):
    """The exact prepared tree: path -> sha256 (repository file or blob), and its empty directories."""
    index, tree, empty = repository_index(), {}, []
    for path in sorted(Path(prepared).rglob('*')):
        rel = path.relative_to(prepared).as_posix()
        if path.is_symlink():
            raise SystemExit(f'prepared tree holds a link: {rel}')
        if path.is_dir():
            if not any(path.iterdir()):
                empty.append(rel)
            continue
        digest = sha(path)
        if (path.stat().st_mode & 0o777) != 0o644:
            raise SystemExit(f'prepared file {rel} mode {oct(path.stat().st_mode & 0o777)} is not 0644')
        if digest in index:
            tree[rel] = {'sha256': digest, 'repository': index[digest]}
        else:
            blob = DEST / BLOBS / digest
            blob.parent.mkdir(parents=True, exist_ok=True)
            if not blob.exists():
                shutil.copyfile(path, blob)
            tree[rel] = {'sha256': digest, 'blob': f'{BLOBS}/{digest}'}
    record = {'schema': 'pod-capture.prepared-tree/1', 'files': tree, 'empty_directories': empty,
              'mode': '0644', 'count': len(tree)}
    (DEST / PREPARED_TREE).write_text(json.dumps(record, indent=1, sort_keys=True) + '\n')
    return {'path': PREPARED_TREE, 'sha256': sha(DEST / PREPARED_TREE), 'files': len(tree),
            'blobs': len({e['sha256'] for e in tree.values() if 'blob' in e})}


def prepared_problems():
    record = json.loads((DEST / PREPARED_TREE).read_text())
    problems = []
    for rel, item in record['files'].items():
        source = ROOT / item['repository'] if 'repository' in item else DEST / item['blob']
        if not source.is_file() or sha(source) != item['sha256']:
            problems.append(f'prepared tree {rel} ({item.get("repository") or item["blob"]})')
    return problems


def materialize(out):
    """Rebuild the complete prepared directory byte for byte (a new directory; never overwrites)."""
    out = Path(out)
    if out.exists():
        raise SystemExit(f'{out} exists')
    problems = prepared_problems()
    if problems:
        raise SystemExit('prepared tree unresolvable: ' + '; '.join(problems[:5]))
    record = json.loads((DEST / PREPARED_TREE).read_text())
    for rel, item in record['files'].items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / item['repository'] if 'repository' in item else DEST / item['blob'], target)
        target.chmod(0o644)
        if sha(target) != item['sha256']:
            raise SystemExit(f'materialized {rel} differs')
    for rel in record['empty_directories']:
        (out / rel).mkdir(parents=True, exist_ok=True)
    print(f"materialized {record['count']} prepared files and {len(record['empty_directories'])} empty directories into {out}")


def install():
    manifest = json.loads((DEST / 'MANIFEST.json').read_text())
    for name, item in manifest['project_install'].items():
        data = (DEST / item['source']).read_bytes()
        (POD / name).parent.mkdir(parents=True, exist_ok=True)
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
    installed_models = {f'{MODELS}{p.name}' for p in (POD / MODELS).iterdir()} if (POD / MODELS).is_dir() else set()
    if installed_models != {n for n in manifest['project_install'] if n.startswith(MODELS)}:
        problems.append(f'telemetry-pod/{MODELS} holds other files than the retained project models')
    if 'prepared_tree' in manifest:
        if sha(DEST / PREPARED_TREE) != manifest['prepared_tree']['sha256']:
            problems.append('prepared-tree.json differs from MANIFEST.json')
        problems += prepared_problems()
    emitted = manifest['emission']
    for key in ('schematic', 'board'):
        if manifest['design'][emitted[key]['path']]['sha256'] != emitted[key]['sha256']:
            problems.append(f'emitted {key} differs from the emission stage record')
    if problems:
        raise SystemExit('retained emission check failed:\n  ' + '\n  '.join(problems))
    print(f"retained emission OK: {len(listed)} retained files, {len(manifest['design'])} design inputs "
          f"({sum(i['retained'] == 'repository path' for i in manifest['design'].values())} repository paths), "
          f"{len(manifest['project_install'])} installed project files"
          + (f", prepared tree {manifest['prepared_tree']['files']} files ({manifest['prepared_tree']['blobs']} blobs)"
             if 'prepared_tree' in manifest else ''))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('pipeline_out', nargs='?')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--materialize-prepared', metavar='OUT')
    args = parser.parse_args()
    if args.materialize_prepared:
        materialize(args.materialize_prepared)
        sys.exit(0)
    if args.check:
        check()
        sys.exit(0)
    if not args.pipeline_out:
        parser.error('PIPELINE_OUT required')
    retain(args.pipeline_out)
    if args.install:
        install()
    check() if args.install else print('retained; not installed')
