"""Crop per-reference fit views from a top render (read-only). The board area in the PNG is the bounding box of
PCB-coloured (green soldermask) pixels; it is mapped linearly onto the Edge.Cuts outline bounds (mm), so a board
position maps to a pixel. Usage: crop.py PNG INVENTORY_JSON OUTDIR SIZE_MM REF[,REF...] [PREFIX]
"""
import json, sys
from pathlib import Path
from PIL import Image
png, invp, outd, size, refs = sys.argv[1:6]
prefix = sys.argv[6] if len(sys.argv) > 6 else ''
im = Image.open(png).convert('RGB'); W, H = im.size
px = im.load()
xs, ys = [], []
for y in range(0, H, 4):
    for x in range(0, W, 4):
        r, g, b = px[x, y]
        if g > r + 15 and g > b + 5 and g < 160:
            xs.append(x); ys.append(y)
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
inv = json.load(open(invp))
OX, OY, OW, OH = 0.0, 0.0, 90.0, 65.0   # Edge.Cuts outline (mm), envelope outline (0,0)-(90,65)
sx, sy = (x1 - x0) / OW, (y1 - y0) / OH
pos = {r['ref']: r for r in inv['rows']}
Path(outd).mkdir(parents=True, exist_ok=True)
half = float(size) / 2
for ref in refs.split(','):
    p = pos[ref]['position_mm']
    cx, cy = x0 + (p[0] - OX) * sx, y0 + (p[1] - OY) * sy
    box = (int(cx - half * sx), int(cy - half * sy), int(cx + half * sx), int(cy + half * sy))
    im.crop(box).resize((600, 600)).save(Path(outd) / f'{prefix}{ref}.png')
print(json.dumps({'board_px': [x0, y0, x1, y1], 'px_per_mm': [round(sx, 2), round(sy, 2)]}))
