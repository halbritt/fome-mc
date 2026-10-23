"""placement-r4 interface probe (disposable copy; no design written to the repo; no placement). Demonstrates, with the
existing agent-ee 7d5b0d4d code, whether the admission/write path can represent a declared side flip:
 a) placer_runner._apply_plan with a plan entry carrying a 'side' field: does the saved footprint change side?
 b) placer_runner._footprint_pad_inventory of R7 before vs after a native pcbnew Flip: the fields that differ (the
    _evaluate_proposal gate refuses any difference: 'native saved board changed footprint pad geometry');
 c) placement_probe.extract + placement.judge on a board where R7 is natively flipped: is a B-side part represented?
Usage: r4_interface_probe.py BOARD OUT_JSON
"""
import json, shutil, sys, tempfile
from pathlib import Path
import pcbnew
from agent_ee import placer_runner as PR
from agent_ee.placement import judge
from agent_ee.placement_probe import extract
board_path, out = Path(sys.argv[1]), Path(sys.argv[2])
tmp = Path(tempfile.mkdtemp())
shutil.copytree(board_path.parent.parent, tmp / 'c')
b = tmp / 'c/project/telemetry-pod.kicad_pcb'
doc = {}
board = pcbnew.LoadBoard(str(b))
r7 = next(fp for fp in board.GetFootprints() if fp.GetReference() == 'R7')
uuid, pos, rot = r7.m_Uuid.AsString(), [r7.GetPosition().x, r7.GetPosition().y], r7.GetOrientationDegrees()
# a) _apply_plan with a declared side
PR._apply_plan(board, {'placements': [{'ref': 'R7', 'uuid': uuid, 'position_nm': pos, 'rotation_deg': rot, 'fixed': False, 'side': 'B'}]}, tmp / 'a.kicad_pcb')
ra = next(fp for fp in pcbnew.LoadBoard(str(tmp / 'a.kicad_pcb')).GetFootprints() if fp.GetReference() == 'R7')
doc['a_apply_plan_side_field'] = {'declared_side': 'B', 'saved_is_flipped': ra.IsFlipped(), 'saved_layer': ra.GetLayerName()}
# b) pad inventory before/after native flip
board = pcbnew.LoadBoard(str(b))
r7 = next(fp for fp in board.GetFootprints() if fp.GetReference() == 'R7')
before = PR._footprint_pad_inventory(r7)
r7.Flip(r7.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
after = PR._footprint_pad_inventory(r7)
names = ['uuid', 'number', 'net', 'attribute', 'padstack_mode', 'shape', 'size', 'offset', 'drill', 'drill_shape',
         'roundrect', 'chamfer', 'chamfer_pos', 'layer_set', 'fp_relative_position', 'fp_relative_orientation', 'custom']
diffs = []
for pb, pa in zip(before['pads'], after['pads']):
    diffs.append({'pad': pb[1], 'changed': {n: [x, y] for n, x, y in zip(names, pb, pa) if x != y}})
doc['b_pad_inventory'] = {'equal': before == after, 'fpid_equal': before['fpid'] == after['fpid'], 'per_pad': diffs,
                          'flipped_layer': r7.GetLayerName(), 'nets_unchanged': [p[2] for p in before['pads']] == [p[2] for p in after['pads']]}
pcbnew.SaveBoard(str(tmp / 'c/project/flip.kicad_pcb'), board)
# c) extract + judge represent a B-side part
facts = extract(tmp / 'c/project/flip.kicad_pcb')
f7 = next(f for f in facts['footprints'] if f['ref'] == 'R7')
j = judge(facts)
doc['c_extract_judge'] = {'R7_courtyard_sides': sorted(f7.get('courtyards', {})), 'judge_ran': True, 'judge_verdict': j.get('verdict'),
                          'J3_sides_in_input': sorted(next(f for f in extract(b)['footprints'] if f['ref'] == 'J3').get('courtyards', {}))}
out.write_text(json.dumps(doc, indent=1, sort_keys=True, default=str) + '\n')
print(json.dumps({'a': doc['a_apply_plan_side_field'], 'b_equal': doc['b_pad_inventory']['equal'], 'b_first_pad_changed': list(diffs[0]['changed']), 'b_nets_unchanged': doc['b_pad_inventory']['nets_unchanged'], 'c': doc['c_extract_judge']}, default=str))
