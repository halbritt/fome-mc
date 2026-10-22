"""Check the J1 mating-interface packet (stdlib only, no network).

Order matters and is fail-closed:
1. SHA256SUMS must cover exactly the intended packet file set (README.md,
   check.py, interface.json and every in-packet source file): well-formed
   lines, valid digests, unique paths, nothing missing and nothing extra.
   Nothing else is checked until the manifest itself is complete.
2. The manifest digests and every source's sha256/size (including the existing
   ../sources/776163-K1.pdf) must match the files.
3. The record: item IDs must be unique (checked on the list, before any index
   is built, so acceptance cannot depend on item order); every required item is
   present; every status is known; every citation names a known source with a
   page and figure; the installed enclosure/harness/tool items stay UNRESOLVED.

`--self-test` also runs negative controls that must be rejected.

Run: python3 -I check.py [--self-test]
"""
import copy
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
STATUSES = {"SOURCED", "PARTIAL", "UNRESOLVED"}
MUST_STAY_UNRESOLVED = {"installed_enclosure_fit", "installed_harness", "installed_tool_access"}
REQUIRED_ITEMS = {
    "plug_identity_and_keying", "mated_height_envelope", "panel_cutout_and_mounting",
    "pcb_thickness", "latch_cpa_and_tool_access", "harness_exit_direction",
} | MUST_STAY_UNRESOLVED
CORE_FILES = {"README.md", "check.py", "interface.json"}
MANIFEST_LINE = re.compile(r"([0-9a-f]{64})  (\S.*)")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def intended_files(record):
    """Packet-relative files SHA256SUMS must cover: the core files plus every
    source that lives inside this packet (../sources/776163-K1.pdf is verified
    separately through its record hash)."""
    names = set(CORE_FILES)
    for src in record["sources"].values():
        path = (HERE / src["file"]).resolve()
        if path.is_relative_to(HERE):
            names.add(path.relative_to(HERE).as_posix())
    return names


def parse_manifest(text, intended):
    """Return ({name: digest}, errors). Any error means the manifest is unusable."""
    errors, entries = [], {}
    for n, line in enumerate(text.splitlines(), 1):
        match = MANIFEST_LINE.fullmatch(line)
        if not match:
            errors.append(f"SHA256SUMS line {n}: not '<64 hex>  <path>'")
            continue
        digest, name = match.groups()
        if name in entries:
            errors.append(f"SHA256SUMS: duplicate entry {name}")
        entries[name] = digest
    missing = intended - entries.keys()
    extra = entries.keys() - intended
    if missing:
        errors.append(f"SHA256SUMS: missing entries {sorted(missing)}")
    if extra:
        errors.append(f"SHA256SUMS: unexpected entries {sorted(extra)}")
    return entries, errors


def check_manifest(record, text):
    entries, errors = parse_manifest(text, intended_files(record))
    on_disk = {p.relative_to(HERE).as_posix() for p in HERE.rglob("*")
               if p.is_file() and p.name != "SHA256SUMS" and "__pycache__" not in p.parts}
    unlisted = on_disk - intended_files(record)
    if unlisted:
        errors.append(f"packet files outside the intended set: {sorted(unlisted)}")
    return entries, errors


def check_files(record, entries):
    errors = []
    for name, digest in sorted(entries.items()):
        path = HERE / name
        if not path.is_file():
            errors.append(f"SHA256SUMS: missing file {name}")
        elif sha256(path) != digest:
            errors.append(f"SHA256SUMS mismatch: {name}")
    for key, src in record["sources"].items():
        path = (HERE / src["file"]).resolve()
        if not path.is_file():
            errors.append(f"{key}: missing {src['file']}")
            continue
        if sha256(path) != src["sha256"]:
            errors.append(f"{key}: sha256 mismatch for {src['file']}")
        if path.stat().st_size != src["bytes"]:
            errors.append(f"{key}: size mismatch for {src['file']}")
    return errors


