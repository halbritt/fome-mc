#!/usr/bin/env python3
"""Regenerate the routing fixture (schematic + placed, partly routed PCB).

The fixture is a routing-toolchain integration check, not part of the ECU design.
It exercises what a routing backend has to respect:

    J1.1 /VIN ---- C1 ---- J2.1      Power class (0.5 mm track, 0.3 mm clearance)
    J1.2 GND  ---- C1 ---- J2.2      Power class, plus a GND zone on B.Cu
    J1.3 /SIG_A -- R1 -- /SIG_A_OUT -- J2.3     Default class (0.2 mm / 0.2 mm)
    J1.4 /SIG_B -- R2 -- /SIG_B_OUT -- J2.4     /SIG_B is pre-routed and LOCKED

- Two copper layers with KiCad's stock 2-layer stackup; the Edge.Cuts outline is
  50 x 30 mm.
- A keepout rule area (no tracks, vias or pour on both layers) sits across the
  direct J1 -> J2 path, so every J1 -> J2 net needs pathfinding around it.
- A custom rule in route_demo.kicad_dru raises Power-to-signal clearance to
  0.4 mm, a constraint that only KiCad's own DRC can grade.
- /SIG_B (J1.4 -> R2.1) is routed with locked tracks and two locked vias: the
  designated protected copper. Everything else is unrouted.

Run with the toolchain interpreter (it needs KiCad's pcbnew bindings):

    toolchain/.venv/bin/python toolchain/fixtures/route_demo/generate.py

As with the rc_filter fixture, the schematic comes from the stock KiCad
symbols and is normalised by `kicad-cli sch upgrade --force`; UUIDs are
derived deterministically.
"""
import json
import shutil
import subprocess
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "route_demo"
SYMBOL_DIR = Path("/usr/share/kicad/symbols")
FOOTPRINT_DIR = Path("/usr/share/kicad/footprints")
TEMPLATE_PRO = Path("/usr/share/kicad/template/kicad.kicad_pro")
STACKUP_SOURCE = Path("/usr/share/kicad/template/RaspberryPi-HAT/RaspberryPi-HAT.kicad_pcb")
NS = uuid.UUID("0b8e4f53-1d2a-4c6e-9f87-5a3c2d1e0f42")

HEADER = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
R0805 = "Resistor_SMD:R_0805_2012Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"

# ref -> (lib, symbol, value, footprint, schematic x, y)
SYMBOLS = {
    "J1": ("Connector_Generic", "Conn_01x04", "Conn_01x04", HEADER, 50.8, 60.96),
    "J2": ("Connector_Generic", "Conn_01x04", "Conn_01x04", HEADER, 127.0, 60.96),
    "C1": ("Device", "C", "1u", C0805, 76.2, 50.8),
    "R1": ("Device", "R", "33", R0805, 88.9, 50.8),
    "R2": ("Device", "R", "33", R0805, 101.6, 50.8),
}
POWER = {"#PWR01": ("power", "GND"), "#PWR02": ("power", "GND"), "#PWR03": ("power", "GND"),
         "#FLG01": ("power", "PWR_FLAG"), "#FLG02": ("power", "PWR_FLAG")}

PIN_OFFSETS = {  # schematic coordinates (y down), rotation 0
    ("Device", "R"): {"1": (0, -3.81), "2": (0, 3.81)},
    ("Device", "C"): {"1": (0, -3.81), "2": (0, 3.81)},
    ("Connector_Generic", "Conn_01x04"): {"1": (-5.08, -2.54), "2": (-5.08, 0),
                                          "3": (-5.08, 2.54), "4": (-5.08, 5.08)},
    ("power", "GND"): {"1": (0, 0)},
    ("power", "PWR_FLAG"): {"1": (0, 0)},
}

# (ref, pin) -> net. "GND" pins end in a GND power symbol.
CONNECTIONS = {
    ("J1", "1"): "VIN", ("J1", "2"): "GND", ("J1", "3"): "SIG_A", ("J1", "4"): "SIG_B",
    ("J2", "1"): "VIN", ("J2", "2"): "GND", ("J2", "3"): "SIG_A_OUT", ("J2", "4"): "SIG_B_OUT",
    ("C1", "1"): "VIN", ("C1", "2"): "GND",
    ("R1", "1"): "SIG_A", ("R1", "2"): "SIG_A_OUT",
    ("R2", "1"): "SIG_B", ("R2", "2"): "SIG_B_OUT",
}

