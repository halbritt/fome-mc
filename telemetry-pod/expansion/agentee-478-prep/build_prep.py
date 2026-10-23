"""AGENTEE-478: build the D1-D5 data files from frozen inputs (read-only; no board is opened for write).

Usage: build_prep.py <frozen telemetry-pod dir> <schematic netlist.json> <out dir>
Inputs: blocks/allocation.json (434a9984), the pin extracts in extract/ (pcbnew, no save),
the netlist exported by kicad-cli from the emitted schematic, retained datasheet PDFs (hashed here).
"""
import hashlib, json, math, re, sys
from pathlib import Path

ROOT, NETLIST, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
EXP = ROOT / 'expansion'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
net = json.loads(NETLIST.read_text())
SCH, NETS = net['components'], net['nets']
ALLOC_PATH = EXP / 'blocks/allocation.json'
ALLOC = json.loads(ALLOC_PATH.read_text())
EXTRACT = {k: json.loads((OUT / 'extract' / f).read_text()) for k, f in
           [('emitted', 'emitted-0b68a0ac.json'),  # AGENTEE-484 regenerated emission (was emitted-2f1c9557.json)
             ('r5', 'r5-8f3bc234.json'), ('route3', 'route3-08066170.json')]}
BOARD = dict(EXTRACT['emitted']['footprints'])
# AGENTEE-484: parts added by the source repair exist in the regenerated schematic but on no board yet.
SCHEMATIC_ONLY = sorted(set(SCH) - set(BOARD))
for _r in SCHEMATIC_ONLY:
    BOARD[_r] = {'value': SCH[_r]['value'], 'side': None, 'on_board': False,
                 'pads': [{'number': k, 'net': v[0], 'pin_function': v[1]} for k, v in SCH[_r]['pins'].items()]}
RAILS = ['/GND', '/+3V3', '/PRE_6V3', '/POD_12V_PROTECTED', '/+5V_CAN', '/POD_5V_SENSOR']
nat = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))

# ---------------------------------------------------------------- D1 membership
FIXED = {  # role fixed: sourced anchors per AGENTEE-474 (entry ids cite agentee-474-constraints/RESULT.md)
    'J1': ['C05', 'C06', 'C07', 'C08'], 'J2': ['C09'], 'J3': ['C10', 'C11'], 'U1': ['C12', 'C13'],
    'U2': ['C14'], 'U3': ['C15'], 'H1': ['C03', 'C04'], 'H2': ['C03', 'C04'], 'H3': ['C03', 'C04'],
    'H4': ['C03', 'C04']}
SHARED = {f'TP{i}': 'test' for i in range(1, 7)}
old = {b['id']: list(b['references']) for b in ALLOC['blocks']}
anchors = {b['id']: b.get('anchor') for b in ALLOC['blocks']}
blocks = {k: list(v) for k, v in old.items()}
corrections = []

def move(refs, src, dst, why, evidence):
    for r in refs:
        if src:
            blocks[src].remove(r)
        blocks.setdefault(dst, []).append(r)
    corrections.append({'references': refs, 'from': src or 'residual/unassigned', 'to': dst,
                        'reason': why, 'evidence': evidence})

# residual and unassigned -> explicit roles
# AGENTEE-484 (decision of agent-529, Plane AGENTEE-484): the 478 bank assignment is replaced by per-pin
# dispositions sourced in ../agentee-484-decoupling/dispositions.json. The netlist is unchanged for rebinds.
move(['C18'], None, 'supplies-5v',
     'AGENTEE-484 rebind: C18 (1 uF) on /PRE_6V3 is the REF5050 (U11) Vin supply bypass (REF50xx: TI '
     'recommends a supply bypass capacitor ranging from 1 uF; place as close as possible). U5 keeps C6/C7 2x22 uF.',
     'netlist C18=/PRE_6V3-/GND, U11.2 Vin=/PRE_6V3; source emitter-layout group supplies-5v')
move(['C38', 'C41'], None, 'imu-support',
     'AGENTEE-484 rebind: C38 -> U2.8 VDD and C41 -> U2.5 VDDIO, the two 100 nF capacitors C1/C2 of the '
     'LSM6DSO32 datasheet; U7 keeps the LMR36520 Table 8-1 3.3 V output bank 3x22 uF (C13-C15)',
     'source emitter-layout group imu; netlist unchanged (+3V3/GND)')
move(['C43'], None, 'gnss-antenna-supply',
     'AGENTEE-484 rebind: C43 (100 nF) -> U10.1 IN, the TPS2553 100-nF bypass near IN and GND',
     'source emitter-layout group gnss; netlist unchanged')
move(['C44'], None, 'gnss-receiver-support',
     'AGENTEE-484 rebind: C44 (1 uF) -> U3.23 VCC (NEO-M9N VCC decoupling as close as possible); also local '
     'to the adjacent V_BCKP pin 22 tied to VCC (PENDING-510)',
     'source emitter-layout group gnss; U3 pads 22/23/24 at 1.1 mm pitch')
move(['C130'], None, 'adc', 'AGENTEE-484 added: 1 uF U4.16 Vdd bypass (MCP3208: 1 uF is recommended)', 'source intent adc/C130')
move(['C131'], None, 'afe', 'AGENTEE-484 added: 100 nF U8.4 V+ bypass', 'source intent power/C131')
move(['C132'], None, 'sensor-ref', 'AGENTEE-484 added: 100 nF U9.5 V+ bypass (OPA320: 0.1-uF bypass close to the supply pins)', 'source intent power/C132')
move(['C133'], None, 'can', 'AGENTEE-484 added: 100 nF U100.5 VIO bypass', 'source intent can/C133')
move(['R33'], None, 'mcu',
     'R33 (10 k) pulls U1 IO46 (/MCU_BOOT46) to GND: a strap of the module. mcu is the U1 support block '
     'anchored on the fixed U1, so a member reachable only through the fixed anchor is expected and valid.',
     'netlist R33.1=/MCU_BOOT46 (U1.16 IO46) R33.2=/GND; emitter group mcu lists support/R33')
move(['U10', 'R24', 'R25', 'R26', 'C42'], None, 'gnss-antenna-supply',
     'Active-antenna bias supply: TPS2553 load switch U10 (EN from U3 LNA_EN, fault flag) feeding '
     '/ANT_LIMITED -> R26 -> /ANT_BIAS (C42). DC circuitry, independent of the RF line; its own small block.',
     'netlist U10.3=/GNSS_LNA_EN (U3.14, R24), U10.4=/GNSS_ANT_FAULT_N (R25), U10.6=/ANT_LIMITED (R26), '
     'C42.1=/ANT_BIAS; emitter group gnss')
move(['L3', 'D3'], None, 'gnss-rf-feed',
     'Parts ON the RF line /POD_GNSS_RF between U3.11 and J2.1: bias-tee inductor L3 and ESD D3. They follow '
     'the RF path (474 C15), so they are a separate block from the DC antenna supply.',
     'netlist L3=/ANT_BIAS-/POD_GNSS_RF, D3=/POD_GNSS_RF-/GND, J2.1=/POD_GNSS_RF, U3.11 RF_IN')
move(['R46', 'R47', 'R48', 'R49', 'R50', 'R55', 'C64', 'C65'], None, 'storage-support',
     'microSD support: pull-ups on CMD/DAT0-3/CD and the J3 VDD capacitors, anchored on the fixed J3 '
     '(seventh fix dissolved the storage block only because J3 became fixed).',
     'netlist R46-R50 to /SD_CMD,/SD_DAT0..3, R55 to /SD_CD, C64/C65 on /+3V3 at J3.4 VDD')
# verification corrections of the existing 18
move(['U9', 'R22', 'R23', 'C39'], 'afe', 'sensor-ref',
     'U9 (OPA320) buffers the 2.5 V ADC reference from the /POD_5V_SENSOR divider R22/R23 (C39 filter) to '
     'U4 Vref. On non-rail nets it is unreachable from the afe anchor U8: an independent circuit. Kept '
     'as its own small block instead of riding with the input buffers.',
     'netlist U9.3=/REF_DIV (R22,R23,C39), U9.1/4=/SENSOR_REF_2V5 = U4.15 Vref (C40); reachability check '
     'in d1-verification.json')
