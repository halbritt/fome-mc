import pcbnew as k, json
W='/home/halbritt/.cache/agent499-d-pcb-3'
b=k.LoadBoard(W+'/in/telemetry-pod.kicad_pcb')
log={'u14':{}, 'silk':{'hidden_refs':[], 'graphics_to_fab':[]}}
f=b.FindFootprintByReference('U14')
vip=('E7','G5','H10','J5','K8')
for p in f.Pads():
    p.SetSize(k.VECTOR2I(int(0.22e6),int(0.22e6)))
    if p.GetNumber() in vip:
        p.SetAttribute(k.PAD_ATTRIB_PTH); p.SetDrillSize(k.VECTOR2I(int(0.15e6),int(0.15e6)))
        p.SetSize(k.VECTOR2I(int(0.25e6),int(0.25e6))); p.SetProperty(k.PAD_PROP_NONE)
        ls=k.LSET(); ls.AddLayer(k.F_Cu); ls.AddLayer(k.B_Cu); ls.AddLayer(k.In1_Cu); ls.AddLayer(k.In2_Cu); ls.AddLayer(k.F_Mask); ls.AddLayer(k.B_Mask)
        p.SetLayerSet(ls)
log['u14']={'pos':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],'layer':f.GetLayerName(),'pth':[(p.GetNumber(),p.GetNetname(),p.GetPosition().x/1e6,p.GetPosition().y/1e6,p.GetDrillSizeX()/1e6,p.GetSizeX()/1e6) for p in f.Pads() if p.GetAttribute()==k.PAD_ATTRIB_PTH]}
drc=json.load(open(W+'/evidence/drc-in.json'))
refs=set(); gfx=set()
for vio in drc['violations']:
    if not vio['type'].startswith('silk'): continue
    for it in vio['items']:
        d=it['description']
        if d.startswith(('Reference field of ','Value field of ')): refs.add(d.split()[-1])
        elif ' on F.Silkscreen' in d or ' on B.Silkscreen' in d: gfx.add(it['uuid'])
for fp in b.GetFootprints():
    r=fp.GetReference()
    if r in refs: fp.Reference().SetVisible(False); log['silk']['hidden_refs'].append(r)
    for g in fp.GraphicalItems():
        if g.m_Uuid.AsString() in gfx and g.GetLayer() in (k.F_SilkS,k.B_SilkS):
            g.SetLayer(k.F_Fab if g.GetLayer()==k.F_SilkS else k.B_Fab); log['silk']['graphics_to_fab'].append(r)
b.Save(W+'/out/telemetry-pod.kicad_pcb')
json.dump(log,open(W+'/evidence/derive-log.json','w'),indent=1)
print(json.dumps(log['u14']))
