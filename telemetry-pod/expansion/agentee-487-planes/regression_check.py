"""AGENTEE-487 focused regression assertion over planes_phase_proof.py outputs.
Usage: regression_check.py <regression-before.json> <regression-after.json>
before (captured plan with /+3V3 island_removal 'always'): the declared add-planes step must REFUSE on the placed board;
after (repaired plan): it must succeed, be adopted, and leave exactly /GND on In1.Cu and /+3V3 on In2.Cu copper zones."""
import json, sys
before, after = (json.load(open(p)) for p in sys.argv[1:3])
ok = True
def check(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name); ok = ok and cond
b, a = before['r5-placed'], after['r5-placed']
check('declared step is stage routing / add-planes', before['spec_stage'] == 'routing' and before['spec_step'] == 'add-planes')
check('before: refused (exit 1, not adopted, no copper zone)', b['exit'] == 1 and b['adopted'] is not True and not [z for z in b['zones_after'] if not z['rule_area']])
copper = sorted((z['net'], tuple(z['layers'])) for z in a['zones_after'] if not z['rule_area'])
check('after: exit 0 and adopted', a['exit'] == 0 and a['adopted'] is True)
check('after: copper zones exactly /GND In1.Cu and /+3V3 In2.Cu', copper == [('/+3V3', ('In2.Cu',)), ('/GND', ('In1.Cu',))])
check('after: rule areas preserved', sorted(z['name'] for z in a['zones_after'] if z['rule_area']) == sorted(z['name'] for z in b['zones_before'] if z['rule_area']))
sys.exit(0 if ok else 1)
