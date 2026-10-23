import pathlib,subprocess,hashlib,json,time
from PIL import Image,ImageDraw,ImageFont
b=pathlib.Path('/home/halbritt/.cache/route-2-agent507');out=pathlib.Path('/home/halbritt/.cache/agent-worktrees/fome-mc/route-2-repair/telemetry-pod/expansion/route-2');board=b/'run/candidate/project/telemetry-pod.kicad_pcb';sha=hashlib.sha256(board.read_bytes()).hexdigest();(out/'render').mkdir(exist_ok=True);commands=[]
for side,kicad in [('front','top'),('back','bottom')]:
 dest=out/'render'/f'INCOMPLETE-candidate-{sha[:12]}-{side}.png';raw=b/f'render-{side}.png';cmd=['xvfb-run','-a','kicad-cli','pcb','render','--width','1600','--height','1000','--side',kicad,'--background','opaque','--output',str(raw),str(board)];st=time.monotonic()
 with (out/'logs'/f'render-{side}.log').open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 commands.append({'argv':cmd,'exit_code':p.returncode,'seconds':time.monotonic()-st,'board_sha256':sha});assert p.returncode==0
 im=Image.open(raw).convert('RGB');image=Image.new('RGB',(im.width,im.height+75),'white');image.paste(im,(0,75));draw=ImageDraw.Draw(image);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23);draw.text((20,8),f'ROUTE-2 INCOMPLETE / NOT ACCEPTED | {side} | candidate {sha[:16]}',font=font,fill='black');draw.text((20,40),'Native KiCad render; no release qualification',font=font,fill='black');image.save(dest);print(dest,flush=True)
(out/'logs'/'render-commands.json').write_text(json.dumps(commands,indent=2));assert hashlib.sha256(board.read_bytes()).hexdigest()==sha
