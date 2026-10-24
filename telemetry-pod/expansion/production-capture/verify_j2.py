"""Read-only native verification of the producer-adopted Amphenol 132134 J2.

Run in the qualified KiCad container against the diagnostic emission directory.
This verifies the selected part and geometry; it does not accept placement or routing.
"""
import argparse
import hashlib
import json
import re
import uuid
from collections import Counter
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pattern(fp):
    anchor = fp.GetPosition()
    if fp.GetOrientationDegrees() != 0 or fp.IsFlipped():
        raise ValueError('J2 writer pose must be front, rotation 0')
    return sorted((p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x - anchor.x), 4),
                   round(pcbnew.ToMM(p.GetPosition().y - anchor.y), 4),
                   round(pcbnew.ToMM(p.GetDrillSize().x), 4), round(pcbnew.ToMM(p.GetDrillSize().y), 4),
                   p.GetAttribute(), tuple(sorted(p.GetLayerSet().Seq()))) for p in fp.Pads())


J2_UUID = '18c6ebf4-5f6a-5227-b278-be0fa33a91c9'


def verify_identity(fp):
    if fp.m_Uuid.AsString() != J2_UUID or fp.GetFPID().GetUniStringLibId() != 'Agentee494:SMA_Amphenol_132134_Manufacturer':
        raise ValueError('wrong J2 native UUID or part footprint')


def verify_inventory(board, native, intent, cap):
    """Account for every frozen source reference, footprint, connected pad and no-connect."""
    components = {c['id']: c for c in intent['components']}
    if len(components) != len(intent['components']):
        raise ValueError('duplicate source component identity')
    expected = {c['reference']: c for c in components.values() if c['footprint']}
    if len(expected) != sum(bool(c['footprint']) for c in components.values()):
        raise ValueError('duplicate source component reference')
    excluded = [dict(reference=c['reference'], reason='source symbol has no footprint', lib_id=c['lib_id'])
                for c in components.values() if not c['footprint']]
    envelope = json.loads((cap / 'composition/envelope.json').read_text())
    holes = {h['id']: h for h in envelope['mounting_holes']}
    if len(holes) != len(envelope['mounting_holes']) or set(holes) & set(expected):
        raise ValueError('ambiguous source mounting-hole identity')
    footprints = list(board.GetFootprints())
    if Counter(f.GetReference() for f in footprints) != Counter({r: 1 for r in set(expected) | set(holes)}):
        raise ValueError('native footprint inventory differs from frozen source references')
    actual_refs = set(native['components'])
    if actual_refs != set(expected):
        raise ValueError(f'native schematic inventory differs: missing {sorted(set(expected)-actual_refs)}, extra {sorted(actual_refs-set(expected))}')
    by_ref = {f.GetReference(): f for f in footprints}
    board_only = []
    for ref, hole in holes.items():
        fp = by_ref[ref]
        pads = list(fp.Pads())
        required_flags = pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES
        position = [pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)]
        if (len(pads) != 1 or position != hole.get('at_mm', hole.get('at'))
                or bool(fp.GetAttributes() & required_flags == required_flags) is False or fp.IsDNP()
                or pads[0].GetNumber() or pads[0].GetNetCode()
                or pads[0].GetAttribute() != (pcbnew.PAD_ATTRIB_PTH if hole['plated'] else pcbnew.PAD_ATTRIB_NPTH)
                or [pcbnew.ToMM(pads[0].GetDrillSize().x),pcbnew.ToMM(pads[0].GetDrillSize().y)] != [hole['drill_mm']]*2):
            raise ValueError('native board-only mounting hole differs from frozen envelope: ' + ref)
        board_only.append({'reference':ref,'uuid':fp.m_Uuid.AsString(),'source':hole,
                           'reason':'frozen envelope mounting hole; no symbol, BOM or CPL membership'})
    source_parts = {}
    pad_inventory = {}
    for ref, comp in expected.items():
        if by_ref[ref].GetFPID().GetUniStringLibId() != comp['footprint']:
            raise ValueError(f'native footprint substitution at {ref}')
        lib, name = comp['footprint'].split(':', 1)
        source_fp = pcbnew.FootprintLoad(str(cap / 'footprints' / (lib + '.pretty')), name)
        if source_fp is None or Counter(p.GetNumber() for p in source_fp.Pads()) != Counter(p.GetNumber() for p in by_ref[ref].Pads()):
            raise ValueError(f'native physical pad inventory differs from frozen footprint: {ref}')
        pad_inventory[ref] = [{'number': p.GetNumber(), 'uuid': p.m_Uuid.AsString(), 'net': p.GetNetname()} for p in by_ref[ref].Pads()]
        fields = comp.get('part_binding', {})
        for key in ('LCSC', 'Partnumber', 'Manufacturer'):
            if key in fields and (native['components'][ref]['binding_fields'].get(key) != fields[key] or by_ref[ref].GetFieldText(key) != fields[key]):
                raise ValueError(f'native part identity differs from source at {ref}: {key}')
        source_parts[ref] = {key: fields[key] for key in ('LCSC', 'Partnumber', 'Manufacturer') if key in fields}
    actual_nets = {(ref, pin): n['name'] for n in native['nets'].values() for ref, pin in n['terminals']}
    checked = []
    expected_terminals = {}
    for net in intent['nets']:
        for term in net['terminals']:
            comp = components[term['component']]
            if not comp['footprint']:
                continue  # the explicit symbol-only exclusions above have no native pads
            ref, pin = comp['reference'], str(term['pin']['number'])
            pads = [p for p in by_ref[ref].Pads() if p.GetNumber() == pin]
            # KiCad's top-level labels acquire a leading slash in the emitted native netlist.
            name = '/' + net['name'].lstrip('/')
            if not pads or actual_nets.get((ref, pin)) != name or any(p.GetNetname() != name for p in pads):
                raise ValueError(f'frozen source pad/net mismatch: {ref}.{pin} expected {name}')
            checked.append([ref, pin, name])
            expected_terminals[(ref, pin)] = name
    actual_connected = {k: v for k,v in actual_nets.items() if not v.startswith('unconnected-')}
    if actual_connected != expected_terminals:
        raise ValueError('native electrical terminal inventory differs from frozen source mapping')
    no_connects = set()
    for term in intent['no_connects']:
        comp = components[term['component']]
        if not comp['footprint']:
            continue
        ref, pin = comp['reference'], str(term['pin']['number'])
        pads = [p for p in by_ref[ref].Pads() if p.GetNumber() == pin]
        if (not pads or (ref, pin) not in actual_nets or not actual_nets[(ref, pin)].startswith('unconnected-')
                or any(not p.GetNetname().startswith('unconnected-') for p in pads)):
            raise ValueError(f'source no-connect has an electrical connection or is missing: {ref}.{pin}')
        no_connects.add((ref, pin))
    for ref, rows in pad_inventory.items():
        for pad in rows:
            if pad['number'] and (ref, pad['number']) not in expected_terminals and (ref, pad['number']) not in no_connects:
                raise ValueError(f'native numbered pad has no source mapping: {ref}.{pad["number"]}')
    return {'source_components': len(components), 'source_nets': len(intent['nets']),
            'source_no_connects': len(intent['no_connects']), 'native_footprints': len(footprints),
            'symbol_only_exclusions': excluded, 'board_only_mounting_holes': board_only, 'connected_terminals': checked,
            'part_identities': source_parts, 'physical_pads': pad_inventory,
            'lcsc_identities': sorted({p['LCSC'] for p in source_parts.values() if re.fullmatch(r'C[0-9]+', p.get('LCSC', ''))}),
            'external_parts': {r:p for r,p in source_parts.items() if p.get('LCSC') == 'NO_LCSC'},
            'unorderable_native_features': sorted(r for r,p in source_parts.items() if not p.get('LCSC'))}


