"""Read-only footprint-index preflight, separate from native inventory limits."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from agent_ee.footprint_library import index_footprints

ROOT = Path(__file__).resolve().parent
inputs = ROOT.parent/'series-divider/native-candidate/inputs'
native = ROOT.parent/'series-divider/native-candidate/native.xml'
manifest = json.loads((ROOT/'footprints.json').read_text())
captures = {m['path']:(inputs/m['path']).read_bytes()
            for lib in manifest['libraries'] for m in lib['members']}
index = index_footprints(manifest, captures)
footprints = {f['lib_id']:f for f in index['footprints']}
xml = ET.parse(native)
libraries = {(p.get('lib'),p.get('part')):{pin.get('num') for pin in p.findall('./pins/pin')}
             for p in xml.findall('./libparts/libpart')}
matched, unavailable, mismatches = [], [], []
for component in xml.findall('./components/comp'):
    ref = component.get('ref')
    footprint = footprints.get(component.findtext('footprint'))
    lib = component.find('libsource')
    pins = libraries[lib.get('lib'),lib.get('part')]
    if footprint is None:
        unavailable.append(ref)
    elif pins != set(footprint['electrical_numbers']):
        mismatches.append({'reference':ref,'symbol_pins':sorted(pins),
                           'footprint_pads':sorted(footprint['electrical_numbers'])})
    else:
        matched.append(ref)
print(json.dumps({
    'scope':'Index diagnostic and electrical numbering only; not native forward annotation or geometry qualification',
    'native_xml_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
    'index':index,
    'numbering':{'matched_count':len(matched),'matched_references':matched,
                 'unindexed_references':unavailable,'mismatches':mismatches},
    'limits':['Full footprint coverage is missing while any selected member is unindexed.',
              'No declaration, footprint geometry, design input or parser limit was changed.',
              'Matching numbers do not establish package dimensions, placement or assembly suitability.']
},indent=2))
