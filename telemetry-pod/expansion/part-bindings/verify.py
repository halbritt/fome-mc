"""Check prepared identity metadata; native checks must be explicitly requested or deferred."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from agent_ee.jlc_stock_capture import validate_capture
from agent_ee.part_binding import parse_param_value

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-only', action='store_true', help='report native verification NOT_RUN')
args = parser.parse_args()
def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}
with tempfile.TemporaryDirectory(prefix='pod-part-bindings-') as temporary:
    run = Path(temporary) / 'candidate'
    command = [sys.executable, str(root / 'prepare.py'), '--out', str(run)]
    if args.source_only:
        command.append('--source-only')
    subprocess.run(command, check=True)
    if hashes(run / 'inputs') != hashes(root / 'prepared/inputs'):
        raise ValueError('Prepared source does not reproduce')
    receipt = json.loads((run / 'binding-receipt.json').read_text())
    if receipt != json.loads((root / 'prepared/binding-receipt.json').read_text()):
        raise ValueError('Binding receipt changed')
    intent = json.loads((run / 'inputs/intent.json').read_text())
    rows = []
    for c in intent['components']:
        state = ('power_symbol' if c['lib_id'] == 'power:PWR_FLAG' else
                 'copper_feature_policy_pending' if c['reference'] in {'JP1','JP2','JP3','JP4','JP5'} else
                 'binding_present_unqualified' if c.get('part_binding') else 'binding_missing')
        rows.append({'id': c['id'], 'reference': c['reference'], 'value': c['value'], 'state': state})
        binding = c.get('part_binding', {})
        if 'PARAM_Datasheet' in binding:
            parsed = parse_param_value(binding['PARAM_Datasheet'], 'PARAM_Datasheet')
            if parsed['url'] != binding['Datasheet']:
                raise ValueError('Datasheet URL disagreement: ' + c['reference'])
    inventory = {'schema':'pod-binding-inventory/1', 'counts':dict(Counter(r['state'] for r in rows)), 'components':rows}
    if inventory != json.loads((root / 'inventory.json').read_text()):
        raise ValueError('Binding inventory differs')
    if not args.source_only:
        schematic = run / 'project/telemetry-pod.kicad_sch'
        subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(run/'native.xml'),str(schematic)], check=True)
        subprocess.run(['kicad-cli','sch','erc','--format','json','-o',str(run/'erc.json'),str(schematic)], check=True)
        erc = json.loads((run / 'erc.json').read_text())
        prior = json.loads((root.parent / 'native-candidate/erc.json').read_text())
        if erc['ignored_checks'] != prior['ignored_checks'] or any(s['violations'] for s in erc['sheets']):
            raise ValueError('Native ERC changed')
    check = [sys.executable,str(root/'review/check_bindings.py'),str(root),str(run),str(run/'review.json')]
    if args.source_only:
        check.append('--source-only')
    subprocess.run(check, check=True)
# Fresh eMMC observation is retained even though U14 remains unbound.
validate_capture(json.loads((root/'emmc-stock/catalog.json').read_text()),
                 lambda path: (root/'emmc-stock'/path).read_bytes())
print('PASS: identity source checks; native verification ' + ('NOT_RUN' if args.source_only else 'PASS'))