move(['R36', 'R39', 'R42', 'R45', 'C55', 'C57', 'C59', 'C61'], 'aux-afe', 'adc',
     'ADC CH4-7 input RC (100 ohm series + 100 pF at the U4 pin) has the same topology and function as the '
     'CH0-3 RC (R12/R15/R18/R21, C31/C33/C35/C37), which are already in adc. The 100 pF is the sampling '
     'reservoir at the U4 pin, so it belongs with the ADC.',
     'netlist C55.1=/ADC_AIN4=U4.5 ... C61.1=/ADC_AIN7=U4.8; R36 /AFE_BUF4-/ADC_AIN4 ...; '
     'CH0-3 equivalents in old adc')
for sv, parts in [('supervisor-3v3', ['U16', 'R56', 'R57', 'C71', 'C72']),
                  ('supervisor-5v-sensor', ['U18', 'R60', 'R181', 'R61', 'C75', 'C76', 'R64']),
                  ('supervisor-12v', ['U19', 'R62', 'R63', 'C77', 'C78', 'R65'])]:
    move(parts, 'supervision', sv,
         'The three TPS389001 supervisors watch different rails (+3V3, /POD_5V_SENSOR, '
         '/POD_12V_PROTECTED) and share only rails; on non-rail nets U18/U19 are unreachable from U16. '
         'Split into independent small blocks (common rails do not merge blocks).',
         'netlist SENSE nets /SUP_U16_SENSE, /SUP_U18_SENSE, /SUP_U19_SENSE; VDD-cap binding by emitter '
         'order (U, Rtop, Rbot, CT, VDD cap)')
del blocks['supervision']
anchors.update({'imu-support': None, 'gnss-receiver-support': None, 'gnss-antenna-supply': 'U10', 'gnss-rf-feed': None, 'storage-support': None, 'sensor-ref': 'U9',
                'supervisor-3v3': 'U16', 'supervisor-5v-sensor': 'U18', 'supervisor-12v': 'U19', 'mcu': None})
anchors.pop('supervision', None)
FIXED_ANCHOR = {'imu-support': 'U2', 'gnss-receiver-support': 'U3', 'mcu': 'U1', 'gnss-rf-feed': 'U3', 'gnss-antenna-supply': 'U3', 'storage-support': 'J3',
                'power-entry': 'J1', 'can': 'J1', 'tire-can': 'J1'}

# ---------------------------------------------------------------- sources (D3 provenance)
DS = {
    'LMR36520': 'parts-closure/recovered-pilot/power-source/acquisition/cb8ebe03bcc7860306c5e291bd6d892cb951f20cf5f21f15ecbcd8efd3029dd1.pdf',
    'TPS7B4253': 'interface-preparation/aux-power/tps7b4253-q1.pdf',
    'TPS2553': 'parts-closure/recovered-pilot/power-source/acquisition/7438702fe3f737612ed5c8f133f60b81eda9c68e3b74ddeffe913858f59c4892.pdf',
    'TPS2662': 'interface-preparation/sensor-power/tps2662.pdf',
    'LSM6DSO32': 'parts-closure/recovered-pilot/core/datasheets-current/fce1bf36cb460a31e2d1f3ede054b5d2e68f07b8f9039cb09062522e9bcf4e2c.pdf',
    'NEO-M9N-IM': 'parts-closure/recovered-pilot/power-source/acquisition/402991ee7566b52693f3ab3400d2e42d878be51ba4de90e8cac049be6104f524.pdf',
    'ESP32-HG': 'production-capture/sources/esp32-guidelines/3dc09a979cf612db0754f966d180b22f05896ad220cece362d62cb0d0eb1d400.pdf',
    'ADS1119': 'interface-preparation/diagnostics/ads1119.pdf',
    'MCP3208': 'native-candidate/sources/mcp3208.pdf',
    'OPA320': 'parts-closure/recovered-pilot/power-source/acquisition-adoption/d6b3c62b2d37a5cb6776d49d62cc4a48cd4fe7226fbd93e52583822adbdae3d0.pdf',
    'LM2903B': 'interface-preparation/wheel-input/lm2903b-q1.pdf',
    'SN74LVC1G132': 'interface-preparation/sources/sn74lvc1g132.pdf',
    'TL431': 'thermistor/sources/tl431.pdf',
    'REF50': 'interface-preparation/aux-power/ref50.pdf',
}
SRC = {k: {'path': 'telemetry-pod/expansion/' + v, 'sha256': sha(EXP / v)} for k, v in DS.items()}
CITE = {  # (source key, page, retained wording, what it constrains)
    'lmr-hotloop': ('LMR36520', 27, '8.5.1: the loop formed by the input capacitors and power ground ... traces wide and short, loop area as small as possible; 1. Place the input capacitors as close as possible to the VIN and GND terminals'),
    'lmr-vcc': ('LMR36520', 27, '2. Place the bypass capacitor for VCC close to the VCC pin ... short, wide traces to the VCC and GND pins'),
    'lmr-boot': ('LMR36520', 27, '3. Place CBOOT close to the device with short, wide traces to the BOOT and SW pins'),
    'lmr-fb': ('LMR36520', 27, '4. Place the feedback divider as close as possible to the FB pin ... connection to VOUT can be somewhat longer (continues p28)'),
    'lmr-sw': ('LMR36520', 28, '8. Keep the switch area small. Keep the copper area connecting the SW pin to the inductor as short and wide as possible'),
    'lmr-thermal': ('LMR36520', 28, '7. Provide enough PCB area for proper heat-sinking ... thermal vias'),
    'tps7b-layout': ('TPS7B4253', 19, '7.4.1: place every capacitor as close as possible to the device and on the same side of the PCB as the regulator. Do not place any of the capacitors on the opposite side'),
    'tps2553-layout': ('TPS2553', 25, '12.1: placing the 100-nF bypass capacitor near the IN and GND pins ... low-inductance trace'),
    'tps2662-layout': ('TPS2662', 35, '12.1: 0.1 uF or higher ceramic decoupling between IN and GND ... closest to the IN and GND terminals ... minimize the loop area'),
    'lsm6-bypass': ('LSM6DSO32', 53, 'Power supply decoupling capacitors (C1, C2 = 100 nF ceramic) should be placed as near as possible to the supply pin of the device'),
    'neo-vcc': ('NEO-M9N-IM', 81, 'The VCC pad needs a large pad and the decoupling capacitor must be placed as close as possible'),
    'neo-rf': ('NEO-M9N-IM', 80, 'RF input co-planar waveguide referenced to layer 2, matched to 50 ohm'),
    'esp-en': ('ESP32-HG', 11, 'add an RC delay circuit at the CHIP_PU pin ... R = 10 kOhm and C = 1 uF (chip guideline; module EN = CHIP_PU)'),
    'esp-rc': ('ESP32-HG', 17, 'Ensure that the RC/LC components are placed close to the pins of the chip or module'),
    'ads-decouple': ('ADS1119', 37, '10.2: AVDD and DVDD must be decoupled with at least a 0.1-uF capacitor. Place the bypass capacitors as close to the power-supply pins'),
    'ads-layer': ('ADS1119', 38, 'Do not place vias between bypass capacitors and the active device. Placing the bypass capacitors on the same layer as close to the active device'),
    'mcp3208-bypass': ('MCP3208', 23, 'A bypass capacitor should always be used ... placed as close as possible to the device pin. A bypass capacitor value of 1 uF is recommended'),
    'ref50-bypass': ('REF50', 29, 'TI recommends a supply bypass capacitor ranging from 1uF to 50uF for REF50xxI ... Place the power-supply bypass capacitor as closely as possible to the supply and ground pins'),
    'neo-bckp': ('NEO-M9N-IM', 71, 'If no backup supply voltage is available, connect the V_BCKP pin to VCC'),
    'opa320-bypass': ('OPA320', 28, 'Place 0.1-uF bypass capacitors close to the power-supply pins'),
    'lm2903-bypass': ('LM2903B', 18, 'A bypass capacitor is recommended on the supply pin'),
    'lvc-bypass': ('SN74LVC1G132', 14, 'Add a decoupling capacitor from VCC to GND ... physically close to the device; 0.1 uF recommended'),
    'tl431-bypass': ('TL431', 31, 'Bypass capacitors should be placed as close to the part as possible'),
}
IC_DECOUPLE_CITE = {'U11': 'ref50-bypass', 'U5': 'lmr-hotloop', 'U7': 'lmr-hotloop', 'U6': 'tps7b-layout', 'U12': 'tps7b-layout',
                    'U10': 'tps2553-layout', 'U23': 'tps2662-layout', 'U24': 'tps2662-layout',
                    'U25': 'tps2662-layout', 'U30': 'tps2662-layout', 'U2': 'lsm6-bypass', 'U3': 'neo-vcc',
                    'U27': 'ads-decouple', 'U28': 'ads-decouple', 'U29': 'ads-decouple', 'U4': 'mcp3208-bypass',
                    'U9': 'opa320-bypass', 'U26': 'lm2903-bypass', 'U22': 'lvc-bypass', 'U31': 'tl431-bypass'}
