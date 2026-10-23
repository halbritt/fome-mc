"""Attribute the telemetry-pod DRC and pod verify-io counts to exact branch identities (AGENTEE-207 j6b2).

Report-only: reads git snapshots and writes evidence, never a capture input or design file. For each fome-mc
commit given, a fresh `git archive` snapshot (made a throwaway git repository, as verify_io_map.py needs one)
is checked natively:

- `kicad-cli pcb drc --severity-all --schematic-parity --format json` on telemetry-pod/telemetry-pod.kicad_pcb;
  the violations and unconnected items are normalized (UUIDs dropped; type, severity, item descriptions and
  positions kept) and listed per item;
- the unconnected count is recomputed independently with pcbnew: the board's tracks, vias and zones are counted,
  and with no copper the minimum number of connections is sum(pads on a net - 1) over nets with two or more
  pads, each net's pads being separate copper islands;
- `scripts/verify_io_map.py --project telemetry-pod` (the `make verify-io PROJECT=telemetry-pod` command): its
  [ERROR] lines are listed;
- the identities: commit, tree, board/schematic sha256, the native netlist sha256 with its volatile <date> line
  removed, and the io-map/contract/bindings/paths sha256.

The lists of every commit are diffed against the first (the frozen reference), item by item.

Usage (fome-mc root, inside one admitted native-admit suite lease):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/count_attribution.py OUT_DIR COMMIT [COMMIT ...]
  /usr/bin/python3 telemetry-pod/expansion/production-capture/count_attribution.py analyze OUT_DIR   (derived; reads only)
"""
import collections
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
IO_INPUTS = ('telemetry-pod/io-map.csv', 'contracts/telemetry-pod.interface.json',
             'telemetry-pod/pinout-checks/bindings.json', 'telemetry-pod/pinout-checks/paths.json',
             'scripts/verify_io_map.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, cwd=ROOT):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, check=True).stdout


def items(entry):
    return sorted((i.get('description', ''), round(i['pos']['x'], 4), round(i['pos']['y'], 4)) for i in entry.get('items', []))


def normalize(report, key):
    return sorted(({'type': v['type'], 'severity': v['severity'], 'description': v['description'], 'items': items(v)}
                   for v in report.get(key, [])), key=lambda v: json.dumps(v, sort_keys=True))


def copper(board):
    script = r'''
import json, sys, collections, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
pads = collections.Counter(p.GetNetname() for p in b.GetPads() if p.GetNetCode() > 0)
print(json.dumps({"tracks": sum(1 for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T),
                  "vias": sum(1 for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T),
                  "zones": b.GetAreaCount(), "nets_with_pads": len(pads),
                  "min_connections": sum(n - 1 for n in pads.values() if n > 1)}))
'''
    done = subprocess.run(['/usr/bin/python3', '-c', script, str(board)], capture_output=True, text=True)
    return json.loads(done.stdout.strip().splitlines()[-1])


def check(commit, work):
    snap = work / commit
    snap.mkdir(parents=True)
    archive = subprocess.Popen(['git', 'archive', commit], cwd=ROOT, stdout=subprocess.PIPE)
    subprocess.run(['tar', '-x', '-C', str(snap)], stdin=archive.stdout, check=True)
    archive.wait()
    subprocess.run(['git', 'init', '-q'], cwd=snap, check=True)
    subprocess.run(['git', '-c', 'user.name=attribution', '-c', 'user.email=attribution@localhost', 'add', '-A'], cwd=snap,
                   check=True, capture_output=True)
    subprocess.run(['git', '-c', 'user.name=attribution', '-c', 'user.email=attribution@localhost', 'commit', '-q', '-m',
                    f'snapshot of fome-mc {commit}'], cwd=snap, check=True)
    pod = snap / 'telemetry-pod'
    board, schematic = pod / 'telemetry-pod.kicad_pcb', pod / 'telemetry-pod.kicad_sch'
    drc_json = work / f'{commit}.drc.json'
    drc = subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity',
                          '-o', str(drc_json), str(board)], capture_output=True, text=True)
    netlist = work / f'{commit}.net.xml'
    net = subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(netlist),
                          str(schematic)], capture_output=True, text=True)
    stable = re.sub(rb'<date>[^<]*</date>', b'<date/>', netlist.read_bytes()) if netlist.is_file() else b''
    io = subprocess.run(['/usr/bin/python3', 'scripts/verify_io_map.py', '--project', 'telemetry-pod'], cwd=snap,
                        capture_output=True, text=True)
    errors = [l.strip() for l in (io.stdout + io.stderr).splitlines() if '[ERROR]' in l]
    report = json.loads(drc_json.read_text())
    violations, unconnected = normalize(report, 'violations'), normalize(report, 'unconnected_items')
    return {
        'identity': {'commit': git('rev-parse', commit).decode().strip(),
                     'tree': git('rev-parse', commit + '^{tree}').decode().strip(),
                     'board_sha256': sha(board.read_bytes()), 'schematic_sha256': sha(schematic.read_bytes()),
                     'netlist_sha256_without_date': sha(stable),
                     'io_inputs': {p: sha((snap / p).read_bytes()) for p in IO_INPUTS if (snap / p).is_file()}},
        'drc': {'exit': drc.returncode, 'violations': len(violations), 'unconnected': len(unconnected),
                'schematic_parity': len(report.get('schematic_parity', [])),
                'by_type': dict(collections.Counter(v['type'] for v in violations)),
                'violation_list': violations, 'unconnected_list': unconnected},
        'copper': copper(board), 'netlist_exit': net.returncode,
        'verify_io': {'exit': io.returncode, 'errors': len(errors), 'error_list': errors}}


