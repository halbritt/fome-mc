"""Production capture for the Rev-3 microSD pod (AGENTEE-207/197, Phase A).

Reconstructs one candidate-root capture from tracked repository files and writes the
generated declarations into it:

- ``composition/refs.json``: the 305 native references of the current microSD source;
- ``composition/parts.json`` (``agent-ee.parts/1``) with ``footprints.json``,
  ``assignments.json`` and ``declarations.json`` (the patched D-PCB-1/13 CAD closure);
- ``composition/part-refs.json`` (``agent-ee.part-refs/1``) and
  ``composition/deviations.json`` (``agent-ee.part-deviations/1``);
- ``composition/j3-source.json``: J3 C114218 catalog capture and its exact missing datasheet capture;
- ``composition/envelope.json`` with ``antenna-facts.json`` and ``captured-rule-areas.json``;
- ``composition/library-updates.json`` and ``reconstruction.json``.

Every manifest entry is an existing captured record re-verified against the microSD intent;
nothing is selected, rated or measured here. J3 has no captured datasheet, so it cannot be a
named part (``parts_manifest`` requires one) and stays an explicit gap, never an exclusion.

Usage (from the fome-mc root; agent-ee is an origin/main export, pcbnew on the system python):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --out NEW_DIR
  /usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --check
"""
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
X = ROOT / 'telemetry-pod/expansion'
REL = HERE.relative_to(ROOT).as_posix()
MICROSD = X / 'storage-microsd'
PATCHED = X / 'design-rules/footprints'
CONSTRAINTS = X / 'design-rules/constraints.json'
OLD_PARTS = X / 'complete-parts-manifest/parts.json'
OLD_ASSIGNMENTS = X / 'complete-parts-manifest/assignments.json'
OLD_DECLARATIONS = X / 'cad-assignments/declarations.json'
FOOTPRINT_MANIFEST = X / 'placement-seed-microsd/footprint-manifest.json'
ENVELOPE = X / 'placement-inputs/envelope.json'
J3_CATALOG = MICROSD / 'stock/catalog.json'
SOURCES = HERE / 'sources'
GUIDELINES = SOURCES / 'esp32-guidelines'
FAB = SOURCES / 'fab-profile'
J3_ATTEMPT = SOURCES / 'j3-capture-attempt'
ESP32_DATASHEET = X / ('parts-closure/recovered-pilot/core/datasheets-core/'
                       'bcd526f54b8de686cec4db67219e36ea7ace50cddb0c92f3dfdac49cf99ffd2e.pdf')
GENERATED = ['refs.json', 'parts.json', 'footprints.json', 'assignments.json', 'declarations.json',
             'part-refs.json', 'deviations.json', 'j3-source.json', 'envelope.json', 'antenna-facts.json',
             'captured-rule-areas.json', 'library-updates.json']
D_PCB_1 = ('Thermal vias are 0.30 mm drill / 0.70 mm diameter after design-rules D-PCB-1 '
           '(footprints/ patched copy; KiCad/library original 0.20 mm).')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return json.dumps(value, indent=1, sort_keys=True) + '\n'


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


class Root:
    """The capture root; every copied file is pinned and every write is recorded."""

    def __init__(self, out):
        self.out, self.copied = out, {}

    def copy(self, source, dest):
        source = Path(source)
        target = self.out / dest
        if target.exists():
            if target.read_bytes() != source.read_bytes():
                raise ValueError('conflicting bytes for ' + dest)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        self.copied[dest] = {'source': rel(source), 'sha256': sha(source)}
        return {'path': dest, 'sha256': sha(target)}

    def write(self, dest, value):
        target = self.out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text(value))
        return {'path': dest, 'sha256': sha(target)}


