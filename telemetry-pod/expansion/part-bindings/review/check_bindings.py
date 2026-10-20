"""Independent identity/metadata delta check: PACKET_DIR CANDIDATE_DIR REPORT_JSON."""
import copy, hashlib, json, sys
from pathlib import Path
import xml.etree.ElementTree as ET
source_only = '--source-only' in sys.argv[1:]
root, candidate, report = map(Path, [a for a in sys.argv[1:] if a != '--source-only']); expansion=root.parent
checks=0

def check(ok, why):
    global checks
    checks+=1
    if not ok: raise ValueError(why)

def pinned(record):
    raw=(expansion/record['path']).read_bytes()
    check(hashlib.sha256(raw).hexdigest()==record['sha256'],'Evidence hash '+record['path'])
    return raw

manifest=json.loads((root/'manifest.json').read_text())
recovery=json.loads((root/'emmc-source.json').read_text())
check(recovery['sha256']=='e26a6008b1d04ceaa514681aabef2e4130eeabe528a775e6be78162000bce733','reviewed eMMC document hash')
check(recovery['url']=='https://atta.szlcsc.com/upload/public/pdf/source/20221101/092D20F086AADEAD174296532B4AE862.pdf','recovered source URL')
pinned(recovery)
emmcpart=next(p for p in manifest['parts'] if p['mpn']=='FEMDME008G-A8A39')
check(all(emmcpart['datasheet'][k]==recovery[k] for k in ('path','sha256','url')),'recovery/manifest linkage')
historic=json.loads((expansion/'storage-candidate/stock-catalog.json').read_text())
check(len(historic['requests'])==4,'four historic requests')
for req in historic['requests']:
    raw=(expansion/'storage-candidate'/req['response']['path']).read_bytes()
    check(hashlib.sha256(raw).hexdigest()==req['response']['sha256'] and len(raw)==req['response']['size_bytes'],'restored original raw response')
