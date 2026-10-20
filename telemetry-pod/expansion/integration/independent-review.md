# Independent integration preparation review

PASS within prepared-source scope. Ran integration/verify.py successfully and separately generated inputs under integration-independent-inputs in this scratch directory. Independently compared those generated inputs with the auxiliary-power baseline without importing producer helpers.313 components and183 nets remain. Only connector/J1.value and connector/J1.footprint change:776163-1→1-776163-1 and ampseal:ampseal-35→PodConnector:AMPSEAL_35_1-776163-1. Every other top-level intent field is equal; all66 other baseline files are byte-identical. The only additions are the connector footprint, STEP and integration receipt. The retained verifier also confirms byte-for-byte regeneration and rejects overwriting an existing capture.

Independently compared the added footprint digest with our previously retained candidate-source-hashes.json and the STEP with our independently examined source digest43ba1f805451c97c81c3e659339e78a5ce25a0cbaeeb0427e809513e38daa473. Both match. The source generator verifies the reviewed footprint pin and all connector source hashes before copying. No authored symbol metadata is stripped and no old captures are rewritten to evade emitter limitations.

The gold header is explicit in the component value and integration README. K1 sheet1 distinguishes black gold1-776163-1 from black tin776163-1; selecting the former is not merely a formatting change to an equivalent BOM identifier. No J1 part/assembly binding is present, and none is invented here. The exact header procurement binding, compatible gold-contact harness terminals, housing, wire/current envelope and mating assembly remain open. A later BOM matcher must not normalize away the leading1- or reuse an old tin-header binding. The integration README accurately discloses that unfinished work. Any downstream requirement/BOM still naming776163-1 must be reconciled during adoption.

The future native project must preserve this layout beneath its project root:

- inputs/footprints/PodConnector.pretty/AMPSEAL_35_1-776163-1.kicad_mod
- inputs/models/c-1-776163-1-t-3d.stp

A project-local fp-lib-table must bind nicknamePodConnector to `${KIPRJMOD}/inputs/footprints/PodConnector.pretty`. The footprint model reference `${KIPRJMOD}/inputs/models/c-1-776163-1-t-3d.stp` then resolves correctly. This preparation output itself has no native project or completed library table, so path existence in the capture is not yet evidence of resolution in an emitted project. The README correctly makes table creation and subsequent native verification an adoption step. Moving captures to a different directory requires updating the table/model paths together.

No actionable defect found in the requested preparation delta. Fresh native emission, correct library/model resolution, full connectivity/ERC, assembly policy and physical placement remain pending; the standalone connector checks do not establish integrated pod acceptance.
