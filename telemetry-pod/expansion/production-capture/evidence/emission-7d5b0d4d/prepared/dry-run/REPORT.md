# Expanded telemetry pod Revision 3 campaign scope (microSD source) review

Outcome: **incomplete**; process state: `incomplete`.

Candidate: `5504a022417b5bf49ad6b1cec7f39f65bd3f8a566e46a286bb656904bef837ba`
Run: `5deded60-67ec-4e56-b292-d3c0ca604765`

Revision 3 accounting for all 59 requirements and 20 prose entries against the current microSD source, declared for the pod driver stage order schematic, placement, routing, verification. Native ERC, netlist, placement-projected DRC, routed DRC, copper facts and the fab_package done gate are the only executable checks; every other obligation remains explicit. The placement subject expects the 305 schematic references plus the envelope corner holes H1-H4. Compilation is preparation, not native execution, placement, routing or acceptance.

## Checks

| Check | Execution | Design result | Summary |
| --- | --- | --- | --- |
| erc | ok | defect | schematic: expected native content absent |
| netlist | ok | defect | schematic: expected native content absent |
| parts | ok | defect | schematic: expected native content absent |
| antenna-facts | ok | defect | schematic: expected native content absent |
| placement-drc | ok | defect | placement: expected native content absent |
| envelope-outline | ok | defect | placement: expected native content absent |
| envelope-layer-count | ok | defect | placement: expected native content absent |
| envelope-stackup | ok | defect | placement: expected native content absent |
| envelope-hole-h1 | ok | defect | placement: expected native content absent |
| envelope-hole-h2 | ok | defect | placement: expected native content absent |
| envelope-hole-h3 | ok | defect | placement: expected native content absent |
| envelope-hole-h4 | ok | defect | placement: expected native content absent |
| envelope-keepout-radio-antenna | ok | defect | placement: expected native content absent |
| envelope-keepout-d-pcb-7v2-in1-no-tracks | ok | defect | placement: expected native content absent |
| envelope-keepout-d-pcb-6-rf-reference | ok | defect | placement: expected native content absent |
| envelope-fixed-j1 | ok | defect | placement: expected native content absent |
| envelope-fixed-j2 | ok | defect | placement: expected native content absent |
| envelope-fixed-u1 | ok | defect | placement: expected native content absent |
| envelope-fixed-u2 | ok | defect | placement: expected native content absent |
| envelope-fixed-j3 | ok | defect | placement: expected native content absent |
| envelope-containment | ok | defect | placement: expected native content absent |
| electrical-locality | ok | defect | placement: expected native content absent |
| drc | ok | defect | routing: expected native content absent |
| routing-geometry | ok | defect | routing: expected native content absent |
| envelope-fab-profile | ok | defect | routing: expected native content absent |
| assembly | ok | defect | verification: expected native content absent |
| fab-package | ok | defect | verification: expected native content absent |

## RF review applicability

RF review required: 2 RF indicator(s) detected in captured sources.
Binding: `0ae9c179e0d29ac416909c1da7b57bd72240804326b0412bafa2e7ef8251adf9`; gate: required RF review missing: no execution record.
- Missing RF evidence: rf_constraints: no captured source bound
- Missing RF evidence: rf_captures: no captured source bound
- Missing RF evidence: planes: no filled copper zone in the captured board; plane continuity is unknown
- Missing RF evidence: routing adapter evidence missing_evidence: no routing adapter receipt was supplied for this candidate; layer policy and RF reference continuity are unknown

## Initial reviews


## Findings and dispositions

### check/erc: schematic: expected native content absent

Disposition: **unresolved**.

Location: erc. Condition: check erc (erc).

schematic: expected native content absent

schematic: expected native content absent
- [work/erc/stage-subject/execution.json](<work/erc/stage-subject/execution.json>): check:erc
- [work/erc/stage-subject/console.log](<work/erc/stage-subject/console.log>): check:erc
- [work/erc/stage-subject/native-netlist.xml](<work/erc/stage-subject/native-netlist.xml>): check:erc
- [work/erc/stage-subject/native-observation.json](<work/erc/stage-subject/native-observation.json>): check:erc
- [work/erc/stage-subject/references.json](<work/erc/stage-subject/references.json>): check:erc
- [work/erc/stage-subject.json](<work/erc/stage-subject.json>): check:erc

### check/netlist: schematic: expected native content absent

Disposition: **unresolved**.

Location: netlist. Condition: check netlist (netlist).

schematic: expected native content absent

schematic: expected native content absent
- [work/netlist/stage-subject/execution.json](<work/netlist/stage-subject/execution.json>): check:netlist
- [work/netlist/stage-subject/console.log](<work/netlist/stage-subject/console.log>): check:netlist
- [work/netlist/stage-subject/native-netlist.xml](<work/netlist/stage-subject/native-netlist.xml>): check:netlist
- [work/netlist/stage-subject/native-observation.json](<work/netlist/stage-subject/native-observation.json>): check:netlist
- [work/netlist/stage-subject/references.json](<work/netlist/stage-subject/references.json>): check:netlist
- [work/netlist/stage-subject.json](<work/netlist/stage-subject.json>): check:netlist

### check/parts: schematic: expected native content absent

Disposition: **unresolved**.

Location: parts. Condition: check parts (parts_subset).

schematic: expected native content absent

schematic: expected native content absent
- [work/parts/stage-subject/execution.json](<work/parts/stage-subject/execution.json>): check:parts
- [work/parts/stage-subject/console.log](<work/parts/stage-subject/console.log>): check:parts
- [work/parts/stage-subject/native-netlist.xml](<work/parts/stage-subject/native-netlist.xml>): check:parts
- [work/parts/stage-subject/native-observation.json](<work/parts/stage-subject/native-observation.json>): check:parts
- [work/parts/stage-subject/references.json](<work/parts/stage-subject/references.json>): check:parts
- [work/parts/stage-subject.json](<work/parts/stage-subject.json>): check:parts

### check/antenna-facts: schematic: expected native content absent

Disposition: **unresolved**.

Location: antenna-facts. Condition: check antenna-facts (datasheet_facts).

schematic: expected native content absent

schematic: expected native content absent
- [work/antenna-facts/stage-subject/execution.json](<work/antenna-facts/stage-subject/execution.json>): check:antenna-facts
- [work/antenna-facts/stage-subject/console.log](<work/antenna-facts/stage-subject/console.log>): check:antenna-facts
- [work/antenna-facts/stage-subject/native-netlist.xml](<work/antenna-facts/stage-subject/native-netlist.xml>): check:antenna-facts
- [work/antenna-facts/stage-subject/native-observation.json](<work/antenna-facts/stage-subject/native-observation.json>): check:antenna-facts
- [work/antenna-facts/stage-subject/references.json](<work/antenna-facts/stage-subject/references.json>): check:antenna-facts
- [work/antenna-facts/stage-subject.json](<work/antenna-facts/stage-subject.json>): check:antenna-facts

### check/placement-drc: placement: expected native content absent

Disposition: **unresolved**.

Location: placement-drc. Condition: check placement-drc (drc).

placement: expected native content absent

placement: expected native content absent
- [work/placement-drc/stage-subject/execution.json](<work/placement-drc/stage-subject/execution.json>): check:placement-drc
- [work/placement-drc/stage-subject/console.log](<work/placement-drc/stage-subject/console.log>): check:placement-drc
- [work/placement-drc/stage-subject/native-observation.json](<work/placement-drc/stage-subject/native-observation.json>): check:placement-drc
- [work/placement-drc/stage-subject/references.json](<work/placement-drc/stage-subject/references.json>): check:placement-drc
- [work/placement-drc/stage-subject.json](<work/placement-drc/stage-subject.json>): check:placement-drc

