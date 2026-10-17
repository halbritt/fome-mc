#!/usr/bin/env python3
"""Temporarily lock a board's existing copper for a routing backend, then restore.

    route_locks.py lock BOARD.kicad_pcb RECORD.json      lock every unlocked track/via (in place)
    route_locks.py restore BOARD.kicad_pcb RECORD.json   unlock exactly those items again (in place)

Backends treat locked copper as untouchable, but some of their recovery paths
rework unlocked input copper even when told to keep it (KRT's net rescue moves
stubs between layers). For `route.py --protect existing` the wrapper locks the
input's unlocked tracks and vias in the work copy, routes, and then restores the
original lock flags on the backend's output. Items are matched by exact
geometry (layer(s), net, width/size, end points), so a backend that rewrites
UUIDs still gets its flags restored. Runs with KiCad's pcbnew module.
"""
import json
import sys


def key(t, pcbnew):
    net = t.GetNetname()
    if isinstance(t, pcbnew.PCB_VIA):
        p = t.GetPosition()
        return ["via", net, int(p.x), int(p.y), int(t.GetWidth(pcbnew.F_Cu)), int(t.GetDrillValue()),
                int(t.TopLayer()), int(t.BottomLayer())]
    a, b = sorted([(int(t.GetStart().x), int(t.GetStart().y)), (int(t.GetEnd().x), int(t.GetEnd().y))])
    mid = []
    if isinstance(t, pcbnew.PCB_ARC):
        m = t.GetMid()
        mid = [int(m.x), int(m.y)]
    return ["track", net, int(t.GetLayer()), int(t.GetWidth()), *a, *b, *mid]


def main(argv):
    import pcbnew
    if len(argv) != 3 or argv[0] not in ("lock", "restore"):
        sys.exit(__doc__)
    board_path, record = argv[1], argv[2]
    board = pcbnew.LoadBoard(board_path)
    if argv[0] == "lock":
        keys = []
        for t in board.GetTracks():
            if not t.IsLocked():
                t.SetLocked(True)
                keys.append(key(t, pcbnew))
        board.Save(board_path)
        with open(record, "w") as f:
            json.dump(keys, f)
        print("LOCKS_JSON: " + json.dumps({"locked": len(keys)}))
        return 0
    wanted = {}
    for k in json.load(open(record)):
        wanted[json.dumps(k)] = wanted.get(json.dumps(k), 0) + 1
    restored = 0
    for t in board.GetTracks():
        k = json.dumps(key(t, pcbnew))
        if t.IsLocked() and wanted.get(k):
            t.SetLocked(False)
            wanted[k] -= 1
            restored += 1
    board.Save(board_path)
    print("LOCKS_JSON: " + json.dumps({"restored": restored, "not_found": sum(wanted.values())}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
