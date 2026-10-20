"""Exercise independent checker on temporary copies. CLI PACKET_DIR REPORT."""
import copy,json,subprocess,sys,tempfile,shutil
from pathlib import Path
root,report=map(Path,sys.argv[1:]);results=[]
for probe in ['wrong_supplier_identity','existing_net_damage','promoted_assembly_flag']:
    with tempfile.TemporaryDirectory(prefix='binding-negative-') as td:
        candidate=Path(td)/'candidate';shutil.copytree(root/'prepared',candidate)
        path=candidate/('binding-receipt.json' if probe=='promoted_assembly_flag' else 'inputs/intent.json')
        data=json.loads(path.read_text())
        if probe=='wrong_supplier_identity':
            next(c for c in data['components'] if c['reference']=='U20')['part_binding']['LCSC']='C38695'
        elif probe=='existing_net_damage':
            data['nets'][0]['terminals'].pop()
        else:
            data['observations'][0]['assemblyComponentFlag']=True
        path.write_text(json.dumps(data,indent=2)+'\n')
        result=subprocess.run([sys.executable,str(root/'review/check_bindings.py'),str(root),str(candidate),str(Path(td)/'report.json'),'--source-only'],capture_output=True,text=True)
        if result.returncode==0:raise ValueError('Negative probe accepted: '+probe)
        results.append({'probe':probe,'status':'REJECTED','exit_code':result.returncode,'evidence':result.stderr.splitlines()[-1]})
report.write_text(json.dumps({'scope':'temporary prepared-source copies only','results':results},indent=2)+'\n')
print('PASS: all three negative controls rejected')
