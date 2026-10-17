#!/usr/bin/env python3
"""
render_docs.py — Reproducible generator for fome-mc schematic SVGs/PDFs, PCB layer renders,
annotated architectural floorplan map, and dual 35-pin TE AMPSEAL connector pinout diagram.
"""
import csv
import html
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RENDERS = REPO / "docs" / "renders"
SCH_OUT = REPO / "docs" / "schematics"
PCB_FILE = REPO / "fome-mc.kicad_pcb"
IO_MAP_CSV = REPO / "io-map.csv"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO, check=True)


def render_kicad_exports() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    SCH_OUT.mkdir(parents=True, exist_ok=True)

    # 1. Export all schematic sheets as SVG + full multi-page PDF
    run(["kicad-cli", "sch", "export", "svg", "--output", str(SCH_OUT), "fome-mc.kicad_sch"])
    run(["kicad-cli", "sch", "export", "pdf", "--output", str(SCH_OUT / "fome-mc-schematics.pdf"), "fome-mc.kicad_sch"])

    # Convert key schematic SVGs to high-res PNGs for inline markdown display
    for svg_name, png_name in [
        ("fome-mc.svg", "fome-mc-schematic-root.png"),
        ("fome-mc-wbo1.svg", "fome-mc-schematic-wbo1.png"),
        ("fome-mc-ign_igbt.svg", "fome-mc-schematic-ign-igbt.png"),
        ("fome-mc-stepper_etb.svg", "fome-mc-schematic-stepper-etb.png"),
        ("fome-mc-mcu.svg", "fome-mc-schematic-mcu.png"),
    ]:
        svg_path = SCH_OUT / svg_name
        if svg_path.exists():
            run(["rsvg-convert", "-w", "2200", "-b", "white", str(svg_path), "-o", str(RENDERS / png_name)])

    # 2. Export PCB layers as SVG, PNG, and multi-page PDF
    run([
        "kicad-cli", "pcb", "export", "svg",
        "--layers", "F.Cu,F.Paste,F.Silkscreen,F.Mask,F.Courtyard,F.Fab,Edge.Cuts",
        "--page-size-mode", "2",
        "--exclude-drawing-sheet",
        "--output", str(RENDERS / "fome-mc-pcb-top.svg"),
        "fome-mc.kicad_pcb",
    ])
    run(["rsvg-convert", "-w", "2400", "-b", "#0d1117", str(RENDERS / "fome-mc-pcb-top.svg"), "-o", str(RENDERS / "fome-mc-pcb-top.png")])

    # Clean Assembly / Courtyard / Paste view (without F.Cu solid zone fill obscuring components)
    run([
        "kicad-cli", "pcb", "export", "svg",
        "--layers", "F.Paste,F.Silkscreen,F.Courtyard,F.Fab,Edge.Cuts",
        "--page-size-mode", "2",
        "--exclude-drawing-sheet",
        "--output", str(RENDERS / "fome-mc-pcb-assembly.svg"),
        "fome-mc.kicad_pcb",
    ])
    run(["rsvg-convert", "-w", "2400", "-b", "#0d1117", str(RENDERS / "fome-mc-pcb-assembly.svg"), "-o", str(RENDERS / "fome-mc-pcb-assembly.png")])

    run([
        "kicad-cli", "pcb", "export", "svg",
        "--layers", "B.Cu,B.Silkscreen,B.Mask,B.Fab,Edge.Cuts",
        "--page-size-mode", "2",
        "--exclude-drawing-sheet",
        "--output", str(RENDERS / "fome-mc-pcb-bottom.svg"),
        "fome-mc.kicad_pcb",
    ])
    run(["rsvg-convert", "-w", "2400", "-b", "#0d1117", str(RENDERS / "fome-mc-pcb-bottom.svg"), "-o", str(RENDERS / "fome-mc-pcb-bottom.png")])

    run([
        "kicad-cli", "pcb", "export", "svg",
        "--layers", "In1.Cu,Edge.Cuts",
        "--page-size-mode", "2",
        "--exclude-drawing-sheet",
        "--output", str(RENDERS / "fome-mc-pcb-in1-gnd.svg"),
        "fome-mc.kicad_pcb",
    ])
    run(["rsvg-convert", "-w", "2000", "-b", "#0d1117", str(RENDERS / "fome-mc-pcb-in1-gnd.svg"), "-o", str(RENDERS / "fome-mc-pcb-in1-gnd.png")])

    run([
        "kicad-cli", "pcb", "export", "svg",
        "--layers", "In2.Cu,Edge.Cuts",
        "--page-size-mode", "2",
        "--exclude-drawing-sheet",
        "--output", str(RENDERS / "fome-mc-pcb-in2-pwr.svg"),
        "fome-mc.kicad_pcb",
    ])
    run(["rsvg-convert", "-w", "2000", "-b", "#0d1117", str(RENDERS / "fome-mc-pcb-in2-pwr.svg"), "-o", str(RENDERS / "fome-mc-pcb-in2-pwr.png")])

    run([
        "kicad-cli", "pcb", "export", "pdf",
        "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Fab,Edge.Cuts",
        "--include-border-title",
        "--output", str(RENDERS / "fome-mc-pcb-layers.pdf"),
        "fome-mc.kicad_pcb",
    ])