def native_inventory(work):
    """Export the microSD schematic's netlist on a temporary copy; the source is never re-saved."""
    from agent_ee.native_netlist import read_native_inventory
    run = work / 'project'
    run.mkdir(parents=True)
    for name in ('telemetry-pod.kicad_sch', 'telemetry-pod.kicad_pro', 'sym-lib-table', 'fp-lib-table'):
        shutil.copyfile(MICROSD / 'project' / name, run / name)
    (work / 'inputs').symlink_to(MICROSD / 'inputs', target_is_directory=True)
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o',
                    str(work / 'native.xml'), str(run / 'telemetry-pod.kicad_sch')], check=True,
                   capture_output=True)
    return read_native_inventory(work / 'native.xml')


def libraries(root):
    """The microSD library closure with the four D-PCB-1/13 patched footprints swapped in."""
    patched = {p.relative_to(PATCHED).as_posix(): p for p in PATCHED.rglob('*.kicad_mod')}
    updates = []
    for source in sorted((MICROSD / 'inputs').rglob('*')):
        name = source.relative_to(MICROSD / 'inputs').as_posix()
        if not source.is_file() or name in ('intent.json', 'emitter-layout.json'):
            continue
        member = name.removeprefix('footprints/')
        if name.startswith('footprints/') and member in patched:
            blob = root.copy(patched[member], name)
            updates.append({'member': name, 'before': {'path': rel(source), 'sha256': sha(source)},
                            'after': {'path': rel(patched[member]), 'sha256': blob['sha256']}})
            continue
        root.copy(source, name)
    if len(updates) != 4 or len(patched) != 4:
        raise ValueError('expected exactly the four patched footprints')
    return updates


def footprint_manifest(root, updates):
    manifest = json.loads(FOOTPRINT_MANIFEST.read_text())
    after = {u['member']: u['after']['sha256'] for u in updates}
    for library in manifest['libraries']:
        for member in library['members']:
            member['sha256'] = after.get(member['path'], member['sha256'])
            if sha(root.out / member['path']) != member['sha256']:
                raise ValueError('footprint manifest member differs from the capture: ' + member['path'])
    missing = set(after) - {m['path'] for lib in manifest['libraries'] for m in lib['members']}
    if missing:
        raise ValueError('patched footprints absent from the manifest: ' + ', '.join(sorted(missing)))
    return manifest


def declarations():
    """Same pad classification; the thermal-via text records the D-PCB-1 drill change."""
    document = json.loads(OLD_DECLARATIONS.read_text())
    for entry in document['footprints']:
        if entry['footprint'] in ('RF_Module:ESP32-S3-WROOM-1', 'PodPower:DDA0008B', 'PodPower:DDA0008J_C02'):
            entry['rationale'] = (entry['rationale'].replace(' 0.2 mm', '').replace('0.2mm', '')
                                  + ' ' + D_PCB_1)
    return document


def j1_deviation(spec_ref, j1_part):
    return {
        'requirement_id': 'POD-AC-5',
        'original': {'mpn': j1_part['mpn'], 'lcsc': j1_part['lcsc']},
        'assembly': 'hand_soldered',
        'policy': 'owner_hand_fit',
        'reason': ('POD-AC-5 names the AMPSEAL harness header as hand-fitted after delivery; J1 is the '
                   'selected AMPSEAL 1-776163-1 and its captured JLCPCB row reports stock 0 and '
                   'assemblyComponentFlag false.'),
        'purchase_source': ('TE Connectivity 1-776163-1 (LCSC C596198 identity, captured stock 0); '
                            'availability unverified. No purchase made or authorized.'),
        'stock_deviation': {'reason': 'Requirement-named hand-fit part with zero captured stock; '
                                      'generation-day stock evidence is still required for release.'},
        'evidence_refs': [
            {'path': spec_ref, 'locator': 'Acceptance criteria item 5'},
            {'path': j1_part['selection']['part_record'], 'locator': 'mpn/lcsc/manufacturer/stock'},
            {'path': 'telemetry-pod/expansion/part-bindings/connector-stock/catalog.json',
             'locator': 'parts/C596198'},
        ],
    }


