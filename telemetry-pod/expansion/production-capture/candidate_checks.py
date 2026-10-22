"""Native checks on the prepared and emitted production candidate (AGENTEE-207 j6b), used by pipeline.py.

Each function reads native KiCad files or agent-ee's own records and returns what it found; any deviation
raises, so a refusal stays visible in pipeline.json. Nothing here edits a design file.

- model_resolution (FOMEMC-34): agent-ee's candidate model inventory (models3d.inspect_models, the inventory
  candidate renders and placement proposals use) must resolve J1 and U3 to the exact bound bytes of
  composition/project-models.json at ${KIPRJMOD}/inputs/models/, with the pose each footprint stores;
- copper_features (agent-509 JP1-JP5 ruling): the composed fab check declares exactly the manifest's
  copper_feature references; agent-ee's own fab/parts cross-check, board and schematic copper predicates
  accept them; natively each is one two-pad surface-copper footprint, excluded from BOM and position files,
  not DNP, on the board, with its two pads on the two distinct declared nets and no copper joining them
  (default open);
- j1_inspection (agent-509 iter8t J1 baseline audit, AGENTEE-446): 35 plated holes 1.75 mm with 2.4 mm lands
  (0.325 mm annulus) on the 4 mm grid and two 2.85 mm unplated locators at (+/-28.5, +0.5), read natively;
- initial_candidate: the identity of the candidate campaign iteration 1 captures, recomputed with agent-ee's
  own candidate.capture from the prepared scope and compared with the dry-run capture.
"""
import hashlib
import json
import tempfile
from pathlib import Path

JUMPERS = ['JP1', 'JP2', 'JP3', 'JP4', 'JP5']
JUMPER_FOOTPRINT = 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'
MM = 1e6


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def model_resolution(board, record, references=('J1', 'U3')):
    """The bound references resolve through agent-ee's inventory to the bound model bytes inside the candidate
    project. The scaffold board holds only the envelope's fixed footprints, so it is graded for J1 alone."""
    from agent_ee.models3d import inspect_models
    board = Path(board).resolve()
    inventory = inspect_models(board, {})
    found = {}
    for bound in record['models']:
        ref = bound['reference']
        if ref not in references:
            continue
        (fp,) = [f for f in inventory['footprints'] if f['reference'] == ref]
        (model,) = fp['models']
        expected = (board.parent / bound['model_reference'].removeprefix('${KIPRJMOD}/')).resolve()
        found[ref] = {'footprint': fp['footprint'], 'status': fp['status'], 'path': model['path'],
                      'resolution_source': model['resolution_source'], 'sha256': model.get('sha256'),
                      'resolved_path': Path(model['resolved_path']).relative_to(board.parent).as_posix()
                      if model.get('resolved_path') else None}
        if (fp['footprint'] != bound['footprint'] or model['status'] != 'resolved' or model['path'] != bound['model_reference']
                or model.get('sha256') != bound['candidate']['sha256'] or Path(model['resolved_path']) != expected
                or model['variable_sources'] != {'KIPRJMOD': 'project'}):
            raise ValueError(f'{ref} model does not resolve to its bound bytes: {json.dumps(found[ref])}')
    return {'board': {'path': str(board), 'sha256': inventory['board']['sha256']}, 'models': found,
            'summary': inventory['summary']}


def native_pose(board, record):
    """The model transform each bound footprint carries on the native board (pcbnew), against the record."""
    import pcbnew
    loaded = pcbnew.LoadBoard(str(board))
    found = {}
    for bound in record['models']:
        fp = loaded.FindFootprintByReference(bound['reference'])
        (model,) = list(fp.Models())
        vec = lambda v: [round(v.x, 6), round(v.y, 6), round(v.z, 6)]  # noqa: E731
        pose = {'offset': vec(model.m_Offset), 'scale': vec(model.m_Scale), 'rotate': vec(model.m_Rotation)}
        found[bound['reference']] = {'filename': model.m_Filename, **pose, 'show': bool(model.m_Show),
                                     'position_mm': [fp.GetPosition().x / MM, fp.GetPosition().y / MM],
                                     'rotation_deg': fp.GetOrientationDegrees(), 'layer': fp.GetLayerName()}
        if (model.m_Filename != bound['model_reference'] or not model.m_Show
                or pose != {k: [float(x) for x in bound['pose'][k]] for k in ('offset', 'scale', 'rotate')}):
            raise ValueError(f"{bound['reference']} native model pose differs from the record: {found[bound['reference']]}")
    return found