def verify_rule_areas(board, binding, envelope_path):
    envelope = json.loads(envelope_path.read_text())
    from agent_ee.scaffold import NAMESPACE
    pinned = binding['native_uuid_derivation']['envelope']
    if pinned['path'] != 'composition/envelope.json' or pinned['sha256'] != digest(envelope_path):
        raise ValueError('RF envelope digest differs from binding')
    expected_sources = {'460352a8-dace-51a2-842b-c1e4ef7ad212': 'D-PCB-7v2-In1-no-tracks',
                        '93d1ddf1-382d-5ed8-abfa-2bf617ad0cae': 'D-PCB-6-RF-reference'}
    if len(binding['rule_area_bindings']) != len(expected_sources) or {a['source_uuid']: a['name'] for a in binding['rule_area_bindings'].values()} != expected_sources:
        raise ValueError('RF source-to-native identity mapping differs')
    areas = {z.m_Uuid.AsString(): z for z in board.Zones()}
    found = []
    for native_uuid, expected_area in binding['rule_area_bindings'].items():
        area = next(a for a in envelope['keepouts'] if a['id'] == expected_area['name'])
        derived_uuid = str(uuid.uuid5(NAMESPACE, digest(envelope_path) + ':area:' + area['id']))
        if native_uuid != derived_uuid or expected_area['polygon_mm'] != area['polygon']:
            raise ValueError('RF binding not derived from frozen envelope')
        if native_uuid not in areas:
            raise ValueError(f'RF area {native_uuid} absent')
        zone = areas[native_uuid]
        points = [[round(pcbnew.ToMM(zone.Outline().CVertex(i).x), 4),
                   round(pcbnew.ToMM(zone.Outline().CVertex(i).y), 4)]
                  for i in range(zone.Outline().TotalVertices())]
        if sorted(points) != sorted(expected_area['polygon_mm']):
            raise ValueError(f'RF area {native_uuid} not rebound to chosen J2: {points}')
        actual_layers = sorted(board.GetLayerName(l) for l in zone.GetLayerSet().Seq())
        prohibited = {'tracks': zone.GetDoNotAllowTracks(), 'vias': zone.GetDoNotAllowVias(),
                      'pads': zone.GetDoNotAllowPads(), 'footprints': zone.GetDoNotAllowFootprints(),
                      'copper_pours': zone.GetDoNotAllowZoneFills()}
        if not zone.GetIsRuleArea() or actual_layers != sorted(area['layers']) or sorted(k for k,v in prohibited.items() if v) != sorted(area['forbid']):
            raise ValueError(f'native rule area {native_uuid} layers/prohibitions changed: {actual_layers}, {prohibited}')
        found.append({'source_uuid': expected_area['source_uuid'], 'native_uuid': native_uuid,
                      'layers': actual_layers, 'prohibitions': prohibited, 'polygon_mm': points})
    return found