old=json.loads(pinned(manifest['baseline'])); new=json.loads((candidate/'inputs/intent.json').read_text())
check(manifest['baseline']['sha256']=='bbb501d7b45b13c231cd95ba02b8b3e6669d066ea29a7580edb191ddf0af89a2','baseline pin')
expected={
'1-776163-1':('C596198',{'J1'}),
'CRCW2512620RFKEG':('C3988368',{'R110','R111','R119','R120'}),'CRCW2512200RFKEGHP':('C2073505',{'R174','R175'}),
'C0603C105K4RACTU':('C2167386',{'C63','C80'}),'CC1210KKX7R8BB226':('C5341638',{'C68','C69','C70'}),'GRM1885C1H103JA01D':('C85973',{'C47','C88','C91','C94','C126'}),
'C0603C104K5RACTU':('C127833',{'C114', 'C67', 'C97', 'C112', 'C129', 'C115', 'C116', 'C78', 'C85', 'C127', 'C93', 'C87', 'C113', 'C117', 'C83', 'C111', 'C110', 'C79', 'C90', 'C72', 'C84', 'C74', 'C65', 'C125', 'C76'}),
'C0805C105K5RACTU':('C3018567',{'C86', 'C89', 'C92', 'C119', 'C118', 'C122', 'C98', 'C123', 'C120', 'C124', 'C121'}),
'C0603C180J5GACTU':('C2168350',{'C82', 'C81'}),
'C0603C221J5GACTU':('C452747',{'C95', 'C96'}),
'C0603C223K5RACTU':('C2167136',{'C71', 'C73', 'C75', 'C77'}),
'C1206C106K4RACTU':('C2174822',{'C128'}),

'RT0603BRD07100KL':('C122538',{'R116', 'R125', 'R180', 'R29'}),
'RT0603BRD0716K9L':('C861156',{'R56'}),
'RT0603BRD0715K2L':('C861141',{'R58'}),
'RT0603BRD0764K9L':('C861510',{'R62'}),
'RT0603BRD07120RL':('C861094',{'R70'}),
'RT0603BRD0768K1L':('C861521',{'R82', 'R74', 'R78'}),
'RT0603BRD07215KL':('C861226',{'R79', 'R75', 'R83'}),
'RT0603BRD0744K2L':('C861410',{'R76', 'R80', 'R165'}),
'RT0603BRD0726K7L':('C728587',{'R84'}),
'RT0603BRD0756KL':('C705785',{'R123', 'R114'}),
'RT0603BRD074K7L':('C513565',{'R117', 'R126'}),
'RT0603BRD07100RL':('C122970',{'R118', 'R127'}),
'RT0603BRD072K2L':('C861295',{'R160', 'R161'}),
'RT0603BRD0795K3L':('C861605',{'R163'}),
'RT0603BRD07287KL':('C861279',{'R164'}),

'RT0603BRD0710KL':('C95204',{f'R{i}' for i in list(range(46,56))+list(range(64,70))+[71,72,57,59,61,63,112,113,115,121,122,124]+list(range(170,174))}),
'MCP3208-BI/SL':('C2979740',{'U4'}),'TL431BQDBZR':('C190245',{'U31'}),'ADS1119IPWR':('C701613',{'U27','U28','U29'}),
'FEMDME008G-A8A39':('C3249972',{'U14'}),
'MCP2518FDT-E/SL':('C626758',{'U20'}),'TJA1051T/3/1J':('C38695',{'U21'}),
'SN74LVC1G132DBVR':('C403723',{'U22'}),'X1E0003410031':('C725712',{'Y1'}),
'PESD2CANFD24V-TR':('C552486',{'D101','D104'}),'TPS26625DRCR':('C2862873',{'U23','U24','U25','U30'}),
'LM2903BQDRQ1':('C3659057',{'U26'}),'BAV199,215':('C40919',{'D102','D103','D105'}),
'TPS62162QDSGRQ1':('C2071196',{'U15'}),'SRP4020TA-2R2M':('C719179',{'L4'}),
'TPS389001DSER':('C1509297',{'U16','U17','U18','U19'}),
'RT0603BRD07499KL':('C515607',{f'R{i}' for start in list(range(128,160,4))+[166,176] for i in range(start,start+3)}),
'RT0603BRD074K99L':('C723532',{f'R{i}' for i in list(range(131,160,4))+[169,179]})}
check({p['mpn'] for p in manifest['parts']}==set(expected) and len(manifest['parts'])==45,'45 exact identities')
oldmap={c['id']:c for c in old['components']};newmap={c['id']:c for c in new['components']}
check(set(oldmap)==set(newmap) and len(newmap)==332,'component membership')
normal=copy.deepcopy(new);normalmap={c['id']:c for c in normal['components']};seen=set();observations=[]
for part in manifest['parts']:
    lcsc, refs=expected[part['mpn']]
    check(part['lcsc']==lcsc and {c['reference'] for c in part['components']}==refs,'reference allocation '+part['mpn'])
    check(part['qualification']=='identity metadata only; assembly and circuit qualification pending','qualification boundary')
    pinned(part['datasheet']);cat=json.loads(pinned(part['catalog'])); identity=cat['parts'][lcsc]
    check((identity['mpn'],identity['mfr'])==(part['mpn'],part['manufacturer']),'catalog identity')
    reqs=[r for r in cat['requests'] if r['lcsc']==lcsc];check(len(reqs)==1,'capture request uniqueness');req=reqs[0]
    raw=((expansion/part['catalog']['path']).parent/req['response']['path']).read_bytes()
    check(hashlib.sha256(raw).hexdigest()==req['response']['sha256'] and len(raw)==req['response']['size_bytes'],'raw capture hash/size')
    rows=[r for r in json.loads(raw)['data']['componentPageInfo']['list'] if r['componentCode']==lcsc];check(len(rows)==1,'raw exact ID');row=rows[0]
    check((row['componentModelEn'],row['componentBrandEn'],row['stockCount'])==(part['mpn'],part['manufacturer'],identity['stock']),'raw catalog identity/stock')
    check(type(row['assemblyComponentFlag']) is bool,'raw assembly observation')
    if part['mpn']=='1-776163-1':
        check(identity['stock']==0 and row['stockCount']==0,'J1 captured zero stock must remain explicit')
    for component in part['components']:
        cid=component['id'];check(cid not in seen,'duplicate binding');seen.add(cid)
        check(all(oldmap[cid][key]==component[key] for key in ('reference','value','footprint')),'original component '+cid)
        check(not oldmap[cid].get('part_binding'),'previously unbound '+cid)
        if part['mpn']=='RT0603BRD0710KL':
            check(oldmap[cid]['value'] in {'10 kohm','10 kohm 0.1%','10 kohm 0.1% 25ppm/K'} and oldmap[cid]['footprint']=='Resistor_SMD:R_0603_1608Metric','10k selection value/footprint')
        if part['mpn'].startswith('RT0603BRD07'):
            suffix=part['mpn'][11:-1]
            nominal=float(suffix.replace('K','.').replace('R','.'))*(1000 if 'K' in suffix else 1)
            tokens=oldmap[cid]['value'].split(); actual=float(tokens[0])*(1000 if tokens[1]=='kohm' else 1)
            check(nominal==actual and oldmap[cid]['footprint']=='Resistor_SMD:R_0603_1608Metric','resistor nominal/0603 '+cid)
        if part['mpn'] in {'C0603C104K5RACTU','C0805C105K5RACTU','C0603C180J5GACTU','C0603C221J5GACTU','C0603C223K5RACTU','C1206C106K4RACTU'}:
            caprules={'C0603C104K5RACTU':({'100nF','100nF 50V X7R'},'0603_1608'),'C0805C105K5RACTU':({'1uF 50V X7R'},'0805_2012'),'C0603C180J5GACTU':({'18pF C0G'},'0603_1608'),'C0603C221J5GACTU':({'220pF C0G'},'0603_1608'),'C0603C223K5RACTU':({'22nF'},'0603_1608'),'C1206C106K4RACTU':({'10uF 16V X7R'},'1206_3216')}
            values,package=caprules[part['mpn']]
            check(oldmap[cid]['value'] in values and oldmap[cid]['footprint']=='Capacitor_SMD:C_'+package+'Metric','capacitor nominal/dielectric/footprint '+cid)
        if part['mpn'] in {'C0603C105K4RACTU','CC1210KKX7R8BB226','GRM1885C1H103JA01D'}:
            rules={'C0603C105K4RACTU':({'1 uF/16 V','1uF'},'0603_1608'),'CC1210KKX7R8BB226':({'22 uF/25 V'},'1210_3225'),'GRM1885C1H103JA01D':({'10nF','10nF 50V C0G 10%'},'0603_1608')}
            values,package=rules[part['mpn']]
            check(oldmap[cid]['value'] in values and oldmap[cid]['footprint']=='Capacitor_SMD:C_'+package+'Metric','additional capacitor nominal/dielectric/footprint '+cid)
        if part['mpn'] in {'CRCW2512620RFKEG','CRCW2512200RFKEGHP'}:
            value='620 ohm' if part['mpn']=='CRCW2512620RFKEG' else '200 ohm 1% 100ppm/K 1.5W CRCW2512-HP'
            check(oldmap[cid]['value']==value and oldmap[cid]['footprint']=='Resistor_SMD:R_2512_6332Metric','power resistor exact value/family/footprint '+cid)
        if part['mpn']=='1-776163-1':
            check(oldmap[cid]['value']=='1-776163-1' and oldmap[cid]['footprint']=='PodConnector:AMPSEAL_35_1-776163-1','exact gold J1 variant and reviewed footprint')
        binding=newmap[cid]['part_binding']
        expectedbinding={'Manufacturer':part['manufacturer'],'Partnumber':part['mpn'],'LCSC':lcsc,'Datasheet':part['datasheet']['url'],'Qualification':'Identity metadata only; assembly and operating qualification pending'}
        check({k:v for k,v in binding.items() if k!='PARAM_Datasheet'}==expectedbinding,'exact binding fields '+cid)
        check(json.loads(binding['PARAM_Datasheet'])=={'schema':'agent-ee.datasheet-binding/1','sha256':part['datasheet']['sha256'],'url':part['datasheet']['url']},'datasheet binding '+cid)
        del normalmap[cid]['part_binding']
    observations.append({'mpn':part['mpn'],'lcsc':lcsc,'stock_at_capture':identity['stock'],'captured_at':identity['last_seen'],'assemblyComponentFlag':row['assemblyComponentFlag'],'references':[c['reference'] for c in part['components']]})