SAME_FACE_MFR = {'U6': 'tps7b-layout', 'U12': 'tps7b-layout', 'U27': 'ads-layer', 'U28': 'ads-layer',
                 'U29': 'ads-layer'}
EJ = 'ENGINEERING JUDGEMENT (agent, AGENTEE-478, labelled; not owner- or manufacturer-set)'

# bound classes: supply leg / return leg in mm (3D pad-centre, dz = 1.6 mm across faces), same-face rule
BOUND = {
    'hot-loop-input': (3.0, 3.0, True, 'topology: hot loop; a via pair adds loop inductance'),
    'bulk-input': (8.0, 8.0, True, 'topology: parallel member of the same hot loop'),
    'vcc-bias': (3.0, 6.0, False, 'return may close through the In1 GND plane'),
    'bootstrap': (3.5, 3.5, True, 'topology: switch-node referenced; vias add radiating area'),
    'switch-inductor': (5.0, None, True, 'topology: switch-node area (dv/dt)'),
    'feedback': (4.0, None, False, 'only the FB leg is bounded (manufacturer: VOUT leg may be longer)'),
    'regulator-output': (10.0, None, False, 'output bank at the inductor output pad; bulk, not HF'),
    'ldo-cap': (4.0, 6.0, True, 'manufacturer forbids opposite-side capacitors'),
    'hf-decoupler': (3.0, 5.0, False, 'single-pin HF decoupler'),
    'secondary-decoupler': (12.0, None, False, 'additional capacitor of a multi-capacitor supply set'),
    'bulk-decoupler': (10.0, None, False, 'bulk capacitor >= 4.7 uF'),
    'hotswap-input': (3.0, 4.0, False, 'IN-GND bypass loop'),
    'crystal': (6.0, None, True, 'oscillator loop kept on one face, no vias'),
    'crystal-load': (3.0, None, True, 'load capacitor at the crystal pin'),
    'esd-connector': (10.0, None, False, 'protector between connector pin and the protected IC'),
    'termination': (15.0, None, False, 'bus termination near the transceiver bus pins'),
    'input-filter': (5.0, None, False, 'filter / sampling reservoir capacitor at the IC input pin'),
    'series-input': (6.0, None, False, 'series resistor of an input RC, at the IC side'),
    'sense-network': (5.0, None, False, 'high-impedance sense/timing node pad at the IC pin'),
    'strap': (10.0, None, False, 'strap / enable / reset pull or RC on a critical control line'),
    'reference-cap': (4.0, None, False, 'reference / noise-reduction capacitor at the pin'),
    'output-load': (10.0, None, False, 'bleed / minimum-load resistor at the regulator output'),
}

# rail-capacitor bindings: (cap, ic, pin, class)
RAIL_BIND = [
    ('C3', 'U5', '2', 'hot-loop-input'), ('C1', 'U5', '2', 'bulk-input'), ('C2', 'U5', '2', 'bulk-input'),
    ('C4', 'U5', '6', 'vcc-bias'),
    ('C10', 'U7', '2', 'hot-loop-input'), ('C8', 'U7', '2', 'bulk-input'), ('C9', 'U7', '2', 'bulk-input'),
    ('C11', 'U7', '6', 'vcc-bias'),
    ('C16', 'U6', '8', 'ldo-cap'), ('C17', 'U6', '1', 'ldo-cap'), ('C20', 'U12', '8', 'ldo-cap'),
    ('C19', 'U12', '1', 'ldo-cap'),
    ('C46', 'U1', '2', 'hf-decoupler'), ('C50', 'U1', '2', 'hf-decoupler'), ('C45', 'U1', '2', 'bulk-decoupler'),
    ('C48', 'U1', '2', 'secondary-decoupler'), ('C49', 'U1', '2', 'secondary-decoupler'),
    ('C51', 'U1', '2', 'secondary-decoupler'), ('C52', 'U1', '2', 'secondary-decoupler'),
    ('C53', 'U1', '2', 'secondary-decoupler'),
    ('C100', 'U100', '3', 'hf-decoupler'), ('C62', 'U13', '4', 'hf-decoupler'),
    ('C72', 'U16', '4', 'hf-decoupler'), ('C76', 'U18', '4', 'hf-decoupler'), ('C78', 'U19', '4', 'hf-decoupler'),
    ('C79', 'U20', '14', 'hf-decoupler'), ('C80', 'U20', '14', 'secondary-decoupler'),
    ('C83', 'U21', '3', 'hf-decoupler'), ('C84', 'U21', '5', 'hf-decoupler'), ('C85', 'U22', '5', 'hf-decoupler'),
    ('C86', 'U23', '1', 'hotswap-input'), ('C89', 'U24', '1', 'hotswap-input'), ('C92', 'U25', '1', 'hotswap-input'),
    ('C124', 'U30', '1', 'hotswap-input'),
    ('C97', 'U26', '8', 'hf-decoupler'), ('C98', 'U26', '8', 'secondary-decoupler'),
    ('C118', 'U27', '12', 'hf-decoupler'), ('C119', 'U27', '13', 'hf-decoupler'),
    ('C120', 'U28', '12', 'hf-decoupler'), ('C121', 'U28', '13', 'hf-decoupler'),
    ('C122', 'U29', '12', 'hf-decoupler'), ('C123', 'U29', '13', 'hf-decoupler'),
    ('C64', 'J3', '4', 'bulk-decoupler'), ('C65', 'J3', '4', 'hf-decoupler'),
    # AGENTEE-484 dispositions
    ('C38', 'U2', '8', 'hf-decoupler'), ('C41', 'U2', '5', 'hf-decoupler'), ('C44', 'U3', '23', 'hf-decoupler'),
    ('C44', 'U3', '22', 'hf-decoupler'), ('C43', 'U10', '1', 'hf-decoupler'), ('C18', 'U11', '2', 'hf-decoupler'),
    ('C130', 'U4', '16', 'hf-decoupler'), ('C131', 'U8', '4', 'hf-decoupler'), ('C132', 'U9', '5', 'hf-decoupler'),
    ('C133', 'U100', '5', 'hf-decoupler'),
]
OUTPUT_BANK = [('C6', 'L1', '2'), ('C7', 'L1', '2'),
               ('C13', 'L2', '2'), ('C14', 'L2', '2'), ('C15', 'L2', '2')]
GAPS = [  # IC supply pins with no dedicated decoupler in the emitted schematic
    ('U2', '8', 'VDD', 'lsm6-bypass', 'C38'), ('U2', '5', 'VDDIO', 'lsm6-bypass', 'C41'),
    ('U3', '23', 'VCC', 'neo-vcc', 'C44'), ('U3', '22', 'V_BCKP', 'neo-vcc', None),
    ('U10', '1', 'IN', 'tps2553-layout', 'C43'), ('U4', '16', 'Vdd', 'mcp3208-bypass', None),
    ('U8', '4', 'V+', None, None), ('U9', '5', 'V+', 'opa320-bypass', None), ('U13', '4', 'V+ (has C62)', None, None),
    ('U100', '5', 'VIO', None, None), ('U11', '2', 'Vin', None, None)]
GAPS = []  # AGENTEE-484: every former gap now has a disposition (see dispositions.json)

