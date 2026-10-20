"""Build the expanded native candidate without modifying earlier source packets."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
out = parser.parse_args().out
if out.exists():
    raise SystemExit('Output must be fresh')
inputs = out / 'inputs'
subprocess.run([sys.executable, str(root.parent / 'thermistor/prepare.py'), '--out', str(inputs)], check=True)
footprint = root / 'sources/C_1206_3216Metric.kicad_mod'
if hashlib.sha256(footprint.read_bytes()).hexdigest() != 'b2e4a08e3aaf40bc587090190c0e3969e962d7ae962c172cce0581ae8327651c':
    raise ValueError('Captured C128 footprint changed')
shutil.copyfile(footprint, inputs / 'footprints/Capacitor_SMD.pretty' / footprint.name)
layout_path = inputs / 'emitter-layout.json'
layout = json.loads(layout_path.read_text())
group, = [g for g in layout['groups'] if g['id'] == 'aux-power']
if group['title'] != 'Protected auxiliary power and ninth diagnostic - qualification pending':
    raise ValueError('Auxiliary title changed; reconcile presentation adaptation')
group['title'] = 'Auxiliary power and diagnostic - qualification pending'
layout_path.write_text(json.dumps(layout, indent=2) + '\n')
# Copper jumpers remain on-board and electrically visible, but are not parts.
intent_path = inputs / 'intent.json'
intent = json.loads(intent_path.read_text())
jumper_ids = {'can2/JP1', *(f'thermistor/JP{i}' for i in range(2, 6))}
found = set()
for component in intent['components']:
    if component['id'] in jumper_ids:
        if component.get('part_binding') or component['lib_id'] != 'CANJumper:SolderJumper_2_Open':
            raise ValueError('Copper jumper identity or binding changed')
        component['in_bom'] = False
        found.add(component['id'])
if found != jumper_ids:
    raise ValueError('Missing copper jumper')
intent_path.write_text(json.dumps(intent, indent=2) + '\n')
project = out / 'project'
subprocess.run([sys.executable, '-m', 'agent_ee.schematic_emitter', str(intent_path),
               '--layout', str(layout_path), '--captures', str(inputs), '--out', str(project),
               '--receipt', str(out / 'emission-receipt.json')], check=True)
# Tables resolve only captured libraries, not a user's global configuration.
symbols = ['(sym_lib_table (version 7)']
for lib in intent['libraries']:
    symbols.append(f'(lib (name "{lib["name"]}") (type "KiCad") (uri "${{KIPRJMOD}}/../inputs/{lib["path"]}") (options "") (descr ""))')
(project / 'sym-lib-table').write_text('\n'.join(symbols) + '\n)\n')
footprints = ['(fp_lib_table (version 7)']
for library in sorted((inputs / 'footprints').glob('*.pretty')):
    footprints.append(f'(lib (name "{library.stem}") (type "KiCad") (uri "${{KIPRJMOD}}/../inputs/footprints/{library.name}") (options "") (descr ""))')
(project / 'fp-lib-table').write_text('\n'.join(footprints) + '\n)\n')
print(out)
