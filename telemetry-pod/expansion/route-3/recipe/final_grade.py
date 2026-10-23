import pathlib,json,sys,hashlib,time
sys.path.insert(0,'/home/halbritt/git/kicad-route/src')
from kicad_route import cli,common
b=pathlib.Path('/home/halbritt/.cache/route-3-agent507');cand=b/'attempt2/run/candidate/project';assert cand.exists();source=pathlib.Path('/home/halbritt/.cache/route-2-agent507/run');origin=pathlib.Path('/tmp/agent-ee-burndown-20261017/workers/pod-capture-j6b2/scratch/route-1/out/runs/project/route-1/20261023T065308.671261Z');records={};before=common.sha256(cand/'telemetry-pod.kicad_pcb')
for label,run,scope in [('route1',source,{'/SENSOR_POWER_AUX_DVDT','/GND'}),('r5',origin,set(common.load_json(origin/'attempt.json')['scope']['nets']))]:
 a=common.load_json(run/'attempt.json');out=b/('native-final-'+label);v,r=cli.validate_candidate(run,a,cand,scope,out);record={'schema':'route-3/native-verification/1','reference_run':str(run),'candidate_dir':str(cand),'scope':sorted(scope),'validation':v,'routing':r,'candidate_sha256':common.sha256(cand/'telemetry-pod.kicad_pcb'),'method':'Existing cli.validate_candidate API with caller-verified exact reference context; native grading only, no ancestry/adoption claim'};common.write_json(b/('grade-'+label+'.json'),record);records[label]=record;print(label,v['status'],v['reasons'],r['status'],flush=True)
assert common.sha256(cand/'telemetry-pod.kicad_pcb')==before,'grading changed candidate bytes; rebind required'
