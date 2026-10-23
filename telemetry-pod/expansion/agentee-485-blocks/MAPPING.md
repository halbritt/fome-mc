# A2 all-source disposition ledger

211 cross-face rows plus three RF records. Each original source record is retained in coverage-ledger.json. UNRESOLVED rows are required unknowns in the consumer contract, never acceptance by omission.

| Relationship | Disposition | State | Exact supported role bindings | Required gap |
|---|---|---|---|---|
| U5.2-C3-hot-loop-input | EXPLICITLY_SUPERSEDE | REPRESENTED | u5-input-hf-C3/supply: U5.2 → C3.1; u5-input-hf-C3/return: U5.1 → C3.2 | — |
| U5.2-C1-bulk-input | EXPLICITLY_SUPERSEDE | REPRESENTED | u5-input-bulk-C1/supply: U5.2 → C1.1; u5-input-bulk-C1/return: U5.1 → C1.2 | — |
| U5.2-C2-bulk-input | EXPLICITLY_SUPERSEDE | REPRESENTED | u5-input-bulk-C2/supply: U5.2 → C2.1; u5-input-bulk-C2/return: U5.1 → C2.2 | — |
| U5.6-C4-vcc-bias | EXPLICITLY_SUPERSEDE | REPRESENTED | u5-vcc-C4/supply: U5.6 → C4.1; u5-vcc-C4/return: U5.1 → C4.2 | — |
| U7.2-C10-hot-loop-input | EXPLICITLY_SUPERSEDE | REPRESENTED | u7-input-hf-C10/supply: U7.2 → C10.1; u7-input-hf-C10/return: U7.1 → C10.2 | — |
| U7.2-C8-bulk-input | EXPLICITLY_SUPERSEDE | REPRESENTED | u7-input-bulk-C8/supply: U7.2 → C8.1; u7-input-bulk-C8/return: U7.1 → C8.2 | — |
| U7.2-C9-bulk-input | EXPLICITLY_SUPERSEDE | REPRESENTED | u7-input-bulk-C9/supply: U7.2 → C9.1; u7-input-bulk-C9/return: U7.1 → C9.2 | — |
| U7.6-C11-vcc-bias | EXPLICITLY_SUPERSEDE | REPRESENTED | u7-vcc-C11/supply: U7.6 → C11.1; u7-vcc-C11/return: U7.1 → C11.2 | — |
| U6.8-C16-ldo-cap | EXPLICITLY_SUPERSEDE | REPRESENTED | U6.8-C16-ldo-cap/supply: U6.8 → C16.1; U6.8-C16-ldo-cap/return: U6.6 → C16.2 | — |
| U6.1-C17-ldo-cap | EXPLICITLY_SUPERSEDE | REPRESENTED | U6.1-C17-ldo-cap/supply: U6.1 → C17.1; U6.1-C17-ldo-cap/return: U6.3 → C17.2 | — |
| U12.8-C20-ldo-cap | EXPLICITLY_SUPERSEDE | REPRESENTED | U12.8-C20-ldo-cap/supply: U12.8 → C20.1; U12.8-C20-ldo-cap/return: U12.6 → C20.2 | — |
| U12.1-C19-ldo-cap | EXPLICITLY_SUPERSEDE | REPRESENTED | U12.1-C19-ldo-cap/supply: U12.1 → C19.1; U12.1-C19-ldo-cap/return: U12.3 → C19.2 | — |
| U1.2-C46-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U1.2-C46-hf-decoupler/supply: U1.2 → C46.1; U1.2-C46-hf-decoupler/return: U1.1 → C46.2 | — |
| U1.2-C50-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U1.2-C50-hf-decoupler/supply: U1.2 → C50.1; U1.2-C50-hf-decoupler/return: U1.1 → C50.2 | — |
| U1.2-C45-bulk-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.2-C48-secondary-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.2-C49-secondary-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.2-C51-secondary-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.2-C52-secondary-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.2-C53-secondary-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U100.3-C100-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U100.3-C100-hf-decoupler/supply: U100.3 → C100.1; U100.3-C100-hf-decoupler/return: U100.2 → C100.2 | — |
| U13.4-C62-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U13.4-C62-hf-decoupler/supply: U13.4 → C62.1; U13.4-C62-hf-decoupler/return: U13.11 → C62.2 | — |
| U16.4-C72-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U16.4-C72-hf-decoupler/supply: U16.4 → C72.1; U16.4-C72-hf-decoupler/return: U16.2 → C72.2 | — |
| U18.4-C76-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U18.4-C76-hf-decoupler/supply: U18.4 → C76.1; U18.4-C76-hf-decoupler/return: U18.2 → C76.2 | — |
| U19.4-C78-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U19.4-C78-hf-decoupler/supply: U19.4 → C78.1; U19.4-C78-hf-decoupler/return: U19.2 → C78.2 | — |
| U20.14-C79-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U20.14-C79-hf-decoupler/supply: U20.14 → C79.1; U20.14-C79-hf-decoupler/return: U20.7 → C79.2 | — |
| U20.14-C80-secondary-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U21.3-C83-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U21.3-C83-hf-decoupler/supply: U21.3 → C83.1; U21.3-C83-hf-decoupler/return: U21.2 → C83.2 | — |
| U21.5-C84-hf-decoupler | CARRY_FORWARD | REPRESENTED | U21.5-C84-hf-decoupler/supply: U21.5 → C84.1; U21.5-C84-hf-decoupler/return: U21.3 → C84.2 | — |
| U22.5-C85-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U22.5-C85-hf-decoupler/supply: U22.5 → C85.1; U22.5-C85-hf-decoupler/return: U22.3 → C85.2 | — |
| U23.1-C86-hotswap-input | EXPLICITLY_SUPERSEDE | REPRESENTED | U23.1-C86-hotswap-input/supply: U23.1 → C86.1; U23.1-C86-hotswap-input/return: U23.6 → C86.2 | — |
| U24.1-C89-hotswap-input | EXPLICITLY_SUPERSEDE | REPRESENTED | U24.1-C89-hotswap-input/supply: U24.1 → C89.1; U24.1-C89-hotswap-input/return: U24.6 → C89.2 | — |
| U25.1-C92-hotswap-input | EXPLICITLY_SUPERSEDE | REPRESENTED | U25.1-C92-hotswap-input/supply: U25.1 → C92.1; U25.1-C92-hotswap-input/return: U25.6 → C92.2 | — |
| U30.1-C124-hotswap-input | EXPLICITLY_SUPERSEDE | REPRESENTED | U30.1-C124-hotswap-input/supply: U30.1 → C124.1; U30.1-C124-hotswap-input/return: U30.6 → C124.2 | — |
| U26.8-C97-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | u26-bypass-C97/supply: U26.8 → C97.1; u26-bypass-C97/return: U26.4 → C97.2 | — |
| U26.8-C98-secondary-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | u26-bypass-C98/supply: U26.8 → C98.1; u26-bypass-C98/return: U26.4 → C98.2 | — |
| U27.12-C118-hf-decoupler | EXPLICITLY_SUPERSEDE | UNRESOLVED | U27.12-C118-hf-decoupler/supply: U27.12 → C118.1; U27.12-C118-hf-decoupler/return: U27.5 → C118.2 | G2_NO_VIA_EVIDENCE |
| U27.13-C119-hf-decoupler | EXPLICITLY_SUPERSEDE | UNRESOLVED | U27.13-C119-hf-decoupler/supply: U27.13 → C119.1; U27.13-C119-hf-decoupler/return: U27.4 → C119.2 | G2_NO_VIA_EVIDENCE |
| U28.12-C120-hf-decoupler | EXPLICITLY_SUPERSEDE | UNRESOLVED | U28.12-C120-hf-decoupler/supply: U28.12 → C120.1; U28.12-C120-hf-decoupler/return: U28.5 → C120.2 | G2_NO_VIA_EVIDENCE |
| U28.13-C121-hf-decoupler | EXPLICITLY_SUPERSEDE | UNRESOLVED | U28.13-C121-hf-decoupler/supply: U28.13 → C121.1; U28.13-C121-hf-decoupler/return: U28.4 → C121.2 | G2_NO_VIA_EVIDENCE |
| U29.12-C122-hf-decoupler | EXPLICITLY_SUPERSEDE | UNRESOLVED | U29.12-C122-hf-decoupler/supply: U29.12 → C122.1; U29.12-C122-hf-decoupler/return: U29.5 → C122.2 | G2_NO_VIA_EVIDENCE |
| U29.13-C123-hf-decoupler | EXPLICITLY_SUPERSEDE | UNRESOLVED | U29.13-C123-hf-decoupler/supply: U29.13 → C123.1; U29.13-C123-hf-decoupler/return: U29.4 → C123.2 | G2_NO_VIA_EVIDENCE |
| J3.4-C64-bulk-decoupler | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| J3.4-C65-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | J3.4-C65-hf-decoupler/supply: J3.4 → C65.1; J3.4-C65-hf-decoupler/return: J3.6 → C65.2 | — |
| U2.8-C38-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U2.8-C38-hf-decoupler/supply: U2.8 → C38.1; U2.8-C38-hf-decoupler/return: U2.7 → C38.2 | — |
| U2.5-C41-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U2.5-C41-hf-decoupler/supply: U2.5 → C41.1; U2.5-C41-hf-decoupler/return: U2.6 → C41.2 | — |
| U3.23-C44-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U3.23-C44-hf-decoupler/supply: U3.23 → C44.1; U3.23-C44-hf-decoupler/return: U3.24 → C44.2 | — |
| U3.22-C44-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U3.22-C44-hf-decoupler/supply: U3.22 → C44.1; U3.22-C44-hf-decoupler/return: U3.24 → C44.2 | — |
| U10.1-C43-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U10.1-C43-hf-decoupler/supply: U10.1 → C43.1; U10.1-C43-hf-decoupler/return: U10.2 → C43.2 | — |
| U11.2-C18-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U11.2-C18-hf-decoupler/supply: U11.2 → C18.1; U11.2-C18-hf-decoupler/return: U11.4 → C18.2 | — |
| U4.16-C130-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U4.16-C130-hf-decoupler/supply: U4.16 → C130.1; U4.16-C130-hf-decoupler/return: U4.14 → C130.2 | — |
| U8.4-C131-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U8.4-C131-hf-decoupler/supply: U8.4 → C131.1; U8.4-C131-hf-decoupler/return: U8.11 → C131.2 | — |
| U9.5-C132-hf-decoupler | EXPLICITLY_SUPERSEDE | REPRESENTED | U9.5-C132-hf-decoupler/supply: U9.5 → C132.1; U9.5-C132-hf-decoupler/return: U9.2 → C132.2 | — |
| U100.5-C133-hf-decoupler | CARRY_FORWARD | REPRESENTED | U100.5-C133-hf-decoupler/supply: U100.5 → C133.1; U100.5-C133-hf-decoupler/return: U100.3 → C133.2 | — |
| U6.1-R6-output-load | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| L1.2-C6-regulator-output | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| L1.2-C7-regulator-output | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| L2.2-C13-regulator-output | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| L2.2-C14-regulator-output | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| L2.2-C15-regulator-output | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| Q1.1-D2-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| Q1.1-R1-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.3-C47-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.3-R29-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.16-R33-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U1.27-R30-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U3.14-R24-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.1-C31-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.1-R12-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.2-C33-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.2-R15-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.3-C35-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.3-R18-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.4-C37-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.4-R21-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.5-C55-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.5-R36-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.6-C57-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.6-R39-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.7-C59-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.7-R42-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.8-C61-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.8-R45-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U4.15-C40-reference-cap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U5.5-R27-feedback | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U5.5-R3-feedback | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U5.7-C5-bootstrap | EXPLICITLY_SUPERSEDE | REPRESENTED | u5-boot-C5/supply: U5.7 → C5.1; u5-boot-C5/return: U5.8 → C5.2 | — |
| U5.8-L1-switch-inductor | EXPLICITLY_SUPERSEDE | REPRESENTED | u5-input-hf-C3/switch: U5.8 → L1.1 | — |
| U7.5-R28-feedback | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U7.5-R5-feedback | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U7.7-C12-bootstrap | EXPLICITLY_SUPERSEDE | REPRESENTED | u7-boot-C12/supply: U7.7 → C12.1; u7-boot-C12/return: U7.8 → C12.2 | — |
| U7.8-L2-switch-inductor | EXPLICITLY_SUPERSEDE | REPRESENTED | u7-input-hf-C10/switch: U7.8 → L2.1 | — |
| U8.3-C30-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.3-R10-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.3-R11-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.5-C32-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.5-R13-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.5-R14-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.10-C34-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.10-R16-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.10-R17-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.12-C36-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.12-R19-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U8.12-R20-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U9.3-C39-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U9.3-R22-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U9.3-R23-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U10.3-R24-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U11.5-C21-reference-cap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.3-C54-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.3-R34-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.3-R35-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.5-C56-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.5-R37-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.5-R38-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.10-C58-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.10-R40-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.10-R41-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.12-C60-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.12-R43-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U13.12-R44-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U16.1-R56-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U16.1-R57-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U16.5-C71-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U18.1-R181-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U18.1-R61-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U18.5-C75-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U19.1-R62-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U19.1-R63-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U19.5-C77-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U20.1-R69-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U20.5-C82-crystal-load | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U20.5-Y1-crystal | CARRY_FORWARD | UNRESOLVED | paired:U20.5-Y1-crystal\|U20.6-Y1-crystal/supply: U20.5 → Y1.3 | G2_NO_VIA_EVIDENCE |
| U20.6-C81-crystal-load | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U20.6-Y1-crystal | CARRY_FORWARD | UNRESOLVED | paired:U20.5-Y1-crystal\|U20.6-Y1-crystal/return: U20.6 → Y1.1 | G2_NO_VIA_EVIDENCE |
| U20.9-R68-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U21.6-D101-esd-connector | DEDUPLICATE | REPRESENTED | paired:J1.29-D101-esd-connector\|U21.6-D101-esd-connector/return: U21.6 → D101.2; paired:U21.6-D101-esd-connector\|U21.7-D101-esd-connector/supply: U21.6 → D101.2 | — |
| U21.7-D101-esd-connector | CARRY_FORWARD | REPRESENTED | paired:U21.6-D101-esd-connector\|U21.7-D101-esd-connector/return: U21.7 → D101.1 | — |
| U21.7-R70-termination | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U21.8-R71-strap | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U23.2-R73-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U23.2-R74-sense-network | CARRY_FORWARD | REPRESENTED | paired:U23.2-R74-sense-network\|U23.3-R74-sense-network/supply: U23.2 → R74.1 | — |
| U23.3-R74-sense-network | CARRY_FORWARD | REPRESENTED | paired:U23.2-R74-sense-network\|U23.3-R74-sense-network/return: U23.3 → R74.2 | — |
| U23.3-R75-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U23.7-R76-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U23.8-C88-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U24.2-R77-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U24.2-R78-sense-network | CARRY_FORWARD | REPRESENTED | paired:U24.2-R78-sense-network\|U24.3-R78-sense-network/supply: U24.2 → R78.1 | — |
| U24.3-R78-sense-network | CARRY_FORWARD | REPRESENTED | paired:U24.2-R78-sense-network\|U24.3-R78-sense-network/return: U24.3 → R78.2 | — |
| U24.3-R79-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U24.7-R80-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U24.8-C91-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U25.2-R81-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U25.2-R82-sense-network | CARRY_FORWARD | REPRESENTED | paired:U25.2-R82-sense-network\|U25.3-R82-sense-network/supply: U25.2 → R82.1 | — |
| U25.3-R82-sense-network | CARRY_FORWARD | REPRESENTED | paired:U25.2-R82-sense-network\|U25.3-R82-sense-network/return: U25.3 → R82.2 | — |
| U25.3-R83-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U25.7-R84-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U25.8-C94-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.2-C95-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.2-R112-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.2-R113-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.3-R114-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.3-R115-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.3-R116-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.5-R123-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.5-R124-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.5-R125-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.6-C96-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.6-R121-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U26.6-R122-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.7-C112-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.7-R138-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.7-R139-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.10-C111-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.10-R134-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.10-R135-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.11-C110-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.11-R130-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U27.11-R131-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.6-C129-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.6-R178-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.6-R179-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.7-C127-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.7-R168-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.7-R169-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.10-C114-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.10-R146-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U28.10-R147-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.7-C117-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.7-R158-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.7-R159-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.10-C116-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.10-R154-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.10-R155-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.11-C115-input-filter | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.11-R150-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U29.11-R151-series-input | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U30.2-R162-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U30.2-R163-sense-network | CARRY_FORWARD | REPRESENTED | paired:U30.2-R163-sense-network\|U30.3-R163-sense-network/supply: U30.2 → R163.1 | — |
| U30.3-R163-sense-network | CARRY_FORWARD | REPRESENTED | paired:U30.2-R163-sense-network\|U30.3-R163-sense-network/return: U30.3 → R163.2 | — |
| U30.3-R164-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U30.7-R165-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U30.8-C126-sense-network | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U100.6-D100-esd-connector | DEDUPLICATE | REPRESENTED | paired:J1.1-D100-esd-connector\|U100.6-D100-esd-connector/return: U100.6 → D100.1; paired:U100.6-D100-esd-connector\|U100.7-D100-esd-connector/supply: U100.6 → D100.1 | — |
| U100.6-R100-termination | CARRY_FORWARD | REPRESENTED | paired:U100.6-R100-termination\|U100.7-R100-termination/supply: U100.6 → R100.2 | — |
| U100.7-D100-esd-connector | CARRY_FORWARD | REPRESENTED | paired:U100.6-D100-esd-connector\|U100.7-D100-esd-connector/return: U100.7 → D100.2 | — |
| U100.7-R100-termination | CARRY_FORWARD | REPRESENTED | paired:U100.6-R100-termination\|U100.7-R100-termination/return: U100.7 → R100.1 | — |
| J1.3-D1-esd-connector | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| J1.1-D100-esd-connector | CARRY_FORWARD | REPRESENTED | paired:J1.1-D100-esd-connector\|U100.6-D100-esd-connector/supply: J1.1 → D100.2 | — |
| J1.29-D101-esd-connector | CARRY_FORWARD | REPRESENTED | paired:J1.29-D101-esd-connector\|U21.6-D101-esd-connector/supply: J1.29 → D101.1 | — |
| J1.24-D104-esd-connector | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G1_SINGLE_LEG_SCHEMA |
| U3.11-L3-rf-line | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G3_RF_CORRIDOR_AND_IMPEDANCE |
| U3.11-D3-rf-line | CARRY_FORWARD | UNRESOLVED | No invented return; source retained as required unknown | G3_RF_CORRIDOR_AND_IMPEDANCE |
| J2.1-none-rf-line | EXPLICITLY_SUPERSEDE | UNRESOLVED | No invented return; source retained as required unknown | G3_RF_CORRIDOR_AND_IMPEDANCE |
