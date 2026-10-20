#!/usr/bin/env python3
"""Independent selection/capture/inventory checker. CLI PART_SELECTION_DIR REPORT."""
import json,hashlib,sys
from pathlib import Path
from collections import Counter
root,out=map(Path,sys.argv[1:]);checks=[];failures=[]
def check(name,value):
 checks.append(name)
 if not value:failures.append(name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((root/'selections.json').read_text());ip=root/s['intent']['path'];d=json.loads(ip.read_text());check('intent pin',sha(ip)==s['intent']['sha256']);cs={c['id']:c for c in d['components']};check('unique component IDs',len(cs)==len(d['components']))
upper={f'diagnostic/R{128+4*i+j}' for i in range(8) for j in range(3)}|{f'aux-power/R{n}' for n in [166,167,168]}|{f'thermistor/R{n}' for n in [176,177,178]}
lower={f'diagnostic/R{131+4*i}' for i in range(8)}|{'aux-power/R169','thermistor/R179'}
expected={'RT0603BRD07499KL':('C515607',499000,upper,'ce504351201504306bc3026d3f08549dcd71f423656734311db63a2b03b7ec6a'),'RT0603BRD074K99L':('C723532',4990,lower,'3296b250247ecff1a1a88353a7f5c89a20508f8abc80e06ac3925c56368663fa')}
check('exact two selections',len(s['parts'])==2 and {p['mpn'] for p in s['parts']}==set(expected));selected={};catalog=json.loads((root/'stock/catalog.json').read_text());evidence=[]
for p in s['parts']:
 if p['mpn'] not in expected:continue
 code,res,ids,pdfhash=expected[p['mpn']];actual=[c['id'] for c in p['components']];check('exact refs '+p['mpn'],len(actual)==len(ids) and set(actual)==ids)
 for k,v in {'manufacturer':'YAGEO','lcsc':code,'resistance_ohm':res,'footprint':'Resistor_SMD:R_0603_1608Metric','tolerance_percent':.1,'tcr_ppm_per_K':25,'operating_temperature_C':[-55,155],'power_W_at_70C':.1,'max_continuous_voltage_V':75,'state':'selected_not_bound'}.items():check(p['mpn']+' '+k,p.get(k)==v)
 check('pinned primary PDF '+code,sha(root/p['datasheet']['path'])==pdfhash==p['datasheet']['sha256'])
 check('manufacturer URL '+code,p['datasheet']['url']=='https://www.yageogroup.com/component-documentation/download/specsheet/'+p['mpn'])
 for item in p['components']:
  cid=item['id'];check('selection unique '+cid,cid not in selected);selected[cid]=p['mpn'];c=cs.get(cid,{});check('reference '+cid,c.get('reference')==item['reference']==cid.split('/')[-1]);check('footprint '+cid,c.get('footprint')==p['footprint']);check('resistor symbol '+cid,c.get('lib_id')=='Device:R');check('value '+cid,c.get('value') in [('499' if res==499000 else '4.99')+' kohm 0.1% 25ppm/'+u for u in ['C','K']]);check('still unbound '+cid,not c.get('part_binding'))
 cr=catalog['parts'][code];check('catalog identity '+code,cr['mpn']==p['mpn'] and cr['lcsc']==code and cr['mfr']=='YAGEO' and cr['package']=='0603')
 req=next(r for r in catalog['requests'] if r['lcsc']==code);rp=root/'stock'/req['response']['path'];check('raw response hash '+code,sha(rp)==req['response']['sha256']);raw=json.loads(rp.read_text());rows=[r for r in raw['data']['componentPageInfo']['list'] if r['componentCode']==code];check('single exact response '+code,len(rows)==1)
 if len(rows)==1:
  r=rows[0];check('raw exact MPN '+code,r['componentModelEn']==p['mpn']);check('stock captured consistently '+code,r['stockCount']==cr['stock']);check('assembly remains false '+code,r['assemblyComponentFlag'] is False);evidence.append({'lcsc':code,'stock_at_capture':cr['stock'],'captured_at':cr['last_seen'],'assemblyComponentFlag':r['assemblyComponentFlag']})
inv=json.loads((root/'inventory.json').read_text());rows={r['id']:r for r in inv['components']};check('complete unique inventory',len(rows)==len(inv['components'])==len(cs) and set(rows)==set(cs));check('inventory source pin',inv['intent_sha256']==sha(ip));states=[]
copper={'can2/JP1','thermistor/JP2','thermistor/JP3','thermistor/JP4','thermistor/JP5'}
for cid,c in cs.items():
 state='power_symbol' if c['lib_id']=='power:PWR_FLAG' else 'copper_feature_policy_pending' if cid in copper else 'selected_not_bound' if cid in selected else 'binding_present_unverified' if c.get('part_binding') else 'unselected';states.append(state);want={k:c[k] for k in ['id','reference','value','lib_id','footprint']};want['state']=state
 if cid in selected:want['selected_mpn']=selected[cid]
 check('inventory exact row '+cid,rows.get(cid)==want)
counts=dict(Counter(states));check('inventory counts',inv['counts']==counts=={'binding_present_unverified':126,'copper_feature_policy_pending':5,'power_symbol':6,'selected_not_bound':40,'unselected':155})
result={'status':'FAIL' if failures else 'PASS','checks':len(checks),'failures':failures,'inventory_counts':counts,'stock_evidence':evidence,'intent_sha256':sha(ip),'selections_sha256':sha(root/'selections.json'),'checker_sha256':sha(Path(__file__)),'limits':'Selection and captured-source custody only.75V ceiling also limited by power/derating; assembly flags false; existing bindings unverified; native/thermal/fault qualification open.'};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));sys.exit(bool(failures))
