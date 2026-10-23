"""AGENTEE-488: pad-centre relationship measurement shared by build_prep.py and its tests.

A relationship with a declared return leg is measured on that leg; a missing, wrong-net or otherwise unmeasurable
required return makes the verdict 'unsatisfied', never 'within'. A NAMED return (device pad, support pad, net) is
measured only between exactly those pads on exactly that net: there is no GND inference for it."""
import math


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
    if not a or not bs or a['net'] != netname:
        return None
    return min(dist(fa, a, fb, b) for b in bs)


def gnd_return_leg(board, ic, cap):
    if ic not in board or cap not in board or board[cap].get('on_board') is False:
        return None
    fi, fc = board[ic], board[cap]
    gi = [p for p in fi['pads'] if p['net'] == '/GND']
    gc = [p for p in fc['pads'] if p['net'] == '/GND']
    if not gi or not gc:
        return None
    return min(dist(fi, a, fc, b) for a in gi for b in gc)


def named_return_leg(board, ic, cap, ret):
    """Exactly device pad ret['device_pad'] and support pad ret['support_pad'], both on net ret['net']."""
    if ic not in board or cap not in board or board[cap].get('on_board') is False:
        return None
    a = pad(board[ic], ret['device_pad'], ret['net'])
    b = pad(board[cap], ret['support_pad'], ret['net'])
    if a is None or b is None:
        return None
    return dist(board[ic], a, board[cap], b)


def verdict(bound, supply, ret, same_face):
    """'within' only when every declared leg is measured and within its bound."""
    if bound.get('status') == 'UNRESOLVED' or supply is None:
        return 'n/a'
    if bound.get('return_leg_max_mm') is not None and ret is None:
        return 'unsatisfied (required return leg missing, wrong net or unmeasurable)'
    ok = supply <= bound['supply_leg_max_mm'] and (bound.get('return_leg_max_mm') is None or ret <= bound['return_leg_max_mm'])
    if bound.get('same_face_required') and not same_face:
        ok = False
    return 'within' if ok else 'exceeds'
