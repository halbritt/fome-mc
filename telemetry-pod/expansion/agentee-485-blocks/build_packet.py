"""Rebuild proposed source reconciliation; never writes board or policy.

Run from the frozen fome-mc root with a native placement-probe/1 JSON path.
The probe must authenticate to this checkout's board bytes. Schema validation
uses the separately frozen agent-ee consumer, not this data-generation script.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path('telemetry-pod')
EXP = ROOT / 'expansion'
PREP = EXP / 'agentee-478-prep'
OUT = EXP / 'agentee-485-blocks'
sha = lambda b: hashlib.sha256(b).hexdigest()
def read(p):
    return json.loads(Path(p).read_bytes())
def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

capture = read(sys.argv[1])
board_hash = sha((ROOT / 'telemetry-pod.kicad_pcb').read_bytes())
assert capture['schema'] == 'agent-ee.placement-probe/1'
assert capture['board_sha256'] == board_hash
native = {f['ref']: f for f in capture['footprints']}
# Execute only the retained, deterministic membership recipe. It reconstructs
# unbound allocation/1 plus documented source corrections, never allocation-v2.
recipe = PREP / 'build_prep.py'
prefix = recipe.read_text().split('# ---------------------------------------------------------------- sources (D3 provenance)')[0]
old_argv = sys.argv
sys.argv = [str(recipe), str(ROOT), str(PREP / 'extract/emitted-schematic-netlist-cef8e4c7.json'), str(PREP)]
ns = {}
try:
    exec(compile(prefix, str(recipe), 'exec'), ns)
finally:
    sys.argv = old_argv
blocks, fixed, shared = ns['blocks'], ns['FIXED'], ns['SHARED']
allocation = {'schema': 'agent-ee.block-allocation/2', 'board_sha256': None,
              'blocks': [], 'fixed': [{'reference': r} for r in sorted(fixed)],
              'shared': [{'reference': r, 'role': shared[r]} for r in sorted(shared)]}
bridge = {'schema': 'agent-ee.block-allocation/1', 'blocks': [], 'residual': sorted(set(fixed) | set(shared))}
for bid, refs in sorted(blocks.items()):
    member = ns['anchors'].get(bid)
    interface = ns['FIXED_ANCHOR'].get(bid)
    anchor = {'member': member} if member else {'fixed': interface} if interface else {'none': 'centroid of members'}
    allocation['blocks'].append({'id': bid, 'references': sorted(refs), 'anchor': anchor, 'interfaces_to_fixed': interface})
    row = {'id': bid, 'references': sorted(refs), 'sheets': []}
    if member:
        row['anchor'] = member
    bridge['blocks'].append(row)
roles = {r: {'role': 'block', 'block_id': bid} for bid, refs in blocks.items() for r in refs}
roles.update({r: {'role': 'fixed'} for r in fixed})
roles.update({r: {'role': 'shared', 'shared_role': shared[r]} for r in shared})
claims = [r for refs in blocks.values() for r in refs] + list(fixed) + list(shared)
assert len(claims) == len(set(claims)) == len(native) == 313
assert set(claims) == set(native)
write('allocation-template.json', allocation)
write('allocation-bridge.json', bridge)
write('membership-coverage.json', {'board_sha256': board_hash, 'native_footprints': len(native),
      'blocks': len(blocks), 'roles': roles, 'recipe': str(recipe), 'recipe_sha256': sha(recipe.read_bytes()),
      'unbound_origin': str(EXP / 'blocks/allocation.json'), 'source_corrections': ns['corrections'],
      'historical_board_bound_allocation_used': False})

oldelig = read(PREP / 'side-eligibility.json')
elig = {'schema': 'fome-mc.side-eligibility/1', 'sources': {'board_sha256': None},
        'default': {'faces': ['F', 'B']}, 'blocks': {}, 'fixed': {}, 'shared': {}, 'members': {}}
for bid in blocks:
    row = oldelig['blocks'][bid]
    elig['blocks'][bid] = {'eligible_faces': row['eligible_faces'], 'face_restrictions': row['face_restrictions']}
for ref in fixed:
    # Preserve the existing fixed-anchor face as a conservative proposal. A
    # logical fixed role is not a pose lock; authenticated production policy
    # and current mechanical_reservations continue to govern placement.
    elig['fixed'][ref] = {'eligible_faces': [native[ref]['side']],
                         'face_restrictions': ['Proposed existing native anchor face; retained 474 register and 478 fixed record; not a new owner requirement.']}
for ref in shared:
    elig['shared'][ref] = {'eligible_faces': ['F', 'B'], 'face_restrictions': []}
write('eligibility-template.json', elig)

raw = (EXP / 'electrical-locality/pad-obligations/electrical-locality.json').read_bytes()
locality = json.loads(raw)
(OUT / 'relationships-effective.json').write_bytes(raw)
bounds = read(PREP / 'relationship-bounds.json')
instances = read(PREP / 'cross-face-templates.json')['instances']
relations = {r['id']: r for r in bounds['relationships']}
inst = {r['relationship']: r for r in instances}
disposition = {r['old_id']: r['new'] for r in bounds['old_obligations_disposition']}
assert len(locality['obligations']) == 12 and len(inst) == 211
assert not ({o['id'] for o in locality['obligations']} & set(inst))

def endpoint(ref, pin, net):
    return {'reference': ref, 'pad': str(pin), 'net': net}
def pads(ref, net):
    return sorted({p['number'] for p in native[ref]['pads'] if p['net'] == net})
def selector(ref, net):
    return [endpoint(ref, p, net) for p in pads(ref, net)]
def legacy_legs(rel):
    d, s = rel['device'], rel['support']
    legs = {'supply': {'from': [endpoint(d['ref'], d['pin'], d['net'])],
                       'to': selector(s['ref'], s['pin_net']),
                       'max_distance_mm': rel['bound']['supply_leg_max_mm']}}
    if rel['bound'].get('return_leg_max_mm') is not None:
        ret = rel.get('return')
        legs['return'] = ({'from': [endpoint(ret['device'], ret['device_pad'], ret['net'])],
                           'to': [endpoint(ret['support'], ret['support_pad'], ret['net'])],
                           'selector': 'explicit named return'} if ret else
                          {'from': selector(d['ref'], '/GND'), 'to': selector(s['ref'], '/GND'),
                           'selector': 'nearest GND pad pair; empty selector is unsatisfied'})
        legs['return']['max_distance_mm'] = rel['bound']['return_leg_max_mm']
    return legs

templates, mapping, legacy_to_current = [], [], {}
for obligation in locality['obligations']:
    ids = disposition[obligation['id']]
    for role in ['supply', 'return', 'switch']:
        if role not in obligation:
            continue
        rid = ids[1] if role == 'switch' else ids[0]
        r = relations[rid]
        legacy_role = 'supply' if role == 'switch' else role
        leg = legacy_legs(r).get(legacy_role)
        effective = obligation[role]
        exact_endpoints = bool(leg and leg['from'] == [effective['from']] and leg['to'] == [effective['to']])
        notes = []
        if not leg:
            notes.append('No corresponding historical leg/bound; current effective leg retained.')
        elif not leg['from'] or not leg['to']:
            notes.append('Historical generic GND selector has no return pair; effective explicit SW return retained.')
        elif not exact_endpoints:
            notes.append('Endpoint/selector difference, not an ID rename. Preserve effective endpoints.')
        if leg and leg['max_distance_mm'] * 1000000 != effective['max_distance_nm']:
            notes.append('Numeric bounds differ; preserve effective ADVISORY value and citation.')
        row = {'effective_id': obligation['id'], 'role': role, 'effective': effective,
               'historical_relationship': rid, 'historical_role': legacy_role, 'historical_leg': leg,
               'template': inst[rid]['template'], 'exact_endpoint_mapping': exact_endpoints,
               'notes': notes, 'source': {'relationship_bounds': str(PREP / 'relationship-bounds.json'),
               'cross_face_templates': str(PREP / 'cross-face-templates.json'), 'provenance': r['provenance']}}
        mapping.append(row)
        legacy_to_current.setdefault(rid, []).append({'id': obligation['id'], 'role': role})
        templates.append({'relationship': obligation['id'], 'role': role, 'template': inst[rid]['template']})
assert len(mapping) == len(templates) == 26
write('effective-role-mapping.json', mapping)
ledger = []
for row in instances:
    r = relations[row['relationship']]
    ledger.append({'relationship': r['id'], 'kind': r['kind'], 'template': row['template'],
        'native_endpoint_selectors': legacy_legs(r), 'effective_counterparts': legacy_to_current.get(r['id'], []),
        'classification': 'SEMANTIC_MAPPING_WITH_EXPLICIT_DELTAS' if r['id'] in legacy_to_current else 'NO_EFFECTIVE_COUNTERPART',
        'membership': r['membership'], 'historical_bound': r['bound'], 'source_record': r,
        'cross_face_source': row})
assert len(ledger) == 211 and sum(not r['effective_counterparts'] for r in ledger) == 197
write('cross-face-ledger.json', ledger)
write('source-reconciliation.json', {'classification': 'PROPOSAL; full critical-pin coverage unresolved',
    'effective_obligations_preserved': 12, 'effective_roles_preserved': 26,
    'historical_relationships': 211, 'historical_relationships_with_semantic_counterparts': 14,
    'historical_relationships_without_effective_counterparts': 197,
    'electrical_obligations_added_to_policy': [], 'electrical_obligations_deleted_from_policy': [],
    'historical_records_without_cross_face_instance': sorted(set(relations) - set(inst)),
    'primary_sources': bounds['sources'],
    'primary_source_hash_checks': {k: sha(Path(v['path']).read_bytes()) == v['sha256'] for k,v in bounds['sources'].items()},
    'current_reservations_sha256': 'a4504674758717274f9be567188751cd11c9721d4a4f434b9c9fc59f7345d1cd'})
contract = {'schema': 'agent-ee.block-contract/1', 'allocation': allocation,
            'eligibility': elig, 'templates': templates, 'thickness_nm': 1600000}
# Preserve the exact source byte sequence as the relationships value span.
encoded = json.dumps(contract, indent=2).rstrip()[:-1].rstrip() + ',\n  "relationships": '
(OUT / 'block-contract-template.json').write_bytes(encoded.encode() + raw + b'\n}\n')
assert read(OUT / 'block-contract-template.json')['relationships'] == locality
lines = ['# Effective role mapping', '', 'All bounds remain the effective ADVISORY values. Historical source IDs establish conceptual intent only. Exact historical endpoint selectors and primary citations appear in the JSON ledgers.', '', '| Effective obligation | Role | Effective endpoints (ref.pin) | Historical relationship | Historical endpoint selector | Template | Difference |', '|---|---|---|---|---|---|---|']
def fmt(e):
    return e['reference'] + '.' + e['pad']
for r in mapping:
    e, h = r['effective'], r['historical_leg']
    historical = ('{' + ', '.join(map(fmt, h['from'])) + '} → {' + ', '.join(map(fmt,h['to'])) + '}') if h else 'absent'
    lines.append('| ' + ' | '.join([r['effective_id'],r['role'],fmt(e['from'])+' → '+fmt(e['to']),r['historical_relationship'],historical,r['template'],'; '.join(r['notes']) or 'same endpoints and bound']) + ' |')
(OUT / 'MAPPING.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'native_footprints':len(native), 'blocks':len(blocks), 'effective_roles':len(mapping), 'legacy_rows':len(ledger)}))
# Keep discarded/stale authoring metadata visible rather than silently importing
# historical board-space rectangles or enclosure assumptions as new gates.
write('eligibility-source-disposition.json', {
    'source': str(PREP / 'side-eligibility.json'), 'source_sha256': sha((PREP / 'side-eligibility.json').read_bytes()),
    'historical_document': oldelig,
    'face_permission': 'Preserve block F/B permissions and RF front restriction; fixed references conservatively keep their native face in this proposal.',
    'region_disposition': 'Historical XY rectangles are source evidence, not transformed production geometry. Preserve current native rule areas and captured a4504674 mechanical_reservations through the unchanged effective policy. No existing policy path is edited.',
    'owner_supersession': '2026-10-23 direct dispatch: enclosure follows PCB; no enclosure or worst-case-stack gate. TP1-6 hand probes on bare board, either face, no fixture. JP1-5 iron access once before enclosure. Agents choose M3; interference fits are not defects.',
    'not_claimed': 'A face-eligibility template alone does not prove mechanical access, transformed keepouts, functional grouping, or electrical closure.'})
lines = ['# All 211 cross-face source relationships', '',
         'Endpoint selectors below are resolved against the frozen writer-C native board. Braces mean the historical measurement chooses among those pins, not a new obligation for every pair. Empty braces mean no measurable named-net pad. Repeated physical pad lands with the same pin number remain one ref.pin selector; no arbitrary UUID is selected. Supply is the historical measurement role; the kind names its electrical function. Sources are relationship-bounds.json /relationships/<id>, cross-face-templates.json /instances/<relationship>, and the cited primary document/page in each JSON ledger source_record.', '',
         '| Historical relationship | Kind / role and exact endpoint selectors | Template | Effective mapping | Primary source / page |', '|---|---|---|---|---|']
for row in ledger:
    legs = []
    for role, leg in row['native_endpoint_selectors'].items():
        legs.append(role + ': {' + ', '.join(map(fmt,leg['from'])) + '} → {' + ', '.join(map(fmt,leg['to'])) + '}')
    sources = [p.get('source','') + ' p.' + str(p.get('page','?')) for p in row['source_record']['provenance'] if 'source' in p]
    links = ', '.join(x['id'] + '/' + x['role'] for x in row['effective_counterparts']) or 'NO EFFECTIVE COUNTERPART (no policy addition in this packet)'
    lines.append('| ' + ' | '.join([row['relationship'], row['kind'] + '; ' + '; '.join(legs),row['template'],links,'; '.join(sources) or 'Retained topology / labelled agent judgment; no primary quantitative bound']) + ' |')
(OUT / 'CROSS_FACE_MAPPING.md').write_text('\n'.join(lines)+'\n')
write('frozen-sources.json', {'fome_mc_head': '4dad3b9951db401102f0691e17063a694da2c803',
    'agent_ee_head': '8e3b382b0f48525742cfd520e3f306b12e78a468', 'board_sha256': board_hash,
    'board_thickness_nm': 1600000, 'board_thickness_source': 'telemetry-pod/telemetry-pod.kicad_pcb general/thickness 1.6 mm',
    'native_probe_sha256': sha(Path(sys.argv[1]).read_bytes()),
    'native_probe_origin': 'writer-C scratch/item4b/probe.json; board-only native capture, not full-project qualification',
    'source_hashes': {str(p): sha(p.read_bytes()) for p in [recipe, EXP/'blocks/allocation.json',
        PREP/'cross-face-templates.json', PREP/'relationship-bounds.json',PREP/'side-eligibility.json',
        EXP/'electrical-locality/pad-obligations/electrical-locality.json', ROOT/'telemetry-pod.kicad_pcb']}})
assert sha((EXP/'agentee-489-source/reservations.json').read_bytes()) == 'a4504674758717274f9be567188751cd11c9721d4a4f434b9c9fc59f7345d1cd'
assert '\t\t(thickness 1.6)' in (ROOT/'telemetry-pod.kicad_pcb').read_text()
write('unresolved-decisions.json', {
    'authority': 'chief/integrator engineering disposition for the combined 485 review; no owner answer required',
    'scope': 'No decision below is enacted by this packet; current policy bytes remain unchanged.',
    'per_relationship_coverage': [
        {'historical_relationship': r['relationship'], 'kind': r['kind'], 'template': r['template'],
         'endpoint_selectors': r['native_endpoint_selectors'], 'membership': r['membership'],
         'decision': 'Determine explicit active-policy coverage/disposition before claiming full critical-pin closure. Preserve any adopted source obligation; do not silently drop this row or harden historical agent numeric bounds.',
         'source_locator': 'cross-face-ledger.json / ' + r['relationship']}
        for r in ledger if not r['effective_counterparts']],
    'endpoint_conflicts': [r for r in mapping if not r['exact_endpoint_mapping']],
    'numeric_deltas': [r for r in mapping if r['historical_leg'] is not None and
                       r['historical_leg']['max_distance_mm'] * 1000000 != r['effective']['max_distance_nm']],
    'implementation_boundary': 'Template/consumer wiring and physical placement controls remain with the fome writer/integrator. Source reconciliation does not certify the candidate.'})
