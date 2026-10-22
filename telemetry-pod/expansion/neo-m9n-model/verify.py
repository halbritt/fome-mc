"""Verify retained visual STEP independently of its authoring constants (CadQuery 2.8)."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / 'NEO-M9N-00B_visualization-only_datasheet-derived_not-manufacturer-mechanical-qualification.step'


def bounds(solid):
    b = solid.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]


def close(actual, expected):
    assert len(actual) == len(expected)
    assert all(abs(a - e) < 1e-5 for a, e in zip(actual, expected)), (actual, expected)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        regenerated = Path(tmp) / 'model.step'
        subprocess.run([sys.executable, '-B', str(ROOT / 'neo_m9n_vis_step.py'), str(regenerated)], check=True)
        assert regenerated.read_bytes() == MODEL.read_bytes(), 'generator reproducibility'
    original = cq.importers.importStep(str(MODEL)).solids().vals()
    native = cq.importers.importStep(str(ROOT / 'evidence/native-u3.step')).solids().vals()
    assert len(original) == len(native) == 29
    assert all(s.isValid() for s in original + native), 'invalid BREP'
    # Directly from R08 Table 20, independently specified, not imported from generator.
    close(bounds(original[0]), [-6.1, 6.1, -8, 8, 0, .82])
    close(bounds(original[1]), [-6.1, 6.1, -8, 8, .82, 2.4])
    pose = json.loads((ROOT / 'evidence/native-pose.json').read_text())
    assert pose['position_mm'] == [71.5, 35.0] and pose['angle_degrees'] == 180
    assert pose['board_thickness_mm'] == 1.6 and pose['layer'] == 'F.Cu'
    # STEP export uses Y-up negation of board-screen Y. Native placement is 180 degrees.
    # Z offset is exporter-specific and is not an assertion about solder stand-off.
    z0 = bounds(native[0])[4]
    assert abs(z0 - 1.6) < .01
    for a, b in zip(original, native):
        lo_x, hi_x, lo_y, hi_y, lo_z, hi_z = bounds(a)
        close(bounds(b), [71.5-hi_x, 71.5-lo_x, -35-hi_y, -35-lo_y, z0+lo_z, z0+hi_z])
    # Every castellation visual overlaps its native pad centre in XY; numbering must align.
    for i, solid in enumerate(native[2:26]):
        pin = i + 1 if i < 12 else 36 - i
        x, board_y = pose['pads_world_mm'][str(pin)]
        b = bounds(solid)
        assert b[0] <= x <= b[1] and b[2] <= -board_y <= b[3], ('pad mismatch', pin)
    # Visualization marker belongs to pin-1 corner, not opposite corner after rotation.
    marker = bounds(native[26])
    p1 = pose['pads_world_mm']['1']
    assert abs((marker[0]+marker[1])/2-p1[0]) < 2
    assert abs((marker[2]+marker[3])/2+p1[1]) < 2
    result = {'status': 'PASS', 'cadquery': cq.__version__, 'valid_solids': 29,
              'pad_overlaps': 24, 'nominal_body_xyz_mm': [12.2,16.0,2.4],
              'native_mounting_z_mm': round(z0,6), 'model_sha256': hashlib.sha256(MODEL.read_bytes()).hexdigest(),
              'limits': 'Visual model only; not manufacturer CAD, collision envelope, solder or mechanical qualification.'}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