def verify(run):
    board_path = run / 'pipe/emission/design/project/telemetry-pod.kicad_pcb'
    before = digest(board_path)
    board = pcbnew.LoadBoard(str(board_path))
    fp = next(f for f in board.GetFootprints() if f.GetReference() == 'J2')
    verify_identity(fp)
    stock = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty',
                                 'SMA_Amphenol_132134_Vertical')
    actual, expected = pattern(fp), pattern(stock)
    if actual != expected:
        raise ValueError(f'native pad/drill/layer pattern differs from stock 132134: {actual}')
    if [(r[0], r[1], r[2], r[3], r[4]) for r in actual] != [
            ('1', 0, 0, 1.5, 1.5), *[('2', x, y, 1.7, 1.7) for x in (-2.54, 2.54) for y in (-2.54, 2.54)]]:
        raise ValueError('published centre 1.5 mm / four 1.7 mm on 5.08 square pattern differs')
    pose = [pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)]
    if pose != [80, 28]:
        raise ValueError(f'J2 writer pose differs: {pose}')
    bounds = fp.GetBoundingBox(False, False)
    if pcbnew.ToMM(bounds.GetRight()) > 90:
        raise ValueError('J2 overhangs the right edge')
    binding = json.loads((run / 'cap/composition/j2-rf-binding.json').read_text())
    found = verify_rule_areas(board, binding, run / 'cap/composition/envelope.json')
    # Read the emitted native netlist: the symbol still has signal pin 1 and ground pin 2.
    from agent_ee.native_netlist import read_native_inventory
    native = read_native_inventory(run / 'pipe/emission/native.xml')
    membership = {n['name']: sorted(pin for ref, pin in n['terminals'] if ref == 'J2')
                  for n in native['nets'].values() if any(ref == 'J2' for ref, pin in n['terminals'])}
    if membership != {'/GND': ['2'], '/POD_GNSS_RF': ['1']}:
        raise ValueError(f'J2 electrical membership changed: {membership}')
    intent = json.loads((run / 'cap/composition/intent.writer.json').read_text())
    inventory = verify_inventory(board, native, intent, run / 'cap')
    # Exercise the BOM/CPL consumer's exclusion rule on both actual native marker sources.
    from agent_ee.fab_export import assembly_exclusions
    xml = ET.parse(run / 'pipe/emission/native.xml').getroot()
    components, footprints = {}, []
    marker_name = 'JLCPCB_Assembly'
    for ref in ('J1', 'J2'):
        symbol = next(c for c in xml.findall('./components/comp') if c.get('ref') == ref)
        fields = {f.get('name'): f.text for f in symbol.findall('./fields/field') if f.get('name') == marker_name}
        native_fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
        if any(p.get('name') == 'dnp' for p in symbol.findall('property')) or native_fp.IsDNP():
            raise ValueError(f'hand-fit part {ref} must stay populated, with not_assembled semantics')
        components[ref] = {'dnp': any(p.get('name') == 'dnp' for p in symbol.findall('property')), 'fields': fields}
        footprints.append({'ref': ref, 'dnp': native_fp.IsDNP(),
                           'fields': {marker_name: native_fp.GetFieldText(marker_name)}})
    excluded, unsupported = assembly_exclusions('JLCPCB_Assembly=not_assembled', components, footprints)
    if unsupported or sorted(e['designator'] for e in excluded) != ['J1', 'J2']:
        raise ValueError(f'BOM/CPL hand-fit exclusions differ: {excluded}, {unsupported}')
    from agent_ee.fab_export import part_bindings, board_facts, assembled_parts, bom_rows, render_bom, cpl_rows, render_cpl
    probes = {c['reference']: json.loads(c['part_binding']['AGENT_EE_Probe']) for c in intent['components']
              if 'AGENT_EE_Probe' in c.get('part_binding', {})}
    parts_manifest = json.loads((run / 'cap/composition/parts.json').read_text())
    copper_refs = {i['reference'] for p in parts_manifest['parts'] if p.get('kind') == 'copper_feature' for i in p['instances']}
    all_components, problems = part_bindings(run / 'pipe/emission/native.xml', probes)
    facts = board_facts(board_path.read_bytes(), probes, copper_refs)
    full_excluded, exclusion_problems = assembly_exclusions('JLCPCB_Assembly=not_assembled', all_components, facts['footprints'])
    excluded_refs = {e['designator'] for e in full_excluded}
    assembled, disagreements, unsupported = assembled_parts(all_components, facts['footprints'], excluded_refs, copper_refs)
    rows, flagged = bom_rows(assembled)
    if problems or exclusion_problems or unsupported or disagreements or flagged or excluded_refs != {'J1','J2'}:
        raise ValueError(f'native BOM consumer refused: {problems}, {exclusion_problems}, {unsupported}, {disagreements}, {flagged}')
    # The native position export is made by the admitted snapshot check, never synthesized from intended poses.
    pos_path = run / 'native-positions.csv'
    positions = [r for r in cpl_rows(pos_path.read_text()) if r[0] not in excluded_refs and r[0] not in copper_refs and r[0] not in probes]
    if {r[0] for r in positions} != set(assembled):
        raise ValueError('native BOM/CPL assembled membership differs')
    evidence = run / 'j2-verification'
    evidence.mkdir(exist_ok=True)
    (evidence / 'BOM.csv').write_text(render_bom(rows))
    (evidence / 'CPL.csv').write_text(render_cpl(positions))
    if digest(board_path) != before:
        raise ValueError('verification modified candidate board')
    # Preserve successful native checks even when required access evidence is absent.
    # This is a partial report; the strict access check below still refuses the CLI.
    (evidence / 'native-checks.json').write_text(json.dumps({
        'status': 'PARTIAL', 'scope': 'native checks only; required access check follows; no candidate acceptance',
        'board_sha256': before, 'j2_uuid': fp.m_Uuid.AsString(), 'pose_mm': pose,
        'pattern': actual, 'electrical_membership': membership, 'rf_areas': found,
        'inventory': inventory, 'bom_cpl_excluded': full_excluded,
        'bom_rows': len(rows), 'cpl_rows': len(positions),
        'bom_sha256': digest(evidence / 'BOM.csv'), 'cpl_sha256': digest(evidence / 'CPL.csv')}, indent=1) + '\n')
    access_path = run / 'pipe/access-rebound/reservations.json'
    access = json.loads(access_path.read_text())
    source_access = json.loads((Path(__file__).parent.parent / 'agentee-489-source/reservations.json').read_text())
    if len(access['reservations']) != 44 or sorted(r['id'] for r in access['reservations']) != sorted(
            r['id'] for r in source_access['reservations']):
        raise ValueError('44 access row identities changed')
    migrations = json.loads((access_path.parent / 'owner-migrations.json').read_text())
    if access['original_board_sha256'] != before or migrations['board_sha256'] != before:
        raise ValueError('access rows were not derived from this final annotated board')
    native_owners = {f.GetReference(): f for f in board.GetFootprints()}
    for row in access['reservations']:
        owner = row['owner']
        native_fp = native_owners[owner['ref']]
        if owner['uuid'] != native_fp.m_Uuid.AsString():
            raise ValueError('access owner UUID differs: ' + row['id'])
        if 'pad' in owner and not any(p.GetNumber() == owner['pad']['number'] and p.m_Uuid.AsString() == owner['pad']['uuid'] for p in native_fp.Pads()):
            raise ValueError('access pad identity differs: ' + row['id'])
    return {'board_sha256': before, 'j2_uuid': fp.m_Uuid.AsString(), 'pose_mm': pose,
            'pattern': actual, 'electrical_membership': membership, 'rf_areas': found,
            'bom_cpl_excluded': full_excluded, 'bom_rows': len(rows), 'cpl_rows': len(positions),
            'bom_sha256': digest(evidence / 'BOM.csv'), 'cpl_sha256': digest(evidence / 'CPL.csv'), 'inventory': inventory,
            'access_rows': 44, 'access_sha256': digest(access_path),
            'status': 'PASS', 'scope': 'diagnostic J2 adoption only; C1 NOT_RUN; no placement/routing acceptance'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.run), indent=1))
