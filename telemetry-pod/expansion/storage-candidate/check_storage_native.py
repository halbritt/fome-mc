"""Check native export against independently transcribed device/host contracts.
Usage: python3 check_storage_native.py NETLIST.xml REPORT.json
This is a wiring check, not storage/power/assembly qualification.
"""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
source, output = map(Path, sys.argv[1:])
tree = ET.parse(source).getroot()
pins = {}
for n in tree.findall('./nets/net'):
    for p in n.findall('node'):
        key=(p.attrib['ref'],p.attrib['pin'])
        assert key not in pins, key
        pins[key]=n.attrib['name'].removeprefix('/')
failures=[];checks=0
def expect(ref,pin,name):
    global checks
    checks+=1
    actual=pins.get((ref,str(pin)))
    if actual!=name: failures.append({'terminal':[ref,str(pin)],'expected':name,'actual':actual})
# FORESEE A-00093 v1.0 Fig1/Table2 vs committed GPIO allocation.
for label,ball,host in [('CLK','M6','31'),('CMD','M5','32'),('DAT0','A3','33'),('DAT1','A4','34'),('DAT2','A5','35'),('DAT3','B2','24')]:
    expect('U14',ball,'EMMC_'+label);expect('U1',host,'EMMC_'+label)
for label,balls in [('VCC_3V3','E6 F5 J10 K9'),('VCCQ_3V3','C6 M4 N4 P3 P5')]:
    for ball in balls.split(): expect('U14',ball,'EMMC_'+label)
for ball in 'A6 E7 G5 H10 J5 K8 C4 N2 N5 P4 P6'.split(): expect('U14',ball,'GND')
expect('U14','C2','EMMC_VDDi');expect('U14','H5','EMMC_DS')
for i,ball in enumerate('B3 B4 B5 B6'.split(),4): expect('U14',ball,'EMMC_DAT'+str(i))
for ref,label in zip(range(46,55),['CMD']+['DAT'+str(i) for i in range(8)]):
    expect('R'+str(ref),1,'EMMC_VCCQ_3V3');expect('R'+str(ref),2,'EMMC_'+label)
for ref,rail in [(63,'VDDi'),(64,'VCC_3V3'),(65,'VCC_3V3'),(66,'VCCQ_3V3'),(67,'VCCQ_3V3')]:
    expect('C'+str(ref),1,'EMMC_'+rail);expect('C'+str(ref),2,'GND')
expect('R55',1,'EMMC_DS');expect('R55',2,'GND')
# Native netlist contains NC-marked balls as isolated singleton nets.
for ball in 'A7 E5 G3 K6 K7 E8 E9 E10 F10 G10 K10 P10 K5'.split():
    checks+=1
    name=pins.get(('U14',ball))
    members=[key for key,value in pins.items() if value==name]
    if name is None or not name.startswith('unconnected-') or members!=[('U14',ball)]:
        failures.append({'isolated_ball':ball,'net':name,'members':members})
report={'status':'FAIL' if failures else 'PASS','checks':checks,'failures':failures,
'netlist_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
'scope':'Storage terminal connectivity only; supplies intentionally undriven. No power, SI, thermal, endurance, assembly or release qualification.'}
output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(bool(failures))
