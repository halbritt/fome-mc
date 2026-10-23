"""AGENTEE-487 focused regression (final policy island_removal=always for both planes; agent-529 76150ac4 option a).
Usage: regression_check.py <regression-final-old.json> <regression-final-pin.json> <regression-badnet-new.json>
- final-old: the PRODUCTION producer (agent-ee 7d5b0d4d) on the placed R5 board refuses the always plan (original evidence);
- final-pin: the same producer + the add_planes fix: adopted, exactly /GND In1.Cu and /+3V3 In2.Cu copper zones, the plan
  still always/always, and the wholly unconnected /+3V3 zone listed as deferred post-routing connectivity;
- badnet-new: a wrong net identity ('GND' for '/GND') still FAILS with the fixed producer."""
import json, sys
old, new, bad = (json.load(open(p)) for p in sys.argv[1:4])
ok = True
def check(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name); ok = ok and bool(cond)
o, n, b = old['r5-placed'], new['r5-placed'], bad['r5-placed']
check('declared step is stage routing / add-planes', new['spec_stage'] == 'routing' and new['spec_step'] == 'add-planes')
check('final plan is always/always', [z['island_removal'] for z in new['plan']['zones']] == ['always', 'always'])
check('before (production producer): refused, not adopted', o['exit'] == 1 and o['adopted'] is not True
      and 'planned zones' in json.dumps(o['report']['findings']))
copper = sorted((z['net'], tuple(z['layers'])) for z in n['zones_after'] if not z['rule_area'])
check('after: exit 0, adopted', n['exit'] == 0 and n['adopted'] is True)
check('after: copper zones exactly /GND In1.Cu and /+3V3 In2.Cu', copper == [('/+3V3', ('In2.Cu',)), ('/GND', ('In1.Cu',))])
d = n['report']['deferred_connectivity']
plus = next(z['uuid'] for z in n['report']['zones'] if z['net'] == '/+3V3')
check('after: /+3V3 zone deferred with policy always, /GND not deferred', [x['zone'] for x in d] == [plus] and d[0]['island_removal'] == 'always')
check('after: rule areas preserved', sorted(z['name'] for z in n['zones_after'] if z['rule_area']) == sorted(z['name'] for z in n['zones_before'] if z['rule_area']))
check('wrong net still fails', b['exit'] == 1 and 'planned plane net is missing: GND' in json.dumps(b['report']['findings']))
sys.exit(0 if ok else 1)