def pad(fp, number, netname=None):
    c = [p for p in fp['pads'] if p['number'] == number and (netname is None or p['net'] == netname)]
    return c[0] if c else None

def dist(fa, pa, fb, pb):
    dz = 0.0 if fa['side'] == fb['side'] else 1.6
    return round(math.sqrt((pa['x'] - pb['x']) ** 2 + (pa['y'] - pb['y']) ** 2 + dz ** 2), 3)

def leg(board, ra, pna, rb, netname, pnb=None):
    if ra not in board or rb not in board or board[rb].get('on_board') is False:
        return None
    fa, fb = board[ra], board[rb]
    a = pad(fa, pna)
    bs = [p for p in fb['pads'] if p['net'] == netname and (pnb is None or p['number'] == pnb)]
    if not a or not bs:
        return None
    return min(dist(fa, a, fb, b) for b in bs)

def return_leg(board, ic, cap):
    if ic not in board or cap not in board or board[cap].get('on_board') is False:
        return None
    fi, fc = board[ic], board[cap]
    gi = [p for p in fi['pads'] if p['net'] == '/GND']
    gc = [p for p in fc['pads'] if p['net'] == '/GND']
    if not gi or not gc:
        return None
    return min(dist(fi, a, fc, b) for a in gi for b in gc)

def measure(rel):
    out = {}
    for k in ('r5', 'route3'):
        bd = EXTRACT[k]['footprints']
        if rel['support']['ref'] not in bd:
            out[k] = {'supply_leg_mm': None, 'return_leg_mm': None, 'faces': None,
                      'verdict': 'not-on-board (added by AGENTEE-484; measured after regeneration and placement)'}
            continue
        s = leg(bd, rel['device']['ref'], rel['device']['pin'], rel['support']['ref'], rel['device']['net'])
        r = return_leg(bd, rel['device']['ref'], rel['support']['ref']) if rel['bound'].get('return_leg_max_mm') else None
        same = bd[rel['device']['ref']]['side'] == bd[rel['support']['ref']]['side']
        res = {'supply_leg_mm': s, 'return_leg_mm': r, 'faces': [bd[rel['device']['ref']]['side'],
                                                                 bd[rel['support']['ref']]['side']]}
        b = rel['bound']
        if b.get('status') == 'UNRESOLVED' or s is None:
            res['verdict'] = 'n/a'
        else:
            ok = s <= b['supply_leg_max_mm'] and (r is None or b.get('return_leg_max_mm') is None or
                                                  r <= b['return_leg_max_mm'])
            if b.get('same_face_required') and not same:
                ok = False
            res['verdict'] = 'within' if ok else 'exceeds'
        out[k] = res
    return out

member_of = {}
for b, rs in blocks.items():
    for r in rs:
        member_of[r] = b
for r in FIXED:
    member_of[r] = 'fixed:' + r
for r in SHARED:
    member_of[r] = 'shared:test'

rels = []
def add(kind, ic, pin, sup, bound_cls, cite=None, note=None, unresolved=None, gap_alt=None):
    netname = BOARD[ic]['pads'] and (pad(BOARD[ic], pin) or {}).get('net')
    fn = SCH[ic]['pins'].get(pin, ['', ''])[1]
    sm, rm, same, why = BOUND[bound_cls] if bound_cls else (None, None, False, '')
    if ic in SAME_FACE_MFR and bound_cls in ('hf-decoupler', 'ldo-cap', 'secondary-decoupler'):
        same = True
    prov = []
    if cite:
        s, p, q = CITE[cite]
        prov.append({'class': 'MFR', 'requirement': 'qualitative', 'source': SRC[s]['path'],
                     'sha256': SRC[s]['sha256'], 'page': p, 'text': q})
    if ic in SAME_FACE_MFR and same:
        s, p, q = CITE[SAME_FACE_MFR[ic]]
        prov.append({'class': 'MFR', 'requirement': 'same-face', 'source': SRC[s]['path'],
                     'sha256': SRC[s]['sha256'], 'page': p, 'text': q})
    prov.append({'class': 'TOPOLOGY', 'text': why})
    prov.append({'class': 'ENGINEERING-JUDGEMENT', 'text': EJ + ': numeric value of the bound'})
    bound = {'metric': 'pad-centre distance, 3D (dz = 1.6 mm when the two pads are on opposite faces)',
             'supply_leg_max_mm': sm, 'return_leg_max_mm': rm, 'same_face_required': same}
    if unresolved:
        bound = {'status': 'UNRESOLVED', 'reason': unresolved}
    kind = kind or 'decoupling-gap'
    rid = f"{ic}.{pin}-{sup or 'none'}-{kind}"
    rel = {'id': rid, 'kind': kind,
           'device': {'ref': ic, 'pin': pin, 'pin_function': fn, 'net': netname},
           'support': {'ref': sup, 'pin_net': netname} if sup else None,
           'membership': {'device': member_of.get(ic), 'support': member_of.get(sup) if sup else None},
           'bound': bound, 'provenance': prov}
    if note:
        rel['note'] = note
    if gap_alt:
        rel['owner_decision_alternative'] = gap_alt
    if sup and not unresolved:
        rel['baseline'] = measure(rel)
    elif sup:
        rel['baseline'] = {k: {'supply_leg_mm': leg(EXTRACT[k]['footprints'], ic, pin, sup, netname),
                               'verdict': 'n/a'} for k in ('r5', 'route3')}
    rels.append(rel)

for cap, ic, pin, cls in RAIL_BIND:
    cite = IC_DECOUPLE_CITE.get(ic)
    if cls == 'vcc-bias':
        cite = 'lmr-vcc'
    if ic == 'U1':
        cite = None
    add(cls, ic, pin, cap, cls, cite,
        note=('U1 has one 3V3 pin; C46 (100 nF) and C50 (1 uF) are the primary HF pair, the others '
              'are interchangeable set members (any 100 nF + any 1 uF may serve as the primary pair)')
        if ic == 'U1' else None)
add('output-load', 'U6', '1', 'R6', 'output-load', None)
for cap, l, pin in OUTPUT_BANK:
    add('regulator-output', l, pin, cap, 'regulator-output', None)

# signal-net relationships derived from the netlist by pin function
CRIT = [(r'^FB', 'feedback'), (r'^BOOT_', 'bootstrap'), (r'^SW_', 'switch-inductor'), (r'^OSC', 'crystal'),
        (r'^dVdT', 'sense-network'), (r'^ILIM', 'sense-network'), (r'^UVLO', 'sense-network'),
        (r'^OVP', 'sense-network'), (r'^SENSE', 'sense-network'), (r'^CT_', 'sense-network'),
        (r'^Trim/NR', 'reference-cap'), (r'^Vref', 'reference-cap'), (r'^EN_', 'strap'), (r'^IO0_', 'strap'),
        (r'^IO46', 'strap'), (r'^GPIO0_XSTBY', 'strap'), (r'^S_8$', 'strap'), (r'^LNA_EN', 'strap'),
        (r'^TXCAN', 'strap'), (r'^\+IN', 'input-filter'), (r'^IN\d-', 'input-filter'),
        (r'^IN\d\+', 'sense-network'), (r'^AIN', 'input-filter'), (r'^CH\d', 'input-filter'),
        (r'^CANH', 'esd-connector'), (r'^CANL', 'esd-connector'), (r'^G_1$', 'sense-network')]
