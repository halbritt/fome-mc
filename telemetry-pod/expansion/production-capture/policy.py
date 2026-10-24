"""The derived request policy (composition/placement-policy.json) and its derivation record, from their two sources.

AGENTEE-485 R1. The policy was derived once (2c768d1) from the agent-449 iter8n packing policy by removing
fixed_overhangs (composition/placement-policy-derivation.json). Re-running that derivation reproduces those bytes
exactly (5fab430a), but the policy then embeds iter8n's 12-obligation electrical_locality, while the production scope
grades the A3 locality (electrical-locality/pad-obligations/electrical-locality.json, 201 obligations), so agent-ee
placement_adapter.bind_locality refuses ("packing electrical locality differs from captured coordinator
obligations"). This producer applies the same derivation and replaces the embedded electrical_locality with the
captured A3 document, byte for byte as parsed, so bind_locality binds it. Both sources are pinned by sha256; a
changed source refuses. Nothing else in the policy changes.

Usage (fome-mc root):
  python3 telemetry-pod/expansion/production-capture/policy.py ITER8N_POLICY [--check]
--check regenerates in memory and refuses unless the committed policy and derivation record equal the output.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = '63138a34d197485673ac8a5615f3d8f39a5a0e50bab95f2e09ff71af5a81c5fb'  # iter8n policy.json (derivation record)
LOCALITY = HERE.parent / 'electrical-locality/pad-obligations/electrical-locality.json'
LOCALITY_SHA = '9852c3ed0127a5b40c957f0624a8cecddf67c1ff2fc8597fba3a1a1e8dc69b7c'  # A3, the scope's locality check
POLICY, RECORD = HERE / 'composition/placement-policy.json', HERE / 'composition/placement-policy-derivation.json'


def dump(doc):
    return (json.dumps(doc, indent=1, sort_keys=True) + '\n').encode()


def produce(source_path):
    raw, loc_raw = Path(source_path).read_bytes(), LOCALITY.read_bytes()
    for name, data, want in (('iter8n policy', raw, SOURCE_SHA), ('A3 locality', loc_raw, LOCALITY_SHA)):
        if hashlib.sha256(data).hexdigest() != want:
            sys.exit(f'{name} sha256 {hashlib.sha256(data).hexdigest()} is not the pinned {want}')
    source, locality = json.loads(raw), json.loads(loc_raw)
    overhangs = source.pop('fixed_overhangs')
    replaced = len(source['electrical_locality']['obligations'])
    source['electrical_locality'] = locality
    policy = dump(source)
    record = json.loads(RECORD.read_text()) if RECORD.is_file() else {}
    record.update({
        'schema': 'pod-capture.policy-derivation/2', 'kept': sorted(source), 'output_sha256':
        hashlib.sha256(policy).hexdigest(), 'producer': 'production-capture/policy.py',
        'source': {'path': '~/.cache/agent449-pod/iter8n/policy.json (agent-449 iter8n packing policy, latest microSD '
                           'policy)', 'sha256': SOURCE_SHA}})
    record['removed']['fixed_overhangs']['count'] = len(overhangs)
    record['replaced'] = {'electrical_locality': {
        'source': {'path': 'telemetry-pod/expansion/electrical-locality/pad-obligations/electrical-locality.json',
                   'sha256': LOCALITY_SHA}, 'obligations': len(locality['obligations']), 'replaced_obligations':
        replaced, 'reason': ('placement_adapter.bind_locality refuses a policy locality that differs from the scope\'s '
                             'captured locality; the scope grades the A3 document (AGENTEE-485 R1)')}}
    return policy, dump(record)


if __name__ == '__main__':
    policy, record = produce(sys.argv[1])
    if '--check' in sys.argv[2:]:
        bad = [p.name for p, b in ((POLICY, policy), (RECORD, record)) if p.read_bytes() != b]
        sys.exit(f'differs from the producer output: {bad}' if bad else print('policy OK:',
                 hashlib.sha256(policy).hexdigest()))
    POLICY.write_bytes(policy)
    RECORD.write_bytes(record)
    print(hashlib.sha256(policy).hexdigest())
