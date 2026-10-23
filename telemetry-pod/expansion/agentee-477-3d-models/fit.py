"""AGENTEE-477 pad-fit evidence (read-only): each modelless reference's footprint (from the board, footprint-local)
against candidate KiCad stock footprints whose stock 3D model would be reused unchanged. Per pad number: centroid
of that number's pads (local nm) and the largest pad size; report the max centroid deviation, max size deviation,
and number sets. A stock model is authored for its stock footprint's origin/orientation, so a pad match at
deviation ~0 means the stock model fits with the stock model offset/rotation. Usage: fit.py BOARD OUT_JSON
"""
import json, sys
from collections import defaultdict
import pcbnew
LIB = '/usr/share/kicad/footprints'
CANDS = {
    'DDA0008B': [('Package_SO', 'TI_SO-PowerPAD-8'), ('Package_SO', 'HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm'), ('Package_SO', 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.81mm')],
    'DDA0008J_C02': [('Package_SO', 'TI_SO-PowerPAD-8'), ('Package_SO', 'HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm'), ('Package_SO', 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.81mm')],
    'DSE0006A': [('Package_SON', 'WSON-6_1.5x1.5mm_P0.5mm')],
    'SOD882BD': [('Diode_SMD', 'D_SOD-882D'), ('Diode_SMD', 'D_SOD-882')],
    'DMP6023LE_SOT223': [('Package_TO_SOT_SMD', 'SOT-223-3_TabPin2'), ('Package_TO_SOT_SMD', 'SOT-223')],
}
def facts(fp):
    by = defaultdict(list)
    for p in fp.Pads():
        rel = p.GetFPRelativePosition()
        by[p.GetNumber()].append(((rel.x, rel.y), (p.GetSizeX(), p.GetSizeY())))
    out = {}
    for n, ps in by.items():
        cx = sum(a[0][0] for a in ps) / len(ps); cy = sum(a[0][1] for a in ps) / len(ps)
        big = max(ps, key=lambda a: a[1][0] * a[1][1])[1]
        out[n] = {'centroid_nm': [round(cx), round(cy)], 'pads': len(ps), 'largest_size_nm': list(big)}
    return out
b = pcbnew.LoadBoard(sys.argv[1])
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
doc = {}
for ref in ['U5', 'U7', 'U6', 'U12', 'U16', 'U18', 'U19', 'D3', 'Q1']:
    fp = fps[ref]
    key = fp.GetFPIDAsString().split(':', 1)[1]
    mine = facts(fp)
    res = []
    for lib, name in CANDS[key]:
        stock = pcbnew.FootprintLoad(f'{LIB}/{lib}.pretty', name)
        theirs = facts(stock)
        common = sorted(set(mine) & set(theirs))
        dev = max((max(abs(mine[n]['centroid_nm'][i] - theirs[n]['centroid_nm'][i]) for i in (0, 1)) for n in common), default=None)
        sdev = max((max(abs(mine[n]['largest_size_nm'][i] - theirs[n]['largest_size_nm'][i]) for i in (0, 1)) for n in common), default=None)
        models = [{'filename': m.m_Filename, 'offset_mm': [m.m_Offset.x, m.m_Offset.y, m.m_Offset.z],
                   'rotation_deg': [m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z], 'scale': [m.m_Scale.x, m.m_Scale.y, m.m_Scale.z]} for m in stock.Models()]
        res.append({'stock': f'{lib}:{name}', 'numbers_mine': sorted(mine), 'numbers_stock': sorted(theirs),
                    'max_centroid_dev_mm': None if dev is None else round(dev / 1e6, 4), 'max_size_dev_mm': None if sdev is None else round(sdev / 1e6, 4),
                    'stock_models': models, 'stock_pads': {n: theirs[n] for n in sorted(theirs)}})
    doc[ref] = {'fpid': fp.GetFPIDAsString(), 'value': fp.GetValue(), 'side': 'B' if fp.IsFlipped() else 'F',
                'pads': {n: mine[n] for n in sorted(mine)}, 'candidates': res}
open(sys.argv[2], 'w').write(json.dumps(doc, indent=1, sort_keys=True) + '\n')
for ref, d in doc.items():
    print(ref, d['fpid'], [(c['stock'].split(':')[1][:28], c['max_centroid_dev_mm'], c['max_size_dev_mm'], c['numbers_mine'] == c['numbers_stock']) for c in d['candidates']])
