# Historical repository-snapshot recovery (AGENTEE-485 J2c)

The active historical retention did not record a fome-mc repository commit for its
repository-path snapshots. Its original `MANIFEST.json`, `prepared-tree.json` and
`SHA256SUMS` remain byte unchanged. Looking those paths up in the current working
tree made historical verification fail after valid composition changes.

`retain.py --repair-repository-snapshots` recovered each required SHA-256 from git
history into `emission-8ab3b0b9-agentee485/blobs/<sha256>`. `RECOVERY.json` records
the matching git blob and a recovery location for every digest. A recovery commit
is a location where matching bytes were found, **not** a claim that the original
retention ran at that commit. All recovered bytes are opaque and unmodified.
Missing matches refuse recovery; no live-path fallback or verification exclusion
is used.

Both `--check` and `--materialize-prepared` use `resolve_snapshot`, which checks
the requested historical SHA-256 before returning bytes. Recorded immutable
commits are supported directly. Legacy snapshots require their recovered blob;
missing or tampered blobs refuse both operations. The prepared-tree file itself
must still match its historical manifest. Future retentions store immutable blobs
at creation time, avoiding new commit-less repository-path dependencies.

The historical counts remain 428 retained files, 576 design inputs, 8 installed
files and 4,336 prepared files. This repair store contains 570 recovered blobs,
a recovery index and a separate checksum manifest; those are additional files,
counted separately. The parent README is documentation outside that store.

Reversal: revert the J2c code, tests and separate repair directory together. The
original historical retention requires no restoration because it was not edited.
No new production retention or receipt is accepted by this repair.