### check/envelope-outline: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-outline. Condition: check envelope-outline (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-outline/stage-subject/execution.json](<work/envelope-outline/stage-subject/execution.json>): check:envelope-outline
- [work/envelope-outline/stage-subject/console.log](<work/envelope-outline/stage-subject/console.log>): check:envelope-outline
- [work/envelope-outline/stage-subject/native-observation.json](<work/envelope-outline/stage-subject/native-observation.json>): check:envelope-outline
- [work/envelope-outline/stage-subject/references.json](<work/envelope-outline/stage-subject/references.json>): check:envelope-outline
- [work/envelope-outline/stage-subject.json](<work/envelope-outline/stage-subject.json>): check:envelope-outline

### check/envelope-layer-count: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-layer-count. Condition: check envelope-layer-count (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-layer-count/stage-subject/execution.json](<work/envelope-layer-count/stage-subject/execution.json>): check:envelope-layer-count
- [work/envelope-layer-count/stage-subject/console.log](<work/envelope-layer-count/stage-subject/console.log>): check:envelope-layer-count
- [work/envelope-layer-count/stage-subject/native-observation.json](<work/envelope-layer-count/stage-subject/native-observation.json>): check:envelope-layer-count
- [work/envelope-layer-count/stage-subject/references.json](<work/envelope-layer-count/stage-subject/references.json>): check:envelope-layer-count
- [work/envelope-layer-count/stage-subject.json](<work/envelope-layer-count/stage-subject.json>): check:envelope-layer-count

### check/envelope-stackup: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-stackup. Condition: check envelope-stackup (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-stackup/stage-subject/execution.json](<work/envelope-stackup/stage-subject/execution.json>): check:envelope-stackup
- [work/envelope-stackup/stage-subject/console.log](<work/envelope-stackup/stage-subject/console.log>): check:envelope-stackup
- [work/envelope-stackup/stage-subject/native-observation.json](<work/envelope-stackup/stage-subject/native-observation.json>): check:envelope-stackup
- [work/envelope-stackup/stage-subject/references.json](<work/envelope-stackup/stage-subject/references.json>): check:envelope-stackup
- [work/envelope-stackup/stage-subject.json](<work/envelope-stackup/stage-subject.json>): check:envelope-stackup

### check/envelope-hole-h1: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-hole-h1. Condition: check envelope-hole-h1 (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-hole-h1/stage-subject/execution.json](<work/envelope-hole-h1/stage-subject/execution.json>): check:envelope-hole-h1
- [work/envelope-hole-h1/stage-subject/console.log](<work/envelope-hole-h1/stage-subject/console.log>): check:envelope-hole-h1
- [work/envelope-hole-h1/stage-subject/native-observation.json](<work/envelope-hole-h1/stage-subject/native-observation.json>): check:envelope-hole-h1
- [work/envelope-hole-h1/stage-subject/references.json](<work/envelope-hole-h1/stage-subject/references.json>): check:envelope-hole-h1
- [work/envelope-hole-h1/stage-subject.json](<work/envelope-hole-h1/stage-subject.json>): check:envelope-hole-h1

### check/envelope-hole-h2: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-hole-h2. Condition: check envelope-hole-h2 (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-hole-h2/stage-subject/execution.json](<work/envelope-hole-h2/stage-subject/execution.json>): check:envelope-hole-h2
- [work/envelope-hole-h2/stage-subject/console.log](<work/envelope-hole-h2/stage-subject/console.log>): check:envelope-hole-h2
- [work/envelope-hole-h2/stage-subject/native-observation.json](<work/envelope-hole-h2/stage-subject/native-observation.json>): check:envelope-hole-h2
- [work/envelope-hole-h2/stage-subject/references.json](<work/envelope-hole-h2/stage-subject/references.json>): check:envelope-hole-h2
- [work/envelope-hole-h2/stage-subject.json](<work/envelope-hole-h2/stage-subject.json>): check:envelope-hole-h2

### check/envelope-hole-h3: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-hole-h3. Condition: check envelope-hole-h3 (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-hole-h3/stage-subject/execution.json](<work/envelope-hole-h3/stage-subject/execution.json>): check:envelope-hole-h3
- [work/envelope-hole-h3/stage-subject/console.log](<work/envelope-hole-h3/stage-subject/console.log>): check:envelope-hole-h3
- [work/envelope-hole-h3/stage-subject/native-observation.json](<work/envelope-hole-h3/stage-subject/native-observation.json>): check:envelope-hole-h3
- [work/envelope-hole-h3/stage-subject/references.json](<work/envelope-hole-h3/stage-subject/references.json>): check:envelope-hole-h3
- [work/envelope-hole-h3/stage-subject.json](<work/envelope-hole-h3/stage-subject.json>): check:envelope-hole-h3

### check/envelope-hole-h4: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-hole-h4. Condition: check envelope-hole-h4 (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-hole-h4/stage-subject/execution.json](<work/envelope-hole-h4/stage-subject/execution.json>): check:envelope-hole-h4
- [work/envelope-hole-h4/stage-subject/console.log](<work/envelope-hole-h4/stage-subject/console.log>): check:envelope-hole-h4
- [work/envelope-hole-h4/stage-subject/native-observation.json](<work/envelope-hole-h4/stage-subject/native-observation.json>): check:envelope-hole-h4
- [work/envelope-hole-h4/stage-subject/references.json](<work/envelope-hole-h4/stage-subject/references.json>): check:envelope-hole-h4
- [work/envelope-hole-h4/stage-subject.json](<work/envelope-hole-h4/stage-subject.json>): check:envelope-hole-h4

### check/envelope-keepout-radio-antenna: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-keepout-radio-antenna. Condition: check envelope-keepout-radio-antenna (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-keepout-radio-antenna/stage-subject/execution.json](<work/envelope-keepout-radio-antenna/stage-subject/execution.json>): check:envelope-keepout-radio-antenna
- [work/envelope-keepout-radio-antenna/stage-subject/console.log](<work/envelope-keepout-radio-antenna/stage-subject/console.log>): check:envelope-keepout-radio-antenna
- [work/envelope-keepout-radio-antenna/stage-subject/native-observation.json](<work/envelope-keepout-radio-antenna/stage-subject/native-observation.json>): check:envelope-keepout-radio-antenna
- [work/envelope-keepout-radio-antenna/stage-subject/references.json](<work/envelope-keepout-radio-antenna/stage-subject/references.json>): check:envelope-keepout-radio-antenna
- [work/envelope-keepout-radio-antenna/stage-subject.json](<work/envelope-keepout-radio-antenna/stage-subject.json>): check:envelope-keepout-radio-antenna

### check/envelope-keepout-d-pcb-7v2-in1-no-tracks: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-keepout-d-pcb-7v2-in1-no-tracks. Condition: check envelope-keepout-d-pcb-7v2-in1-no-tracks (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/execution.json](<work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/execution.json>): check:envelope-keepout-d-pcb-7v2-in1-no-tracks
- [work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/console.log](<work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/console.log>): check:envelope-keepout-d-pcb-7v2-in1-no-tracks
- [work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/native-observation.json](<work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/native-observation.json>): check:envelope-keepout-d-pcb-7v2-in1-no-tracks
- [work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/references.json](<work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject/references.json>): check:envelope-keepout-d-pcb-7v2-in1-no-tracks
- [work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject.json](<work/envelope-keepout-d-pcb-7v2-in1-no-tracks/stage-subject.json>): check:envelope-keepout-d-pcb-7v2-in1-no-tracks