NETCLASSES = {
    "Default": {"clearance": 0.2, "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3},
    "Power": {"clearance": 0.3, "track_width": 0.5, "via_diameter": 0.8, "via_drill": 0.4},
}
NETCLASS_PATTERNS = [("/VIN", "Power"), ("GND", "Power")]

DRU = """(version 1)
# Fixture rule: Power nets keep 0.4 mm from everything that is not Power.
(rule "power_to_signal_clearance"
\t(constraint clearance (min 0.4mm))
\t(condition "A.NetClass == 'Power' && B.NetClass != 'Power'"))
"""


def uid(tag):
    return str(uuid.uuid5(NS, tag))


def fmt(v):
    return f"{v:g}"


def extract_symbol(lib, name):
    text = (SYMBOL_DIR / f"{lib}.kicad_sym").read_text()
    start = text.index(f'\n\t(symbol "{name}"') + 1
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1].replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    raise ValueError(f"unterminated symbol {lib}:{name}")


def wire(a, b):
    return (f'\t(wire (pts (xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])}))\n'
            f'\t\t(stroke (width 0) (type default)) (uuid "{uid(f"wire{a}{b}")}"))\n')


def label(text, at):
    return (f'\t(label "{text}" (at {fmt(at[0])} {fmt(at[1])} 0)\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
            f'\t\t(uuid "{uid(f"label{text}{at}")}"))\n')


