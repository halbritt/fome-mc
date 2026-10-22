"""Author the U3 NEO-M9N-00B VISUALIZATION model as STEP (AP214) for native KiCad GLB export.

visualization-only, datasheet-derived, not manufacturer/mechanical qualification.

Same geometry as tools/neo_m9n_vis_model.py (iter8s WRL): u-blox UBX-19014285 R08
pp. 16-17, Figure 5 and Table 20; nominal 16.0 x 12.2 x 2.4 mm, pin 1 at footprint pad 1,
mounting plane Z=0, translucent residual-tab envelope. The solid list is derived from the
WRL generator constants (imported, not re-typed); units here are millimetres (the WRL
used 0.1 inch). Stdlib only: each box is a MANIFOLD_SOLID_BREP written directly.

Why STEP: this kicad-cli 10.0.7 `pcb export glb` reads VRML through OpenCASCADE and fails
(readVRML() failed) for every .wrl, including KiCad's own VRML export; STEP loads.

usage: python3 neo_m9n_vis_step.py OUT.step
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import neo_m9n_vis_model as wrl  # noqa: E402

LABEL = wrl.LABEL
NAME = 'NEO-M9N-00B visualization-only datasheet-derived not-manufacturer-mechanical-qualification'
# (vertex index quad, outward normal) for a box whose vertex i has bits x=i&1, y=(i>>1)&1, z=(i>>2)&1.
FACES = [((0, 2, 3, 1), (0, 0, -1)), ((4, 5, 7, 6), (0, 0, 1)),
         ((0, 1, 5, 4), (0, -1, 0)), ((2, 6, 7, 3), (0, 1, 0)),
         ((0, 4, 6, 2), (-1, 0, 0)), ((1, 3, 7, 5), (1, 0, 0))]


def solids():
    """Boxes (centre x,y,z, size x,y,z mm, rgb, transparency) in the WRL model frame, from the WRL generator."""
    out = []
    for text in wrl.build():
        t = text.replace('{', ' ').replace('}', ' ').replace('[', ' ').replace(']', ' ').split()
        tr = [float(v) for v in t[t.index('translation') + 1:][:3]]
        rgb = [float(v) for v in t[t.index('diffuseColor') + 1:][:3]]
        transp = float(t[t.index('transparency') + 1])
        size = [float(v) for v in t[t.index('size') + 1:][:3]]
        # WRL values are 6-decimal 0.1-inch units; snap the mm to 0.1 um to drop that rounding noise.
        out.append(([round(v / wrl.U, 4) for v in tr], [round(v / wrl.U, 4) for v in size], rgb, transp))
    return out


class Step:
    def __init__(self):
        self.lines = []

    def add(self, body):
        self.lines.append(body)
        return len(self.lines)

    def ref(self, body):
        return f'#{self.add(body)}'


def num(v):
    """STEP real: always a plain decimal (no exponent; '1e-06' is not a valid STEP real), 0.1 um grid."""
    return f'{round(v, 4) + 0.0:.4f}'.rstrip('0') if round(v, 4) % 1 else f'{round(v, 4) + 0.0:.1f}'


def vec(p):
    return ','.join(num(c) for c in p)


def build(out):
    s = Step()
    pt = lambda p: s.ref(f"CARTESIAN_POINT('',({vec(p)}))")
    di = lambda d: s.ref(f"DIRECTION('',({vec(d)}))")
    app = s.ref("APPLICATION_CONTEXT('automotive design')")
    s.ref(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{app})")
    pctx = s.ref(f"PRODUCT_CONTEXT('',{app},'mechanical')")
    prod = s.ref(f"PRODUCT('U3','{NAME}','{LABEL}',({pctx}))")
    form = s.ref(f"PRODUCT_DEFINITION_FORMATION('','',{prod})")
    dctx = s.ref(f"PRODUCT_DEFINITION_CONTEXT('part definition',{app},'design')")
    pdef = s.ref(f"PRODUCT_DEFINITION('design','',{form},{dctx})")
    pds = s.ref(f"PRODUCT_DEFINITION_SHAPE('','',{pdef})")
    lu = s.ref("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
    au = s.ref("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
    su = s.ref("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
    unc = s.ref(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-5),{lu},'distance_accuracy_value','')")
    gctx = s.ref(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc}))"
                 f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({lu},{au},{su}))REPRESENTATION_CONTEXT('',''))")
    wp = s.ref(f"AXIS2_PLACEMENT_3D('',{pt((0, 0, 0))},{di((0, 0, 1))},{di((1, 0, 0))})")
    breps, styled = [], []
    for n, (c, size, rgb, transp) in enumerate(solids(), 1):
        lo = [c[i] - size[i] / 2 for i in range(3)]
        hi = [c[i] + size[i] / 2 for i in range(3)]
        verts = [s.ref(f"VERTEX_POINT('',{pt([(hi if (i >> b) & 1 else lo)[b] for b in range(3)])})")
                 for i in range(8)]
        edges = {}

        def edge(a, b):
            key = (min(a, b), max(a, b))
            if key not in edges:
                a_, b_ = key
                pa = [(hi if (a_ >> k) & 1 else lo)[k] for k in range(3)]
                pb = [(hi if (b_ >> k) & 1 else lo)[k] for k in range(3)]
                length = sum((pb[k] - pa[k]) ** 2 for k in range(3)) ** 0.5
                d = [(pb[k] - pa[k]) / length for k in range(3)]
                line = s.ref(f"LINE('',{pt(pa)},{s.ref(f'VECTOR({chr(39)}{chr(39)},{di(d)},{num(length)})')})")
                edges[key] = s.ref(f"EDGE_CURVE('',{verts[a_]},{verts[b_]},{line},.T.)")
            return edges[key], a < b

        faces = []
        for quad, normal in FACES:
            oriented = []
            for k in range(4):
                a, b = quad[k], quad[(k + 1) % 4]
                ec, fwd = edge(a, b)
                oriented.append(s.ref(f"ORIENTED_EDGE('',*,*,{ec},{'.T.' if fwd else '.F.'})"))
            loop = s.ref(f"EDGE_LOOP('',({','.join(oriented)}))")
            bound = s.ref(f"FACE_OUTER_BOUND('',{loop},.T.)")
            origin = [(hi if (quad[0] >> k) & 1 else lo)[k] for k in range(3)]
            p1 = [(hi if (quad[1] >> k) & 1 else lo)[k] for k in range(3)]
            ref = [p1[k] - origin[k] for k in range(3)]
            ln = sum(v * v for v in ref) ** 0.5
            plane = s.ref(f"PLANE('',{s.ref(f'AXIS2_PLACEMENT_3D({chr(39)}{chr(39)},{pt(origin)},{di(normal)},{di([v / ln for v in ref])})')})")
            faces.append(s.ref(f"ADVANCED_FACE('',({bound}),{plane},.T.)"))
        shell = s.ref(f"CLOSED_SHELL('',({','.join(faces)}))")
        brep = s.ref(f"MANIFOLD_SOLID_BREP('U3_solid_{n}',{shell})")
        breps.append(brep)
        col = s.ref(f"COLOUR_RGB('',{vec(rgb)})")
        fill = s.ref(f"FILL_AREA_STYLE_COLOUR('',{col})")
        fas = s.ref(f"FILL_AREA_STYLE('',({fill}))")
        ssf = s.ref(f"SURFACE_STYLE_FILL_AREA({fas})")
        sides = [ssf]
        if transp:
            sides.append(s.ref(f"SURFACE_STYLE_RENDERING_WITH_PROPERTIES(.NORMAL_SHADING.,{col},"
                               f"({s.ref(f'SURFACE_STYLE_TRANSPARENT({num(transp)})')}))"))
        sse = s.ref(f"SURFACE_SIDE_STYLE('',({','.join(sides)}))")
        ssu = s.ref(f"SURFACE_STYLE_USAGE(.BOTH.,{sse})")
        psa = s.ref(f"PRESENTATION_STYLE_ASSIGNMENT(({ssu}))")
        styled.append(s.ref(f"STYLED_ITEM('',({psa}),{brep})"))
    rep = s.ref(f"ADVANCED_BREP_SHAPE_REPRESENTATION('',({wp},{','.join(breps)}),{gctx})")
    s.ref(f"SHAPE_DEFINITION_REPRESENTATION({pds},{rep})")
    header = ("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('" + LABEL + "; UBX-19014285 R08 pp. 16-17'),'2;1');\n"
              "FILE_NAME('NEO-M9N-00B_visualization-only.step','2026-10-21T00:00:00',('agent-ee'),(''),"
              "'neo_m9n_vis_step.py','neo_m9n_vis_step.py','');\n"
              "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n")
    body = ''.join(f'#{i}={line};\n' for i, line in enumerate(s.lines, 1))
    Path(out).write_text(header + body + 'ENDSEC;\nEND-ISO-10303-21;\n')


if __name__ == '__main__':
    build(sys.argv[1])
