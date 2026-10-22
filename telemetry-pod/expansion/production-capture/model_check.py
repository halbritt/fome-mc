"""FOMEMC-34: native KiCad STEP export of the bound J1 and U3 models from an emitted candidate board.

KiCad itself must load each bound model (kicad-cli pcb export step, one component at a time); CadQuery 2.8.0
then reads the native exports independently:

- J1: the criteria of connector-candidate/check_model.py (board body plus J1; the exact model solid, 35 tail
  axes on the drilled coordinates, 35 tip faces below the two rear support flats, 3.50 mm projection, model
  envelope), graded against this board's own native exporter datum. check_model.py itself is also run,
  unchanged, and its result is kept verbatim: its absolute Z values are the connector-only fixture's exporter
  datum (board body Z 0..1.48, supports Z 1.565), which the connector README says is not a physical stand-off;
  the candidate stackup exports a different body thickness. The candidate J1 must sit where the fixture puts
  it: (45, 55.5) mm, 0 degrees, F.Cu, on a 1.6 mm board;
- U3: the 29 visualization solids at the board's U3 pose (rotation 0 or 180 on F.Cu), every castellation
  overlapping its native pad centre and the pin-1 marker at pad 1 (neo-m9n-model/verify.py's criteria,
  with the pose read from this board instead of iter8t).

Visual/mechanical model placement only: no fit, retention, mating, solder or electrical claim.

Usage (fome-mc root, system python with pcbnew; uv with a cached cadquery 2.8.0, run offline):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/model_check.py BOARD OUT_DIR
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONNECTOR_CHECK = HERE.parent / 'connector-candidate/check_model.py'
UV = ['uv', 'run', '--offline', '--no-project', '--python', '3.12', '--with', 'cadquery==2.8.0', 'python', '-B']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export(board, out, reference, board_body):
    argv = ['kicad-cli', 'pcb', 'export', 'step', '--force', '--component-filter', reference,
            *([] if board_body else ['--no-board-body']), '-o', str(out), str(board)]
    done = subprocess.run(argv, capture_output=True, text=True, timeout=900)
    log = (done.stdout + done.stderr).splitlines()
    (out.parent / f'{reference}-step-export.log').write_text('\n'.join(log) + '\n')
    problems = [l for l in log if any(w in l.lower() for w in ('cannot', 'could not', 'not found', 'failed', 'error'))]
    if done.returncode or problems or not out.is_file():
        raise SystemExit(f'native {reference} STEP export did not load its model (rc {done.returncode}): {problems[:5]}')
    return {'argv': argv[:-1] + ['BOARD'], 'rc': done.returncode, 'log': f'{reference}-step-export.log',
            'step': out.name, 'sha256': sha(out), 'log_lines': len(log)}


def board_facts(board):
    import pcbnew
    loaded = pcbnew.LoadBoard(str(board))
    facts = {'thickness_mm': loaded.GetDesignSettings().GetBoardThickness() / 1e6}
    for ref in ('J1', 'U3'):
        fp = loaded.FindFootprintByReference(ref)
        if len(list(fp.Models())) != 1:
            raise SystemExit(f'{ref} carries {len(list(fp.Models()))} models; exactly one bound model is required')
        (model,) = list(fp.Models())
        facts[ref] = {'position_mm': [fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6],
                      'rotation_deg': fp.GetOrientationDegrees(), 'layer': fp.GetLayerName(), 'model': model.m_Filename,
                      'pads_world_mm': {p.GetNumber(): [p.GetPosition().x / 1e6, p.GetPosition().y / 1e6] for p in fp.Pads()
                                        if p.GetNumber()}}
    return facts


# connector-candidate/check_model.py constants (fixture native export) and its envelope, for the datum shift.
J1_VOLUME = 20330.606767556506
FIXTURE_SUPPORT_Z, FIXTURE_BODY_TOP_Z = 1.565, 1.48
FIXTURE_BOUNDS = [6.55, 83.45, -87.3, -49.5, -2.765, 29.335]


def j1_cadquery(step):
    """check_model.py's criteria with the absolute Z values taken relative to this export's own datum."""
    import math
    import cadquery as cq
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
    solids = cq.importers.importStep(str(step)).solids().vals()
    models = [s for s in solids if abs(s.Volume() - J1_VOLUME) < 0.01]
    assert len(solids) == 2 and len(models) == 1, 'one board and exact connector required'
    model, (board,) = models[0], [s for s in solids if s is not models[0]]
    axes, tips, supports = set(), [], []
    for f in model.Faces():
        surface = BRepAdaptor_Surface(f.wrapped)
        if surface.GetType() == GeomAbs_Cylinder:
            cylinder = surface.Cylinder()
            if abs(cylinder.Axis().Direction().Z()) > .99999 and abs(cylinder.Radius() - .65) < 1e-5:
                axes.add((round(cylinder.Location().X(), 5), round(cylinder.Location().Y(), 5)))
        elif surface.GetType() == GeomAbs_Plane and abs(surface.Plane().Axis().Direction().Z()) > .99999:
            if abs(f.Area() - math.pi * .65 ** 2) < 1e-5:
                tips.append(surface.Plane().Location().Z())
            if abs(f.Area() - 6.5) < 1e-5:
                supports.append(surface.Plane().Location().Z())
    expected = {(45 + x0 + 4 * i, -55.5 - y) for count, x0, y in [(12, -22, -4), (11, -20, 0), (12, -22, 4)]
                for i in range(count)}
    assert axes == expected, 'native model tails must align with all 35 PCB drill axes'
    assert len(tips) == 35 and len(supports) == 2, 'tail tips and rear seating flats'
    datum = supports[0]
    body_top = board.BoundingBox().zmax
    assert all(abs(z - datum) < 1e-5 for z in supports), 'both rear support flats on one plane'
    assert all(abs(datum - z - 3.5) < 1e-5 for z in tips), 'tail projection 3.50 mm below the support flats'
    assert abs((datum - body_top) - (FIXTURE_SUPPORT_Z - FIXTURE_BODY_TOP_Z)) < 1e-4, 'exporter body-to-model datum'
    shift = datum - FIXTURE_SUPPORT_Z
    b = model.BoundingBox()
    bounds = [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]
    want = FIXTURE_BOUNDS[:4] + [FIXTURE_BOUNDS[4] + shift, FIXTURE_BOUNDS[5] + shift]
    assert all(abs(a - e) < 1e-4 for a, e in zip(bounds, want)), ('model envelope', bounds, want)
    return {'status': 'PASS', 'cadquery_version': cq.__version__, 'native_step_sha256': sha(step), 'tail_axes': len(axes),
            'tail_tips': len(tips), 'tail_projection_mm': 3.5, 'rear_support_z_mm': round(datum, 6),
            'board_body_top_z_mm': round(body_top, 6), 'exporter_datum_shift_from_fixture_mm': round(shift, 6),
            'bounds_mm': [round(x, 6) for x in bounds],
            'limits': ('Native exporter datum, not physical stand-off, seating, fit, retention or mating acceptance '
                       '(connector-candidate/README.md)')}


def u3_cadquery(step, model, facts):
    """Run inside the CadQuery environment: the native U3 solids against the model and this board's pose."""
    import cadquery as cq
    original = cq.importers.importStep(str(model)).solids().vals()
    native = cq.importers.importStep(str(step)).solids().vals()
    assert len(original) == len(native) == 29, (len(original), len(native))
    assert all(s.isValid() for s in original + native), 'invalid BREP'
    u3 = facts['U3']
    (x, y), angle = u3['position_mm'], u3['rotation_deg']
    assert u3['layer'] == 'F.Cu' and angle in (0.0, 180.0), (u3['layer'], angle)
    bounds = lambda s: [getattr(s.BoundingBox(), k) for k in ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax')]  # noqa: E731
    z0 = bounds(native[0])[4]
    assert abs(z0 - facts['thickness_mm']) < .01, z0
    for a, b in zip(original, native):
        lo_x, hi_x, lo_y, hi_y, lo_z, hi_z = bounds(a)
        want = ([x + lo_x, x + hi_x, -y + lo_y, -y + hi_y] if angle == 0 else [x - hi_x, x - lo_x, -y - hi_y, -y - lo_y])
        assert all(abs(p - q) < 1e-5 for p, q in zip(bounds(b), want + [z0 + lo_z, z0 + hi_z])), (bounds(b), want)
    for i, solid in enumerate(native[2:26]):
        pin = i + 1 if i < 12 else 36 - i
        px, py = u3['pads_world_mm'][str(pin)]
        b = bounds(solid)
        assert b[0] <= px <= b[1] and b[2] <= -py <= b[3], ('pad mismatch', pin)
    marker, (p1x, p1y) = bounds(native[26]), u3['pads_world_mm']['1']
    assert abs((marker[0] + marker[1]) / 2 - p1x) < 2 and abs((marker[2] + marker[3]) / 2 + p1y) < 2, 'pin-1 marker'
    return {'status': 'PASS', 'cadquery_version': cq.__version__, 'valid_solids': 29, 'pad_overlaps': 24,
            'native_mounting_z_mm': round(z0, 6), 'pose': {'position_mm': [x, y], 'rotation_deg': angle},
            'native_step_sha256': sha(step),
            'limits': 'Datasheet-derived visualization placement only; not mechanical qualification'}


def main(board, out):
    board, out = Path(board).resolve(), Path(out).resolve()
    out.mkdir(parents=True)
    facts = board_facts(board)
    record = json.loads((HERE / 'composition/project-models.json').read_text())
    models = {m['reference']: m for m in record['models']}
    for ref in ('J1', 'U3'):
        target = (board.parent / models[ref]['model_reference'].removeprefix('${KIPRJMOD}/'))
        if facts[ref]['model'] != models[ref]['model_reference'] or sha(target) != models[ref]['candidate']['sha256']:
            raise SystemExit(f'{ref} board model is not the bound file')
    if (facts['J1']['position_mm'], facts['J1']['rotation_deg'], facts['J1']['layer'], facts['thickness_mm']) != (
            [45.0, 55.5], 0.0, 'F.Cu', 1.6):
        raise SystemExit(f"J1 is not at the connector fixture pose: {facts['J1']}")
    j1 = export(board, out / 'J1.step', 'J1', True)
    u3 = export(board, out / 'U3.step', 'U3', False)
    env = {**os.environ, 'UV_OFFLINE': '1'}
    done = subprocess.run([*UV, str(CONNECTOR_CHECK), str(out / 'J1.step')], capture_output=True, text=True, env=env, timeout=900)
    j1['fixture_check_model'] = {'script': 'connector-candidate/check_model.py', 'sha256': sha(CONNECTOR_CHECK),
                                 'rc': done.returncode, 'stdout': done.stdout.strip()[-800:],
                                 'stderr_tail': done.stderr.strip().splitlines()[-1:] if done.returncode else []}
    done = subprocess.run([*UV, str(Path(__file__).resolve()), '--cadquery-j1', str(out / 'J1.step')],
                          capture_output=True, text=True, env=env, timeout=900)
    if done.returncode:
        raise SystemExit(f'J1 CadQuery check failed: {done.stderr[-800:]}')
    j1['check'] = json.loads(done.stdout)
    (out / 'facts.json').write_text(json.dumps(facts, indent=1, sort_keys=True) + '\n')
    done = subprocess.run([*UV, str(Path(__file__).resolve()), '--cadquery-u3', str(out / 'U3.step'),
                           str(HERE.parent / 'neo-m9n-model' / Path(models['U3']['source']['path']).name), str(out / 'facts.json')],
                          capture_output=True, text=True, env=env, timeout=900)
    if done.returncode:
        raise SystemExit(f'U3 CadQuery check failed: {done.stderr[-800:]}')
    u3['check'] = json.loads(done.stdout)
    result = {'schema': 'pod-capture.model-check/1', 'status': 'PASS',
              'board': {'path': board.relative_to(HERE.parents[2]).as_posix() if board.is_relative_to(HERE.parents[2])
                        else str(board), 'sha256': sha(board)}, 'kicad_cli': subprocess.run(
                  ['kicad-cli', 'version'], capture_output=True, text=True).stdout.strip(),
              'record': {'path': 'composition/project-models.json', 'sha256': sha(HERE / 'composition/project-models.json')},
              'J1': j1, 'U3': u3, 'not_bound': record['not_bound'], 'open': record['open']}
    (out / 'model-check.json').write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'board')}, sort_keys=True))


if __name__ == '__main__':
    if sys.argv[1:2] == ['--cadquery-j1']:
        print(json.dumps(j1_cadquery(Path(sys.argv[2]))))
    elif sys.argv[1:2] == ['--cadquery-u3']:
        print(json.dumps(u3_cadquery(Path(sys.argv[2]), Path(sys.argv[3]), json.loads(Path(sys.argv[4]).read_text()))))
    else:
        main(*sys.argv[1:3])
