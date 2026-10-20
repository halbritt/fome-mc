"""Verify integration's exact delta and source/model custody; no native ERC claim."""
import copy
import json
import tempfile
from pathlib import Path

from prepare import BASE, CONNECTOR, FOOTPRINT, MODEL, digest, files, prepare

with tempfile.TemporaryDirectory(prefix='pod-integration-') as temp:
    out = Path(temp) / 'inputs'
    receipt = prepare(out)
    before = json.loads((BASE / 'intent.json').read_text())
    expected = copy.deepcopy(before)
    j1 = next(c for c in expected['components'] if c['reference'] == 'J1')
    j1.update(value='1-776163-1', footprint='PodConnector:AMPSEAL_35_1-776163-1')
    actual = json.loads((out / 'intent.json').read_text())
    assert actual == expected, 'Only the two declared J1 identity fields may change'
    old_files = files(BASE)
    new_files = files(out)
    assert set(new_files) - set(old_files) == {
        'footprints/' + FOOTPRINT, 'models/' + MODEL, 'integration-receipt.json'
    }, 'Unexpected capture addition'
    assert set(old_files) <= set(new_files), 'Capture was removed'
    for path, sha in old_files.items():
        if path != 'intent.json':
            assert new_files[path] == sha, f'Existing capture changed: {path}'
    assert digest(out / 'footprints' / FOOTPRINT) == digest(CONNECTOR / FOOTPRINT)
    assert digest(out / 'models' / MODEL) == digest(CONNECTOR / 'sources' / MODEL)
    footprint_text = (out / 'footprints' / FOOTPRINT).read_text()
    assert '${KIPRJMOD}/inputs/models/' + MODEL in footprint_text, 'Model capture path'
    assert receipt['baseline_files_sha256'] == old_files
    assert receipt['outputs_sha256'] == {k: v for k, v in new_files.items() if k != 'integration-receipt.json'}
    try:
        prepare(out)
    except ValueError as e:
        assert str(e) == 'Output must be fresh'
    else:
        raise AssertionError('Existing capture was overwritten')
    out2 = Path(temp) / 'second'
    prepare(out2)
    assert files(out2) == new_files, 'Integration must reproduce byte-for-byte'
    print(json.dumps({'status': 'PASS', 'components': len(actual['components']),
                      'nets': len(actual['nets']), 'baseline_files_preserved': len(old_files)-1,
                      'allowed_component_field_changes': 2, 'added_asset_files': 2,
                      'reproducible': True, 'native_ERC': 'NOT_RUN'}, indent=2))
