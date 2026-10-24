"""AGENTEE-489 consumer check: agent-ee's own validate/bind/materialize/grade on the real pod snapshot.

Run inside fome-runtime (native pcbnew) with agent-ee mounted. Usage:
  python3 -I consumer_check.py <repo-root> <probe.json> <out.json>
<probe.json> is agent_ee.placement_probe output for telemetry-pod/telemetry-pod.kicad_pcb.
"""
import copy, hashlib, json, sys
from pathlib import Path
from agent_ee import mechanical_reservations as mr

root, probe, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
pkt = root / 'telemetry-pod/expansion/agentee-489-source'
raw = (pkt / 'reservations.json').read_bytes()
doc = json.loads(raw)
cap = json.loads(probe.read_text())
board_sha = hashlib.sha256((root / 'telemetry-pod/telemetry-pod.kicad_pcb').read_bytes()).hexdigest()
cap['board_sha256'] = cap.get('board_sha256') or board_sha
rec = {'document_sha256': hashlib.sha256(raw).hexdigest(), 'board_sha256': board_sha,
       'probe_board_sha256': cap['board_sha256'], 'controls': {}}


def refuses(fn):
    try:
        fn()
    except ValueError as exc:
        return {'refused': True, 'reason': str(exc)}
    return {'refused': False}


mr.validate(doc)
binding = mr.bind(doc, cap, source_sha256=rec['document_sha256'])
g = mr.grade(cap, binding)
rec['full'] = {'status': g['status'], 'reservations_materialized': len(g['reservations']),
               'unknown': g['unknown'], 'defects': g['defects'], 'advisories': len(g['advisories'])}
rec['per_phase'] = {p: (lambda r: {'status': r['status'], 'unknown': len(r['unknown']), 'defects': len(r['defects'])})(
    mr.grade(cap, binding, phase=p)) for p in g['phases']}

# Controls on the consumer contract (fixtures derived from the real snapshot; not vendor evidence).
stale = copy.deepcopy(doc); stale['original_board_sha256'] = '0' * 64
rec['controls']['stale_board_hash_refused'] = refuses(lambda: mr.bind(stale, cap))
wrong = copy.deepcopy(doc); wrong['reservations'][0]['owner']['uuid'] = '00000000-0000-0000-0000-000000000000'
rec['controls']['wrong_owner_uuid_refused'] = refuses(lambda: mr.bind(wrong, cap))
eng = copy.deepcopy(doc); eng['source']['classification'] = 'manufacturer'
rec['controls']['non_engineering_classification_refused'] = refuses(lambda: mr.validate(eng))
missing = copy.deepcopy(cap); missing['footprints'] = [f for f in cap['footprints'] if f['ref'] != 'H1']
m = mr.materialize(binding, missing)
rec['controls']['missing_required_owner_not_pass'] = {
    'status': m['status'], 'H1_unknown': sorted({u['reservation'] for u in m['unknown'] if u['reservation'] and u['reservation'].startswith('H1/')})}
unresolved = sorted(u['reservation'] for u in g['unknown'] if u.get('kind') == 'unresolved')
rec['controls']['unresolved_required_not_pass'] = {'status': g['status'], 'rows': unresolved}
# Attached rows follow the owner: H1 washer@F after a +10 mm X move and a flip to B.
moved = copy.deepcopy(cap)
for f in moved['footprints']:
    if f['ref'] == 'H1':
        dx = 10_000_000
        f['position_nm'][0] += dx
        for p in f['pads']:
            p['position_nm'][0] += dx
mm = mr.materialize(binding, moved)
base = {r['id']: r for r in mr.materialize(binding, cap)['reservations']}
after = {r['id']: r for r in mm['reservations']}
rid = 'H1/ISO7089-washer@F.Cu'
shift = [after[rid]['polygons_nm'][0][0][i] - base[rid]['polygons_nm'][0][0][i] for i in (0, 1)]
fixed_other = after['H2/ISO7089-washer@F.Cu']['polygons_nm'] == base['H2/ISO7089-washer@F.Cu']['polygons_nm']
rec['controls']['attached_moves_with_owner'] = {'vertex_shift_nm': shift, 'other_owner_unchanged': fixed_other}
rec['controls']['faces_resolved'] = {rid: base[rid]['faces'], 'H1/Harwin-standoff@B.Cu': base['H1/Harwin-standoff@B.Cu']['faces']}
# Legitimate case with no extra restrictions: only the resolved hardware rows.
sub = copy.deepcopy(doc)
sub['reservations'] = [r for r in doc['reservations'] if r['id'].startswith('H1/ISO7089-washer@F')]
sg = mr.grade(cap, mr.bind(sub, cap))
rec['controls']['resolved_subset_grade'] = {'status': sg['status'], 'defects': sg['defects'], 'unknown': sg['unknown']}
out.write_text(json.dumps(rec, indent=1) + '\n')
print('full status', g['status'], 'materialized', len(g['reservations']), 'unknown', len(g['unknown']),
      'defects', len(g['defects']))

# Envelope opt-in (agent-ee board_envelope.mechanical_reservations) on a captured candidate root laid out
# exactly as production-capture/build.py --mechanical-reservations writes it.
import shutil, tempfile
from agent_ee import board_envelope
with tempfile.TemporaryDirectory(prefix='ee489-envelope-') as tmp:
    cand = Path(tmp)
    layout = {'mechanics/reservations.json': pkt / 'reservations.json',
              'mechanics/agentee-490-bound-reservations.json': root / 'telemetry-pod/expansion/agentee-490-mechanical-inputs/bound-reservations.json',
              'mechanics/original-board.kicad_pcb': root / 'telemetry-pod/telemetry-pod.kicad_pcb'}
    for rel, src in layout.items():
        (cand / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, cand / rel)
    files = {rel: hashlib.sha256((cand / rel).read_bytes()).hexdigest() for rel in layout}
    field = {'path': 'mechanics/reservations.json', 'sha256': files['mechanics/reservations.json']}
    env = board_envelope.mechanical_reservations(field, (files, cand))
    rec['envelope_binding'] = {'path': env['path'], 'sha256': env['sha256'], 'source': env['source'],
                               'source_paths': env['source_paths'], 'rows': len(env['document']['reservations'])}
    stale_files = dict(files); stale_files['mechanics/original-board.kicad_pcb'] = '1' * 64
    rec['controls']['envelope_stale_snapshot_refused'] = refuses(
        lambda: board_envelope.mechanical_reservations(field, (stale_files, cand)))
    rec['controls']['envelope_uncaptured_refused'] = refuses(lambda: board_envelope.mechanical_reservations(field, None))
out.write_text(json.dumps(rec, indent=1) + '\n')
print('envelope binding', rec['envelope_binding']['sha256'], 'rows', rec['envelope_binding']['rows'])
