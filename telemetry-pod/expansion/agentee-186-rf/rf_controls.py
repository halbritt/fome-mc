"""AGENTEE-186 RF native controls on a DISPOSABLE copy (the source board is never saved).
Usage: rf_controls.py <project dir> <rules file> <work dir> <out.json>
Adds F.Cu test tracks (x 150-156 mm, off the outline, plus two inside U3's courtyard) and runs native DRC:
  nominal 0.293 RF; too narrow 0.25; too wide 0.34; gap 0.201 mm (below the 0.2032 nominal, above the 0.2 default);
  gap 0.30 mm (above nominal); wrong net 0.25 on /GNSS_PPS; launch 0.25 and 0.34 inside U3's courtyard."""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
import pcbnew as k
src, rules, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
work.mkdir(parents=True)
for n in ('telemetry-pod.kicad_pcb', 'telemetry-pod.kicad_pro'):
    shutil.copyfile(src / n, work / n)
shutil.copyfile(rules, work / 'telemetry-pod.kicad_dru')
b = k.LoadBoard(str(work / 'telemetry-pod.kicad_pcb'))
nets = {str(n): v for n, v in b.GetNetsByName().items()}
def track(net, w, x0, y, x1=None):
    t = k.PCB_TRACK(b); t.SetStart(k.VECTOR2I(k.FromMM(x0), k.FromMM(y))); t.SetEnd(k.VECTOR2I(k.FromMM(x1 if x1 else x0 + 6), k.FromMM(y)))
    t.SetWidth(k.FromMM(w)); t.SetLayer(k.F_Cu); t.SetNet(nets[net]); b.Add(t); return t.m_Uuid.AsString()
T = {}
T['nominal'] = track('/POD_GNSS_RF', 0.293, 150, 100)
T['too_narrow'] = track('/POD_GNSS_RF', 0.25, 150, 103)
T['too_wide'] = track('/POD_GNSS_RF', 0.34, 150, 106)
T['gap_below_rf'] = track('/POD_GNSS_RF', 0.293, 150, 110); T['gap_below_gnd'] = track('/GND', 0.293, 150, 110 + 0.293 + 0.201)
T['gap_above_rf'] = track('/POD_GNSS_RF', 0.293, 150, 115); T['gap_above_gnd'] = track('/GND', 0.293, 150, 115 + 0.293 + 0.30)
T['wrong_net'] = track('/GNSS_PPS', 0.25, 150, 120)
u3 = next(f for f in b.GetFootprints() if f.GetReference() == 'U3'); c = u3.GetPosition()
cx, cy = k.ToMM(c.x), k.ToMM(c.y)
T['launch_narrow'] = track('/POD_GNSS_RF', 0.25, cx - 1, cy - 2, cx + 1)
T['launch_wide'] = track('/POD_GNSS_RF', 0.34, cx - 1, cy + 2, cx + 1)
k.SaveBoard(str(work / 'telemetry-pod.kicad_pcb'), b)
rep = work / 'drc.json'
subprocess.run(['kicad-cli', 'pcb', 'drc', '--severity-all', '--format', 'json', '-o', str(rep), str(work / 'telemetry-pod.kicad_pcb')], check=True, capture_output=True)
viol = json.loads(rep.read_text()).get('violations', [])
uu = {v: k_ for k_, v in T.items()}
hits = {k_: [] for k_ in T}
for v in viol:
    for it in v.get('items', []):
        if it.get('uuid') in uu and v['type'] in ('track_width', 'clearance'):
            hits[uu[it['uuid']]].append(f"{v['type']}: {v['description']}")
doc = {'rules_sha256': hashlib.sha256(rules.read_bytes()).hexdigest(), 'board_sha256': hashlib.sha256((src / 'telemetry-pod.kicad_pcb').read_bytes()).hexdigest(),
       'u3_centre_mm': [cx, cy], 'findings': hits, 'total_violations': len(viol)}
out.write_text(json.dumps(doc, indent=1) + '\n')
for k_, v in hits.items(): print(k_, v)
