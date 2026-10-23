"""Adopt the frozen A2 single-leg sources using the sealed G1/G4 consumer API.

Run at the fome-mc root with the retained native probe path. Frozen A2 git
objects are the baseline; repeated generation never adopts its own output.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from collections import Counter

BASE='a1678bdf6583263b4c0917de77a950f21c6748d6'
CONSUMER='8ab3b0b95dd3ece043e67fff6bd226c36427ff22'
OUT=Path('telemetry-pod/expansion/agentee-485-blocks')
POLICY=Path('telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json')
BOUNDS=Path('telemetry-pod/expansion/agentee-478-prep/relationship-bounds.json')
def frozen(path):
    return subprocess.check_output(['git','show',BASE+':'+str(path)])
def load(raw):return json.loads(raw)
def encode(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode('utf-8')
def write(name,value):(OUT/name).write_bytes(encode(value))
sha=lambda raw:hashlib.sha256(raw).hexdigest()

probe_path=Path(sys.argv[1]);probe=load(probe_path.read_bytes())
board=Path('telemetry-pod/telemetry-pod.kicad_pcb')
assert sha(board.read_bytes())==probe['board_sha256']
policy=load(frozen(POLICY));contract=load(frozen(OUT/'block-contract-template.json'))
eligibility=contract['eligibility'];ledger=load(frozen(OUT/'coverage-ledger.json'))
rows=ledger['rows'];by_source={r['relationship']:r for r in rows}
assert len(rows)==len(by_source)==214
old_policy_sha=sha(frozen(POLICY));old_contract_sha=sha(frozen(OUT/'block-contract-template.json'))
templates=contract['templates'];existing={o['id'] for o in policy['obligations']}
converted=[]
for row in rows:
    if 'G1_SINGLE_LEG_SCHEMA' not in row['unresolved_gaps']:continue
    rid=row['relationship'];source=row['source']['record'];pair=copy.deepcopy(row['declared_primary_pair'])
    assert rid not in existing
    target=source['bound']['supply_leg_max_mm']
    assert target is not None
    pair.update(max_distance_nm=round(target*1000000),
                citation=str(BOUNDS)+' /relationships/'+rid+'; retained ADVISORY engineering default, not a manufacturer or owner numeric radius.',
                provenance={'class':'default','numeric_provenance':'Unchanged 478 engineering target; exact physical source relationship adopted through kind=single-leg.'})
    policy['obligations'].append({'id':rid,'kind':'single-leg','metric':'pad-centre-to-centre','leg':pair})
    templates.append({'relationship':rid,'role':'leg','template':row['source_template']['template']})
    row['supported_bindings']=[{'obligation':rid,'role':'leg'}]
    row['disposition']='CARRY_FORWARD'
    row['disposition_reason']='Exact declared physical pair and original engineering maximum adopted as one explicit leg; no fabricated return.'
    converted.append(rid)
assert len(converted)==143
by_obligation={o['id']:o for o in policy['obligations']}

# The authoring record is captured byte-for-byte for source-reference checks.
source_raw=BOUNDS.read_bytes();assert source_raw==frozen(BOUNDS)
source_text=source_raw.decode('utf-8')
policy['source_records'][str(BOUNDS)]=source_text
routing=[]
for row in rows:
    gaps=row['unresolved_gaps']
    if not any(g in gaps for g in ['G2_NO_VIA_EVIDENCE','G3_RF_CORRIDOR_AND_IMPEDANCE']):continue
    pairs=[]
    for binding in row['supported_bindings']:
        pair=by_obligation[binding['obligation']][binding['role']]
        item={k:copy.deepcopy(pair[k]) for k in ('from','to')}
        if item not in pairs:pairs.append(item)
    if not pairs:pairs=[copy.deepcopy(row['declared_primary_pair'])]
    rid=row['relationship'];quote='"id": '+json.dumps(rid)
    assert quote in source_text
    routing.append({'id':rid,'stage':'routing',
        'kind':'no-via' if row['no_vias_required'] else 'controlled-impedance',
        'pairs':pairs,'requirement':json.dumps(row['source']['record'],sort_keys=True),
        'source':{'path':str(BOUNDS),'sha256':sha(source_raw),'locator':'/relationships/'+rid,'quote':quote}})
assert len(routing)==11 and Counter(r['kind'] for r in routing)=={'no-via':8,'controlled-impedance':3}
route_ids={r['id'] for r in routing}

# Remove only identified, now represented or stage-migrated guards. Preserve any
# unrelated material unknown, including future source additions.
migrations=[]
for bid,entry in eligibility['blocks'].items():
    keep=[]
    for guard in entry.get('material_unknowns',[]):
        rid=guard.get('relationship');gap=guard.get('gap')
        if gap=='G1_SINGLE_LEG_SCHEMA' and rid in converted:
            target={'obligation':rid,'role':'leg'}
            action='PLACEMENT_LEG_REPRESENTED'
        elif gap in ('G2_NO_VIA_EVIDENCE','G3_RF_CORRIDOR_AND_IMPEDANCE') and rid in route_ids:
            target={'routing_obligation':rid,'stage':'routing','status':'pending'}
            action='EXPLICIT_ROUTING_STAGE_MIGRATION'
        else:
            keep.append(guard);continue
        migrations.append({'block':bid,'original_guard':guard,'action':action,'target':target})
    entry['material_unknowns']=keep
assert len(migrations)==154
assert Counter(m['action'] for m in migrations)=={'PLACEMENT_LEG_REPRESENTED':143,'EXPLICIT_ROUTING_STAGE_MIGRATION':11}
for row in rows:
    old_gaps=row['unresolved_gaps'][:]
    row['a2_unresolved_gaps']=old_gaps
    row['unresolved_gaps']=[]
    row['pending_stage_requirements']=[{'gap':g,'id':row['relationship'],'stage':'routing','status':'pending'}
        for g in old_gaps if g in ('G2_NO_VIA_EVIDENCE','G3_RF_CORRIDOR_AND_IMPEDANCE')]
    row['status']=('PLACEMENT_REPRESENTED_ROUTING_PENDING' if row['supported_bindings'] else 'ROUTING_PENDING') if row['relationship'] in route_ids else 'REPRESENTED'
ledger['adoption']={'fome_baseline':BASE,'consumer':CONSUMER,'single_legs':143,
                    'routing_obligations':11,'meaning':'Placement representation adopted; no routing clause discharged.'}
write('coverage-ledger.json',ledger)
policy['source_records'][str(OUT/'coverage-ledger.json')]=encode(ledger).decode('utf-8')
contract['relationships']=policy;contract['eligibility']=eligibility
contract['routing_obligations']=routing
contract['templates']=sorted(templates,key=lambda r:(r['relationship'],r['role']))
raw=encode(policy);POLICY.write_bytes(raw);(OUT/'relationships-effective.json').write_bytes(raw)
# The exact policy byte span is also embedded in the contract's relationship value.
other={k:v for k,v in contract.items() if k!='relationships'}
prefix=json.dumps(other,indent=2).rstrip()[:-1].rstrip()+',\n  "relationships": '
(OUT/'block-contract-template.json').write_bytes(prefix.encode('utf-8')+raw+b'\n}\n')
write('eligibility-template.json',eligibility)
write('guard-migrations.json',migrations)
write('routing-obligations.json',routing)
write('single-leg-adoption.json',{'baseline':BASE,'consumer':CONSUMER,'baseline_policy_sha256':old_policy_sha,
    'baseline_contract_sha256':old_contract_sha,'single_leg_ids':converted,
    'preserved_a2_obligations':58,'preserved_a2_roles':118,'routing_stage_clauses':11})
counts={'historical_cross_face_rows':211,'additional_rf_rows':3,'total_source_rows':214,
        'source_rows_with_placement_bindings':sum(bool(r['supported_bindings']) for r in rows),
        'explicit_single_leg_obligations':len(converted),'effective_obligations':len(policy['obligations']),
        'effective_roles':sum(1 if o.get('kind')=='single-leg' else sum(k in o for k in ['supply','return','switch']) for o in policy['obligations']),
        'material_guards_remaining':sum(len(e.get('material_unknowns',[])) for e in eligibility['blocks'].values()),
        'routing_pending':11,'no_via_pending':8,'rf_pending':3}
write('source-reconciliation.json',counts)
write('cross-face-ledger.json',[r for r in rows if r['historical_cross_face_instance']])
write('effective-role-mapping.json',[{'obligation':o['id'],'role':role,'pair':o[role],
      'historical_relationships':[r['relationship'] for r in rows if {'obligation':o['id'],'role':role} in r['supported_bindings']]}
      for o in policy['obligations'] for role in (['leg'] if o.get('kind')=='single-leg' else [k for k in ['supply','return','switch'] if k in o])])
write('unresolved-decisions.json',{'G1_and_G4':'Resolved by sealed consumer '+CONSUMER+' and explicit adoption, not by lowering source scope.',
    'routing_obligations_pending':routing,'material_guards_remaining':[
      {'block':bid,'guard':g} for bid,b in eligibility['blocks'].items() for g in b.get('material_unknowns',[])],
    'remaining_native_findings':'See NATIVE-FINDINGS.json from the actual frozen-consumer check; no geometry or pin coverage waived.'})
write('frozen-sources.json',{'fome_mc_head':BASE,'agent_ee_head':CONSUMER,
    'board_sha256':probe['board_sha256'],'native_probe_sha256':sha(probe_path.read_bytes()),
    'reservations_sha256':sha(Path('telemetry-pod/expansion/agentee-489-source/reservations.json').read_bytes()),
    'relationship_bounds_sha256':sha(source_raw),'baseline_policy_sha256':old_policy_sha,'baseline_contract_sha256':old_contract_sha})
write('POLICY-HASHES.json',{'effective_policy_path':str(POLICY),'effective_policy_sha256':sha(raw),
    'contract_sha256':sha((OUT/'block-contract-template.json').read_bytes()),
    'eligibility_sha256':sha((OUT/'eligibility-template.json').read_bytes()),
    'coverage_ledger_sha256':sha((OUT/'coverage-ledger.json').read_bytes()),
    'routing_obligations_sha256':sha((OUT/'routing-obligations.json').read_bytes())})
lines=['# A3 complete source coverage','','All 211 cross-face relationships plus three RF records. Pending routing is not a pass. Sources and original disposition reasons remain in coverage-ledger.json.','','| Source relationship | State | Placement bindings | Pending routing |','|---|---|---|---|']
for row in rows:
    bindings=', '.join(b['obligation']+'/'+b['role'] for b in row['supported_bindings']) or '—'
    cells=[row['relationship'],row['status'],bindings,', '.join(r['gap'] for r in row['pending_stage_requirements']) or '—']
    lines.append('| '+' | '.join(c.replace('|',r'\|') for c in cells)+' |')
for name in ['MAPPING.md','CROSS_FACE_MAPPING.md']:(OUT/name).write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(counts,indent=2))