def copper_features(root, scope, files, manifest_rel, board_rel, schematic_rel, netlist):
    """agent-509 ruling: JP1-JP5 are on-board, normally-open copper; never BOM, never DNP; cross-check kept."""
    import pcbnew
    from agent_ee.copper_features import fab_parts_manifests
    from agent_ee.fab_export import copper_feature_problems, copper_schematic_problems
    from agent_ee.native_netlist import read_native_inventory
    from agent_ee.symbol_library import parse_sexpr
    root = Path(root)
    manifest = json.loads((root / manifest_rel).read_text())
    declared = {i['reference']: (p, i) for p in manifest['parts'] if p.get('kind') == 'copper_feature'
                for i in p['instances']}
    (fab,) = [c for c in scope['checks'] if c['kind'] == 'fab_package']
    if sorted(declared) != JUMPERS or fab['params'].get('copper_features') != JUMPERS:
        raise ValueError(f"copper features {sorted(declared)} / fab {fab['params'].get('copper_features')} are not JP1-JP5")
    for ref, (part, _) in declared.items():
        if (part['copper']['native_flags'] != {'in_bom': False, 'dnp': False, 'exclude_from_board': False}
                or part['footprint'] != JUMPER_FOOTPRINT or part.get('lcsc') or 'selection' in part):
            raise ValueError(f'{ref} manifest declaration is not unpurchased on-board copper')
    cross = fab_parts_manifests(fab['params'], scope, files, root)  # the agent-ee fab/parts cross-check, unsuppressed
    if [r['references'] for r in cross] != [JUMPERS]:
        raise ValueError(f'fab/parts copper cross-check did not bind JP1-JP5: {cross}')
    board_bytes, sch_bytes = (root / board_rel).read_bytes(), (root / schematic_rel).read_bytes()
    predicates = {'board': copper_feature_problems(board_bytes, set(JUMPERS)),
                  'schematic': copper_schematic_problems(sch_bytes, set(JUMPERS))}
    if any(predicates.values()):
        raise ValueError(f'agent-ee copper predicates refuse: {predicates}')
    native = read_native_inventory(netlist)
    symbols = {}
    for node in parse_sexpr(sch_bytes)[1:]:
        if isinstance(node, list) and node and node[0] == 'symbol':
            refs = [p[2] for p in node if isinstance(p, list) and p[:2] == ['property', 'Reference']]
            if refs and refs[0] in declared:
                flags = {n[0]: n[1] for n in node if isinstance(n, list) and len(n) == 2 and n[0] in
                         ('in_bom', 'on_board', 'dnp', 'in_pos_files', 'exclude_from_sim')}
                symbols.setdefault(refs[0], []).append(flags)
    board = pcbnew.LoadBoard(str(root / board_rel))
    tracks = len(board.GetTracks())
    found = {}
    for ref, (part, instance) in sorted(declared.items()):
        fp = board.FindFootprintByReference(ref)
        pads = sorted(fp.Pads(), key=lambda p: p.GetNumber())
        boxes = [p.GetBoundingBox() for p in pads]
        gap = (boxes[1].GetLeft() - boxes[0].GetRight()) / MM if len(boxes) == 2 else None
        nets = {p.GetNumber(): p.GetNetname() for p in pads}
        joined = [z.GetNetname() for z in board.Zones() if z.GetNetname() in nets.values()]
        netlist_nets = {pin: next(n['name'] for n in native['nets'].values() if (ref, pin) in n['terminals'])
                        for pin in native['components'][ref]['pins']}
        record = {'footprint': fp.GetFPIDAsString(), 'layer': fp.GetLayerName(), 'pads': len(pads),
                  'pad_kinds': sorted({str(p.GetAttribute()) for p in pads}), 'pad_layers': sorted(
                      {pcbnew.BOARD.GetStandardLayerName(l) for p in pads for l in p.GetLayerSet().Seq() if pcbnew.IsCopperLayer(l)}),
                  'pad_gap_mm': gap, 'nets': nets, 'netlist_nets': netlist_nets, 'declared_nets': instance['nets'],
                  'excluded_from_bom': fp.IsExcludedFromBOM(), 'excluded_from_pos_files': fp.IsExcludedFromPosFiles(),
                  'dnp': fp.IsDNP(), 'board_only': fp.IsBoardOnly(), 'zones_on_its_nets': joined,
                  'schematic_flags': symbols.get(ref)}
        found[ref] = record
        smd = str(pcbnew.PAD_ATTRIB_SMD)
        if (record['footprint'] != JUMPER_FOOTPRINT or len(pads) != 2 or record['pad_kinds'] != [smd]
                or not gap or gap <= 0 or nets != instance['nets'] or netlist_nets != instance['nets']
                or len(set(nets.values())) != 2 or not record['excluded_from_bom'] or not record['excluded_from_pos_files']
                or record['dnp'] or joined or symbols.get(ref) != [{**symbols[ref][0], 'in_bom': 'no', 'on_board': 'yes', 'dnp': 'no'}]):
            raise ValueError(f'{ref} is not native on-board normally-open copper: {json.dumps(record)}')
    if tracks:
        raise ValueError(f'the emitted board has {tracks} tracks; default-open copper is graded on the unrouted seed only')
    return {'ruling': 'agent-509 source decision (coordinator notes, 2026-10-22): on-board normally-open copper, '
                      'not BOM, not DNP; never dropped or relabelled; cross-check not suppressed',
            'fab_check': {'id': fab['id'], 'copper_features': fab['params']['copper_features']},
            'fab_parts_cross_check': cross, 'agent_ee_predicates': predicates, 'board_tracks': tracks,
            'board_sha256': sha(root / board_rel), 'schematic_sha256': sha(root / schematic_rel),
            'netlist_sha256': sha(netlist), 'native': found,
            'default_open': ('each jumper is two separate surface pads on its two distinct declared nets, with no track, '
                             'via or zone joining them on this unrouted board; closing one is a later solder action')}