NONCRIT = ('CS', 'INT', 'SDA', 'SCL', 'FAULT', 'TXD', 'RXD', 'GPIO1', 'SD_', 'TIMEPULSE', 'OUT')
for ic in sorted((r for r in SCH if re.match(r'^(U|Q)\d', r)), key=nat):
    for pin, (netname, fn) in sorted(SCH[ic]['pins'].items(), key=lambda x: nat('p' + x[0])):
        if netname in RAILS or netname.startswith('unconnected') or netname == '/POD_GNSS_RF':
            continue
        cls = next((c for k, c in CRIT if re.search(k, fn)), None)
        if ic in ('U5', 'U7') and fn.startswith('SW'):
            cls = 'switch-inductor'
        if fn.startswith('BOOT_'):
            cls = 'bootstrap'
        if cls is None:
            continue
        for r, p, _ in NETS[netname]:
            if r == ic or not re.match(r'^(C|R|L|D|Y)\d', r):
                continue
            k = cls
            if cls == 'crystal' and r.startswith('C'):
                k = 'crystal-load'
            if cls == 'esd-connector' and r.startswith('R'):
                k = 'termination'
            if cls == 'input-filter' and r.startswith('R'):
                k = 'series-input' if 'AIN' in netname or 'CH' in fn else 'sense-network'
            if cls == 'switch-inductor' and not r.startswith('L'):
                continue
            if cls == 'bootstrap' and not r.startswith('C'):
                continue
            if k == 'feedback' and ic in ('U6', 'U12'):
                continue  # TPS7B4253 FB is tied to OUT (tracking mode): no divider
            cite = {'feedback': 'lmr-fb', 'bootstrap': 'lmr-boot', 'switch-inductor': 'lmr-sw'}.get(k) \
                if ic in ('U5', 'U7') else None
            if ic == 'U1' and k == 'strap':
                cite = 'esp-en' if fn.startswith('EN') else 'esp-rc'
            if ic in ('U23', 'U24', 'U25', 'U30') and k == 'sense-network':
                cite = 'tps2662-layout'
            add(k, ic, pin, r, k, cite)
# connector-side protection: TVS / ESD parts measured to the connector pin they protect
for d, conn_pin, cls, note in [('D1', ('J1', '3'), 'esd-connector', 'input surge TVS at the power entry'),
                               ('D100', ('J1', '1'), 'esd-connector', 'pod CAN ESD at J1'),
                               ('D101', ('J1', '29'), 'esd-connector', 'tire CAN ESD at J1'),
                               ('D104', ('J1', None), 'esd-connector', 'wheel-signal ESD at J1')]:
    j, p = conn_pin
    if p is None:
        p = next(pp for pp, (nn, _) in SCH['J1']['pins'].items() if nn == '/POD_WHEEL_FRONT_SIGNAL')
    add(cls, j, p, d, cls, None, note=note)
# RF line: unresolved until 474 C15 is reconciled
for r in ('L3', 'D3'):
    add('rf-line', 'U3', '11', r, None, 'neo-rf', unresolved=(
        '474 C15: the RF path /POD_GNSS_RF (U3.11 - L3/D3 - J2.1) and its F-over-In1 reference corridor are '
        'not reconciled with the actual U3/J2 locations; no pin bound can be set before that reconciliation'))
add('rf-line', 'J2', '1', None, None, 'neo-rf', unresolved='474 C15 (as above); J2 to U3.11 RF length bound UNKNOWN')
for ic, pin, fn, cite, alt in GAPS:
    add(None, ic, pin, None, None, cite, unresolved=(
        f'emitted schematic has no capacitor dedicated to {ic}.{pin} {fn}; placement cannot satisfy a '
        'decoupling relationship that the design does not contain. Blocks acceptance of this relationship'),
        gap_alt=({'option': 'bind an existing +3V3 bank capacitor to this pin instead of the U7 output bank',
                  'capacitor': alt, 'status': 'proposed, NOT applied (needs 529/owner decision via 519)'}
                 if alt else {'option': 'design change: add a decoupler', 'status': 'proposed, not applied'}))

for r in rels:
    if r['id'] == 'U3.22-C44-hf-decoupler':
        r['disposition'] = ('NO DEDICATED CAPACITOR - PENDING-510: V_BCKP is tied to VCC as the integration manual '
                            'directs when no backup supply exists (p71); C44 sits at the adjacent VCC pin 23 '
                            '(1.1 mm pitch, GND pin 24 adjacent), so it is local to pin 22 and not a remote capacitor. '
                            'Needs agent-510 agreement')
        s_, p_, q_ = CITE['neo-bckp']
        r['provenance'].insert(0, {'class': 'MFR', 'requirement': 'topology', 'source': SRC[s_]['path'],
                                   'sha256': SRC[s_]['sha256'], 'page': p_, 'text': q_})
# old 12 obligations -> disposition
POLICY = json.loads((EXP / 'production-capture/evidence/emission-7d5b0d4d/design/composition/placement-policy.json').read_text())
old_dispo = []
for o in POLICY['electrical_locality']['obligations']:
    legs = {k: (v['from']['reference'], v['from']['pad'], v['to']['reference'], v['max_distance_nm'] / 1e6)
            for k, v in o.items() if isinstance(v, dict) and 'from' in v}
    new = sorted({r['id'] for v in legs.values() for r in rels if r['support']
                  and {r['device']['ref'], r['support']['ref']} == {v[0], v[2]}})
    notes = []
    if any(v[1] == '3' for v in legs.values()):
        notes.append('old supply leg used pin 3 (EN, tied to VIN); new relationship uses VIN pin 2')
    old_dispo.append({'old_id': o['id'], 'old_legs_mm': {k: v[3] for k, v in legs.items()},
                      'old_class': 'ADVISORY (agent-499, unsourced numeric)', 'new': new,
                      'disposition': 'replaced, not hardened: new bound re-derived per class with labelled '
                                     'provenance (see bound classes); old numeric value not carried as authority',
                      'notes': notes})

# ---------------------------------------------------------------- D2 eligibility
FACE_RESTRICT = {
    'gnss-rf-feed': (['F'], [{'id': 'C15', 'text': 'RF line parts follow the U3.11-J2.1 RF path, which must be F.Cu over the In1 reference (OWNER/project R:65); U3 and J2 are F. Re-check once C15 is reconciled'}]),
}
REGION = {
    'mcu': [{'id': 'C12', 'face': 'F,B', 'region_mm': [48.5, -21.25, 96.5, -0.25], 'rule': 'U1 antenna area: no parts on any layer'}],
    'storage-support': [{'id': 'C11', 'face': 'B', 'region': 'J3 native B-only rule areas (5 polygons, native-geometry.json)', 'rule': 'no parts/pads inside'},
                        {'id': 'C10', 'face': 'B', 'region_mm': [-20.095, 24.125, 17.715, 39.815], 'rule': 'J3 card/lane courtyard (AGENT 15 mm lane); card removal off the left edge'}],
}
J1_B = {'id': 'C06', 'face': 'B', 'region_mm': [6.055, 48.955, 83.945, 65.0],
        'rule': 'J1 PTH pin field: B parts may not overlap PTH pads/drills; lead stickout after trim UNKNOWN (no B courtyard)'}
# AGENTEE-478b: owner physical answers, agent-529 notice Cairn a13a1ba8-2838-4044-a40c-fe875b4e83f1 v1
# (owner relay fd5bea71@1). Quotes verbatim; the interpretation is kept separate. They resolve usage and
# selection only; no geometric clearance becomes PASS from them.
OWNER_SRC = 'agent-529 consolidated owner-directions notice, Cairn a13a1ba8-2838-4044-a40c-fe875b4e83f1 v1 (owner relay fd5bea71@1)'
OWNER = {
    'C20': {'quote': 'Pogo clip on bench', 'source': OWNER_SRC,
            'interpretation': 'hand-held pogo clip / probes on the bare board, on the bench, before enclosure; bottom-side TPs allowed; BLE OTA after sealing. No fixed fixture pattern, no post-seal access. Reserve probe-tip approach clearance only (no tall parts or screw hardware over or around the pads)'},
    'C21': {'quote': 'Once, on the bench', 'source': OWNER_SRC,
            'interpretation': 'one-time soldering-iron access on the bare board before enclosure only'},
    'C22': {'quote': "I'm sure it's ~90mm or more.",
            'quote_correction': '90mm height, the length and width are quite a bit more than that',
            'source': OWNER_SRC + '; cowl paragraph superseded by a13a1ba8 v2 (owner relays fd5bea71@1 and correction 27c51f73@1)',
            'interpretation': 'about 90 mm is the provisional available HEIGHT (owner estimate, not a measured rigid cap) for the full vertical stack: enclosure floor and lid, standoffs, board, both-face parts, connector bodies, cable/harness. Length and width are substantially larger, with no numeric outline constraint; the outline is not cowl-constrained. Final physical fit stays with bench/install verification. The v1 unspecified/smallest-dimension reading is superseded'},
    'C04': {'quote': 'Agents pick M3 hardware', 'source': OWNER_SRC,
            'interpretation': 'hardware is M3, selected and sourced by agents: agent-507 in AGENTEE-480 (pending). Head/washer/standoff/driver geometry is reserved on the relevant faces once AGENTEE-480 supplies it; not duplicated here'},
}
HOLES = [{'id': 'C04', 'face': 'F,B', 'region': f'around {h} ({x},{y}), radius UNKNOWN pending AGENTEE-480',
          'rule': 'M3 hardware (owner: "Agents pick M3 hardware"); head/washer/standoff/driver envelope UNKNOWN on both faces until AGENTEE-480 supplies the selected geometry; hole courtyard only is enforced; no clearance PASS',
          'owner_answer': OWNER['C04']}
         for h, x, y in [('H1', 4, 4), ('H2', 86, 4), ('H3', 86, 61), ('H4', 4, 61)]]
