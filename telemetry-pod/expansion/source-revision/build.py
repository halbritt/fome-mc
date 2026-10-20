"""Build reviewed PDF revision records and an explicit candidate intent revision."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from agent_ee.part_record import prepare_record, qualify_record

ROOT=Path(__file__).resolve().parents[3]
PACKET=Path(__file__).resolve().parent
INTENT=ROOT/'telemetry-pod/expansion/series-divider/native-candidate/inputs/intent.json'

def blob(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def build():
    comparison=json.loads((PACKET/'comparison.json').read_text())
    inventory=json.loads((PACKET.parent/'parts-closure/inventory.json').read_text())
    acquisition=PACKET.parent/'canonical-parts/acquisition/manifest.json'
    acquired=json.loads(acquisition.read_text())
    original=json.loads(INTENT.read_text()); intent=copy.deepcopy(original)
    changes=[]; files={}
    for pair in comparison['pairs']:
        lcsc=pair['id'].split('-')[0]
        part=next(p for p in inventory['parts'] if p['lcsc']==lcsc)
        sheet=part['datasheets'][pair['old_sha256']]
        catalog=max(part['matching_catalogs'],key=lambda c:(c['fetched_at'],c['catalog']))
        capture=next(p for p in acquired['parts'] if p['id']==pair['id'])
        assert capture['sha256']==pair['new_sha256'] and capture['url']==sheet['url']
        record=prepare_record(ROOT,lcsc,blob(ROOT/catalog['catalog']),blob(acquisition),capture['id'])
        assert (record['mpn'],record['manufacturer'],record['artifact']['sha256'],record['datasheet_url'])==(part['mpn'],part['manufacturer'],pair['new_sha256'],sheet['url'])
        dependencies=qualify_record(record,ROOT)
        refs=[]
        for c in intent['components']:
            binding=c.get('part_binding',{})
            if binding.get('LCSC')!=lcsc: continue
            old=json.loads(binding['PARAM_Datasheet'])
            assert old['sha256']==pair['old_sha256'] and old['url']==sheet['url']
            assert binding['Partnumber']==part['mpn'] and binding['Manufacturer']==part['manufacturer']
            new={**old,'sha256':pair['new_sha256']}
            binding['PARAM_Datasheet']=json.dumps(new,separators=(',',':'))
            refs.append(c['reference'])
        assert set(refs)==set(sheet['references'])
        name=lcsc+'.json'; files[name]=record
        changes.append({'lcsc':lcsc,'references':sorted(refs),'old_sha256':pair['old_sha256'],'new_sha256':pair['new_sha256'],
            'url':sheet['url'],'record':name,'dependencies':dependencies})
    changed_refs={r for c in changes for r in c['references']}
    assert len(changed_refs)==16
    reverted=copy.deepcopy(intent)
    for before,after in zip(original['components'],reverted['components']):
        if after['reference'] in changed_refs: after['part_binding']['PARAM_Datasheet']=before['part_binding']['PARAM_Datasheet']
    assert reverted==original
    files['intent.json']=intent
    files['revision.json']={'schema':'pod-source-revision/1','base_intent':blob(INTENT),'changes':changes,
        'changed_field':'part_binding.PARAM_Datasheet.sha256','references':16,
        'status':'Reviewed source revision for next native candidate; existing native artifacts retain their old source bindings.',
        'limits':['Records qualify exact identity/captured source only, not operating suitability or stock freshness.',
            'No existing source packet or native schematic is replaced. Regenerate and verify native binding correspondence before use.']}
    return files

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--verify',action='store_true');a=p.parse_args()
    for name,doc in build().items():
        path=PACKET/name
        if a.verify: assert doc==json.loads(path.read_text()),name
        else: path.write_text(json.dumps(doc,indent=2)+'\n')
    print('PASS: three canonical records, 16 explicit source-binding revisions; all other intent data unchanged')
