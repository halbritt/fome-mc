#!/usr/bin/env python3
"""Verify a project's I/O map and hardware interface contracts.

The default fome-mc audit also checks its ECU-specific pin expectations, firmware
board configuration, connector YAML and sheet-contract documentation. Other
projects use the FOMEMC-30 CSV header, optionally with MCU_Path; see toolchain/README.md
for the input contract and contract locations.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# fome-mc pins no agent-ee: it uses the agent-ee CLI on PATH. This asks that CLI's own
# interpreter where agent_ee lives and digests the modules the pod contract depends on.
AGENT_EE_PROBE = """
import hashlib, importlib.metadata, json
from pathlib import Path
import agent_ee
pkg = Path(agent_ee.__file__).resolve().parent
dist = importlib.metadata.distribution("agent-ee")
print(json.dumps({"src": str(pkg.parent), "version": dist.version,
                  "direct_url": json.loads(dist.read_text("direct_url.json") or "null"),
                  "modules": {"agent_ee/" + n: hashlib.sha256((pkg / n).read_bytes()).hexdigest()
                              for n in ("io_map.py", "hardware_interface.py", "symbol_library.py")}}))
"""


def agent_ee_on_path() -> dict:
    """The agent-ee CLI on PATH: its interpreter, the source it imports and that source's commit."""
    cli = shutil.which("agent-ee")
    if cli is None:
        raise SystemExit("agent-ee is not on PATH; fome-mc uses the installed agent-ee CLI")
    script = Path(cli).resolve()
    shebang = script.read_bytes().split(b"\n", 1)[0]
    if not shebang.startswith(b"#!"):
        raise SystemExit(f"agent-ee on PATH ({script}) is not a Python console script")
    python = shebang[2:].decode().strip()
    probe = subprocess.run([python, "-I", "-c", AGENT_EE_PROBE], capture_output=True, text=True, check=False)
    if probe.returncode != 0:
        raise SystemExit(f"agent-ee on PATH ({cli}) does not import agent_ee: {probe.stderr.strip()}")
    info = json.loads(probe.stdout)
    src = Path(info["src"])
    git = ["git", "-C", str(src)]
    commit = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
    dirty = subprocess.run(git + ["status", "--porcelain", "--", "."], capture_output=True, text=True,
                           check=False).stdout.strip() if commit else ""
    if not commit:
        commit = ((info["direct_url"] or {}).get("vcs_info") or {}).get("commit_id", "")
    return {"cli": cli, "python": python, "src": src, "version": info["version"], "commit": commit,
            "dirty": bool(dirty), "modules": info["modules"]}


AGENT_EE = agent_ee_on_path()
sys.path.insert(0, str(AGENT_EE["src"]))

try:
    from agent_ee.hardware_interface import (  # noqa: E402
        atom, capability, declared_pins, evaluate, qualify_global_names, read_inventory,
        resolve_components, strict_json, verify_contract,
    )
except ImportError as exc:
    raise SystemExit(f"agent-ee on PATH ({AGENT_EE['cli']}, {AGENT_EE['src']} @ {AGENT_EE['commit'] or 'unknown'}) "
                     f"lacks the AGENTEE-188 qualification-record loader: {exc}") from exc
from agent_ee.symbol_library import children, field, parse_sexpr  # noqa: E402

REPO = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).resolve().parent, text=True
).strip())
sys.path.insert(0, str(REPO / "toolchain"))
import eda  # noqa: E402

IO_MAP_CSV = REPO / "io-map.csv"
NETLIST = REPO / "export/fome-mc.net"
ROOT_SCH = REPO / "fome-mc.kicad_sch"
SHEETS_DIR = REPO / "sheets"
CONTRACTS_DIR = REPO / "contracts"
SHEET_CONTRACTS_MD = REPO / "docs/SHEET_CONTRACTS.md"
FW_DIR = Path.home() / "git/fome-fw/firmware/config/boards/fome-mc"
BOARD_CFG = FW_DIR / "board_configuration.cpp"
CONN_DIR = FW_DIR / "connectors"

