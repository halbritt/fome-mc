**CURRENT AUTHORITY: [2026-10-23 owner correction](OWNER-CORRECTION.md) supersedes conflicting historical findings below. Keep 132134; SMT search cancelled; paper fit-blocker withdrawn.**

# AGENTEE-494b interface continuation

Recommend **Würth 60312102114405** as the first alternative for chief review. It is the single SMT RF connector evaluated in this slice. Its published land pattern and reproduced native footprint remove the 132134 pin-to-hole fit problem while retaining standard SMA, the 105 °C part rule and the active-antenna DC path. Rank the selected-direction Amphenol 132134 second: its larger-hole joint still depends on an unpublished pin-axis interpretation and an unqualified solder process. Neither recommendation adopts a canonical part or authorizes fabrication.

The remaining admission boundary is the **complete assembled installation contract**: exact mating/seating and bulkhead engagement, panel/O-ring stack, and the assembly process that bounds actual envelopes, including the exact cable assembly’s temperature rating. This packet supplies captured source dimensions and finite conservative planning volumes; it does not claim that those planning volumes prove placement admission. No installed ingress or bench qualification has occurred.

Work starts at `de2cc15b5f9c8b65d3a393ca23fb8c503db7ac42`, descended from frozen `58eac58f`. REQUIREMENTS.md remains `dd6555f706d163709bccb3417d8c366c38de7d603fca8894d0c4a95a58928208`. This is the one deliberate continuation, with replacement cutoff **15:31:34Z**. Agent-449 integrates and arranges the same Fable HIGH delta review; chief adoption follows review.

## Captured evidence and rule precision

The packet retains three real PDFs, with hashes and acquisition URLs in `source-manifest.json`:

- Würth datasheet 60312102114405, revision 002.000, 2019-08-07, seven pages: `b33c2251c45a9966981fab42e26cbff2a804af164184afeb6fb1ece570802e5f`. The manufacturer-authored PDF was captured from its distributor mirror; page 1 was rendered and inspected.
- Amphenol 95-902-570-XXX, revision A, 17-Jan-2022, customer-outline sheet 2 of 2: `e58abfb8db5b623073ceebae28b26b8703300853fc133ab8d94cba42fed52c76`. The literal-plus manufacturer S3 URL returned the PDF, which was rendered and inspected. Its percent-encoded-plus URL returned 403. A **403 error body is not a capture**.
- ISO 2768-1:1989, Table 1: `9d19c25b371f154e7f7f116784bb32cc917f634fe9d0404e9f4f6a77aab6f556`, retained to interpret the tolerance class called by the Würth drawing.

The exact Amphenol drawing now supports RA orientation, standard SMA interfaces, 50 Ω, DC–6 GHz/continuity, 6.00 ±0.25 inch datum length, the nominal Ø6.60/6.10 D-hole and 8/11 mm wrench jaws. This selectively supersedes the prior packet’s uncaptured status for those values. It supplies no complete plug maximum, bend-radius guarantee, seal installation contract or maximum panel thickness; **10.50 REF remains a reference dimension**. `cable-source-resolution.json` records that distinction.

The owner rule remains an **external antenna cable no longer than 500 mm** to SMA, REQUIREMENTS line 70. An external 457 mm cable does **not** violate that rule merely because an internal pigtail exists. The derived 341.25 mm allocation (`500−158.75`) belongs only to an optional **ENGINEERING PROPOSAL** for a combined path; it is not an owner requirement or hard packing constraint. The drawing’s length datum is also not a proven free-cable routing length.

The (+20,+12) correspondence applies only to two explicitly named J2 RF-pad points: saved old pad (86.96,28) ↔ lineage old pad (106.96,40), and saved-frame candidate (83,28) ↔ proposed-outline candidate (103,40). It does not transform other footprints, cutouts, supports, rule areas or outlines. Candidate F(103,40,0) belongs to the proposed 110×80 frame and proves no saved pose or edge clearance against the saved 90×65 board. The earlier packet’s frame files now state this scope explicitly.

## One SMT alternative, with exact electrical binding

The package-local copy is `Agentee494b:SMA_Wurth_60312102114405_Vertical`, unchanged from installed KiCad and hashed `bb57ad63617467448acc24c27dc7a0eae443c9a375a3da26dbad59746f51c01f`. Keep J2 UUID `18c6ebf4-5f6a-5227-b278-be0fa33a91c9`. Pad 1 at local (0,0) is `/POD_GNSS_RF`; two custom pad-2 objects at (0,±2.8) are `/GND`. They represent the ground solder lands, not 1×1 mm anchor rectangles. Keep the four paste windows. The native pattern is rotated 90° relative to the published drawing; nominal pad dimensions agree within its stated ±0.05 mm pattern tolerances.