UNKNOWNS_ALL = [{'id': 'C19', 'what': 'installed heights of all parts on both faces; enclosure clearance per face (owner: about 90 mm provisional available HEIGHT for the full stack incl. enclosure floor/lid, standoffs, board, both-face parts, connector bodies, cable/harness; not a measured cap; per-face heights still UNKNOWN)', 'region': 'whole board', 'face': 'F,B', 'owner_answer': OWNER['C22']},
                {'id': 'C22', 'what': 'enclosure / cowl / harness envelope: owner estimate about 90 mm available HEIGHT for the full stack (not a measured rigid cap); length/width substantially larger, no numeric outline constraint; fit carried to bench/install verification', 'region': 'whole board', 'face': 'F,B', 'owner_answer': OWNER['C22']}]
THERMAL = {'pre-6v3', 'buck-3v3', 'supplies-5v', 'mcu', 'gnss-antenna-supply', 'storage-support',
           'sensor-power-front', 'sensor-power-rear', 'sensor-power-tire', 'aux-power'}
NEAR_J1 = {'power-entry', 'can', 'tire-can', 'wheel-input', 'sensor-power-front', 'sensor-power-rear',
           'sensor-power-tire', 'aux-power', 'afe', 'aux-afe', 'thermistor'}

eligibility = {'schema': 'fome-mc.side-eligibility/1 (proposed consumer: agent-ee, AGENTEE-479)',
               'default': {'faces': ['F', 'B'], 'source': 'C01 (OWNER R:65, 2026-10-19): both faces permitted; no count balance'},
               'count_balance': 'none: no side quota or balance term (C01)',
               'blocks': {}, 'fixed': {}, 'shared': {}}
for b in sorted(blocks):
    faces, restr = FACE_RESTRICT.get(b, (['F', 'B'], []))
    reg = list(REGION.get(b, []))
    if b in NEAR_J1:
        reg.append(J1_B)
    unk = list(UNKNOWNS_ALL) + HOLES
    if b in THERMAL:
        unk.append({'id': 'C23', 'what': 'validated local operating temperature / enclosure airflow; no sourced thermal spacing or hot-zone', 'region': 'block footprint', 'face': 'F,B'})
    if b in ('pre-6v3', 'buck-3v3'):
        unk.append({'id': 'C23', 'what': 'LMR36520 heat-sink copper area / thermal vias under the exposed pad (MFR p28 item 7): the opposite-face area under each EP is reserved for thermal vias; its size is UNKNOWN', 'region': 'under U5/U7 exposed pad', 'face': 'opposite of the IC'})
    intra = []
    for r in rels:
        if r['membership']['device'] == b and r['membership']['support'] == b and r['bound'].get('same_face_required'):
            intra.append(r['id'])
    eligibility['blocks'][b] = {'eligible_faces': faces, 'face_restrictions': restr,
                                'region_restrictions': reg, 'material_unknowns': unk,
                                'whole_block_transform': 'native pcbnew Flip(LEFT_RIGHT) of every member; same-face relationships stay same-face',
                                'same_face_relationships': intra}
# AGENTEE-478c (agent-529, AGENTEE-479 comment 5dbeb677 / Cairn c228b69f): a fixed ROLE is not side or pose
# authority. Per part: (a) SOURCED restrictions with their 474 entry and class, (b) the ENGINEERING anchor selected
# for this candidate (AGENT, reconsiderable, with a disposition), (c) captured STARTING poses (start state only).
REG = 'agentee-474-constraints/RESULT.md'
ANCHOR_RULE = ('chosen BEFORE packing; reconsiderable within the authorized repair with an explicit disposition; '
               'any reconsidered anchor needs final transformed keepout and axis checks (AGENTEE-479 acceptance item)')
ROLE = {
 'J1': {'sourced': [{'entry': 'C05', 'class': 'OWNER', 'restriction': 'right-angle connector (D:175)'},
                    {'entry': 'C05', 'class': 'MFR', 'restriction': 'mating direction +Y to the board edge, recommended PCB edge at local y+9.5 (TE 776163 K1 sh2)'},
                    {'entry': 'C06', 'class': 'MFR', 'restriction': '35-pin PTH pattern and locators; through-board pads/drills on both faces'},
                    {'entry': 'C07/C08', 'class': 'MFR', 'restriction': 'panel/mate interface geometry (owner-relay items labelled as such)'}],
        'anchor': 'XY (45, 55.5) rot 0 on F: AGENT (E:67-83; global X is an agent choice). Face F follows the right-angle body over the board with mating toward the edge; reconsidering the face needs the mirrored mate/panel check',
        'face_decision': 'F as engineering anchor (AGENT), reconsiderable'},
 'J2': {'sourced': [{'entry': 'C15', 'class': 'OWNER/project', 'restriction': 'GNSS RF path on F.Cu over In1 (R:65): the J2 signal launch must be on the F.Cu RF path'},
                    {'entry': 'C09', 'class': 'MECH-DERIVED', 'restriction': 'edge-mount launch at a board edge (footprint geometry)'}],
        'anchor': 'XY (85.24, 28) rot 180: AGENT (D-PCB-4); RF corridor and anchor per AGENTEE-480 (agent-507, landed b389b47), not duplicated here',
        'face_decision': 'F, required by the F-over-In1 RF path (sourced, C15/R:65)'},
 'J3': {'sourced': [{'entry': 'C10', 'class': 'OWNER', 'restriction': 'card slot points off the left board edge (D:176)'},
                    {'entry': 'C11', 'class': 'MFR', 'restriction': 'socket body, push-push travel and socket-owned no-conductor areas move with the part'}],
        'anchor': 'XY (8.9, 32) rot 90 on B, 15 mm lane: AGENT/MECH-DERIVED (D:120-126, E:130-145)',
        'face_decision': 'B as engineering anchor (AGENT), reconsiderable; the off-left-edge direction is the sourced restriction'},
 'U1': {'sourced': [{'entry': 'C12', 'class': 'OWNER', 'restriction': 'accepted antenna overhang / antenna case (D:179); preserve the antenna feed orientation and the all-layer antenna area'},
                    {'entry': 'C12', 'class': 'MFR', 'restriction': 'module land pattern and antenna geometry (datasheet Fig 11-1 p45)'},
                    {'entry': 'C13', 'class': 'MFR', 'restriction': 'housing clearance recommendation (not a board keepout)'}],
        'anchor': 'XY (72.5, 6.5) rot 0 on F: AGENT baseline, not a manufacturer-mandated XY',
        'face_decision': 'F as engineering anchor (AGENT), reconsiderable with the antenna-case check'},
 'U2': {'sourced': [{'entry': 'C14', 'class': 'OWNER/project', 'restriction': 'REQUIRED installed axes X forward, Y left, Z up, marked on silkscreen, without a software rotation (REQUIREMENTS.md:69); tall/heavy parts kept away (R:68, no numeric distance)'}],
        'anchor': 'XY (12, 10) rot 0: AGENT historical pose (E:120-128); no owner/manufacturer source for XY or F-only (C14)',
        'face_decision': ('OPEN for agent-529. Evidence: R:69 requires sensor Z up with no software rotation, so U2 must sit on the board face '
                          'that points UP when installed, at the rotation that maps sensor X forward / Y left. The installed board '
                          'orientation (which face is up, which edge is forward) is not sourced (C14 board-to-bike transform UNKNOWN; C22). '
                          'Either face is physically possible; neither is inherited. Candidate start: F, labelled AGENT, valid only under '
                          'the assumption F faces up; any face/rotation must pass the final axis check')},
 'U3': {'sourced': [{'entry': 'C15', 'class': 'OWNER/project', 'restriction': 'F.Cu over In1 GNSS RF path REQUIRED (R:65); RF_IN pad 11 on the F.Cu path'}],
        'anchor': 'pose is placement-derived (staged off-board in the emitted board); component-relative RF corridor and anchor belong to AGENTEE-480 (agent-507, landed b389b47) and are referenced, not duplicated',
        'face_decision': 'F, required by the F-over-In1 RF path (sourced)'},
}
for h, xy in (('H1', (4, 4)), ('H2', (86, 4)), ('H3', (86, 61)), ('H4', (4, 61))):
    ROLE[h] = {'sourced': [{'entry': 'C03', 'class': 'OWNER', 'restriction': 'a mounting hole in each corner (R:65)'},
                           {'entry': 'C04', 'class': 'OWNER (selection)', 'restriction': 'M3 hardware, agents select (AGENTEE-480); envelope per AGENTEE-480'}],
               'anchor': f'XY {xy}, 3.2 mm NPTH: AGENT (E:227-267)', 'face_decision': 'n/a: NPTH through both faces; hardware reservations on both faces per AGENTEE-480'}
