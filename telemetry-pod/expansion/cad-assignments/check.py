"""Replay current physical symbol/footprint assignments, not enclosure or assembly approval."""
import argparse
import hashlib
import json
from pathlib import Path
from agent_ee.native_netlist import read_native_inventory
from agent_ee.native_binding import virtual_symbols, bind_native_assignments

PACKET=Path(__file__).resolve().parent
BASE=PACKET.parent
INPUTS=BASE/'series-divider/native-candidate/inputs'
NATIVE=BASE/'text-candidate'

def build():
    intent=json.loads((INPUTS/'intent.json').read_text())
    graph=read_native_inventory(NATIVE/'native.xml')
    schematic='project/telemetry-pod.kicad_sch'
    virtual=virtual_symbols({schematic:(NATIVE/schematic).read_bytes()},schematic,graph)
    if any('problem' in v or not v.get('embedded_power') for v in virtual):
        raise ValueError('Native exporter omissions not qualified as power symbols')
    physical=graph['components']
    byref={c['reference']:c for c in intent['components']}
    if set(byref)-set(physical) != {ref for v in virtual for ref in v['references']}:
        raise ValueError('Source/native physical and virtual membership disagree')
    manifest=json.loads((BASE/'board-preflight/footprints.json').read_text())
    assignments={'schema':'agent-ee.footprint-assignments-input/1','libraries':intent['libraries'],
        'components':[{'reference':c['id'],'lib_id':c['lib_id'],'footprint':c['footprint'],
            'assembly':'through_hole' if ref=='J1' else 'smd','connector':None}
            for ref,c in sorted(byref.items()) if ref in physical]}
    paths={m['path'] for lib in manifest['libraries'] for m in lib['members']}
    paths.update(lib['path'] for lib in assignments['libraries'])
    captures={p:(INPUTS/p).read_bytes() for p in sorted(paths)}
    declarations=json.loads((PACKET/'declarations.json').read_text())
    mapping={c['id']:ref for ref,c in byref.items() if ref in physical}
    native_assignments={**assignments,'components':[{**c,'reference':mapping[c['reference']]} for c in assignments['components']]}
    report=bind_native_assignments(manifest,captures,native_assignments,graph,virtual,
        hashlib.sha256((NATIVE/'native.xml').read_bytes()).hexdigest(),declarations=declarations)
    return assignments, {'software_scope':'Experimental combined298/300 source pinned in ../board-preflight/import-experiment/software.json',
        'inputs':{p:hashlib.sha256(raw).hexdigest() for p,raw in captures.items()},
        'intent_sha256':hashlib.sha256((INPUTS/'intent.json').read_bytes()).hexdigest(),
        'native_xml_sha256':hashlib.sha256((NATIVE/'native.xml').read_bytes()).hexdigest(),
        'physical_count':len(physical),'virtual_power':virtual,
        'mapping':{c['id']:ref for ref,c in byref.items() if ref in physical},'report':report,
        'limits':['Assignment intent is J1 through-hole; every other circuit footprint SMD.',
            'Shared-number ground vias are explicitly declared; no thermal/process qualification claimed.',
            'Pin/pad, attributes and native membership only; not manufacturer land dimensions, placement or assembly approval.',
            'Five copper jumpers still lack full parts-manifest declaration support.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    if bool(args.out)==bool(args.verify):parser.error('Choose --out or --verify')
    assignments,report=build()
    if args.verify:
        assert assignments==json.loads((PACKET/'assignments.json').read_text())
        assert report==json.loads((PACKET/'report.json').read_text())
    else:
        args.out.mkdir(exist_ok=False)
        for name,doc in [('assignments.json',assignments),('report.json',report)]:
            (args.out/name).write_text(json.dumps(doc,indent=2)+'\n')
    result=report['report']
    print(json.dumps({k:result[k] for k in ['execution','outcome','coverage']}))
    print(json.dumps({'physical':report['physical_count'],'bindings':len(result['bindings']),'findings':result['findings']}))