def symbol_block(ref, lib, name, value, footprint, x, y, root_uuid):
    power = ref.startswith("#")
    pins = "".join(f'\t\t(pin "{n}" (uuid "{uid(f"pin{ref}{n}")}"))\n' for n in PIN_OFFSETS[(lib, name)])
    hidden = " (hide yes)" if power else ""
    return (
        f'\t(symbol (lib_id "{lib}:{name}") (at {fmt(x)} {fmt(y)} 0) (unit 1)\n'
        f'\t\t(exclude_from_sim yes) (in_bom {"no" if power else "yes"})'
        f' (on_board {"no" if power else "yes"}) (dnp no)\n'
        f'\t\t(uuid "{uid(f"sym{ref}")}")\n'
        f'\t\t(property "Reference" "{ref}" (at {fmt(x + 2.54)} {fmt(y - 1.27)} 0)'
        f' (effects (font (size 1.27 1.27)) (justify left){hidden}))\n'
        f'\t\t(property "Value" "{value}" (at {fmt(x + 2.54)} {fmt(y + 1.27)} 0)'
        f' (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'\t\t(property "Footprint" "{footprint}" (at {fmt(x)} {fmt(y)} 0)'
        f' (effects (font (size 1.27 1.27)) (hide yes)))\n'
        f'\t\t(property "Datasheet" "~" (at {fmt(x)} {fmt(y)} 0)'
        f' (effects (font (size 1.27 1.27)) (hide yes)))\n'
        f'{pins}'
        f'\t\t(instances (project "{NAME}" (path "/{root_uuid}" (reference "{ref}") (unit 1))))\n'
        f'\t)\n'
    )


def write_schematic():
    root_uuid = uid("root")
    libs = sorted({(s[0], s[1]) for s in SYMBOLS.values()} | set(POWER.values()))
    lib_symbols = "".join("\t\t" + extract_symbol(lib, name).replace("\n", "\n\t") + "\n"
                          for lib, name in libs)
    body, symbols, gnd = "", "", iter(["#PWR01", "#PWR02", "#PWR03"])
    gnd_points = []
    for (ref, number), net in CONNECTIONS.items():
        lib, name, _, _, x, y = SYMBOLS[ref]
        dx, dy = PIN_OFFSETS[(lib, name)][number]
        p = (round(x + dx, 2), round(y + dy, 2))
        # Connectors stub to the left, two-terminal parts up (pin 1) or down (pin 2).
        step = (-2.54, 0) if lib == "Connector_Generic" else ((0, -2.54) if number == "1" else (0, 2.54))
        end = (round(p[0] + step[0], 2), round(p[1] + step[1], 2))
        body += wire(p, end)
        if net == "GND":
            if ref == "C1":
                gnd_points.append(end)
            ref_g = next(gnd)
            symbols += symbol_block(ref_g, "power", "GND", "GND", "", end[0], end[1], root_uuid)
        else:
            body += label(net, end)
    # PWR_FLAGs: one on the GND point of C1, one on a VIN label stub.
    symbols += symbol_block("#FLG01", "power", "PWR_FLAG", "PWR_FLAG", "", *gnd_points[0], root_uuid)
    vin = (76.2, 40.64)
    body += wire((76.2, 44.45), vin)
    symbols += symbol_block("#FLG02", "power", "PWR_FLAG", "PWR_FLAG", "", *vin, root_uuid)
    for ref, (lib, name, value, footprint, x, y) in SYMBOLS.items():
        symbols += symbol_block(ref, lib, name, value, footprint, x, y, root_uuid)
    text = (
        '(kicad_sch (version 20231120) (generator "fome_mc_route_fixture") (generator_version "10.0")\n'
        f'\t(uuid "{root_uuid}")\n'
        '\t(paper "A5")\n'
        '\t(title_block (title "Routing fixture (not ECU design)") (rev "1"))\n'
        f'\t(lib_symbols\n{lib_symbols}\t)\n'
        f'{body}{symbols}'
        '\t(sheet_instances (path "/" (page "1")))\n'
        ')\n'
    )
    path = HERE / f"{NAME}.kicad_sch"
    path.write_text(text)
    subprocess.run(["kicad-cli", "sch", "upgrade", "--force", str(path)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_project():
    pro = json.loads(TEMPLATE_PRO.read_text())
    pro["meta"]["filename"] = f"{NAME}.kicad_pro"
    pro["schematic"] = {"top_level_sheets": [
        {"filename": f"{NAME}.kicad_sch", "name": NAME, "uuid": uid("root")}]}
    pro["sheets"] = [[uid("root"), "Root"]]
    base = {"bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2, "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
            "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
            "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6}
    classes = []
    for name, values in NETCLASSES.items():
        c = dict(base)
        c.update(values, name=name)
        classes.append(c)
    pro["net_settings"]["classes"] = classes
    pro["net_settings"]["netclass_patterns"] = [{"netclass": c, "pattern": p} for p, c in NETCLASS_PATTERNS]
    # The stock template carries net_settings schema 0, which KiCad 10 migrates by
    # dropping the pattern assignments; write the current schema.
    pro["net_settings"].update({"meta": {"version": 3}, "net_colors": None, "netclass_assignments": None})
    rules = pro["board"]["design_settings"]["rules"]
    rules.update({"min_clearance": 0.15, "min_track_width": 0.15, "min_copper_edge_clearance": 0.3,
                  "min_via_diameter": 0.5, "min_through_hole_diameter": 0.25, "min_via_annular_width": 0.1,
                  "min_hole_clearance": 0.25})
    (HERE / f"{NAME}.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")
    (HERE / f"{NAME}.kicad_dru").write_text(DRU)
    sym = ["(sym_lib_table", "  (version 7)"]
    for lib in sorted({s[0] for s in SYMBOLS.values()} | {"power"}):
        sym.append(f'  (lib (name "{lib}")(type "KiCad")(uri "${{KICAD10_SYMBOL_DIR}}/{lib}.kicad_sym")'
                   '(options "")(descr ""))')
    (HERE / "sym-lib-table").write_text("\n".join(sym + [")"]) + "\n")
    fp = ["(fp_lib_table", "  (version 7)"]
    for lib in sorted({s[3].split(":")[0] for s in SYMBOLS.values()}):
        fp.append(f'  (lib (name "{lib}")(type "KiCad")(uri "${{KICAD10_FOOTPRINT_DIR}}/{lib}.pretty")'
                  '(options "")(descr ""))')
    (HERE / "fp-lib-table").write_text("\n".join(fp + [")"]) + "\n")


def write_pcb():
    import pcbnew

    mm = pcbnew.FromMM
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)

    def pt(x, y):
        return pcbnew.VECTOR2I(mm(x), mm(y))

    nets = {}
    for net in sorted(set(CONNECTIONS.values())):
        full = "GND" if net == "GND" else f"/{net}"
        nets[net] = pcbnew.NETINFO_ITEM(board, full)
        board.Add(nets[net])

    placements = {"J1": (104, 106, 0), "J2": (146, 106, 0), "C1": (110, 104, 0),
                  "R1": (125, 103, 0), "R2": (125, 126, 0)}
    pads = {}
    for ref, (x, y, angle) in placements.items():
        _, _, value, footprint, _, _ = SYMBOLS[ref]
        lib, fp_name = footprint.split(":")
        fp = pcbnew.FootprintLoad(str(FOOTPRINT_DIR / f"{lib}.pretty"), fp_name)
        fp.SetFPID(pcbnew.LIB_ID(lib, fp_name))
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetPath(pcbnew.KIID_PATH(f"/{uid(f'sym{ref}')}"))
        fp.SetSheetname("/")
        fp.SetSheetfile(f"{NAME}.kicad_sch")
        board.Add(fp)
        fp.SetPosition(pt(x, y))
        fp.SetOrientationDegrees(angle)
        for (r, number), net in CONNECTIONS.items():
            if r == ref:
                pad = fp.FindPadByNumber(number)
                pad.SetNet(nets[net])
                pads[(ref, number)] = pad.GetPosition()

    corners = [(100, 100), (150, 100), (150, 130), (100, 130)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pt(*a))
        seg.SetEnd(pt(*b))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.1))
        board.Add(seg)

    copper = pcbnew.LSET()
    copper.AddLayer(pcbnew.F_Cu)
    copper.AddLayer(pcbnew.B_Cu)

    keepout = pcbnew.ZONE(board)
    keepout.SetIsRuleArea(True)
    keepout.SetLayerSet(copper)
    keepout.SetDoNotAllowTracks(True)
    keepout.SetDoNotAllowVias(True)
    keepout.SetDoNotAllowZoneFills(True)
    keepout.SetDoNotAllowPads(False)
    keepout.SetDoNotAllowFootprints(False)
    keepout.SetZoneName("route_keepout")
    outline = keepout.Outline()
    outline.NewOutline()
    for x, y in [(119, 105), (131, 105), (131, 122), (119, 122)]:
        outline.Append(mm(x), mm(y))
    board.Add(keepout)

    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(nets["GND"])
    zone.SetZoneName("GND_B")
    zone.SetLocalClearance(mm(0.3))
    zone.SetMinThickness(mm(0.25))
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in [(100.5, 100.5), (149.5, 100.5), (149.5, 129.5), (100.5, 129.5)]:
        outline.Append(mm(x), mm(y))
    board.Add(zone)

    # Protected copper: /SIG_B from J1.4 to R2.1, locked, through two vias.
    w = mm(NETCLASSES["Default"]["track_width"])
    path_f1 = [pads[("J1", "4")], pt(108, 113.62), pt(116, 121.62)]
    path_b = [pt(116, 121.62), pt(120.38, 126), pt(121.5, 126)]
    path_f2 = [pt(121.5, 126), pads[("R2", "1")]]
    for layer, path in ((pcbnew.F_Cu, path_f1), (pcbnew.B_Cu, path_b), (pcbnew.F_Cu, path_f2)):
        for a, b in zip(path, path[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(a)
            t.SetEnd(b)
            t.SetWidth(w)
            t.SetLayer(layer)
            t.SetNet(nets["SIG_B"])
            t.SetLocked(True)
            board.Add(t)
    for at in (pt(116, 121.62), pt(121.5, 126)):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(at)
        via.SetWidth(mm(NETCLASSES["Default"]["via_diameter"]))
        via.SetDrill(mm(NETCLASSES["Default"]["via_drill"]))
        via.SetNet(nets["SIG_B"])
        via.SetLocked(True)
        board.Add(via)

    path = HERE / f"{NAME}.kicad_pcb"
    pcbnew.SaveBoard(str(path), board)
    write_project()  # SaveBoard writes its own project file; ours is authoritative
    # The SWIG API does not expose the stackup; take KiCad's stock 2-layer stackup
    # and let kicad-cli normalise the file.
    text = path.read_text()
    text = text.replace("\n\t(setup\n", "\n\t(setup\n\t\t" + stock_stackup() + "\n", 1)
    path.write_text(text)
    subprocess.run(["kicad-cli", "pcb", "upgrade", "--force", str(path)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Fill the zone with the full project rules (net-class patterns and the
    # custom .kicad_dru rule), which the bare pcbnew board above did not know.
    report = HERE / "generate-drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--save-board", "--format", "json",
                    "-o", str(report), str(path)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report.unlink()


def stock_stackup():
    text = STACKUP_SOURCE.read_text()
    start = text.index("(stackup")
    depth = 0
    for i in range(start, len(text)):
        depth += {"(": 1, ")": -1}.get(text[i], 0)
        if depth == 0:
            return text[start:i + 1]
    raise ValueError("unterminated stackup")


def main():
    for stale in HERE.glob(f"{NAME}.kicad_*"):
        stale.unlink()
    shutil.rmtree(HERE / f"{NAME}-backups", ignore_errors=True)
    write_project()
    write_schematic()
    write_pcb()
    for leftover in [HERE / f"{NAME}.kicad_prl", HERE / "fp-info-cache"]:
        leftover.unlink(missing_ok=True)
    print("fixture written to", HERE)


if __name__ == "__main__":
    main()
