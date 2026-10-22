"""Check the J1 mating-interface packet (stdlib only, no network).

Verifies source hashes and sizes, SHA256SUMS, that every citation names a
known source, that every status is a known value, and that the installed
enclosure/harness/tool items stay UNRESOLVED. `--self-test` also runs
negative controls that must be rejected.

Run: python3 -I check.py [--self-test]
"""
import copy
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
STATUSES = {"SOURCED", "PARTIAL", "UNRESOLVED"}
MUST_STAY_UNRESOLVED = {"installed_enclosure_fit", "installed_harness", "installed_tool_access"}
REQUIRED_ITEMS = {
    "plug_identity_and_keying", "mated_height_envelope", "panel_cutout_and_mounting",
    "pcb_thickness", "latch_cpa_and_tool_access", "harness_exit_direction",
} | MUST_STAY_UNRESOLVED


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_files(record):
    errors = []
    for key, src in record["sources"].items():
        path = (HERE / src["file"]).resolve()
        if not path.is_file():
            errors.append(f"{key}: missing {src['file']}")
            continue
        if sha256(path) != src["sha256"]:
            errors.append(f"{key}: sha256 mismatch for {src['file']}")
        if path.stat().st_size != src["bytes"]:
            errors.append(f"{key}: size mismatch for {src['file']}")
    for line in (HERE / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if sha256(HERE / name) != digest:
            errors.append(f"SHA256SUMS mismatch: {name}")
    return errors


def check_record(record):
    errors = []
    items = {item["id"]: item for item in record["items"]}
    missing = REQUIRED_ITEMS - items.keys()
    if missing:
        errors.append(f"missing items: {sorted(missing)}")
    for item_id, item in items.items():
        if item["status"] not in STATUSES:
            errors.append(f"{item_id}: unknown status {item['status']}")
        if item["status"] != "UNRESOLVED" and not item["evidence"]:
            errors.append(f"{item_id}: {item['status']} without evidence")
        if item["status"] != "SOURCED" and not item["not_resolved"]:
            errors.append(f"{item_id}: {item['status']} without an unresolved list")
        for ev in item["evidence"]:
            if ev["source"] not in record["sources"]:
                errors.append(f"{item_id}: unknown source {ev['source']}")
            if not ev.get("page") or not ev.get("figure"):
                errors.append(f"{item_id}: citation lacks page or figure")
    for item_id in MUST_STAY_UNRESOLVED & items.keys():
        if items[item_id]["status"] != "UNRESOLVED":
            errors.append(f"{item_id}: must stay UNRESOLVED without an installed-fit source")
    return errors


def self_test(record):
    def mutated(fn):
        rec = copy.deepcopy(record)
        fn(rec)
        return rec

    def item(rec, item_id):
        return next(i for i in rec["items"] if i["id"] == item_id)

    controls = {
        "installed fit promoted": mutated(lambda r: item(r, "installed_enclosure_fit").update(status="SOURCED")),
        "uncited source": mutated(lambda r: item(r, "pcb_thickness")["evidence"].append(
            {"source": "NOPE", "page": 1, "figure": "x", "fact": "x"})),
        "unknown status": mutated(lambda r: item(r, "mated_height_envelope").update(status="PASS")),
        "item dropped": mutated(lambda r: r["items"].pop(0)),
    }
    failed = [name for name, rec in controls.items() if not check_record(rec)]
    for name in controls:
        print(f"negative control {name}: {'NOT REJECTED' if name in failed else 'rejected'}")
    return failed


def main():
    record = json.loads((HERE / "interface.json").read_text())
    errors = check_files(record) + check_record(record)
    for err in errors:
        print("ERROR", err)
    if "--self-test" in sys.argv and self_test(record):
        errors.append("negative control accepted")
    counts = {}
    for item in record["items"]:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    print(f"items: {dict(sorted(counts.items()))}; sources: {len(record['sources'])}; "
          f"missing captures: {len(record['missing_captures'])}")
    print("mating-interface: " + ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
