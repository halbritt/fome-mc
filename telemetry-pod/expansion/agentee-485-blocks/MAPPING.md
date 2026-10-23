# Effective role mapping

All bounds remain the effective ADVISORY values. Historical source IDs establish conceptual intent only. Exact historical endpoint selectors and primary citations appear in the JSON ledgers.

| Effective obligation | Role | Effective endpoints (ref.pin) | Historical relationship | Historical endpoint selector | Template | Difference |
|---|---|---|---|---|---|---|
| u5-input-hf-C3 | supply | U5.2 → C3.1 | U5.2-C3-hot-loop-input | {U5.2} → {C3.1} | same-face-only | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-input-hf-C3 | return | U5.1 → C3.2 | U5.2-C3-hot-loop-input | {U5.1, U5.9} → {C3.2} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-input-hf-C3 | switch | U5.8 → L1.1 | U5.8-L1-switch-inductor | {U5.8} → {L1.1} | same-face-only | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-input-bulk-C1 | supply | U5.3 → C1.1 | U5.2-C1-bulk-input | {U5.2} → {C1.1} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-input-bulk-C1 | return | U5.1 → C1.2 | U5.2-C1-bulk-input | {U5.1, U5.9} → {C1.2} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-input-bulk-C2 | supply | U5.3 → C2.1 | U5.2-C2-bulk-input | {U5.2} → {C2.1} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-input-bulk-C2 | return | U5.1 → C2.2 | U5.2-C2-bulk-input | {U5.1, U5.9} → {C2.2} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-vcc-C4 | supply | U5.6 → C4.1 | U5.6-C4-vcc-bias | {U5.6} → {C4.1} | decoupler-under-device | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-vcc-C4 | return | U5.1 → C4.2 | U5.6-C4-vcc-bias | {U5.1, U5.9} → {C4.2} | decoupler-under-device | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u5-boot-C5 | supply | U5.7 → C5.1 | U5.7-C5-bootstrap | {U5.7} → {C5.1} | same-face-only | same endpoints and bound |
| u5-boot-C5 | return | U5.8 → C5.2 | U5.7-C5-bootstrap | {U5.1, U5.9} → {} | same-face-only | Historical generic GND selector has no return pair; effective explicit SW return retained. |
| u7-input-hf-C10 | supply | U7.2 → C10.1 | U7.2-C10-hot-loop-input | {U7.2} → {C10.1} | same-face-only | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-input-hf-C10 | return | U7.1 → C10.2 | U7.2-C10-hot-loop-input | {U7.1, U7.9} → {C10.2} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-input-hf-C10 | switch | U7.8 → L2.1 | U7.8-L2-switch-inductor | {U7.8} → {L2.1} | same-face-only | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-input-bulk-C8 | supply | U7.3 → C8.1 | U7.2-C8-bulk-input | {U7.2} → {C8.1} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-input-bulk-C8 | return | U7.1 → C8.2 | U7.2-C8-bulk-input | {U7.1, U7.9} → {C8.2} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-input-bulk-C9 | supply | U7.3 → C9.1 | U7.2-C9-bulk-input | {U7.2} → {C9.1} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-input-bulk-C9 | return | U7.1 → C9.2 | U7.2-C9-bulk-input | {U7.1, U7.9} → {C9.2} | same-face-only | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-vcc-C11 | supply | U7.6 → C11.1 | U7.6-C11-vcc-bias | {U7.6} → {C11.1} | decoupler-under-device | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-vcc-C11 | return | U7.1 → C11.2 | U7.6-C11-vcc-bias | {U7.1, U7.9} → {C11.2} | decoupler-under-device | Endpoint/selector difference, not an ID rename. Preserve effective endpoints.; Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u7-boot-C12 | supply | U7.7 → C12.1 | U7.7-C12-bootstrap | {U7.7} → {C12.1} | same-face-only | same endpoints and bound |
| u7-boot-C12 | return | U7.8 → C12.2 | U7.7-C12-bootstrap | {U7.1, U7.9} → {} | same-face-only | Historical generic GND selector has no return pair; effective explicit SW return retained. |
| u26-bypass-C97 | supply | U26.8 → C97.1 | U26.8-C97-hf-decoupler | {U26.8} → {C97.1} | decoupler-under-device | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u26-bypass-C97 | return | U26.4 → C97.2 | U26.8-C97-hf-decoupler | {U26.4} → {C97.2} | decoupler-under-device | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u26-bypass-C98 | supply | U26.8 → C98.1 | U26.8-C98-secondary-decoupler | {U26.8} → {C98.1} | decoupler-under-device | Numeric bounds differ; preserve effective ADVISORY value and citation. |
| u26-bypass-C98 | return | U26.4 → C98.2 | U26.8-C98-secondary-decoupler | absent | decoupler-under-device | No corresponding historical leg/bound; current effective leg retained. |
