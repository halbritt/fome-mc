"""AGENTEE-446 ee446g: read-only native (pcbnew) probe of J1/U3 on a board snapshot.

Usage (inside fome-runtime:d96f8e00, through native-admit; see README.md):
    python3 probe.py BOARD [BOARD ...] --library PRETTY:NAME --coordinates COORDS.json > facts.json

Each BOARD is a snapshot copy under build/runs/; it is loaded with pcbnew.LoadBoard and never saved. The output is
deterministic (no timestamps) so its sha256 is stable. Nothing here is a TE compliance, retention, seating or fit
claim: these are the board's own nominal native values.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import pcbnew

MM = 1e6


def mm(v):
    return round(v / MM, 4)


def pt(p, origin=None):
    if origin is None:
        return [mm(p.x), mm(p.y)]
    return [mm(p.x - origin.x), mm(p.y - origin.y)]


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def pad_record(pad, origin):
    attrib = {pcbnew.PAD_ATTRIB_PTH: 'PTH', pcbnew.PAD_ATTRIB_NPTH: 'NPTH',
              pcbnew.PAD_ATTRIB_SMD: 'SMD', pcbnew.PAD_ATTRIB_CONN: 'CONN'}[pad.GetAttribute()]
    drill = pad.GetDrillSize()
    size = pad.GetSize(pcbnew.F_Cu)
    rec = {'number': pad.GetNumber(), 'attrib': attrib, 'at': pt(pad.GetPosition(), origin),
           'size': [mm(size.x), mm(size.y)], 'shape': pad.ShowPadShape(pcbnew.F_Cu),
           'drill': [mm(drill.x), mm(drill.y)], 'drill_shape': pad.GetDrillShape(),
           'layers': sorted(pcbnew.LayerName(l) for l in pad.GetLayerSet().Seq()),
           'orientation_deg': round(pad.GetOrientationDegrees(), 4)}
    if attrib == 'PTH':
        rec['nominal_radial_annulus_mm'] = round((min(rec['size']) - max(rec['drill'])) / 2, 4)
    return rec


def footprint_geometry(fp):
    """Footprint-local geometry (pads, graphics, models), independent of board pose, uuids and net names."""
    origin = fp.GetPosition()
    pads = sorted((pad_record(p, origin) for p in fp.Pads()), key=lambda r: (r['number'], r['at']))
    graphics = []
    for g in fp.GraphicalItems():
        box = g.GetBoundingBox()
        graphics.append({'class': g.GetClass(), 'layer': pcbnew.LayerName(g.GetLayer()),
                         'bbox': [mm(box.GetLeft() - origin.x), mm(box.GetTop() - origin.y),
                                  mm(box.GetRight() - origin.x), mm(box.GetBottom() - origin.y)]})
    graphics.sort(key=lambda r: json.dumps(r, sort_keys=True))
    models = [{'file': m.m_Filename, 'offset': [round(m.m_Offset.x, 4), round(m.m_Offset.y, 4), round(m.m_Offset.z, 4)],
               'rotation': [round(m.m_Rotation.x, 4), round(m.m_Rotation.y, 4), round(m.m_Rotation.z, 4)],
               'scale': [round(m.m_Scale.x, 4), round(m.m_Scale.y, 4), round(m.m_Scale.z, 4)]} for m in fp.Models()]
    return {'pads': pads, 'graphics': graphics, 'models': models}


def edge_segments(board):
    segs = []
    for d in board.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and d.GetClass() == 'PCB_SHAPE' and d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            segs.append((d.GetStart(), d.GetEnd()))
    return segs


def point_segment_mm(p, a, b):
    ax, ay, bx, by, px, py = a.x, a.y, b.x, b.y, p.x, p.y
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy)) / MM


def board_facts(path):
    board = pcbnew.LoadBoard(str(path))
    ds = board.GetDesignSettings()
    edges = board.GetBoardEdgesBoundingBox()
    out = {'path': str(path), 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
           'board_thickness_mm': mm(ds.GetBoardThickness()), 'copper_layers': board.GetCopperLayerCount(),
           'design_rules_mm': {'min_through_hole': mm(ds.m_MinThroughDrill),
                               'hole_clearance': mm(ds.m_HoleClearance), 'hole_to_hole': mm(ds.m_HoleToHoleMin),
                               'copper_edge_clearance': mm(ds.m_CopperEdgeClearance)},
           'edge_cuts_bbox_mm': [mm(edges.GetLeft()), mm(edges.GetTop()), mm(edges.GetRight()), mm(edges.GetBottom())],
           'footprints': {}}
    segs = edge_segments(board)
    for ref in ('J1', 'U3'):
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            out['footprints'][ref] = None
            continue
        box = fp.GetBoundingBox(False)
        inside = edges.Contains(box.GetOrigin()) and edges.Contains(box.GetEnd())
        geom = footprint_geometry(fp)
        rec = {'fpid': fp.GetFPIDAsString(), 'position_mm': pt(fp.GetPosition()),
               'rotation_deg': round(fp.GetOrientationDegrees(), 4), 'layer': fp.GetLayerName(),
               'locked': fp.IsLocked(), 'bbox_inside_edge_cuts_bbox': inside,
               'geometry_sha256': digest(geom), 'pads_sha256': digest(geom['pads']), 'geometry': geom}
        if ref == 'J1':
            holes = [(p, p.GetDrillSize().x / MM) for p in fp.Pads() if p.GetDrillSize().x > 0]
            gap = min((math.hypot((a.GetPosition().x - b.GetPosition().x) / MM, (a.GetPosition().y - b.GetPosition().y) / MM)
                       - da / 2 - db / 2, a.GetNumber() or 'npth', b.GetNumber() or 'npth')
                      for i, (a, da) in enumerate(holes) for b, db in holes[i + 1:])
            rec['min_hole_wall_gap_mm'] = {'value': round(gap[0], 4), 'pair': [gap[1], gap[2]]}
            pth = [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
            rec['min_pth_land_to_edge_mm'] = round(min(
                point_segment_mm(p.GetPosition(), a, b) - p.GetSize(pcbnew.F_Cu).x / MM / 2 for p in pth for a, b in segs), 4)
            npth = [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
            rec['locator_centreline_to_edge_mm'] = sorted(round(min(point_segment_mm(p.GetPosition(), a, b)
                                                                    for a, b in segs), 4) for p in npth)
        out['footprints'][ref] = rec
    return out


def footprint_text_digest(path, ref):
    """sha256 of the board file's footprint block for REF with uuids, the footprint's own (at ...) and net names removed."""
    text = Path(path).read_text()
    i = text.index(f'(property "Reference" "{ref}"')
    start = text.rindex('\n\t(footprint ', 0, i) + 1
    end = text.index('\n\t)\n', i) + 4
    block = text[start:end]
    block = re.sub(r'\(uuid "[^"]*"\)', '', block)
    block = re.sub(r'\(net "[^"]*"\)|\(net \d+ "[^"]*"\)', '', block)
    block = re.sub(r'\A(\t\(footprint "[^"]*"\s*(?:\(locked\)\s*)?\(layer "[^"]*"\)\s*)\(at [^)]*\)', r'\1', block)
    return hashlib.sha256(block.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('boards', nargs='+')
    ap.add_argument('--library', required=True, help='PRETTY_DIR:FOOTPRINT_NAME of the captured J1 library footprint')
    ap.add_argument('--coordinates', required=True, help='connector-candidate/review/coordinates.json')
    a = ap.parse_args()
    lib, name = a.library.rsplit(':', 1)
    libfp = pcbnew.FootprintLoad(lib, name)
    coords = json.loads(Path(a.coordinates).read_text())
    expected = {str(p['number']): [p['x_mm'], p['y_mm']] for p in coords['pads']}
    out = {'schema': 'ee446g.native-probe/1', 'kicad': pcbnew.Version(), 'boards': [],
           'library': {'path': a.library, 'geometry_sha256': None, 'pads_sha256': None}}
    libgeom = footprint_geometry(libfp)
    out['library'].update(geometry_sha256=digest(libgeom), pads_sha256=digest(libgeom['pads']),
                          graphics_sha256=digest(libgeom['graphics']), models=libgeom['models'])
    for b in a.boards:
        facts = board_facts(b)
        j1 = facts['footprints']['J1']
        got = {p['number']: p['at'] for p in j1['geometry']['pads'] if p['attrib'] == 'PTH'}
        j1['pth_matches_coordinates_json'] = got == expected
        j1['pads_equal_library'] = j1['pads_sha256'] == out['library']['pads_sha256']
        j1['graphics_equal_library'] = digest(j1['geometry']['graphics']) == out['library']['graphics_sha256']
        for ref in ('J1', 'U3'):
            facts['footprints'][ref]['text_block_sha256'] = footprint_text_digest(b, ref)
        out['boards'].append(facts)
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()


if __name__ == '__main__':
    main()
