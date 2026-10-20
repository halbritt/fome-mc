"""Apply only declared candidate sides and four anchors to an isolated board."""
import argparse
import hashlib
import json
from pathlib import Path
import pcbnew
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if a.out.exists(): p.error('Output must be fresh')
source=P.parent/'probe-import/staged-board.kicad_pcb';raw=source.read_bytes()
board=pcbnew.LoadBoard(str(source));fps={f.GetReference():f for f in board.GetFootprints()}
assign=json.loads((P/'side-assignment.json').read_text())
refs=[r for g in assign['groups'] for r in g['references']];assert len(refs)==len(set(refs))==327
assert set(fps)==set(refs)|set(assign['board_only']['references'])
for group in assign['groups']:
 for ref in group['references']:
  fp=fps[ref];assert fp.GetLayer()==pcbnew.F_Cu
  if group['side']=='B':fp.Flip(fp.GetPosition(),False)
for ref,anchor in json.loads((P/'anchors.json').read_text()).items():
 fp=fps[ref];assert fp.GetLayer()==pcbnew.F_Cu
 fp.SetOrientationDegrees(anchor['rotation_deg']);fp.SetPosition(pcbnew.VECTOR2I(*anchor['position_nm']))
a.out.parent.mkdir(parents=True,exist_ok=True);pcbnew.SaveBoard(str(a.out),board)
assert source.read_bytes()==raw
print(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest()}))
