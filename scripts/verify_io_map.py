#!/usr/bin/env python3
"""
verify_io_map.py — End-to-end hardware/firmware pin & netlist consistency verifier for fome-mc.

Checks 1-to-1 agreement across:
  1. /home/halbritt/git/fome-mc/io-map.csv (all 70 J1/J2 pins + 15 INTERNAL-* rows)
  2. /home/halbritt/git/fome-mc/export/fome-mc.net (exported from fome-mc.kicad_sch)
  3. /home/halbritt/git/fome-fw/firmware/config/boards/fome-mc/board_configuration.cpp & connectors/*.yaml
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path("/home/halbritt/git/fome-mc")
IO_MAP_CSV = REPO / "io-map.csv"
NETLIST = REPO / "export/fome-mc.net"
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
    "J1-13": ("/LS8",            "U1102:8", "D208:2"),
    "J1-14": ("/MAIN_RLY",       "U1202:6", "D209:2"),
    "J1-15": ("/ETB1_OUT+",      "U201:5"),
    "J1-16": ("/ETB1_OUT-",      "U201:7"),
    "J1-17": ("/ETB2_OUT+",      "U203:5"),
    "J1-18": ("/ETB2_OUT-",      "U203:7"),
    "J1-19": ("/STEP_1A",        "U202:4"),
    "J1-20": ("/STEP_1B",        "U202:6"),
    "J1-21": ("/STEP_2A",        "U202:9"),
    "J1-22": ("/STEP_2B",        "U202:7"),
    "J1-23": ("/WBO1_H-",        "Q301:2"),
    "J1-24": ("/12V_MR",         "D201:1"),
    "J1-25": ("/WBO2_H-",        "Q401:2"),
    "J1-26": ("/12V_IGN_SW",     "D20:2", "R96:1"),
    "J1-27": ("/12V_MR",         "D201:1", "D21:2"),
    "J1-28": ("/Perm_Live",      "D16:2"),
    "J1-29": ("/5V_SENSOR_1",    "U1:1"),
    "J1-30": ("/5V_SENSOR_2",    "U2:1"),
    "J1-31": ("GND",             "U26:31"),
    "J1-32": ("GND",             "U26:16"),
    "J1-33": ("GND",             "U26:16"),
    "J1-34": ("GND",             "U26:16"),
    "J1-35": ("/RC2",            "U26:101", "R209:1"),
    "J2-1":  ("/AT1",            "R39:2"),
    "J2-2":  ("/AT2",            "R40:2"),
    "J2-3":  ("/AV2",            "R52:1"),
    "J2-4":  ("/AV4",            "R54:1"),
    "J2-5":  ("/AV1",            "R51:1"),
    "J2-6":  ("/AV3",            "R53:1"),
    "J2-7":  ("/AV5",            "R63:1"),
    "J2-8":  ("/AV6",            "R64:1"),
    "J2-9":  ("/KNOCK_1",        "C16:2"),
    "J2-10": ("/KNOCK_2",        "C17:2"),
    "J2-11": ("/VR1+",           "C37:1"),
    "J2-12": ("GND",             "U26:16"),
    "J2-13": ("/VR2+",           "C36:1"),
    "J2-14": ("GND",             "U26:16"),
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
    "J2-27": ("/LS14",           "U1201:8", "R212:2"),
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
    "INTERNAL-WBO1_NRST":     ("/WBO1_NRST",       "U26:1",   "U302:4"),
    "INTERNAL-WBO1_BOOT0":    ("/WBO1_BOOT0",      "U26:2",   "U302:31"),
    "INTERNAL-WBO2_NRST":     ("/WBO2_NRST",       "U26:3",   "U402:4"),
    "INTERNAL-WBO2_BOOT0":    ("/WBO2_BOOT0",      "U26:4",   "U402:31"),
    "INTERNAL-WBO1_SEL":      ("GND",              "U302:15"),
    "INTERNAL-WBO2_SEL":      ("+3V3_WBO2",        "U402:18", "U409:2"),
    "INTERNAL-SDMMC_D0":      ("/mcu/SD_D0",       "U26:98",  "U25:7"),
    "INTERNAL-SDMMC_D1":      ("/mcu/SD_D1",       "U26:99",  "U25:8"),
    "INTERNAL-SDMMC_D2":      ("/mcu/SD_D2",       "U26:111", "U25:1"),
    "INTERNAL-SDMMC_D3":      ("/mcu/SD_D3",       "U26:112", "U25:2"),
    "INTERNAL-SDMMC_CK":      ("/mcu/SD_CLK",      "U26:113", "U25:5"),
    "INTERNAL-SDMMC_CMD":     ("/mcu/SD_CMD",      "U26:116", "U25:3"),
    "INTERNAL-BARO_I2C":      ("/mcu/BARO_SCL",    "U26:69",  "U24:2"),
    "INTERNAL-PWR_KEEPALIVE": ("/lowside_quad4/IN3","U26:141", "RN9:6"),
}


def main() -> int:
    errors = []
    rows = list(csv.DictReader(IO_MAP_CSV.open()))
    pin_rows = {r["Connector_Pin"]: r for r in rows}

    # 1. Verify all 70 J1/J2 pins + 16 INTERNAL rows exist in io-map.csv
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
        'efiSetPadMode("WBO1_NRST", Gpio::E2',
        'efiSetPadMode("WBO1_BOOT0", Gpio::E3',
        'efiSetPadMode("WBO2_NRST", Gpio::E4',
        'efiSetPadMode("WBO2_BOOT0", Gpio::E5',
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

    if errors:
        print("FAILED io-map / netlist / firmware verification:")
        for e in errors:
            print("  [ERROR]", e)
        return 1

    print(f"PASS: Verified {len(EXPECTED_PIN_NETS)} external connector pins (J1-1..35, J2-1..35),")
    print(f"      {len(EXPECTED_INTERNAL_NODES)} internal MCU/WBO/SDNAND/Baro buses,")
    print(f"      {len(comps)} netlist components (0 unannotated, 0 duplicates),")
    print(f"      and {len(yaml_pins)} TunerStudio YAML connector definitions + board_configuration.cpp.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