def check_record(record):
    errors = []
    ids = [item.get("id") for item in record["items"]]
    duplicates = sorted({i for i in ids if ids.count(i) > 1}, key=str)
    if duplicates:
        # Reject before indexing: a later entry must never mask an earlier one.
        return [f"duplicate item ids: {duplicates}"]
    missing = REQUIRED_ITEMS - set(ids)
    if missing:
        errors.append(f"missing items: {sorted(missing)}")
    for item in record["items"]:
        item_id = item.get("id")
        status = item.get("status")
        evidence = item.get("evidence")
        not_resolved = item.get("not_resolved")
        if not isinstance(evidence, list) or not isinstance(not_resolved, list):
            errors.append(f"{item_id}: evidence and not_resolved must be lists")
            continue
        if status not in STATUSES:
            errors.append(f"{item_id}: unknown status {status}")
        if status != "UNRESOLVED" and not evidence:
            errors.append(f"{item_id}: {status} without evidence")
        if status != "SOURCED" and not not_resolved:
            errors.append(f"{item_id}: {status} without an unresolved list")
        for ev in evidence:
            if ev.get("source") not in record["sources"]:
                errors.append(f"{item_id}: unknown source {ev.get('source')}")
            if not ev.get("page") or not ev.get("figure"):
                errors.append(f"{item_id}: citation lacks page or figure")
        if item_id in MUST_STAY_UNRESOLVED and status != "UNRESOLVED":
            errors.append(f"{item_id}: must stay UNRESOLVED without an installed-fit source")
    return errors


def self_test(record, manifest_text):
    def mutated(fn):
        rec = copy.deepcopy(record)
        fn(rec)
        return rec

    def item(rec, item_id):
        return next(i for i in rec["items"] if i["id"] == item_id)

    def duplicate(rec, item_id, first, **changes):
        bad = copy.deepcopy(item(rec, item_id))
        bad.update(changes)
        rec["items"].insert(0, bad) if first else rec["items"].append(bad)

    promoted = dict(status="SOURCED", result="installed fit asserted",
                    evidence=copy.deepcopy(record["items"][0]["evidence"]))
    record_controls = {
        "installed fit promoted": mutated(lambda r: item(r, "installed_enclosure_fit").update(status="SOURCED")),
        "uncited source": mutated(lambda r: item(r, "pcb_thickness")["evidence"].append(
            {"source": "NOPE", "page": 1, "figure": "x", "fact": "x"})),
        "unknown status": mutated(lambda r: item(r, "mated_height_envelope").update(status="PASS")),
        "item dropped": mutated(lambda r: r["items"].pop(0)),
        "duplicate id, promoted entry first": mutated(
            lambda r: duplicate(r, "installed_tool_access", True, **promoted)),
        "duplicate id, promoted entry last": mutated(
            lambda r: duplicate(r, "installed_tool_access", False, **promoted)),
        "duplicate id masking unknown status": mutated(
            lambda r: duplicate(r, "mated_height_envelope", True, status="PASS")),
        "duplicate id, identical copy": mutated(
            lambda r: duplicate(r, "pcb_thickness", False)),
    }
    lines = manifest_text.splitlines()
    manifest_controls = {
        "empty SHA256SUMS": "",
        "interface.json entry removed": "\n".join(l for l in lines if not l.endswith("  interface.json")),
        "duplicate manifest path": "\n".join(lines + [lines[0]]),
        "malformed digest": "\n".join(["zz" + lines[0][2:]] + lines[1:]),
        "unexpected manifest entry": "\n".join(lines + ["0" * 64 + "  extra.txt"]),
    }
    results = {name: check_record(rec) for name, rec in record_controls.items()}
    results.update({name: check_manifest(record, text)[1] for name, text in manifest_controls.items()})
    failed = [name for name, errors in results.items() if not errors]
    for name in results:
        print(f"negative control {name}: {'NOT REJECTED' if name in failed else 'rejected'}")
    return failed


def main():
    record = json.loads((HERE / "interface.json").read_text())
    manifest_text = (HERE / "SHA256SUMS").read_text()
    entries, errors = check_manifest(record, manifest_text)
    if not errors:
        errors = check_files(record, entries) + check_record(record)
    for err in errors:
        print("ERROR", err)
    if "--self-test" in sys.argv and self_test(record, manifest_text):
        errors.append("negative control accepted")
    counts = {}
    for item in record["items"]:
        counts[item.get("status")] = counts.get(item.get("status"), 0) + 1
    print(f"items: {dict(sorted(counts.items(), key=str))}; sources: {len(record['sources'])}; "
          f"missing captures: {len(record['missing_captures'])}")
    print("mating-interface: " + ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
