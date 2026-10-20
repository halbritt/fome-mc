import hashlib,json
from pathlib import Path
root=Path(__file__).parent
source=root.parent/'candidate-drc.json'
data=json.loads(source.read_text())
rows=[]
for index,v in enumerate(data['violations']):
    if v['type'] not in {'solder_mask_bridge','silk_overlap','silk_over_copper'}: continue
    refs=sorted({i['description'].removeprefix('Reference field of ') for i in v['items'] if i['description'].startswith('Reference field of ')})
    pth=[i['uuid'] for i in v['items'] if i['description'].startswith('PTH pad ')]
    rows.append({'native_index':index,'reference_fields':refs,'pth_pad_uuids':pth,'finding':v})
summary={t:{'total':sum(r['finding']['type']==t for r in rows),'with_reference':sum(r['finding']['type']==t and bool(r['reference_fields']) for r in rows),'with_pth':sum(r['finding']['type']==t and bool(r['pth_pad_uuids']) for r in rows)} for t in sorted({r['finding']['type'] for r in rows})}
result={'source':'../candidate-drc.json','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'classification_basis':'Native item descriptions; involvement is not proof of root cause or future repair.','summary':summary,'unique_reference_fields':sorted({ref for r in rows for ref in r['reference_fields']}),'findings':rows}
(root/'classification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='findings'},indent=2))
