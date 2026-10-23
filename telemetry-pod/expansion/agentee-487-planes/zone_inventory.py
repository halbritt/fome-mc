"""AGENTEE-487 read-only zone inventory (no save). Usage: zone_inventory.py <out.json> LABEL=BOARD ...
Per board: sha256, every board-owned zone (rule area or copper; net name exactly as stored; layers; filled
polygon count), and whether the plane-plan nets /GND and /+3V3 exist as board nets."""
import hashlib, json, sys
import pcbnew
out = {}
for arg in sys.argv[2:]:
    label, path = arg.split('=', 1)
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    b = pcbnew.LoadBoard(path)
    zones = []
    for z in b.Zones():
        zones.append({'rule_area': z.GetIsRuleArea(), 'net': z.GetNetname(), 'name': z.GetZoneName(),
                      'layers': [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
                      'filled_polys': sum(z.GetFilledPolysList(l).OutlineCount() for l in z.GetLayerSet().Seq()) if not z.GetIsRuleArea() else None})
    nets = {str(k) for k in b.GetNetsByName().keys()}
    out[label] = {'path': path, 'sha256': sha, 'zones': zones,
                  'copper_zones': sum(not z['rule_area'] for z in zones), 'rule_areas': sum(z['rule_area'] for z in zones),
                  'net_/GND': '/GND' in nets, 'net_GND': 'GND' in nets, 'net_/+3V3': '/+3V3' in nets, 'net_+3V3': '+3V3' in nets,
                  'footprint_owned_zones': sum(len(list(fp.Zones())) for fp in b.GetFootprints())}
json.dump(out, open(sys.argv[1], 'w'), indent=1)
for k, v in out.items():
    print(k, v['sha256'][:12], 'copper', v['copper_zones'], 'rule', v['rule_areas'], 'fp-owned', v['footprint_owned_zones'], '/GND', v['net_/GND'], 'GND', v['net_GND'])
