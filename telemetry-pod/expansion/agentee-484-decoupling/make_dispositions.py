"""AGENTEE-484 per-pin decoupling dispositions (data). Usage: make_dispositions.py <expansion dir> <out.json>"""
import hashlib, json, sys
from pathlib import Path
X = Path(sys.argv[1])
sha = lambda p: hashlib.sha256((X / p).read_bytes()).hexdigest()
DS = {'LSM6DSO32': 'parts-closure/recovered-pilot/core/datasheets-current/fce1bf36cb460a31e2d1f3ede054b5d2e68f07b8f9039cb09062522e9bcf4e2c.pdf',
      'NEO-M9N-IM': 'parts-closure/recovered-pilot/power-source/acquisition/402991ee7566b52693f3ab3400d2e42d878be51ba4de90e8cac049be6104f524.pdf',
      'TPS2553': 'parts-closure/recovered-pilot/power-source/acquisition/7438702fe3f737612ed5c8f133f60b81eda9c68e3b74ddeffe913858f59c4892.pdf',
      'MCP3208': 'native-candidate/sources/mcp3208.pdf',
      'ADA4096': 'parts-closure/recovered-pilot/power-source/acquisition-adoption/1b0bcb3b671fc2fcfa8ab1938e74d5191322da58252000488f4085c424f6037e.pdf',
      'OPA320': 'parts-closure/recovered-pilot/power-source/acquisition-adoption/d6b3c62b2d37a5cb6776d49d62cc4a48cd4fe7226fbd93e52583822adbdae3d0.pdf',
      'TJA1051': 'interface-preparation/sources/tja1051.pdf',
      'REF50': 'interface-preparation/aux-power/ref50.pdf',
      'LMR36520': 'parts-closure/recovered-pilot/power-source/acquisition/cb8ebe03bcc7860306c5e291bd6d892cb951f20cf5f21f15ecbcd8efd3029dd1.pdf'}
