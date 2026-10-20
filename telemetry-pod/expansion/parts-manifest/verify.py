"""Reconstruct immutable selected sources and replay the diagnostic full-native comparison."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from agent_ee.parts_subset import evaluate
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if a.out.exists():p.error('Output must be fresh')
a.out.mkdir(parents=True)
for name,digest in json.loads((P/'provenance.json').read_text())['files'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
for dest,record in json.loads((P/'reconstruction.json').read_text())['copied'].items():
    source=ROOT/record['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==record['sha256'],dest
    target=a.out/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
for name in ['parts.json','assignments.json']:shutil.copyfile(P/name,a.out/name)
report=evaluate(a.out,'parts.json',a.out/'native.xml',['project/telemetry-pod.kicad_sch'])
(a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
assert report==json.loads((P/'report.json').read_text())
print(json.dumps({k:report[k] for k in ['execution','outcome','coverage','findings']}))