### check/envelope-keepout-d-pcb-6-rf-reference: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-keepout-d-pcb-6-rf-reference. Condition: check envelope-keepout-d-pcb-6-rf-reference (board_envelope).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/execution.json](<work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/execution.json>): check:envelope-keepout-d-pcb-6-rf-reference
- [work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/console.log](<work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/console.log>): check:envelope-keepout-d-pcb-6-rf-reference
- [work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/native-observation.json](<work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/native-observation.json>): check:envelope-keepout-d-pcb-6-rf-reference
- [work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/references.json](<work/envelope-keepout-d-pcb-6-rf-reference/stage-subject/references.json>): check:envelope-keepout-d-pcb-6-rf-reference
- [work/envelope-keepout-d-pcb-6-rf-reference/stage-subject.json](<work/envelope-keepout-d-pcb-6-rf-reference/stage-subject.json>): check:envelope-keepout-d-pcb-6-rf-reference

### check/envelope-fixed-j1: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-fixed-j1. Condition: check envelope-fixed-j1 (placement).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-fixed-j1/stage-subject/execution.json](<work/envelope-fixed-j1/stage-subject/execution.json>): check:envelope-fixed-j1
- [work/envelope-fixed-j1/stage-subject/console.log](<work/envelope-fixed-j1/stage-subject/console.log>): check:envelope-fixed-j1
- [work/envelope-fixed-j1/stage-subject/native-observation.json](<work/envelope-fixed-j1/stage-subject/native-observation.json>): check:envelope-fixed-j1
- [work/envelope-fixed-j1/stage-subject/references.json](<work/envelope-fixed-j1/stage-subject/references.json>): check:envelope-fixed-j1
- [work/envelope-fixed-j1/stage-subject.json](<work/envelope-fixed-j1/stage-subject.json>): check:envelope-fixed-j1

### check/envelope-fixed-j2: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-fixed-j2. Condition: check envelope-fixed-j2 (placement).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-fixed-j2/stage-subject/execution.json](<work/envelope-fixed-j2/stage-subject/execution.json>): check:envelope-fixed-j2
- [work/envelope-fixed-j2/stage-subject/console.log](<work/envelope-fixed-j2/stage-subject/console.log>): check:envelope-fixed-j2
- [work/envelope-fixed-j2/stage-subject/native-observation.json](<work/envelope-fixed-j2/stage-subject/native-observation.json>): check:envelope-fixed-j2
- [work/envelope-fixed-j2/stage-subject/references.json](<work/envelope-fixed-j2/stage-subject/references.json>): check:envelope-fixed-j2
- [work/envelope-fixed-j2/stage-subject.json](<work/envelope-fixed-j2/stage-subject.json>): check:envelope-fixed-j2

### check/envelope-fixed-u1: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-fixed-u1. Condition: check envelope-fixed-u1 (placement).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-fixed-u1/stage-subject/execution.json](<work/envelope-fixed-u1/stage-subject/execution.json>): check:envelope-fixed-u1
- [work/envelope-fixed-u1/stage-subject/console.log](<work/envelope-fixed-u1/stage-subject/console.log>): check:envelope-fixed-u1
- [work/envelope-fixed-u1/stage-subject/native-observation.json](<work/envelope-fixed-u1/stage-subject/native-observation.json>): check:envelope-fixed-u1
- [work/envelope-fixed-u1/stage-subject/references.json](<work/envelope-fixed-u1/stage-subject/references.json>): check:envelope-fixed-u1
- [work/envelope-fixed-u1/stage-subject.json](<work/envelope-fixed-u1/stage-subject.json>): check:envelope-fixed-u1

### check/envelope-fixed-u2: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-fixed-u2. Condition: check envelope-fixed-u2 (placement).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-fixed-u2/stage-subject/execution.json](<work/envelope-fixed-u2/stage-subject/execution.json>): check:envelope-fixed-u2
- [work/envelope-fixed-u2/stage-subject/console.log](<work/envelope-fixed-u2/stage-subject/console.log>): check:envelope-fixed-u2
- [work/envelope-fixed-u2/stage-subject/native-observation.json](<work/envelope-fixed-u2/stage-subject/native-observation.json>): check:envelope-fixed-u2
- [work/envelope-fixed-u2/stage-subject/references.json](<work/envelope-fixed-u2/stage-subject/references.json>): check:envelope-fixed-u2
- [work/envelope-fixed-u2/stage-subject.json](<work/envelope-fixed-u2/stage-subject.json>): check:envelope-fixed-u2

### check/envelope-fixed-j3: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-fixed-j3. Condition: check envelope-fixed-j3 (placement).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-fixed-j3/stage-subject/execution.json](<work/envelope-fixed-j3/stage-subject/execution.json>): check:envelope-fixed-j3
- [work/envelope-fixed-j3/stage-subject/console.log](<work/envelope-fixed-j3/stage-subject/console.log>): check:envelope-fixed-j3
- [work/envelope-fixed-j3/stage-subject/native-observation.json](<work/envelope-fixed-j3/stage-subject/native-observation.json>): check:envelope-fixed-j3
- [work/envelope-fixed-j3/stage-subject/references.json](<work/envelope-fixed-j3/stage-subject/references.json>): check:envelope-fixed-j3
- [work/envelope-fixed-j3/stage-subject.json](<work/envelope-fixed-j3/stage-subject.json>): check:envelope-fixed-j3

### check/envelope-containment: placement: expected native content absent

Disposition: **unresolved**.

Location: envelope-containment. Condition: check envelope-containment (placement).

placement: expected native content absent

placement: expected native content absent
- [work/envelope-containment/stage-subject/execution.json](<work/envelope-containment/stage-subject/execution.json>): check:envelope-containment
- [work/envelope-containment/stage-subject/console.log](<work/envelope-containment/stage-subject/console.log>): check:envelope-containment
- [work/envelope-containment/stage-subject/native-observation.json](<work/envelope-containment/stage-subject/native-observation.json>): check:envelope-containment
- [work/envelope-containment/stage-subject/references.json](<work/envelope-containment/stage-subject/references.json>): check:envelope-containment
- [work/envelope-containment/stage-subject.json](<work/envelope-containment/stage-subject.json>): check:envelope-containment

### check/electrical-locality: placement: expected native content absent

Disposition: **unresolved**.

Location: electrical-locality. Condition: check electrical-locality (placement).

placement: expected native content absent

placement: expected native content absent
- [work/electrical-locality/stage-subject/execution.json](<work/electrical-locality/stage-subject/execution.json>): check:electrical-locality
- [work/electrical-locality/stage-subject/console.log](<work/electrical-locality/stage-subject/console.log>): check:electrical-locality
- [work/electrical-locality/stage-subject/native-observation.json](<work/electrical-locality/stage-subject/native-observation.json>): check:electrical-locality
- [work/electrical-locality/stage-subject/references.json](<work/electrical-locality/stage-subject/references.json>): check:electrical-locality
- [work/electrical-locality/stage-subject.json](<work/electrical-locality/stage-subject.json>): check:electrical-locality

### check/drc: routing: expected native content absent

Disposition: **unresolved**.

Location: drc. Condition: check drc (drc).

routing: expected native content absent

routing: expected native content absent
- [work/drc/stage-subject/execution.json](<work/drc/stage-subject/execution.json>): check:drc
- [work/drc/stage-subject/console.log](<work/drc/stage-subject/console.log>): check:drc
- [work/drc/stage-subject/native-observation.json](<work/drc/stage-subject/native-observation.json>): check:drc
- [work/drc/stage-subject/references.json](<work/drc/stage-subject/references.json>): check:drc
- [work/drc/stage-subject.json](<work/drc/stage-subject.json>): check:drc

### check/routing-geometry: routing: expected native content absent

Disposition: **unresolved**.

