import pathlib,shutil,json,sys,pcbnew,time
sys.path.insert(0,'/home/halbritt/git/kicad-route/src')
from kicad_route import cli,common
base=pathlib.Path('/home/halbritt/.cache/route-3-agent507');origin=pathlib.Path('/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z');reference_run=pathlib.Path('/home/halbritt/.cache/route-2-agent507/run');project=base/'attempt1/input/project';shutil.copytree(origin/'candidate',project.parent)
board=project/'telemetry-pod.kicad_pcb';b=pcbnew.LoadBoard(str(board));items={t.m_Uuid.AsString():t for t in b.GetTracks()};via=items['95eb3ed7-dec5-459e-b8a9-54c5721e1fb9'];assert via.GetNetname()=='/GND' and not via.IsLocked();old=via.GetPosition();new=pcbnew.VECTOR2I(pcbnew.FromMM(56.25),pcbnew.FromMM(45.7));records=[]
for uid in ['e5bb9f5b-aedb-4e07-a56a-5dfb1fce52a9','88cf8301-d63a-42a8-a0ac-72b5f187aa99']:
 t=items[uid];assert not t.IsLocked() and t.GetNetname()=='/GND';ends=[]
 for kind,get,setter in [('start',t.GetStart,t.SetStart),('end',t.GetEnd,t.SetEnd)]:
  p=get()
  if p==old:setter(new);ends.append(kind)
 assert len(ends)==1;records.append({'uuid':uid,'endpoints_moved':ends})
via.SetPosition(new);pcbnew.SaveBoard(str(board),b,aSkipSettings=True);common.write_json(base/'attempt1/edit.json',{'target':'/SENSOR_POWER_AUX_DVDT','blocker_net':'/GND','via_uuid':via.m_Uuid.AsString(),'from_mm':[56.3,45.7],'to_mm':[56.25,45.7],'tracks':records,'bbox_mm':[55.9,45.3,56.8,46.2]})
attempt=common.load_json(reference_run/'attempt.json');scope={'/SENSOR_POWER_AUX_DVDT','/GND'}
v,r=cli.validate_candidate(reference_run,attempt,project,scope,base/'attempt1/precheck');common.write_json(base/'attempt1/precheck-result.json',{'validation':v,'routing':r,'reference_run':str(reference_run),'scope':sorted(scope),'purpose':'Native validation of a caller-verified local edit against exact ROUTE-1 reference; does not claim routing-run ancestry or adoption'})
print('precheck',v['status'],v['reasons'],flush=True)
