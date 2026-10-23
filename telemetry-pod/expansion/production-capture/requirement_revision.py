"""AGENTEE-488c (agent-529 38f1ac7e v1 item 1): the EXPLICIT accepted revision delta between the pinned historical
telemetry-pod-rev3 registry source (kept unchanged, exact identity) and the current microSD spec record.

Admitted, and nothing else:
- the already-adopted POD-CD-STORAGE addition (non-acceptance kind);
- the EXACT accepted POD-ME-1 height-ESTIMATE correction (owner-relayed a13a1ba8@2, accepted AGENTEE-486 / 27c51f73):
  text sha256 d865a76d... -> 09c89ce3..., with id/kind/section/cells unchanged. This is not a measured 90 mm cap and
  not a new owner measurement request, and the same ID does NOT transfer the old acceptance.
Bound to the accepted REQUIREMENTS.md and the recaptured spec record. Any other added/removed/changed row, any prose
or acceptance-set change, a stale pin, or a different text under the allowed ID refuses."""

ACCEPTED_SPEC_SHA256 = 'dd6555f706d163709bccb3417d8c366c38de7d603fca8894d0c4a95a58928208'
ACCEPTED_RECORD_SHA256 = '21288e0126995c9e25f12de759a17ea6fe8200a64dc7c5eeee0f258b30a23ea5'
ALLOWED_ADDED = {'POD-CD-STORAGE'}
ALLOWED_CHANGED = {'POD-ME-1': {'before_text_sha256': 'd865a76d53f44c1c275964a9dbcd98585cf70d6ac68af5e44e66767713c3b9bb',
                                'after_text_sha256': '09c89ce3dad63794da060b1d81d8aff112fc199ce8ad06ed144ad3430590fc36',
                                'unchanged_fields': ('id', 'kind', 'section', 'cells'),
                                'authority': 'owner-relayed a13a1ba8@2; accepted AGENTEE-486 / 27c51f73 (height estimate)'}}


def problems(pinned, current, spec_sha256, record_sha256):
    """Refusal reasons ([] = admitted). pinned/current are verified agent-ee.spec-record/1 documents."""
    import hashlib
    out = []
    if spec_sha256 != ACCEPTED_SPEC_SHA256:
        out.append(f'current spec sha256 {spec_sha256} is not the accepted REQUIREMENTS.md {ACCEPTED_SPEC_SHA256}')
    if record_sha256 != ACCEPTED_RECORD_SHA256:
        out.append(f'current spec record sha256 {record_sha256} is not the accepted recapture {ACCEPTED_RECORD_SHA256}')
    norm = lambda doc: {r['id']: {k: v for k, v in r.items() if k != 'locator'} for r in doc['requirements']}
    a, b = norm(pinned), norm(current)
    added, removed = set(b) - set(a), set(a) - set(b)
    changed = {i for i in set(a) & set(b) if a[i] != b[i]}
    if added != ALLOWED_ADDED:
        out.append(f'added rows {sorted(added)} are not exactly {sorted(ALLOWED_ADDED)}')
    elif any(b[i]['kind'] == 'acceptance' for i in added):
        out.append('an added row is an acceptance row')
    if removed:
        out.append(f'removed rows {sorted(removed)}')
    for i in sorted(changed):
        rule = ALLOWED_CHANGED.get(i)
        if rule is None:
            out.append(f'changed row {i} is not an accepted revision')
            continue
        txt = lambda r: hashlib.sha256(r['text'].encode()).hexdigest()
        if (txt(a[i]), txt(b[i])) != (rule['before_text_sha256'], rule['after_text_sha256']):
            out.append(f'{i} text is not the exact accepted correction ({txt(a[i])} -> {txt(b[i])})')
        if any(a[i].get(f) != b[i].get(f) for f in rule['unchanged_fields']):
            out.append(f'{i} changed outside its text')
        if b[i].get('text_sha256') != txt(b[i]):
            out.append(f'{i} text_sha256 does not match its text')
    for i in ALLOWED_CHANGED:
        if i not in changed:
            out.append(f'accepted correction {i} is not present (stale)')
    pa = {p['id']: p['text'] for p in pinned['prose']}; pb = {p['id']: p['text'] for p in current['prose']}
    if pa != pb:
        out.append('prose differs')
    acc = lambda d: sorted(i for i, r in d.items() if r['kind'] == 'acceptance')
    if acc(a) != acc(b):
        out.append('acceptance set differs')
    return out
