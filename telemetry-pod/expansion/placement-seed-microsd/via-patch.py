"""Apply the D-PCB-1 thermal-via patch (0.20 mm drill -> 0.30 / 0.70 mm) to the five footprints
whose patched library sources live in ../design-rules/footprints (U1, U5, U6, U7, U12), on a copy.
Usage: python3 -B via-patch.py IN.kicad_pcb OUT.kicad_pcb"""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for fp in b.GetFootprints():
    if fp.GetReference() in ('U1', 'U5', 'U6', 'U7', 'U12'):
        for pad in fp.Pads():
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and pad.GetDrillSizeX() == 200000:
                pad.SetDrillSize(pcbnew.VECTOR2I(300000, 300000)); pad.SetSize(pcbnew.VECTOR2I(700000, 700000)); n += 1
pcbnew.SaveBoard(sys.argv[2], b); print(json.dumps({'vias_patched': n}))