Location: routing-geometry. Condition: check routing-geometry (geometry).

routing: expected native content absent

routing: expected native content absent
- [work/routing-geometry/stage-subject/execution.json](<work/routing-geometry/stage-subject/execution.json>): check:routing-geometry
- [work/routing-geometry/stage-subject/console.log](<work/routing-geometry/stage-subject/console.log>): check:routing-geometry
- [work/routing-geometry/stage-subject/native-observation.json](<work/routing-geometry/stage-subject/native-observation.json>): check:routing-geometry
- [work/routing-geometry/stage-subject/references.json](<work/routing-geometry/stage-subject/references.json>): check:routing-geometry
- [work/routing-geometry/stage-subject.json](<work/routing-geometry/stage-subject.json>): check:routing-geometry

### check/envelope-fab-profile: routing: expected native content absent

Disposition: **unresolved**.

Location: envelope-fab-profile. Condition: check envelope-fab-profile (fab_profile).

routing: expected native content absent

routing: expected native content absent
- [work/envelope-fab-profile/stage-subject/execution.json](<work/envelope-fab-profile/stage-subject/execution.json>): check:envelope-fab-profile
- [work/envelope-fab-profile/stage-subject/console.log](<work/envelope-fab-profile/stage-subject/console.log>): check:envelope-fab-profile
- [work/envelope-fab-profile/stage-subject/native-observation.json](<work/envelope-fab-profile/stage-subject/native-observation.json>): check:envelope-fab-profile
- [work/envelope-fab-profile/stage-subject/references.json](<work/envelope-fab-profile/stage-subject/references.json>): check:envelope-fab-profile
- [work/envelope-fab-profile/stage-subject.json](<work/envelope-fab-profile/stage-subject.json>): check:envelope-fab-profile

### check/assembly: verification: expected native content absent

Disposition: **unresolved**.

Location: assembly. Condition: check assembly (assembly_readiness).

verification: expected native content absent

verification: expected native content absent
- [work/assembly/stage-subject/execution.json](<work/assembly/stage-subject/execution.json>): check:assembly
- [work/assembly/stage-subject/console.log](<work/assembly/stage-subject/console.log>): check:assembly
- [work/assembly/stage-subject/native-netlist.xml](<work/assembly/stage-subject/native-netlist.xml>): check:assembly
- [work/assembly/stage-subject/native-observation.json](<work/assembly/stage-subject/native-observation.json>): check:assembly
- [work/assembly/stage-subject/references.json](<work/assembly/stage-subject/references.json>): check:assembly
- [work/assembly/stage-subject.json](<work/assembly/stage-subject.json>): check:assembly

### check/fab-package: verification: expected native content absent

Disposition: **unresolved**.

Location: fab-package. Condition: check fab-package (fab_package).

verification: expected native content absent

verification: expected native content absent
- [work/fab-package/stage-subject/execution.json](<work/fab-package/stage-subject/execution.json>): check:fab-package
- [work/fab-package/stage-subject/console.log](<work/fab-package/stage-subject/console.log>): check:fab-package
- [work/fab-package/stage-subject/native-netlist.xml](<work/fab-package/stage-subject/native-netlist.xml>): check:fab-package
- [work/fab-package/stage-subject/native-observation.json](<work/fab-package/stage-subject/native-observation.json>): check:fab-package
- [work/fab-package/stage-subject/references.json](<work/fab-package/stage-subject/references.json>): check:fab-package
- [work/fab-package/stage-subject.json](<work/fab-package/stage-subject.json>): check:fab-package

## Limitations

