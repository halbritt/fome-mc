# J2 producer adoption (AGENTEE-485 J2b)

The producer adopts the retained Amphenol RF 132134 external record and the
Agentee494 manufacturer-pattern footprint. Its supplier identity is NO_LCSC and
stock is null. The previous Molex C841205 is historical input, not the adopted
part. No catalog observation was deleted or fabricated.

J2 keeps component id connector/J2, native UUID prefix 18c6ebf4 and its two
symbol terminals: /POD_GNSS_RF pin 1, /GND pin 2. The production ledger retains
the prior component declaration. Published drills are 1.5 mm centre and four
1.7 mm grounds on a 5.08 mm square, from the retained 132134 Rev C sheet 3;
source bytes and hashes remain in j2-historical-source and agentee-494-j2.

The writer chooses front-side anchor (80,28) mm, zero rotation and from_top
insertion. This is an engineering pose, not an owner-specified anchor or final
placement approval. It puts the published footprint inside the right board
edge. The RF corridor follows U3's historical RF endpoint (77.5,29.1) to J2
pad 1 (80,28); its 1.5 mm margin is class: default, advisory. The associated
native inner-layer rule areas keep their tracks/vias prohibitions. The producer
records the original logical identities 460352a8 and 93d1ddf1 and maps them to
the UUIDs the existing scaffold derives from the changed envelope hash.
Actual routed connectivity, return fill and neighbouring bodies remain unqualified.

J1 retains its existing POD-AC-5 selection chain. J2 separately cites the
verbatim ccbe2294 owner words; composition/j2-hand-fit-mapping.json labels the
reference/MPN/context association as engineering. The source note's subject and
chief ruling are not owner quotations. Both parts carry not_assembled in native
properties, for the existing BOM/CPL exclusion rule.

Alternatives were retaining the wrong Molex identity or retaining the old
edge-launch pose; neither represents this vertical through-hole part. Reverse
this change by reverting the producer and regenerated composition together,
never by editing the emitted native files. This slice is diagnostic: C1 remains
REQUIRED NOT_RUN and no campaign, routing, receipt or retention is accepted.
