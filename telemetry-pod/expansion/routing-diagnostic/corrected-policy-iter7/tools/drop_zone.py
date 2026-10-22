"""drop_zone.py BOARD OUT NAME: copy of BOARD without the rule area called NAME (attribution fixture)."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
z = [z for z in b.Zones() if z.GetZoneName() == sys.argv[3]]
assert len(z) == 1
b.Remove(z[0])
assert pcbnew.SaveBoard(sys.argv[2], b)
