#!/usr/bin/env python3
"""
verify_io_map.py — End-to-end hardware/firmware pin & netlist consistency verifier for fome-mc.

Checks 1-to-1 agreement across:
  1. /home/halbritt/git/fome-mc/io-map.csv (all 70 J1/J2 pins + 22 INTERNAL-* rows)
  2. /home/halbritt/git/fome-mc/export/fome-mc.net (exported from fome-mc.kicad_sch)
  3. /home/halbritt/git/fome-fw/firmware/config/boards/fome-mc/board_configuration.cpp & connectors/*.yaml
  4. /home/halbritt/git/fome-mc/docs/SHEET_CONTRACTS.md & /home/halbritt/git/fome-mc/contracts/*.interface.json
     (verified against fome-mc.kicad_sch, sheets/*.kicad_sch, and a freshly exported KiCad XML netlist)
"""
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

AGENT_EE_SRC = Path("/home/halbritt/git/agent-ee/src")
if AGENT_EE_SRC.exists() and str(AGENT_EE_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_EE_SRC))

from agent_ee.hardware_interface import evaluate, load_contract, read_inventory  # noqa: E402
from agent_ee.symbol_library import children, field, parse_sexpr  # noqa: E402

REPO = Path("/home/halbritt/git/fome-mc")
IO_MAP_CSV = REPO / "io-map.csv"
NETLIST = REPO / "export/fome-mc.net"
ROOT_SCH = REPO / "fome-mc.kicad_sch"
SHEETS_DIR = REPO / "sheets"
CONTRACTS_DIR = REPO / "contracts"
SHEET_CONTRACTS_MD = REPO / "docs/SHEET_CONTRACTS.md"
FW_DIR = Path("/home/halbritt/git/fome-fw/firmware/config/boards/fome-mc")
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


def main() -> int:
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
    pinned = Path("/home/halbritt/.local/opt/kicad-10.0.7/bin/kicad-cli")
    if pinned.exists():
        return str(pinned)
    found = shutil.which("kicad-cli")
    if found:
        return found
    raise FileNotFoundError("kicad-cli not found in /home/halbritt/.local/opt/kicad-10.0.7/bin or PATH")


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

    # Export a fresh KiCad XML netlist into a temporary directory (never touching the repo tree)
    kicad_cli = _find_kicad_cli()
    with tempfile.TemporaryDirectory(prefix="fome-mc-verify-contracts-") as tmpdir:
        xml_path = Path(tmpdir) / "design.xml"
        proc = subprocess.run(
            [kicad_cli, "sch", "export", "netlist", "--format", "kicadxml", "--output", str(xml_path), str(ROOT_SCH)],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0 or not xml_path.exists():
            errors.append(f"kicad-cli sch export netlist failed (rc={proc.returncode}): {proc.stderr.strip()}")
            return stats
        inventory = read_inventory(xml_path)

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