def parse_pcb_footprints() -> list[tuple[str, float, float]]:
    """Extract (Reference, X_mm, Y_mm) in native KiCad top-left sheet coordinates."""
    text = PCB_FILE.read_text()
    fps = []
    pattern = r'\t\(footprint\s+"[^"]+"\n\t\t\(layer\s+"[^"]+"\)\n\t\t\(uuid\s+"[^"]+"\)\n\t\t\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+[-\d.]+)?\)'
    for m in re.finditer(pattern, text):
        x, y = float(m.group(1)), float(m.group(2))
        chunk = text[m.start():m.start() + 1500]
        rm = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', chunk)
        if rm:
            fps.append((rm.group(1), x, y))
    return fps


def render_floorplan_diagram() -> None:
    """Generate annotated architectural floorplan SVG & PNG from native KiCad PCB coordinates."""
    # Native KiCad board outline (Edge.Cuts): X = 26.0 .. 188.0 mm (162.0 mm), Y = 25.0 .. 140.0 mm (115.0 mm)
    bx0, by0, bw, bh = 26.0, 25.0, 162.0, 115.0
    scale = 11.0  # 11 px per mm
    pad_x, pad_y = 140, 130
    img_w = int(bw * scale + 2 * pad_x)
    img_h = int(bh * scale + 2 * pad_y + 115)

    def tx(x_mm: float) -> float:
        return pad_x + (x_mm - bx0) * scale

    def ty(y_mm: float) -> float:
        return pad_y + (y_mm - by0) * scale

    fps = parse_pcb_footprints()

    # Exact functional zones matching native KiCad PCB coordinates (X=26..188, Y=25..140)
    zones = [
        # (x_mm, y_mm, w_mm, h_mm, fill, stroke, title, subtitle)
        (32.0, 27.5, 72.0, 28.0, "#1c2430", "#58a6ff", "J1: TE AMPSEAL 35-PIN (BLACK 776163-1)", "Power, Grounds, INJ1..4, IGBT1..4, AUX_LS1..4, ETB1/2, STEP, WBO HTR, DFU"),
        (110.0, 27.5, 74.0, 28.0, "#24292f", "#a5d6ff", "J2: TE AMPSEAL 35-PIN (GREY 776163-2)", "CLT, IAT, TPS1/2, MAP1/2, Baro, Gear, Knock, VR1/2, Hall, WBO1/2 Cells, CAN1, USB"),
        (28.0, 58.0, 22.0, 49.0, "#3b1d2e", "#f85149", "4x IGNITION IGBTs", "Q201-Q204 FGD3040G2 (400V)"),
        (28.0, 108.5, 33.5, 29.5, "#1f2d3d", "#58a6ff", "STEPPER, H-BRIDGES & SDNAND", "U201/U203 TLE9201 • U202 DRV8825 • U25 SDNAND"),
        (62.5, 58.0, 91.5, 46.5, "#2b2318", "#d29922", "POWER SUPPLY, LDOs, CAN, IGN BUFFERS, LOW-SIDE & HIGH-SIDE DRIVERS", "U3 LMR14020 5V • U1/U2 TLS115D0E • U40 BTS716G • U1001..U1102 VNLD5090 • U42..U45 MIC4427"),
        (62.5, 106.0, 91.5, 32.0, "#162b24", "#3fb950", "STM32H753 BRAIN, BARO, PRECISION REF & ANALOG FRONT-END", "U26 STM32H753ZIT6 • U24 LPS25HB • U23 REF3333 • U1201/U1202 VNLD5090 • U7/U15..U21 MCP6004"),
        (155.5, 58.0, 30.5, 34.5, "#271d3b", "#bc8cff", "WIDEBAND #1 (LSU 4.9)", "U302 F042 • Q301 HTR • U301/U305/U307"),
        (155.5, 94.0, 30.5, 44.0, "#271d3b", "#d2a8ff", "WIDEBAND #2 & VBOOST", "U402 F042 • Q401 HTR • U401/U405 • U46 LM2733"),
    ]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{img_w}" height="{img_h}" viewBox="0 0 {img_w} {img_h}">',
        '<defs>',
        '  <style>',
        '    .bg { fill: #0d1117; }',
        '    .pcb { fill: #0d231a; stroke: #3fb950; stroke-width: 3; }',
        '    .title { font-family: "DejaVu Sans", sans-serif; font-size: 26px; font-weight: bold; fill: #f0f6fc; }',
        '    .subtitle { font-family: "DejaVu Sans", sans-serif; font-size: 15px; fill: #8b949e; }',
        '    .ztitle { font-family: "DejaVu Sans", sans-serif; font-size: 12.5px; font-weight: bold; fill: #ffffff; }',
        '    .zsub { font-family: "DejaVu Sans", sans-serif; font-size: 10px; fill: #d0d7de; }',
        '    .comp { font-family: "DejaVu Sans Mono", monospace; font-size: 9px; font-weight: bold; fill: #ffffff; }',
        '    .dim { font-family: "DejaVu Sans Mono", monospace; font-size: 13px; fill: #58a6ff; font-weight: bold; }',
        '  </style>',
        '</defs>',
        f'<rect class="bg" x="0" y="0" width="{img_w}" height="{img_h}"/>',
        f'<text class="title" x="{pad_x}" y="48">fome-mc — 4-Layer Integrated Motorcycle ECU Floorplan &amp; Functional Zones</text>',
        f'<text class="subtitle" x="{pad_x}" y="74">Board Dimensions: 162.0 mm × 115.0 mm (Edge.Cuts X=26..188, Y=25..140) • 474 Placed Components • Dual 35-Pin TE AMPSEAL Headers</text>',
        f'<rect class="pcb" x="{tx(bx0)}" y="{ty(by0)}" width="{bw*scale}" height="{bh*scale}" rx="15" ry="15"/>',
    ]

    # Dimension lines
    lines.append(f'<line x1="{tx(bx0)}" y1="{ty(by0)-22}" x2="{tx(bx0+bw)}" y2="{ty(by0)-22}" stroke="#58a6ff" stroke-width="2"/>')
    lines.append(f'<line x1="{tx(bx0)}" y1="{ty(by0)-30}" x2="{tx(bx0)}" y2="{ty(by0)-14}" stroke="#58a6ff" stroke-width="2"/>')
    lines.append(f'<line x1="{tx(bx0+bw)}" y1="{ty(by0)-30}" x2="{tx(bx0+bw)}" y2="{ty(by0)-14}" stroke="#58a6ff" stroke-width="2"/>')
    lines.append(f'<text class="dim" x="{tx(bx0+bw/2)}" y="{ty(by0)-28}" text-anchor="middle">162.0 mm (6.38 in)</text>')

    lines.append(f'<line x1="{tx(bx0)-25}" y1="{ty(by0)}" x2="{tx(bx0)-25}" y2="{ty(by0+bh)}" stroke="#58a6ff" stroke-width="2"/>')
    lines.append(f'<line x1="{tx(bx0)-33}" y1="{ty(by0)}" x2="{tx(bx0)-17}" y2="{ty(by0)}" stroke="#58a6ff" stroke-width="2"/>')
    lines.append(f'<line x1="{tx(bx0)-33}" y1="{ty(by0+bh)}" x2="{tx(bx0)-17}" y2="{ty(by0+bh)}" stroke="#58a6ff" stroke-width="2"/>')
    lines.append(f'<text class="dim" x="{tx(bx0)-38}" y="{ty(by0+bh/2)}" text-anchor="middle" transform="rotate(-90 {tx(bx0)-38} {ty(by0+bh/2)})">115.0 mm (4.53 in)</text>')

    # Zone background boxes
    for zx, zy, zw, zh, fill, stroke, _, _ in zones:
        lines.append(f'<rect x="{tx(zx):.1f}" y="{ty(zy):.1f}" width="{zw*scale:.1f}" height="{zh*scale:.1f}" rx="8" ry="8" fill="{fill}" fill-opacity="0.65" stroke="{stroke}" stroke-width="2" stroke-dasharray="6,3"/>')

    # Draw 35-pin staggered arrays inside J1 (center X=68, Y=43) and J2 (center X=148, Y=43)
    for jx0 in (46.0, 126.0):
        for r_idx, (cnt, x_off, py) in enumerate([(12, 0.0, 39.0), (11, 2.0, 43.0), (12, 0.0, 47.0)]):
            for c_idx in range(cnt):
                px = jx0 + x_off + c_idx * 4.0
                lines.append(f'<circle cx="{tx(px):.1f}" cy="{ty(py):.1f}" r="9" fill="#d29922" stroke="#ffffff" stroke-width="1.5"/>')
                lines.append(f'<circle cx="{tx(px):.1f}" cy="{ty(py):.1f}" r="4.5" fill="#0d1117"/>')

    # 4x M4 Corner Mounting Holes (4.0 mm from board corners: X=30/184, Y=29/136)
    for mx, my in [(30.0, 29.0), (184.0, 29.0), (30.0, 136.0), (184.0, 136.0)]:
        lines.append(f'<circle cx="{tx(mx)}" cy="{ty(my)}" r="33" fill="#161b22" stroke="#d29922" stroke-width="2.5" stroke-dasharray="4,2"/>')
        lines.append(f'<circle cx="{tx(mx)}" cy="{ty(my)}" r="21" fill="#0d1117" stroke="#f0f6fc" stroke-width="2"/>')

    major_highlights = {
        "U26": (20.0, 20.0, "#238636", "U26 STM32H753ZIT6"),
        "U25": (6.0, 8.0, "#1f6feb", "U25 SDNAND"),
        "U24": (4.5, 4.5, "#d29922", "U24 BARO"),
        "Q201": (9.0, 6.6, "#da3633", "Q201 IGBT1"),
        "Q202": (9.0, 6.6, "#da3633", "Q202 IGBT2"),
        "Q203": (9.0, 6.6, "#da3633", "Q203 IGBT3"),
        "Q204": (9.0, 6.6, "#da3633", "Q204 IGBT4"),
        "U201": (7.5, 10.0, "#1f6feb", "U201 TLE9201 #1"),
        "U202": (6.4, 9.7, "#388bfd", "U202 DRV8825"),
        "U203": (7.5, 10.0, "#1f6feb", "U203 TLE9201 #2"),
        "U302": (7.0, 7.0, "#8957e5", "U302 WBO1 F042"),
        "Q301": (6.6, 9.0, "#a371f7", "Q301 WBO1 HTR"),
        "U307": (5.0, 4.0, "#8957e5", "U307 CAN"),
        "U402": (7.0, 7.0, "#8957e5", "U402 WBO2 F042"),
        "Q401": (6.6, 9.0, "#a371f7", "Q401 WBO2 HTR"),
        "U407": (5.0, 4.0, "#8957e5", "U407 CAN"),
        "U46": (5.5, 4.0, "#d29922", "U46 VBOOST"),
        "U1": (6.5, 5.0, "#d29922", "U1 5VP_1"),
        "U2": (6.5, 5.0, "#d29922", "U2 5VP_2"),
        "U3": (5.5, 5.0, "#d29922", "U3 5V BUCK"),
        "U4": (5.5, 4.0, "#e3b341", "U4 CAN1"),
        "U5": (5.5, 4.0, "#e3b341", "U5 CAN2"),
        "U40": (11.0, 7.5, "#2ea043", "U40 BTS716G HS"),
        "U1001": (6.0, 4.5, "#2ea043", "U1001 INJ1/2"),
        "U1002": (6.0, 4.5, "#2ea043", "U1002 INJ3/4"),
        "U1101": (6.0, 4.5, "#2ea043", "U1101 LS5/6"),
        "U1102": (6.0, 4.5, "#2ea043", "U1102 LS7/8"),
        "U1201": (6.0, 4.5, "#2ea043", "U1201 LS9/10"),
        "U1202": (6.0, 4.5, "#2ea043", "U1202 LS11/12"),
    }

    # Minor footprints first
    for ref, cx, cy in fps:
        if ref in ("J1", "J2") or ref in major_highlights or ref.startswith("LOGO"):
            continue
        c_fill = "#6e7681" if ref.startswith(("R", "C")) else "#58a6ff"
        lines.append(f'<rect x="{tx(cx)-4.5:.1f}" y="{ty(cy)-4.5:.1f}" width="9" height="9" rx="2" ry="2" fill="{c_fill}" fill-opacity="0.7" stroke="#c9d1d9" stroke-width="0.6"/>')

    # Major ICs on top
    for ref, cx, cy in fps:
        if ref in major_highlights:
            w_mm, h_mm, color, label = major_highlights[ref]
            rx = tx(cx - w_mm / 2)
            ry = ty(cy - h_mm / 2)
            lines.append(f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{w_mm*scale:.1f}" height="{h_mm*scale:.1f}" rx="4" ry="4" fill="{color}" fill-opacity="0.92" stroke="#ffffff" stroke-width="1.5"/>')
            lines.append(f'<text class="comp" x="{tx(cx):.1f}" y="{ty(cy)+3:.1f}" text-anchor="middle">{html.escape(label)}</text>')

    # Zone header banners drawn ON TOP with solid pill backgrounds so text is never occluded
    for zx, zy, zw, zh, fill, stroke, zt, zs in zones:
        bx_px = tx(zx) + 6
        by_px = ty(zy) + 5
        bw_px = min(zw * scale - 12, max(len(zt) * 8.2, len(zs) * 5.8) + 18)
        lines.append(f'<rect x="{bx_px:.1f}" y="{by_px:.1f}" width="{bw_px:.1f}" height="34" rx="5" ry="5" fill="#0d1117" fill-opacity="0.88" stroke="{stroke}" stroke-width="1.2"/>')
        lines.append(f'<text class="ztitle" x="{bx_px+8:.1f}" y="{by_px+15:.1f}">{html.escape(zt)}</text>')
        lines.append(f'<text class="zsub" x="{bx_px+8:.1f}" y="{by_px+28:.1f}">{html.escape(zs)}</text>')

    # Footer
    fy = ty(by0 + bh) + 42
    lines.append(f'<rect x="{pad_x}" y="{fy}" width="{bw*scale}" height="78" rx="8" ry="8" fill="#161b22" stroke="#30363d" stroke-width="1.5"/>')
    lines.append(f'<text class="ztitle" x="{pad_x+16}" y="{fy+24}">4-Layer Impedance-Controlled Stackup (1.6 mm FR-4 TG170, 1 oz Outer / 1 oz Inner) &amp; Thermal Coupling</text>')
    lines.append(f'<text class="zsub" x="{pad_x+16}" y="{fy+44}">• L1 (F.Cu): High-speed signals, 90Ω USB / 120Ω CAN diff pairs, SDMMC1, WBO Kelvin Nernst/Ip traces, high-current IGBT/Heater pours</text>')
    lines.append(f'<text class="zsub" x="{pad_x+16}" y="{fy+62}">• L2 (In1.Cu): Unbroken solid GND plane + Star AGND split   • L3 (In2.Cu): +5V, +3.3V, +12V_MR, +3V3_WBO1/2 power islands   • L4 (B.Cu): Bottom GND + thermal pad coupling</text>')

    lines.append('</svg>')
    svg_path = RENDERS / "fome-mc-floorplan-zones.svg"
    svg_path.write_text("\n".join(lines))
    run(["rsvg-convert", "-w", "2400", str(svg_path), "-o", str(RENDERS / "fome-mc-floorplan-zones.png")])


def render_pinout_diagram() -> None:
    """Generate visual Dual 35-Pin TE AMPSEAL (J1 & J2) Faceplate & Pinout Diagram."""
    rows = list(csv.DictReader(IO_MAP_CSV.open()))
    pin_map = {r["Connector_Pin"]: r for r in rows if r["Connector_Pin"].startswith("J")}

    def classify(pin: str, r: dict) -> tuple[str, str]:
        sig = r["Signal_Name"]
        cls = r["Direction_Class"]
        if "Ground" in cls or "GND" in sig:
            return "#30363d", "Ground (PGND / SGND)"
        if "Power" in cls or sig.startswith(("+12V", "5V_", "WBO_HTR+")) or "VBUS" in sig:
            return "#b62324", "Power / 5V Sensor / DFU"
        if "IGBT" in sig:
            return "#d29922", "Ignition IGBT (400V 30A)"
        if "IGN" in sig:
            return "#9e6a03", "Ignition Logic (5V Push-Pull)"
        if sig.startswith(("INJ", "AUX_LS", "HS", "DASH")):
            return "#1f6feb", "Injector / Low-Side / High-Side"
        if sig.startswith(("ETB", "STEP")):
            return "#0969da", "Stepper (ISC) & H-Bridge (STVA)"
        if "WBO" in sig:
            return "#8957e5", "Dual Wideband (LSU 4.9 #1 & #2)"
        if sig.startswith(("VR", "HALL", "DIN")):
            return "#2ea043", "Crank/Cam VR & Digital/Hall"
        if sig.startswith(("CAN", "USB")):
            return "#0e8a16", "Communication (CAN1 & USB)"
        return "#1b7c83", "Analog / Thermistor / Knock"

    img_w, img_h = 2200, 1420
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{img_w}" height="{img_h}" viewBox="0 0 {img_w} {img_h}">',
        '<defs>',
        '  <style>',
        '    .bg { fill: #0d1117; }',
        '    .title { font-family: "DejaVu Sans", sans-serif; font-size: 26px; font-weight: bold; fill: #f0f6fc; }',
        '    .sub { font-family: "DejaVu Sans", sans-serif; font-size: 14px; fill: #8b949e; }',
        '    .hdr { font-family: "DejaVu Sans", sans-serif; font-size: 18px; font-weight: bold; fill: #f0f6fc; }',
        '    .pnum { font-family: "DejaVu Sans Mono", monospace; font-size: 12px; font-weight: bold; fill: #ffffff; }',
        '    .psig { font-family: "DejaVu Sans Mono", monospace; font-size: 11px; font-weight: bold; fill: #f0f6fc; }',
        '    .pmcu { font-family: "DejaVu Sans Mono", monospace; font-size: 9.5px; fill: #ffd33d; }',
        '    .psv { font-family: "DejaVu Sans", sans-serif; font-size: 9.5px; fill: #c9d1d9; }',
        '    .leg { font-family: "DejaVu Sans", sans-serif; font-size: 12px; fill: #f0f6fc; }',
        '  </style>',
        '</defs>',
        f'<rect class="bg" x="0" y="0" width="{img_w}" height="{img_h}"/>',
        '<text class="title" x="40" y="45">fome-mc — Dual 35-Pin TE AMPSEAL Connector Pinout &amp; 2007 Suzuki SV650 (K7) Harness Map</text>',
        '<text class="sub" x="40" y="70">Mating View (Looking into PCB Header Pins / Back of Mating Plug Cavity Numbers 1–35) • 3-Row Staggered AMPSEAL Layout (Row 1: 1–12, Row 2: 13–23, Row 3: 24–35)</text>',
    ]

    categories = [
        ("#b62324", "Power / 5V / VBUS-DFU"),
        ("#30363d", "Ground (PGND / SGND)"),
        ("#1f6feb", "Injector / Aux Low-Side / HS"),
        ("#d29922", "Ignition IGBT (400V 30A)"),
        ("#9e6a03", "Ignition Logic (5V)"),
        ("#0969da", "Stepper (ISC) & H-Bridge (STVA)"),
        ("#8957e5", "Wideband LSU 4.9 (#1 & #2)"),
        ("#1b7c83", "Analog / Thermistor / Knock"),
        ("#2ea043", "VR Triggers & Digital/Hall"),
        ("#0e8a16", "CAN1 & USB 2.0 FS"),
    ]
    lx = 40
    for color, label in categories:
        lines.append(f'<rect x="{lx}" y="86" width="18" height="18" rx="4" ry="4" fill="{color}" stroke="#f0f6fc" stroke-width="1"/>')
        lines.append(f'<text class="leg" x="{lx+24}" y="100">{html.escape(label)}</text>')
        lx += len(label) * 7 + 42

    def draw_connector(conn_prefix: str, title: str, housing_fill: str, housing_stroke: str, y_top: int) -> None:
        lines.append(f'<rect x="35" y="{y_top}" width="2130" height="600" rx="16" ry="16" fill="{housing_fill}" stroke="{housing_stroke}" stroke-width="3"/>')
        lines.append(f'<text class="hdr" x="60" y="{y_top+32}">{html.escape(title)}</text>')

        row_defs = [
            (range(1, 13), y_top + 50, 0),
            (range(13, 24), y_top + 225, 86),
            (range(24, 36), y_top + 400, 0),
        ]
        card_w, card_h = 166, 155
        pitch_x = 173

        for pin_range, ry, x_offset in row_defs:
            for idx, pnum in enumerate(pin_range):
                pid = f"{conn_prefix}-{pnum}"
                r = pin_map[pid]
                c_fill, _ = classify(pid, r)
                cx = 55 + x_offset + idx * pitch_x
                sig = r["Signal_Name"]
                mcu = r["MCU_Pin"].replace("_", "/")
                sv_fn = r["SV650_K7_Harness_Function"]
                if len(sv_fn) > 24:
                    sv_fn = sv_fn[:22] + ".."
                sv_wire = r["SV650_K7_Wire_Color_Pin"]
                if len(sv_wire) > 24:
                    sv_wire = sv_wire[:22] + ".."

                lines.append(f'<rect x="{cx}" y="{ry}" width="{card_w}" height="{card_h}" rx="10" ry="10" fill="#161b22" stroke="{c_fill}" stroke-width="2.5"/>')
                lines.append(f'<rect x="{cx}" y="{ry}" width="{card_w}" height="28" rx="8" ry="8" fill="{c_fill}"/>')
                lines.append(f'<text class="pnum" x="{cx+10}" y="{ry+19}">{pid}</text>')
                lines.append(f'<text class="pmcu" x="{cx+card_w-8}" y="{ry+19}" text-anchor="end">{html.escape(mcu[:12])}</text>')
                lines.append(f'<text class="psig" x="{cx+10}" y="{ry+52}">{html.escape(sig)}</text>')
                lines.append(f'<text class="psv" x="{cx+10}" y="{ry+76}">{html.escape(r["Voltage_Current_Domain"][:22])}</text>')
                lines.append(f'<line x1="{cx+8}" y1="{ry+88}" x2="{cx+card_w-8}" y2="{ry+88}" stroke="#30363d" stroke-width="1"/>')
                lines.append(f'<text class="psv" x="{cx+10}" y="{ry+108}">SV650: {html.escape(sv_fn)}</text>')
                lines.append(f'<text class="psv" x="{cx+10}" y="{ry+128}">Wire: {html.escape(sv_wire)}</text>')

    draw_connector(
        "J1",
        "J1 — TE AMPSEAL 35-Pin Right-Angle Header (Key 1 Black: PCB 776163-1 / Mating Plug 776164-1) — Power, Grounds & High-Current Outputs",
        "#131922",
        "#58a6ff",
        125,
    )
    draw_connector(
        "J2",
        "J2 — TE AMPSEAL 35-Pin Right-Angle Header (Key 2 Grey: PCB 776163-2 / Mating Plug 776164-2) — Sensors, Dual Wideband Cells, Logic Coils, CAN1 & USB",
        "#1b2028",
        "#a5d6ff",
        765,
    )

    lines.append('</svg>')
    svg_path = RENDERS / "fome-mc-pinout-diagram.svg"
    svg_path.write_text("\n".join(lines))
    run(["rsvg-convert", "-w", "2400", str(svg_path), "-o", str(RENDERS / "fome-mc-pinout-diagram.png")])


if __name__ == "__main__":
    render_kicad_exports()
    render_floorplan_diagram()
    render_pinout_diagram()
    print("PASS: Generated all schematic SVGs/PDF, PCB layer renders, floorplan map, and J1/J2 pinout diagram.")
