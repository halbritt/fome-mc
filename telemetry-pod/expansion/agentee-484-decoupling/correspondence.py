"""AGENTEE-484 schematic/board correspondence (read-only; no save).
Usage: correspondence.py <native.xml from the schematic> <board.kicad_pcb> <out.json>
Compares every schematic component with its board footprint: presence, footprint id, value, and the net of
every pad; board-only footprints are listed separately."""
import hashlib, json, sys
import xml.etree.ElementTree as ET
import pcbnew
xml, pcb, out = sys.argv[1:4]
root = ET.parse(xml).getroot()
sch = {c.get('ref'): {'footprint': c.findtext('footprint'), 'value': c.findtext('value')} for c in root.iter('comp')}
pins = {}
for n in root.iter('net'):
    for node in n.findall('node'):
        pins[(node.get('ref'), node.get('pin'))] = n.get('name')
sha = hashlib.sha256(open(pcb, 'rb').read()).hexdigest()
b = pcbnew.LoadBoard(pcb)
brd = {}
for fp in b.GetFootprints():
    brd[fp.GetReference()] = {'footprint': fp.GetFPIDAsString(), 'value': fp.GetValue(),
                              'pads': {p.GetNumber(): p.GetNetname() for p in fp.Pads() if p.GetNumber()}}
findings = []
for r, c in sorted(sch.items()):
    f = brd.get(r)
    if f is None:
        findings.append({'ref': r, 'kind': 'missing_on_board'}); continue
    if f['footprint'] != c['footprint']:
        findings.append({'ref': r, 'kind': 'footprint', 'sch': c['footprint'], 'board': f['footprint']})
    if f['value'] != c['value']:
        findings.append({'ref': r, 'kind': 'value', 'sch': c['value'], 'board': f['value']})
    for num, net in f['pads'].items():
        want = pins.get((r, num))
        if want is not None and want != net:
            findings.append({'ref': r, 'pad': num, 'kind': 'net', 'sch': want, 'board': net})
    for (rr, num), net in pins.items():
        if rr == r and num not in f['pads']:
            findings.append({'ref': r, 'pad': num, 'kind': 'pin_without_pad', 'sch': net})
board_only = sorted(set(brd) - set(sch))
assert hashlib.sha256(open(pcb, 'rb').read()).hexdigest() == sha
doc = {'schematic_netlist_sha256': hashlib.sha256(open(xml, 'rb').read()).hexdigest(), 'board_sha256': sha,
       'schematic_components': len(sch), 'board_footprints': len(brd), 'board_only': board_only,
       'findings': findings, 'finding_count': len(findings)}
json.dump(doc, open(out, 'w'), indent=1)
print(len(sch), len(brd), board_only, len(findings))
