"""Regenerate the pod with the independently reviewed dated source revisions."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

PACKET=Path(__file__).resolve().parent
BASE=PACKET.parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if a.out.exists(): p.error('Output must be fresh')
subprocess.run([sys.executable,str(BASE/'series-divider/prepare.py'),'--source-only','--out',str(a.out)],check=True)
inputs=a.out/'inputs'
assert (inputs/'intent.json').read_bytes()==(BASE/'series-divider/native-candidate/inputs/intent.json').read_bytes()
shutil.copyfile(BASE/'source-revision/intent.json',inputs/'intent.json')
layout=json.loads((inputs/'emitter-layout.json').read_text())
for before,after in {
    'eMMC interface candidate - supplies pending':'eMMC interface - qualification pending',
    'Separate eMMC core supply - supervisor pending':'Separate eMMC core supply - qualification pending',
}.items():
    group,=[g for g in layout['groups'] if g['title']==before];group['title']=after
(inputs/'emitter-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
subprocess.run([sys.executable,'-m','agent_ee.schematic_emitter',str(inputs/'intent.json'),'--layout',str(inputs/'emitter-layout.json'),
    '--captures',str(inputs),'--out',str(a.out/'project'),'--receipt',str(a.out/'emission-receipt.json')],check=True)
for name in ['sym-lib-table','fp-lib-table']:
    shutil.copyfile(BASE/'native-candidate/captured/project'/name,a.out/'project'/name)
