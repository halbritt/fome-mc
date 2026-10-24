# AGENTEE-485 J2c diagnostic: PARTIAL

The ONE diagnostic ended with 27 accepted stages, one refused stage and C1
REQUIRED_NOT_RUN; pipeline/outer exit 3. `STAGES.md` lists the actual names from
`pipeline.json.stages`. No production candidate, receipt or placement is accepted.

The emission stage saved the full schematic and annotated board, then refused
because its access-materializer child raised `ModuleNotFoundError: No module
named 'agent_ee'`. It did not produce the required 44-row reservations file. The
failure is preserved, not repaired or retried. No second emission ran.

The saved board hash is
`fec5170a497bfad0d56be7e12c8d2597fe4541a0ed2c1bb60c3980933a6704c9`.
`j2-verification/native-checks.json` is explicitly PARTIAL: independent checks
completed before the strict verifier refused the absent access evidence. It
records the complete J2 UUID, electrical membership, stock pad/drill/layer parity,
front (80,28) pose, source-to-native RF mappings and every prohibition, source
component/ref/pad/net identities, and native BOM/CPL consumer results.

The source has 314 intent components, including five symbol-only power flags.
All 309 electrical footprints and four envelope-defined board-only mounting
holes are accounted for: 313 native footprints, with no numerical substitution
or inventory waiver. All 1,059 electrical-footprint pads are enumerated. The
source has 182 nets and 53 no-connect declarations; 886 connected terminals were
checked. BOM/CPL evidence has 93 grouped BOM rows and 296 CPL rows. J1 and J2
remain populated and carry `JLCPCB_Assembly=not_assembled`; the full native
identity comparison retains 80 LCSC identities and external Amphenol 132134.

Native tool execution passed using the repository ERC/DRC adapters on an isolated
snapshot. ERC: one sheet, zero violations. DRC: 15 violations, 499 unconnected
items, zero schematic-parity errors. The violations are one L1/L2 courtyard
overlap, 12 text-height/thickness warnings and two J1/J3 library-footprint
warnings. Nothing is waived. The text limits are existing KiCad project settings
without a cited manufacturer source in the captured fab profile: class: default,
advisory; they are not new acceptance gates. This is an unrouted diagnostic,
with no physical access, functional placement, return-path or manufacturing
acceptance.

The full native candidate is under `pipe/emission/design`; the frozen source
capture is under `cap`. `native/` holds native reports and source hashes.
Receipt JSONs under `receipt-metadata/` are metadata only, not accepted receipts.
No runtime observation/receipt write followed the refusing pipeline.

## Source boundary

The emission archive is exactly fome-mc `3db711151c1c98edbe598f72f9a77d116eaf9f32`.
The remaining prefix-only UUID guard in pipeline.py was discovered after that
archive began running. The delivered caller uses the same complete-UUID helper
as the verifier; the frozen run was not edited. The final candidate independently
passes that complete-UUID check, including the prior same-prefix negative control.
This final caller change was not exercised by another full emission.

The verifier was subsequently corrected to account for the envelope's four
board-only mounting holes and to retain successful independent checks before
refusing missing access evidence. The first inventory refusal and the subsequent
strict missing-access refusal are both retained. These are verifier-contract
corrections on the same unchanged saved bytes, not new emissions.

## Validation

Commands ran from the assigned worktree on proximal; all tests/native gates used
admission. `validation/ee485.mk` and the retained drivers contain exact recipes.
Logs preserve failures as well as final outcomes.

- Bootstrap: wrapper exit 0, `fome-bootstrap: OK`; only the permitted host apt
  patch drift. Container doctor: PASS, 54 checks, zero required failures.
- `fome-gate.sh "$WT" ... doctor check MAKEFILES=build/ee485.mk`: all five ECU
  steps PASS, exit 0. `ecu-before-after.json` proves identical before/after gate
  results and 94 byte-unchanged snapshot source files.
- Six retention tests; eight native UUID/RF tests; 19 launch-preflight tests:
  final logs end OK / exit 0. Five saved-inventory negative controls: OK / exit 0.
- Retention check: 428 retained files, 576 design inputs, eight installed files,
  4,336 prepared files. Exact materialization: 4,336 files and 108 empty dirs.
  The separate immutable repair store has 570 blobs plus index/checksums.
- Merged F8 `SHA256SUMS`: every entry OK, exit 0. Main's F8 manifest and correction
  record, historical retention and historical J2 import remain byte unchanged.
- Final `build.py /work/export --check`: byte-for-byte reproduction, exit 0.
- ONE emission: test/1, three CPUs, 12 GiB, 1,800-second cap, jobs 1; selected
  runtime `agentee-485j2c.json`, exact mounted agent-ee 00d3243a, C1 held.
- `python3 verify_j2.py <run>`: strict refusal, Python exit 1 / make exit 2,
  missing `pipe/access-rebound/reservations.json`; successful native checks are
  explicitly partial. Native ERC/DRC and position-export tools exit 0.

No routing/campaign launch, receipt acceptance, rule relaxation, purchase, vendor
upload, tracker/main change or additional agent was performed. Hosted CI is
NOT EVIDENCE (not observed, not required). Model route: Sol (Codex), HIGH as
dispatched; exact runtime model identifier is not exposed by the harness.

The first seal's overbroad whitespace check inspected captured PDF bytes and
reported trailing whitespace. Those bytes remain unchanged. The final whitespace
check excludes the hash-bound `cap/`, emitted `design/` and raw `logs/` trees;
`SHA256SUMS` still verifies every retained file. Human-authored code and notes
remain covered by whitespace checks.
