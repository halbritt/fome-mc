# Read-only baseline

Check status is about whether each native tool ran to completion; design
findings are listed separately and are baseline facts, not setup failures.

| Run | Source | Overall | ERC | DRC | Netlist | Export | Analyze |
|---|---|---|---|---|---|---|---|
| [fome-mc](fome-mc/SUMMARY.md) | git revision HEAD (c43ad7bafc9a8e3be337f1342ae0cb259918882a) | PASS | PASS | PASS | PASS | PASS | PASS |
| [universal-112](universal-112/SUMMARY.md) | git revision HEAD (ddcf0f77fecf3ea7f093954ce1becb7c4a26e970) | PASS | PASS | PASS | PASS | PASS | PASS |
| [fome-mc-worktree](fome-mc-worktree/SUMMARY.md) | working tree @ c43ad7bafc + 12 uncommitted | FAIL | PASS | PASS | PASS | FAIL | PASS |

Working-tree runs are published without analyzer JSON and PDFs; the full run
stays under `build/runs/project/<label>/`. Re-run with `make baseline`.
