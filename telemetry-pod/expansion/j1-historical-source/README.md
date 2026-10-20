# J1 retained drawing import

The AGENTEE-306 candidate imports the exact retained TE 776163 K1 drawing
and its original source note. The canonical C596198 record replays against
the captured supplier response and matches J1's existing intent identity,
datasheet URL and PDF hash. No native design or source binding changed.

The acquisition is explicitly historical. Its final redirect URL and fetch
time are null; its recorded capture time is retained verbatim. Supplier stock
is the historical value zero. Source closure does not establish availability,
electrical or mechanical suitability, assembly acceptance, or release approval.
AGENTEE-271's release policy question remains open.

Together with the 315 instances covered by `canonical-parts` and
`source-revision`, this supplies records for all 316 purchased instances.
It does not yet add J1 to the separate `parts-manifest` packet. That packet
still has 326 declarations and its full native comparison still refuses
the legacy probe marker before comparison.

Software is pinned in `software.json` to an isolated archive of unreleased
agent-ee commit 5140939bf0d2b7a323cc30f7e3876b9032d991db.
Replay from any checkout of this repository:

```sh
PYTHONPATH=/path/to/exact-agent-ee-archive/src \
  python3 telemetry-pod/expansion/j1-historical-source/build.py --verify
```

Replay creates a fresh temporary acquisition, compares all three output files
byte for byte, qualifies the retained record dependencies and compares the
record to J1's intent. It performs no network acquisition.
