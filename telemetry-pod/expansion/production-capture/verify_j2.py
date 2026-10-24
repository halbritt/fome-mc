"""Read-only native verification of the producer-adopted Amphenol 132134 J2.

Run in the qualified KiCad container against the diagnostic emission directory.
This verifies the selected part and geometry; it does not accept placement or routing.
"""
import argparse
import hashlib
import json
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


def verify(run):
    board_path = run / 'pipe/emission/design/project/telemetry-pod.kicad_pcb'
    before = digest(board_path)
    board = pcbnew.LoadBoard(str(board_path))
    fp = next(f for f in board.GetFootprints() if f.GetReference() == 'J2')
    if not fp.m_Uuid.AsString().startswith('18c6ebf4') or (fp.GetFPID().GetLibNickname(), fp.GetFPID().GetLibItemName()) != ('Agentee494', 'SMA_Amphenol_132134_Manufacturer'):
        raise ValueError('wrong J2 native UUID or part footprint')
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
    areas = {z.m_Uuid.AsString(): z for z in board.Zones()}
    found = []
    for uuid in binding['rule_area_uuids']:
        if uuid not in areas:
            raise ValueError(f'RF area {uuid} absent')
        zone = areas[uuid]
        points = [[round(pcbnew.ToMM(zone.Outline().CVertex(i).x), 4),
                   round(pcbnew.ToMM(zone.Outline().CVertex(i).y), 4)]
                  for i in range(zone.Outline().TotalVertices())]
        expected_area = binding['rule_area_bindings'][uuid]
        if sorted(points) != sorted(expected_area['polygon_mm']):
            raise ValueError(f'RF area {uuid} not rebound to chosen J2: {points}')
        if (zone.GetDoNotAllowTracks() != expected_area['tracks_forbidden'] or
                zone.GetDoNotAllowVias() != expected_area['vias_forbidden']):
            raise ValueError(f'native rule area {uuid} prohibitions changed')
        found.append({'uuid': uuid, 'polygon_mm': points})
    access_path = run / 'pipe/access-rebound/reservations.json'
    access = json.loads(access_path.read_text())
    source_access = json.loads((Path(__file__).parent.parent / 'agentee-489-source/reservations.json').read_text())
    if len(access['reservations']) != 44 or sorted(r['id'] for r in access['reservations']) != sorted(
            r['id'] for r in source_access['reservations']):
        raise ValueError('44 access row identities changed')
    # Read the emitted native netlist: the symbol still has signal pin 1 and ground pin 2.
    from agent_ee.native_netlist import read_native_inventory
    native = read_native_inventory(run / 'pipe/emission/native.xml')
    membership = {n['name']: sorted(pin for ref, pin in n['terminals'] if ref == 'J2')
                  for n in native['nets'].values() if any(ref == 'J2' for ref, pin in n['terminals'])}
    if membership != {'/GND': ['2'], '/POD_GNSS_RF': ['1']}:
        raise ValueError(f'J2 electrical membership changed: {membership}')
    # Exercise the BOM/CPL consumer's exclusion rule on both actual native marker sources.
    from agent_ee.fab_export import assembly_exclusions
    xml = ET.parse(run / 'pipe/emission/native.xml').getroot()
    components, footprints = {}, []
    marker_name = 'JLCPCB_Assembly'
    for ref in ('J1', 'J2'):
        symbol = next(c for c in xml.findall('./components/comp') if c.get('ref') == ref)
        fields = {f.get('name'): f.text for f in symbol.findall('./fields/field') if f.get('name') == marker_name}
        native_fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
        components[ref] = {'dnp': any(p.get('name') == 'dnp' for p in symbol.findall('property')), 'fields': fields}
        footprints.append({'ref': ref, 'dnp': native_fp.IsDNP(),
                           'fields': {marker_name: dict(native_fp.GetProperties()).get(marker_name)}})
    excluded, unsupported = assembly_exclusions('JLCPCB_Assembly=not_assembled', components, footprints)
    if unsupported or sorted(e['designator'] for e in excluded) != ['J1', 'J2']:
        raise ValueError(f'BOM/CPL hand-fit exclusions differ: {excluded}, {unsupported}')
    if digest(board_path) != before:
        raise ValueError('verification modified candidate board')
    return {'board_sha256': before, 'j2_uuid': fp.m_Uuid.AsString(), 'pose_mm': pose,
            'pattern': actual, 'electrical_membership': membership, 'rf_areas': found,
            'bom_cpl_excluded': excluded,
            'access_rows': 44, 'access_sha256': digest(access_path),
            'status': 'PASS', 'scope': 'diagnostic J2 adoption only; C1 NOT_RUN; no placement/routing acceptance'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.run), indent=1))