src = lambda k, page, text: {'source': 'telemetry-pod/expansion/' + DS[k], 'sha256': sha(DS[k]), 'page': page, 'text': text}
C100N = {'part': 'TDK CGA3E2X7R1H104KT0Y0N (LCSC C76711), 100 nF 50 V X7R 0603, already used (C38 etc.)'}
C1U = {'part': 'TDK CGA3E1X7R1C105KT0Y0N (LCSC C76706), 1 uF 16 V X7R 0603, already used (C44, C18)'}
rail3 = '+3V3 from U7 (LMR36520) bank; return /GND, In1 plane'
rows = [
 {'pin': 'U2.8 VDD', 'requirement': [src('LSM6DSO32', 53, 'Power supply decoupling capacitors (C1, C2 = 100 nF ceramic) should be placed as near as possible to the supply pin of the device'), src('LSM6DSO32', 24, 'Recommended 100 nF filter capacitor')],
  'required': '100 nF ceramic per supply pin (C1, C2)', 'effective': '100 nF X7R 50 V on a 3.3 V rail: negligible DC-bias loss', 'disposition': 'REBIND existing C38', 'support': 'C38', **C100N, 'block': 'imu-support (anchored on fixed U2)', 'topology': rail3, 'bound': 'hf-decoupler: supply leg <= 3.0 mm, return <= 5.0 mm (3D pad-centre; EJ numeric)', 'side': 'cross-face allowed (decoupler-under-device)', 'status': 'RESOLVED'},
 {'pin': 'U2.5 VDDIO', 'requirement': [src('LSM6DSO32', 53, 'C1, C2 = 100 nF ceramic ... as near as possible to the supply pin')], 'required': '100 nF ceramic (second capacitor; VDD and VDDIO are separate pins 1.67 mm apart)', 'effective': 'as above',
  'disposition': 'REBIND existing C41', 'support': 'C41', **C100N, 'block': 'imu-support', 'topology': rail3, 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED'},
 {'pin': 'U3.23 VCC', 'requirement': [src('NEO-M9N-IM', 81, 'The VCC pad needs a large pad and the decoupling capacitor must be placed as close as possible')], 'required': 'decoupling capacitor, value not stated in the retained integration manual text',
  'effective': '1 uF X7R 16 V at 3.3 V (value is ENGINEERING JUDGEMENT: no manufacturer value found)', 'disposition': 'REBIND existing C44', 'support': 'C44', **C1U, 'block': 'gnss-receiver-support (anchored on fixed U3)', 'topology': rail3 + '; adjacent GND pin 24', 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED (value EJ)'},
 {'pin': 'U3.22 V_BCKP', 'requirement': [src('NEO-M9N-IM', 71, 'If no backup supply voltage is available, connect the V_BCKP pin to VCC'), src('NEO-M9N-IM', 90, 'Backup current NEO-M9N: I_BCKP = 45 uA')],
  'required': 'connection to VCC; no separate decoupler stated', 'effective': 'C44 at adjacent VCC pin 23 (1.1 mm pitch) is local to pin 22: not a remote capacitor', 'disposition': 'NO DEDICATED CAPACITOR - PENDING-510', 'support': 'C44 (shared, adjacent pin)', 'block': 'gnss-receiver-support', 'topology': 'V_BCKP tied to VCC (+3V3) in the schematic', 'bound': 'U3.22-C44 supply leg <= 3.0 mm, same as pin 23', 'side': 'cross-face allowed', 'status': 'PENDING-510'},
 {'pin': 'U10.1 IN', 'requirement': [src('TPS2553', 25, 'placing the 100-nF bypass capacitor near the IN and GND pins, and make the connections using a low-inductance trace')], 'required': '100 nF', 'effective': '100 nF X7R', 'disposition': 'REBIND existing C43', 'support': 'C43', **C100N,
  'block': 'gnss-antenna-supply', 'topology': rail3 + '; U10 GND pin 2', 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED'},
 {'pin': 'U4.16 Vdd', 'requirement': [src('MCP3208', 23, 'A bypass capacitor should always be used ... placed as close as possible to the device pin. A bypass capacitor value of 1 uF is recommended')], 'required': '1 uF', 'effective': '1 uF X7R 16 V', 'disposition': 'ADD C130', 'support': 'C130', **C1U,
  'block': 'adc', 'topology': rail3 + '; U4 AGND/DGND pins', 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED (source + emission; production regeneration pending)'},
 {'pin': 'U8.4 V+', 'requirement': [{'source': 'telemetry-pod/expansion/' + DS['ADA4096'], 'sha256': sha(DS['ADA4096']), 'page': None, 'text': 'no decoupling wording found in the retained ADA4096-4 datasheet text (pdftotext search: bypass/decoupl/0.1 uF)'}],
  'required': 'UNSTATED by retained source; local supply bypass is standard op-amp practice (TOPOLOGY + ENGINEERING JUDGEMENT)', 'effective': '100 nF X7R', 'disposition': 'ADD C131', 'support': 'C131', **C100N, 'block': 'afe', 'topology': rail3 + '; V- pin 11 = GND', 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED (value EJ; 510 to confirm source gap)'},
 {'pin': 'U9.5 V+', 'requirement': [src('OPA320', 28, 'Place 0.1-uF bypass capacitors close to the power-supply pins'), src('OPA320', 16, 'should have local bypass ceramic capacitors (typically 0.001 uF to 0.1 uF)')], 'required': '0.1 uF', 'effective': '100 nF X7R', 'disposition': 'ADD C132', 'support': 'C132', **C100N,
  'block': 'sensor-ref', 'topology': rail3 + '; V- pin 2 = GND', 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED'},
 {'pin': 'U100.5 VIO', 'requirement': [{'source': 'telemetry-pod/expansion/' + DS['TJA1051'], 'sha256': sha(DS['TJA1051']), 'page': 13, 'text': 'Fig 6 typical application of the TJA1051T/3: capacitor labels are graphics, not extractable text; value NOT verified from text'}],
  'required': 'UNVERIFIED value; VIO supplies the I/O level adapter (p4) from +3V3, a separate rail from VCC (+5V_CAN, C100)', 'effective': '100 nF X7R', 'disposition': 'ADD C133', 'support': 'C133', **C100N, 'block': 'can', 'topology': rail3 + '; U100 GND pin 2', 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED (value EJ; 510 to check Fig 6)'},
 {'pin': 'U11.2 Vin', 'requirement': [src('REF50', 29, 'TI recommends a supply bypass capacitor ranging from 1uF to 50uF for REF50xxI and REF50xxAI'), src('REF50', 29, 'Place the power-supply bypass capacitor as closely as possible to the supply and ground pins')], 'required': '1 uF to 50 uF', 'effective': '1 uF X7R 16 V on 6.3 V: at the low end of the range after DC-bias derating; 510 to judge (larger value is a design option)',
  'disposition': 'REBIND existing C18', 'support': 'C18', **C1U, 'block': 'supplies-5v', 'topology': '/PRE_6V3 from U5 (C6/C7 2x22 uF remain); return /GND', 'bound': 'hf-decoupler', 'side': 'cross-face allowed', 'status': 'RESOLVED (derating flagged)'},
]
banks = {
 'U7 3V3 output (LMR36520)': {'requirement': src('LMR36520', 18, 'Table 8-1, 400 kHz, 3.3 V, 6.8 uH: nominal COUT 3 x 22 uF, minimum COUT 3 x 22 uF (rated)'), 'kept': ['C13', 'C14', 'C15'], 'released': ['C38', 'C41', 'C43', 'C44'],
   'finding': 'the table requirement is met by C13-C15 alone; the four small capacitors were never part of it, so rebinding them preserves the output bank and loop stability as tabulated'},
 'U5 6V3 output (LMR36520)': {'requirement': src('LMR36520', 18, 'Table 8-1 rows 5 V: 2 x 22 uF and 12 V: 4 x 10 uF (6.3 V not tabulated)'), 'kept': ['C6', 'C7'], 'released': ['C18'],
   'finding': 'C6/C7 2 x 22 uF match the 5 V row; 6.3 V is between rows, so 510 should confirm. C18 (1 uF) is not part of the tabulated bank'},
}
doc = {'schema': 'fome-mc.decoupling-dispositions/1', 'decision': 'agent-529, Plane AGENTEE-484', 'rows': rows, 'banks': banks,
       'double_counting': 'each capacitor serves exactly one pin, except C44 shared by adjacent U3 pins 22/23 (PENDING-510); no remote capacitor is counted for any pin',
       'new_parts': ['C130', 'C131', 'C132', 'C133'], 'rebinds': ['C38', 'C41', 'C43', 'C44', 'C18']}
Path(sys.argv[2]).write_text(json.dumps(doc, indent=1) + '\n')
print(len(rows))
