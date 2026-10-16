#!/usr/bin/env python3
"""Regenerate the RC low-pass toolchain fixture (schematic + PCB).

The fixture is a toolchain integration check, not part of the ECU design:

    J1.1 (IN) --R1 10k-- OUT (J1.2) --C1 100n-- GND (J1.3)

Run with the toolchain interpreter (it needs KiCad's pcbnew bindings):

    toolchain/.venv/bin/python toolchain/fixtures/rc_filter/generate.py

The schematic is written from the stock KiCad 10 symbol libraries and then
normalised by `kicad-cli sch upgrade --force`, so KiCad itself has the last
word on the file format. The PCB is built through the pcbnew API with each
footprint linked to its schematic symbol (KIID path), routed, and given a
filled GND zone on B.Cu so zone fill state is exercised by the checks.
UUIDs are derived deterministically so regeneration is reproducible.
"""
import json
import shutil
import subprocess
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "rc_filter"
SYMBOL_DIR = Path("/usr/share/kicad/symbols")
FOOTPRINT_DIR = Path("/usr/share/kicad/footprints")
TEMPLATE_PRO = Path("/usr/share/kicad/template/kicad.kicad_pro")
NS = uuid.UUID("6f1c2a9e-4d55-4b3a-9a43-0c1f6e7d2b10")


def uid(tag):
    return str(uuid.uuid5(NS, tag))


def extract_symbol(lib, name):
    """Return the top-level `(symbol "name" ...)` block from a .kicad_sym file."""
    text = (SYMBOL_DIR / f"{lib}.kicad_sym").read_text()
    start = text.index(f'\n\t(symbol "{name}"') + 1
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                block = text[start:i + 1]
                return block.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    raise ValueError(f"unterminated symbol {lib}:{name}")


# Symbol placements: ref -> (lib, name, value, footprint, x, y, angle, exclude_from_sim)
SYMBOLS = {
    "J1": ("Connector_Generic", "Conn_01x03", "Conn_01x03",
           "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", 60.96, 63.5, 180, True),
    "R1": ("Device", "R", "10k", "Resistor_SMD:R_0805_2012Metric", 86.36, 63.5, 0, False),
    "C1": ("Device", "C", "100n", "Capacitor_SMD:C_0805_2012Metric", 101.6, 63.5, 0, False),
    "#PWR01": ("power", "GND", "GND", "", 101.6, 71.12, 0, False),
    "#PWR02": ("power", "GND", "GND", "", 71.12, 60.96, 0, False),
    "#FLG01": ("power", "PWR_FLAG", "PWR_FLAG", "", 109.22, 71.12, 0, False),
}

# Pin connection points relative to the symbol origin (schematic coordinates,
# y down, rotation 0) for the stock symbols used here.
PIN_OFFSETS = {
    ("Device", "R"): {"1": (0, -3.81), "2": (0, 3.81)},
    ("Device", "C"): {"1": (0, -3.81), "2": (0, 3.81)},
    ("Connector_Generic", "Conn_01x03"): {"1": (-5.08, -2.54), "2": (-5.08, 0), "3": (-5.08, 2.54)},
    ("power", "GND"): {"1": (0, 0)},
    ("power", "PWR_FLAG"): {"1": (0, 0)},
}


def pin(ref, number):
    lib, name, _, _, x, y, angle, _ = SYMBOLS[ref]
    dx, dy = PIN_OFFSETS[(lib, name)][number]
    if angle == 180:
        dx, dy = -dx, -dy
    return (round(x + dx, 2), round(y + dy, 2))


def fmt(v):
    return f"{v:g}"


def wire(a, b):
    return (f'\t(wire (pts (xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])}))\n'
            f'\t\t(stroke (width 0) (type default)) (uuid "{uid(f"wire{a}{b}")}"))\n')


def label(text, at, angle=0):
    return (f'\t(label "{text}" (at {fmt(at[0])} {fmt(at[1])} {angle})\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
            f'\t\t(uuid "{uid(f"label{text}{at}")}"))\n')


