"""Run agent-ee's access_direction judge on a COPY of a board with the declared J3 property.

Read-only on the input board and on the agent-ee checkout:
  PYTHONDONTWRITEBYTECODE=1 python3 check.py --agent-ee /path/to/agent-ee --board B.kicad_pcb --out DIR
"""
import argparse, hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent


def inject(text, ref, value):
    """Add the agent_ee_access_direction field to footprint `ref` in board text (copy only)."""
    for m in re.finditer(r'\n\t\(footprint "[^"]*"', text):
        end = text.find('\n\t(footprint "', m.end())
        block = text[m.start():end if end > 0 else len(text)]
        if f'(property "Reference" "{ref}"' not in block:
            continue
        side = 'B' if '(layer "B.Cu")' in block[:200] else 'F'
        field = ('\n\t\t(property "agent_ee_access_direction" %s\n\t\t\t(at 0 0 0)\n\t\t\t(layer "%s.Fab")\n\t\t\t(hide yes)\n'
                 '\t\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t\t)' % (json.dumps(json.dumps(value[side], separators=(',', ':'))), side))
        anchor = block.index('\n\t\t(property "Reference"')
        return side, text[:m.start() + anchor] + field + text[m.start() + anchor:]
    raise SystemExit(f'{ref} not found')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agent-ee', required=True)
    ap.add_argument('--board', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--declarations', default=str(HERE / 'declarations.json'))
    a = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(pathlib.Path(a.agent_ee) / 'src'))
    from agent_ee import placement, placement_probe
    board = pathlib.Path(a.board)
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    decl = json.loads(pathlib.Path(a.declarations).read_text())['parts']['J3']
    before = hashlib.sha256(board.read_bytes()).hexdigest()
    side, text = inject(board.read_text(), 'J3', {'F': decl['F_side'], 'B': decl['B_side']})
    copy = out / 'candidate-with-J3-access.kicad_pcb'
    copy.write_text(text)
    capture = placement_probe.extract(str(copy))
    judgment = placement.judge(capture)
    (out / 'placement-judgment.json').write_text(json.dumps(judgment, indent=1))
    rows = judgment.get('access_directions', [])
    summary = {'input_board_sha256': before, 'copy_sha256': hashlib.sha256(copy.read_bytes()).hexdigest(),
               'input_unchanged': hashlib.sha256(board.read_bytes()).hexdigest() == before,
               'j3_side': side, 'verdict': judgment['verdict'],
               'access_rows': [{k: r.get(k) for k in ('ref', 'status', 'reason', 'inboard_area_mm2', 'mouth_nm', 'vector', 'relaxes_outline')} for r in rows],
               'hard_failure_kinds': sorted({f['kind'] for f in judgment['hard_failures']}),
               'hard_failures_by_ref': {f['ref']: f['kind'] for f in judgment['hard_failures'] if 'ref' in f},
               'unknown': [u.get('ref') for u in judgment['unknown']]}
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


main()
