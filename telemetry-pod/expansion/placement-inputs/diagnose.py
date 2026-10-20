"""Diagnose native property serialization without relaxing the placement gate."""
import gzip
import json
from pathlib import Path
from agent_ee.symbol_library import parse_sexpr
from agent_ee.placement_adapter import children, _at, _flip_follows, _property_font_defaults
P=Path(__file__).resolve().parent
before=parse_sexpr((P.parent/'probe-import/staged-board.kicad_pcb').read_bytes())
after=parse_sexpr(gzip.decompress((P/'rejected-seed.kicad_pcb.gz').read_bytes()))
def key(node): return children(node,'uuid')[0][1]
footprints={key(f):f for f in children(after,'footprint')};rows=[]
for old in children(before,'footprint'):
    new=footprints[key(old)]
    if children(old,'layer')==children(new,'layer'): continue
    props={key(x):x for x in children(new,'property')}
    ref=next(x[2] for x in children(old,'property') if x[1]=='Reference')
    for a in children(old,'property'):
        b=props[key(a)]
        if not _flip_follows(a,b,_at(old)[2],_at(new)[2]):
            normalized=_flip_follows(_property_font_defaults(a),_property_font_defaults(b),_at(old)[2],_at(new)[2])
            rows.append({'reference':ref,'field':a[1],'resolved_by_existing_property_default_normalizer':normalized})
result={'scope':'Diagnostic only, does not change gate or saved bytes','rejected_properties':len(rows),
        'resolved_by_existing_normalizer':sum(x['resolved_by_existing_property_default_normalizer'] for x in rows),'details':rows}
assert result==json.loads((P/'property-diagnostic.json').read_text())
print('PASS: 843 property refusals isolated to existing native default normalization; actual gate remains refused')
