#!/usr/bin/env python3
"""KiCad <-> Specctra bridge for Freerouting, through KiCad's own pcbnew module.

    route_specctra.py export BOARD.kicad_pcb OUT.dsn [--skip-nets NETS.json] [--default-clearance UM]
                                                     [--dru RULES.kicad_dru] [--clearance-margin UM]
    route_specctra.py import BOARD.kicad_pcb SESSION.ses OUT.kicad_pcb

kicad-cli 10 has no DSN export or SES import, so this uses the two-argument
SWIG functions pcbnew.ExportSpecctraDSN(board, path) and
pcbnew.ImportSpecctraSES(board, path), which work headless (the one-argument
forms need a running PCB editor).

export --skip-nets: Freerouting selects work by net class only. Nets outside
the routing scope are moved into a copy of their class (same width, clearance
and via rules) named `<class>__skip`; the caller passes those names to
--router.autorouter.ignore_net_classes. Clearances are unchanged.

export --default-clearance: raise the Default net class (`kicad_default`) and
the board-level clearance rule to UM micrometres when they are lower. It only
ever tightens, matching KRT's --clearance (which sets the Default class).

export --dru: KiCad's DSN export ignores custom rules. The subset Specctra can
express -- a minimum clearance between net classes, with no layer, item-type or
area condition -- is added as (class_class ...) rules, which Freerouting reads
into its clearance matrix. Supported conditions:
    A.NetClass == 'X' && B.NetClass == 'Y'   (X against Y)
    A.NetClass == 'X' && B.NetClass != 'X'   (X against every other class)
    A.NetClass == 'X'                        (X against every class)
Every other rule is reported as untranslated; KiCad DRC still grades all rules.

export --clearance-margin: add UM micrometres to every untyped clearance in the
DSN (board rule, class rules, translated class_class rules). Freerouting
approximates pad shapes, so it can land a few micrometres inside a clearance
that KiCad then grades exactly; a margin trades routing room for that.

Pre-existing copper is locked for the round trip. KiCad exports locked items
as (type fix), which Freerouting freezes and never writes back, and its SES
import leaves locked items untouched. Unlocked items would instead be deleted
and rebuilt from the session, where Freerouting may have collapsed short
segments or re-normalised junctions (upstream #958, #960, #987). After import
the original lock flags are restored, so input copper comes back bit-identical.

import: the session's (placement ...) section is dropped before KiCad reads
it, so a session can never move footprints. Zones are not refilled here; the
caller grades with a refill.
"""
import json
import re
import sys
from pathlib import Path


def block_span(text, start):
    """End index (exclusive) of the parenthesised block starting at `start`."""
    depth, i, in_str = 0, start, False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced s-expression")


def atoms(text):
    return re.findall(r'"(?:[^"])*"|[^\s()]+', text)


def unquote(a):
    return a[1:-1] if a.startswith('"') and a.endswith('"') else a


def split_classes(dsn, skip):
    """Move nets in `skip` into `<class>__skip` copies of their DSN class."""
    out, pos, ignored = [], 0, []
    for m in re.finditer(r"\(class\s", dsn):
        if m.start() < pos:
            continue
        end = block_span(dsn, m.start())
        block = dsn[m.start():end]
        first_sub = block.find("(", 1)
        head = block[:first_sub] if first_sub > 0 else block[:-1]
        body = block[first_sub:-1] if first_sub > 0 else ""
        names = atoms(head[len("(class"):])
        if not names:
            continue
        cls, nets = names[0], names[1:]
        keep = [n for n in nets if unquote(n) not in skip]
        drop = [n for n in nets if unquote(n) in skip]
        if not drop:
            continue
        skip_name = f'"{unquote(cls)}__skip"'
        new = f"(class {cls} {' '.join(keep)}\n      {body.strip()})" if keep else ""
        new += f"\n    (class {skip_name} {' '.join(drop)}\n      {body.strip()})"
        out.append(dsn[pos:m.start()])
        out.append(new.strip())
        pos = end
        ignored.append(unquote(skip_name))
    out.append(dsn[pos:])
    return "".join(out), ignored