# Expected netlist net name and at least one required component:pin on that net for each J1/J2 pin
EXPECTED_PIN_NETS = {
    "J1-1":  ("/LS1",            "U1001:6", "D201:2"),
    "J1-2":  ("/LS2",            "U1001:8", "D202:2"),
    "J1-3":  ("/LS3",            "U1002:6", "D203:2"),
    "J1-4":  ("/LS4",            "U1002:8", "D204:2"),
    "J1-5":  ("GND",             "U26:16"),
    "J1-6":  ("/IGN1_COIL",      "Q201:2"),
    "J1-7":  ("/IGN2_COIL",      "Q202:2"),
    "J1-8":  ("/IGN3_COIL",      "Q203:2"),
    "J1-9":  ("/IGN4_COIL",      "Q204:2"),
    "J1-10": ("/LS5",            "U1101:6", "D205:2"),
    "J1-11": ("/LS6",            "U1101:8", "D206:2"),
    "J1-12": ("/LS7",            "U1102:6", "D207:2"),
    "J1-13": ("/LS8",            "U1102:8", "D208:2", "R212:2"),
    "J1-14": ("/MAIN_RLY",       "U1202:6", "D209:2"),
    "J1-15": ("/ETB1_OUT+",      "U201:5"),
    "J1-16": ("/ETB1_OUT-",      "U201:7"),
    "J1-17": ("/ETB2_OUT+",      "U203:5"),
    "J1-18": ("/ETB2_OUT-",      "U203:7"),
    "J1-19": ("/STEP_1A",        "U202:5"),
    "J1-20": ("/STEP_1B",        "U202:7"),
    "J1-21": ("/STEP_2A",        "U202:10"),
    "J1-22": ("/STEP_2B",        "U202:8"),
    "J1-23": ("/WBO1_H-",        "Q301:2"),
    "J1-24": ("/12V_MR",         "D201:1"),
    "J1-25": ("/WBO2_H-",        "Q401:2"),
    "J1-26": ("/12V_IGN_SW",     "D20:2", "R96:1"),
    "J1-27": ("/12V_MR",         "D201:1", "D21:2", "D22:1"),
    "J1-28": ("/Perm_Live",      "D16:2"),
    "J1-29": ("/5V_SENSOR_1",    "U1:1", "R219:1"),
    "J1-30": ("/5V_SENSOR_2",    "U2:1"),
    "J1-31": ("GND",             "U26:31"),
    "J1-32": ("GND",             "U26:16"),
    "J1-33": ("GND",             "U26:16"),
    "J1-34": ("GND",             "U26:16"),
    "J1-35": ("/USB_VBUS_BOOT0", "D210:1", "R217:1"),
    "J2-1":  ("/AT1",            "R39:2"),
    "J2-2":  ("/AT2",            "R40:2"),
    "J2-3":  ("/AV2",            "R52:1"),
    "J2-4":  ("/AV4",            "R54:1"),
    "J2-5":  ("/AV1",            "R51:1"),
    "J2-6":  ("/AV3",            "R53:1"),
    "J2-7":  ("/AV5",            "R63:1"),
    "J2-8":  ("/AV6",            "R64:1", "R219:2"),
    "J2-9":  ("/KNOCK_1",        "C16:2"),
    "J2-10": ("/KNOCK_2",        "C17:2"),
    "J2-11": ("/VR1+",           "R35:1"),
    "J2-12": ("/VR1-",           "R36:1"),
    "J2-13": ("/VR2+",           "R37:1"),
    "J2-14": ("/VR2-",           "R38:1"),
    "J2-15": ("/DIGITAL_2",      "R24:2"),
    "J2-16": ("/DIGITAL_1",      "R23:2"),
    "J2-17": ("/DIGITAL_4",      "R26:2"),
    "J2-18": ("/DIGITAL_3",      "R25:2"),
    "J2-19": ("/WBO1_VM",        "U302:7"),
    "J2-20": ("/WBO1_IP",        "R310:2"),
    "J2-21": ("/WBO1_RTRIM",     "R310:1"),
    "J2-22": ("/WBO1_UN",        "U301:10"),
    "J2-23": ("/IGN5",           "R112:1"),
    "J2-24": ("/IGN6",           "R113:1"),
    "J2-25": ("/IGN7",           "R114:1"),
    "J2-26": ("/IGN8",           "R115:1"),
    "J2-27": ("/LS14",           "U1201:8"),
    "J2-28": ("/CAN+",           "U4:7", "D4:2"),
    "J2-29": ("/CAN-",           "U4:6", "D4:1"),
    "J2-30": ("/WBO2_VM",        "U402:7"),
    "J2-31": ("/WBO2_IP",        "R410:2"),
    "J2-32": ("/WBO2_RTRIM",     "R410:1"),
    "J2-33": ("/WBO2_UN",        "U401:10"),
    "J2-34": ("/USB_D+",         "U26:104", "U27:1"),
    "J2-35": ("/USB_D-",         "U26:103", "U27:3"),
}

EXPECTED_INTERNAL_NODES = {
    "INTERNAL-CAN2_RX":       ("/mcu/CAN2_RX",     "U26:73",  "U5:4"),
    "INTERNAL-CAN2_TX":       ("/mcu/CAN2_TX",     "U26:74",  "U5:1"),
    "INTERNAL-WBO1_NRST":     ("/WBO1_NRST",       "U26:118", "U302:4"),
    "INTERNAL-WBO1_BOOT0":    ("/WBO1_BOOT0",      "U26:119", "U302:31"),
    "INTERNAL-WBO2_NRST":     ("/WBO2_NRST",       "U26:122", "U402:4"),
    "INTERNAL-WBO2_BOOT0":    ("/WBO2_BOOT0",      "U26:123", "U402:31"),
    "INTERNAL-WBO1_SEL":      ("GND",              "U302:15"),
    "INTERNAL-WBO2_SEL":      ("+3V3_WBO2",        "U402:18", "U409:2"),
    "INTERNAL-SDMMC_D0":      ("/mcu/SD_D0",       "U26:98",  "U25:7", "R127:2"),
    "INTERNAL-SDMMC_D1":      ("/mcu/SD_D1",       "U26:99",  "U25:8", "R128:2"),
    "INTERNAL-SDMMC_D2":      ("/mcu/SD_D2",       "U26:111", "U25:1", "R129:2"),
    "INTERNAL-SDMMC_D3":      ("/mcu/SD_D3",       "U26:112", "U25:2", "R130:2"),
    "INTERNAL-SDMMC_CK":      ("/mcu/SD_CLK",      "U26:113", "R132:1"),
    "INTERNAL-SDMMC_CMD":     ("/mcu/SD_CMD",      "U26:116", "U25:3", "R131:2"),
    "INTERNAL-BARO_I2C":      ("/mcu/BARO_SCL",    "U26:69",  "U24:2"),
    "INTERNAL-PWR_KEEPALIVE": ("/lowside_quad4/IN3","U26:141", "RN9:6", "U1203:9"),
    "INTERNAL-WIFI_SCK":      ("/mcu/WIFI_SCK",    "U26:1",   "U29:18"),
    "INTERNAL-WIFI_IRQ":      ("/mcu/WIFI_IRQ",    "U26:2",   "U29:13"),
    "INTERNAL-WIFI_CS":       ("/mcu/WIFI_CS",     "U26:3",   "U29:16"),
    "INTERNAL-WIFI_MISO":     ("/mcu/WIFI_MISO",   "U26:4",   "U29:17"),
    "INTERNAL-WIFI_MOSI":     ("/mcu/WIFI_MOSI",   "U26:5",   "U29:15"),
    "INTERNAL-WIFI_RST":      ("/mcu/WIFI_RST",    "U26:7",   "U29:4"),
}