def envelope(constraints_blob):
    """The placement envelope revised with the microSD-era decisions; nothing else changes."""
    record = json.loads(ENVELOPE.read_text())
    record['id'] = 'expanded-pod-microsd-production'
    fixed = {f['reference']: f for f in record['fixed_footprints']}
    fixed['J2']['inset_mm'] = 4.76
    record['fixed_footprints'].append({
        'reference': 'J3', 'side': 'back', 'edge': 'left', 'position_mm': 33, 'inset_mm': 8.9,
        'rotation_deg': 90, 'insertion': 'through_edge', 'tolerance_mm': 0,
        'courtyard_overhangs': [{'edge': 'left', 'max_mm': 20.3}]})
    outline = [[0, 0], [90, 0], [90, 65], [0, 65]]
    record['keepouts'] += [
        {'id': 'D-PCB-7v2-In1-no-tracks', 'polygon': outline, 'layers': ['In1.Cu'], 'forbid': ['tracks']},
        {'id': 'D-PCB-6-RF-reference', 'polygon': [[76, 26.5], [88, 26.5], [88, 30.6], [76, 30.6]],
         'layers': ['In1.Cu', 'In2.Cu'], 'forbid': ['tracks', 'vias']}]
    for item in record['obligations']:
        if item['id'] == 'antenna':
            item['statement'] = (
                'ESP32-S3-WROOM-1 antenna overhangs the top edge (D-PCB-16, owner 2026-10-21: outside-board '
                'placement case, Espressif hardware design guidelines Section 1.4.7, page 33). The module-owned '
                'keepout rule area is retained from the captured footprint; datasheet Figure 11-1 module '
                'dimensions define no base-board clearance (AGENTEE-211). Feed-point side, housing clearance '
                'and RF performance remain unqualified.')
    source = {'path': constraints_blob['path'], 'sha256': constraints_blob['sha256']}
    index = {f['reference']: i for i, f in enumerate(record['fixed_footprints'])}

    def fact(quote):
        if quote not in CONSTRAINTS.read_text():
            raise ValueError('decision quote absent from constraints.json: ' + quote)
        return {'quote': quote, 'source': source}
    record['constraint_provenance'] = {
        f"/fixed_footprints/{index['J2']}": {
            'class': 'derived',
            'derivation': 'D-PCB-4: J2 anchor x 85.24 mm on the right edge gives inset 4.76 mm at y 28 mm.',
            'facts': [fact('Decision: move the J2 anchor to x=85.24 so the datum coincides with the edge')]},
        f"/fixed_footprints/{index['J3']}": {
            'class': 'derived',
            'derivation': ('D-PCB-13 v3: J3 anchor (8.9, 32.0) on B.Cu, rotation 90, mouth at the left edge, '
                           'gives inset 8.9 mm and position 33 mm from the left edge start (0, 65); the card '
                           'lane overhangs the left edge by 20.3 mm.'),
            'facts': [fact('J3 is fixed at (8.9, 32.0) on B, rotation 90, mouth at the left board edge'),
                      fact('declared overhang band, left edge, 20.3 mm')]},
        f"/keepouts/{len(record['keepouts']) - 2}": {
            'class': 'derived',
            'derivation': 'D-PCB-7 v2: In1.Cu no-tracks rule area over the board outline (0,0)-(90,65).',
            'facts': [fact('In1.Cu stays a pure GND reference (no-tracks rule area over the outline')]},
        f"/keepouts/{len(record['keepouts']) - 1}": {
            'class': 'derived',
            'derivation': 'D-PCB-6: no tracks and no vias on In1.Cu and In2.Cu in x 76..88 mm, y 26.5..30.6 mm.',
            'facts': [fact('keep tracks and vias off In1.Cu and In2.Cu in x 76..88, y 26.5..30.6 mm')]},
    }
    return record