check(len(seen)==188 and normal==old,'only188 metadata additions; entire prior graph/source preserved')
check(sum(bool(c.get('part_binding')) for c in new['components'])==314,'314 binding fields present, not qualification')
for p in (expansion/'native-candidate/captured/inputs').rglob('*'):
    if p.is_file() and p.name!='intent.json':check((candidate/'inputs'/p.relative_to(expansion/'native-candidate/captured/inputs')).read_bytes()==p.read_bytes(),'capture byte preservation '+str(p))
receipt=json.loads((candidate/'binding-receipt.json').read_text())
check(receipt=={'schema':'pod-part-binding-receipt/1','new_bindings':188,'total_bindings_present':314,'qualification':'Not qualified for assembly or operation','observations':observations},'receipt historical observations and qualification')
check({str(p.relative_to(candidate/'inputs')) for p in (candidate/'inputs').rglob('*') if p.is_file()}=={str(p.relative_to(expansion/'native-candidate/captured/inputs')) for p in (expansion/'native-candidate/captured/inputs').rglob('*') if p.is_file()},'capture file membership')
if source_only:
    result={'status':'SOURCE_ONLY_PASS','checks':checks,'identities':45,'new_bindings':188,'total_bindings_present':314,'observations':observations,'scope':'Prepared metadata-only source delta verified. Native emission and metadata round-trip not verified. Historical catalog facts do not establish assembly/operational qualification.'}
    report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));sys.exit(0)
