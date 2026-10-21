"""Recheck the microSD storage stage without modifying its native project.

Exports a fresh netlist and ERC from a temporary copy and checks the storage
contract: no eMMC-era part remains, J3 is the Hirose DM3AT socket on the four-bit
SDMMC pins the MCU contract reserves, card detect is on GPIO35 (module pin 28) with
R55 as its pull-up, and ERC reports zero violations at every severity.
"""
from collections import Counter
import json, shutil, subprocess, sys
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
EXPECT = {'/SD_CLK': {('J3', '5'), ('U1', '31')}, '/SD_CMD': {('J3', '3'), ('R46', '2'), ('U1', '32')},
          '/SD_DAT0': {('J3', '7'), ('R47', '2'), ('U1', '33')}, '/SD_DAT1': {('J3', '8'), ('R48', '2'), ('U1', '34')},
          '/SD_DAT2': {('J3', '1'), ('R49', '2'), ('U1', '35')}, '/SD_DAT3': {('J3', '2'), ('R50', '2'), ('U1', '24')},
          '/SD_CD': {('J3', '9'), ('R55', '1'), ('U1', '28')}}
GONE = {'U14', 'U15', 'U17', 'L4', 'R51', 'R52', 'R53', 'R54', 'R58', 'R59', 'C63', 'C66', 'C67', 'C68', 'C69', 'C70', 'C73', 'C74', 'R140', 'R141', 'R142', 'R143', 'C113'}
with TemporaryDirectory(prefix='pod-microsd-check-') as directory:
    top = Path(directory); run = top / 'project'; run.mkdir()
    for name in ['telemetry-pod.kicad_sch', 'telemetry-pod.kicad_pro', 'sym-lib-table', 'fp-lib-table']:
        shutil.copyfile(BASE / 'project' / name, run / name)
    (top / 'inputs').symlink_to(BASE / 'inputs', target_is_directory=True)
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(run / 'native.xml'), str(run / 'telemetry-pod.kicad_sch')], check=True, capture_output=True)
    subprocess.run(['kicad-cli', 'sch', 'erc', '--severity-all', '--format', 'json', '-o', str(run / 'erc.json'), str(run / 'telemetry-pod.kicad_sch')], check=True, capture_output=True)
    root = ET.parse(run / 'native.xml').getroot()
    refs = {c.get('ref') for c in root.iter('comp')}
    assert not (refs & GONE), refs & GONE
    assert 'J3' in refs
    j3 = [c for c in root.iter('comp') if c.get('ref') == 'J3'][0]
    assert j3.find('value').text == 'DM3AT-SF-PEJM5' and j3.find('footprint').text == 'Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5', ET.tostring(j3)[:200]
    nets = {n.get('name'): {(x.get('ref'), x.get('pin')) for x in n.findall('node')} for n in root.iter('net')}
    for name, nodes in EXPECT.items():
        assert nets.get(name) == nodes, (name, nets.get(name))
    assert {('J3', '4'), ('C64', '1'), ('C65', '1'), ('R55', '2')} <= nets['/+3V3']
    assert {('J3', '6'), ('J3', '10'), ('J3', 'SH'), ('C64', '2'), ('C65', '2')} <= nets['/GND']
    assert not any(n.startswith('/EMMC') for n in nets), [n for n in nets if n.startswith('/EMMC')]
    report = json.loads((run / 'erc.json').read_text())
    actual = Counter((v['type'], v['severity']) for sheet in report['sheets'] for v in sheet['violations'])
    assert not actual, actual
    print('microSD storage contract holds; ERC zero violations; %d components, %d nets' % (len(refs), len(nets)))