- No expanded placed or routed PCB exists for this scope. The pod driver scaffold supplies scaffold/project; never substitute the historical v9 pilot, a diagnostic placement (iteration-7, iter8n) or a historical route.
- Stage order is schematic, placement, routing, verification, as pod_driver requires. Fab stays outside stages.order until AGENTEE-146-compatible pod step wiring exists; the fab_package done check grades the verification stage.
- Stage subjects are the 305 native references of the current microSD schematic (telemetry-pod/expansion/storage-microsd/project/telemetry-pod.kicad_sch sha256 4da27afc8d9cd7ff3d1fd8e23f855747072c050d25601b89fb3909b688e49f23). The placement subject also expects the four board-only corner mounting holes H1-H4 (309 footprints; POD-ME-HOLES). No other board-only footprint is an expected subject.
- Review profile pod-rf-review-v1 (agent-ee profiles/pod-review.json sha256 885e17074b9c367f296eb6acc4c2a2f65fb29108f332f0a55fb622a38ae858da) declares the rf reviewer that the pod RF applicability gate requires. A declared reviewer is not an RF review result; a fresh RF review of a routed current-placement candidate is still owed.
- Routing-stage copper geometry reports facts only. No pod-wide numeric track-width gate is declared here because none has a cited source in this scope; net-class widths are graded by native DRC from the captured project rules.
- POD-AC-6: NOT CHECKED beyond the fab_package done gate: the owner uploads the sealed Gerber package to JLCPCB once and binds the saved DFM report to the package hash, and confirms every PREVIEW_REQUIRED CPL rotation in the placement preview before ordering. Local geometry and package checks do not replace either; this scope authorizes no upload or order.
- POD-TEMP-AUTHORITY: NOT CHECKED: Recorded authority for retaining parts rated below 105 degC. Direct owner acceptance exists only for U1, U2 and U4 (operating-temperature-acceptances.txt sha256 7ca91bc748e3029432e5bb40501c056301429da08119759c612daea7cca8678a, lines 1-3, -20 to 85 degC each). U3 NEO-M9N-00B and J3 DM3AT-SF-PEJM5 carry DELEGATED ENGINEERING acceptance, not owner acceptance: telemetry-pod/expansion/design-rules/constraints.json (sha256 e7e095b3ca595fdfb3c73fc22ad87c326fbc1c152523e85f2da4df4d908ea2e4) decisions "D-PCB-9 NEO-M9N 85 C rating exception (2026-10-21)" and "D-PCB-12 J3 microSD socket 85 C rating exception (2026-10-21)", decided autonomously under the owner's delegation (AGENTS.md: owner-reserved decisions are made autonomously, recorded, and reviewed by the owner after the fact) on the owner's U1/U2/U4 terms of AGENTEE-209 and AGENTEE-310: each part is tested against its actual limit and thermal evidence is required. Executable provenance for U3 and J3 is unresolved: the AGENTEE-310 reduced_acceptance contract (agent-ee assembly_readiness) accepts only a {source, sha256, line, quote} citation of one canonical line of the dedicated operating-temperature-acceptances.txt, which it treats as a captured owner decision, and has no form for delegated authority; no U3 or J3 line is written there, because that would misstate the authority. Actual thermal qualification is pending for all five parts (POD-TEMP-ENCLOSURE).
- POD-TEMP-SELECTION: NOT CHECKED: Part-selection criterion (POD-ME-3: parts rated to 105 degC or higher). U1, U2, U3 and U4 (-40 to 85 degC) and J3 (-25 to 85 degC) do not meet it. They are retained under POD-TEMP-AUTHORITY, not exempted; retention changes neither their ratings nor the criterion. The D-PCB-9 and D-PCB-12 bases (no stocked 105 degC alternative with a library footprint; NEO-M9L-01A has no JLC stock and changes three pin functions) are agent engineering judgements awaiting owner review, reversible by substituting a 105 degC part.
- POD-TEMP-ACTUAL-LIMITS: NOT CHECKED: Exact part limits. Each part below 105 degC is judged against its own manufacturer rating; none is skipped. U1 ESP32-S3-WROOM-1-N8 (Espressif Systems, LCSC C2913198, RF_Module:ESP32-S3-WROOM-1): -40 to 85 degC ambient, datasheet sha256 27d71971da07c280c6068d08c74720d1a25b8f20cf8494dc1765bdd28d40d435 page 27 (Recommended operating conditions table, TA operating ambient temperature, 85 degC version); U2 LSM6DSO32TR (STMicroelectronics, LCSC C1864162, Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y): -40 to 85 degC operating, datasheet sha256 d1776336f5060da06c4fa4c3aac293372e20cffa4f9d72fe3296b9a56ed6c0b7 page 26 (Mechanical characteristics table, Top operating temperature range); U3 NEO-M9N-00B (U-BLOX, LCSC C5119087, RF_GPS:ublox_NEO): -40 to 85 degC operating, datasheet sha256 e21b35c1a4fd04f353e298a3c3c411c08e683a318d87ad3af9f570da40a40150 page 11 (Operating conditions table, Topr operating temperature); U4 MCP3208-BI/SL (Microchip Tech, LCSC C2979740, Package_SO:SOIC-16_3.9x9.9mm_P1.27mm): -40 to 85 degC ambient, datasheet sha256 89bc1e17c35e2bb1c7b8fbf0b775b3729ce9fe4d27f7e9c052a774757afc0c20 page 37 (Product identification system, temperature range I (industrial)); J3 DM3AT-SF-PEJM5 (HRS(Hirose), LCSC C114218, Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5): catalog -25 to 85 degC from telemetry-pod/expansion/part-bindings/microsd-stock/responses/C114218.json sha256 af7f58470a86d75ebd83620b9b6ce0270e242a2f765f652e195a0d90c5c7b3ae. Evidence gaps: the J3 manufacturer rating is not captured (Hirose datasheet bytes absent; the catalog value is a distributor attribute), and U3 archive coverage is incomplete (the cited NEO-M9N datasheet bytes are outside this repository, in the coordinator cache only). Each obligation requires the exact MPN, manufacturer and package binding and the captured manufacturer rating; a captured rating that does not cover the accepted range, or an expected part temperature above the rating, is a defect, and a missing rating is unknown, never pass.
- POD-TEMP-UNRATED: NOT CHECKED: Of 305 references, 172 have a captured catalog rating of at least 105 degC, 5 are below it (POD-TEMP-ACTUAL-LIMITS), 117 bound parts have no captured operating-temperature rating, and 11 references (JP1, JP2, JP3, JP4, JP5, TP1, TP2, TP3, TP4, TP5, TP6) carry no part binding. Unknown ratings remain unknown, never pass; catalog ratings still need manufacturer confirmation (rev3-microsd/temperature-ratings.json).
- POD-TEMP-ENCLOSURE: NOT CHECKED: 85 degC board ambient plus self-heating, kept separate from the 105 degC selection and the exact part limits. Neither the -20 to +85 degC board ambient envelope in the tail cowl nor each part's temperature rise above it is qualified. Enclosure thermal validation must measure the selected components, including U3 and J3, under worst-case supply, sensor load, radio and logging activity, including self-heating and heat from neighbouring parts, against each part's own manufacturer limit. Missing part-bound thermal evidence is unknown, never pass; enclosure ambient may not stand in for a part's rated metric without evidence relating them. D-PCB-12's statement that J3 is a passive contact set with no self-heating is an engineering assumption needing review, not evidence: contact-resistance heating under card supply current and the inserted card's own dissipation are not evaluated. A passing assembly predicate does not discharge this obligation.
- POD-ME-HOLES: NOT CHECKED beyond presence: The placement-stage subject expects 309 footprints: the 305 schematic references plus the four board-only corner mounting holes H1, H2, H3 and H4 declared in telemetry-pod/expansion/placement-inputs/envelope.json (sha256 ad0a3597ad0a7d4e5b52288405c510fe60b92595b52350feb1e6ee89d537b685, mounting_holes): H1 centred at (4, 4) mm, 3.2 mm round drill, non-plated (NPTH), position tolerance 0 mm; H2 centred at (86, 4) mm, 3.2 mm round drill, non-plated (NPTH), position tolerance 0 mm; H3 centred at (86, 61) mm, 3.2 mm round drill, non-plated (NPTH), position tolerance 0 mm; H4 centred at (4, 61) mm, 3.2 mm round drill, non-plated (NPTH), position tolerance 0 mm. The stage subject witness grades only that every expected reference is present (missing references are stage_not_reached); it does not compare positions or drills, and it does not refuse extra footprints. The executable position, drill and plating binding is the agent-ee board_envelope check (criterion mounting-holes/1, selected by id), which requires a scope envelope declaration; agent-ee requirement_scope refuses that declaration for this envelope ("envelope references a fab profile; declare its captured path") because the referenced fab profile bytes are not captured, and its recorded validation (placement-inputs/envelope-validation.json) is outcome unknown with unresolved stackup, finished-thickness and mechanical (AGENTEE-177/179) predicates. Provenance: the envelope is a candidate declaration whose corner-holes obligation leaves drill, plating, inset and coordinates to the generator; these values are not owner-stated or manufacturer limits and do not gate acceptance until sourced (POD-ME-1, POD-AC-7).
- POD-FN-LATERAL-LONGITUDINAL-VERTICAL-ACCELERATION: NOT CHECKED: Firmware quantities, filtering, scaling and publication rates need firmware and bench evidence; no complete executable mapping is declared.
- POD-FN-YAW-ROLL-PITCH-RATE: NOT CHECKED: Firmware quantities, filtering, scaling and publication rates need firmware and bench evidence; no complete executable mapping is declared.
- POD-FN-LEAN-AND-PITCH-ANGLE: NOT CHECKED: Firmware quantities, filtering, scaling and publication rates need firmware and bench evidence; no complete executable mapping is declared.
- POD-FN-FRONT-FORK-TRAVEL: NOT CHECKED: Firmware quantities, filtering, scaling and publication rates need firmware and bench evidence; no complete executable mapping is declared.
- POD-FN-REAR-SHOCK-TRAVEL: NOT CHECKED: Firmware quantities, filtering, scaling and publication rates need firmware and bench evidence; no complete executable mapping is declared.
- POD-FN-FRONT-AND-REAR-BRAKE-PRESSURE: NOT CHECKED: Firmware quantities, filtering, scaling and publication rates need firmware and bench evidence; no complete executable mapping is declared.
- POD-FN-POSITION-SPEED-HEADING-ALTITUDE: NOT CHECKED: Firmware quantities, filtering, scaling and publication rates need firmware and bench evidence; no complete executable mapping is declared.
- POD-IF-CAN1: NOT CHECKED: ISO 11898-2 physical-layer operation at 500 kbit/s, CAN 2.0B timing, required transmit frame rates and received-frame firmware behavior require circuit, timing and built-board evidence. Native net connectivity alone does not establish them; criterion 8 remains a separate bench obligation.
- POD-IF-BLUETOOTH-LE: NOT CHECKED: BLE 5.0 RaceChrono GATT behavior and radio range to a phone in a tank bag or jacket pocket require firmware and installed-board measurements. Module identity and antenna keepout checks do not establish radio performance; criterion 9 remains a separate bench obligation.
- POD-IF-POWER-IN: NOT CHECKED: Operation over 9 V to 16 V, ISO 7637-2 automotive transient survival with the stated 40 V clamp, reverse-polarity survival and the under-2 A power budget require captured protection/power analysis and physical evidence. Wiring and part identity checks alone do not establish survival or operation.
- POD-IF-SENSOR-SUPPLY: NOT CHECKED: Qualify pod-owned 5.00 V +/-1% at the connector across the expanded sensor load; reassess the old 200 mA budget, connector-derived ADC reference and wiring drops. ECU 5V_SENSOR_2 remains unused. Existing topology and local rail monitoring do not establish delivered accuracy or validity.
- POD-IF-ANALOG-INPUTS: NOT CHECKED: Qualify all eight 0-5 V, 12-bit channels at 200 Hz/channel with 16 V protection, optional auxiliary thermistor pull-ups, filtering, settling, calibration and fault interpretation for selected sensors. Retained analysis has unresolved settling and thermistor-loading findings.
- POD-IF-WHEEL-SPEED: NOT CHECKED: Qualify both independent front/rear inputs against selected sensors and tone geometry: electrical levels, frequency, low-speed behavior and faults. Hall candidate circuitry is not sensor selection or qualification; simultaneous Hall/VR support is not required.
- POD-IF-DIGITAL-TIRE-TEMPERATURE: NOT CHECKED: CAN candidate provision does not establish sensor compatibility. Resolve actual front/rear sensor protocol, zones, power, harness length, protection, mounting and update rate, then verify the selected interface.
- POD-IF-STANDALONE-LOGGING: NOT CHECKED: Qualify phone-independent pod and ECU recording, workload/throughput, timestamp source, full-media and power-recovery behavior, and parked wireless retrieval. Report achieved duration; eight hours is a soft target, not a hard pass threshold.
- POD-IF-GNSS-ANTENNA: NOT CHECKED: Qualify active antenna, SMA/U.FL selection, bias/protection and complete RF path. Preserve F.Cu over In1.Cu and antenna placement/cable obligations; calculator geometry or minimum-width checks alone do not establish installed impedance or reception.
- POD-IF-PROGRAMMING-AND-DEBUG: NOT CHECKED: A complete pinout and captured electrical contracts are required before hardware_interface can cover this interface; physical and firmware performance remains unverified.
- POD-IF-HARNESS-CONNECTOR: NOT CHECKED: The 35-cavity endpoint contract is partial evidence only. Complete all signal/power/return/spare allocations, exact black sealed right-angle header and mating contacts/plug, footprint and enclosure verification. Record the gold 1-776163-1 selection against mechanical candidate 776163-1 explicitly.
- POD-CD-MCU-AND-RADIO: NOT CHECKED: Part identity, suitability and allowed deviations need a populated parts manifest and captured contracts; property equality alone cannot prove this decision.
- POD-CD-CAN-TRANSCEIVER: NOT CHECKED: Part identity, suitability and allowed deviations need a populated parts manifest and captured contracts; property equality alone cannot prove this decision.
- POD-CD-IMU: NOT CHECKED: Part identity, suitability and allowed deviations need a populated parts manifest and captured contracts; property equality alone cannot prove this decision.
- POD-CD-GNSS: NOT CHECKED: Part identity, suitability and allowed deviations need a populated parts manifest and captured contracts; property equality alone cannot prove this decision.
- POD-CD-STORAGE: NOT CHECKED: Verify J3 Hirose DM3AT-SF-PEJM5 (LCSC C114218) on the four-bit SDMMC pins with SD_CD on GPIO35 against the storage-microsd source. Datasheet bytes are not captured; its -25 to +85 C catalog rating is below the 105 C criterion and is retained by delegated engineering acceptance D-PCB-12 (POD-TEMP-AUTHORITY, POD-TEMP-ACTUAL-LIMITS). Card-lane fit (D-PCB-13), SD bus length/timing (D-PCB-14), logging integrity and power-loss behavior remain unqualified.
- POD-CD-ANALOG-FRONT-END: NOT CHECKED: Verify exact MCP3208 binding, 3.3 V supply and nominal 2:1 input/reference scaling for every input configuration. Replacing MCP3204 and checking identity alone does not establish analog accuracy or settling.
- POD-CD-POWER: NOT CHECKED: Part identity, suitability and allowed deviations need a populated parts manifest and captured contracts; property equality alone cannot prove this decision.
- POD-CD-HARNESS-CONNECTOR: NOT CHECKED: Resolve the gold 1-776163-1 header deviation from candidate 776163-1, matching 776164-1 plug, exact contacts/cavity plugs, drawing/footprint and assembly procurement. Native identity alone does not qualify mating or enclosure fit.
- POD-CD-BOARD: NOT CHECKED: Part identity, suitability and allowed deviations need a populated parts manifest and captured contracts; property equality alone cannot prove this decision.
- POD-ME-1: NOT CHECKED: Validate actual cowl/enclosure envelope, four corner mounting holes, double-sided clearance, antenna keepout, F.Cu/In1.Cu GNSS path and connector constraints. 90x65 mm is a target, not proven fit; neither 80x50 mm nor the withdrawn 12 mm height is an owner limit. Corner holes H1-H4 are expected placement subjects; their declared positions and drills are stated in POD-ME-HOLES and are not yet executably bound.
- POD-ME-2: NOT CHECKED: Validate IP67 sealing, non-metallic antenna region, only harness/SMA penetrations and rigid board-to-enclosure-to-frame IMU coupling. Potting is not authorized by this map and requires demonstrated necessity.
- POD-ME-3: NOT CHECKED: Qualify -20 to +85 C board ambient and at least 105 C part ratings. The three obligations stay separate: 105 C selection (POD-TEMP-SELECTION), exact part limits (POD-TEMP-ACTUAL-LIMITS, U1, U2, U3, U4, J3; POD-TEMP-UNRATED) and 85 C ambient plus self-heating (POD-TEMP-ENCLOSURE). Retention authority is POD-TEMP-AUTHORITY: owner acceptance for U1, U2, U4; delegated engineering acceptance for U3, J3. Nothing is skipped.
- POD-ME-4: NOT CHECKED: Complete mechanical, mounting, environment and datasheet declarations are not yet captured for an executable predicate.
- POD-ME-5: NOT CHECKED: Complete mechanical, mounting, environment and datasheet declarations are not yet captured for an executable predicate.
- POD-ME-6: NOT CHECKED: Complete mechanical, mounting, environment and datasheet declarations are not yet captured for an executable predicate.
- POD-TE-U1: NOT CHECKED: Owner exception retains U1 ESP32-S3-WROOM-1-N8 (Espressif Systems, LCSC C2913198, RF_Module:ESP32-S3-WROOM-1): manufacturer rating -40 to 85 degC ambient, datasheet sha256 27d71971da07c280c6068d08c74720d1a25b8f20cf8494dc1765bdd28d40d435 page 27 (Recommended operating conditions table, TA operating ambient temperature, 85 degC version). Judged against that rating with owner-accepted -20 to 85 degC (operating-temperature-acceptances.txt sha256 7ca91bc748e3029432e5bb40501c056301429da08119759c612daea7cca8678a, line 1); not exempted. Missing part-bound thermal evidence is unknown, never pass; a captured rating that does not cover the accepted range, or an expected part temperature above the rating, is a defect. Enclosure ambient may not stand in for the part's rated metric without evidence relating them.
- POD-TE-U2: NOT CHECKED: Owner exception retains U2 LSM6DSO32TR (STMicroelectronics, LCSC C1864162, Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y): manufacturer rating -40 to 85 degC operating, datasheet sha256 d1776336f5060da06c4fa4c3aac293372e20cffa4f9d72fe3296b9a56ed6c0b7 page 26 (Mechanical characteristics table, Top operating temperature range). Judged against that rating with owner-accepted -20 to 85 degC (operating-temperature-acceptances.txt sha256 7ca91bc748e3029432e5bb40501c056301429da08119759c612daea7cca8678a, line 2); not exempted. Missing part-bound thermal evidence is unknown, never pass; a captured rating that does not cover the accepted range, or an expected part temperature above the rating, is a defect. Enclosure ambient may not stand in for the part's rated metric without evidence relating them.
- POD-TE-U4: NOT CHECKED: Owner exception retains U4 MCP3208-BI/SL (Microchip Tech, LCSC C2979740, Package_SO:SOIC-16_3.9x9.9mm_P1.27mm): manufacturer rating -40 to 85 degC ambient, datasheet sha256 89bc1e17c35e2bb1c7b8fbf0b775b3729ce9fe4d27f7e9c052a774757afc0c20 page 37 (Product identification system, temperature range I (industrial)). Judged against that rating with owner-accepted -20 to 85 degC (operating-temperature-acceptances.txt sha256 7ca91bc748e3029432e5bb40501c056301429da08119759c612daea7cca8678a, line 3); not exempted. Missing part-bound thermal evidence is unknown, never pass; a captured rating that does not cover the accepted range, or an expected part temperature above the rating, is a defect. Enclosure ambient may not stand in for the part's rated metric without evidence relating them.
- POD-PI-1: NOT CHECKED: Coordinate actual pulse voltage/duration/source impedance, reverse-polarity protection, TVS/disconnect, capacitor ratings and regulator absolute maxima; nominal TVS voltage alone is insufficient.
- POD-PI-2: NOT CHECKED: Define and validate separate continuous operation, dip ride-through and controlled-reset regions for both electronics and powered sensors; running MCU is not sensor validity.
- POD-PI-3: NOT CHECKED: Qualify filter/damping stability over load and radio/storage bursts; measure connector, logic, sensor and reference ripple against stability and acquisition error budgets.
- POD-PI-4: NOT CHECKED: Qualify independent input/rail monitoring, supervisor/reset and hysteresis, recorded faults and invalidation of affected samples; local U18 sensing is not universal sensor validity.
- POD-PI-5: NOT CHECKED: Establish bounded log loss, recovery/restart and hold-up using measured worst-case consumption and storage completion time. Capacitor presence does not demonstrate safe flush or indefinite ride-through.
- POD-PI-6: NOT CHECKED: Recalculate expanded rail current and thermal limits, protected branches and sensor-short effects. Pilot 300 mA regulator/200 mA aggregate budget is not expanded-load qualification.
- POD-ED-1: NOT CHECKED: Complete joint GPIO/SPI/bus/35-pin allocation across analog, wheel, tire, storage, IMU/GNSS/CAN/debug; preserve existing ECU connector/frame contracts and allocate new messages separately.
- POD-ED-2: NOT CHECKED: Select wheel sensors/tone geometry and resolve voltage/current, maximum frequency, low-speed behavior and conditioning. Hall candidate is not a selected sensor; dual Hall/VR support is not required.
- POD-ED-3: NOT CHECKED: Select and qualify tire sensor protocol, mounting/FOV, zones, harness length and update rate. CAN provision alone is not compatibility.
- POD-ED-4: NOT CHECKED: Resolve logging duration/workload, format, timestamps, retrieval, endurance and power-loss behavior while retaining BLE OTA and sealed enclosure. Eight hours remains soft.
- POD-ED-5: NOT CHECKED: Close expanded power/thermal budgets for sensor faults and storage/radio peaks, rail monitoring, sensor-supply fault detection and feasible open/short diagnostics.
- POD-ED-6: NOT CHECKED: Validate full connector courtyard, antenna keepouts, holes and enclosure fit. Start at 90x65 mm without treating it as qualified; TE overall width is 76.9 mm, not 63.4 mm.
- POD-AC-1: NOT CHECKED: Complete the full connector/MCU/external-destination contract and verify against the expanded schematic. Existing 35-cavity/15-GPIO evidence is partial; satisfy every interface row separately, including firmware and physical behavior.
- POD-AC-2: NOT CHECKED: Compare every component-decision row against the complete expanded selected-parts manifest and retain reasoned deviations. Existing bindings are identity evidence, not complete suitability or deviation closure.
- POD-AC-4: NOT CHECKED: The registered kicad_happy_severity_gate requires a captured analyzer pin, policy and warning dispositions; those pod inputs are not supplied by this accounting fixture.
- POD-AC-5: NOT CHECKED: Capture day-of-generation raw JLC stock responses with LCSC IDs, hashes and UTC times for every assembly BOM line. Declare not_assembled hand-fit exclusions and purchase-source deviations for unstocked/unassembled items; gold J1 zero stock remains unresolved.
- POD-AC-7: NOT CHECKED: board_envelope, placement and dfa_dft need complete mechanical declarations; silkscreen axes and antenna datasheet keepout coverage are not declared here. Mounting-hole presence is a placement subject; hole position and drill remain NOT CHECKED (POD-ME-HOLES).
- POD-AC-8: BENCH REQUIRED: CAN frame rates within 5% and ECU .mlg channel logging on a built pod.; procedure: Connect the built pod and ECU to a bench CAN bus; retain timestamped traffic for all six specified frame IDs, compare rates with the spec, and retain an ECU .mlg file showing lean, brake pressure and suspension travel.
- POD-AC-9: BENCH REQUIRED: RaceChrono Pro BLE pairing and combined ECU RPM, pod lean and 25 Hz GPS speed.; procedure: Pair RaceChrono Pro with the built pod over BLE; retain the app session showing ECU RPM alongside pod lean and GPS speed and measure the GPS update rate against 25 Hz.
- POD-AC-10: BENCH REQUIRED: Eight-channel range, accuracy and acquisition plus selected wheel speed/fault behavior under concurrent operation.; procedure: Declare selected sensor ranges, error and sampling bounds; exercise all eight analog channels while wheel capture, IMU/GNSS, CAN, BLE and logging run. Retain timestamped acquisition/error results and front/rear wheel speed and fault tests over the declared range.
- POD-AC-11: BENCH REQUIRED: Phone-independent logging duration/integrity and actual digital tire sensor/harness/zone coverage.; procedure: Declare workload and achieved duration against the soft eight-hour target; record without a phone, test full media and power interruption/restart, and verify retained data integrity and parked wireless retrieval. Exercise the selected tire sensors over the declared harness and record actual zones and updates.
- POD-PU-P1: NOT CHECKED: The real-board generator objective and pre-generation decision closure remain incomplete; candidate implementation does not establish resolved or qualified decisions.
- POD-FN-P1: NOT CHECKED: Qualify CAN1/BLE publication and ECU frame relay, installation and absence of control outputs. Native connectivity does not establish firmware behavior.
- POD-FN-P2: NOT CHECKED: Verify subscription-filtered ECU relay, all eight 12-bit inputs, own-rail reference, separate ratiometric and absolute-voltage error treatment, and no use of ECU 5V_SENSOR_2.
- POD-IF-P1: NOT CHECKED: Preserve canonical ECU frame layouts/scaling/RaceChrono equations and harness assignments; capture exact reference-document versions into the eventual full interface contract.
- POD-CD-P1: NOT CHECKED: Verify composed prior parts and capture remaining LCSC selections and evidence. Historical reuse does not qualify the expanded circuit.
- POD-ME-P1: NOT CHECKED: Tail-cowl installation, sealing, vibration and service assumptions require physical qualification.
- POD-TE-P1: NOT CHECKED: The owner approval retains U1, U2 and U4 below the 105 C criterion with enclosure thermal validation required. Per the owner correction of 2026-10-20 each is tested against its actual limit, not exempted; see POD-TEMP-ACTUAL-LIMITS and POD-TEMP-ENCLOSURE.
- POD-TE-P2: NOT CHECKED: Superseded mechanism: operating-temperature-exemptions.txt (sha256 45b9ba0af879fabd7f33b99c0fa83e61a29fba2ec338bfa5cdf95e1484cd9236) is retained for provenance only and is not an input to this scope. The AGENTEE-310 reduced_acceptance input is operating-temperature-acceptances.txt sha256 7ca91bc748e3029432e5bb40501c056301429da08119759c612daea7cca8678a, lines 1-3; capture it with each exact part binding when the assembly_readiness check is integrated. No exemption is carried.
- POD-TE-P3: NOT CHECKED: Enclosure thermal validation must measure the selected components under worst-case supply, sensor load, radio and logging activity, including self-heating, against each part's own manufacturer limit (POD-TEMP-ACTUAL-LIMITS). Neither the +85 C board ambient envelope nor adequate margin is qualified. Disposition insufficient thermal margin before release.
- POD-TE-P4: NOT CHECKED: The described exclusion of U1, U2 and U4 from the operating-temperature predicate is superseded by AGENTEE-310 reduced_acceptance: no reference is excluded, and each is compared with its own rating. This scope declares no assembly predicate yet; POD-TEMP-ACTUAL-LIMITS remains NOT CHECKED, never exempt, and a future passing predicate does not discharge enclosure thermal validation.
- POD-PI-P1: NOT CHECKED: Redesign and qualify power for brownouts, ripple and expanded load. SV650 behavior at 2500 rpm remains an unmeasured lead, not an established defect or input waveform.
- POD-PI-P2: BENCH REQUIRED: Power-integrity and actual-bike disturbance qualification.; procedure: Programmable dips/recovery, swept ripple, sensor shorts and load steps during acquisition/logging; actual harness waveform capture at 2500 rpm, across operation and starting, followed by bench replay. Keep simulation, injected and on-bike evidence distinct; establish actual amplitudes/durations.
- POD-ED-P1: NOT CHECKED: Accepted capabilities do not settle all implementation decisions; close each pre-layout decision with evidence rather than silently choosing.
- POD-ED-P3: NOT CHECKED: Regenerate expanded candidate and repeat placement/routing/review; v9 pilot schematic, PCB, BOM, IO map and compiled contract are historical evidence only.
- POD-AC-P1: NOT CHECKED: All eleven criteria require evidence. File checks alone do not close AC6 owner DFM/preview or AC8-11 built-board obligations; this scope has incomplete acceptance coverage.
- Composed by production-capture/pipeline.py: assembly_readiness over assembly-stock/catalog.json (the captured stock named in scope-composition.json, as_of 2026-10-22T10:50:06.618194+00:00). It carries the binding-fill --ratings receipt into rating_provenance. Of 81 BOM LCSC ids: in_stock 80, zero_stock 1; 0 are older than 24 hours at composition (2026-10-23T00:26:05.047052+00:00) and the check re-grades age at its own run. The J1 owner_hand_fit deviation is cited by hand_fit_policy: the unchanged POD-AC-5 owner statement (REQUIREMENTS.md line 139, "the AMPSEAL header") with its category selection chain (D-PCB-10, the C596198 part record and both manifests). That is an assembly disposition only, not mating, enclosure or purchase qualification. Captured stock and bindings are not assembly qualification. POD-AC-5 remains NOT CHECKED.
- POD-DERIVED-BLOCK-PRE-6V3-BOARD-REGION-COPPER-NATIVE-CHECK: NOT CHECKED (unresolved; composition/block-obligations.json sha256 22ef180ae719d1e409b73172d19eda3d8882e317a0864eeb1ba0f66623874851): The pre-6v3 library entry (U5) was refused by the released engine: copper_unknown: board-region copper application and native checking are unavailable; a placement-only candidate cannot materialize this entry. Its board-region copper application and the native checks over it are not executed; the generic candidate is geometry only and closes neither. Generic packing is geometry only. A real placement repacks this block against its own emitted board; it inherits neither the iter8n seed board identity nor any qualification from this candidate.
- POD-DERIVED-BLOCK-PRE-6V3-WITNESS-POSE-EQUIVALENCE: NOT CHECKED (unresolved; composition/block-obligations.json sha256 22ef180ae719d1e409b73172d19eda3d8882e317a0864eeb1ba0f66623874851): Witness-pose equivalence between the generic pre-6v3 candidate and the library entry witness is not established; the generic pose is not the library pose. Generic packing is geometry only. A real placement repacks this block against its own emitted board; it inherits neither the iter8n seed board identity nor any qualification from this candidate.
- POD-DERIVED-BLOCK-BUCK-3V3-BOARD-REGION-COPPER-NATIVE-CHECK: NOT CHECKED (unresolved; composition/block-obligations.json sha256 22ef180ae719d1e409b73172d19eda3d8882e317a0864eeb1ba0f66623874851): The buck-3v3 library entry (U7) was refused by the released engine: copper_unknown: board-region copper application and native checking are unavailable; a placement-only candidate cannot materialize this entry. Its board-region copper application and the native checks over it are not executed; the generic candidate is geometry only and closes neither. Generic packing is geometry only. A real placement repacks this block against its own emitted board; it inherits neither the iter8n seed board identity nor any qualification from this candidate.
- POD-DERIVED-BLOCK-BUCK-3V3-WITNESS-POSE-EQUIVALENCE: NOT CHECKED (unresolved; composition/block-obligations.json sha256 22ef180ae719d1e409b73172d19eda3d8882e317a0864eeb1ba0f66623874851): Witness-pose equivalence between the generic buck-3v3 candidate and the library entry witness is not established; the generic pose is not the library pose. Generic packing is geometry only. A real placement repacks this block against its own emitted board; it inherits neither the iter8n seed board identity nor any qualification from this candidate.
- Composed by production-capture/pipeline.py: the scope envelope, one check per derived envelope obligation, the electrical-locality check and the parts membership check. The five generic envelope obligations are staged under agent-ee source contract telemetry-pod-expanded/1: candidate generation is admitted and every open qualification item (enclosure and harness fit among them, open design deliverables) keeps blocking final acceptance. Structural envelope validity is not mechanical qualification.
- Composed by production-capture/pipeline.py: the plan selects requirement_source telemetry-pod-rev3, the pinned Revision 3 capture (requirements-source/spec.md sha256 e71dcca744f4b520fc4698402202d7d9efff2d316f8ad3c5eb6403cdf9d036c6, requirements-source/spec-record.json sha256 1d978fc1ddeddfe64a6900a719c437dabb31b2999feb258265b0fbad1ab4820b). The scope is compiled from the microSD spec (requirements-map/spec.md sha256 0f52e0ae17f62be348525a5cfab2d9ea5c823df7bc5f580700ed7dd10cbcaae7), which equals it in every requirement and prose entry and adds only the POD-CD-STORAGE decision row; the microSD spec is not a pinned source. Carrying every criterion is not acceptance.
- Final qualification open in the captured envelope baseline; the outcome stays incomplete: R-envelope-expanded-pod-microsd-production-obligation-corner-holes staged (hole-authority, fabricated-holes); R-envelope-expanded-pod-microsd-production-obligation-height staged (candidate-heights, cowl-fit, underside-fit, connector-fit, mating-plug-fit, harness-fit); R-envelope-expanded-pod-microsd-production-obligation-harness-edge staged (panel-cutout, mating-plug, retention, thickness-tolerance, harness-clearance); R-envelope-expanded-pod-microsd-production-obligation-antenna staged (feed-point-side, housing-pocket, nearby-metal, support, rf-performance); R-envelope-expanded-pod-microsd-production-obligation-imu-separation staged (placement-assessment, vibration-coupling)
- Checks-only run: independent agent reviews and adjudication not performed.

This result applies only to the captured candidate and declared criteria. Prototype and bench
validation, including operating conditions omitted from this review, remain necessary.
