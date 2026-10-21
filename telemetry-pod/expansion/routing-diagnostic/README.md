# Routing diagnostic on the frozen placement (not an adopted board)

First end-to-end routing evidence for the expanded telemetry pod, produced with
kicad-route (checkout fcea559, KRT 0.23.1 owned source, Freerouting 2.5.0, KiCad 10.0.7)
on the frozen 17-group diagnostic placement `79cc1310…` with decision D-PCB-1 applied
(enlarged thermal vias, scoped fine-pitch rule, cited board setup from
`../design-rules/`; 4 copper layers, no zones). The placement is unqualified (13 declared
pad-locality exceedances, see `../electrical-locality/pad-obligations/`), so the candidate
is evidence about the tooling and the board's routability, never a design candidate.

## Input readiness

`blocked-by-input.json` (`kicad-route blocked --board`, heuristic): 487 of 499
connections unobstructed on straight or L corridors; the 12 obstructed ones sit at J1,
U12, U7, U6, U1 and U14.

## Attempts

| Attempt | Setting | Outcome |
| --- | --- | --- |
| KRT, 600 s | defaults | main pass routed all but about 10 nets, then KRT's net-rescue phase ignored the stop file and was killed; no candidate (`failed-attempts/`) |
| Freerouting, 1500 s, stall 300 s | defaults | killed by the stall watchdog while actively routing: the headless log is silent between stages (`failed-attempts/`) |
| Freerouting, 1500 s, stall off | defaults | timed out with a candidate: 110 of 194 nets, 1976 tracks, 154 vias, 84 nets open; receipts under `patched2/cited-freerouting-nostall/`; `compare-krt-freerouting.txt` |
| **KRT, 1800 s, net rescue and plane finalize off** | `--backend-env KICAD_NET_RESCUE=0 KICAD_PLANE_FINALIZE=0` | candidate in 1014 s: 142 of 194 nets routed, 4656 tracks, 404 vias, 5.99 m of track; 52 nets open; receipts under `patched2/cited-krt-norescue/` |