def j1_inspection(board):
    """The agent-509 iter8t J1 audit, rerun natively on this board (pcbnew), footprint-local coordinates."""
    import pcbnew
    loaded = pcbnew.LoadBoard(str(board))
    fp = loaded.FindFootprintByReference('J1')
    origin, plated, npth = fp.GetPosition(), [], []
    if fp.GetOrientationDegrees() != 0:
        raise ValueError('J1 is rotated; footprint-local audit coordinates need rotation 0')
    for pad in fp.Pads():
        local = [round((pad.GetPosition().x - origin.x) / MM, 4), round((pad.GetPosition().y - origin.y) / MM, 4)]
        drill = [round(pad.GetDrillSize().x / MM, 4), round(pad.GetDrillSize().y / MM, 4)]
        size = [round(pad.GetSize(pcbnew.F_Cu).x / MM, 4), round(pad.GetSize(pcbnew.F_Cu).y / MM, 4)]
        entry = {'number': pad.GetNumber(), 'at': local, 'drill': drill, 'size': size}
        (plated if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else npth).append(entry)
    rows = {-4: (12, -22), 0: (11, -20), 4: (12, -22)}
    expected = {(x0 + 4 * i, y) for y, (n, x0) in rows.items() for i in range(n)}
    centres = {tuple(p['at']) for p in plated}
    annulus = sorted({round((p['size'][0] - p['drill'][0]) / 2, 4) for p in plated})
    result = {'board_sha256': sha(board), 'position_mm': [origin.x / MM, origin.y / MM], 'side': fp.GetLayerName(),
              'plated': len(plated), 'plated_drill_mm': sorted({p['drill'][0] for p in plated}),
              'plated_land_mm': sorted({p['size'][0] for p in plated}), 'annulus_mm': annulus,
              'grid_matches_k1_sheet_2': centres == {(float(x), float(y)) for x, y in expected},
              'numbers': sorted(int(p['number']) for p in plated) == list(range(1, 36)),
              'npth': [{k: p[k] for k in ('at', 'drill')} for p in sorted(npth, key=lambda p: p['at'])]}
    if (result['plated'] != 35 or result['plated_drill_mm'] != [1.75] or result['plated_land_mm'] != [2.4]
            or annulus != [0.325] or not result['grid_matches_k1_sheet_2'] or not result['numbers']
            or result['npth'] != [{'at': [-28.5, 0.5], 'drill': [2.85, 2.85]}, {'at': [28.5, 0.5], 'drill': [2.85, 2.85]}]):
        raise ValueError(f'J1 native pattern differs from the audited baseline: {json.dumps(result)}')
    return result


def initial_candidate(prepared, dry_run_candidate):
    """Iteration 1 captures prepared/scope.json; agent-ee's candidate.capture recomputes its identity here."""
    from agent_ee import candidate
    prepared = Path(prepared)
    recorded = json.loads(Path(dry_run_candidate).read_text())
    with tempfile.TemporaryDirectory(prefix='pod-initial-candidate-') as tmp:
        manifest = candidate.capture(prepared / 'scope.json', Path(tmp))
    if manifest['candidate_id'] != recorded['candidate_id'] or manifest['files'] != recorded['files']:
        raise ValueError('the prepared scope does not capture the dry-run candidate')
    scope = manifest['scope']
    return {'candidate_id': manifest['candidate_id'], 'scope_sha256': sha(prepared / 'scope.json'),
            'campaign_sha256': sha(prepared / 'campaign.json'), 'driver_receipt_sha256': sha(prepared / 'driver-receipt.json'),
            'files': len(manifest['files']),
            'board': {'path': scope['board'], 'sha256': manifest['files'][scope['board']]},
            'schematic': {'path': scope['schematic'], 'sha256': manifest['files'][scope['schematic']]},
            'models': {k: v for k, v in manifest['files'].items() if k.startswith('project/inputs/models/')},
            'equals_dry_run_candidate': True,
            'meaning': ('candidate.capture of prepared/scope.json, the capture campaign iteration 1 starts from; '
                        'equal to the dry-run candidate.json identity and file manifest')}
