# Read-only baseline

Check status is about whether each native tool ran to completion; design
findings are listed separately and are baseline facts, not setup failures.

| Run | Source | Overall | ERC | DRC | Netlist | Export | Analyze |
|---|---|---|---|---|---|---|---|
| [fome-mc](fome-mc/SUMMARY.md) | git revision HEAD (36db604471e65ccab12c2572aad6d8b458ad31fc) | PASS | PASS | PASS | PASS | PASS | PASS |
| [universal-112](universal-112/SUMMARY.md) | git revision HEAD (ddcf0f77fecf3ea7f093954ce1becb7c4a26e970) | PASS | PASS | PASS | PASS | PASS | PASS |
| [fome-mc-worktree](fome-mc-worktree/SUMMARY.md) | working tree @ 36db604471 + 45 uncommitted | PASS | PASS | PASS | PASS | PASS | PASS |

Working-tree runs are published without analyzer JSON and PDFs; the full run
stays under `build/runs/project/<label>/`. Re-run with `make baseline`.
*(Note: The `36db604471` snapshot above preserves the historical pre-`FOMEMC-1..27` baseline before routing and schematic/PCB remediation; for the current `HEAD` release verification see `docs/VALIDATION.md`, `reports/toolchain/fab-manifest.json`, and `reports/toolchain/bom-cpl-parity.json`.)*
