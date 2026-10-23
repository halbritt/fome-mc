"""placement-r3: ONE targeted constructive placement of the 22 parts missing from the R2 peak (agent-521 99e8ab55; plan
rev 3). Existing agent-ee 7d5b0d4d code only (the R2 step's tool snapshot); no new placer, scorer or search.
1. INSPECT: on the input board with the R2 diagnostic 287 poses applied (placer_runner._apply_plan on a copy), report
   the existing placer's free-area/capacity diagnostic and run its own fixed-qualification of all 296 held parts.
2. PLACE the 22: the existing placer (place_candidate -> pack, ranked-first-fit-backjump/1), with the 287 R2 poses and
   the 9 sourced parts held fixed, so ONLY the 22 missing parts are searched (local, not global; step_budget 200000,
   the r1 value; no numeric constraint changed).
3. VALIDATE THE ENTIRE ARRANGEMENT under the ORIGINAL policy r1 (all 300 movable, 9 sourced fixed): every pose is
   re-applied to the ORIGINAL input board by placer_runner._evaluate_proposal (pad-geometry identity, native courtyard
   DRC, polygon judge, placement groups, electrical locality, netlist binding, reserved area), plus the placer's own
   _fits edge-margin test (min_courtyard_edge_mm) for every movable part.
Usage: r3_local.py WORK   (WORK holds inputs/ (candidate tree), r2/ (placement-result.json, request.json), netlist.xml)
"""
import copy, json, shutil, sys, traceback
from pathlib import Path
import pcbnew
from agent_ee import placer as P, placer_runner as PR
from agent_ee.placement_probe import extract
from agent_ee.silkscreen import reserve_imu_markings
from agent_ee.storage import digest
W = Path(sys.argv[1])
report = {}
src_tree, base = W / 'inputs', W / 'inputs/project/telemetry-pod.kicad_pcb'
r2 = json.loads((W / 'r2/placement-result.json').read_text())
req = json.loads((W / 'r2/request.json').read_text())
r1_policy = {k: v for k, v in req['policy'].items() if k not in ('search_timeout_s',)}
r1_policy['step_budget'] = 200000  # policy r1 exactly (r2 differs only in these two keys)
partial = r2['search']['partial']['placements']
sourced_fixed = set(r1_policy['fixed_refs'])
netlist = W / 'netlist.xml'
# --- 1. inspect: 287 poses on an isolated copy ---
stage = W / 'r3-287'
shutil.copytree(src_tree, stage)
b287 = stage / 'project/telemetry-pod.kicad_pcb'
board = pcbnew.LoadBoard(str(base))
PR._apply_plan(board, {'placements': [{**p, 'fixed': False} for p in partial]}, b287)
facts = extract(b287)
all_refs = {f['ref'] for f in facts['footprints']}
missing = sorted(all_refs - sourced_fixed - {p['ref'] for p in partial})
report['missing'] = missing
local = copy.deepcopy(r1_policy)
import os
release = set(json.loads(Path(os.environ['RELEASE']).read_text())['release']) if os.environ.get('RELEASE') else set()
assert not release & sourced_fixed
report['released_neighbours'] = sorted(release)
local['fixed_refs'] = sorted(sourced_fixed | ({p['ref'] for p in partial} - release))
req_local = {'policy': local, 'skip_visuals': True, 'authorization': {'schema': 'agent-ee.placement-write/1',
             'single_design_writer': True, 'source_sha256': digest(b287), 'writable_root': str(W / 'r3root')}}
(W / 'r3root').mkdir()
(W / 'r3-request-local.json').write_text(json.dumps(req_local, indent=1, sort_keys=True) + '\n')
# --- 2. place only the 22 with the existing placer ---
try:
    res = PR.place_candidate(b287, netlist, W / 'r3root/placed', req_local)
except Exception as exc:
    res = {'status': 'error', 'error': f'{type(exc).__name__}: {exc}'}
(W / 'r3-local-result.json').write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + '\n')
report['local'] = {k: res.get(k) for k in ('status', 'outcome', 'reason', 'steps_used', 'error')}
if 'search' in res:
    report['local']['search'] = {k: res['search'].get(k) for k in ('termination', 'unplaced', 'backjumps', 'placed_peak')}
if res.get('status') != 'placed':
    if 'capacity' in res:
        report['capacity_F_free_area'] = res['capacity']['sides'].get('F', {}).get('free_area', {}).get('ratio_display')
    (W / 'r3-report.json').write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + '\n')
    print(json.dumps(report, default=str)); sys.exit(1)
# --- 3. validate the ENTIRE arrangement under the original r1 policy, on the ORIGINAL input board ---
placed_facts = extract(W / 'r3root/placed/candidate.kicad_pcb')
uuid_fixed = {f['uuid'] for f in placed_facts['footprints'] if f['ref'] in sourced_fixed}
plan = {'schema': 'agent-ee.packing-plan/1', 'status': 'planned', 'board_sha256': digest(base),
        'min_courtyard_edge_mm': r1_policy['min_courtyard_edge_mm'],
        'policy': reserve_imu_markings(pcbnew.LoadBoard(str(base)), PR._effective_policy({'policy': r1_policy})),
        'placements': [{'ref': f['ref'], 'uuid': f['uuid'], 'position_nm': f['position_nm'], 'rotation_deg': f['rotation_deg'],
                        'fixed': f['uuid'] in uuid_fixed} for f in placed_facts['footprints']]}
final_dir = W / 'final'
final_dir.mkdir()
out = final_dir / 'candidate.kicad_pcb'
try:
    full = PR._evaluate_proposal(pcbnew.LoadBoard(str(base)), out, plan, netlist.read_bytes(), extract(base), base)
    report['full_validation'] = {'status': full['status'], 'verdict': full['verdict'], 'open_defects': full['open_defects'],
                                 'judge': full['judgment'].get('verdict'),
                                 'groups': full['judgment'].get('group_grading', {}).get('status') if isinstance(full['judgment'].get('group_grading'), dict) else 'see json',
                                 'locality': full['judgment'].get('locality_grading', {}).get('status'),
                                 'native_courtyard_overlaps': full['native_courtyard_overlaps'], 'board_sha256': full['board_sha256']}
    (final_dir / 'full-validation.json').write_text(json.dumps(full, indent=1, sort_keys=True, default=str) + '\n')
except Exception as exc:
    report['full_validation'] = {'status': 'refused', 'error': f'{type(exc).__name__}: {exc}', 'trace': traceback.format_exc()[-1500:]}
r2pose = {p['ref']: (p['position_nm'], p['rotation_deg'] % 360) for p in partial}
if out.is_file():
    fin = {f['ref']: (f['position_nm'], f['rotation_deg'] % 360) for f in extract(out)['footprints']}
    report['moved_from_r2'] = sorted(r for r in r2pose if fin.get(r) != r2pose[r])
    report['newly_placed'] = missing
# edge margin for every movable part with the placer's own test
outline = P._qualified(extract(out)) if out.is_file() else None
if outline is not None:
    margin = P._edge_margin_nm(r1_policy)
    bad = [f['ref'] for f in extract(out)['footprints'] if f['ref'] not in sourced_fixed and not P._fits(f, outline, margin)]
    report['edge_margin'] = {'margin_nm': margin, 'violations': bad}
(W / 'r3-report.json').write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'full_validation'} | {'full_validation': {k: v for k, v in report.get('full_validation', {}).items() if k != 'trace'}}, default=str))
sys.exit(0 if report.get('full_validation', {}).get('status') == 'placed' else 2)
