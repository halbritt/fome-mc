"""Author the U3 NEO-M9N-00B VISUALIZATION model (VRML 2.0) from u-blox UBX-19014285 R08 pp. 16-17.

visualization-only, datasheet-derived, not manufacturer/mechanical qualification.

Frame: KiCad footprint RF_GPS:ublox_NEO local frame, model units 0.1 inch (KiCad
VRML convention, 1 unit = 2.54 mm). Model X = footprint X, model Y = -footprint Y,
Z = 0 on the board top surface (mounting plane), +Z away from the board.
Datasheet Table 20 (typical): A 16.0 (along footprint Y, the pin rows),
B 12.2 (along X), C 2.4 total height, H 0.82 module PCB thickness,
K 0.8 castellation width, M 0.9 castellation depth, P* 0..0.5 residual
de-paneling tabs on either short side (not both). Pin 1 = footprint pad 1 at
(-6.0, -7.0) footprint mm. The shield is drawn as the full A x B outline (its
inset is not dimensioned in the datasheet). The pin-1 dot is a visualization
cue, not a datasheet marking. The tab envelope is drawn translucent on both short
sides because the actual side is unspecified.

usage: python3 neo_m9n_vis_model.py OUT.wrl
"""
import sys

A, B, C, H = 16.0, 12.2, 2.4, 0.82
A_MAX, B_MAX, C_MAX, P_MAX = 16.1, 12.3, 2.6, 0.5
K, M = 0.8, 0.9
# Footprint pad centres along Y (footprint mm), left column pins 1..12; right 24..13.
ROWS = [-7.0, -5.9, -4.8, -3.7, -2.6, -1.5, -0.4, 2.6, 3.7, 4.8, 5.9, 7.0]
U = 1 / 2.54
LABEL = 'visualization-only, datasheet-derived, not manufacturer/mechanical qualification'


def box(cx, cy, cz, sx, sy, sz, colour, transparency=0.0):
    """Centre and size in mm (model frame); emitted in 0.1-inch units."""
    return (f'Transform {{ translation {cx*U:.6f} {cy*U:.6f} {cz*U:.6f} children [ Shape {{\n'
            f'  appearance Appearance {{ material Material {{ diffuseColor {colour} '
            f'transparency {transparency} }} }}\n'
            f'  geometry Box {{ size {sx*U:.6f} {sy*U:.6f} {sz*U:.6f} }} }} ] }}\n')


def build():
    shapes = []
    # Module PCB substrate (H) and shield to total height C, nominal A x B.
    shapes.append(box(0, 0, H / 2, B, A, H, '0.12 0.35 0.15'))
    shapes.append(box(0, 0, H + (C - H) / 2, B, A, C - H, '0.75 0.75 0.78'))
    # Castellated contacts: K wide, M deep from each long edge, substrate height.
    for side in (-1, 1):
        for y in ROWS:
            shapes.append(box(side * (B / 2 - M / 2), -y, H / 2, M + 0.02, K, H + 0.02, '0.85 0.65 0.2'))
    # Pin-1 visualization dot on the shield top above footprint pad 1 (x -6.0, y -7.0).
    shapes.append(box(-4.6, 6.6, C + 0.025, 0.8, 0.8, 0.05, '0.05 0.05 0.05'))
    # Residual tab envelope P* (0..0.5 mm) beyond each short edge, substrate height, translucent.
    for side in (-1, 1):
        shapes.append(box(0, side * (A / 2 + P_MAX / 2), H / 2, B, P_MAX, H, '0.9 0.2 0.2', 0.6))
    return shapes


def main(out):
    header = ('#VRML V2.0 utf8\n'
              f'# U3 NEO-M9N-00B: {LABEL}\n'
              '# Source: u-blox NEO-M9N-00B Data sheet UBX-19014285 R08 (09-Oct-2025), '
              'section 6 Mechanical specifications, pp. 16-17, Figure 5 and Table 20.\n'
              f'# Nominal {A} x {B} x {C} mm; maximum {A_MAX} x {B_MAX} x {C_MAX} mm; '
              f'residual de-paneling tabs 0..{P_MAX} mm on either short side (not both).\n'
              '# Not an exact or manufacturer model. Do not use for mechanical qualification.\n'
              f'WorldInfo {{ title "NEO-M9N-00B {LABEL}" info [ "UBX-19014285 R08 pp. 16-17" '
              f'"nominal {A}x{B}x{C} mm" "max {A_MAX}x{B_MAX}x{C_MAX} mm" "tabs 0..{P_MAX} mm one short side" ] }}\n')
    with open(out, 'w') as handle:
        handle.write(header + ''.join(build()))


if __name__ == '__main__':
    main(sys.argv[1])