def symbol_instance(ref, root_uuid):
    lib, name, value, footprint, x, y, angle, no_sim = SYMBOLS[ref]
    sym_uuid = uid(f"sym{ref}")
    pins = "".join(f'\t\t(pin "{n}" (uuid "{uid(f"pin{ref}{n}")}"))\n'
                   for n in PIN_OFFSETS[(lib, name)])
    hidden = " (hide yes)" if ref.startswith("#") else ""
    return (
        f'\t(symbol (lib_id "{lib}:{name}") (at {fmt(x)} {fmt(y)} {angle}) (unit 1)\n'
        f'\t\t(exclude_from_sim {"yes" if no_sim else "no"}) (in_bom {"no" if ref.startswith("#") else "yes"})'
        f' (on_board {"no" if ref.startswith("#") else "yes"}) (dnp no)\n'
        f'\t\t(uuid "{sym_uuid}")\n'
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
    lib_symbols = "".join(
        "\t\t" + extract_symbol(lib, name).replace("\n", "\n\t") + "\n"
        for lib, name in sorted({(s[0], s[1]) for s in SYMBOLS.values()}))

    def stub(a, dx, dy):
        b = (round(a[0] + dx, 2), round(a[1] + dy, 2))
        return wire(a, b), b

    body = ""
    # Each pin gets a short stub ending in a net label or a power symbol.
    for ref, number, dx, dy, net in (("J1", "1", 2.54, 0, "IN"), ("J1", "2", 2.54, 0, "OUT"),
                                     ("R1", "1", 0, -2.54, "IN"), ("R1", "2", 0, 2.54, "OUT"),
                                     ("C1", "1", 0, -2.54, "OUT")):
        w, end = stub(pin(ref, number), dx, dy)
        body += w + label(net, end)
    # GND: J1.3 -> #PWR02, C1.2 -> #PWR01, PWR_FLAG wired to #PWR01.
    body += wire(pin("J1", "3"), pin("#PWR02", "1"))
    body += wire(pin("C1", "2"), pin("#PWR01", "1"))
    body += wire(pin("#PWR01", "1"), pin("#FLG01", "1"))
    symbols = "".join(symbol_instance(ref, root_uuid) for ref in SYMBOLS)

    text = (
        '(kicad_sch (version 20231120) (generator "fome_mc_toolchain_fixture") (generator_version "10.0")\n'
        f'\t(uuid "{root_uuid}")\n'
        '\t(paper "A5")\n'
        '\t(title_block (title "Toolchain fixture: RC low-pass (not ECU design)") (rev "1"))\n'
        f'\t(lib_symbols\n{lib_symbols}\t)\n'
        f'{body}{symbols}'
        '\t(sheet_instances (path "/" (page "1")))\n'
        ')\n'
    )
    path = HERE / f"{NAME}.kicad_sch"
    path.write_text(text)
    subprocess.run(["kicad-cli", "sch", "upgrade", "--force", str(path)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return root_uuid


def write_project():
    pro = json.loads(TEMPLATE_PRO.read_text())
    pro["meta"]["filename"] = f"{NAME}.kicad_pro"
    # KiCad 10 maps the top-level schematic to its UUID through the project.
    pro["schematic"] = {"top_level_sheets": [
        {"filename": f"{NAME}.kicad_sch", "name": NAME, "uuid": uid("root")}]}
    pro["sheets"] = [[uid("root"), "Root"]]
    (HERE / f"{NAME}.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")
    # Hermetic library tables: only the stock libraries the fixture uses.
    sym = ["(sym_lib_table", "  (version 7)"]
    for lib in sorted({s[0] for s in SYMBOLS.values()}):
        sym.append(f'  (lib (name "{lib}")(type "KiCad")(uri "${{KICAD10_SYMBOL_DIR}}/{lib}.kicad_sym")'
                   '(options "")(descr ""))')
    (HERE / "sym-lib-table").write_text("\n".join(sym + [")"]) + "\n")
    fp = ["(fp_lib_table", "  (version 7)"]
    for lib in sorted({s[3].split(":")[0] for s in SYMBOLS.values() if s[3]}):
        fp.append(f'  (lib (name "{lib}")(type "KiCad")(uri "${{KICAD10_FOOTPRINT_DIR}}/{lib}.pretty")'
                  '(options "")(descr ""))')
    (HERE / "fp-lib-table").write_text("\n".join(fp + [")"]) + "\n")


def write_pcb():
    import pcbnew

    mm = pcbnew.FromMM
    board = pcbnew.BOARD()
    nets = {}
    for name in ("/IN", "/OUT", "GND"):
        nets[name] = pcbnew.NETINFO_ITEM(board, name)
        board.Add(nets[name])

    def place(ref, x, y, angle=0):
        value, footprint = SYMBOLS[ref][2], SYMBOLS[ref][3]
        lib, fp_name = footprint.split(":")
        fp = pcbnew.FootprintLoad(str(FOOTPRINT_DIR / f"{lib}.pretty"), fp_name)
        fp.SetFPID(pcbnew.LIB_ID(lib, fp_name))
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetPath(pcbnew.KIID_PATH(f"/{uid(f'sym{ref}')}"))
        fp.SetSheetname("/")
        fp.SetSheetfile(f"{NAME}.kicad_sch")
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetOrientationDegrees(angle)
        return fp

    j1 = place("J1", 100, 100)
    r1 = place("R1", 105, 100)
    c1 = place("C1", 110, 100)
    pads = {}
    for fp, assign in ((j1, {"1": "/IN", "2": "/OUT", "3": "GND"}),
                       (r1, {"1": "/IN", "2": "/OUT"}),
                       (c1, {"1": "/OUT", "2": "GND"})):
        for number, net in assign.items():
            pad = fp.FindPadByNumber(number)
            pad.SetNet(nets[net])
            pads[f"{fp.GetReference()}.{number}"] = pad.GetPosition()

    def track(a, b, net):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(a)
        t.SetEnd(b)
        t.SetWidth(mm(0.25))
        t.SetLayer(pcbnew.F_Cu)
        t.SetNet(nets[net])
        board.Add(t)

    def pt(x, y):
        return pcbnew.VECTOR2I(mm(x), mm(y))

    track(pads["J1.1"], pads["R1.1"], "/IN")
    track(pads["R1.2"], pads["C1.1"], "/OUT")
    track(pads["J1.2"], pt(107.5, 102.54), "/OUT")
    track(pt(107.5, 102.54), pt(107.5, 100), "/OUT")
    via_at = pt(113, 100)
    track(pads["C1.2"], via_at, "GND")
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(via_at)
    via.SetWidth(mm(0.6))
    via.SetDrill(mm(0.3))
    via.SetNet(nets["GND"])
    board.Add(via)

    corners = [(96, 96), (116, 96), (116, 108), (96, 108)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pt(*a))
        seg.SetEnd(pt(*b))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.1))
        board.Add(seg)

    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(nets["GND"])
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in [(96.5, 96.5), (115.5, 96.5), (115.5, 107.5), (96.5, 107.5)]:
        outline.Append(mm(x), mm(y))
    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    path = HERE / f"{NAME}.kicad_pcb"
    pcbnew.SaveBoard(str(path), board)
    # SaveBoard writes a project file next to the board; keep ours authoritative.
    write_project()


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