PROJECT_MAP_COLUMNS = [
    "Connector_Pin", "Signal_Name", "Net", "Direction_Class",
    "Voltage_Current_Domain", "MCU_Ref", "MCU_Pin", "External_Destination", "Notes",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", default="fome-mc", help="Project from toolchain/versions.toml")
    ap.add_argument("--compile", action="store_true",
                    help="telemetry-pod only: regenerate the contract, record and compile receipt with the "
                         "agent-ee on PATH, then stop")
    args = ap.parse_args()
    cfg = eda.project_config(args.project)
    if args.compile:
        if args.project != "telemetry-pod":
            ap.error("--compile applies to --project telemetry-pod")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        run_dir = REPO / "build/runs/verify-io/telemetry-pod" / stamp
        run_dir.mkdir(parents=True)
        for rel, path in compile_pod(run_dir).items():
            shutil.copyfile(path, REPO / rel)
            print(f"wrote {rel}")
        print(f"compiler: agent-ee {AGENT_EE['version']} @ {AGENT_EE['commit']} ({AGENT_EE['cli']})")
        return 0
    if args.project != "fome-mc":
        try:
            return verify_project_io(cfg)
        except (OSError, ValueError, csv.Error) as exc:
            print(f"FAIL: project {args.project}: {exc}", file=sys.stderr)
            return 1
    return verify_fome_mc()


def verify_fome_mc() -> int:
    errors = []
    rows = list(csv.DictReader(IO_MAP_CSV.open()))
    pin_rows = {r["Connector_Pin"]: r for r in rows}

    # 1. Verify all 70 J1/J2 pins + 22 INTERNAL rows exist in io-map.csv
    for j in ("J1", "J2"):
        for n in range(1, 36):
            key = f"{j}-{n}"
            if key not in pin_rows:
                errors.append(f"Missing {key} in io-map.csv")
    for k in EXPECTED_INTERNAL_NODES:
        if k not in pin_rows:
            errors.append(f"Missing {k} in io-map.csv")

    # 2. Parse exported netlist
    net_text = NETLIST.read_text()
    comps = re.findall(r'\(comp\s+\(ref\s+"([^"]+)"\)\s+\(value\s+"([^"]+)"\)', net_text)
    unannotated = [c for c in comps if "?" in c[0]]
    duplicates = [k for k, v in Counter(c[0] for c in comps).items() if v > 1]
    if unannotated:
        errors.append(f"Unannotated components in netlist: {unannotated}")
    if duplicates:
        errors.append(f"Duplicate component references in netlist: {duplicates}")

    nets = {}
    pin_to_net = {}
    for m in re.finditer(r'\(net\s+\(code\s+"\d+"\)\s+\(name\s+"([^"]+)"\)(.*?)\n\t\t\)', net_text, re.S):
        nname = m.group(1)
        nodes = [f"{r}:{p}" for r, p in re.findall(r'\(ref\s+"([^"]+)"\)\s*\(pin\s+"([^"]+)"\)', m.group(2))]
        nets[nname] = set(nodes)
        for nd in nodes:
            pin_to_net[nd] = nname

    # 3. Verify every J1/J2 pin in netlist
    for j_pin, exp_tuple in EXPECTED_PIN_NETS.items():
        exp_net = exp_tuple[0]
        req_nodes = exp_tuple[1:]
        ref, num = j_pin.split("-")
        nd_key = f"{ref}:{num}"
        actual_net = pin_to_net.get(nd_key)
        if actual_net != exp_net:
            errors.append(f"{j_pin} ({nd_key}): expected net '{exp_net}', got '{actual_net}'")
            continue
        for req in req_nodes:
            if req not in nets.get(actual_net, set()):
                errors.append(f"{j_pin} net '{actual_net}' missing expected node '{req}' (has {sorted(nets.get(actual_net, set()))[:8]})")

    # 4. Verify every INTERNAL-* signal in netlist
    for int_key, exp_tuple in EXPECTED_INTERNAL_NODES.items():
        exp_net = exp_tuple[0]
        req_nodes = exp_tuple[1:]
        if exp_net not in nets:
            errors.append(f"{int_key}: expected net '{exp_net}' not found in netlist")
            continue
        for req in req_nodes:
            if req not in nets[exp_net]:
                errors.append(f"{int_key} net '{exp_net}' missing expected node '{req}' (has {sorted(nets[exp_net])[:8]})")

    # 5. Verify CAN1 and CAN2 are separate differential buses and CAN2 connects U5 (psu), U307 (wbo1), U407 (wbo2)
    if nets.get("/CAN+") == nets.get("/CAN2+"):
        errors.append("CAN1 (/CAN+) and CAN2 (/CAN2+) are shorted together!")
    for can2_node in ("U5:7", "U307:7", "U407:7", "J2:30"):
        # Note J2:30 is WBO2_VM in io-map.csv; CAN2 is internal between U5, U307, U407
        if can2_node != "J2:30" and can2_node not in nets.get("/CAN2+", set()):
            errors.append(f"Internal CAN2+ missing transceiver node {can2_node}")
    for can2_node in ("U5:6", "U307:6", "U407:6"):
        if can2_node not in nets.get("/CAN2-", set()):
            errors.append(f"Internal CAN2- missing transceiver node {can2_node}")

    # 6. Verify firmware board_configuration.cpp and connectors/*.yaml pin mappings match io-map.csv
    bcfg = BOARD_CFG.read_text()
    required_fw_snippets = [
        "Gpio::G5, // INJ1",
        "Gpio::G6, // INJ2",
        "Gpio::G7, // INJ3",
        "Gpio::G8, // INJ4",
        "Gpio::B3,  // IGN1 / IGBT1",
        "Gpio::G15, // IGN2 / IGBT2",
        "Gpio::G14, // IGN3 / IGBT3",
        "Gpio::G13, // IGN4 / IGBT4",
        "engineConfiguration->idle.stepperStepPin = Gpio::B4;",
        "engineConfiguration->idle.stepperDirectionPin = Gpio::B7;",
        "engineConfiguration->stepperEnablePin = Gpio::B8;",
        "engineConfiguration->canTxPin = Gpio::D1;",
        "engineConfiguration->canRxPin = Gpio::D0;",
        "engineConfiguration->can2RxPin = Gpio::B12;",
        "engineConfiguration->can2TxPin = Gpio::B13;",
        "engineConfiguration->lps25BaroSensorScl = Gpio::Unassigned;",
        "engineConfiguration->lps25BaroSensorSda = Gpio::Unassigned;",
        "engineConfiguration->baroSensor.hwChannel = EFI_ADC_2;",
        "engineConfiguration->baroSensor.type = MT_GM_1_BAR;",
        "engineConfiguration->is_enabled_spi_4 = true;",
        "engineConfiguration->spi4sckPin = Gpio::E2;",
        "engineConfiguration->spi4misoPin = Gpio::E5;",
        "engineConfiguration->spi4mosiPin = Gpio::E6;",
        "spi_device_e getWifiSpiDevice()",
        "Gpio getWifiCsPin()",
        "Gpio getWifiResetPin()",
        "Gpio getWifiIsrPin()",
        'efiSetPadMode("WBO1_NRST", Gpio::D4',
        'efiSetPadMode("WBO1_BOOT0", Gpio::D5',
        'efiSetPadMode("WBO2_NRST", Gpio::D6',
        'efiSetPadMode("WBO2_BOOT0", Gpio::D7',
    ]
    for snip in required_fw_snippets:
        if snip not in bcfg:
            errors.append(f"board_configuration.cpp missing expected mapping: {snip}")

    yaml_pins = {}
    for yfile in sorted(CONN_DIR.glob("*.yaml")):
        ytext = yfile.read_text()
        for m in re.finditer(r"-\s+pin:\s+(J[12]-\d+)", ytext):
            yaml_pins[m.group(1)] = yfile.name
            if m.group(1) not in pin_rows:
                errors.append(f"{yfile.name} references {m.group(1)} not in io-map.csv")

    # 7. Verify docs/SHEET_CONTRACTS.md and contracts/*.interface.json against schematic hierarchy & fresh XML netlist
    sheet_stats = verify_sheet_contracts(errors)

    if errors:
        print("FAILED io-map / netlist / firmware / sheet-contract verification:")
        for e in errors:
            print("  [ERROR]", e)
        return 1

    print(f"PASS: Verified {len(EXPECTED_PIN_NETS)} external connector pins (J1-1..35, J2-1..35),")
    print(f"      {len(EXPECTED_INTERNAL_NODES)} internal MCU/WBO/SDNAND/Baro buses,")
    print(f"      {len(comps)} netlist components (0 unannotated, 0 duplicates),")
    print(f"      {len(yaml_pins)} TunerStudio YAML connector definitions + board_configuration.cpp,")
    print(
        f"      and {sheet_stats['contracts']} contracts/*.interface.json files "
        f"({sheet_stats['instances']} sheet instances, {sheet_stats['unique_hlabels']} hierarchical labels, "
        f"{sheet_stats['pin_bindings']} instance-pin bindings, {sheet_stats['invariants']} invariants evaluated)."
    )
    return 0


def _find_kicad_cli() -> str:
    pinned = Path.home() / ".local/opt/kicad-10.0.7/bin/kicad-cli"
    if pinned.exists():
        return str(pinned)
    found = shutil.which("kicad-cli")
    if found:
        return found
    raise FileNotFoundError("kicad-cli not found in ~/.local/opt/kicad-10.0.7/bin or PATH")


def load_contract(root: Path, rel: str) -> dict:
    """A contract that declares no qualification record (the ECU's legacy contracts).

    A qualification-bound contract cannot load here: verify_contract refuses it without
    its record and captured inputs. The pod goes through capability() instead."""
    return verify_contract(strict_json((Path(root) / rel).read_bytes(), f"interface contract {rel}"))[0]


def fresh_inventory(cfg: dict, contracts=(), expect_sha256=None) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = REPO / "build/runs/verify-io" / cfg["name"] / stamp
    run_dir.mkdir(parents=True)
    snap, metadata = eda.make_snapshot(cfg, run_dir)
    if expect_sha256 is not None:
        actual = hashlib.sha256((snap / cfg["schematic"]).read_bytes()).hexdigest()
        if actual != expect_sha256:
            raise ValueError(f"snapshot {cfg['schematic']} sha256 {actual} differs from pinned {expect_sha256}")
    if metadata["missing_sheets"] or metadata["sheet_case_aliases"]:
        raise ValueError(f"invalid schematic hierarchy; see {run_dir / 'snapshot.json'}")
    xml_path = run_dir / "design.xml"
    proc = subprocess.run(
        [_find_kicad_cli(), "sch", "export", "netlist", "--format", "kicadxml",
         "--output", str(xml_path), str(snap / cfg["schematic"])],
        cwd=snap, env=eda.tool_env(), capture_output=True, text=True, check=False,
    )
    (run_dir / "netlist.log").write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0 or not xml_path.exists():
        raise ValueError(f"kicad-cli sch export netlist failed (rc={proc.returncode}); see {run_dir / 'netlist.log'}")
    inventory = read_inventory(xml_path)
    if contracts:
        # Only the design's own sheet hierarchy, as agent-ee's native check does. Other
        # schematics under the project (retained copies of the same design) would make
        # its symbol UUIDs ambiguous.
        schematics = {Path(rel).as_posix(): parse_sexpr((snap / rel).read_bytes())
                      for rel in metadata["schematic_files"]}
        pins = set().union(*(declared_pins(c, inventory) for c in contracts))
        qualify_global_names(inventory, schematics, atom(schematics[cfg["schematic"]], "uuid"), pins)
    return inventory


def read_project_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames not in (PROJECT_MAP_COLUMNS, PROJECT_MAP_COLUMNS + ["MCU_Path"]):
            raise ValueError("io-map.csv header must be exactly " + ",".join(PROJECT_MAP_COLUMNS)
                             + " (optionally followed by ,MCU_Path)")
        pins = {}
        for row in reader:
            if None in row or any(value is None or not value.strip() for value in row.values()):
                raise ValueError(f"invalid io-map row: {row!r}")
            identity = row["Connector_Pin"].strip()
            net = row["Net"].strip()
            if identity in pins:
                raise ValueError(f"duplicate io-map connector pin {identity}")
            if net == "N/C" and not (row["Direction_Class"] == "No_Connect"
                                         and row["Signal_Name"] == "NO_CONNECT"
                                         and row["MCU_Ref"] == row["MCU_Pin"] == "N/A"):
                raise ValueError(f"{identity}: N/C requires an explicit No_Connect row without MCU pins")
            pins[identity] = {k: v.strip() for k, v in row.items()}
    if not pins:
        raise ValueError("io-map.csv contains no connector pins")
    return pins


def read_project_map(path: Path) -> dict[str, str]:
    return {identity: row["Net"] for identity, row in read_project_rows(path).items()}


def compile_pod(out_dir: Path) -> dict[str, Path]:
    """The one pod compile path: the agent-ee on PATH compiles the contract and its record, and
    a receipt records that compiler's identity. Regeneration and verification both use this."""
    if not AGENT_EE["commit"] or AGENT_EE["dirty"]:
        raise ValueError(f"agent-ee on PATH ({AGENT_EE['cli']}, source {AGENT_EE['src']}) has "
                         f"{'uncommitted changes' if AGENT_EE['dirty'] else 'no recoverable commit'}; "
                         "the compile receipt must name an exact commit")
    out = {POD_CONTRACT: out_dir / Path(POD_CONTRACT).name, POD_RECORD: out_dir / Path(POD_RECORD).name,
           POD_RECEIPT: out_dir / Path(POD_RECEIPT).name}
    def arguments(contract, record):
        return ["telemetry-pod/io-map.csv", "--csv-path", "telemetry-pod/io-map.csv",
                "--requirement", "POD-AC-1-pinout", "--source", POD_REQUIREMENTS,
                "--locator", "Acceptance criteria / item 1", "--require-source-sha256",
                "--bindings", "telemetry-pod/pinout-checks/bindings.json",
                "--paths", "telemetry-pod/pinout-checks/paths.json",
                "--history", POD_HISTORY, "--history-source", POD_V9_ORIGIN,
                "--record-path", POD_RECORD, "--record-out", record, "--out", contract]
    proc = subprocess.run([AGENT_EE["python"], "-m", "agent_ee.io_map",
                           *arguments(str(out[POD_CONTRACT]), str(out[POD_RECORD]))], cwd=REPO,
                          env=eda.tool_env(), capture_output=True, text=True, check=False)
    (out_dir / "compile.log").write_text(f"agent-ee on PATH: {AGENT_EE['cli']} -> {AGENT_EE['python']}, "
                                         f"source {AGENT_EE['src']} @ {AGENT_EE['commit']}\n"
                                         + proc.stdout + proc.stderr)
    if proc.returncode != 0 or not out[POD_CONTRACT].is_file():
        raise ValueError(f"pod contract compile failed (rc={proc.returncode}); see {out_dir / 'compile.log'}")
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()  # noqa: E731
    inputs = ["telemetry-pod/io-map.csv", POD_REQUIREMENTS, "telemetry-pod/pinout-checks/bindings.json",
              "telemetry-pod/pinout-checks/paths.json", POD_HISTORY, POD_V9_ORIGIN]
    receipt = {
        "schema": "fome-mc.pod-contract-compile/1",
        "compiler": {"distribution": "agent-ee", "version": AGENT_EE["version"], "commit": AGENT_EE["commit"],
                     "modules": AGENT_EE["modules"],
                     "entry": "python -m agent_ee.io_map, run by the interpreter of the agent-ee CLI on PATH"},
        "arguments": arguments(POD_CONTRACT, POD_RECORD),
        "inputs": {path: digest(REPO / path) for path in inputs},
        "outputs": {POD_CONTRACT: digest(out[POD_CONTRACT]), POD_RECORD: digest(out[POD_RECORD])},
        "note": ("Provenance of the committed pod contract and qualification record: the agent-ee that compiled "
                 "them. Written by scripts/verify_io_map.py --project telemetry-pod --compile, never by hand; "
                 "verify-io recompiles with the agent-ee on PATH and requires all three files byte for byte."),
    }
    out[POD_RECEIPT].write_text(json.dumps(receipt, indent=2) + "\n")
    return out


def check_pod_compilation(contract_path: Path) -> list[str]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = REPO / "build/runs/verify-io/telemetry-pod" / stamp
    run_dir.mkdir(parents=True)
    try:
        fresh = compile_pod(run_dir)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    for rel, path in fresh.items():
        committed = REPO / rel
        if not committed.is_file() or path.read_bytes() != committed.read_bytes():
            errors.append(f"{rel} differs from a fresh compile by the agent-ee on PATH; "
                          "regenerate with --compile (see telemetry-pod/IO_MAP.md)")
    receipt = REPO / POD_RECEIPT
    if receipt.is_file():
        recorded = json.loads(receipt.read_text()).get("compiler", {}).get("commit")
        if recorded != AGENT_EE["commit"]:
            errors.append(f"{POD_RECEIPT} records agent-ee {recorded}; the agent-ee on PATH is "
                          f"{AGENT_EE['commit']} ({AGENT_EE['src']})")
    return errors


POD_CONTRACT = "contracts/telemetry-pod.interface.json"
POD_RECORD = "contracts/telemetry-pod.qualification.json"
POD_RECEIPT = "contracts/telemetry-pod.compile-receipt.json"
POD_HISTORY = "telemetry-pod/pinout-checks/history.json"
POD_CSV = "telemetry-pod/io-map.csv"
POD_V9_ORIGIN = "telemetry-pod/pinout-checks/v9-pilot/io-map.csv"
POD_REQUIREMENTS = "telemetry-pod/REQUIREMENTS.md"
POD_SOURCE = REPO / "telemetry-pod/pinout-checks/source.json"
POD_GENERATOR = REPO / "telemetry-pod/pinout-checks/generate.py"


def pod_source_config(cfg: dict) -> tuple[dict, list[str]]:
    import json
    source = json.loads(POD_SOURCE.read_text())
    schematic = REPO / source["schematic"]
    native_cfg = dict(cfg, path=schematic.parent.resolve(), schematic=schematic.name)
    actual = hashlib.sha256(schematic.read_bytes()).hexdigest()
    if actual != source["sha256"]:
        return native_cfg, [f"{source['schematic']} sha256 {actual} differs from pinned {source['sha256']}"]
    return native_cfg, []


def check_pod_generation() -> list[str]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = REPO / "build/runs/verify-io/telemetry-pod" / stamp
    run_dir.mkdir(parents=True)
    proc = subprocess.run([sys.executable, str(POD_GENERATOR), "--check"], cwd=REPO, env=eda.tool_env(),
                          capture_output=True, text=True, check=False)
    (run_dir / "generate.log").write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0:
        return [f"pod io-map does not reproduce from its source netlist (rc={proc.returncode}); "
                f"see {run_dir / 'generate.log'}"]
    return []


POD_LOCATOR = re.compile(r"row ([0-9]+) \(([^)]+)\): carried (.+); not requalified for Rev-3")
POD_DESCRIPTIVE = ("Signal_Name", "Direction_Class", "Voltage_Current_Domain", "External_Destination")


def pod_capability() -> dict:
    """The pod contract through agent-ee's scope consumer and its one record loader.

    The scope pins the record path; capability() refuses a contract that does not declare
    that record, a record whose bytes differ from the pin, and any citation the record does
    not bind. It also verifies the v9 origin bytes and returns the requirement authority
    and history."""
    record = REPO / POD_RECORD
    if not record.is_file():
        raise ValueError(f"missing qualification record {POD_RECORD}")
    pin = {"path": POD_RECORD, "sha256": hashlib.sha256(record.read_bytes()).hexdigest()}
    scope = {"baseline": {"requirements": [{
        "id": "POD-AC-1-pinout", "checks": ["interface"],
        "source": {"path": POD_REQUIREMENTS, "locator": "Acceptance criteria / item 1"}}]}}
    files = {POD_CONTRACT, POD_RECORD, POD_CSV, POD_V9_ORIGIN, POD_REQUIREMENTS}
    return capability({"contract": POD_CONTRACT, "netlist_check": "netlist", "qualification_record": pin},
                      scope, files, REPO, "interface")


def check_pod_history(descriptor: dict, rows: dict) -> list[str]:
    """What the loader does not prove: each carried value and ID really is in its v9 row.

    The loader authenticates the v9 origin bytes and binds every citation to the record.
    It does not open the origin row. Here every row located in a v9 row must reproduce
    that row's carried columns and POD-IF IDs. Every other row must carry no ID and no
    descriptive value beyond the generated ones (unknown, N/A, the N/C template)."""
    errors = []
    history = descriptor["requirement_history"]
    if history.get("origin_verification") != {POD_V9_ORIGIN: "verified"}:
        return [f"qualification record origin is not the verified v9 io-map: {history.get('origin_verification')}"]
    if descriptor["requirement_authority"]["sourced"]:
        errors.append("sourced requirement in the pod contract: "
                      f"{descriptor['requirement_authority']['sourced']} (no Rev-3 qualification source is committed)")
    v9 = {}
    reader = csv.DictReader((REPO / POD_V9_ORIGIN).read_text().splitlines(True))
    for row in reader:
        v9[reader.line_num] = row
    record = json.loads((REPO / POD_RECORD).read_bytes())
    for entry in record["rows"]:
        pin, ids = entry["connector_pin"], [r["id"] for r in entry["requirements"]]
        row = rows.get(pin)
        match = POD_LOCATOR.fullmatch(entry["origin"]["locator"])
        if row is None:
            errors.append(f"qualification record row {pin} is not an io-map row")
        elif match is None:
            values = [k for k in POD_DESCRIPTIVE[1:] if row[k] not in ("unknown", "N/A")]
            if ids or (row["Net"] != "N/C" and values):
                errors.append(f"{pin}: {ids or values} without a located v9 origin row")
        else:
            old = v9.get(int(match.group(1)))
            carried = [c for c in match.group(3).split(", ") if c != "POD-IF citations"]
            if old is None or old["Connector_Pin"] != match.group(2):
                errors.append(f"{pin}: v9 origin row {match.group(1)} is not {match.group(2)}")
            elif any(c not in POD_DESCRIPTIVE or old[c] != row[c] for c in carried):
                errors.append(f"{pin}: carried values differ from v9 row {match.group(2)}")
            elif not set(ids) <= set(re.findall(r"\bPOD-IF-[A-Z0-9-]+\b", old["Notes"])):
                errors.append(f"{pin}: cites IDs that v9 row {match.group(2)} does not")
    return errors


def pod_candidate_config(cfg: dict) -> tuple[dict, str, dict]:
    """The candidate pinned in source.json: in place once the project holds it, else its commit."""
    candidate = json.loads(POD_SOURCE.read_text())["candidate"]
    root = REPO / candidate["schematic"]
    cand_cfg = dict(cfg, path=root.parent.resolve(), schematic=root.name)
    manifest_path = REPO / candidate["emission_manifest"]["path"]
    if root.is_file() and hashlib.sha256(root.read_bytes()).hexdigest() == candidate["sha256"]:
        manifest = manifest_path.read_bytes() if manifest_path.is_file() else b""
    else:
        cand_cfg["rev"] = candidate["commit"]
        manifest = subprocess.run(["git", "-C", str(REPO), "show",
                                   f"{candidate['commit']}:{candidate['emission_manifest']['path']}"],
                                  capture_output=True, check=False).stdout
    # The pin must be the emission's own identity: manifest bytes, candidate id and installed schematic.
    if hashlib.sha256(manifest).hexdigest() != candidate["emission_manifest"]["sha256"]:
        raise ValueError(f"candidate emission manifest differs from pinned {candidate['emission_manifest']['sha256']}")
    emitted = json.loads(manifest)
    if (emitted["emission"]["candidate_id"] != candidate["candidate_id"]
            or emitted["project_install"][root.name]["sha256"] != candidate["sha256"]):
        raise ValueError("candidate pin disagrees with its emission manifest")
    return cand_cfg, candidate["sha256"], candidate


def grade(cfg: dict, rows: dict, contract_paths, contracts, inventory, digest: str) -> tuple[list, list, list, int, int]:
    """Native structural grading of every contract against one fresh inventory."""
    pins = {identity: row["Net"] for identity, row in rows.items()}
    errors, wireless, covered = [], [], []
    invariants = satisfied = 0
    native_pins = {(comp["reference"], pin)
                   for comp in inventory["components"].values()
                   if re.fullmatch(r"J[0-9]+", comp["reference"])
                   for pin in comp["pins"]}
    bindings = {}
    for path, contract in zip(contract_paths, contracts):
        resolved = resolve_components(contract, inventory)
        records = evaluate(contract, inventory)
        invariants += len(records)
        for record in records:
            inv = record["expected"]
            citation = inv.get("io_map")
            if citation and citation["sha256"] != digest:
                errors.append(f"{path.name}: stale io-map citation for {record['id']}")
            # Only the pod's explicitly declared wireless row is exempt. It
            # remains unknown and contributes nothing to the satisfied count.
            is_wireless = (cfg["name"] == "telemetry-pod"
                           and record["id"] == "BLE-RADIO:net"
                           and inv["kind"] == "unresolved"
                           and citation is not None
                           and citation["connector_pin"] == "BLE-RADIO"
                           and pins.get("BLE-RADIO") == "N/A"
                           and rows["BLE-RADIO"]["Direction_Class"] == "Bidirectional_RF"
                           and rows["BLE-RADIO"]["MCU_Pin"] == "N/A"
                           and "BLE-RADIO" not in contract["terminals"])
            if is_wireless and record["status"] == "not_evaluated":
                wireless.append("BLE-RADIO")
            elif record["status"] != "satisfied":
                errors.append(f"{path.name}: invariant {record['id']} is {record['status']}")
            else:
                satisfied += 1
        for tid, terminal in contract["terminals"].items():
            if "unresolved" in terminal:
                errors.append(f"{path.name}: unresolved terminal {tid}: {terminal['unresolved']}")
                continue
            component = resolved[terminal["component"]]
            if not component or "error" in component or terminal["pin"] not in component["pins"]:
                errors.append(f"{path.name}: terminal {tid} has no unique supported native pin")
                continue
            native = (component["reference"], terminal["pin"])
            # Compiled maps use logical terminal IDs. Legacy contracts cite
            # their CSV row in the net invariant's source locator.
            identities = {tid} & pins.keys()
            identities.update(i["source"]["locator"] for i in contract["invariants"]
                              if i.get("terminal") == tid and i["source"].get("locator") in pins)
            for identity in identities:
                bindings.setdefault(identity, []).append(native)
    for identity, expected in pins.items():
        if identity in wireless:
            continue
        matches = bindings.get(identity, [])
        if len(matches) != 1:
            errors.append(f"io-map coverage: {identity} requires exactly one resolved contract terminal")
            continue
        native = matches[0]
        covered.append(native)
        actual = inventory["nets"].get(inventory["memberships"].get(native))
        if expected == "N/C":
            if native not in inventory["disconnected"] or native in inventory["unresolved"]:
                errors.append(f"{identity}: N/C requires a proven unconnected native pad")
        elif actual != expected or native in inventory["disconnected"] or native in inventory["unresolved"]:
            errors.append(f"{identity}: expected connected net {expected!r}, got {actual!r}")
    missing = native_pins - set(covered)
    if missing or len(set(covered)) != len(covered):
        errors.append(f"io-map connector coverage: missing={sorted(missing)}, duplicate native bindings="
                      f"{len(covered) - len(set(covered))}")
    # REQUIREMENTS.md requires Bluetooth LE (POD-IF-BLUETOOTH-LE). Its row has no pin
    # to cover, so dropping it would otherwise pass unnoticed.
    if cfg["name"] == "telemetry-pod" and wireless != ["BLE-RADIO"]:
        errors.append("declared wireless obligation BLE-RADIO (POD-IF-BLUETOOTH-LE) is missing; "
                      "it must stay as an unresolved, not_evaluated row")
    return errors, covered, wireless, satisfied, invariants


def verify_project_io(cfg: dict) -> int:
    project_dir = cfg["path"]
    map_path = project_dir / "io-map.csv"
    if not map_path.is_file():
        raise ValueError(f"no io-map for project {cfg['name']}: {map_path}")
    rows = read_project_rows(map_path)
    digest = hashlib.sha256(map_path.read_bytes()).hexdigest()
    errors, native_cfg, descriptor = [], cfg, None
    if cfg["name"] == "telemetry-pod":
        contract_path = REPO / POD_CONTRACT
        if not contract_path.is_file():
            raise ValueError(f"missing interface contract: {contract_path}")
        contract_paths = [contract_path]
        # The map describes the Rev-3 source schematic named in source.json, not the
        # v9 pilot snapshot at the project root; its pinned digest must still match.
        native_cfg, source_errors = pod_source_config(cfg)
        errors = source_errors + check_pod_generation() + check_pod_compilation(contract_path)
        try:
            descriptor = pod_capability()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"FAIL: project {cfg['name']} io-map / contract verification:")
            for error in errors + [f"qualification-bound contract refused by agent-ee capability: {exc}"]:
                print(f"  [ERROR] {error}")
            return 1
        contracts = [descriptor["contract"]]
        errors += check_pod_history(descriptor, rows)
    else:
        contract_paths = sorted((project_dir / "contracts").glob("*.interface.json"))
        if not contract_paths:
            raise ValueError(f"no interface contracts for project {cfg['name']}")
        contracts = [load_contract(project_dir, p.relative_to(project_dir).as_posix()) for p in contract_paths]
    inventory = fresh_inventory(native_cfg, contracts)
    graded, covered, wireless, satisfied, invariants = grade(cfg, rows, contract_paths, contracts, inventory, digest)
    errors += graded
    candidate = None
    if cfg["name"] == "telemetry-pod":
        # The same contract against the actual emitted candidate, bound by its pinned digest.
        cand_cfg, cand_sha, pinned = pod_candidate_config(cfg)
        cand_inventory = fresh_inventory(cand_cfg, contracts, expect_sha256=cand_sha)
        cand_errors, *candidate = grade(cfg, rows, contract_paths, contracts, cand_inventory, digest)
        errors += [f"candidate {pinned['candidate_id'][:12]}: {e}" for e in cand_errors]
        candidate.append(pinned)
    if errors:
        print(f"FAIL: project {cfg['name']} io-map / contract verification:")
        for error in errors:
            print(f"  [ERROR] {error}")
        return 1
    for identity in wireless:
        print(f"NOT_EVALUATED: {identity}: declared wireless row (no electrical connector pin)")
    if descriptor is not None:
        authority, history = descriptor["requirement_authority"], descriptor["requirement_history"]
        print(f"QUALIFICATION: record {history['record']['path']} sha256 {history['record']['sha256']} bound "
              f"to {len(history['rows'])} io-map rows; v9 origin {POD_V9_ORIGIN} "
              f"{history['origin_verification'][POD_V9_ORIGIN]}")
        print(f"REQUIREMENT_AUTHORITY: sourced: {', '.join(authority['sourced']) or 'none'}; "
              f"unqualified-carryover (reported, never authority): {', '.join(authority['unqualified-carryover'])}")
    if native_cfg is not cfg:
        print(f"source schematic: {native_cfg['path'].relative_to(REPO) / native_cfg['schematic']}")
    print(f"PASS: project {cfg['name']}: verified {len(covered)} connector pins, "
          f"{len(contracts)} interface contracts, {satisfied}/{invariants} invariants satisfied "
          f"against fresh netlist; {len(wireless)} declared wireless not_evaluated")
    if candidate is not None:
        c_covered, c_wireless, c_satisfied, c_invariants, pinned = candidate
        where = "project root" if "rev" not in cand_cfg else f"commit {pinned['commit']}"
        print(f"PASS: candidate {pinned['candidate_id']} ({pinned['schematic']} sha256 {pinned['sha256']}, "
              f"{where}): verified {len(c_covered)} connector pins, {c_satisfied}/{c_invariants} invariants "
              f"satisfied against fresh netlist; {len(c_wireless)} declared wireless not_evaluated")
    return 0