# XML graph and per-component values/footprints are independent of added metadata.
before=ET.parse(expansion/'native-candidate/native.xml');after=ET.parse(candidate/'native.xml')
def graph(tree):
    return {n.attrib['name']:sorted(tuple(sorted(x.attrib.items())) for x in n.findall('node')) for n in tree.findall('./nets/net')}
check(graph(before)==graph(after),'native complete graph/function/NC preservation')
oldxml={c.attrib['ref']:c for c in before.findall('./components/comp')};newxml={c.attrib['ref']:c for c in after.findall('./components/comp')}
check(set(oldxml)==set(newxml) and len(newxml)==326,'native membership')
for ref,c in newxml.items():
    for key in ('value','footprint'):check(c.findtext(key)==oldxml[ref].findtext(key),'native '+key+' '+ref)
for cid in seen:
    c=newxml[newmap[cid]['reference']];fields={f.attrib['name']:f.text or '' for f in c.findall('./fields/field')}
    for k,v in newmap[cid]['part_binding'].items():check(fields.get(k)==v,'native binding '+cid+' '+k)
result={'status':'PASS','checks':checks,'identities':45,'new_bindings':188,'total_bindings_present':314,'components':332,'native_components':326,'observations':observations,'scope':'Identity metadata only. Historical stock/assembly flags are not current availability or qualification. U14 source provenance restored; qualification remains pending. Existing electrical/thermal/mechanical/fabrication holds remain.'}
report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
