"""Actual sealed-consumer controls for the complete A3 source declarations."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from collections import Counter

parser=argparse.ArgumentParser()
parser.add_argument('--agent-ee-src',required=True)
parser.add_argument('--probe',required=True)
parser.add_argument('--report',required=True)
args=parser.parse_args()
sys.path.insert(0,args.agent_ee_src)
from agent_ee import block_contract,electrical_locality,locality_provenance

BASE='a1678bdf6583263b4c0917de77a950f21c6748d6'
CONSUMER='8ab3b0b95dd3ece043e67fff6bd226c36427ff22'
p=Path('telemetry-pod/expansion/agentee-485-blocks')
policy_path=Path('telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json')
load=lambda name:json.loads((p/name).read_bytes())
def frozen(path):return json.loads(subprocess.check_output(['git','show',BASE+':'+str(path)]))
probe=json.loads(Path(args.probe).read_bytes())
contract=load('block-contract-template.json');policy=json.loads(policy_path.read_bytes())
base=frozen(policy_path);base_contract=frozen(p/'block-contract-template.json')
ledger=load('coverage-ledger.json')['rows'];old_ledger=frozen(p/'coverage-ledger.json')['rows']
by_old={r['relationship']:r for r in old_ledger}
assert len(ledger)==214 and {r['relationship'] for r in ledger}==set(by_old)
assert sum(r['historical_cross_face_instance'] for r in ledger)==211
new_by_id={o['id']:o for o in policy['obligations']}
for old in base['obligations']:assert new_by_id[old['id']]==old
single=[o for o in policy['obligations'] if o.get('kind')=='single-leg']
assert len(single)==143 and len(policy['obligations'])==201
expected_ids={r['relationship'] for r in old_ledger if 'G1_SINGLE_LEG_SCHEMA' in r['unresolved_gaps']}
assert {o['id'] for o in single}==expected_ids
for o in single:
    row=by_old[o['id']]
    assert set(o)=={'id','kind','metric','leg'}
    assert {k:o['leg'][k] for k in ('from','to')}==row['declared_primary_pair']
    assert o['leg']['max_distance_nm']==round(row['source']['record']['bound']['supply_leg_max_mm']*1000000)
    assert o['leg']['provenance']['class']=='default'
assert policy['source_records'][str(p/'coverage-ledger.json')]==(p/'coverage-ledger.json').read_text()
raw=policy_path.read_bytes();encoded=(p/'block-contract-template.json').read_bytes()
start=encoded.index(b'  "relationships": ')+len(b'  "relationships": ')
assert encoded[start:start+len(raw)]==raw==(p/'relationships-effective.json').read_bytes()
assert contract['relationships']==policy
assert contract['eligibility']==load('eligibility-template.json')
assert contract['allocation']==base_contract['allocation']==load('allocation-template.json')
assert contract['allocation']['board_sha256'] is None and contract['eligibility']['sources']['board_sha256'] is None
assert contract['routing_obligations']==load('routing-obligations.json')
pairs={(o['id'],role):o[role] for o in policy['obligations'] for role in electrical_locality.roles(o)}
assert len(pairs)==261
assert {(t['relationship'],t['role']) for t in contract['templates']}==set(pairs)
assert len(contract['templates'])==261
for t in contract['templates']:
    if t['relationship'] in expected_ids:
        assert t['role']=='leg' and t['template']==by_old[t['relationship']]['source_template']['template']
for pair in pairs.values():
    assert locality_provenance.classify(pair,policy['source_records'])['enforcement']=='advisory'
    for endpoint in pair.values():
        if isinstance(endpoint,dict) and {'reference','pad','net'}<=endpoint.keys():electrical_locality.resolve(probe['footprints'],endpoint)
for row in ledger:
    assert row['source']==by_old[row['relationship']]['source']
    assert row['declared_primary_pair']==by_old[row['relationship']]['declared_primary_pair']
    for binding in row['supported_bindings']:assert (binding['obligation'],binding['role']) in pairs
    assert row['supported_bindings'] or row['pending_stage_requirements']
# Each removed A2 guard must have one explicit placement/routing migration.
migrations=load('guard-migrations.json')
old_guards=[g for b in base_contract['eligibility']['blocks'].values() for g in b.get('material_unknowns',[])]
assert len(migrations)==len(old_guards)==154
assert {m['original_guard']['id'] for m in migrations}=={g['id'] for g in old_guards}
assert Counter(m['action'] for m in migrations)=={'PLACEMENT_LEG_REPRESENTED':143,'EXPLICIT_ROUTING_STAGE_MIGRATION':11}
for m in migrations:
    if m['action']=='PLACEMENT_LEG_REPRESENTED':assert m['target']['obligation'] in expected_ids
    else:assert m['target']['routing_obligation'] in {r['id'] for r in contract['routing_obligations']}
remaining_guards=[g for b in contract['eligibility']['blocks'].values() for g in b.get('material_unknowns',[])]
assert not remaining_guards
bound=copy.deepcopy(contract)
bound['allocation']['board_sha256']=probe['board_sha256'];bound['eligibility']['sources']['board_sha256']=probe['board_sha256']
section={'contract':bound,'side_eligibility':bound['eligibility'],'allocation_text':(p/'allocation-bridge.json').read_text()}
effective={'electrical_locality':policy}
members=block_contract.validate(probe,section,effective)
assert len(members['roles'])==313
routing=block_contract.routing_obligations(bound,probe)
assert len(routing)==11 and Counter(r['kind'] for r in routing)=={'no-via':8,'controlled-impedance':3}
assert all(r['status']=='pending' for r in routing)
expected_routing={r['relationship'] for r in old_ledger if any(g in r['unresolved_gaps'] for g in ['G2_NO_VIA_EVIDENCE','G3_RF_CORRIDOR_AND_IMPEDANCE'])}
assert {r['id'] for r in routing}==expected_routing
# Use the real generic grader for an all-143 positive, independent of the full
# board's remaining template/pin-coverage failures.
single_grade=electrical_locality.grade(probe,{'schema':electrical_locality.SCHEMA,'obligations':single,'source_records':policy['source_records']})
assert len(single_grade['measured'])==143 and not single_grade['unknown'] and not single_grade['defects']
assert single_grade['status']=='info' and len(single_grade['advisories'])==143
full=block_contract.judge(probe,bound,original_capture=probe)
planning=block_contract.check_complete(probe,bound)
assert len(full['relationships'])==261 and len(full['advisories'])==261
assert not any(u['kind']=='required_numeric_authority_missing' for u in full['unknown'])
assert full['routing_obligations']==routing==planning['routing_obligations']
assert len([r for r in full['relationships'] if r['role']=='leg'])==143
controls=[]
def refused(name,call):
    try:call()
    except ValueError as exc:controls.append({'control':name,'result':'REFUSE','reason':str(exc)})
    else:raise AssertionError(name+' was admitted')
selected=next(o for o in single if o['id']=='U5.5-R27-feedback')
bad=copy.deepcopy(selected);del bad['leg']
refused('omitted single leg',lambda:electrical_locality.validate({'schema':electrical_locality.SCHEMA,'obligations':[bad]}))
bad_section=copy.deepcopy(section)
bad_section['contract']['relationships']['obligations']=[o for o in bad_section['contract']['relationships']['obligations'] if o['id']!=selected['id']]
bad_section['contract']['templates']=[t for t in bad_section['contract']['templates'] if t['relationship']!=selected['id']]
refused('omitted source relationship against complete effective policy',lambda:block_contract.validate(probe,bad_section,effective))
wrong=copy.deepcopy(selected['leg']['from']);wrong['pad']='4'
refused('wrong physical native pin in single leg',lambda:electrical_locality.resolve(probe['footprints'],wrong))
refused('stale A2 effective policy',lambda:block_contract.validate(probe,section,{'electrical_locality':base}))
bad_contract=copy.deepcopy(bound);bad_contract['routing_obligations'][0]['status']='pass'
refused('claimed routing pass',lambda:block_contract._contract(probe,bad_contract))
bad_contract=copy.deepcopy(bound);bad_contract['routing_obligations'][0]['source']['sha256']='0'*64
refused('changed routing source hash',lambda:block_contract._contract(probe,bad_contract))
bad_contract=copy.deepcopy(bound);bad_contract['routing_obligations'][0]['pairs'][0]['from']['pad']='99999'
refused('wrong routing terminal pin',lambda:block_contract._contract(probe,bad_contract))
side_selected=next(o for o in single if o['id']=='U20.5-C82-crystal-load')
candidate=copy.deepcopy(probe)
dev=next(f for f in candidate['footprints'] if f['ref']==side_selected['leg']['from']['reference'])
support=next(f for f in candidate['footprints'] if f['ref']==side_selected['leg']['to']['reference'])
support['side']='B' if dev['side']=='F' else 'F'
side_report=block_contract.judge(candidate,bound,original_capture=probe)
assert any(d['kind']=='same_face_required' and d['relationship']==side_selected['id'] and d['role']=='leg' for d in side_report['defects'])
controls.append({'control':'illegal opposite face for source single leg','result':'DEFECT','reason':'same_face_required'})
# Keep all material residuals, not just the minimal planning report.
findings={'consumer':CONSUMER,'board_sha256':probe['board_sha256'],'saved_report_status':full['status'],
          'planning_status':planning['status'],'defects':full['defects'],'unknown':full['unknown'],
          'material_guards':remaining_guards,'routing_obligations':routing,
          'under_device_J3':[r for r in full['relationships'] if r['from']['reference']=='J3'],
          'advisory_measurements':len(full['advisories']),
          'advisory_rows':[{k:r[k] for k in ['relationship','role','max_distance_nm','distance_mm','exceeded','constraint_provenance'] if k in r} for r in full['advisories']]}
write_path=p/'NATIVE-FINDINGS.json';write_path.write_text(json.dumps(findings,indent=2)+'\n')
pin_unknown=[u for u in full['unknown'] if u['kind']=='block_pin_relationships_missing']
result={'verdict':'143 SINGLE LEGS ADOPTED; 11 ROUTING CLAUSES PENDING; FULL NATIVE CONTRACT STILL HAS EXPLICIT FINDINGS',
    'consumer_head':CONSUMER,'declaration_positive':'PASS','single_leg_positive':{'status':single_grade['status'],'measured':143,'unknown':0,'defects':0,'advisories':143,'exceeded':sum(a['exceeded'] for a in single_grade['advisories'])},
    'counts':{'single_legs':143,'coverage_rows':214,'placement_source_rows':211,'obligations':201,'role_pairs':261,
              'native_endpoint_resolutions':522,'routing_pending':11,'material_guards_remaining':len(remaining_guards),
              'pin_coverage_unknown_groups':len(pin_unknown),'pin_coverage_unknown_references':sum(len(u['references']) for u in pin_unknown),
              'internal_net_geometry_unknowns':sum(u['kind']=='internal_net_geometry_missing' for u in full['unknown'])},
    'full_report_status':full['status'],'full_report_defects':len(full['defects']),
    'full_report_unknown_counts':dict(Counter(u['kind'] for u in full['unknown'])),
    'negative_controls':controls,
    'limitations':['Full native contract is not accepted; J3/C65 and C64 under-device findings and remaining pin/internal-net unknowns are preserved.',
                   'The genuine retained native board capture is used; side fault is an in-memory mutation, no board file is changed.',
                   'Pending routing clauses are declarations, not routed evidence or impedance qualification.']}
Path(args.report).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
