"""AGENTEE-488 focused tests: named returns are measured exactly; a missing/wrong-net/unmeasurable return never passes.
Run: python3 -I test_relationship_measure.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from relationship_measure import named_return_leg, gnd_return_leg, leg, verdict
results = []
def case(name, cond):
    results.append(bool(cond)); print(('PASS ' if cond else 'FAIL ') + name)
def fp(side, pads):
    return {'side': side, 'pads': [dict(number=n, net=net, x=x, y=y) for n, net, x, y in pads]}
RET = {'device_pad': '3', 'support_pad': '2', 'net': '/+5V_CAN'}
BOUND = {'supply_leg_max_mm': 3.0, 'return_leg_max_mm': 5.0, 'same_face_required': False}
good = {'U100': fp('F', [('5', '/+3V3', 0, 0), ('3', '/+5V_CAN', 1, 0), ('2', '/GND', 2, 0)]),
        'C133': fp('F', [('1', '/+3V3', 0, 1), ('2', '/+5V_CAN', 1, 1)])}
s = leg(good, 'U100', '5', 'C133', '/+3V3'); r = named_return_leg(good, 'U100', 'C133', RET)
case('positive: named supply and return measured', s == 1.0 and r == 1.0 and verdict(BOUND, s, r, True) == 'within')
far = {**good, 'C133': fp('F', [('1', '/+3V3', 0, 1), ('2', '/+5V_CAN', 1, 7)])}
case('positive: governed return overrun is exceeds', verdict(BOUND, 1.0, named_return_leg(far, 'U100', 'C133', RET), True) == 'exceeds')
wrong = {**good, 'C133': fp('F', [('1', '/+3V3', 0, 1), ('2', '/GND', 1, 1)])}
rw = named_return_leg(wrong, 'U100', 'C133', RET)
case('negative: wrong-net support return (GND) is unmeasurable', rw is None)
case('negative: wrong-net return verdict is unsatisfied, not within', verdict(BOUND, 1.0, rw, True).startswith('unsatisfied'))
case('negative: no GND inference for the named return (GND pads present but not used)', gnd_return_leg(wrong, 'U100', 'C133') is not None and rw is None)
missing = {**good, 'C133': fp('F', [('1', '/+3V3', 0, 1)])}
case('negative: missing return pad -> unsatisfied', verdict(BOUND, 1.0, named_return_leg(missing, 'U100', 'C133', RET), True).startswith('unsatisfied'))
nodev = {**good, 'U100': fp('F', [('5', '/+3V3', 0, 0)])}
case('negative: missing device return pad -> unsatisfied', verdict(BOUND, 1.0, named_return_leg(nodev, 'U100', 'C133', RET), True).startswith('unsatisfied'))
nognd = {'U9': fp('F', [('5', '/+3V3', 0, 0)]), 'C132': fp('F', [('1', '/+3V3', 0, 1), ('2', '/GND', 1, 1)])}
case('negative: generic GND return unmeasurable -> unsatisfied (old code passed this)', verdict(BOUND, 1.0, gnd_return_leg(nognd, 'U9', 'C132'), True).startswith('unsatisfied'))
case('supply-only bound with no return declared still passes on supply', verdict({'supply_leg_max_mm': 3.0, 'return_leg_max_mm': None}, 1.0, None, True) == 'within')
print(f'{sum(results)}/{len(results)} passed'); sys.exit(0 if all(results) else 1)