def build(out, agent_ee):
    sys.path[:0] = [str(Path(agent_ee).resolve() / 'src')]
    from agent_ee import binding_fill, board_envelope
    from agent_ee.footprint_library import (antenna_placement_context, esp32_s3_wroom_1_datasheet_facts,
                                            esp32_s3_wroom_1_placement_policy, probe_rule_areas,
                                            validate_declarations)
    from agent_ee.jlc_stock_capture import validate_capture
    from agent_ee.part_decisions import validate_deviation
    from agent_ee.part_record import qualify_record
    from agent_ee.parts_manifest import qualify_manifest, validate_manifest
    from agent_ee.scaffold_rule_areas import load_retention
    from agent_ee.storage import identity

    out = Path(out).absolute()
    if out.exists():
        raise ValueError('output must not exist')
    out.mkdir(parents=True)
    root = Root(out)
    with tempfile.TemporaryDirectory(prefix='pod-capture-native-') as tmp:
        native = native_inventory(Path(tmp))

    # Library closure and the writer-owned microSD intent, both unchanged except D-PCB-1/13.
    updates = libraries(root)
    intent_blob = root.copy(MICROSD / 'inputs/intent.json', 'composition/intent.json')
    root.copy(MICROSD / 'inputs/emitter-layout.json', 'composition/emitter-layout.json')
    # binding_fill.configuration(output=...) needs a captured projection; it starts as the current
    # bound intent and the binding-fill step replaces it before emission (pod_driver.STEPS order).
    root.copy(MICROSD / 'inputs/intent.json', 'composition/intent.bound.json')
    intent = json.loads((out / intent_blob['path']).read_text())
    physical = {c['reference']: c for c in intent['components'] if not c['reference'].startswith('#')}
    if set(physical) != set(native['components']) or len(physical) != 305:
        raise ValueError('intent and native references differ')
    constraints_blob = root.copy(CONSTRAINTS, rel(CONSTRAINTS))
    spec_blob = root.copy(X / 'requirements/compiled/requirements-map/spec.md', 'composition/spec.md')

    # Existing named records, probes and copper features, re-verified against the microSD intent.
    old = json.loads(OLD_PARTS.read_text())
    parts, kept = [], {}
    for part in old['parts']:
        refs = [i['reference'] for i in part['instances']]
        if not set(refs) <= set(physical):
            if set(refs) & set(physical):
                raise ValueError('partly removed part: ' + part['id'])
            continue
        part = copy.deepcopy(part)
        for instance in part['instances']:
            instance['sheet'] = native['components'][instance['reference']]['sheet']
        (ref,) = refs
        comp = physical[ref]
        if ((part.get('kind') != 'bare_copper_probe' and part['id'] != comp['id']) or
                any(part[k] != comp[k] for k in ('lib_id', 'footprint'))):
            raise ValueError('CAD identity differs from the microSD intent: ' + ref)
        if part.get('kind') == 'copper_feature':
            nets = {pin: next(n['name'] for n in native['nets'].values() if (ref, pin) in n['terminals'])
                    for pin in native['components'][ref]['pins']}
            if part['instances'][0]['nets'] != nets:
                raise ValueError('copper feature nets differ: ' + ref)
        elif 'selection' in part:
            record_path = ROOT / part['selection']['part_record']
            record = json.loads(record_path.read_text())
            binding = comp['part_binding']
            sheet = json.loads(binding['PARAM_Datasheet'])
            if ((record['lcsc'], record['mpn'], record['manufacturer']) !=
                    (binding['LCSC'], binding['Partnumber'], binding['Manufacturer']) or
                    (record['artifact']['sha256'], record['datasheet_url']) != (sheet['sha256'], sheet['url'])):
                raise ValueError('binding differs from the canonical record: ' + ref)
            root.copy(record_path, part['selection']['part_record'])
            for path in qualify_record(record, ROOT):
                root.copy(ROOT / path, path)
            part['selection']['decision_ref'] = {**intent_blob, 'locator': f'components[reference={ref}]'}
        parts.append(part)
        kept[ref] = part['id']
    gaps = sorted(set(physical) - set(kept))
    if gaps != ['J3']:
        raise ValueError('unexpected undeclared references: ' + ', '.join(gaps))
    for part in parts:  # probe/copper symbol and footprint pins must match the capture root
        feature = part.get('probe') or part.get('copper')
        for blob in ([feature['symbol'], feature['footprint']] if feature else []):
            if sha(out / blob['path']) != blob['sha256']:
                raise ValueError('feature CAD differs from the capture: ' + part['id'])

    manifest = footprint_manifest(root, updates)
    manifest_blob = root.write('composition/footprints.json', manifest)
    old_assignments = {c['reference']: c for c in json.loads(OLD_ASSIGNMENTS.read_text())['components']}
    assignments = {'schema': 'agent-ee.footprint-assignments-input/1', 'libraries': intent['libraries'],
                   'components': [old_assignments[p['id']] for p in parts]}
    assignments_blob = root.write('composition/assignments.json', assignments)
    declared = declarations()
    validate_declarations(declared)
    declarations_blob = root.write('composition/declarations.json', declared)
    members = [m for lib in manifest['libraries'] for m in lib['members']] + [
        {k: lib[k] for k in ('path', 'sha256')} for lib in intent['libraries']]
    document = {
        'schema': 'agent-ee.parts/1', 'declaration_source': {**intent_blob, 'locator': 'components'},
        'catalog': None, 'selection': None,
        'cad': {'manifest': manifest_blob, 'assignments': assignments_blob,
                'members_sha256': identity(sorted(members, key=lambda m: m['path'])),
                'declarations': declarations_blob},
        'property_fields': old['property_fields'], 'population': old['population'], 'parts': parts}
    validate_manifest(document)
    parts_blob = root.write('composition/parts.json', document)
    qualification = qualify_manifest(document, out)

    # Part refs: every non-power component except J3, which has no declarable part.
    refs = {'schema': 'agent-ee.part-refs/1',
            'components': {physical[r]['id']: {'part_ref': kept[r]} for r in sorted(kept)}}
    if {p['id'] for p in parts} != {v['part_ref'] for v in refs['components'].values()}:
        raise ValueError('part refs differ from the manifest')
    root.write('composition/part-refs.json', refs)

    # The actual deviations: J1 only (POD-AC-5 hand fit, zero captured stock).
    j1 = next(p for p in parts if p['instances'][0]['reference'] == 'J1')
    deviations = {'schema': 'agent-ee.part-deviations/1',
                  'deviations': [j1_deviation(spec_blob['path'], j1)]}
    for d in deviations['deviations']:
        validate_deviation(d)
        for ref in d['evidence_refs']:
            if ref['path'] not in (spec_blob['path'],):
                root.copy(ROOT / ref['path'], ref['path'])
    root.write('composition/deviations.json', deviations)

    # J3: captured catalog identity; the datasheet stays an exact missing capture.
    catalog_blob = root.copy(J3_CATALOG, rel(J3_CATALOG))
    response = MICROSD / 'stock/responses/C114218.json'
    response_blob = root.copy(response, rel(response))
    catalog = json.loads(J3_CATALOG.read_text())
    validate_capture(catalog, lambda name: (J3_CATALOG.parent / name).read_bytes())
    item = json.loads(response.read_text())['data']['componentPageInfo']['list'][0]
    attempt = json.loads((J3_ATTEMPT / 'manifest.json').read_text())
    j3 = {
        'schema': 'pod-capture.missing-capture/1', 'reference': 'J3', 'component': physical['J3']['id'],
        'identity': {k: catalog['parts']['C114218'][k] for k in ('lcsc', 'mpn', 'mfr', 'package', 'stock')},
        'catalog': {**catalog_blob, 'fetched_at': catalog['requests'][0]['fetched_at'],
                    'response': response_blob},
        'catalog_attributes': {a['attribute_name_en']: a['attribute_value_name'] for a in item['attributes']},
        'assembly_component_flag': item['assemblyComponentFlag'],
        'symbol': physical['J3']['lib_id'], 'footprint': physical['J3']['footprint'],
        'datasheet': {
            'status': 'missing',
            'urls': {'catalog dataManualUrl': item['dataManualUrl'],
                     'intent Datasheet field': physical['J3']['part_binding']['Datasheet'],
                     'KiCad footprint descr (Hirose 2D drawing)':
                         'https://www.hirose.com/product/en/download_file/key_name/DM3AT-SF-PEJM5/category/'
                         'Drawing%20(2D)/doc_file_id/44099/?file_category_id=6&item_id=06090031000&is_series='},
            'attempt': {'path': rel(J3_ATTEMPT / 'manifest.json'), 'sha256': sha(J3_ATTEMPT / 'manifest.json'),
                        'outcome': attempt['outcome'], 'reason': attempt['parts'][0]['reason'],
                        'fetched_at': attempt['parts'][0]['fetched_at']},
            'offline_search': 'No PDF with DM3A text exists in local repositories, caches or /tmp '
                              '(scratch search 2026-10-22); network capture is outside this lane.',
            'facts_needed': [
                'Exact PDF bytes for the agent-ee acquisition producer (agent-ee.datasheet-capture/1) '
                'and a canonical part record (part_record.prepare_record) for C114218.',
                'Pin map: CLK/CMD/DAT0-3/VDD/VSS, card-detect switch (intent pins 9 and 10) and shell; the '
                'catalog row says "Additional Card Detection Pins: No", which conflicts with the wired detect.',
                'Recommended land pattern and the card insertion/ejection stroke (D-PCB-13 lane 15 mm).',
                'Operating temperature (catalog row -25 to +85 C; D-PCB-12 exception basis).',
                'Card-side contact ratings and mating cycles.'],
            'blocks': ['agent-ee.parts/1 named J3 entry', 'binding-fill (part_ref coverage)',
                       'envelope content (J3 fixed footprint)', 'pod_driver dry run past the scaffold']}}
    root.write('composition/j3-source.json', j3)

    # Envelope: microSD decisions, antenna facts (AGENTEE-211) and captured antenna CAD retention.
    for name in ('jlcpcb-capabilities.txt', 'jlcpcb-stackup.txt', 'jlcpcb-thickness.txt'):
        root.copy(FAB / 'sources' / name, 'sources/' + name)
    profile_blob = root.copy(FAB / 'fab-profile.json', 'sources/fab-profile.json')
    revised = envelope(constraints_blob)
    if revised['fab_profile']['sha256'] != profile_blob['sha256']:
        raise ValueError('envelope fab profile differs from the captured profile')
    envelope_blob = root.write('composition/envelope.json', revised)
    files = {p.relative_to(out).as_posix(): sha(p) for p in out.rglob('*') if p.is_file()}
    record = board_envelope.validate((out / envelope_blob['path']).read_bytes(),
                                     profile=(out / profile_blob['path']).read_bytes(), captured=(files, out))
    datasheet = root.copy(ESP32_DATASHEET, rel(ESP32_DATASHEET))
    facts = esp32_s3_wroom_1_datasheet_facts(pdf_path=datasheet['path'], pdf_sha256=datasheet['sha256'])
    root.write('composition/antenna-facts.json', facts)
    pdf = next(GUIDELINES.glob('*.pdf'))
    guideline = root.copy(pdf, rel(pdf))
    root.copy(GUIDELINES / 'manifest.json', rel(GUIDELINES / 'manifest.json'))
    policy = esp32_s3_wroom_1_placement_policy('outside_board', pdf_path=guideline['path'])
    member = next(m for lib in manifest['libraries'] for m in lib['members']
                  if m['path'] == 'footprints/RF_Module.pretty/ESP32-S3-WROOM-1.kicad_mod')
    u1 = next(f for f in record['fixed_footprints'] if f['reference'] == 'U1')
    retention = {
        'schema': 'agent-ee.captured-rule-areas/1', 'purpose': 'retain-captured-cad-only',
        'envelope': envelope_blob, 'parts': parts_blob,
        'items': [{'keepout_id': 'radio-antenna', 'reference': 'U1', 'footprint': 'RF_Module:ESP32-S3-WROOM-1',
                   'pose': {k: u1[k] for k in ('anchor_mm', 'rotation_deg', 'side')}, 'source': member,
                   'rule_areas': probe_rule_areas((out / member['path']).read_bytes(), library='RF_Module',
                                                  path=member['path'], declared=validate_declarations(declared)[0]),
                   'policy': policy,
                   'context': antenna_placement_context(policy, {guideline['path']: (out / guideline['path']).read_bytes()})}]}
    retention_blob = root.write('composition/captured-rule-areas.json', retention)
    retained = load_retention(out, retention_blob['path'], envelope_blob['path'], parts_blob['path'], record, document)

    refs_record = {'schema': 'pod-capture.microsd-refs/1', 'source': {**intent_blob, 'locator': 'components'},
                   'native_schematic': {'path': rel(MICROSD / 'project/telemetry-pod.kicad_sch'),
                                        'sha256': sha(MICROSD / 'project/telemetry-pod.kicad_sch')},
                   'count': len(physical),
                   'references': {r: {'id': c['id'], 'lib_id': c['lib_id'], 'footprint': c['footprint'],
                                      'value': c['value'], 'sheet': native['components'][r]['sheet'],
                                      'declaration': ('gap: no captured datasheet (j3-source.json)' if r == 'J3'
                                                      else next(p.get('kind', 'named') for p in parts
                                                                if p['instances'][0]['reference'] == r))}
                                  for r, c in sorted(physical.items())}}
    root.write('composition/refs.json', refs_record)
    root.write('composition/library-updates.json', {
        'schema': 'pod-capture.library-updates/1',
        'decisions': ['D-PCB-1 (thermal-via drills)', 'D-PCB-13 v2 (J3 card-lane courtyard)'],
        'decision_source': constraints_blob, 'updates': updates})

    # Binding-fill on the writer-owned intent: the genuine producer, its refusal retained verbatim.
    try:
        _, report = binding_fill.fill(out, json.loads((out / 'composition/intent.json').read_text()), document,
                                      refs, deviations, captures='.', source_migration=True)
        fill = {'execution': 'ok', 'components': len(report['components'])}
    except (ValueError, KeyError, TypeError) as exc:
        fill = {'execution': 'refused', 'error': f'{type(exc).__name__}: {exc}'}
    summary = {
        'references': len(physical), 'declared': len(kept), 'gaps': gaps,
        'parts': {'named': sum('selection' in p for p in parts),
                  'bare_copper_probe': sum(p.get('kind') == 'bare_copper_probe' for p in parts),
                  'copper_feature': sum(p.get('kind') == 'copper_feature' for p in parts)},
        'qualify_manifest': {'dependencies': len(qualification['dependencies']),
                             'missing_provenance': qualification['missing_provenance'],
                             'cad': {k: qualification['cad'][k] for k in ('execution', 'outcome', 'coverage')}},
        'envelope': {'structural': record.get('structural'), 'outcome': record.get('outcome'),
                     'fixed': [f['reference'] for f in record['fixed_footprints']],
                     'keepouts': [k['id'] for k in revised['keepouts']],
                     'provenance_status': record['constraint_provenance']['status']},
        'retention': sorted(retained['items']), 'binding_fill': fill}
    root.copied = dict(sorted(root.copied.items()))
    (out / 'reconstruction.json').write_text(text({'copied': root.copied, 'summary': summary}))
    return summary


def check(agent_ee):
    """Rebuild in a fresh directory and compare every generated file with the committed copy."""
    with tempfile.TemporaryDirectory(prefix='pod-capture-check-') as tmp:
        summary = build(Path(tmp) / 'root', agent_ee)
        differ = [n for n in GENERATED + ['../reconstruction.json']
                  if (Path(tmp) / 'root/composition' / n).read_bytes() != (HERE / 'composition' / n).read_bytes()]
    if differ:
        raise SystemExit('differs from the committed capture: ' + ', '.join(differ))
    print(json.dumps(summary, indent=1, sort_keys=True))
    print('production capture reproduces byte for byte')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('agent_ee')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--out', type=Path)
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        check(args.agent_ee)
    else:
        print(json.dumps(build(args.out, args.agent_ee), indent=1, sort_keys=True))
