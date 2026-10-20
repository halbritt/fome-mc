"""Require the revised native design to differ only in the 16 reviewed PDF bindings."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

BASE=Path(__file__).resolve().parent.parent
candidate,report=map(Path,sys.argv[1:])
revision=json.loads((BASE/'source-revision/revision.json').read_text())
old_intent=json.loads((BASE/'series-divider/native-candidate/inputs/intent.json').read_text())
new_intent=json.loads((candidate/'inputs/intent.json').read_text())
assert new_intent==json.loads((BASE/'source-revision/intent.json').read_text())
byref={c['reference']:c for c in old_intent['components']}
refs={r:change for change in revision['changes'] for r in change['references']}
assert len(refs)==16
# The emitter is deterministic: exact reversal must recover the entire prior schematic.
old_sch=(BASE/'text-candidate/project/telemetry-pod.kicad_sch').read_bytes()
new_sch=(candidate/'project/telemetry-pod.kicad_sch').read_bytes()
reverted=new_sch
for change in revision['changes']:
    before,after=change['old_sha256'].encode(),change['new_sha256'].encode()
    assert new_sch.count(after)==len(change['references']) and old_sch.count(before)==len(change['references'])
    assert before not in new_sch and after not in old_sch
    reverted=reverted.replace(after,before)
assert reverted==old_sch,'Schematic changed beyond reviewed hashes'

def normalized(path,undo):
    tree=ET.parse(path).getroot()
    for name in ('source','date'):
        node=tree.find('design/'+name);assert node is not None;tree.find('design').remove(node)
    seen=set()
    for c in tree.findall('./components/comp'):
        ref=c.attrib['ref']
        if ref=='U14':
            node=c.find('tstamps');assert node is not None and node.text
            node.text=' '.join(sorted(node.text.split()))
        if undo and ref in refs:
            seen.add(ref)
            change=refs[ref]; expected=byref[ref]['part_binding']['PARAM_Datasheet']
            fields=c.findall("./fields/field[@name='PARAM_Datasheet']")
            props=c.findall("./property[@name='PARAM_Datasheet']")
            assert len(fields)==len(props)==1
            for raw in (fields[0].text,props[0].attrib['value']):
                value=json.loads(raw);assert value['sha256']==change['new_sha256']
                value['sha256']=change['old_sha256'];assert value==json.loads(expected)
            fields[0].text=expected;props[0].set('value',expected)
    if undo: assert seen==set(refs)
    return ET.tostring(tree)
assert normalized(candidate/'native.xml',True)==normalized(BASE/'text-candidate/native.xml',False)
assert (candidate/'native-bom.csv').read_bytes()==(BASE/'text-candidate/native-bom.csv').read_bytes()
erc=json.loads((candidate/'erc.json').read_text())
assert erc['sheets'] and not any(s['violations'] for s in erc['sheets'])
result={'status':'PASS','revised_references':sorted(refs),'count':len(refs),
    'schematic':'Byte-identical to text-candidate after reversing only the three declared SHA values at 16 instances',
    'native_xml':'Identical after reversing 16 field/property hashes and normalizing source/date and U14 UUID list order',
    'native_bom':'byte-identical','erc_violations':0,
    'schematic_sha256':hashlib.sha256(new_sch).hexdigest(),'native_xml_sha256':hashlib.sha256((candidate/'native.xml').read_bytes()).hexdigest(),
    'scope':'Native source revision correspondence only; not placement, assembly or operating qualification.'}
report.write_text(json.dumps(result,indent=2)+'\n');print('PASS: exactly 16 revised native bindings; all other schematic bytes, graph and BOM preserved; ERC zero')
