# Research brief: routability-driven placement and congestion-aware routing for the pod toolchain

Prepared 2026-10-21 by agent-499 for a research agent. Self-contained; no access to the
repositories is needed.

## Context (read first)

We build small automotive PCBs with an autonomous toolchain: **agent-ee** (Python) places
parts, **kicad-route** (Python plus an owned grid router derived from KRT 0.23.1, with
Freerouting as a second backend) routes them, and KiCad 10 grades the result with its own
DRC. The current board: 90 × 65 mm, 4 layers (two signal layers, GND plane on In1, +3V3
plane on In2), 309 footprints, 235 nets, 0.2 mm tracks and clearances, JLCPCB fabrication.

Placement is two-level: 17–19 functional blocks are each packed in isolation by a
deterministic first-fit search with backjumping (objective: pad-to-pad locality for
decoupling, minimum block area), then arranged as rigid macros with residual parts packed
around them. Routing is a single-pass grid router with rip-up disabled by default, run in
"campaigns" that re-order nets (hard nets first) across rounds, graded against KiCad DRC
after every step.

## Measured problem

Placement completes in 2–3 minutes and passes every electrical locality bound, but routing
plateaus at 203 of 235 nets: a second run with twice the time budget reproduces the
identical result, and re-ordering nets in later rounds makes it worse (59–64 open). The 32
open nets are short intra-block nets (eFuse setting resistors packed at 0.26 mm courtyard
gaps, which cannot pass a 0.2 mm track) and a few long buses. Widening the packing gap
globally to 0.6 mm fails because fixed geometry (a connector 0.36 mm from mounting holes,
an IMU keep-out ring, an RF corridor at 0.16 mm) cannot honour it. The packer has no notion
of routing demand; the router has no notion of congestion history.

## Questions to answer, with citations

Cite papers, theses, open-source repositories (name the specific file or algorithm) and
vendor documentation.

1. **Routability-driven placement.** What are the established cheap congestion estimators
   used during placement (RUDY and its variants, probabilistic/pin-density maps,
   Steiner-tree-based demand, FastRoute-style global-route-in-the-loop), how are they
   integrated into a placer's objective or legalization step, and which of them apply to a
   packing-style (non-analytical) placer with rigid macros? What do PCB-specific placers
   (open-source or published: DeepPCB, Horizon, the Autodesk/InstaDeep and Google-style RL
   placers, academic PCB placement papers 2018–2026) do differently from IC placers given
   through-hole pins, two-sided boards and plane layers?
2. **Channel reservation around dense macros.** How do IC and PCB flows decide how much
   whitespace to leave around a macro or a tight cluster (halo/keep-out sizing, channel
   width from pin count and track pitch, routing-track supply versus demand rules)? Give
   the concrete formulas or heuristics, not just names.
3. **Congestion-aware detailed routing.** Explain negotiated-congestion routing
   (PathFinder and its descendants) and how modern open routers (FastRoute, NCTU-GR, CUGR,
   SPRoute, TritonRoute / OpenROAD's detailed router, Freerouting's own rip-up loop)
   structure global routing, rip-up and reroute, and history costs so that the result
   converges instead of plateauing. Which of these ideas transfer to a grid router on a
   4-layer PCB whose two plane layers may carry short tracks, and what is the minimal
   change to a single-pass router that gives most of the benefit (for example, iterative
   reroute of open nets with a congestion history cost on occupied cells)?
4. **Escape and fanout.** Prior art for escape routing from connector pin fields and
   fine-pitch packages (ordered escape, BGA and connector escape routing papers, standard
   fanout patterns) and how routers decide escape direction before global routing.
5. **Benchmarks and evaluation.** What open PCB routing or placement benchmarks or
   datasets exist, if any, that we could use to measure improvements, and how do published
   works report routability (overflow, open nets, DRC counts) so our numbers are
   comparable?

## Deliverable

A written brief, 3–6 pages equivalent, organised by the five questions. Each section ends
with a short "what this would mean for our tools" paragraph naming the smallest concrete
change that captures most of the benefit, ranked by expected payoff against implementation
cost. Cite every claim; prefer primary sources (papers, repositories) over blog posts; flag
anything you could not verify. Do not propose replacing the toolchain with a commercial
router; the question is what to borrow.
