"""Independent interface-contract oracle and temporary damaged-native controls."""
import copy, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
contract=json.loads((root/'contract.json').read_text())
intent=root.parent/'series-divider/prepared/intent.json'
native=root.parent/'series-divider/native-candidate/native.xml'
checker=root/'check.py'
expected_j1=['POD_CAN_P','POD_CAN_N','POD_12V_IN','GND','POD_5V_SENSOR','POD_FRONT_FORK_SIGNAL','GND','POD_5V_SENSOR','POD_REAR_SHOCK_SIGNAL','GND','POD_5V_SENSOR','POD_FRONT_BRAKE_SIGNAL','GND','POD_5V_SENSOR','POD_REAR_BRAKE_SIGNAL','GND','POD_AUX1_SIGNAL','POD_AUX2_SIGNAL','POD_AUX3_SIGNAL','POD_AUX4_SIGNAL','POD_5V_AUX','GND','POD_WHEEL_FRONT_SUPPLY','POD_WHEEL_FRONT_SIGNAL','GND','POD_WHEEL_REAR_SUPPLY','POD_WHEEL_REAR_SIGNAL','GND','TIRE_CAN_H','TIRE_CAN_L','POD_TIRE_SUPPLY','GND','TIRE_CAN_H','TIRE_CAN_L',None]
assert {r['pin']:r['native_net'] for r in contract['j1']}==dict(enumerate(expected_j1,1))
expected_gpio={1:(39,'WHEEL_FRONT_CAPTURE'),2:(38,'WHEEL_REAR_CAPTURE'),8:(12,'POWER_FAIL_N'),14:(22,'DIAG_I2C_SDA'),21:(23,'DIAG_I2C_SCL'),15:(8,'TIRE_CAN_CS'),16:(9,'TIRE_CAN_INT_N'),38:(31,'EMMC_CLK'),39:(32,'EMMC_CMD'),40:(33,'EMMC_DAT0'),41:(34,'EMMC_DAT1'),42:(35,'EMMC_DAT2'),47:(24,'EMMC_DAT3'),48:(25,'SENSOR_FAULT_N'),35:(28,None)}
assert {r['gpio']:(r['module_pin'],r['native_net']) for r in contract['gpio']}==expected_gpio
assert contract['connector_mpn']=='1-776163-1'
assert contract['module_mpn']=='ESP32-S3-WROOM-1-N8'
result=subprocess.run([sys.executable,str(checker)],capture_output=True,text=True,check=True)
report=json.loads(result.stdout)
if (root/'report.json').exists(): assert report==json.loads((root/'report.json').read_text())
probes={}
with tempfile.TemporaryDirectory(prefix='interface-review-') as td:
    for name in ['swapped_cavities','wrong_gpio_label','native_nc_removed']:
        tree=ET.parse(native)
        if name=='swapped_cavities':
            a=tree.find("./nets/net/node[@ref='J1'][@pin='24']")
            b=tree.find("./nets/net/node[@ref='J1'][@pin='27']")
            a.set('pin','27'); b.set('pin','24')
            reason='Native net mismatch'
        elif name=='wrong_gpio_label':
            node=tree.find("./libparts/libpart[@part='ESP32-S3-WROOM-1']/pins/pin[@num='39']")
            node.set('name','IO2'); reason='GPIO/module-pin mismatch'
        else:
            node=tree.find("./nets/net/node[@ref='U1'][@pin='28']")
            node.set('pintype',node.get('pintype').replace('+no_connect',''))
            reason='Missing native NC'
        path=Path(td)/(name+'.xml'); tree.write(path)
        bad=subprocess.run([sys.executable,str(checker),'--native',str(path)],capture_output=True,text=True)
        assert bad.returncode!=0 and reason in bad.stderr,(name,bad.stdout,bad.stderr)
        probes[name]={'rejected':True,'reason':bad.stderr.splitlines()[-1]}
print(json.dumps({'status':'PASS','connector_cavities':35,'expansion_gpio_allocations':15,'independent_map_matches':True,'report_replay_matches':True,'negative_controls':probes,'sha256':{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in {'contract':root/'contract.json','checker':checker,'intent':intent,'native':native}.items()},'scope':'Partial interface correspondence only; no pilot io-map replacement or operational qualification.'},indent=2))
