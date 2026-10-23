"""Source coverage and real frozen-consumer controls; never rewrites a board."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from collections import Counter

parser=argparse.ArgumentParser()
parser.add_argument('--agent-ee-src',required=True)
parser.add_argument('--probe',required=True)
parser.add_argument('--report',required=True)
args=parser.parse_args()
sys.path.insert(0,args.agent_ee_src)
from agent_ee import block_contract,electrical_locality,locality_provenance

p=Path('telemetry-pod/expansion/agentee-485-blocks')
load=lambda name:json.loads((p/name).read_bytes())
probe=json.loads(Path(args.probe).read_bytes())
contract=load('block-contract-template.json')
policy=json.loads(Path('telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json').read_bytes())
original=load('policy-before-cA2.json')
sources=load('frozen-sources.json')
assert hashlib.sha256(Path(args.probe).read_bytes()).hexdigest()==sources['native_probe_sha256']
assert probe['board_sha256']==sources['board_sha256']
for path,digest in sources['source_hashes'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
assert all(sources['primary_source_hash_checks'].values())
raw=Path('telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json').read_bytes()
encoded=(p/'block-contract-template.json').read_bytes()
start=encoded.index(b'  "relationships": ')+len(b'  "relationships": ')
assert encoded[start:start+len(raw)]==raw==(p/'relationships-effective.json').read_bytes()
assert contract['relationships']==policy
assert contract['allocation']==load('allocation-template.json')
assert contract['eligibility']==load('eligibility-template.json')
assert contract['allocation']['board_sha256'] is None and contract['eligibility']['sources']['board_sha256'] is None
ledger=load('coverage-ledger.json')['rows']
source=json.loads(Path('telemetry-pod/expansion/agentee-478-prep/relationship-bounds.json').read_bytes())['relationships']
source_by_id={r['id']:r for r in source}
pin_functions=json.loads(Path('telemetry-pod/expansion/agentee-478-prep/extract/emitted-schematic-netlist-cef8e4c7.json').read_bytes())['components']
template_by_key={(r['relationship'],r['role']):r['template'] for r in contract['templates']}
assert {r['relationship'] for r in ledger}=={r['id'] for r in source} and len(ledger)==214
assert sum(r['historical_cross_face_instance'] for r in ledger)==211
assert policy['source_records'][str(p/'coverage-ledger.json')]==(p/'coverage-ledger.json').read_text()
obligations={o['id']:o for o in policy['obligations']}
expected={(o['id'],role) for o in policy['obligations'] for role in electrical_locality.roles(o)}
assert {(r['relationship'],r['role']) for r in contract['templates']}==expected
assert len(contract['templates'])==len(expected)==118
# Every source row is represented by real physical pairs or has an explicit
# required-unknown guard in the consumer contract, including no-via subclauses.
guards=[u for b in contract['eligibility']['blocks'].values() for u in b['material_unknowns']]
for row in ledger:
    for endpoint in row['declared_primary_pair'].values():
        electrical_locality.resolve(probe['footprints'],endpoint)
    for binding in row['supported_bindings']:
        pair=obligations[binding['obligation']][binding['role']]
        historical=source_by_id[row['relationship']]
        # Compare the actual physical binding to the independent source pair,
        # not merely to a second serialization of the generated policy.
        is_return=historical['bound'].get('return_leg_max_mm') is not None and binding['role']=='return'
        retained_c98_return=row['relationship']=='U26.8-C98-secondary-decoupler' and binding['role']=='return'
        if not is_return and not retained_c98_return:
            assert pair['from']==row['declared_primary_pair']['from'] and pair['to']==row['declared_primary_pair']['to']
        if is_return:
            if historical.get('return'):
                named=historical['return']
                assert pair['from']=={'reference':named['device'],'pad':named['device_pad'],'net':named['net']}
                assert pair['to']=={'reference':named['support'],'pad':named['support_pad'],'net':named['net']}
            elif historical['kind']=='bootstrap':
                assert pair['from']['pad']=='8' and pair['to']['pad']=='2'
            else:
                f=pin_functions[pair['from']['reference']]['pins'][pair['from']['pad']][1]
                assert f.split('_')[0] in {'GND','AGND','DGND','PGND','VSS','V-'},f
                assert pair['from']['net']==pair['to']['net']=='/GND'
        assert template_by_key[binding['obligation'],binding['role']]==row['source_template']['template']
        for endpoint in (pair['from'],pair['to']):electrical_locality.resolve(probe['footprints'],endpoint)
    for gap in row['unresolved_gaps']:
        assert any(u['relationship']==row['relationship'] and u['gap']==gap for u in guards)
    assert row['supported_bindings'] or row['unresolved_gaps'],row['relationship']
# Keep the original 12 IDs and every original radius; authorize exactly four
# supply-pad changes. Ground and SW returns retain their physical endpoints.
corrected_ids={'u5-input-bulk-C1','u5-input-bulk-C2','u7-input-bulk-C8','u7-input-bulk-C9'}
for old in original['obligations']:
    new=obligations[old['id']]
    for role in electrical_locality.roles(old):
        assert new[role]['max_distance_nm']==old[role]['max_distance_nm']
        for side in ('from','to'):
            expected_endpoint=copy.deepcopy(old[role][side])
            if old['id'] in corrected_ids and role=='supply' and side=='from':expected_endpoint['pad']='2'
            assert new[role][side]==expected_endpoint
for r in ['U21.5-C84-hf-decoupler','U100.5-C133-hf-decoupler']:
    pair=obligations[r]['return']; ref='U21' if r.startswith('U21.') else 'U100'
    assert pair['from']=={'reference':ref,'pad':'3','net':'/+5V_CAN'}
    assert pair['to']['pad']=='2' and pair['to']['net']=='/+5V_CAN'
for oid in ['u5-boot-C5','u7-boot-C12']:
    assert obligations[oid]['return']['from']['pad']=='8'
for oid in ['u5-input-hf-C3','u5-input-bulk-C1','u5-input-bulk-C2','u5-vcc-C4','u7-input-hf-C10','u7-input-bulk-C8','u7-input-bulk-C9','u7-vcc-C11']:
    assert obligations[oid]['return']['from']['pad']=='1'
for o in policy['obligations']:
    for role in electrical_locality.roles(o):
        assert locality_provenance.classify(o[role],policy['source_records'])['enforcement']=='advisory'
        for endpoint in (o[role]['from'],o[role]['to']):electrical_locality.resolve(probe['footprints'],endpoint)

bound=copy.deepcopy(contract)
bound['allocation']['board_sha256']=probe['board_sha256']
bound['eligibility']['sources']['board_sha256']=probe['board_sha256']
section={'contract':bound,'side_eligibility':bound['eligibility'],'allocation_text':(p/'allocation-bridge.json').read_text()}
effective={'electrical_locality':policy}
members=block_contract.validate(probe,section,effective)
assert len(members['roles'])==313
report=block_contract.check_complete(probe,bound)
assert report['status']=='unknown' and not report['defects']
unknown_guard_rows=[u for u in report['unknown'] if u['kind']=='eligibility_requirement_unresolved']
assert {u['id'] for r in unknown_guard_rows for u in r['declaration']}=={u['id'] for u in guards}
controls=[]
def refuses(name,bad_section,bad_policy):
    try:block_contract.validate(probe,bad_section,bad_policy)
    except ValueError as exc:controls.append({'control':name,'result':'REFUSE','reason':str(exc)})
    else:raise AssertionError(name+': invalid contract admitted')
bad=copy.deepcopy(section)
bad['contract']['relationships']['obligations']=[o for o in bad['contract']['relationships']['obligations'] if o['id']!='U21.5-C84-hf-decoupler']
bad['contract']['templates']=[t for t in bad['contract']['templates'] if t['relationship']!='U21.5-C84-hf-decoupler']
refuses('omitted adopted VIO relationship against authenticated full corrected policy',bad,effective)
bad=copy.deepcopy(section)
next(o for o in bad['contract']['relationships']['obligations'] if o['id']=='u5-input-bulk-C1')['supply']['from']['pad']='3'
refuses('same-net wrong physical EN3 instead of VIN2 against corrected policy',bad,effective)
refuses('stale cA 12-obligation effective policy',section,{'electrical_locality':original})
bad=copy.deepcopy(section)
next(o for o in bad['contract']['relationships']['obligations'] if o['id']=='U100.5-C133-hf-decoupler')['return']={
    'from':{'reference':'U100','pad':'2','net':'/GND'},'to':{'reference':'C133','pad':'2','net':'/GND'},'max_distance_nm':5000000}
refuses('unauthorized named VIO-to-VCC return relaxed to generic GND',bad,effective)
# Native endpoint wrong-net negative is independent of policy byte equality.
wrong_pin=copy.deepcopy(obligations['u5-input-bulk-C1']['supply']['from']);wrong_pin['pad']='4'
try:electrical_locality.resolve(probe['footprints'],wrong_pin)
except ValueError as exc:controls.append({'control':'wrong physical native PG4 claimed as protected supply','result':'REFUSE','reason':str(exc)})
else:raise AssertionError('wrong physical pin passed native resolution')
for oid in ['U6.8-C16-ldo-cap','U12.8-C20-ldo-cap','U27.12-C118-hf-decoupler','U28.12-C120-hf-decoupler','U29.12-C122-hf-decoupler']:
    candidate=copy.deepcopy(probe);o=obligations[oid]
    dev=next(f for f in candidate['footprints'] if f['ref']==o['supply']['from']['reference'])
    cap=next(f for f in candidate['footprints'] if f['ref']==o['supply']['to']['reference'])
    cap['side']='B' if dev['side']=='F' else 'F'
    fault=block_contract.check_complete(candidate,bound)
    assert any(d['kind']=='same_face_required' and d['relationship']==oid for d in fault['defects'])
    controls.append({'control':'unauthorized opposite-side support: '+oid,'result':'DEFECT','reason':'same_face_required'})
# Demonstrate the exact implementation gaps through the unmodified consumer.
gap_controls=[]
for name,mutation in [('G1_SINGLE_LEG_SCHEMA',{'schema':electrical_locality.SCHEMA,'obligations':[{
    'id':'U5.5-R27-feedback','metric':'pad-centre-to-centre','supply':{
        **next(r['declared_primary_pair'] for r in ledger if r['relationship']=='U5.5-R27-feedback'),
        'max_distance_nm':5000000,'provenance':{'class':'default'}}}]}),
    ('G2_NO_VIA_EVIDENCE',copy.deepcopy(policy))]:
    if name=='G2_NO_VIA_EVIDENCE':
        next(o for o in mutation['obligations'] if o['id']=='U27.12-C118-hf-decoupler')['no_vias_required']=True
    try:electrical_locality.validate(mutation)
    except ValueError as exc:gap_controls.append({'gap':name,'result':'UNSUPPORTED_REFUSAL','reason':str(exc)})
    else:raise AssertionError('consumer unexpectedly supports '+name)
output={'verdict':'SUPPORTED INCREMENT IMPLEMENTED; full acceptance UNRESOLVED and consumer refuses pass by required unknowns',
    'consumer_head':'8e3b382b0f48525742cfd520e3f306b12e78a468','real_consumer_declaration_positive':'PASS',
    'real_consumer_full_check_status':report['status'],'native_endpoint_resolutions':len(expected)*2,
    'all_source_primary_endpoint_resolutions':len(ledger)*2,'source_rows':len(ledger),'cross_face_rows':211,
    'source_rows_with_supported_bindings':sum(bool(r['supported_bindings']) for r in ledger),
    'unresolved_source_rows':sum(r['status']=='UNRESOLVED' for r in ledger),'required_unknown_guards':len(guards),
    'full_check_unknown_counts':dict(Counter(u['kind'] for u in report['unknown'])),
    'negative_controls':controls,'gap_controls':gap_controls,
    'limitations':['Full check does not pass; all numeric maxima remain ADVISORY.',
                   'Equality negatives compare against the authenticated corrected effective policy; consumer does not independently interpret primary datasheets.',
                   'Side fault controls mutate only in-memory capture copies; no native board/schematic edits or routed-via qualification.']}
Path(args.report).write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