for f, ids in FIXED.items():
    r5, em = EXTRACT['r5']['footprints'][f], BOARD[f]
    eligibility['fixed'][f] = {
        'sourced_restrictions': ROLE[f]['sourced'], 'register': REG,
        'engineering_anchor': {'pose': ROLE[f]['anchor'], 'label': 'AGENT', 'reconsiderable': True, 'rule': ANCHOR_RULE,
                               'disposition': 'retained as the candidate anchor for AGENTEE-479 packing unless reconsidered'},
        'face_decision': ROLE[f]['face_decision'],
        'starting_poses': {'label': 'captured start state only, never a constraint',
                           'r5': {'x_mm': r5['x'], 'y_mm': r5['y'], 'rot_deg': r5['rot'], 'side': r5['side']},
                           'emitted': {k: em.get(k) for k in ('x', 'y', 'rot', 'side')}},
        'sources': ids}
eligibility['shared']['TP1-TP6'] = {
    'eligible_faces': ['F', 'B'], 'constraint': 'either face per pad (bottom allowed); probe-tip approach clearance reserved on the probed face; no fixed fixture pattern, no common-face requirement',
    'sources': ['C20', 'C01'], 'owner_answer': OWNER['C20'],
    'material_unknowns': [{'id': 'C20', 'what': 'probe-tip / pogo-clip approach clearance dimensions (no tall part or screw hardware over or around each pad); size not supplied', 'region': 'each TP pad', 'face': 'probed face'}],
    'owner_reserved': 'none: usage decided by the owner (bench pogo clip, before sealing); clearance geometry is engineering and still UNKNOWN'}
eligibility['shared']['JP1-JP5'] = {
    'eligible_faces': ['F', 'B'], 'constraint': 'face follows its block (tire-can: JP1; thermistor: JP2-JP5); one-time soldering-iron access on the bare board before enclosure',
    'sources': ['C21'], 'owner_answer': OWNER['C21'],
    'material_unknowns': [{'id': 'C21', 'what': 'soldering-iron access zone (tool angle / clear footprint) on the bare board; size not supplied; timing decided (once, on the bench)', 'region': 'each JP', 'face': 'jumper face'}],
    'owner_reserved': 'none'}
TP_PLAN = {
    'purpose': 'UART programming and console on the bench before enclosure with a hand-held pogo clip or probes (owner: "Pogo clip on bench"; R:42); BLE OTA after sealing; no post-seal access',
    'owner_answers': {'C20': OWNER['C20'], 'C21': OWNER['C21']},
    'pads': {f'TP{i}': SCH[f'TP{i}']['pins']['1'][0] for i in range(1, 7)},
    'rules': ['REQUIRED: each pad is reachable by a hand-held pogo clip / probe on the bare board before enclosure; either face, bottom allowed (C20 owner answer, C01)',
              'REQUIRED: probe-tip approach clearance over and around each pad: no tall part and no screw hardware there; clearance size UNKNOWN (C20), reported unresolved, never PASS',
              'NOT required: no fixed fixture pattern, no common face, no grouping distance, no post-seal access',
              'ENGINEERING CONVENIENCE (labelled, optional, never a hard constraint): keeping the six pads on one face and near each other eases a single clip; the planner may use it only as a tie-break',
              'pads stay outside the U1 antenna area (C12) and J3 card path (C10/C11)'],
    'JP1-JP5': 'configured once by solder bridge on the bare board on the bench, before enclosure (owner: "Once, on the bench"; C21); JP1 closes only at the bus end (value text); no tall part within the soldering-iron access zone: size UNKNOWN',
    'owner_reserved_flags': []}
eligibility['test_assembly_access_plan'] = TP_PLAN

# ---------------------------------------------------------------- D4 cross-face templates
templates = {'schema': 'fome-mc.cross-face-templates/1 (proposed consumer: agent-ee, AGENTEE-479)',
             'templates': [
    {'id': 'decoupler-under-device', 'applies_to_classes': ['hf-decoupler', 'secondary-decoupler', 'bulk-decoupler', 'vcc-bias', 'reference-cap', 'input-filter', 'sense-network', 'strap', 'series-input'],
     'excluded_devices': {k: CITE[v][2] for k, v in SAME_FACE_MFR.items()},
     'membership': 'device and support in ONE logical membership (same block, or block anchored on the fixed device)',
     'pin_locality': 'the relationship bound in 3D (dz = 1.6 mm): XY offset <= sqrt(bound^2 - 1.6^2) from the device pin pad; both pads joined by one via within that XY span',
     'per_face_limits': ['support courtyard must not overlap device thermal/EP via field on the opposite face (LMR36520 p28 item 7 for U5/U7)',
                         'support must not sit in any native rule area of its face (C11 J3, C12 U1 antenna, C16/D-PCB-6 via exclusions apply to its via)',
                         'heights UNKNOWN (C19): no claim of enclosure clearance on the support face',
                         'support must not occupy J1 PTH pin field on B (C06) or hole hardware zones (C04 UNKNOWN)']},
    {'id': 'same-face-only', 'applies_to_classes': ['hot-loop-input', 'bulk-input', 'bootstrap', 'switch-inductor', 'ldo-cap', 'crystal', 'crystal-load'],
     'rule': 'cross-face placement of the support is a violation (topology or MFR same-side text)'},
    {'id': 'whole-block-flip', 'rule': 'a whole block on the opposite face is not a split: every member is transformed by the native flip and the relationships are evaluated unchanged'},
             ],
             'split_criterion': {
    'deliberate': ['support on the opposite face of its device', 'relationship class allows cross-face (decoupler-under-device) and the device is not excluded',
                   'measured 3D pin metric within the relationship bound', 'support XY inside the device courtyard expanded by the XY allowance (vertical adjacency, not drift)'],
    'lost_cohesion': ['any member on the face opposite to the block majority/anchor that is NOT covered by a deliberate template instance',
                      'a covered member whose 3D metric exceeds its bound, or that lies outside the device shadow allowance',
                      'a same-face-only relationship split across faces'],
    'regression': '473 congested-underside case: before (current code) members leak to the opposite face without template -> lost_cohesion > 0 (must fail); after -> every opposite-face member classified deliberate (must pass)'},
             'instances': []}
for r in rels:
    if r['support'] and r['bound'].get('status') != 'UNRESOLVED':
        t = 'same-face-only' if r['bound'].get('same_face_required') else 'decoupler-under-device'
        sm = r['bound']['supply_leg_max_mm']
        templates['instances'].append({'relationship': r['id'], 'template': t,
                                       'xy_allowance_mm': round(math.sqrt(max(sm ** 2 - 1.6 ** 2, 0)), 3) if t != 'same-face-only' else None,
                                       'baseline_faces': {k: r['baseline'][k]['faces'] for k in ('r5', 'route3')}})