def diff(a, b):
    sa = {json.dumps(x, sort_keys=True) for x in a}
    sb = {json.dumps(x, sort_keys=True) for x in b}
    return {'only_reference': sorted(sa - sb), 'only_other': sorted(sb - sa), 'common': len(sa & sb)}


def main(out, commits):
    out = Path(out)
    out.mkdir(parents=True)
    results = {}
    with tempfile.TemporaryDirectory(prefix='pod-attribution-') as tmp:
        for commit in commits:
            results[commit] = check(commit, Path(tmp))
            (out / f'{commit}.json').write_text(json.dumps(results[commit], indent=1, sort_keys=True) + '\n')
            print(commit, json.dumps({k: results[commit]['drc'][k] for k in ('exit', 'violations', 'unconnected')}),
                  'verify-io', results[commit]['verify_io']['exit'], results[commit]['verify_io']['errors'], flush=True)
    ref = commits[0]
    diffs = {c: {'violations': diff(results[ref]['drc']['violation_list'], results[c]['drc']['violation_list']),
                 'unconnected': diff(results[ref]['drc']['unconnected_list'], results[c]['drc']['unconnected_list']),
                 'verify_io': diff(results[ref]['verify_io']['error_list'], results[c]['verify_io']['error_list'])}
             for c in commits[1:]}
    summary = {'schema': 'pod-capture.count-attribution/1', 'reference': ref, 'commits': commits,
               'counts': {c: {'drc_violations': r['drc']['violations'], 'drc_by_type': r['drc']['by_type'],
                              'drc_unconnected': r['drc']['unconnected'], 'copper': r['copper'],
                              'verify_io_errors': r['verify_io']['errors'], 'identity': r['identity']}
                          for c, r in results.items()},
               'diffs_against_reference': {c: {k: {'only_reference': len(v['only_reference']), 'only_other': len(v['only_other']),
                                                   'common': v['common']} for k, v in d.items()} for c, d in diffs.items()}}
    (out / 'diffs.json').write_text(json.dumps(diffs, indent=1, sort_keys=True) + '\n')
    (out / 'summary.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
    print(json.dumps(summary['diffs_against_reference'], sort_keys=True))


def analyze(out):
    """Derive the attribution from a finished run's JSON (report-only; no check is rerun)."""
    out = Path(out)
    summary = json.loads((out / 'summary.json').read_text())
    ref, commits = summary['reference'], summary['commits']
    runs = {c: json.loads((out / f'{c}.json').read_text()) for c in commits}
    diffs = json.loads((out / 'diffs.json').read_text())
    pad = re.compile(r'^(?:PTH pad|Pad) (\S+) \[([^\]]*)\] of (\S+)(?: on (\S+))?$')  # SMD pads name a layer
    current = commits[-1]

    def pads(item):
        return [pad.match(d) for d, _, _ in item['items']]
    unconnected = runs[current]['drc']['unconnected_list']
    pad_pairs = [u for u in unconnected if len(u['items']) == 2 and all(pads(u))
                 and pads(u)[0].group(2) == pads(u)[1].group(2)]
    tie_breaks = []
    for c in commits[1:]:
        only_ref = [json.loads(x) for x in diffs[c]['unconnected']['only_reference']]
        only_other = [json.loads(x) for x in diffs[c]['unconnected']['only_other']]
        strip = lambda u: sorted((m.group(1), m.group(2), m.group(3), x, y) for m, (_, x, y) in zip(pads(u), u['items']))  # noqa: E731
        tie_breaks.append({'commit': c, 'differing_items': len(only_ref) + len(only_other),
                           'equal_ignoring_copper_layer_label': sorted(map(strip, only_ref)) == sorted(map(strip, only_other))})
    by_type = {}
    for v in runs[current]['drc']['violation_list']:
        by_type.setdefault(v['type'], []).append({'description': v['description'], 'items': [d for d, _, _ in v['items']]})
    io = runs[current]['verify_io']['error_list']
    frozen_io = runs[commits[1]]['verify_io']['error_list'] if len(commits) > 1 else []
    result = {
        'schema': 'pod-capture.count-attribution-analysis/1', 'reference': ref, 'current': current,
        'identities': {c: runs[c]['identity'] for c in commits},
        'drc_violations': {'count': runs[current]['drc']['violations'], 'by_type': by_type,
                           'identical_to_reference': {c: diffs[c]['violations']['only_reference'] == [] and
                                                      diffs[c]['violations']['only_other'] == [] for c in commits[1:]}},
        'drc_unconnected': {'count': len(unconnected), 'pad_to_pad_same_net': len(pad_pairs),
                            'copper': {c: runs[c]['copper'] for c in commits},
                            'differences_against_reference': tie_breaks,
                            'note': ('kicad-cli DRC reports unconnected items at its own granularity; the pcbnew pad '
                                     'count min_connections is not that number and is not used to reproduce it')},
        'verify_io': {'count': len(io), 'common_with_second_commit': sorted(set(io) & set(frozen_io)),
                      'only_current': len(set(io) - set(frozen_io)),
                      'by_kind': dict(collections.Counter(re.sub(r'^\[ERROR\] ', '', e).split(':')[0] for e in io)),
                      'identical_to_reference': {c: diffs[c]['verify_io']['only_reference'] == [] and
                                                 diffs[c]['verify_io']['only_other'] == [] for c in commits[1:]}}}
    (out / 'analysis.json').write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk not in ('by_type', 'copper')})
                      for k, v in result.items() if k not in ('identities',)}, sort_keys=True)[:3000])


if __name__ == '__main__':
    if sys.argv[1] == 'analyze':
        analyze(sys.argv[2])
    else:
        main(sys.argv[1], sys.argv[2:])
