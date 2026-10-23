import pcbnew,json,pathlib
r=pathlib.Path('/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z')
b=pcbnew.LoadBoard(str(r/'candidate/project/telemetry-pod.kicad_pcb'))
nets=['/SENSOR_POWER_AUX_DVDT','/SENSOR_POWER_FRONT_ILIM','/IMU_CS','/SUP_U18_CT','/TIRE_CAN_OSC2']
out=[]
for fp in b.GetFootprints():
 for p in fp.Pads():
  if p.GetNetname() in nets:
   out.append(dict(ref=fp.GetReference(),pad=p.GetNumber(),net=p.GetNetname(),x=pcbnew.ToMM(p.GetPosition().x),y=pcbnew.ToMM(p.GetPosition().y),size=[pcbnew.ToMM(p.GetSize().x),pcbnew.ToMM(p.GetSize().y)],layers=[b.GetLayerName(l) for l in p.GetLayerSet().Seq() if pcbnew.IsCopperLayer(l)]))
print(json.dumps(out,indent=2));pathlib.Path('/home/halbritt/.cache/route-2-agent507/pads.json').write_text(json.dumps(out,indent=2))
print('locked',sum(t.IsLocked() for t in b.GetTracks()))
