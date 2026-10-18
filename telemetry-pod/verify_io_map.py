#!/usr/bin/env python3
"""Check the pod CSV and interface-ID coverage; no schematic/compiler verdict."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

POD = Path(__file__).resolve().parent
COLUMNS = [
    "Connector_Pin", "Signal_Name", "Net", "Direction_Class",
    "Voltage_Current_Domain", "MCU_Ref", "MCU_Pin", "External_Destination", "Notes",
]
SPEC_SHA256 = "09e02c8d9471aabfa5d25935c87f436370cf1be367a96425b35305a53ce93493"
RECORD_SHA256 = "58f07c5ab3206aad70fc31561d873200d18ff9145b97cc0b1570c465a84fd250"
DOC_BLOBS = {
    "WIRING_SV650_K7.md": "bb0ff8c1a32faef6e7cc8fe1e67538829544b106",
    "TELEMETRY_AND_RACECHRONO.md": "3dafed620a10f8fba209c2707b8f832eec6f6303",
}


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def load_interfaces(record_path):
    spec_bytes = (POD / "REQUIREMENTS.md").read_bytes()
    require(hashlib.sha256(spec_bytes).hexdigest() == SPEC_SHA256,
            "REQUIREMENTS.md differs from pinned revision 2; recapture before checking")
    record_bytes = record_path.read_bytes()
    require(hashlib.sha256(record_bytes).hexdigest() == RECORD_SHA256,
            "spec-record.json differs from agent-ee ffa8c85 capture")
    record = json.loads(record_bytes)
    require(record["spec"]["sha256"] == SPEC_SHA256, "capture names another spec")
    interfaces = [r for r in record["requirements"] if r["section"] == "Interfaces"]
    require(len(interfaces) == 8, "expected all eight captured interface rows")
    for requirement in interfaces:
        locator = requirement["locator"]
        captured_row = spec_bytes[locator["byte_start"]:locator["byte_end"]]
        require(hashlib.sha256(captured_row).hexdigest() == requirement["text_sha256"],
                f"source row digest mismatch: {requirement['id']}")
    for filename, blob in DOC_BLOBS.items():
        content = (POD.parent / "docs" / filename).read_bytes()
        identity = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        require(identity == blob, f"citation changed: docs/{filename}; review mapping")
    return interfaces


def load_rows():
    with (POD / "io-map.csv").open(newline="", encoding="utf-8") as source:
        records = list(csv.reader(source, strict=True))
    require(records and records[0] == COLUMNS, "CSV header must match ticket exactly")
    require(all(len(r) == len(COLUMNS) for r in records[1:]), "ragged CSV row")
    require(all(cell.strip() and '\n' not in cell and '\r' not in cell
                for row in records[1:] for cell in row), "blank or multiline cell")
    rows = [dict(zip(COLUMNS, r)) for r in records[1:]]
    pins = [r["Connector_Pin"] for r in rows]
    require(len(set(pins)) == len(pins), "duplicate Connector_Pin")
    harness = [r for r in rows if r["Connector_Pin"].startswith("AMPSEAL-")]
    require({r["Connector_Pin"] for r in harness} ==
            {f"AMPSEAL-{n}" for n in range(1, 24)}, "must cover cavities 1..23 exactly")
    plugged = [r for r in harness if r["Direction_Class"] == "No_Connect"]
    require(len(plugged) == 7 and len(harness) - len(plugged) == 16,
            "must have 16 used cavities and seven no-connect cavities")
    for row in plugged:
        require(row["Signal_Name"] == "NO_CONNECT" and row["Net"] == "N/C" and
                row["MCU_Ref"] == row["MCU_Pin"] == "N/A" and
                "770678-1" in row["External_Destination"],
                f"incomplete no-connect declaration: {row['Connector_Pin']}")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec_record", type=Path,
                        help="agent-ee ffa8c85:fixtures/telemetry-pod/spec-record.json")
    args = parser.parse_args()
    interfaces = load_interfaces(args.spec_record)
    rows = load_rows()
    coverage = {r["id"]: [] for r in interfaces}
    for row in rows:
        ids = set(re.findall(r"\bPOD-IF-[A-Z0-9-]+\b", row["Notes"]))
        require(not ids - coverage.keys(), f"unknown interface IDs: {sorted(ids - coverage.keys())}")
        for requirement_id in ids:
            coverage[requirement_id].append(row["Connector_Pin"])
    require(all(coverage.values()),
            f"unmapped interface IDs: {[k for k, v in coverage.items() if not v]}")
    print(f"spec_sha256: {SPEC_SHA256}")
    print(f"spec_record_sha256: {RECORD_SHA256} (agent-ee ffa8c85)")
    print(f"io_map_sha256: {hashlib.sha256((POD / 'io-map.csv').read_bytes()).hexdigest()}")
    for requirement_id, pins in coverage.items():
        print(f"{requirement_id}: {', '.join(pins)}")
    for row in rows:
        for column in COLUMNS:
            if "TBD" in row[column]:
                print(f"TBD: {row['Connector_Pin']} / {column}: {row[column]}")
    print(f"PASS: {len(rows)} regular CSV rows; 23 cavities (16 used / 7 no-connect); "
          f"{len(coverage)}/8 interface IDs mapped")
    print("NOT_EVALUATED: generated schematic/netlist agreement and AGENTEE-188 io_map compilation")


if __name__ == "__main__":
    main()
