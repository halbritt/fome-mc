"""Extract current monitor coverage from the expanded source graph; no electrical qualification."""
import hashlib
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--intent', type=Path, default=ROOT.parent / 'series-divider/prepared/intent.json')
source = parser.parse_args().intent
raw = source.read_bytes()
p = json.loads(raw)
by_ref = {c['reference']: c for c in p['components']}
by_id = {c['id']: c for c in p['components']}
terminals = {}
for net in p['nets']:
    for t in net['terminals']:
        key = (by_id[t['component']]['reference'], t['pin']['number'])
        if key in terminals:
            raise ValueError('Terminal occurs in multiple nets: ' + str(key))
        terminals[key] = net

def net(ref, pin):
    return terminals[(ref, str(pin))]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def same(*pins):
    require(len({net(*p)['id'] for p in pins}) == 1, 'Connectivity mismatch: ' + str(pins))

same(('U6', 1), ('U6', 4), ('R60', 1), ('U30', 1))
same(('R60', 2), ('R181', 1))
bridge = net('R60', 2)
require({(by_id[t['component']]['reference'], str(t['pin']['number']))
         for t in bridge['terminals']} == {('R60','2'), ('R181','1')},
        'Series midpoint must contain only R60.2 and R181.1')
same(('R181', 2), ('R61', 1), ('U18', 1))
same(('R61', 2), ('U18', 2))
require(net('R61',2)['name'] == 'GND', 'Supervisor divider bottom not grounded')
require(len({net('R60',1)['id'], bridge['id'], net('R181',2)['id']}) == 3,
        'Supervisor divider bypassed')
require([by_ref[r]['value'] for r in ['R60','R181','R61']] ==
        ['30.1 kohm 0.1% 25ppm/K', '1.2 kohm 0.1% 25ppm/K', '10 kohm 0.1%'],
        'Supervisor divider selection changed')
same(('U18', 6), ('R64', 2), ('U1', 25))
same(('U30', 10), ('J1', 21), ('R166', 1))
require(net('U30', 1)['id'] != net('U30', 10)['id'], 'Auxiliary input/output collapsed')
for ref, rail, connector_pin in [('U23','POD_WHEEL_FRONT_SUPPLY',23),
                                 ('U24','POD_WHEEL_REAR_SUPPLY',26),
                                 ('U25','POD_TIRE_SUPPLY',31)]:
    require(net(ref,1)['name'] == 'PRE_6V3' and net(ref,10)['name'] == rail, 'Branch source changed')
    same((ref,10),('J1',connector_pin))
channels = []
for start, adc, channel, pin in [(128,'U27',0,11),(132,'U27',1,10),(136,'U27',2,7),
        (140,'U28',0,11),(144,'U28',1,10),(148,'U29',0,11),(152,'U29',1,10),
        (156,'U29',2,7),(166,'U28',2,7),(176,'U28',3,6)]:
    refs = [f'R{i}' for i in range(start, start+4)]
    for upper, lower in zip(refs, refs[1:]):
        same((upper,2),(lower,1))
    same((refs[2],2),(adc,pin))
    require(net(refs[3],2)['name'] == 'GND', 'Divider bottom not grounded')
    require(all(by_ref[r]['value'].startswith('499 kohm') for r in refs[:3]), 'Upper ladder changed')
    require(by_ref[refs[3]]['value'].startswith('4.99 kohm'), 'Bottom ladder changed')
    sensed = net(refs[0],1)
    channels.append({'adc':adc, 'channel':channel, 'pin':pin, 'rail':sensed['name'],
        'divider':refs, 'nominal_ratio':301,
        'connector_pins_at_sensed_node': sorted(int(t['pin']['number']) for t in sensed['terminals']
                            if by_id[t['component']]['reference'] == 'J1')})
report = {'schema':'pod-supply-monitor-coverage/2', 'intent_sha256':hashlib.sha256(raw).hexdigest(),
    'supervisor': {'device':'U18', 'rail':net('R60',1)['name'], 'divider':['R60','R181','R61'],
                  'series_midpoint':bridge['name'],
                  'top_nominal_ohm':31300, 'bottom_nominal_ohm':10000,
                  'signal':net('U18',6)['name'], 'module_pin':25,
                  'coverage':'Local U6 output; upstream of U30 and external wiring'},
    'adc_channels':channels,
    'limits':['Graph inspection only; no native emission or functional monitoring proof.',
              'Connector-node sensing does not observe remote cable or return-path drop.',
              'SENSOR_FAULT_N high does not establish all sensor supplies healthy.',
              'ADC conversion/error/settling bounds and firmware validity policy remain separate.']}
print(json.dumps(report, indent=2))
