from pathlib import Path
import pcbnew as K,json,hashlib,sys
p=Path(sys.argv[1]);name='SMA_Wurth_60312102114405_Vertical';f=K.FootprintLoad(str(p/'Agentee494b.pretty'),name);assert f
f.SetPosition(K.VECTOR2I(K.FromMM(103),K.FromMM(40)));f.SetOrientationDegrees(0);rows=[]
for q in f.Pads():
 d=q.GetDrillSize();a=q.GetPosition();s=q.GetSize();b=q.GetBoundingBox();rows.append({'number':str(q.GetNumber()),'at':[a.x/1e6,a.y/1e6],'local_at':[(a.x/1e6)-103,(a.y/1e6)-40],'attribute':int(q.GetAttribute()),'drill':[d.x/1e6,d.y/1e6],'anchor_size':[s.x/1e6,s.y/1e6],'bbox':[b.GetLeft()/1e6,b.GetTop()/1e6,b.GetRight()/1e6,b.GetBottom()/1e6],'net_to_bind':'/POD_GNSS_RF' if str(q.GetNumber())=='1' else '/GND'})
assert len(rows)==3 and sum(r['number']=='1' for r in rows)==1 and sum(r['number']=='2' for r in rows)==2 and all(r['drill']==[0,0] for r in rows)
for r in rows:
 a,b,c,d=r['bbox'];r['ideal_proposed_110x80_margin']=min(a,b,110-c,80-d);assert r['ideal_proposed_110x80_margin']>0
# Read saved board only to bind observed endpoint and outline. No SaveBoard.
bp=p/'saved-source.kicad_pcb';before=hashlib.sha256(bp.read_bytes()).hexdigest();board=K.LoadBoard(str(bp));j=next(z for z in board.GetFootprints() if z.GetReference()=='J2');rf=next(z for z in j.Pads() if str(z.GetNumber())=='1');v=rf.GetPosition();old=[v.x/1e6,v.y/1e6];assert old==[86.96,28.0]
# Record existing GNSS DC bias terminal nets; this is not connectivity acceptance of changed geometry.
refs={}
for z in board.GetFootprints():
 if z.GetReference() in ['J2','L3','C42','D3']:
  refs[str(z.GetReference())]=[{'pad':str(q.GetNumber()),'net':str(q.GetNetname())} for q in z.Pads()]
assert before==hashlib.sha256(bp.read_bytes()).hexdigest()
x={'schema':'agentee494b.native/1','tool_status':'PASS','runtime':K.GetBuildVersion(),'footprint_sha256':hashlib.sha256((p/'Agentee494b.pretty'/(name+'.kicad_mod')).read_bytes()).hexdigest(),'candidate_proposed_outline_frame':[103,40,0],'pads':rows,'source_board_sha256':before,'source_unchanged':True,'observed_saved_RF_pad1':old,'existing_bias_pad_nets':refs,'scope':'Three actual SMT pads (oneRF/twoGND), no drills, native custom-pad bboxes, ideal110x80 margins; saved-board oldRFendpoint and padnet observations. No new board saved, no finalplacement/DRC/RF/joint/ingress acceptance.'}
(p/'native494b.json').write_text(json.dumps(x,indent=2)+'\n');print('PASS',json.dumps(x))