The datasheet gives −65 to +165 °C, a standard SMA jack, DC–18 GHz and finite centre-contact resistance. It needs no new temperature exception and adds no DC-blocking element. Preserve L3 pad 1 `/ANT_BIAS` → pad 2 `/POD_GNSS_RF` → J2 pad 1. Existing C42 and D3 RF/GND relations remain unchanged. The captured cable drawing specifies continuity. These facts preserve the intended DC route; they do not prove powered antenna operation or fault protection.

The datasheet’s application conditions and actual automotive vibration suitability remain explicit review matters. No manufacturer automotive approval is claimed and no vendor contact was made. Named manual-fit source: **Mouser 710-60312102114405**. Record the criterion-5 `not_assembled` deviation, exclude J2 from JLC assembly BOM/CPL, preserve electrical membership, and use a qualified manual reflow process. No LCSC ID, stock claim or order is invented. Retain the external sealed SMA through the candidate 095-902-570-006 interface, whose purchase source remains Newark 25AK8098.

## Finite reservations and assembly

`published-vs-selected.json` separates the dimensional evidence from engineering defaults. The SMT body’s linear bounds are 6.55 mm square and 9.04 mm high before solder seating, from 6.35/8.84 nominal and the referenced ±0.2 mm general tolerance. These are linear dimensional bounds, not a complete assembled tolerance model. The contact’s 0–0.07 mm relative coplanarity is not a solder-standoff guarantee.

`finite-reservations.json` gives finite volumes for both faces, seating/solder, mate, insertion, tools, cable and two strain-relief clamps. The SMT proposal uses an 8×8×10 mm F-side body bin and no J2 pin/solder volume below B. The retained THT proposal uses a 9×9×10 mm F bin and 3.2 mm B-depth bin. Selected seating lift ≤0.20 mm and F solder extent ≤0.50 mm are **conservative assembly proposals**, not published capabilities or qualified joint limits.

The RA mate bin is 40×24×30 mm. A phase-only tool cylinder of radius 175 mm accommodates a selected tool head/handle envelope; published jaw sizes do not establish those head dimensions. The cable bay, radius-10 mm filleted path and two 10×10×8 mm clamp bins are finite local proposals with explicit coordinates. The path’s 144.832 mm arithmetic does not establish actual termination/slack fit or a published minimum bend radius. These defaults are advisory and must not silently become sourced hard gates. Actual process and mating datums must bind them before placement admission.

`assembly-and-qualification.json` supplies the sequence: qualified reflow and inspection on the bare board; continuity/isolation and bias-net checks; body counterhold in a fixture during mating; manufacturer-recommended 0.57 N·m for the Würth interface; reviewed cable routing and jacket clamps; then the actual bulkhead seal stack before lid closure. Never react mating torque through the SMT solder pads. The local interface proposal designs no complete enclosure and adds no penetration.

Before fabrication release, bind the adopted MPN/land pattern, actual installation/process contract, BOM/CPL deviation and final source geometry. The writer must regenerate and bind both RF board-area UUIDs `460352a8-dace-51a2-842b-c1e4ef7ad212` and `93d1ddf1-382d-5ed8-abfa-2bf617ad0cae` after adoption. Preserve ordinary RF 0.293/0.2032 pending 492; regenerate the endpoint, launch and ground transition and remove obsolete PTH antipads. No net-wide waiver or stackup change is introduced.

After a built assembly exists, qualify actual solder/retention, vibration, cable strain relief, powered antenna/RF performance, thermal rise and complete installed IP67. Those later tests are not substitutes for missing pre-fab inputs, and no pre-build ingress test is claimed.

## Verification

`native494b.json` records peecee-wsl `native-admit` test/weight 1, KiCad 10.0.7: three actual SMT pads, one RF/two GND, zero drills; exact custom-pad bounds; minimum 3.4395 mm margin against the ideal proposed 110×80 rectangle. It also observes the saved old RF pad (86.96,28) and existing bias-pad nets. The source board hash remains `0b68a0ac4b3978b77faa497fd208b35a376c89d576f1b4e08b276966db997eac`; no board was saved. This is no final placement, native DRC, RF or assembly acceptance. Footprint and source hashes, JSON/receipt schema and both packet manifests are checked before commit. The prior accepted H1 correction and H2 unresolved disclosures are preserved.

Doctrine receipt: `analysis/decision-receipt.json` abstains from complete admission while ranking the one SMT alternative. It applies authority boundaries, evidence before intervention, explicit invariants, implementation readiness and repository precedence from packet `pkt-d4962ee60fcbc8a2`, content hash `d4962ee60fcbc8a2cca80dad352ff06b8648114b23da13fc2d755797fc9b53b7`. Corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`, validated release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Unmet obligations retain material/nonmaterial classifications; the assembly-contract omission stays material.
