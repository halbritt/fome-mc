# Independent storage power review

No wiring defect found in the final native candidate: 574 power/delta checks pass,
including replay of the previous independently transcribed 324-check storage
contract. Four deliberate XML regressions were detected on temporary copies.

Run the portable checker with four positional arguments:

```sh
python3 independent-review/check_power_independent.py CURRENT.xml PREVIOUS-STORAGE.xml PREVIOUS-ADC.xml REPORT.json
```

Keep `storage_contract.py` beside the checker. The checker finds the actual
inductor footprint at `../inputs/footprints/PodStoragePower.pretty/SRP4020TA.kicad_mod`
relative to its directory. Scratch preparation also supports `../storage-power-inputs`.
It does not require the original absolute workspace paths. Temporary normalized
XML is deleted; it restores only the separately checked power delta so the full
original storage contract can be replayed. The outer report binds the real
current/previous inputs and both checker hashes.

The final ERC observation and flag registration are recorded separately in
`flag-and-erc-review.json`. PWR_FLAG is on an output with a real U15 SW -> L4 ->
VCC path; it does not qualify converter performance. Final ERC retains the
existing J1 missing-footprint warning only. Supervision, early power failure,
hold-up, exact passive bindings, thermal, SI and assembly remain open.

The Bourns copper dimensions match its recommended land pattern. Its courtyard
covers the maximum body and copper with at least 0.25 mm clearance; that remains
a candidate assembly courtyard, not fabricator approval.
