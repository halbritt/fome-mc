"""AGENTEE-484r native proof of the RF width rule (disposable copy only; the source board is never saved).
Usage: drc_proof.py <source project dir> <rules file> <work dir> <out.json>
Copies board + project, installs the given rules file, adds three test tracks on F.Cu outside other copper:
  T1 0.20 mm on /POD_GNSS_RF (must be flagged by agent_ee_netclass_RF_50 when the binding exists),
  T2 0.335 mm on /POD_GNSS_RF (must not be flagged), T3 0.20 mm on /GNSS_PPS (control: not selected),
saves the COPY, runs kicad-cli pcb drc (all severities, JSON) and reports the track_width findings on T1-T3."""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
import pcbnew
src, rules, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
work.mkdir(parents=True)
for n in ('telemetry-pod.kicad_pcb', 'telemetry-pod.kicad_pro'):
    shutil.copyfile(src / n, work / n)
shutil.copyfile(rules, work / 'telemetry-pod.kicad_dru')
b = pcbnew.LoadBoard(str(work / 'telemetry-pod.kicad_pcb'))
nets = b.GetNetsByName()
def track(name, width_mm, y_mm):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(150), pcbnew.FromMM(y_mm)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(156), pcbnew.FromMM(y_mm)))
    t.SetWidth(pcbnew.FromMM(width_mm)); t.SetLayer(pcbnew.F_Cu); t.SetNet(nets[name]); b.Add(t)
    return {'net': name, 'width_mm': width_mm, 'y_mm': y_mm, 'uuid': t.m_Uuid.AsString()}
tracks = {'T1': track('/POD_GNSS_RF', 0.20, 100), 'T2': track('/POD_GNSS_RF', 0.335, 105), 'T3': track('/GNSS_PPS', 0.20, 110)}
b.Save(str(work / 'telemetry-pod.kicad_pcb'))
rep = work / 'drc.json'
subprocess.run(['kicad-cli', 'pcb', 'drc', '--severity-all', '--format', 'json', '-o', str(rep), str(work / 'telemetry-pod.kicad_pcb')], check=True, capture_output=True)
d = json.loads(rep.read_text())
viol = d.get('violations', [])
uu = {v['uuid']: k for k, v in tracks.items()}
hits = {k: [] for k in tracks}
for v in viol:
    for it in v.get('items', []):
        if it.get('uuid') in uu and v['type'] == 'track_width':
            hits[uu[it['uuid']]].append(v['description'])
doc = {'rules_file_sha256': hashlib.sha256(rules.read_bytes()).hexdigest(),
       'source_board_sha256': hashlib.sha256((src / 'telemetry-pod.kicad_pcb').read_bytes()).hexdigest(),
       'tracks': tracks, 'track_width_findings': hits, 'total_violations': len(viol)}
out.write_text(json.dumps(doc, indent=1) + '\n')
print(json.dumps(hits))