def verify_sheet_contracts(errors: list[str]) -> dict[str, int]:
    stats = {
        "contracts": 0,
        "instances": 0,
        "unique_hlabels": 0,
        "pin_bindings": 0,
        "invariants": 0,
    }
    if not SHEET_CONTRACTS_MD.exists():
        errors.append(f"Missing {SHEET_CONTRACTS_MD}")
        return stats
    md_text = SHEET_CONTRACTS_MD.read_text()

    # Parse child sheet instances from fome-mc.kicad_sch
    root_tree = parse_sexpr(ROOT_SCH.read_bytes())
    file_to_instances: dict[str, list[dict[str, object]]] = {}
    for s in children(root_tree, "sheet"):
        sname = None
        sfile = None
        for p in children(s, "property"):
            if len(p) >= 3 and p[1] == "Sheetname":
                sname = p[2]
            elif len(p) >= 3 and p[1] == "Sheetfile":
                sfile = p[2]
        pins = {}
        for pin in children(s, "pin"):
            if len(pin) >= 3 and isinstance(pin[1], str):
                pins[pin[1]] = str(pin[2])
        if sname and sfile:
            file_to_instances.setdefault(sfile, []).append({"name": sname, "pins": pins})
            stats["instances"] += 1
            if f"`/{sname}/`" not in md_text:
                errors.append(f"docs/SHEET_CONTRACTS.md missing sheet instance path `/{sname}/`")

    inventory = fresh_inventory(eda.project_config("fome-mc"))

    for sch_path in sorted(SHEETS_DIR.glob("*.kicad_sch")):
        rel_file = f"sheets/{sch_path.name}"
        stem = sch_path.stem
        contract_path = CONTRACTS_DIR / f"{stem}.interface.json"
        if not contract_path.exists():
            errors.append(f"Missing contract file {contract_path} for {rel_file}")
            continue

        # Parse unique hierarchical_label names in child sheet
        stree = parse_sexpr(sch_path.read_bytes())
        hlabels: dict[str, str] = {}
        for hl in children(stree, "hierarchical_label"):
            if len(hl) >= 2 and isinstance(hl[1], str):
                shape = field(hl, "shape", 1)[0] if children(hl, "shape") else "passive"
                if hl[1] not in hlabels:
                    hlabels[hl[1]] = str(shape)
        stats["unique_hlabels"] += len(hlabels)

        # Verify every hierarchical_label appears in docs/SHEET_CONTRACTS.md and on every parent sheet symbol
        instances = file_to_instances.get(rel_file, [])
        if not instances:
            errors.append(f"Child sheet {rel_file} has no sheet instances in fome-mc.kicad_sch")
        for hname in sorted(hlabels):
            if f"| `{hname}` |" not in md_text:
                errors.append(f"docs/SHEET_CONTRACTS.md missing hierarchical_label `{hname}` from {rel_file}")
            for inst in instances:
                inst_pins = inst["pins"]
                if hname not in inst_pins:
                    errors.append(f"Root sheet instance /{inst['name']}/ missing sheet pin for hierarchical_label `{hname}`")

        # Validate contract schema and evaluate against fresh XML netlist
        try:
            contract = load_contract(REPO, f"contracts/{stem}.interface.json")
        except Exception as exc:
            errors.append(f"Invalid contract {contract_path.name}: {exc}")
            continue

        stats["contracts"] += 1
        records = evaluate(contract, inventory)
        stats["invariants"] += len(records)
        unsat = [r["id"] for r in records if r["status"] != "satisfied"]
        if unsat:
            errors.append(
                f"Contract {contract_path.name} failed evaluation against fresh netlist: {unsat}"
            )

        # Verify every (instance, hierarchical_label) binding has a pin:<inst>:<hname> named_net invariant
        inv_by_id = {inv["id"]: inv for inv in contract.get("invariants", [])}
        for inst in instances:
            iname = inst["name"]
            for hname in sorted(hlabels):
                stats["pin_bindings"] += 1
                expected_id = f"pin:{iname}:{hname}"
                if expected_id not in inv_by_id:
                    errors.append(f"{contract_path.name} missing invariant id '{expected_id}'")
                elif inv_by_id[expected_id].get("kind") != "named_net":
                    errors.append(f"{contract_path.name} invariant '{expected_id}' must have kind 'named_net'")

    return stats


if __name__ == "__main__":
    sys.exit(main())
