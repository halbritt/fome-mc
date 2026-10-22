#!/usr/bin/env python3
"""Derive the pod io-map, bindings and indirect paths from the Rev-3 source netlist.

Nothing here is authored pin data. Every row, net, MCU pin and path terminal is read
from a kicad-cli XML netlist of the source schematic named in source.json, exported
from a temporary copy (the design is never opened in place). The only declarations
are the crossing rules below: which pin names of a part type carry a signal through
that part. A rerun on the same schematic writes byte-identical files; --check
compares instead of writing.

Rows: every pin of every J<n> and TP<n> component, in reference/pin order.
  Connector_Pin  <ref>-<pin>
  Signal_Name    net name without the leading '/', or NO_CONNECT
  Net            native net name, or N/C for a natively unconnected pin
  MCU_*          direct when the row's own net holds an MCU pin; otherwise one
                 indirect path per conductor chain that reaches the MCU through the
                 crossing rules, never into a power/ground net or another contact's
                 net. Rail nets
                 (any power_in/power_out pin) declare no MCU pin.
  Direction_Class, Voltage_Current_Domain, External_Destination
                 carried from the retained v9 io-map row bound to the same native
                 pin when its net name is identical; otherwise unknown. The v9 row's
                 POD-IF-* interface citations are carried with them.

Wireless rows: each source.json "wireless" entry adds one row with Net=N/A and no MCU
pin, after the contact rows. It names no native pin; the compiler keeps it unresolved
and verify-io reports it NOT_EVALUATED. Its requirement IDs must exist in the Rev-3
spec record, whose source digest and byte locators must match REQUIREMENTS.md.

History (history.json, agent-ee.io-map-history/1): the AGENTEE-188 compiler input
that binds carried citations to their original provenance. Its origin is the v9 io-map
(path, revision and sha256 from source.json "v9_origin"; the revision's bytes at the
original path must equal the retained file). Each carried row gets its own locator:
the v9 row number, v9 Connector_Pin and the carried columns. "sourced" is empty: no
cited ID is promoted, so the compiler emits every one as unqualified-carryover.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SOURCE_JSON = HERE / "source.json"
V9_DIR = HERE / "v9-pilot"
OUTPUTS = {
    "io-map": REPO / "telemetry-pod/io-map.csv",
    "bindings": HERE / "bindings.json",
    "paths": HERE / "paths.json",
    "history": HERE / "history.json",
}
COLUMNS = ["Connector_Pin", "Signal_Name", "Net", "Direction_Class", "Voltage_Current_Domain",
           "MCU_Ref", "MCU_Pin", "External_Destination", "Notes", "MCU_Path"]
CARRIED = ("Direction_Class", "Voltage_Current_Domain", "External_Destination")
CONTACT_REF = re.compile(r"(J|TP)[0-9]+")
INTERFACE_ID = re.compile(r"\bPOD-IF-[A-Z0-9-]+\b")
RAIL_TYPES = {"power_in", "power_out"}
DRIVERS = {"output", "tri_state", "open_collector", "open_emitter"}

# Part-type crossings, by native pin name: (role, enter pattern, exit names or a
# function of the entry name). Only these and the R/D reference rules below are
# crossed; every other part ends a chain. Crossings are one-way, connector to MCU.
SECTION = (lambda m: ["OUT" + m.group(1)])
CROSSINGS = {
    "PodPower:ADA4096-4ARUZ-R7": ("op-amp section", r"[+-]IN([A-D])", SECTION),
    "PodWheel:LM2903BQ_D": ("comparator section", r"IN([12])[+-]", SECTION),
    "Analog_ADC:MCP3208": ("ADC channel to SPI", r"CH[0-7]", ["~{CS}/SHDN", "Din", "Dout", "CLK"]),
    "Block_63616e_496e746572666163655f43414e5f4c494e:TJA1051T-3":
        ("CAN transceiver bus to logic", r"CAN[HL]", ["TXD", "RXD"]),
    "PodCAN:MCP2518FD_SL": ("CAN controller to SPI/interrupt", r"(TX|RX)CAN", ["SCK", "SDI", "SDO", "nCS", "INT"]),
}
DIODE_TOKEN = re.compile(r"([AK])([0-9]*)")
UNCARRIED = ("none: no v9 row carried. Signal_Name and Net are native; the other descriptive columns are "
             "generated (unknown, N/C or N/A)")


def natural(text):
    return [int(t) if t.isdigit() else t for t in re.split(r"([0-9]+)", text)]


def export_netlist(schematic: Path) -> bytes:
    cli = Path.home() / ".local/opt/kicad-10.0.7/bin/kicad-cli"
    cli = str(cli) if cli.exists() else shutil.which("kicad-cli")
    if not cli:
        sys.exit("kicad-cli not found")
    with tempfile.TemporaryDirectory(prefix="pod-io-map-") as tmp:
        copy = Path(tmp) / "project"
        shutil.copytree(schematic.parent, copy)
        out = Path(tmp) / "native.xml"
        proc = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadxml", "--output", str(out),
                               str(copy / schematic.name)], cwd=copy, capture_output=True, text=True)
        if proc.returncode != 0 or not out.is_file():
            sys.exit(f"kicad-cli netlist export failed (rc={proc.returncode}): {proc.stdout}{proc.stderr}")
        return out.read_bytes()


class Netlist:
    def __init__(self, raw: bytes):
        root = ET.fromstring(raw)
        lib = {}
        for part in root.findall("./libparts/libpart"):
            lib[f"{part.get('lib')}:{part.get('part')}"] = {
                p.get("num"): (p.get("name") or "", p.get("type")) for p in part.findall("./pins/pin")}
        self.comps = {}
        for comp in root.findall("./components/comp"):
            src = comp.find("libsource")
            symbol = f"{src.get('lib')}:{src.get('part')}"
            self.comps[comp.get("ref")] = {"symbol": symbol, "value": comp.findtext("value") or "",
                                           "sheet": comp.find("sheetpath").get("tstamps"), "pins": lib[symbol]}
        self.net_of, self.nodes = {}, {}
        for net in root.findall("./nets/net"):
            name = net.get("name")
            self.nodes[name] = [(n.get("ref"), n.get("pin")) for n in net.findall("node")]
            for node in self.nodes[name]:
                self.net_of[node] = name

    def name(self, ref, pin):
        return self.comps[ref]["pins"][pin][0]

    def ptype(self, ref, pin):
        return self.comps[ref]["pins"][pin][1]

    def unconnected(self, ref, pin):
        net = self.net_of.get((ref, pin))
        return net is None or (net.startswith("unconnected-") and len(self.nodes[net]) == 1)

    def rail(self, net):
        return any(self.ptype(r, p) in RAIL_TYPES for r, p in self.nodes[net])

    def crossings(self, ref, pin):
        """(exit pin, role) pairs for a signal entering ref at pin."""
        comp = self.comps[ref]
        pins = comp["pins"]
        by_name = {}
        for num, (name, _) in pins.items():
            by_name.setdefault(name, []).append(num)
        prefix = re.match(r"[A-Z]+", ref).group(0)
        if prefix == "R" and len(pins) == 2:
            return [(other, "series resistor") for other in pins if other != pin]
        if prefix == "D":
            out = []
            tokens = {num: [DIODE_TOKEN.fullmatch(t) for t in name.split("_")] for num, (name, _) in pins.items()}
            for m in filter(None, tokens[pin]):
                want = ("K" if m.group(1) == "A" else "A") + m.group(2)
                for num, toks in tokens.items():
                    if num != pin and any(t and t.group(0) == want for t in toks):
                        out.append((num, f"diode element {m.group(2) or '1'}"))
            return out
        rule = CROSSINGS.get(comp["symbol"])
        if not rule:
            return []
        role, enter, exits = rule
        m = re.fullmatch(enter, self.name(ref, pin))
        if not m:
            return []
        names = exits(m) if callable(exits) else exits
        return [(num, f"{role} {self.name(ref, pin)}->{name}") for name in names for num in by_name.get(name, [])]


def trace(nl, mcu, ref, pin):
    """Every simple chain from (ref, pin) to an MCU pin: lists of terminals and device roles.

    A chain never enters a rail net or another external contact's net (for example
    through a bus termination resistor into the other bus wire)."""
    found = []

    def walk(net, terminals, roles, seen):
        hits = sorted((p for r, p in nl.nodes[net] if r == mcu), key=natural)
        if hits:
            for p in hits:
                found.append((terminals + [(mcu, p)], roles))
            return
        for r, p in sorted(nl.nodes[net], key=lambda n: (natural(n[0]), natural(n[1]))):
            if (r, p) in terminals or CONTACT_REF.fullmatch(r):
                continue
            for exit_pin, role in nl.crossings(r, p):
                nxt = nl.net_of.get((r, exit_pin))
                if (nxt is None or nxt in seen or nl.rail(nxt) or nl.unconnected(r, exit_pin)
                        or any(CONTACT_REF.fullmatch(c) for c, _ in nl.nodes[nxt])):
                    continue
                walk(nxt, terminals + [(r, p), (r, exit_pin)], roles + [role], seen | {nxt})

    start = nl.net_of[(ref, pin)]
    walk(start, [(ref, pin)], [], {start})
    return found


def directions(nl, terminals, roles):
    """Segment directions from native pin types; passive-only stretches inherit."""
    def decide(a, b):
        ta, tb = nl.ptype(*a), nl.ptype(*b)
        if ta in DRIVERS and tb not in DRIVERS:
            return "toward_mcu"
        if tb in DRIVERS and ta not in DRIVERS:
            return "toward_connector"
        if ta == "input" and tb != "input":
            return "toward_connector"
        if tb == "input" and ta != "input":
            return "toward_mcu"
        if ta == tb == "bidirectional":
            return "bidirectional"
        return None
    segs = [decide(terminals[2 * k], terminals[2 * k + 1]) for k in range(len(roles) + 1)]
    passive = [role.startswith(("series resistor", "diode element")) for role in roles]
    # Segment i and segment j are joined by passive devices roles[min(i,j):max(i,j)].
    def nearest(i, span):
        for j in span:
            lo, hi = min(i, j), max(i, j)
            if not all(passive[lo:hi]):
                return None, None
            if segs[j]:
                return segs[j], hi - lo
        return None, None
    result = []
    for i, seg in enumerate(segs):
        if seg is None:
            back, bdist = nearest(i, range(i - 1, -1, -1))
            fwd, fdist = nearest(i, range(i + 1, len(segs)))
            if back and (fwd is None or bdist <= fdist):
                seg = back
            else:
                seg = fwd or "bidirectional"
        result.append(seg)
    return result


def v9_rows():
    """Retained v9 rows keyed by their bound native (reference, pin), and all rows by Connector_Pin."""
    bindings = json.loads((V9_DIR / "bindings.json").read_text())
    rows, by_id = {}, {}
    with (V9_DIR / "io-map.csv").open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_line"] = reader.line_num
            by_id[row["Connector_Pin"]] = row
            term = bindings["terminals"].get(row["Connector_Pin"])
            if term:
                refs = [loc["reference"] for loc in bindings["components"][term["component"]]["locations"]]
                if len(refs) == 1:
                    rows[(refs[0], term["pin"])] = row
    return rows, by_id


def v9_origin(source: dict):
    """The v9 io-map origin: retained path, original revision and digest, checked against git."""
    declared = source["v9_origin"]
    path = REPO / declared["path"]
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    original = subprocess.run(["git", "-C", str(REPO), "show", f"{declared['commit']}:{declared['original_path']}"],
                              capture_output=True, check=False).stdout
    if hashlib.sha256(original).hexdigest() != sha:
        sys.exit(f"{declared['path']} differs from {declared['original_path']} at {declared['commit']}")
    revision = (f"{declared['commit']} (original path {declared['original_path']}; "
                f"moved byte-identical to {declared['path']} by {declared['moved_by']})")
    return {"path": declared["path"], "revision": revision, "sha256": sha}


def spec_requirements(source: dict):
    """Rev-3 spec-record entries by ID, after checking their bytes against REQUIREMENTS.md."""
    record = json.loads((REPO / source["spec_record"]).read_text())
    spec = REPO / source["requirements"]
    if spec.name != record["spec"]["name"]:
        sys.exit(f"{source['spec_record']} records {record['spec']['name']}, not {source['requirements']}")
    data = spec.read_bytes()
    if hashlib.sha256(data).hexdigest() != record["spec"]["sha256"]:
        sys.exit(f"{spec.relative_to(REPO)} differs from the spec record {source['spec_record']}")
    entries = {}
    for entry in record["requirements"]:
        loc = entry["locator"]
        if data[loc["byte_start"]:loc["byte_end"]].decode() != entry["text"]:
            sys.exit(f"{entry['id']}: spec-record locator does not match {spec.relative_to(REPO)}")
        entries[entry["id"]] = dict(entry, path=str(spec.relative_to(REPO)), sha256=record["spec"]["sha256"])
    return entries


def generate(raw: bytes, source: dict):
    nl = Netlist(raw)
    mcu = source["mcu"]["reference"]
    if nl.comps[mcu]["value"] != source["mcu"]["value"]:
        sys.exit(f"{mcu} is {nl.comps[mcu]['value']!r}, source.json declares {source['mcu']['value']!r}")
    carried, v9_by_id = v9_rows()
    spec = spec_requirements(source)
    contacts = sorted((r for r in nl.comps if CONTACT_REF.fullmatch(r)), key=natural)
    components, terminals, paths, rows = {}, {}, {}, []
    origin = v9_origin(source)
    located = {}

    def locate(rid, old, keys):
        located[rid] = (f"row {old['_line']} ({old['Connector_Pin']}): carried {', '.join(keys)}; "
                        "not requalified for Rev-3")

    def bind(tid, ref, pin):
        comp = nl.comps[ref]
        components.setdefault(ref, {"locations": [{"sheet": comp["sheet"], "reference": ref}],
                                    "symbols": [comp["symbol"]]})
        terminals[tid] = {"component": ref, "pin": pin}
        return tid

    short = source["sha256"][:12]
    for ref in contacts:
        for pin in sorted(nl.comps[ref]["pins"], key=natural):
            rid = f"{ref}-{pin}"
            bind(rid, ref, pin)
            old = carried.get((ref, pin))
            row = dict.fromkeys(COLUMNS, "N/A")
            row["Connector_Pin"] = rid
            if nl.unconnected(ref, pin):
                row.update(Signal_Name="NO_CONNECT", Net="N/C", Direction_Class="No_Connect",
                           External_Destination="unused: native no-connect; cavity plug not selected (unknown)")
                note = "native no-connect"
                old = None
            else:
                net = nl.net_of[(ref, pin)]
                row.update(Signal_Name=net.lstrip("/"), Net=net)
                mcu_pins = sorted((p for r, p in nl.nodes[net] if r == mcu), key=natural)
                if nl.rail(net):
                    note = "rail net (power pin on net); no MCU pin declared"
                elif len(mcu_pins) == 1:
                    row.update(MCU_Ref=mcu, MCU_Pin=mcu_pins[0], MCU_Path="direct")
                    bind(f"{mcu}:{mcu_pins[0]}", mcu, mcu_pins[0])
                    note = f"direct to {mcu}:{mcu_pins[0]}"
                elif mcu_pins:
                    sys.exit(f"{rid}: net {net} holds several MCU pins {mcu_pins}; no direct form exists")
                else:
                    chains = sorted(trace(nl, mcu, ref, pin),
                                    key=lambda c: (natural(c[0][-1][1]), [natural(r) + natural(p) for r, p in c[0]]))
                    ids, pins_out, devices_seen = [], [], []
                    for terms, roles in chains:
                        mpin = terms[-1][1]
                        base = f"{rid}.{mcu}-{mpin}"
                        same = sum(1 for t, _ in chains if t[-1][1] == mpin)
                        pid = base if same == 1 else f"{base}.{sum(1 for i in ids if i.startswith(base + '.')) + 1}"
                        tids = [rid] + [bind(f"{r}:{p}", r, p) for r, p in terms[1:]]
                        devices = []
                        for k, role in enumerate(roles):
                            dref = terms[2 * k + 1][0]
                            bind(f"{dref}:{terms[2 * k + 1][1]}", dref, terms[2 * k + 1][1])
                            devices.append({"component": dref, "value": nl.comps[dref]["value"], "role": role})
                            if dref not in devices_seen:
                                devices_seen.append(dref)
                        paths[pid] = {"terminals": tids, "pin_names": [nl.name(r, p) for r, p in terms],
                                      "devices": devices, "directions": directions(nl, terms, roles)}
                        ids.append(pid)
                        pins_out.append(mpin)
                    if ids:
                        row.update(MCU_Ref=mcu, MCU_Pin=";".join(pins_out), MCU_Path=";".join(ids))
                        note = f"indirect: {len(ids)} path{'s' if len(ids) != 1 else ''} via {','.join(devices_seen)}"
                    else:
                        note = f"no declared crossing reaches {mcu}"
                if old is not None and old["Net"] != net:
                    old = None
            if old is not None:
                row.update({k: old[k] for k in CARRIED})
                note += (f"; Direction_Class, Voltage_Current_Domain and External_Destination carried from v9 row "
                         f"{old['Connector_Pin']} (same native pin, identical net; not requalified for Rev-3)")
                ids = sorted(set(INTERFACE_ID.findall(old["Notes"])))
                unknown = [i for i in ids if i not in spec]
                if unknown:
                    sys.exit(f"{rid}: v9 row {old['Connector_Pin']} cites {unknown}, absent from the Rev-3 spec record")
                if ids:
                    note += f"; v9 interface citations carried: {', '.join(ids)}"
                locate(rid, old, CARRIED + (("POD-IF citations",) if ids else ()))
            elif row["Net"] != "N/C":
                row.update(Direction_Class="unknown", Voltage_Current_Domain="unknown",
                           External_Destination="unknown")
                note += "; direction, domain and external destination unknown (no committed per-pin source)"
            row["Notes"] = f"Rev-3 source {short}; {note}"
            rows.append(row)
    for decl in source.get("wireless", []):
        old = v9_by_id[decl["v9_row"]]
        if old["Net"] != "N/A" or old["Direction_Class"] != "Bidirectional_RF":
            sys.exit(f"v9 row {decl['v9_row']} is not a wireless row")
        missing = [i for i in decl["requirements"] if i not in spec]
        if missing:
            sys.exit(f"{decl['row']}: {missing} absent from the Rev-3 spec record")
        cites = ", ".join(f"{i} (bytes {spec[i]['locator']['byte_start']}-{spec[i]['locator']['byte_end']})"
                          for i in decl["requirements"])
        row = dict.fromkeys(COLUMNS, "N/A")
        row.update(Connector_Pin=decl["row"], Signal_Name=old["Signal_Name"], **{k: old[k] for k in CARRIED})
        row["Notes"] = (f"Rev-3 source {short}; declared wireless obligation: no native pin, net or MCU pin "
                        f"(none invented); not evaluated by the topology gate; requirements {cites} of "
                        f"{source['requirements']} sha256 {spec[decl['requirements'][0]]['sha256'][:12]}, "
                        f"via {source['spec_record']}; "
                        f"Signal_Name, Direction_Class, Voltage_Current_Domain and External_Destination carried "
                        f"from v9 row {old['Connector_Pin']} (not requalified for Rev-3)")
        if not set(INTERFACE_ID.findall(row["Notes"])) <= set(INTERFACE_ID.findall(old["Notes"])):
            sys.exit(f"{decl['row']}: cites POD-IF IDs that v9 row {old['Connector_Pin']} does not")
        locate(decl["row"], old, ("Signal_Name",) + CARRIED + ("POD-IF citations",))
        rows.append(row)
    out = io.StringIO()
    writer = csv.DictWriter(out, COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    for row in rows:
        # Every cited ID must come from a located v9 row; nothing else may carry one.
        cited = set(INTERFACE_ID.findall(row["Notes"]))
        if cited and row["Connector_Pin"] not in located:
            sys.exit(f"{row['Connector_Pin']}: cites {sorted(cited)} without a v9 origin row")
    history = {"schema": "agent-ee.io-map-history/1", "origin": dict(origin, locator=UNCARRIED),
               "rows": located, "sourced": {}}
    used = {t for p in paths.values() for t in p["terminals"]} | {r["Connector_Pin"] for r in rows} | {
        f"{r['MCU_Ref']}:{r['MCU_Pin']}" for r in rows if r["MCU_Path"] == "direct"}
    bindings = {"schema": "agent-ee.interface/1",
                "components": {c: components[c] for c in sorted(components, key=natural)},
                "terminals": {t: terminals[t] for t in terminals if t in used},
                "allowed_edits": [], "invariants": []}
    # interface/1 requires invariants; the compiler borrows only components and terminals.
    for cid in bindings["components"]:
        bindings["invariants"].append({
            "id": f"present:{cid}", "kind": "component", "requirement": "POD-AC-1-pinout",
            "source": {"path": source["schematic"], "locator": f"native netlist component {cid}",
                       "sha256": source["sha256"]},
            "component": cid, "populated": True})
    return {
        "io-map": out.getvalue().encode(),
        "bindings": (json.dumps(bindings, indent=2) + "\n").encode(),
        "paths": (json.dumps({"schema": "agent-ee.io-map-paths/1", "paths": paths}, indent=2) + "\n").encode(),
        "history": (json.dumps(history, indent=2) + "\n").encode(),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--netlist", help="use this kicad-cli XML netlist instead of exporting one")
    ap.add_argument("--check", action="store_true", help="compare with the committed files; write nothing")
    args = ap.parse_args(argv)
    source = json.loads(SOURCE_JSON.read_text())
    schematic = REPO / source["schematic"]
    actual = hashlib.sha256(schematic.read_bytes()).hexdigest()
    if actual != source["sha256"]:
        sys.exit(f"{source['schematic']} sha256 {actual} differs from source.json {source['sha256']}")
    raw = Path(args.netlist).read_bytes() if args.netlist else export_netlist(schematic)
    files = generate(raw, source)
    stale = [k for k, data in files.items() if not OUTPUTS[k].is_file() or OUTPUTS[k].read_bytes() != data]
    if args.check:
        if stale:
            print("FAIL: regenerated " + ", ".join(str(OUTPUTS[k].relative_to(REPO)) for k in stale)
                  + " differ from the committed files")
            return 1
        print(f"PASS: io-map, bindings, paths and history reproduce byte-identically from {source['schematic']}")
        return 0
    for key, data in files.items():
        OUTPUTS[key].write_bytes(data)
    print(f"wrote {', '.join(str(p.relative_to(REPO)) for p in OUTPUTS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
