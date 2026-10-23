import pathlib,json,pcbnew,hashlib,math
base=pathlib.Path('/home/halbritt/.cache/route-4-agent507');path=pathlib.Path('/home/halbritt/.cache/route-3-agent507/attempt2/run/candidate/project/telemetry-pod.kicad_pcb');b=pcbnew.LoadBoard(str(path));assert b.BuildConnectivity();conn=b.GetConnectivity();items={x.m_Uuid.AsString():x for x in b.GetTracks()};report=[]
for xy in [(30.8,56.4),(41.8,29.6),(49.4,14.1)]:
 point=pcbnew.VECTOR2I(pcbnew.FromMM(xy[0]),pcbnew.FromMM(xy[1]));tracks=[x for x in b.GetTracks() if not isinstance(x,pcbnew.PCB_VIA) and x.GetNetname()=='/GND' and point in [x.GetStart(),x.GetEnd()]];entries=[]
 for t in tracks:
  pads=[p for p in conn.GetConnectedItems(t,0) if p.GetClass()=='PAD'];entries.append({'uuid':t.m_Uuid.AsString(),'layer':b.GetLayerName(t.GetLayer()),'terminals':[{'uuid':p.m_Uuid.AsString(),'ref':p.GetParentFootprint().GetReference(),'number':p.GetNumber(),'net':p.GetNetname()} for p in pads]})
 near=[]
 for fp in b.GetFootprints():
  for p in fp.Pads():
   d=math.hypot(pcbnew.ToMM(p.GetPosition().x)-xy[0],pcbnew.ToMM(p.GetPosition().y)-xy[1])
   if d<1.1 and p.GetNetname()!='/GND':near.append({'ref':fp.GetReference(),'pad':p.GetNumber(),'net':p.GetNetname(),'distance':d,'position':[pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y)],'size':[pcbnew.ToMM(p.GetSize().x),pcbnew.ToMM(p.GetSize().y)]})
 report.append({'point_mm':xy,'tracks':entries,'foreign_pads_within_1p1mm':near})
# Precise native copper geometry around U18.5, projected pad outlines/bounding boxes.
u=[]
for fp in b.GetFootprints():
 for p in fp.Pads():
  if fp.GetReference()=='U18':
   box=p.GetBoundingBox();u.append({'ref':'U18','pad':p.GetNumber(),'net':p.GetNetname(),'uuid':p.m_Uuid.AsString(),'pos':[pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y)],'box_mm':[pcbnew.ToMM(box.GetLeft()),pcbnew.ToMM(box.GetTop()),pcbnew.ToMM(box.GetRight()),pcbnew.ToMM(box.GetBottom())]})
(base/'inspection.json').write_text(json.dumps({'board_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ground_junctions':report,'U18_pads':u},indent=2))
for r in report:
 print('GND',r['point_mm'],'terminal_groups',[(t['layer'],len(t['terminals']),sorted({p['ref'] for p in t['terminals']})[:8]) for t in r['tracks']],'near',r['foreign_pads_within_1p1mm'],flush=True)
print('U18',json.dumps(u),flush=True)
