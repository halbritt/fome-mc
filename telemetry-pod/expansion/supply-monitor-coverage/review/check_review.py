"""Independent source/native coverage comparison and bounded damaged-input controls."""
import copy, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
intent=root.parent/'series-divider/prepared/intent.json'
xml=root.parent/'series-divider/native-candidate/native.xml'
checker=root/'check_coverage.py'
p=json.loads(intent.read_text()); refs={c['id']:c['reference'] for c in p['components']}
source={(refs[t['component']],str(t['pin']['number'])):n['name'] for n in p['nets'] for t in n['terminals']}
native={(t.attrib['ref'],t.attrib['pin']):n.attrib['name'].removeprefix('/') for n in ET.parse(xml).findall('./nets/net') for t in n.findall('node')}
run=subprocess.run([sys.executable,str(checker),'--intent',str(intent)],capture_output=True,text=True,check=True)
report=json.loads(run.stdout)
assert report==json.loads((root/'report.json').read_text())
assert report['adc_channels']==json.loads((root/'component-fit-report.json').read_text())['adc_channels']
selected={'U6','U18','U30','R60','R181','R61','R64'}
selected.update(r for c in report['adc_channels'] for r in c['divider'])
selected.update(['U27','U28','U29','U23','U24','U25'])
checked={t:n for t,n in source.items() if t[0] in selected or t==('U1','25') or t[0]=='J1'}
for terminal,name in checked.items():
    assert native.get(terminal)==name,(terminal,name,native.get(terminal))
assert source[('U1','25')]=='SENSOR_FAULT_N'
assert ET.parse(xml).find("./libparts/libpart[@part='ESP32-S3-WROOM-1']/pins/pin[@num='25']").attrib['name']=='IO48'

def move(p,ref,pin,target):
    nets=p['nets']; origin=next(n for n in nets if any(refs[t['component']]==ref and str(t['pin']['number'])==str(pin) for t in n['terminals']))
    term=next(t for t in origin['terminals'] if refs[t['component']]==ref and str(t['pin']['number'])==str(pin))
    origin['terminals'].remove(term); next(n for n in nets if n['name']==target)['terminals'].append(term)
probes={}
with tempfile.TemporaryDirectory(prefix='coverage-independent-') as tmp:
    for name,ref,pin,target,expected in [
        ('downstream_tap','R60',1,'POD_5V_AUX','Connectivity mismatch'),
        ('bypassed_midpoint','R181',2,'SUP_U18_TOP_SERIES','Series midpoint must contain'),
        ('misgrounded_bottom','R61',2,'+3V3','Connectivity mismatch')]:
        damaged=copy.deepcopy(p); move(damaged,ref,pin,target)
        path=Path(tmp)/(name+'.json'); path.write_text(json.dumps(damaged))
        result=subprocess.run([sys.executable,str(checker),'--intent',str(path)],capture_output=True,text=True)
        assert result.returncode!=0 and expected in result.stderr,(name,result.stdout,result.stderr)
        probes[name]={'rejected':True,'reason':result.stderr.splitlines()[-1]}
out={'status':'PASS','intent_sha256':hashlib.sha256(intent.read_bytes()).hexdigest(),
     'native_sha256':hashlib.sha256(xml.read_bytes()).hexdigest(),
     'checker_sha256':hashlib.sha256(checker.read_bytes()).hexdigest(),
     'source_native_terminals_compared':len(checked),'adc_channels_unchanged':10,
     'report_exact_replay':True,'module_pin_25':'IO48','negative_controls':probes,
     'scope':'Source/native correspondence and damaged-input rejection only; no electrical qualification.'}
print(json.dumps(out,indent=2))
