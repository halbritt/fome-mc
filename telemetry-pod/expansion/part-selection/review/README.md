# Independent diagnostic resistor selection review

PASS for exact component selection and captured evidence; no actionable mapping or rating discrepancy found. This does not create assembly bindings or qualify the analog circuit. The independent checker imports no inventory/generator helper and reconstructs the expected40 references and complete inventory.616 checks pass; inventory.py --check also passes.

The exact YAGEO manufacturer-generated PDFs identify RT0603BRD07499KL as499kΩ and RT0603BRD074K99L as4.99kΩ. Both specify0603/1608,0.1%,±25ppm/°C,−55..155°C,0.1W at70°C and75V maximum continuous-voltage ceiling. PDF identity/hashes are pinned independently. These meet the declared nominal value, tolerance, TCR, package and temperature requirements; exact assembly/pad and environmental qualification remain open.

All30 upper-chain resistors map to the499k part: three per each of the original eight diagnostics plus auxiliary5V and thermistor excitation monitors. All10 corresponding lower resistors map to4.99k. IDs, references, values and footprints match the frozen intent. No10k thermistor pullup or other resistor is accidentally included. The intent digest remains148164de5cd362dc7f99307896ebc7811efc4ed03891e28802734da97fac115c. All40 still lack part_binding, as intended.

Voltage and power are simultaneous constraints: use the lesser of75V andsqrt(Pallowed×R), with actual temperature derating. At full0.1W rating the4.99k resistor reaches its power limit at22.34V, well below75V. In the existing301:1 chain, nominal60V across the divider puts about19.93V and0.796mW on each499k upper resistor, and0.1993V/7.96µW on the4.99k lower resistor. This is only a static stress screen under the previously assumed±60V envelope. It does not establish that upstream circuitry limits every fault/transient to60V. The150V overload entry in the exact-part sheet is not a continuous rating or automotive surge qualification. Long-term drift, voltage coefficient, humidity, thermal distribution and complete ADC error/backfeed bounds remain unchanged by selecting these parts.

Retained JLC responses match exact manufacturer/MPN/LCSC identities. C515607 stock101082 was captured2026-10-20T13:17:54.004882+00:00; C723532 stock16395 at13:17:59.421427+00:00. Those are capture-time quantities, not a fresh checkout/availability promise. Both raw responses contain assemblyComponentFlag=false. Catalog stock and extended-library labels therefore do not constitute assembly approval; this review does not change or reinterpret the flag. Recheck procurement/assembly workflow before binding.

Inventory reconciles all332 components into126 binding_present_unverified,6 power_symbol,5 copper_feature_policy_pending,40 selected_not_bound and155 unselected. Thus the40 selections reduce the unresolved selection list but do not reduce the count of actual missing bindings. Existing126 bindings are presence observations, not requalification. JP1–5 remain copper-policy pending; no fake/DNP part bindings are introduced.

The unrelated1.05M search normalization to1K05L is not evidence that1.05M is unavailable. No conclusion about that part is made here.

Run `python3 review/check_selection.py PART_SELECTION_DIR REPORT`. The output includes intent/selection/checker hashes, explicit inventory counts and capture-time stock/assembly facts. No repository circuit source was edited by this reviewer.

## Final producer and adversarial replay

Inspected the completed verify.py and expanded README. The producer checks retained source hashes, validates exact-ID stock captures through the official parser, regenerates the inventory and requires the independent report to reproduce exactly. Its normal replay passes. It makes no network request or source-intent mutation. The README preserves selection-versus-binding and stock-versus-assembly distinctions and the power-limited voltage caveat.

Temporary-copy negative controls all reject in both the independent checker and producer verifier: swapped upper/lower component assignments; changed source-intent value without updating its pin; and raw assemblyComponentFlag changed totrue with the response hash/size updated to avoid a trivial stale-hash failure. The last control fails the explicit assembly-state check. See negative-probes.json and reproducible negative_probes.py. The real source intent remains unchanged. This confirms the captured-false policy is enforced; a future genuine eligibility change needs a new reviewed capture and selection revision, not manual alteration of this packet.
