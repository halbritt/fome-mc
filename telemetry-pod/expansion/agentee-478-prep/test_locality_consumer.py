"""AGENTEE-488 H1 consumer-boundary test: the EMITTED electrical-locality-named-returns.json must pass agent-ee's
electrical_locality.validate and classify as advisory (unsourced defaults).
Usage: python3 -I test_locality_consumer.py <agent-ee src dir>"""
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from agent_ee import electrical_locality, locality_provenance
doc = json.loads((Path(__file__).resolve().parent / 'electrical-locality-named-returns.json').read_text())
ok = True
try:
    electrical_locality.validate(doc); print('PASS emitted file validates against agent_ee.electrical_locality')
except ValueError as exc:
    ok = False; print('FAIL validate:', exc)
for o in doc['obligations']:
    for role in ('supply', 'return'):
        c = locality_provenance.classify(o[role], doc.get('source_records'))
        good = c['enforcement'] == 'advisory'
        ok = ok and good; print(('PASS ' if good else 'FAIL ') + f"{o['id']} {role}: {c['class']} / {c['enforcement']} ({c['reason']})")
    ret = o['return']
    good = ret['from']['net'] == ret['to']['net'] == '/+5V_CAN' and ret['max_distance_nm'] == 5000000
    ok = ok and good; print(('PASS ' if good else 'FAIL ') + f"{o['id']} named return on /+5V_CAN at 5 mm")
sys.exit(0 if ok else 1)
