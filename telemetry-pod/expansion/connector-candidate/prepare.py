"""Emit a project-local footprint from TE drawing 776163 K1, sheets 1/2."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = 'AMPSEAL_35_1-776163-1'


def footprint():
    lines = [f'(footprint "{NAME}"', ' (version 20241229)',
             ' (generator "pod_connector")', ' (layer "F.Cu")',
             ' (descr "TE 776163 K1; mating side +Y; recommended PCB edge Y=9.5 mm")',
             ' (attr through_hole)',
             ' (fp_text reference "REF**" (at 0 -8) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
             f' (fp_text value "{NAME}" (at 0 -10) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
             ' (fp_rect (start -38.45 -6.05) (end 38.45 31.85) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))',
             ' (fp_rect (start -38.95 -6.55) (end 38.95 32.35) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
             ' (fp_line (start -38.45 9.5) (end 38.45 9.5) (stroke (width 0.1) (type dash)) (layer "Dwgs.User"))',
             ' (fp_text user "PCB EDGE / MATE +Y" (at 0 11.5) (layer "Dwgs.User") (effects (font (size 1 1) (thickness 0.15))))',
             ' (fp_line (start -24 -5.5) (end -24 -2.5) (stroke (width 0.15) (type default)) (layer "F.SilkS"))',
             ' (fp_line (start -24 -5.5) (end -21 -5.5) (stroke (width 0.15) (type default)) (layer "F.SilkS"))']
    for start, count, x0, y in [(1, 12, -22, -4), (13, 11, -20, 0), (24, 12, -22, 4)]:
        for i in range(count):
            n = start + i
            shape = 'rect' if n == 1 else 'circle'
            lines.append(f' (pad "{n}" thru_hole {shape} (at {x0+4*i} {y}) (size 2.4 2.4) (drill 1.75) (layers "*.Cu" "*.Mask"))')
    for x in [-28.5, 28.5]:
        lines.append(f' (pad "" np_thru_hole circle (at {x} 0.5) (size 2.85 2.85) (drill 2.85) (layers "*.Cu" "*.Mask"))')
    lines.append(' (model "${KIPRJMOD}/inputs/models/c-1-776163-1-t-3d.stp" (offset (xyz 0 -31.8 11.72)) (scale (xyz 1 1 1)) (rotate (xyz -90 0 0)))')
    lines.append(')')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    dest = ROOT / 'PodConnector.pretty' / f'{NAME}.kicad_mod'
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(footprint())
