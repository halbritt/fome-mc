# Independent supervisor candidate review

Run with Python 3:

```sh
python3 check_supervisor_independent.py CURRENT_XML PRIOR_POWER_XML PRIOR_STORAGE_XML PRIOR_ADC_XML INPUTS REPORT_JSON
```

Keep `check_power_independent.py` and `storage_contract.py` beside this checker. INPUTS contains both PodSupervisor and retained PodStoragePower footprint directories. The prior power native input is pinned by its report hash (parent source commit cfd6f18). All native input and dependency hashes are in report.json.

Result: 655 supervisor graph/component/footprint checks passed. The normalized historical predecessor replay passed 574 power checks and its 324 storage checks. Nested predecessor reports describe that historical graph, with the independently verified supervisor delta removed; their statement that no supervisor was added is historical, not a description of this candidate.

Both requested mutations were detected: U17.6 moved from MCU_EN to GND, and C31.1 moved from ADC_AIN0 to GND. See negative-probes.json. These modified only temporary XML copies.

Native ERC contains one existing missing ampseal-35 footprint warning and no errors. Gerber aperture dimensions and centers independently match the authored copper, mask and paste candidate; see gerber-review.json. TI drawing interpretation remains unresolved for final land qualification. Left pads have nominal 0.05 mm mask overlap, right pads 0.05 mm mask expansion. Manufacturing registration tolerances still need acceptance.

See calculations.json for 16.9 kohm main threshold corner arithmetic. Initial resistor tolerance and conservative sense leakage are included; TCR, transients, effective capacitance, exact passive binding, startup behavior, fault firmware, power-loss durability and physical qualification remain open. No measured hardware acceptance is claimed.
