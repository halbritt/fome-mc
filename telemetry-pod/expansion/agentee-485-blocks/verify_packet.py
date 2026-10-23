"""Verify declarations against the frozen real agent-ee consumer (no board writes)."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--agent-ee-src', required=True)
parser.add_argument('--probe', required=True)
args = parser.parse_args()
sys.path.insert(0, args.agent_ee_src)
from agent_ee import block_contract, electrical_locality

root = Path('telemetry-pod/expansion/agentee-485-blocks')
load = lambda name: json.loads((root / name).read_bytes())
contract = load('block-contract-template.json')
probe = json.loads(Path(args.probe).read_bytes())
sources = load('frozen-sources.json')
assert hashlib.sha256(Path(args.probe).read_bytes()).hexdigest() == sources['native_probe_sha256']
assert probe['board_sha256'] == sources['board_sha256']
for path, expected in sources['source_hashes'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
raw = Path('telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json').read_bytes()
encoded = (root / 'block-contract-template.json').read_bytes()
start = encoded.index(b'  "relationships": ') + len(b'  "relationships": ')
assert encoded[start:start + len(raw)] == raw
assert (root / 'relationships-effective.json').read_bytes() == raw
assert contract['allocation'] == load('allocation-template.json')
assert contract['eligibility'] == load('eligibility-template.json')
assert contract['allocation']['board_sha256'] is None
assert contract['eligibility']['sources']['board_sha256'] is None
assert contract['thickness_nm'] == 1600000
assert contract['relationships'] == json.loads(raw)
expected = {(o['id'], role) for o in contract['relationships']['obligations'] for role in electrical_locality.roles(o)}
actual = {(r['relationship'], r['role']) for r in contract['templates']}
assert actual == expected and len(actual) == len(contract['templates']) == 26
bound = copy.deepcopy(contract)
bound['allocation']['board_sha256'] = probe['board_sha256']
bound['eligibility']['sources']['board_sha256'] = probe['board_sha256']
section = {'contract': bound, 'side_eligibility': bound['eligibility'],
           'allocation_text': (root / 'allocation-bridge.json').read_text()}
policy = {'electrical_locality': json.loads(raw)}
members = block_contract.validate(probe, section, policy)
assert len(members['roles']) == 313 and len(members['blocks']) == 26
for o in contract['relationships']['obligations']:
    for role in electrical_locality.roles(o):
        for side in ('from', 'to'):
            electrical_locality.resolve(probe['footprints'], o[role][side])
ledger = load('cross-face-ledger.json')
legacy = json.loads(Path('telemetry-pod/expansion/agentee-478-prep/cross-face-templates.json').read_bytes())['instances']
assert {r['relationship'] for r in ledger} == {r['relationship'] for r in legacy}
assert len(ledger) == 211
assert sum(not r['effective_counterparts'] for r in ledger) == 197
assert all(load('source-reconciliation.json')['primary_source_hash_checks'].values())
refusals = []
def refuses(name, bad_section, bad_policy):
    try:
        block_contract.validate(probe, bad_section, bad_policy)
    except ValueError as exc:
        refusals.append({'control': name, 'refusal': str(exc)})
    else:
        raise AssertionError(name + ': consumer accepted invalid declaration')
refuses('unbound template cannot be consumed as bound contract',
        {**section, 'contract': contract, 'side_eligibility': contract['eligibility']}, policy)
bad = copy.deepcopy(section)
bad['contract']['allocation']['board_sha256'] = '0' * 64
refuses('stale board binding', bad, policy)
bad = copy.deepcopy(section)
bad['contract']['allocation']['blocks'][0]['references'].pop(0)
refuses('missing native allocation member', bad, policy)
bad_policy = copy.deepcopy(policy)
bad_policy['electrical_locality']['obligations'][0]['supply']['max_distance_nm'] += 1
refuses('different effective locality bytes/semantics', section, bad_policy)
bad = copy.deepcopy(section)
bad['contract']['templates'][0]['relationship'] = 'invented-string-match'
refuses('invented historical ID as effective ID', bad, policy)
print(json.dumps({'verdict': 'PASS: declaration/source controls only; full critical-pin acceptance unresolved',
    'native_footprints': len(members['roles']), 'blocks': len(members['blocks']),
    'effective_roles': len(actual), 'historical_rows': len(ledger), 'unmapped_historical_rows': 197,
    'byte_equal_relationships': True, 'native_endpoint_resolutions': 52,
    'real_consumer_positive': True, 'negative_controls': refusals}, indent=2))