# ---------------------------------------------------------------- D5 fixed and shared rules
POSE_CLASS = {'J1': 'OWNER right-angle + MFR datum; global XY AGENT (C05)', 'J2': 'MECH-DERIVED/AGENT (C09, D-PCB-4)',
              'J3': 'OWNER off-left-edge direction; XY/rot AGENT (C10)', 'U1': 'OWNER accepted overhang; XY AGENT baseline (C12)',
              'U2': 'AGENT historical pose; OWNER axis mapping (C14)', 'U3': 'MECH-DERIVED from placement (staged off-board in the emitted board); RF path UNRESOLVED (C15)',
              'H1': 'OWNER four corners; XY/drill AGENT (C03)', 'H2': 'same as H1', 'H3': 'same as H1', 'H4': 'same as H1'}
ACCESS = {'J1': ['mating direction +Y to board edge y=65 (C05)', 'B: PTH tails and solder/trim access; stickout UNKNOWN (C06)', 'mate/CPA/latch/harness lanes UNKNOWN (C08)'],
          'J2': ['edge launch at x=90; cable sweep / wrench UNKNOWN (C09)'],
          'J3': ['card mouth points off the left edge; push-push travel 4.0 eject / 0.8 overstroke from catalog; hand access UNKNOWN (C10, C11)'],
          'U1': ['antenna area all layers keep-out (C12); housing 15 mm recommendation is NOT a board keep-out (C13)', 'UART programming via TP1/TP2/TP4/TP5 (C20)'],
          'U2': ['installed axis transform X fwd/Y left/Z up must be preserved; rot/face fixed (C14)', 'tall/heavy parts away: numeric distance UNKNOWN (C14)'],
          'U3': ['RF_IN pad 11 to J2.1 path F-over-In1 (C15, R:65); corridor UNRESOLVED'],
          'H1': ['M3 hardware (owner: "Agents pick M3 hardware"); envelope UNKNOWN F/B pending AGENTEE-480 (C04)'],
          'H2': ['M3 hardware (owner: "Agents pick M3 hardware"); envelope UNKNOWN F/B pending AGENTEE-480 (C04); near U1 antenna/housing (C13)'],
          'H3': ['M3 hardware (owner: "Agents pick M3 hardware"); envelope UNKNOWN F/B pending AGENTEE-480 (C04)'],
          'H4': ['M3 hardware (owner: "Agents pick M3 hardware"); envelope UNKNOWN F/B pending AGENTEE-480 (C04)']}
ADJ = {'U1': ['mcu'], 'U3': ['gnss-rf-feed', 'gnss-antenna-supply'], 'J2': ['gnss-rf-feed'], 'J3': ['storage-support'],
       'J1': ['power-entry', 'can', 'tire-can'], 'U2': []}
fixed_rules = {'schema': 'fome-mc.fixed-shared-rules/1 (proposed consumer: agent-ee, AGENTEE-479)',
               'role_vs_authority': 'complete role coverage is not side or pose authority (AGENTEE-478c)',
               'no_flat_fallback': 'every footprint is a block member, a fixed anchor or a shared part with the rules below; an unlisted footprint is a refusal, never a residual pack',
               'fixed': {}, 'shared': {}, 'rails': {}}
for f in FIXED:
    fp = EXTRACT['r5']['footprints'][f]
    rel_ids = [r['id'] for r in rels if r['device']['ref'] == f]
    fixed_rules['fixed'][f] = {'sourced_restrictions': ROLE[f]['sourced'],
                               'engineering_anchor': {'pose': ROLE[f]['anchor'], 'label': 'AGENT', 'reconsiderable': True,
                                                      'rule': ANCHOR_RULE},
                               'face_decision': ROLE[f]['face_decision'],
                               'starting_poses': {'label': 'captured start state only, never a constraint',
                                                  'r5': {'x_mm': fp['x'], 'y_mm': fp['y'], 'rot_deg': fp['rot'], 'side': fp['side']},
                                                  'emitted': {k: BOARD[f].get(k) for k in ('x', 'y', 'rot', 'side')}},
                               'pose_authority_summary': POSE_CLASS[f], 'register_entries': FIXED[f],
                               'adjacent_blocks': ADJ.get(f, []), 'support_relationships': rel_ids,
                               'access': ACCESS[f],
                               'side_rule': 'per face_decision (sourced restriction, AGENT anchor or OPEN); never inherited from the starting pose'}
fixed_rules['shared']['TP1-TP6'] = {'role': 'test', 'anchor': 'none (movable)', 'adjacency': TP_PLAN['rules'],
                                    'access': 'hand-held pogo clip / probes on the bare board before enclosure; probe-tip approach clearance only (size UNKNOWN); no fixture pattern; no post-seal access',
                                    'owner_answer': OWNER['C20'], 'side_rule': 'either face per pad (bottom allowed); common face is an optional labelled convenience only'}
fixed_rules['shared']['JP1-JP5 (block members)'] = {'role': 'assembly configuration', 'membership': 'JP1 tire-can; JP2-JP5 thermistor',
                                                     'access': 'one-time soldering-iron access on the bare board before enclosure (zone size UNKNOWN)',
                                                     'owner_answer': OWNER['C21'], 'side_rule': 'face of its block'}
for rail in RAILS:
    fixed_rules['rails'][rail] = {'parts': 'none: rails are nets, not memberships; rail capacitors are bound to their device pins in relationship-bounds.json', 'merge_rule': 'a common rail never merges blocks'}

# ---------------------------------------------------------------- write
def anchor_of(b):
    a = anchors.get(b)
    return {'member': a} if a else {'fixed': FIXED_ANCHOR.get(b)} if FIXED_ANCHOR.get(b) else {'none': 'centroid of members'}
alloc2 = {'schema': 'agent-ee.block-allocation/2 (proposed; /1 consumers ignore fixed/shared)',
          'derived_from': {'path': 'telemetry-pod/expansion/blocks/allocation.json', 'sha256': sha(ALLOC_PATH)},
          'board_sha256': EXTRACT['emitted']['sha256'],
          'inventory': {'board_sha256': EXTRACT['emitted']['sha256'], 'board_extract': 'extract/emitted-0b68a0ac.json', 'schematic_netlist': 'extract/' + NETLIST.name,
                        'schematic_netlist_sha256': sha(NETLIST), 'schematic_only_not_yet_on_board': SCHEMATIC_ONLY},
          'blocks': [{'id': b, 'references': sorted(rs, key=nat), 'anchor': anchor_of(b),
                      'interfaces_to_fixed': FIXED_ANCHOR.get(b)} for b, rs in sorted(blocks.items())],
          'fixed': [{'reference': f, 'register_entries': ids} for f, ids in FIXED.items()],
          'shared': [{'reference': t, 'role': r} for t, r in SHARED.items()],
          'corrections': corrections}
for name, doc in [('allocation-v2.json', alloc2), ('side-eligibility.json', eligibility),
                  ('relationship-bounds.json', {'schema': 'fome-mc.relationship-bounds/1 (proposed consumer: agent-ee, AGENTEE-479)',
                                                'baselines': {k: EXTRACT[k]['sha256'] for k in ('r5', 'route3')},
                                                'metric_note': 'pad-centre distance is a lower bound of trace length; routed length is measured only after routing',
                                                'bound_classes': {k: {'supply_leg_max_mm': v[0], 'return_leg_max_mm': v[1], 'same_face_required': v[2], 'topology': v[3], 'numeric_provenance': EJ} for k, v in BOUND.items()},
                                                'sources': SRC, 'old_obligations_disposition': old_dispo, 'relationships': rels}),
                  ('cross-face-templates.json', templates), ('fixed-shared-rules.json', fixed_rules)]:
    (OUT / name).write_text(json.dumps(doc, indent=1) + '\n')
print('blocks', len(blocks), 'members', sum(len(v) for v in blocks.values()), 'fixed', len(FIXED), 'shared', len(SHARED),
      'relationships', len(rels), 'unresolved', sum(1 for r in rels if r['bound'].get('status') == 'UNRESOLVED'))