The published receipts are kicad-route's verdict for that run: routing INCOMPLETE,
validation FAIL with 430 new findings. 398 of those were via-diameter and annular-width
findings against the board setup of the time (0.70 mm / 0.20 mm), which contradicted the
0.60 / 0.30 mm net-class via the router used; `../design-rules/` has since corrected the
via minimum to JLCPCB's published via capability (0.50 mm / 0.10 mm). `krt-candidate-
regrade-drc.json` is the same candidate under the corrected project: 32 new findings, all
`track_dangling` stubs of the unfinished nets, no copper clearance or geometry finding,
and 101 unconnected items left of 499. Preservation checks all PASS except
`net_completion`, which lists the nets the router left partly connected.

## What the open nets say

- **eMMC bus** (`EMMC_CLK/CMD/DAT*/DS/VCC/VDDi`): U14 is a 0.5 mm-pitch BGA-153 with ten
  connected interior balls; a 0.60 mm via cannot dogbone between them. Open design item
  D-PCB-3 in `../design-rules/constraints.json` (BGA net class on JLCPCB's published BGA
  allowances, or filled via-in-pad).
- **Sensor-power control nets** (`SENSOR_POWER_*_DVDT/ILIM/OVP/UVLO`, 16 nets) and several
  analog lines (`ADC_AIN*`, `AFE_*`): blocked mainly by the router's own earlier copper
  (`blocked_by` top entries are new tracks of the diagnostic ADC nets on the inner layers),
  which is the hard-nets-first case for `kicad-route campaign`.
- `GND`, `+3V3`, `PRE_6V3`: plane nets with no zones in this diagnostic; plane planning
  (`kicad-route planes`) is a separate step once the placement is qualified.

## Tool behaviour worth knowing

KRT's net-rescue phase ignores the stop file and can overrun the budget by minutes; run
pod-scale attempts with `KICAD_NET_RESCUE=0` or a budget with headroom. Freerouting's
headless log is silent between stages, so `--stall` must be at least the budget.

## Campaign on the cluster-anchored iteration-1 placement (rejected placement; diagnostic)

`kicad-route campaign --backend krt --rounds 2 --budget 900 --total-budget 3300`, net rescue
and plane finalize off, on the cluster-anchored iteration-1 candidate under the cited
rules with patched thermal vias (`campaign-iter1-anchored.json`, receipts under
`cited/anchored-krt-campaign-r0/`): best chain is round 0 (full pass, 372 s): 145 of 194
nets routed, 89 unconnected items left, 4352 tracks, 381 vias, **1 new finding (a
dangling-stub warning)**, net_completion FAIL for the 31 unfinished nets. The two
hard-nets-first rounds finished worse (73 and 69 nets open), so net ordering is not the
limiter on this board. The open set is the same as before: eMMC bus (D-PCB-3), the
TPS26625 control nets, and the plane nets GND / +3V3 / PRE_6V3 without zones (D-PCB-5).

## Planed iteration-2 placement (D-PCB-5 planes, then KRT)

`kicad-route planes --plan ../design-rules/planes.json` on the via-patched iteration-2
candidate filled In1.Cu GND and In2.Cu +3V3 over the board outline (`planes-iter2.json`;
exit 3 = production success that still needs the full electrical checks, as documented).
`kicad-route run --backend krt --budget 1500`, net rescue off, on the planed board
(`candidate/planed-krt/`): 143 of 194 nets, 3875 tracks, 407 vias, **6 new findings, all
dangling-stub warnings**, net_completion FAIL for 32 nets. With the planes, 305 nets were
already connected in the input (GND and +3V3 pads reach the pours). The open set is the
same families as before and is addressed by iteration 3's placement (U14 under the MCU,
L3 in the RF corridor).

## Planed iteration-3 placement (reviewed candidate)

Same plane plan and `kicad-route run --backend krt --budget 1500` (net rescue off) on the
via-patched iteration-3 candidate (`iteration-3/`): 136 of 194 nets, 3918 tracks, 390
vias, **5 new findings, all dangling-stub warnings**, net_completion FAIL for 39 nets. The
blocked-by receipt names the router's own new tracks on **In1.Cu, the GND plane layer**, as
the top blockers: kicad-route lets the backend route signals on the plane layers, which
breaks the reference under the GNSS line and crowds the planes. Decision D-PCB-7 in
`../design-rules/`: In1.Cu and In2.Cu carry no tracks (rule areas, no-tracks, whole board;
vias still pass through). The eMMC bus (all `EMMC_*` nets) is open again with U14 under the
MCU: with 0.24 mm balls at 0.5 mm pitch and the default 0.20 mm track / 0.20 mm clearance,
no trace can pass between balls, so rows B and C cannot escape; D-PCB-3 must be decided from
the FEMDME008G land pattern (pad size, NSMD) and a BGA net class before routing can finish.

## D-PCB-3 experiment: eMMC escape on iteration 3 (`iteration-3/bga-exp/`)

Planed iteration-3 board plus D-PCB-3 v2 (0.22 mm balls, BGA_EMMC class 0.09/0.09 mm, B.Cu
pours under U14), D-PCB-6 (RF reference keep-out) and D-PCB-7 (no tracks on the plane
layers). `kicad-route run --nets '/EMMC_*' --budget 600`, net rescue off: **routing
COMPLETE for every eMMC net**, 126 tracks, 10 vias, 151 mm, **0 new DRC violations**. The
only failure is pour integrity: the GND pour under U14 collapsed to 1.1 mm² in 11 islands,
so the five interior GND balls are not reachable by a pour between 0.22 mm balls; the
EMMC_VCC_3V3 interior balls are connected. Decision text in `../design-rules/constraints.json`
(D-PCB-3): filled via-in-pad for those five balls is the remaining spec-compliant answer and
an owner cost decision.

## Full pass on the D-PCB-3 board with both inner layers closed (`iteration-3/bga-exp/bg2-full-nofinalize/`)

`kicad-route run --backend builtin --budget 1800`, net rescue and plane finalize off (a
first 1500 s attempt was killed in the engine's refill recheck, which ignores the stop
file): 114 of 194 nets, 4335 tracks, 344 vias, 80 nets open, 77 new findings = 64
`items_not_allowed` (46 In1.Cu and 18 In2.Cu layer-change stubs inside the no-tracks rule
areas, 3.8 mm total; the builtin engine does not honour inner-layer rule areas, reported
to the kicad-route owner) + 13 dangling stubs. Two signal layers are too few for this
board; D-PCB-7 v2 keeps only In1.Cu closed and opens In2.Cu to signals.

## Full pass with D-PCB-7 v2 (In1 closed, In2 open) (`iteration-3/bga-exp/bg3-in2-open/`)

Same settings on `bg3`: 136 of 194 nets, 4413 tracks, 401 vias (939 mm on In2.Cu, 1.4 mm
of stubs on In1.Cu), 58 nets open, 60 new findings = 35 `items_not_allowed` (In1 stubs,
the same engine limitation) + 25 dangling stubs; copper clearance findings 0.

## Where routing stands after six attempts on the cluster-anchored placements

| Input | Nets routed | Open | New copper findings |
| --- | ---: | ---: | --- |
| iteration 1, no planes, 4 layers routable | 145 | 49 | 1 dangling |
| iteration 2, planes, 4 layers routable | 143 | 51 | 6 dangling |
| iteration 3, planes, 4 layers routable | 136 | 58 | 5 dangling |
| iteration 3 + D-PCB-3/6/7, eMMC nets only | all eMMC | 0 | 0 |
| iteration 3 + D-PCB-3/6/7, In1+In2 closed | 114 | 80 | 64 rule-area stubs |
| iteration 3 + D-PCB-3/6/7 v2, In1 closed | 136 | 58 | 35 rule-area stubs |
| **iteration 5 (microSD source, eMMC gone), planes, campaign best chain r1** | **182** | **53** | 0 DRC; pour integrity 1 spoke below minimum |

Iteration 5 on the microSD source (`iteration-5/`, kicad-route 784fd6d builtin, `campaign
--rounds 2 --budget 900 --total-budget 3300`, net rescue and plane finalize off, planes from
`../design-rules/planes.json`) moved the plateau: the best chain routes 182 of 235 nets graded
against the planed input (53 open; the r1-rest step alone leaves 32 of its scope open), 1602
new tracks, 251 vias, 3.01 m, **0 new DRC violations**; the only validation failure is
`pour_integrity` (one zone-connected pad below 2 spokes, both planes −8 % area). The open set
is now AFE dividers and ADC inputs, the DIAG I2C pair and U29 inputs, the GNSS UART/PPS,
SD_DAT0/DAT2/CD, TIRE_CAN control lines, wheel captures, PRE_6V3, +5V_CAN and SENSOR_REF_2V5.

A continuation campaign from that best candidate with `--protect human` (builtin may rip up
its own copper; 2 rounds, 1200 s each, 4200 s total; receipts not published) did not improve
it: graded against its input the chains leave 51-52 nets open, disconnect 5-15 nets that were
complete (`net_completion` FAIL) and add 1-4 dangling stubs. The open set is therefore a
placement/density limit of this candidate for the builtin engine, not a budget limit.

Before iteration 5 the plateau was 136-145 nets with zero clearance violations. The open set is stable:
analog front-end and ADC lines, the diagnostic I2C pair, the SPI bus, the TPS26625
control nets and the plane nets' last pads. Net ordering (campaign) and layer policy do
not move it; the remaining levers are placement (the two-level block placer,
AGENTEE-339/340, with the allocation in `../blocks/`), the builtin engine honouring rule
areas (reported to the kicad-route owner), and the eMMC interior-ground via-in-pad
decision (D-PCB-3).

KRT is the stronger backend on this board (142 versus 110 nets in comparable budgets); the
next routing step is `kicad-route campaign --backend krt` with `KICAD_NET_RESCUE=0` on a
qualified placement, after plane planning.

No file outside this directory was changed; no candidate board is committed.
