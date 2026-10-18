#!/usr/bin/env python3
"""Export JLCPCB-compatible BOM and CPL CSVs and verify 1:1 BOM/CPL parity."""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCB_PATH = ROOT / "fome-mc.kicad_pcb"
SCH_PATH = ROOT / "fome-mc.kicad_sch"
BOM_CSV_PATH = ROOT / "export" / "BOM-fome-mc.csv"
CPL_CSV_PATH = ROOT / "export" / "CPL-fome-mc.csv"
PARITY_JSON_PATH = ROOT / "reports" / "toolchain" / "bom-cpl-parity.json"


def natural_key(ref: str) -> tuple[str, int, str]:
    m = re.match(r"^([A-Za-z_]+)(\d+)(.*)$", ref)
    if m:
        return (m.group(1), int(m.group(2)), m.group(3))
    return (ref, 0, "")


def parse_pcb_footprints(pcb_text: str) -> dict[str, dict[str, object]]:
    footprints: dict[str, dict[str, object]] = {}
    for m in re.finditer(r"\t\(footprint\s+\"([^\"]+)\".*?\n\t\)", pcb_text, flags=re.DOTALL):
        fblock = m.group(0)
        lib_fp = m.group(1)
        props: dict[str, str] = {}
        for pm in re.finditer(r'\(property\s+"([^"]+)"\s+"([^"]*)"', fblock):
            props[pm.group(1)] = pm.group(2)
        ref = props.get("Reference", "")
        if not ref:
            continue
        attr_m = re.search(r"\n\t\t\(attr\s+([^\)]+)\)", fblock)
        attrs = attr_m.group(1).split() if attr_m else []
        footprints[ref] = {
            "ref": ref,
            "value": props.get("Value", ""),
            "lib_footprint": lib_fp,
            "package": lib_fp.split(":")[-1],
            "lcsc": props.get("LCSC", "").strip(),
            "attrs": attrs,
        }
    return footprints


def export_cpl_rows() -> list[dict[str, str]]:
    env = os.environ.copy()
    env.setdefault("KICAD_CONFIG_HOME", str(ROOT / "build" / "kicad-config"))
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            [
                "kicad-cli",
                "pcb",
                "export",
                "pos",
                "--format",
                "csv",
                "--units",
                "mm",
                "--exclude-dnp",
                "-o",
                str(tmp_path),
                str(PCB_PATH),
            ],
            check=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        rows: list[dict[str, str]] = []
        with tmp_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                side = row["Side"].strip().lower()
                layer = "Top" if side == "top" else ("Bottom" if side == "bottom" else row["Side"].strip())
                rows.append(
                    {
                        "Designator": row["Ref"].strip(),
                        "Val": row["Val"].strip(),
                        "Package": row["Package"].strip(),
                        "Mid X": f"{float(row['PosX']):.4f}mm",
                        "Mid Y": f"{float(row['PosY']):.4f}mm",
                        "Rotation": f"{float(row['Rot']):.4f}",
                        "Layer": layer,
                    }
                )
        rows.sort(key=lambda r: natural_key(r["Designator"]))
        return rows
    finally:
        tmp_path.unlink(missing_ok=True)


def main() -> None:
    pcb_text = PCB_PATH.read_text(encoding="utf-8")
    pcb_fps = parse_pcb_footprints(pcb_text)

    cpl_rows = export_cpl_rows()
    CPL_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CPL_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"],
        )
        writer.writeheader()
        writer.writerows(cpl_rows)

    # Build BOM from non-excluded, non-DNP footprints on the PCB
    bom_items: list[dict[str, object]] = []
    dnp_excluded_refs: list[str] = []
    for ref, info in sorted(pcb_fps.items(), key=lambda kv: natural_key(kv[0])):
        attrs = info["attrs"]
        if (
            "dnp" in attrs
            or "exclude_from_bom" in attrs
            or "exclude_from_pos_files" in attrs
            or "board_only" in attrs
        ):
            dnp_excluded_refs.append(ref)
            continue
        bom_items.append(info)

    groups: dict[tuple[str, str, str], list[str]] = {}
    for item in bom_items:
        key = (str(item["value"]), str(item["package"]), str(item["lcsc"]))
        groups.setdefault(key, []).append(str(item["ref"]))

    bom_rows: list[dict[str, str]] = []
    for (val, pkg, lcsc), refs in sorted(
        groups.items(), key=lambda kv: natural_key(kv[1][0])
    ):
        refs_sorted = sorted(refs, key=natural_key)
        bom_rows.append(
            {
                "Comment": val,
                "Designator": ",".join(refs_sorted),
                "Footprint": pkg,
                "LCSC": lcsc,
            }
        )

    with BOM_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Comment", "Designator", "Footprint", "LCSC"]
        )
        writer.writeheader()
        writer.writerows(bom_rows)

    bom_refs = sorted([str(item["ref"]) for item in bom_items], key=natural_key)
    cpl_refs = sorted([r["Designator"] for r in cpl_rows], key=natural_key)
    bom_set = set(bom_refs)
    cpl_set = set(cpl_refs)
    bom_minus_cpl = sorted(bom_set - cpl_set, key=natural_key)
    cpl_minus_bom = sorted(cpl_set - bom_set, key=natural_key)
    missing_lcsc = sorted(
        [str(item["ref"]) for item in bom_items if not str(item["lcsc"]).strip()],
        key=natural_key,
    )
    tht_populated = sorted(
        [str(item["ref"]) for item in bom_items if "through_hole" in item["attrs"]],
        key=natural_key,
    )
    smd_populated = sorted(
        [str(item["ref"]) for item in bom_items if "smd" in item["attrs"]],
        key=natural_key,
    )

    status = (
        "PASS"
        if (not bom_minus_cpl and not cpl_minus_bom and not missing_lcsc and len(bom_refs) > 0)
        else "FAIL"
    )

    parity_report = {
        "status": status,
        "bom_csv": str(BOM_CSV_PATH.relative_to(ROOT)),
        "cpl_csv": str(CPL_CSV_PATH.relative_to(ROOT)),
        "bom_line_count": len(bom_rows),
        "bom_designator_count": len(bom_refs),
        "cpl_designator_count": len(cpl_refs),
        "smd_populated_count": len(smd_populated),
        "through_hole_populated_refs": tht_populated,
        "dnp_or_excluded_refs": dnp_excluded_refs,
        "bom_minus_cpl": bom_minus_cpl,
        "cpl_minus_bom": cpl_minus_bom,
        "missing_lcsc": missing_lcsc,
    }

    PARITY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    PARITY_JSON_PATH.write_text(json.dumps(parity_report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(parity_report, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