def raise_default_clearance(dsn, floor_um):
    """Raise the structure rule and the kicad_default class clearance (never lower)."""
    changes = []

    def bump_rule(rule_text, where):
        def bump(m):
            if float(m.group(1)) < floor_um:
                changes.append({"where": where, "from_um": float(m.group(1)), "to_um": floor_um})
                return f"(clearance {floor_um:g})"
            return m.group(0)
        return re.sub(r"\(clearance\s+([0-9.]+)\s*\)", bump, rule_text)

    # board-level rule inside (structure ...)
    m = re.search(r"\(structure\b", dsn)
    if m:
        end = block_span(dsn, m.start())
        struct = dsn[m.start():end]
        r = re.search(r"\n\s*\(rule\b", struct)
        if r:
            rs = r.start() + struct[r.start():].index("(")
            re_ = block_span(struct, rs)
            struct = struct[:rs] + bump_rule(struct[rs:re_], "structure rule") + struct[re_:]
        dsn = dsn[:m.start()] + struct + dsn[end:]
    m = re.search(r"\(class\s+kicad_default\b", dsn)
    if m:
        end = block_span(dsn, m.start())
        dsn = dsn[:m.start()] + bump_rule(dsn[m.start():end], "class kicad_default") + dsn[end:]
    return dsn, changes


UNIT_MM = {"mm": 1.0, "mil": 0.0254, "in": 25.4, "um": 0.001, None: 1.0}
NC_TERM = re.compile(r"([AB])\.NetClass\s*(==|!=)\s*'([^']+)'")


