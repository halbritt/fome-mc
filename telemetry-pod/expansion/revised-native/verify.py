"""Verify retained bytes and replay the narrow native source-revision comparison."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACKET=Path(__file__).resolve().parent
provenance=json.loads((PACKET/'provenance.json').read_text())
for name,digest in provenance['files'].items():
    assert hashlib.sha256((PACKET/name).read_bytes()).hexdigest()==digest,name
with tempfile.TemporaryDirectory(prefix='pod-revised-native-verify-') as directory:
    root=Path(directory);(root/'inputs').mkdir()
    (root/'inputs/intent.json').symlink_to(PACKET.parent/'source-revision/intent.json')
    for name in ['project','native.xml','native-bom.csv','erc.json']:
        (root/name).symlink_to(PACKET/name)
    output=root/'comparison.json'
    subprocess.run([sys.executable,str(PACKET/'compare.py'),str(root),str(output)],check=True)
    assert json.loads(output.read_text())==json.loads((PACKET/'comparison.json').read_text())
print('PASS: all retained artifact hashes and exact native comparison')
