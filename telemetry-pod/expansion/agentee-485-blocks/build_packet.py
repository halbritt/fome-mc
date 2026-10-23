"""Incrementally correct the cA locality/contract sources from frozen evidence.

Run from the frozen fome-mc root with the writer-C native probe JSON path.
Unsupported source requirements become required unknowns in the real contract.
No synthetic returns, manufacturer numeric radii, board or topology changes.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
from collections import defaultdict

ROOT = Path('telemetry-pod')
EXP = ROOT / 'expansion'
PREP = EXP / 'agentee-478-prep'
OUT = EXP / 'agentee-485-blocks'
POLICY = EXP / 'electrical-locality/pad-obligations/electrical-locality.json'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
def read(path):
    return json.loads(Path(path).read_bytes())
def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')
def write(name, value):
    (OUT/name).write_bytes(encode(value))

probe_path = Path(sys.argv[1])
probe = read(probe_path)
board_hash = sha((ROOT/'telemetry-pod.kicad_pcb').read_bytes())
assert probe['board_sha256'] == board_hash
native = {f['ref']: f for f in probe['footprints']}
assert len(native) == 313
before = read(OUT/'policy-before-cA2.json')
policy = copy.deepcopy(before)
relations_doc = read(PREP/'relationship-bounds.json')
relations = {r['id']: r for r in relations_doc['relationships']}
instances = {r['relationship']: r for r in read(PREP/'cross-face-templates.json')['instances']}
assert len(relations) == 214 and len(instances) == 211
netlist_path = PREP/'extract/emitted-schematic-netlist-cef8e4c7.json'
netlist = read(netlist_path)['components']
allocation = read(OUT/'allocation-template.json')
assert allocation['board_sha256'] is None
eligibility = read(OUT/'eligibility-before-cA2.json')
roles = read(OUT/'membership-coverage.json')['roles']
for entry in eligibility['blocks'].values():
    entry['material_unknowns'] = []

# Explicit engineering return-pin designations, based on electrical pin roles in
# the retained netlist and primary pin tables, never nearest arbitrary GND ties.
# Pin 9 EP, strap pins, USB supply, card detect and shields are not substitutes
# for the selected functional power ground. Numeric limits remain defaults.
selected_grounds = {
    'U1': '1', 'U100': '2', 'J3': '6', 'U3': '24', 'U4': '14',
}
def ground_pin(r):
    ref, supply = r['device']['ref'], r['device']['pin']
    if ref in ('U5','U7'):
        return '1', 'TI LMR36520 p.4 PGND1; thermal PAD is not an electrical interconnect; layout p.27.'
    if ref in ('U6','U12'):
        return ('6' if supply == '8' else '3'), 'Engineering designation of adjacent electrical GND pin (TPS7B4253 p.3 GND3/GND6), excluding thermal EP9.'
    if ref in ('U27','U28','U29'):
        return ('5' if supply == '12' else '4'), 'TI ADS1119 p.3 PW package: AVDD12/AGND5; DVDD13/DGND4. Exclude grounded address pins.'
    if ref == 'U2':
        return ('7' if supply == '8' else '6'), 'Engineering designation of adjacent GND7/GND6 (LSM6DSO32 pin description p.24); exclude grounded SDx/SCx signal pins.'
    if ref in selected_grounds:
        return selected_grounds[ref], 'Engineering designated functional power-ground pin from retained native netlist pin functions; no numeric manufacturer-radius claim.'
    pins = {p['number'] for p in native[ref]['pads'] if p['net'] == '/GND'}
    assert len(pins) == 1, (ref,pins)
    return next(iter(pins)), 'Unique captured GND pad; retained relationship declares a GND return.'

def endpoint(ref, pin, net):
    return {'reference': ref, 'pad': str(pin), 'net': net}
def support_endpoint(r):
    support = r['support']
    matches = {p['number'] for p in native[support['ref']]['pads'] if p['net'] == support['pin_net']}
    assert len(matches) == 1, (r['id'],matches)
    return endpoint(support['ref'], next(iter(matches)), support['pin_net'])
def citation(r):
    sources = [f"{x['source']} sha256 {x['sha256']} p.{x['page']}" for x in r['provenance'] if 'source' in x]
    return '; '.join(sources + [str(PREP/'relationship-bounds.json')+' /relationships/'+r['id'],
                               'Numeric maximum is an ADVISORY engineering default; qualitative manufacturer prose does not establish a radius.'])
def pair(r):
    return {'from': endpoint(r['device']['ref'],r['device']['pin'],r['device']['net']),
            'to': support_endpoint(r), 'max_distance_nm': round(r['bound']['supply_leg_max_mm']*1000000),
            'citation': citation(r), 'provenance': {'class':'default','numeric_provenance':'retained 478 engineering default, not manufacturer or owner numeric authority'}}

template_map = {(r['relationship'],r['role']):r['template'] for r in read(OUT/'block-contract-template.json')['templates']
                if r['relationship'] in {o['id'] for o in before['obligations']}}
links = defaultdict(list)
by_id = {o['id']:o for o in policy['obligations']}
corrections = []
# Keep original IDs, all existing limits and citations. Correct only the four
# physical supply selectors called out by the retained TI source evidence.
for oid in ['u5-input-bulk-C1','u5-input-bulk-C2','u7-input-bulk-C8','u7-input-bulk-C9']:
    o = by_id[oid]
    old = copy.deepcopy(o['supply']['from'])
    o['supply']['from']['pad'] = '2'
    o['supply']['citation'] += '; A2 source correction: TI LMR36520 retained pin table p.4 identifies VIN2 and EN3; layout p.27 item1 requires VIN/PGND locality. Same net is not the same physical pin.'
    corrections.append({'id':oid,'old_from':old,'new_from':copy.deepcopy(o['supply']['from']),
                        'reason':'Correct EN3 to VIN2 from primary TI pin table p.4 and layout p.27; preserve ADVISORY radius.'})
for o in policy['obligations']:
    for role in ('supply','return','switch'):
        if role in o:
            o[role]['provenance'] = {'class':'default','numeric_provenance':'unchanged effective ADVISORY bound; no manufacturer numeric radius'}
for row in relations_doc['old_obligations_disposition']:
    for i,rid in enumerate(row['new']):
        for role in (['switch'] if i else ['supply','return']):
            if role in by_id[row['old_id']]:
                links[rid].append({'obligation':row['old_id'],'role':role})

selected_returns = []
for rid,r in relations.items():
    if rid in links or r['bound'].get('return_leg_max_mm') is None:
        continue
    supply = pair(r)
    ret = r.get('return')
    if ret:
        a = endpoint(ret['device'],ret['device_pad'],ret['net'])
        b = endpoint(ret['support'],ret['support_pad'],ret['net'])
        reason = 'Preserve adopted 488 VIO-to-VCC named return, agent-529 061a1b20@2. No GND substitution.'
    else:
        pin,reason = ground_pin(r)
        a = endpoint(r['device']['ref'],pin,'/GND')
        grounds = {p['number'] for p in native[r['support']['ref']]['pads'] if p['net']=='/GND'}
        assert len(grounds)==1,(rid,grounds)
        b = endpoint(r['support']['ref'],next(iter(grounds)),'/GND')
    returned = {'from':a,'to':b,'max_distance_nm':round(r['bound']['return_leg_max_mm']*1000000),
                'citation':citation(r)+'; '+reason,
                'provenance':{'class':'default','numeric_provenance':'retained 478 ADVISORY engineering return default','pin_selection_reason':reason}}
    policy['obligations'].append({'id':rid,'metric':'pad-centre-to-centre','supply':supply,'return':returned})
    for role in ('supply','return'):
        links[rid].append({'obligation':rid,'role':role})
        template_map[rid,role] = instances[rid]['template']
    selected_returns.append({'relationship':rid,'return':returned,'reason':reason})

# Represent a single leg only by pairing it with another ALREADY DECLARED leg
# to a distinct physical pad on the same support. Never invent a fake return.
remaining = defaultdict(list)
for rid,r in relations.items():
    if rid not in links and r['support'] and r['bound'].get('supply_leg_max_mm') is not None:
        remaining[r['support']['ref']].append(r)
paired = {}
for rows in remaining.values():
    for r in rows:
        a = pair(r)
        peers=[]
        for other in rows:
            if other['id']==r['id']:continue
            b=pair(other)
            if (a['to']['pad']!=b['to']['pad'] and a['from']!=b['from'] and
                (a['from']['reference']==b['from']['reference'] or a['from']['net']!=b['from']['net'])):
                peers.append(other)
        if not peers:continue
        other=sorted(peers,key=lambda x:x['id'])[0]
        ids=tuple(sorted([r['id'],other['id']]))
        if ids not in paired:
            first,second=(relations[i] for i in ids)
            oid='paired:'+ids[0]+'|'+ids[1]
            policy['obligations'].append({'id':oid,'metric':'pad-centre-to-centre','supply':pair(first),'return':pair(second)})
            for role,source in [('supply',first),('return',second)]:
                links[source['id']].append({'obligation':oid,'role':role})
                template_map[oid,role]=instances[source['id']]['template']
            paired[ids]=oid

# Explicit source-backed coverage guards use the existing consumer mechanism.
# They cannot be mistaken for accepted electrical coverage by block_contract.
ledger=[]
def block_for(r):
    refs=[r['support']['ref']] if r['support'] else []
    refs.append(r['device']['ref'])
    for ref in refs:
        if roles[ref]['role']=='block':return roles[ref]['block_id']
    return 'gnss-rf-feed' if r['kind']=='rf-line' else 'power-entry'
for rid,r in relations.items():
    gaps=[]
    if rid not in links:
        gaps.append('G1_SINGLE_LEG_SCHEMA' if r['kind']!='rf-line' else 'G3_RF_CORRIDOR_AND_IMPEDANCE')
    no_vias=(r['device']['ref'] in ('U27','U28','U29') and r['kind']=='hf-decoupler') or r['kind']=='crystal'
    if no_vias:gaps.append('G2_NO_VIA_EVIDENCE')
    mapped=links.get(rid,[])
    # Resolve historical generic return selectors to designated functional
    # physical grounds; primary PGND/SW corrections override erroneous defaults.
    superseded=[]
    if r['bound'].get('return_leg_max_mm') is not None and not r.get('return'):
        superseded.append('Replace nearest-any-GND selector (including tied signal/EP pads) with explicit functional power-ground designation; bootstrap uses SW, not GND. See role bindings and selected returns.')
    if r['device']['ref'] in ('U5','U7') and r['bound'].get('return_leg_max_mm') is not None:
        superseded.append('LMR36520 retained PDF c5be6bd4 p.4 and p.27: use explicit SW8 for BOOT7 capacitor return, otherwise PGND1; exclude thermal PAD9 as an electrical return selector.')
    if rid in {x for d in relations_doc['old_obligations_disposition'] for x in d['new']}:
        superseded.append('Deduplicate corrected endpoint intent into preserved effective obligation IDs and existing ADVISORY bounds. Historical class radii are explicitly superseded, not hardened.')
    if rid=='J2.1-none-rf-line':
        superseded.append('Resolve the historical null support placeholder to U3.11 from that same retained source row reason (J2 to U3.11 RF path); no bound or impedance acceptance is inferred.')
    status='UNRESOLVED' if gaps else 'REPRESENTED'
    disposition='EXPLICITLY_SUPERSEDE' if superseded else 'CARRY_FORWARD'
    if mapped and not superseded and len(mapped)>1 and r['bound'].get('return_leg_max_mm') is None:
        disposition='DEDUPLICATE'
    declared = ({'from':endpoint(r['device']['ref'],r['device']['pin'],r['device']['net']), 'to':support_endpoint(r)} if r['support'] else {'from':endpoint('J2','1','/POD_GNSS_RF'), 'to':endpoint('U3','11','/POD_GNSS_RF')})
    row={'declared_primary_pair':declared, 'relationship':rid,'historical_cross_face_instance':rid in instances,'kind':r['kind'],
         'disposition':disposition,'disposition_reason':('; '.join(superseded) if superseded else 'Retain the exact declared physical edge and source template; consumer support is incomplete, so preserve it as a required unknown.' if gaps else 'Carry the original physical relationship and source template into supported policy roles; any repeated binding is the same exact declared edge, not a new edge.'),'status':status,'supported_bindings':mapped,'unresolved_gaps':gaps,
         'source':{'path':str(PREP/'relationship-bounds.json'),'record':r},
         'source_template':instances.get(rid), 'supersession_reason':superseded,
         'no_vias_required':no_vias, 'block':block_for(r)}
    ledger.append(row)
    for gap in gaps:
        eligibility['blocks'][row['block']]['material_unknowns'].append({
            'id':rid+':'+gap,'relationship':rid,'status':'UNRESOLVED','gap':gap,
            'requirement':('No vias between this bypass/device pair; same-side placement alone does not prove it.' if gap=='G2_NO_VIA_EVIDENCE' else
                           'Preserve RF path, F-over-In1 reference corridor and 50-ohm source requirement; no invented radius.' if gap=='G3_RF_CORRIDOR_AND_IMPEDANCE' else
                           'Enforce this existing single physical pin relationship without fabricating a second return.'),
            'source':str(PREP/'relationship-bounds.json')+' /relationships/'+rid})
assert len(ledger)==214 and sum(r['historical_cross_face_instance'] for r in ledger)==211
# Store the exact complete source/coverage document in the supported source text
# surface as well as the contract guard; the consumer does not parse this ledger.
ledger_doc={'schema':'fome-mc.relationship-source-disposition/1','owner_item_4':'Enforce the declared relationships between devices and their decoupling, feedback, filtering, protection, and other supporting components',
            'owner_source':'verbatim current dispatch, 2026-10-23; chief 531 1cc5fe76@1 relayed authority',
            'rows':ledger}
write('coverage-ledger.json',ledger_doc)
policy['source_records']={str(OUT/'coverage-ledger.json'):encode(ledger_doc).decode('utf-8')}
raw=encode(policy)
POLICY.write_bytes(raw)
(OUT/'relationships-effective.json').write_bytes(raw)
write('eligibility-template.json',eligibility)
contract={'schema':'agent-ee.block-contract/1','allocation':allocation,'eligibility':eligibility,
          'templates':[{'relationship':key[0],'role':key[1],'template':value} for key,value in sorted(template_map.items())],
          'thickness_nm':1600000}
encoded=json.dumps(contract,indent=2).rstrip()[:-1].rstrip()+',\n  "relationships": '
(OUT/'block-contract-template.json').write_bytes(encoded.encode('utf-8')+raw+b'\n}\n')
assert read(OUT/'block-contract-template.json')['relationships']==policy
write('selected-return-pins.json',selected_returns)
write('policy-corrections.json',{'bulk_vin_corrections':corrections,
    'preserved_original_obligations':list(by_id),'added_supported_obligations':[o['id'] for o in policy['obligations'] if o['id'] not in by_id],
    'existing_numeric_limits_changed':False,'old_policy_sha256':sha((OUT/'policy-before-cA2.json').read_bytes()),
    'source':str(PREP/'relationship-bounds.json'),'pairing_note':'Supply/return are consumer role names; paired single-leg roles retain their original electrical kind and actual declared endpoints. No new electrical edge is synthesized.'})
write('unresolved-decisions.json',{'authority':'Consumer implementation gaps; no owner clarification required.',
    'gaps':{
      'G1_SINGLE_LEG_SCHEMA':{'module':'agent_ee.electrical_locality._validated','requirement':'Allow an explicit nonempty named leg list / single pair without fabricating a capacitor supply/return. Keep exact physical endpoints and per-leg templates.',
                            'current_refusal':'locality obligation needs id, metric, supply and return; optional switch'},
      'G2_NO_VIA_EVIDENCE':{'module':'agent_ee.block_contract.judge / native route evidence','requirement':'Represent and independently grade a source-backed no-vias-between-endpoints requirement against authenticated routed geometry. Same-face alone is insufficient.'},
      'G3_RF_CORRIDOR_AND_IMPEDANCE':{'module':'agent_ee.electrical_locality / block_contract','requirement':'Represent routed RF path topology/reference corridor/impedance evidence independently of an unsourced pad-centre radius. Preserve the three explicit source records.'},
      'G4_ADVISORY_ACCEPTANCE':{'module':'agent_ee.block_contract.judge','requirement':'Separate qualitative/source coverage completion from numeric authority. Current consumer emits required_numeric_authority_missing for ADVISORY maxima; do not counterfeit numeric hard authority to get pass.'}},
    'rows':[r for r in ledger if r['status']=='UNRESOLVED']})
counts={'historical_cross_face_rows':211,'additional_rf_rows':3,'total_source_rows':214,
    'source_rows_with_supported_bindings':sum(bool(r['supported_bindings']) for r in ledger),
    'source_rows_unresolved':sum(r['status']=='UNRESOLVED' for r in ledger),
    'effective_obligations':len(policy['obligations']),'effective_roles':sum(len([k for k in ('supply','return','switch') if k in o]) for o in policy['obligations']),
    'required_unknown_guards':sum(len(x['material_unknowns']) for x in eligibility['blocks'].values())}
write('source-reconciliation.json',counts)
write('cross-face-ledger.json',[r for r in ledger if r['historical_cross_face_instance']])
write('effective-role-mapping.json',[{'obligation':o['id'],'role':role,'pair':o[role],
      'historical_relationships':[r['relationship'] for r in ledger if {'obligation':o['id'],'role':role} in r['supported_bindings']]}
      for o in policy['obligations'] for role in ('supply','return','switch') if role in o])
write('frozen-sources.json',{'fome_mc_head':'15544f67b00175a08eb34996de94c15e79eb7fe2','agent_ee_head':'8e3b382b0f48525742cfd520e3f306b12e78a468',
    'board_sha256':board_hash,'native_probe_sha256':sha(probe_path.read_bytes()),
    'reservations_sha256':sha((EXP/'agentee-489-source/reservations.json').read_bytes()),
    'source_hashes':{str(p):sha(p.read_bytes()) for p in [PREP/'relationship-bounds.json',PREP/'cross-face-templates.json',netlist_path,OUT/'policy-before-cA2.json',OUT/'eligibility-before-cA2.json']},
    'primary_source_hash_checks':{k:sha(Path(v['path']).read_bytes())==v['sha256'] for k,v in relations_doc['sources'].items()}})
assert sha((EXP/'agentee-489-source/reservations.json').read_bytes())=='a4504674758717274f9be567188751cd11c9721d4a4f434b9c9fc59f7345d1cd'
assert all(read(OUT/'frozen-sources.json')['primary_source_hash_checks'].values())
lines=['# A2 all-source disposition ledger','','211 cross-face rows plus three RF records. Each original source record is retained in coverage-ledger.json. UNRESOLVED rows are required unknowns in the consumer contract, never acceptance by omission.','','| Relationship | Disposition | State | Exact supported role bindings | Required gap |','|---|---|---|---|---|']
for r in ledger:
    bs=[]
    for link in r['supported_bindings']:
        o=next(o for o in policy['obligations'] if o['id']==link['obligation']);p=o[link['role']]
        bs.append(link['obligation']+'/'+link['role']+': '+p['from']['reference']+'.'+p['from']['pad']+' → '+p['to']['reference']+'.'+p['to']['pad'])
    lines.append('| '+' | '.join(cell.replace('|',r'\|') for cell in [r['relationship'],r['disposition'],r['status'],'; '.join(bs) or 'No invented return; source retained as required unknown',', '.join(r['unresolved_gaps']) or '—'])+' |')
for name in ['MAPPING.md','CROSS_FACE_MAPPING.md']:(OUT/name).write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(counts,indent=2))
write('POLICY-HASHES.json',{
    'effective_policy_path':str(POLICY),'effective_policy_sha256':sha(POLICY.read_bytes()),
    'contract_sha256':sha((OUT/'block-contract-template.json').read_bytes()),
    'eligibility_sha256':sha((OUT/'eligibility-template.json').read_bytes()),
    'coverage_ledger_sha256':sha((OUT/'coverage-ledger.json').read_bytes()),
    'allocation_template_sha256':sha((OUT/'allocation-template.json').read_bytes())})