def sexpr(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()"]+', re.sub(r"(?m)^\s*#.*$", "", text))
    stack, cur = [], []
    for t in tokens:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    return cur


def dru_class_clearances(text):
    """[(name, class_a, class_b|'*other'|'*all', clearance_mm)], [(name, reason)]"""
    done, skipped = [], []
    for rule in sexpr(text):
        if not (isinstance(rule, list) and rule and rule[0] == "rule"):
            continue
        name = rule[1] if len(rule) > 1 and isinstance(rule[1], str) else "?"
        parts = {r[0]: r for r in rule[2:] if isinstance(r, list) and r}
        cons = [r for r in rule[2:] if isinstance(r, list) and r and r[0] == "constraint"]
        extra = set(parts) - {"constraint", "condition", "severity"}
        if extra or len(cons) != 1 or cons[0][1] != "clearance":
            skipped.append((name, "only a single clearance constraint without layer clauses is translatable"))
            continue
        mins = [c for c in cons[0][2:] if isinstance(c, list) and c and c[0] == "min"]
        m = re.fullmatch(r"([0-9.]+)\s*(mm|mil|in|um)?", mins[0][1]) if mins else None
        if not m or len(cons[0]) != 3:
            skipped.append((name, "clearance without a plain min value"))
            continue
        mm = float(m.group(1)) * UNIT_MM[m.group(2)]
        cond = parts.get("condition", [None, ""])[1]
        terms = NC_TERM.findall(cond)
        residue = NC_TERM.sub("", cond).replace("&&", "").strip()
        if residue or not terms:
            skipped.append((name, f"condition {cond!r} is not purely net-class based"))
            continue
        eq = [(side, c) for side, op, c in terms if op == "=="]
        ne = [(side, c) for side, op, c in terms if op == "!="]
        if len(eq) == 2 and not ne and eq[0][0] != eq[1][0]:
            done.append((name, eq[0][1], eq[1][1], mm))
        elif len(eq) == 1 and len(ne) == 1 and ne[0][0] != eq[0][0] and ne[0][1] == eq[0][1]:
            done.append((name, eq[0][1], "*other", mm))
        elif len(eq) == 1 and not ne:
            done.append((name, eq[0][1], "*all", mm))
        else:
            skipped.append((name, f"condition {cond!r} is not a supported net-class pairing"))
    return done, skipped


def add_class_clearances(dsn, rules):
    """Append (class_class ...) rules to (network ...) for translated .kicad_dru rules."""
    classes = re.findall(r"\(class\s+(\"[^\"]*\"|\S+)", dsn)
    classes = [unquote(c) for c in classes]

    def dsn_names(kicad_class):  # Default is exported as kicad_default; __skip copies share rules
        base = "kicad_default" if kicad_class == "Default" else kicad_class
        return [c for c in classes if c == base or c == f"{base}__skip"]

    blocks, applied = [], []
    for name, a, b, mm in rules:
        first = dsn_names(a)
        if not first:
            continue
        if b == "*other":
            second = [c for c in classes if c not in first]
        elif b == "*all":
            second = classes
        else:
            second = dsn_names(b)
        um = mm * 1000
        for x in first:
            for y in second:
                blocks.append(f'    (class_class (classes "{x}" "{y}")\n      (rule (clearance {um:g})))')
        applied.append({"rule": name, "classes": [a, b], "clearance_mm": mm, "pairs": len(first) * len(second)})
    if not blocks:
        return dsn, applied
    m = re.search(r"\(network\b", dsn)
    end = block_span(dsn, m.start())
    return dsn[:end - 1] + "\n".join(blocks) + "\n  " + dsn[end - 1:], applied


def add_margin(dsn, margin_um):
    count = [0]

    def bump(m):
        count[0] += 1
        return f"(clearance {float(m.group(1)) + margin_um:g})"
    return re.sub(r"\(clearance\s+([0-9.]+)\s*\)", bump, dsn), count[0]


def drop_placement(ses):
    m = re.search(r"\(placement\b", ses)
    if not m:
        return ses, False
    end = block_span(ses, m.start())
    return ses[:m.start()] + ses[end:], True


def main(argv):
    import pcbnew

    def lock_existing(board):
        unlocked = [t for t in board.GetTracks() if not t.IsLocked()]
        for t in unlocked:
            t.SetLocked(True)
        return unlocked

    if len(argv) >= 3 and argv[0] == "export":
        board = pcbnew.LoadBoard(argv[1])
        temporarily_locked = len(lock_existing(board))
        out = Path(argv[2])
        if not pcbnew.ExportSpecctraDSN(board, str(out)):
            sys.exit("ExportSpecctraDSN failed")
        info = {"dsn": str(out), "ignored_classes": [], "clearance_raised": [],
                "existing_copper_locked_for_export": temporarily_locked}
        opts = dict(zip(argv[3::2], argv[4::2]))
        text = out.read_text()
        if "--skip-nets" in opts:
            text, info["ignored_classes"] = split_classes(text, set(json.loads(Path(opts["--skip-nets"]).read_text())))
        if "--dru" in opts:
            rules, skipped = dru_class_clearances(Path(opts["--dru"]).read_text())
            text, info["dru_translated"] = add_class_clearances(text, rules)
            info["dru_untranslated"] = [{"rule": n, "reason": r} for n, r in skipped]
        if "--default-clearance" in opts:
            text, info["clearance_raised"] = raise_default_clearance(text, float(opts["--default-clearance"]))
        if "--clearance-margin" in opts:
            text, n = add_margin(text, float(opts["--clearance-margin"]))
            info["clearance_margin"] = {"um": float(opts["--clearance-margin"]), "rules": n}
        out.write_text(text)
        print("BRIDGE_JSON: " + json.dumps(info))
        return 0
    if len(argv) == 4 and argv[0] == "import":
        board = pcbnew.LoadBoard(argv[1])
        ses_path = Path(argv[2])
        text, dropped = drop_placement(ses_path.read_text())
        clean = ses_path.with_suffix(".noplacement.ses")
        clean.write_text(text)
        unlocked = {t.m_Uuid.AsString() for t in lock_existing(board)}
        if not pcbnew.ImportSpecctraSES(board, str(clean)):
            sys.exit("ImportSpecctraSES failed")
        restored = 0
        for t in board.GetTracks():
            if t.m_Uuid.AsString() in unlocked:
                t.SetLocked(False)
                restored += 1
        board.Save(argv[3])
        print("BRIDGE_JSON: " + json.dumps({"placement_dropped": dropped, "session": str(clean),
                                            "existing_copper_locked": len(unlocked),
                                            "lock_flags_restored": restored}))
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
