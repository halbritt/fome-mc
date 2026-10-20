"""Build a source-bound diagnostic parts manifest, explicitly omitting unclosed J1."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from agent_ee.part_record import qualify_record
from agent_ee.native_netlist import read_native_inventory
from agent_ee.probe_features import parse_marker, PROPERTY
from agent_ee.storage import identity

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'telemetry-pod/expansion'
P=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def build(out):
    if out.exists():raise ValueError('Output must be fresh')
    out.mkdir(parents=True)
    copies={}
    def copy(source,dest):
        source=Path(source);target=out/dest
        if target.exists():assert target.read_bytes()==source.read_bytes()
        else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        copies[dest]={'source':source.relative_to(ROOT).as_posix(),'sha256':digest(source)}
        return {'path':dest,'sha256':digest(target)}
    def write(name,obj):
        (out/name).write_text(json.dumps(obj,indent=2)+'\n');return {'path':name,'sha256':digest(out/name)}
    original=BASE/'series-divider/native-candidate/inputs'
    intent=json.loads((BASE/'source-revision/intent.json').read_text())
    intent_blob=copy(BASE/'source-revision/intent.json','intent.json')
    copy(BASE/'revised-native/native.xml','native.xml')
    copy(BASE/'revised-native/project/telemetry-pod.kicad_sch','project/telemetry-pod.kicad_sch')
    graph=read_native_inventory(out/'native.xml')
    byref={c['reference']:c for c in intent['components']}
    records={}
    index=json.loads((BASE/'canonical-parts/records/index.json').read_text())
    for row in index['records']:
        path=BASE/'canonical-parts/records'/row['file']
        for ref in row['references']:records[ref]=path
    revision=json.loads((BASE/'source-revision/revision.json').read_text())
    for row in revision['changes']:
        for ref in row['references']:records[ref]=BASE/'source-revision'/row['record']
    assert len(records)==315
    record_data={}
    for path in sorted(set(records.values())):
        record=json.loads(path.read_text());record_data[path]=record
        copy(path,path.relative_to(ROOT).as_posix())
        for rel,sha in qualify_record(record,ROOT).items():
            assert digest(ROOT/rel)==sha;copy(ROOT/rel,rel)
    manifest=json.loads((BASE/'board-preflight/footprints.json').read_text())
    manifest_blob=copy(BASE/'board-preflight/footprints.json','footprints.json')
    member_blobs=[];members={}
    for lib in manifest['libraries']:
        for m in lib['members']:
            copy(original/m['path'],m['path']);member_blobs.append(m)
            members[lib['name']+':'+Path(m['path']).stem]=m
    for lib in intent['libraries']:
        copy(original/lib['path'],lib['path']);member_blobs.append({k:lib[k] for k in ['path','sha256']})
    declarations=copy(BASE/'cad-assignments/declarations.json','declarations.json')
    parts=[];assignments=[]
    libraries={lib['name']:{k:lib[k] for k in ['path','sha256']} for lib in intent['libraries']}
    for ref,comp in sorted(graph['components'].items()):
        if ref=='J1':continue
        c=byref[ref];part_id=c['id'];instance={'sheet':comp['sheet'],'reference':ref}
        part={'id':part_id,'role':'Expanded pod '+ref+' '+c['value'],'required':True,
            'instances':[instance],'lib_id':c['lib_id'],'footprint':c['footprint']}
        if ref in records:
            path=records[ref];r=record_data[path];param=json.loads(c['part_binding']['PARAM_Datasheet'])
            assert r['artifact']['sha256']==param['sha256'] and r['datasheet_url']==param['url']
            assert (r['lcsc'],r['mpn'],r['manufacturer'])==(c['part_binding']['LCSC'],c['part_binding']['Partnumber'],c['part_binding']['Manufacturer'])
            part.update(selection_id=part_id,**{k:r[k] for k in ['lcsc','mpn','manufacturer','package','stock']},
                datasheet={'status':'captured','required':True,'artifact':r['artifact'],
                    'provenance':{**r['datasheets'],'locator':'parts[id='+r['datasheet_id']+']'}},
                selection={'kind':'named','lcsc':r['lcsc'],'part_record':path.relative_to(ROOT).as_posix(),
                    'part_record_sha256':digest(path),'decision_ref':{**intent_blob,'locator':'components[reference='+ref+']'}})
        elif PROPERTY in comp['properties']:
            r=parse_marker(comp['properties'][PROPERTY]);part_id=r['part_id']
            part.update(kind='bare_copper_probe',id=part_id,instances=[{**instance,'net':r['net'],'native_net':r['native_net']}],
                probe={'symbol':r['symbol'],'footprint':r['footprint_source'],'pin':r['pin']})
        elif ref in {'JP1','JP2','JP3','JP4','JP5'}:
            nets={pin:next(n['name'] for n in graph['nets'].values() if (ref,pin) in n['terminals']) for pin in comp['pins']}
            part.update(kind='copper_feature',instances=[{**instance,'nets':nets}],copper={
                'symbol':libraries[c['lib_id'].split(':')[0]],'footprint':members[c['footprint']],
                'pins':[{'number':number,**meta} for number,meta in sorted(comp['pin_metadata'].items())],
                'native_flags':{'in_bom':False,'dnp':False,'exclude_from_board':False}})
        else:raise ValueError('Unexpected unclassified native component '+ref)
        parts.append(part)
        assignments.append({'reference':part_id,'lib_id':c['lib_id'],'footprint':c['footprint'],'assembly':'smd','connector':None})
    assert len(parts)==326
    assignment_blob=write('assignments.json',{'schema':'agent-ee.footprint-assignments-input/1','libraries':intent['libraries'],'components':assignments})
    doc={'schema':'agent-ee.parts/1','declaration_source':{**intent_blob,'locator':'components'},'catalog':None,'selection':None,
        'cad':{'manifest':manifest_blob,'assignments':assignment_blob,'members_sha256':identity(sorted(member_blobs,key=lambda m:m['path'])),'declarations':declarations},
        'property_fields':{'lcsc':'LCSC','mpn':'Partnumber','manufacturer':'Manufacturer'},'population':'native-dnp-optional-only/1','parts':parts}
    write('parts.json',doc)
    write('reconstruction.json',{'copied':dict(sorted(copies.items())),'omitted':['J1'],'scope':'Diagnostic 326-of-327 manifest; missing J1 must remain a failure, not an exclusion.'})
    print('Built315 purchased +6probes +5copper declarations; J1 intentionally omitted pending canonical import')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.out)
