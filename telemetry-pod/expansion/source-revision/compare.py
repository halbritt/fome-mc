"""Compare retained PDF revisions at 144 dpi, allowing only the exact dated footer."""
import argparse
import hashlib
import json
from pathlib import Path
import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).resolve().parent
PAIRS = ROOT/'telemetry-pod/expansion/canonical-parts/changed-pdf-text-comparison.json'

def build():
    results=[]
    for pair in json.loads(PAIRS.read_text()):
        paths=[ROOT/pair[k] for k in ('old','new')]
        docs=[fitz.open(p) for p in paths]
        assert len(docs[0])==len(docs[1])
        pages=[]
        for index,(old,new) in enumerate(zip(*docs)):
            assert old.rect==new.rect
            dates=['Generated 10/19/2026','Generated 10/20/2026']
            text=[p.get_text() for p in (old,new)]
            assert all(t.count(d)==1 for t,d in zip(text,dates))
            assert text[0].replace(dates[0],'Generated DATE')==text[1].replace(dates[1],'Generated DATE')
            rects=[p.search_for(d) for p,d in zip((old,new),dates)]
            assert all(len(r)==1 for r in rects)
            region=rects[0][0] | rects[1][0]
            region=fitz.Rect(region.x0-1,region.y0-1,region.x1+1,region.y1+1)
            pix=[p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False) for p in (old,new)]
            assert (pix[0].width,pix[0].height,pix[0].n)==(pix[1].width,pix[1].height,pix[1].n)
            arrays=[np.frombuffer(p.samples,dtype=np.uint8).reshape(p.height,p.width,p.n) for p in pix]
            changed=np.any(arrays[0]!=arrays[1],axis=2)
            ys,xs=np.where(changed)
            assert len(xs)>0
            assert xs.min()>=int(region.x0*2) and xs.max()<int(np.ceil(region.x1*2))
            assert ys.min()>=int(region.y0*2) and ys.max()<int(np.ceil(region.y1*2))
            pages.append({'page':index+1,'page_size_points':list(old.rect),'date_region_points':list(region),
                'changed_pixels':len(xs),'changed_bbox_pixels':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
                'pixels_outside_date_identical':True,'text_except_date_identical':True,
                'render_sha256':[hashlib.sha256(p.samples).hexdigest() for p in pix]})
        results.append({'id':pair['id'],'old_path':pair['old'],'new_path':pair['new'],
            'old_sha256':hashlib.sha256(paths[0].read_bytes()).hexdigest(),
            'new_sha256':hashlib.sha256(paths[1].read_bytes()).hexdigest(),'pages':pages})
    return {'renderer':fitz.VersionBind,'dpi':144,'pairs':results,
        'scope':'All-page text and raster comparison at stated resolution, not binary PDF equivalence or operating qualification.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--verify',action='store_true');a=p.parse_args()
    result=build()
    if a.verify:
        assert result==json.loads((PACKET/'comparison.json').read_text())
    else:
        (PACKET/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'documents':len(result['pairs']),'pages':sum(len(p['pages']) for p in result['pairs']),'outside_date_identical':True}))
