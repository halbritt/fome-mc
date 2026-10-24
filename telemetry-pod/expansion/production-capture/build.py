"""Production capture for the Rev-3 microSD pod (AGENTEE-207/197, Phase A).

Reconstructs one candidate-root capture from tracked repository files and writes the
generated declarations into it:

- ``composition/refs.json``: the 305 native references of the current microSD source;
- ``composition/parts.json`` (``agent-ee.parts/1``) with ``footprints.json``,
  ``assignments.json`` and ``declarations.json`` (the patched D-PCB-1/13 CAD closure);
- ``composition/part-refs.json`` (``agent-ee.part-refs/1``) and
  ``composition/deviations.json`` (``agent-ee.part-deviations/1``);
- ``composition/j3-source.json``: J3 C114218's captured catalog row, datasheet acquisition,
  failed attempts, detect-switch mapping evidence and limitations;
- ``composition/intent.writer.json``, ``binding-ledger.json`` and ``binding-migration.json``:
  the writer intent binding-fill reads, with the 174 project-authored ``Qualification``
  limitations moved into a ledger (agent-509 binding composition decision, 2026-10-22);
- ``composition/rating-sources.json`` and ``rating-comparison.json``: the captured
  ``--ratings`` declaration and the comparison of every original rating with the producer's;
- ``composition/envelope.json`` with ``antenna-facts.json`` and ``captured-rule-areas.json``;
- ``composition/library-updates.json`` and ``reconstruction.json``;
- ``composition/project-models.json`` (FOMEMC-34): the two project-local 3D models the candidate carries at
  ``project/inputs/models/`` (``${KIPRJMOD}/inputs/models/``, KIPRJMOD being the candidate's ``project/``):
  the exact-part J1 header STEP (TE 1-776163-1 rev T) with its sourced native pose, and the U3 NEO-M9N
  datasheet-derived visualization, which the captured ``RF_GPS:ublox_NEO`` member references with zero transform.
  Visual/mechanical models only; no electrical claim.

Every manifest entry is an existing captured record re-verified against the microSD intent;
nothing is selected, rated or measured here. The original intent stays byte-identical as
``composition/intent.json`` (provenance and the parts declaration source).

Usage (from the fome-mc root; agent-ee is an origin/main export, pcbnew on the system python):
  /usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --out NEW_DIR
  /usr/bin/python3 telemetry-pod/expansion/production-capture/build.py AGENT_EE_EXPORT --check
"""
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
X = ROOT / 'telemetry-pod/expansion'
REL = HERE.relative_to(ROOT).as_posix()
MICROSD = X / 'storage-microsd'
PATCHED = X / 'design-rules/footprints'
CONSTRAINTS = X / 'design-rules/constraints.json'
OLD_PARTS = X / 'complete-parts-manifest/parts.json'
OLD_ASSIGNMENTS = X / 'complete-parts-manifest/assignments.json'
# AGENTEE-484: capacitors added by the decoupling source repair, each reusing an existing design part.
ADDITIONS = HERE / 'sources/decoupling-additions-agentee-484.json'
OLD_DECLARATIONS = X / 'cad-assignments/declarations.json'
FOOTPRINT_MANIFEST = X / 'placement-seed-microsd/footprint-manifest.json'
ENVELOPE = X / 'placement-inputs/envelope.json'
# AGENTEE-489: source-bound mechanical reservations (agent-ee.mechanical-reservations/1), opt-in until the
# production agent-ee pin carries the consumer (agent-ee 1177cbc2+); 7d5b0d4d does not know the field.
MECHANICAL = X / 'agentee-489-source'
MECHANICAL_SOURCES = {'mechanics/agentee-490-bound-reservations.json': X / 'agentee-490-mechanical-inputs/bound-reservations.json',
                      # AGENTEE-485 correction: the board the reservations were measured on (fa7c2ca6, bound in
                      # reservations.json), from its retained emission; the installed project is now the 485 emission.
                      'mechanics/original-board.kicad_pcb': HERE / 'evidence/emission-7d5b0d4d-agentee491/design/project/telemetry-pod.kicad_pcb'}
# AGENTEE-485 G3: the 489 per-dielectric material declaration (agent-529 1f09c567@1), opt-in. It enters the sourced
# envelope stackup (agent-ee.envelope/2 dielectric_type/epsilon_r/loss_tangent); thickness, copper and every layer
# source stay byte-identical, and a declaration that names another layer or thickness is refused.
STACKUP_MATERIALS = MECHANICAL / 'stackup-materials.json'
# AGENTEE-485 F6: the retained J2 132134 Rev C drawing (1ec1d365...) and its source/PCB-pattern bindings.
J2_132134 = X / 'agentee-494-j2'
J2_SOURCE = X / 'j2-historical-source'
# F8 changed the drawing's surrounding source manifest; historical import stays untouched.
J2_RECORD = HERE / 'sources/j2-adoption-f8/132134.json'
J2_FP = 'Agentee494:SMA_Amphenol_132134_Manufacturer'
J2_132134_CARRIED = ('132134-revC.pdf', 'source-manifest.json', 'pad-map.json')
J3_CATALOG = MICROSD / 'stock/catalog.json'
SOURCES = HERE / 'sources'
GUIDELINES = SOURCES / 'esp32-guidelines'
FAB = SOURCES / 'fab-profile'
J3_ATTEMPT = SOURCES / 'j3-capture-attempt'
J3_SOURCE = SOURCES / 'j3-datasheet'
J3_RECORD = J3_SOURCE / 'C114218.part-record.json'
J3_ORIGIN_RECORD = J3_SOURCE / 'origin-record/C114218.part-record.json'
J3_FAILED = ('acquisition', 'acquisition-direct', 'acquisition-legacy', 'acquisition-mirror')
J3_FOOTPRINT = 'footprints/Connector_Card.pretty/microSD_HC_Hirose_DM3AT-SF-PEJM5.kicad_mod'
RATINGS = SOURCES / 'rating-sources.json'
CATALOG_ONLY = {'schema': 'agent-ee.passive-rating-sources/1', 'catalog': True, 'facts': None, 'extractor': None}
PILOT = SOURCES / 'pilot-ratings'
RECOVERED = X / 'parts-closure/recovered-pilot'
LOCALITY = X / 'electrical-locality/pad-obligations/electrical-locality.json'
# The project-authored Qualification statements (part-bindings/prepare.py:52-58 and later
# lanes), each an exact text; any other text refuses.
QUALIFICATION_CLASSES = {
    'Identity metadata only; assembly and operating qualification pending': 'identity-only',
    'Identity and package selection only; assembly and operating qualification pending': 'package-selection',
    'Identity and series-divider selection only; assembly and operating qualification pending': 'series-divider',
}
QUALIFICATION_COUNTS = {'identity-only': 166, 'package-selection': 5, 'series-divider': 2, 'historical-j3': 1}
ESP32_DATASHEET = X / ('parts-closure/recovered-pilot/core/datasheets-core/'
                       'bcd526f54b8de686cec4db67219e36ea7ace50cddb0c92f3dfdac49cf99ffd2e.pdf')
GENERATED = ['refs.json', 'parts.json', 'footprints.json', 'assignments.json', 'declarations.json',
             'part-refs.json', 'deviations.json', 'j3-source.json', 'envelope.json', 'antenna-facts.json',
             'captured-rule-areas.json', 'library-updates.json', 'intent.writer.json', 'binding-ledger.json',
             'binding-migration.json', 'rating-comparison.json', 'rating-sources.json', 'rating-facts.json',
             'datasheet-source-selection.json', 'fab-profile.json', 'project-models.json', 'hand-fit-policy.json',
             'j2-hand-fit-mapping.json', 'j2-rf-binding.json', 'J2.external-part-record.json', 'intent.adopted.json',
             'j1-j2-assembly-source.json']
# FOMEMC-34 (agent-449 pod lane): both 3D models bound into the prepared scope at the path the footprints name.
MODELS_AT = 'project/inputs/models/'
MODEL_REFERENCE = '${KIPRJMOD}/inputs/models/'
CONNECTOR = X / 'connector-candidate'
J1_MODEL = CONNECTOR / 'sources/c-1-776163-1-t-3d.stp'
J1_FOOTPRINT = 'footprints/PodConnector.pretty/AMPSEAL_35_1-776163-1.kicad_mod'
# connector-candidate/README.md "Model placement and native convention": the sourced native pose.
J1_POSE = {'offset': [0, -31.8, 11.72], 'scale': [1, 1, 1], 'rotate': [-90, 0, 0]}
J1_POSE_QUOTE = ('KiCad stores the corresponding model rotation as **(-90, 0, 0)** degrees and\n'
                 'offset **(0, -31.8, 11.72)** mm')
# agent-521 correction (relayed in the coordinator's j6b assignment, Cairn 2026-10-22), quoted verbatim.
PLUG_ARCHIVE = CONNECTOR / 'mating-interface/sources/TE-CVM_776164-1-F-3d_stp.zip'
PLUG_RULING = ('CORRECTION by agent-521, Cairn 2026-10-22: the rev F CVM_776164-1 file is the mating PLUG, '
               'plug-only, in its own frame with no mating datum. It is NOT the J1 model. Keep it only as '
               'mating-interface evidence. A composite/mated view needs a sourced engagement datum and stays OPEN, '
               'so infer no transform.')
NEO = X / 'neo-m9n-model'
U3_MODEL = NEO / ('NEO-M9N-00B_visualization-only_datasheet-derived_'
                  'not-manufacturer-mechanical-qualification.step')
U3_FOOTPRINT = 'footprints/RF_GPS.pretty/ublox_NEO.kicad_mod'
U3_POSE = {'offset': [0, 0, 0], 'scale': [1, 1, 1], 'rotate': [0, 0, 0]}
U3_POSE_QUOTE = 'Zero model rotation/offset and unit scale place it on `RF_GPS:ublox_NEO`.'
U3_TAIL = '\t(embedded_fonts no)\n)\n'
D_PCB_1 = ('Thermal vias are 0.30 mm drill / 0.70 mm diameter after design-rules D-PCB-1 '
           '(footprints/ patched copy; KiCad/library original 0.20 mm).')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return json.dumps(value, indent=1, sort_keys=True) + '\n'


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


class Root:
    """The capture root; every copied file is pinned and every write is recorded."""

    def __init__(self, out):
        self.out, self.copied = out, {}

    def copy(self, source, dest):
        source = Path(source)
        target = self.out / dest
        if target.exists():
            if target.read_bytes() != source.read_bytes():
                raise ValueError('conflicting bytes for ' + dest)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        self.copied[dest] = {'source': rel(source), 'sha256': sha(source)}
        return {'path': dest, 'sha256': sha(target)}

    def derive(self, dest, data, source, derivation):
        """Write generated bytes derived from one repository source; the source and the output are pinned."""
        target = self.out / dest
        if target.exists():
            raise ValueError('conflicting bytes for ' + dest)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.copied[dest] = {'source': rel(source), 'sha256': sha(source), 'derived': derivation,
                             'output_sha256': sha(target)}
        return {'path': dest, 'sha256': sha(target)}

    def write(self, dest, value):
        target = self.out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text(value))
        return {'path': dest, 'sha256': sha(target)}


def native_inventory(work):
    """Export the microSD schematic's netlist on a temporary copy; the source is never re-saved."""
    from agent_ee.native_netlist import read_native_inventory
    run = work / 'project'
    run.mkdir(parents=True)
    for name in ('telemetry-pod.kicad_sch', 'telemetry-pod.kicad_pro', 'sym-lib-table', 'fp-lib-table'):
        shutil.copyfile(MICROSD / 'project' / name, run / name)
    (work / 'inputs').symlink_to(MICROSD / 'inputs', target_is_directory=True)
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o',
                    str(work / 'native.xml'), str(run / 'telemetry-pod.kicad_sch')], check=True,
                   capture_output=True)
    return read_native_inventory(work / 'native.xml')


def model_block(path, pose):
    """One KiCad 10 footprint model node, in the layout the captured J1 member uses."""
    xyz = lambda v: ' '.join(f'{x:g}' for x in v)  # noqa: E731
    return (f'\t(model "{path}"\n\t\t(offset\n\t\t\t(xyz {xyz(pose["offset"])})\n\t\t)\n'
            f'\t\t(scale\n\t\t\t(xyz {xyz(pose["scale"])})\n\t\t)\n'
            f'\t\t(rotate\n\t\t\t(xyz {xyz(pose["rotate"])})\n\t\t)\n\t)\n')


def bind_u3_model(source):
    """The captured ublox_NEO member plus exactly one zero-transform model node naming the U3 visualization.

    The captured member has no model (the stock KiCad 10 reference names a model the package does not ship);
    the node is inserted where KiCad writes it, after embedded_fonts, and nothing else changes (FOMEMC-34,
    neo-m9n-model/README.md: bind U3 to ${KIPRJMOD}/inputs/models/<same STEP filename> with zero transform)."""
    before = source.read_text()
    if '(model ' in before or not before.endswith(U3_TAIL) or before.count(U3_TAIL) != 1:
        raise ValueError('captured ublox_NEO member is not the expected model-less footprint')
    block = model_block(MODEL_REFERENCE + U3_MODEL.name, U3_POSE)
    return before[:-2] + block + ')\n', block


def libraries(root):
    """The microSD library closure with the four D-PCB-1/13 patched footprints swapped in, and the U3 member
    bound to its visualization model (FOMEMC-34). The source's unreferenced root models/ copy is not carried:
    the J1 member names ${KIPRJMOD}/inputs/models/, which project_models() fills from the connector source."""
    patched = {p.relative_to(PATCHED).as_posix(): p for p in PATCHED.rglob('*.kicad_mod')}
    updates, bindings = [], []
    for source in sorted((MICROSD / 'inputs').rglob('*')):
        name = source.relative_to(MICROSD / 'inputs').as_posix()
        if not source.is_file() or name in ('intent.json', 'emitter-layout.json') or name.startswith('models/'):
            continue
        member = name.removeprefix('footprints/')
        if name.startswith('footprints/') and member in patched:
            blob = root.copy(patched[member], name)
            updates.append({'member': name, 'before': {'path': rel(source), 'sha256': sha(source)},
                            'after': {'path': rel(patched[member]), 'sha256': blob['sha256']}})
            continue
        if name == U3_FOOTPRINT:
            data, block = bind_u3_model(source)
            blob = root.derive(name, data.encode(), source, 'FOMEMC-34 U3 model binding (library-updates.json)')
            bindings.append({'member': name, 'reference': 'U3', 'before': {'path': rel(source), 'sha256': sha(source)},
                             'after': {'sha256': blob['sha256'], 'derivation': 'inserted model node only'},
                             'inserted': block})
            continue
        root.copy(source, name)
    if len(updates) != 4 or len(patched) != 4 or len(bindings) != 1:
        raise ValueError('expected exactly the four patched footprints and the one U3 model binding')
    root.copy(J2_132134 / 'Agentee494.pretty/SMA_Amphenol_132134_Manufacturer.kicad_mod',
              'footprints/Agentee494.pretty/SMA_Amphenol_132134_Manufacturer.kicad_mod')
    return updates, bindings


def model_node(text):
    """The single model node of a footprint member: its path and offset/scale/rotate vectors."""
    import re
    nodes = re.findall(r'\(model "([^"]+)"\s*\(offset\s*\(xyz ([^)]*)\)\s*\)\s*\(scale\s*\(xyz ([^)]*)\)\s*\)'
                       r'\s*\(rotate\s*\(xyz ([^)]*)\)\s*\)\s*\)', text)
    if len(nodes) != 1 or text.count('(model ') != 1:
        raise ValueError('expected exactly one model node')
    path, *vectors = nodes[0]
    return path, dict(zip(('offset', 'scale', 'rotate'), ([float(x) for x in v.split()] for v in vectors)))


def project_models(root, bindings):
    """FOMEMC-34: both model files at ${KIPRJMOD}/inputs/models/ of the candidate project, hash-bound to their
    committed sources and source records, with the pose each footprint member stores. Visual/mechanical models
    only; no electrical claim. The CVM_776164-1 rev F mating plug is recorded as not bound."""
    import zipfile
    readme = CONNECTOR / 'README.md'
    if J1_POSE_QUOTE not in readme.read_text():
        raise ValueError('the J1 native pose is not the connector-candidate README statement')
    path, pose = model_node((root.out / J1_FOOTPRINT).read_text())
    if path != MODEL_REFERENCE + J1_MODEL.name or pose != {k: [float(x) for x in v] for k, v in J1_POSE.items()}:
        raise ValueError(f'captured J1 member model {path} {pose} is not the sourced pose')
    records = json.loads((CONNECTOR / 'sources.json').read_text())
    entry = next(r for r in records if r['file'] == 'sources/' + J1_MODEL.name)
    archive = next(r for r in records if r['file'] == entry['derived_from'])
    with zipfile.ZipFile(CONNECTOR / archive['file']) as z:
        member = z.read(entry['archive_member'])
    if (sha(J1_MODEL) != entry['sha256'] or sha(CONNECTOR / archive['file']) != archive['sha256']
            or hashlib.sha256(member).hexdigest() != entry['sha256']):
        raise ValueError('J1 STEP is not the recorded verbatim member of the captured TE archive')
    u3_path, u3_pose = model_node((root.out / U3_FOOTPRINT).read_text())
    provenance = json.loads((NEO / 'provenance.json').read_text())
    sums = dict(reversed(line.split('  ', 1)) for line in (NEO / 'SHA256SUMS').read_text().splitlines())
    if (u3_path != MODEL_REFERENCE + U3_MODEL.name or u3_pose != {k: [float(x) for x in v] for k, v in U3_POSE.items()}
            or provenance['adopted_model']['file'] != U3_MODEL.name
            or not sha(U3_MODEL) == provenance['adopted_model']['sha256'] == sums[U3_MODEL.name]
            or U3_POSE_QUOTE not in (NEO / 'README.md').read_text()):
        raise ValueError('U3 model binding differs from the neo-m9n-model package')
    member = lambda name: {'path': name, 'sha256': sha(root.out / name)}  # noqa: E731
    j1 = root.copy(J1_MODEL, MODELS_AT + J1_MODEL.name)
    u3 = root.copy(U3_MODEL, MODELS_AT + U3_MODEL.name)
    return {
        'schema': 'pod-capture.project-models/1',
        'authority': ('FOMEMC-34 (agent-449 pod lane, relayed in the j6b assignment): bind the J1 header STEP and the U3 '
                      'NEO-M9N visualization into the prepared scope, hash-bound. Visual/mechanical models only; '
                      'no electrical, fit, mating or qualification claim.'),
        'kiprjmod': 'project/', 'models_at': MODELS_AT,
        'models': [
            {'reference': 'J1', 'footprint': 'PodConnector:AMPSEAL_35_1-776163-1', 'member': member(J1_FOOTPRINT),
             'model_reference': path, 'candidate': {**j1, 'size_bytes': J1_MODEL.stat().st_size},
             'source': {'path': rel(J1_MODEL), 'sha256': sha(J1_MODEL),
                        'record': {'path': rel(CONNECTOR / 'sources.json'), 'sha256': sha(CONNECTOR / 'sources.json'),
                                   'entry': entry, 'archive': archive}},
             'part': {'mpn': '1-776163-1', 'manufacturer': 'TE Connectivity', 'model_revision': 'T',
                      'kind': 'right-angle 35-position AMPSEAL PCB header'},
             'pose': {**J1_POSE, 'source': {'path': rel(readme), 'sha256': sha(readme), 'quote': J1_POSE_QUOTE}},
             'pose_checks': ('connector-candidate/check_model.py: 35 tail axes on the drilled coordinates, 35 tip faces '
                             'below the two rear support flats, 3.50 mm projection, model envelope'),
             'class': ('exact-part manufacturer customer view model; mechanical visualization, not physical fit, '
                       'retention or mating acceptance')},
            {'reference': 'U3', 'footprint': 'RF_GPS:ublox_NEO', 'member': member(U3_FOOTPRINT),
             'model_reference': u3_path, 'candidate': {**u3, 'size_bytes': U3_MODEL.stat().st_size},
             'binding': bindings[0]['before'] | {'after_sha256': bindings[0]['after']['sha256']},
             'source': {'path': rel(U3_MODEL), 'sha256': sha(U3_MODEL),
                        'record': {'path': rel(NEO / 'provenance.json'), 'sha256': sha(NEO / 'provenance.json'),
                                   'class': provenance['class'], 'datasheet': provenance['source']}},
             'part': {'mpn': 'NEO-M9N-00B', 'manufacturer': 'u-blox'},
             'pose': {**U3_POSE, 'source': {'path': rel(NEO / 'README.md'), 'sha256': sha(NEO / 'README.md'),
                                            'quote': U3_POSE_QUOTE}},
             'class': provenance['class']}],
        'not_bound': [{'path': rel(PLUG_ARCHIVE), 'sha256': sha(PLUG_ARCHIVE),
                       'reason': 'mating plug (CVM_776164-1 rev F), mating-interface evidence only',
                       'ruling': {'class': 'coordinator-relayed agent-521 decision', 'quote': PLUG_RULING}}],
        'open': ['A composite or mated J1 view needs a sourced engagement datum; it stays OPEN and no transform is '
                 'inferred.',
                 'Native model resolution and pose checks run on each emitted candidate (pipeline.py models stage, '
                 'model_check.py); file presence here is not proof that KiCad loaded a model.']}


def footprint_manifest(root, updates, bindings=()):
    manifest = json.loads(FOOTPRINT_MANIFEST.read_text())
    after = {u['member']: u['after']['sha256'] for u in [*updates, *bindings]}
    for library in manifest['libraries']:
        for member in library['members']:
            member['sha256'] = after.get(member['path'], member['sha256'])
            if sha(root.out / member['path']) != member['sha256']:
                raise ValueError('footprint manifest member differs from the capture: ' + member['path'])
    missing = set(after) - {m['path'] for lib in manifest['libraries'] for m in lib['members']}
    if missing:
        raise ValueError('patched footprints absent from the manifest: ' + ', '.join(sorted(missing)))
    manifest['libraries'].append({'name': 'Agentee494', 'members': [{
        'path': 'footprints/Agentee494.pretty/SMA_Amphenol_132134_Manufacturer.kicad_mod',
        'sha256': sha(root.out / 'footprints/Agentee494.pretty/SMA_Amphenol_132134_Manufacturer.kicad_mod')}]})
    return manifest


def declarations():
    """Same pad classification; the thermal-via text records the D-PCB-1 drill change."""
    document = json.loads(OLD_DECLARATIONS.read_text())
    for entry in document['footprints']:
        if entry['footprint'] in ('RF_Module:ESP32-S3-WROOM-1', 'PodPower:DDA0008B', 'PodPower:DDA0008J_C02'):
            entry['rationale'] = (entry['rationale'].replace(' 0.2 mm', '').replace('0.2mm', '')
                                  + ' ' + D_PCB_1)
    return document


def j1_deviation(spec_ref, j1_part):
    return {
        'requirement_id': 'POD-AC-5',
        'original': {'mpn': j1_part['mpn'], 'lcsc': j1_part['lcsc']},
        'assembly': 'hand_soldered',
        'policy': 'owner_hand_fit',
        'reason': ('POD-AC-5 names the AMPSEAL harness header as hand-fitted after delivery; J1 is the '
                   'selected AMPSEAL 1-776163-1 and its captured JLCPCB row reports stock 0 and '
                   'assemblyComponentFlag false.'),
        'purchase_source': ('TE Connectivity 1-776163-1 (LCSC C596198 identity, captured stock 0); '
                            'availability unverified. No purchase made or authorized.'),
        'stock_deviation': {'reason': 'Requirement-named hand-fit part with zero captured stock; '
                                      'generation-day stock evidence is still required for release.'},
        'evidence_refs': [
            {'path': spec_ref, 'locator': 'Acceptance criteria item 5'},
            {'path': j1_part['selection']['part_record'], 'locator': 'mpn/lcsc/manufacturer/stock'},
            {'path': 'telemetry-pod/expansion/part-bindings/connector-stock/catalog.json',
             'locator': 'parts/C596198'},
        ],
    }


# j6: the five generic envelope obligations staged for candidate generation (agent-509 decision
# 2026-10-22, notes/509-envelope-obligations-20261022.txt) under agent-ee's reviewed source contract
# telemetry-pod-expanded/1 (board_envelope.OBLIGATION_CONTRACTS; 81e387ee, and 7d5b0d4d since j6b2). Witnesses are
# concrete envelope locators; open items are text only and add no numeric limit. Nothing here closes
# an item: board_envelope.require_final keeps every one blocking final acceptance. The enclosure/harness and
# board-thickness texts cite the committed relay record (j6b, review H2): class owner-relayed, agent-drafted,
# unconfirmed by the owner; authority is only the verbatim Cairn relay quoted (RELAY_QUOTES), never agent prose.
# At agent-ee 7d5b0d4d the contract screens J1 board thickness itself (AGENTEE-448 tht_thickness_fit) and no longer
# requires 'thickness-tolerance'; the contract refuses only dropped or restaged required items. The item is kept as
# an extra open item for the relayed board-side checks (d162e001); dropping it is a reviewed decision, not done here.
PHYSICAL, CANDIDATE = 'physical_qualification', 'candidate_assessment'
RELAY = X / 'connector-candidate/mating-interface/sources/owner-decision-2026-10-22-board-thickness.txt'
RELAY_CLASS = 'owner-relayed, agent-drafted, unconfirmed'
# Verbatim fragments of the agent-509 relays recorded in RELAY (Cairn id: quote); build() refuses unless each
# occurs in RELAY exactly as written.
RELAY_QUOTES = {
    'b706da93-a2c0-4c65-b36f-5e2697146aa3': (
        'accept the standard JLCPCB four-layer 1.6 mm nominal finished-board choice and its published standard '
        'tolerance.'),
    'b706da93-a2c0-4c65-b36f-5e2697146aa3/deliverables': (
        'Keep the owner direction that enclosure/harness are future design deliverables'),
    'd162e001-8f44-47cb-8960-d68ac9484d14': (
        'Keep normal footprint, finished-hole/pad, retention and solder-joint checks; a narrower requirement '
        'would need a concrete source or observed failure.'),
    '9561cd0c-759a-461e-955d-8f32829a5a73': 'Do not conflate these two tolerances.'}


def relay(key):
    """A cited relay: record path, the Cairn id it was relayed in, and the verbatim quote."""
    return f'Cairn {key.split("/")[0]} (verbatim): "{RELAY_QUOTES[key]}"'


RELAY_CITE = (f'[{RELAY_CLASS}; {RELAY.relative_to(ROOT).as_posix()} sha256 '
              f'{hashlib.sha256(RELAY.read_bytes()).hexdigest()}]')
ENCLOSURE = (f'The enclosure is an open design deliverable, not a blocker to candidate generation {RELAY_CITE}, '
             f'{relay("b706da93-a2c0-4c65-b36f-5e2697146aa3/deliverables")}; ')
HARNESS = (f'The harness is an open design deliverable, not a blocker to candidate generation {RELAY_CITE}, '
           f'{relay("b706da93-a2c0-4c65-b36f-5e2697146aa3/deliverables")}; ')
OPEN_ITEMS = {
    'corner-holes': [
        ('hole-authority', PHYSICAL, 'H1-H4 drill, plating, inset and coordinates are generator-selected values '
         'carried from placement-inputs/envelope.json (POD-ME-HOLES); no owner, manufacturer or standard source '
         'fixes them. ' + ENCLOSURE + 'the mounting interface is sourced from it once designed.'),
        ('fabricated-holes', PHYSICAL, 'Fabricated hole position, drill and plating are not verified; generation '
         'witnesses only the declared holes on the candidate board.')],
    'height': [
        ('candidate-heights', CANDIDATE, 'Component heights of a generated candidate are assessed from captured '
         'part heights; no height cap is adopted.'),
        ('cowl-fit', PHYSICAL, ENCLOSURE + 'fit under the tail cowl is verified against it.'),
        ('underside-fit', PHYSICAL, ENCLOSURE + 'back-side clearance, J3 included, is verified against it.'),
        ('connector-fit', PHYSICAL, ENCLOSURE + 'J1 and J2 installed height and access are verified against it.'),
        ('mating-plug-fit', PHYSICAL, 'The mated AMPSEAL plug envelope against the enclosure is not established '
         '(connector-candidate/mating-interface records it as unresolved).'),
        ('harness-fit', PHYSICAL, HARNESS + 'its routing and bend clearance are verified against it.')],
    'harness-edge': [
        ('panel-cutout', PHYSICAL, ENCLOSURE + 'the J1 panel cutout is verified against it.'),
        ('mating-plug', PHYSICAL, 'Engagement of the mating plug and the mated envelope are not established '
         '(connector-candidate/mating-interface).'),
        ('retention', PHYSICAL, 'Board-lock and plug retention are not established; no PCB retention is inferred '
         'from contact retention.'),
        ('thickness-tolerance', PHYSICAL, f'Board thickness {RELAY_CITE}. Relayed board choice: '
         f'{relay("b706da93-a2c0-4c65-b36f-5e2697146aa3")} Relayed checks: '
         f'{relay("d162e001-8f44-47cb-8960-d68ac9484d14")} Agent reasoning (not owner text): the J1 footprint, '
         'finished-hole, pad, board-lock and solder-tail checks against the TE drawing for the fabricated board '
         'therefore stay open here, and no thickness limit is adopted. The fabricator finished-thickness tolerance '
         'is a board-side fact; the component-side through-hole fit screening is a separate rule '
         f'({relay("9561cd0c-759a-461e-955d-8f32829a5a73")}; agent-ee AGENTEE-448) and is not evaluated by this '
         'item.'),
        ('harness-clearance', PHYSICAL, HARNESS + 'clearance at the J1 edge is verified against it.')],
    'antenna': [
        ('feed-point-side', PHYSICAL, 'The antenna feed-point side relative to the installed orientation is not '
         'qualified.'),
        ('housing-pocket', PHYSICAL, ENCLOSURE + 'the non-metallic antenna pocket (D-PCB-16) is verified against it.'),
        ('nearby-metal', PHYSICAL, 'Metal near the installed antenna (frame, cowl fixings, harness) is not assessed.'),
        ('support', PHYSICAL, 'Mechanical support of the overhanging module in the enclosure is not established.'),
        ('rf-performance', PHYSICAL, 'Installed RF performance needs a bench measurement (POD-AC-9).')],
    'imu-separation': [
        ('placement-assessment', CANDIDATE, 'The generated candidate is assessed for tall or heavy parts near U2 '
         '(J1, the SMA, electrolytic capacitors and L1); no numeric keep-apart threshold is adopted, and L1 near '
         'U2 stays an unresolved concern, not a pass.'),
        ('vibration-coupling', PHYSICAL, 'Vibration coupling into the IMU on the installed pod needs bench or '
         'installed evidence.')]}


def stage_obligations(record, index):
    """Coverage records for the contracted obligations; contract fields stay verbatim."""
    holes = {h['id']: i for i, h in enumerate(record['mounting_holes'])}
    keepouts = {k['id']: i for i, k in enumerate(record['keepouts'])}
    j1, u1 = f"/fixed_footprints/{index['J1']}", f"/fixed_footprints/{index['U1']}"
    generation = {
        'corner-holes': [{'locator': f'/mounting_holes/{holes[h]}'} for h in ('H1', 'H2', 'H3', 'H4')],
        'height': [],
        'harness-edge': [{'locator': j1}, {'locator': j1, 'criterion': 'outline-containment/1'},
                         {'locator': j1, 'criterion': 'part-identity/1'}],
        'antenna': [{'locator': u1}, {'locator': u1, 'criterion': 'outline-containment/1'},
                    {'locator': f"/keepouts/{keepouts['radio-antenna']}"}],
        'imu-separation': []}
    if sorted(o['id'] for o in record['obligations']) != sorted(generation):
        raise ValueError('envelope obligations differ from the five staged ones')
    for item in record['obligations']:
        item['coverage'] = {'generation': generation[item['id']],
                            'open': [{'id': i, 'stage': s, 'statement': t} for i, s, t in OPEN_ITEMS[item['id']]]}


def envelope(constraints_blob):
    """The placement envelope revised with the microSD-era decisions; nothing else changes."""
    record = json.loads(ENVELOPE.read_text())
    record['id'] = 'expanded-pod-microsd-production'
    fixed = {f['reference']: f for f in record['fixed_footprints']}
    fixed['J2'].update(side='front', inset_mm=10, position_mm=28, rotation_deg=0, insertion='from_top')
    fixed['J2'].pop('courtyard_overhangs', None)
    record['fixed_footprints'].append({
        'reference': 'J3', 'side': 'back', 'edge': 'left', 'position_mm': 33, 'inset_mm': 8.9,
        'rotation_deg': 90, 'insertion': 'through_edge', 'tolerance_mm': 0,
        'courtyard_overhangs': [{'edge': 'left', 'max_mm': 20.3}]})
    outline = [[0, 0], [90, 0], [90, 65], [0, 65]]
    record['keepouts'] += [
        {'id': 'D-PCB-7v2-In1-no-tracks', 'polygon': outline, 'layers': ['In1.Cu'], 'forbid': ['tracks']},
        {'id': 'D-PCB-6-RF-reference', 'polygon': [[76, 26.5], [81.5, 26.5], [81.5, 30.6], [76, 30.6]],
         'layers': ['In1.Cu', 'In2.Cu'], 'forbid': ['tracks', 'vias']}]
    for item in record['obligations']:
        if item['id'] == 'antenna':
            item['statement'] = (
                'ESP32-S3-WROOM-1 antenna overhangs the top edge (D-PCB-16, owner 2026-10-21: outside-board '
                'placement case, Espressif hardware design guidelines Section 1.4.7, page 33). The module-owned '
                'keepout rule area is retained from the captured footprint; datasheet Figure 11-1 module '
                'dimensions define no base-board clearance (AGENTEE-211). Feed-point side, housing clearance '
                'and RF performance remain unqualified.')
    source = {'path': constraints_blob['path'], 'sha256': constraints_blob['sha256']}
    index = {f['reference']: i for i, f in enumerate(record['fixed_footprints'])}
    stage_obligations(record, index)

    def fact(quote):
        if quote not in CONSTRAINTS.read_text():
            raise ValueError('decision quote absent from constraints.json: ' + quote)
        return {'quote': quote, 'source': source}
    record['constraint_provenance'] = {
        f"/fixed_footprints/{index['J2']}": {
            'class': 'derived',
            'derivation': 'WRITER engineering pose: J2 top-side anchor (80,28), rotation 0, from_top; sourced 132134 body and courtyard inside board. Supersedes Molex edge datum; no owner pose claim.',
            'facts': [fact('Decision: move the J2 anchor to x=85.24 so the datum coincides with the edge')]},
        f"/fixed_footprints/{index['J3']}": {
            'class': 'derived',
            'derivation': ('D-PCB-13 v3: J3 anchor (8.9, 32.0) on B.Cu, rotation 90, mouth at the left edge, '
                           'gives inset 8.9 mm and position 33 mm from the left edge start (0, 65); the card '
                           'lane overhangs the left edge by 20.3 mm.'),
            'facts': [fact('J3 is fixed at (8.9, 32.0) on B, rotation 90, mouth at the left board edge'),
                      fact('declared overhang band, left edge, 20.3 mm')]},
        f"/keepouts/{len(record['keepouts']) - 2}": {
            'class': 'derived',
            'derivation': 'D-PCB-7 v2: In1.Cu no-tracks rule area over the board outline (0,0)-(90,65).',
            'facts': [fact('In1.Cu stays a pure GND reference (no-tracks rule area over the outline')]},
        f"/keepouts/{len(record['keepouts']) - 1}": {
            'class': 'derived',
            'derivation': 'WRITER engineering rebind of D-PCB-6: U3 RF pad (77.5,29.1) to adopted J2 pad 1 (80,28); 1.5 mm advisory margin, x 76..81.5, y 26.5..30.6. Both inner-layer RF areas follow this sourced-endpoint corridor; no routing/return-path acceptance.',
            'facts': [fact('keep tracks and vias off In1.Cu and In2.Cu in x 76..88, y 26.5..30.6 mm')]},
    }
    return record


def j3_part(root, comp, sheet, intent_blob, qualify_record):
    """J3 as a named part from the path-bound C114218 record (part_record.prepare_record output)."""
    record = json.loads(J3_RECORD.read_text())
    binding = comp['part_binding']
    if ((record['lcsc'], record['mpn'], record['manufacturer']) !=
            (binding['LCSC'], binding['Partnumber'], binding['Manufacturer'])):
        raise ValueError('J3 binding differs from the C114218 record')
    origin = json.loads(J3_ORIGIN_RECORD.read_text())
    moved = {k for k in ('catalog', 'datasheets', 'artifact') if record[k]['path'] != origin[k]['path']}
    if ({k: v for k, v in record.items() if k not in moved} != {k: v for k, v in origin.items() if k not in moved}
            or any(record[k]['sha256'] != origin[k]['sha256'] for k in moved)):
        raise ValueError('relocated J3 record differs from the origin record beyond its paths')
    root.copy(J3_RECORD, rel(J3_RECORD))
    for path in qualify_record(record, ROOT):
        root.copy(ROOT / path, path)
    return {
        'id': comp['id'], 'role': 'Expanded pod J3 ' + record['mpn'], 'required': True,
        'instances': [{'sheet': sheet, 'reference': 'J3'}], 'lib_id': comp['lib_id'], 'footprint': comp['footprint'],
        'selection_id': comp['id'], 'lcsc': record['lcsc'], 'mpn': record['mpn'],
        'manufacturer': record['manufacturer'], 'package': record['package'], 'stock': record['stock'],
        'datasheet': {'status': 'captured', 'required': True, 'artifact': record['artifact'],
                      'provenance': {**record['datasheets'], 'locator': 'parts[id=' + record['datasheet_id'] + ']'}},
        'selection': {'kind': 'named', 'lcsc': record['lcsc'], 'part_record': rel(J3_RECORD),
                      'part_record_sha256': sha(J3_RECORD),
                      'decision_ref': {**intent_blob, 'locator': 'components[reference=J3]'}}}


def writer_intent(intent, intent_blob, j3_record):
    """The writer intent and its ledger: Qualification moves out; nothing else changes except J3's
    historical Datasheet URL, which the captured record supersedes (recorded, never silently dropped)."""
    from agent_ee.storage import identity
    writer, entries, migrations = copy.deepcopy(intent), {}, []
    for comp in writer['components']:
        binding = comp.get('part_binding', {})
        if 'Qualification' in binding:
            text_ = binding.pop('Qualification')
            kind = 'historical-j3' if comp['id'] == 'storage/J3' else QUALIFICATION_CLASSES.get(text_)
            if kind is None:
                raise ValueError('unclassified Qualification text: ' + comp['id'])
            entries[comp['id']] = {'reference': comp['reference'], 'field': 'Qualification', 'class': kind,
                                   'text': text_, 'text_sha256': hashlib.sha256(text_.encode()).hexdigest()}
        if 'AGENT_EE_Ratings' in binding:
            migrations.append({
                'component': comp['id'], 'reference': comp['reference'], 'field': 'AGENT_EE_Ratings',
                'original': binding.pop('AGENT_EE_Ratings'),
                'producer_value': 'binding-fill --ratings (composition/rating-sources.json)',
                'reason': ('The field pins the v9 pilot rating record by hash; that record names the pilot part id '
                           'and pilot-root response path. Its rating values stay in the writer intent and must be '
                           'regenerated exactly; the record difference is explained in rating-comparison.json.')})
        if comp['id'] == 'storage/J3':
            previous = binding.pop('Datasheet')
            if previous == j3_record['datasheet_url'] or 'PARAM_Datasheet' in binding:
                raise ValueError('J3 datasheet binding is not the historical uncaptured URL')
            migrations.append({
                'component': comp['id'], 'reference': comp['reference'], 'field': 'Datasheet', 'original': previous,
                'producer_value': j3_record['datasheet_url'],
                'producer_source': {'path': rel(J3_RECORD), 'sha256': sha(J3_RECORD), 'locator': 'datasheet_url'},
                'reason': ('The historical URL served no PDF (sources/j3-capture-attempt, outcome missing; '
                           'sources/j3-datasheet/acquisition-direct, J3-lcsc). binding-fill writes Datasheet and '
                           'PARAM_Datasheet from the captured C114218 record; an unequal writer value would refuse.')})
    counts = {k: sum(e['class'] == k for e in entries.values()) for k in QUALIFICATION_COUNTS}
    added_ids = {a['id'] for a in json.loads(ADDITIONS.read_text())['additions']}  # AGENTEE-484, template bindings
    if sum(m['field'] == 'AGENT_EE_Ratings' and m['component'] not in added_ids for m in migrations) != 98:
        raise ValueError('expected the 98 original AGENT_EE_Ratings fields')
    if counts != QUALIFICATION_COUNTS:
        raise ValueError(f'Qualification classes differ from the reviewed 174: {counts}')
    ledger = {
        'schema': 'pod-capture.binding-ledger/1',
        'source_intent': {**intent_blob, 'identity': identity(intent)},
        'authority': ('agent-509 binding composition decision 2026-10-22 '
                      '(sources/j3-datasheet/review/509-binding-composition-20261022.txt): project-authored '
                      'limitations, not producer bindings. They stay visible here and in the review inputs; '
                      'none is waived or satisfied by this move.'),
        'qualification': dict(sorted(entries.items())),
        'field_migrations': migrations,
        'annotations': [{
            'component': 'storage/J3', 'annotates': 'qualification[storage/J3]',
            'date': '2026-10-22',
            'statement': ('The historical statement above is retained verbatim. Since it was written, the J3 '
                          'datasheet has been captured: the DigiKey mirror of the Hirose DM3 Series MicroSD '
                          '2010.6 reference catalog (sha256 ' + j3_record['artifact']['sha256'] + '), canonical record '
                          + rel(J3_RECORD) + '. It is not the latest engineering drawing. Assembly and operating '
                          'qualification remain pending.'),
            'limitations': J3_LIMITATIONS}]}
    restored = copy.deepcopy(writer)
    for comp in restored['components']:
        if comp['id'] in entries:
            comp['part_binding']['Qualification'] = entries[comp['id']]['text']
        for m in migrations:
            if m['component'] == comp['id']:
                comp['part_binding'][m['field']] = m['original']
        if 'part_binding' in comp:  # restore the original field order too
            original = next(c for c in intent['components'] if c['id'] == comp['id'])['part_binding']
            comp['part_binding'] = {k: comp['part_binding'][k] for k in original}
    if restored != intent or json.dumps(restored) != json.dumps(intent):
        raise ValueError('writer intent plus ledger does not restore the original intent')
    changed = sorted(c['id'] for c, o in zip(writer['components'], intent['components']) if c != o)
    migration = {
        'schema': 'pod-capture.binding-migration/1', 'source_intent': ledger['source_intent'],
        'writer_intent_identity': identity(writer),
        'components_changed': len(changed), 'changed': changed,
        'qualification': {'fields': len(entries), 'classes': counts,
                          'texts': {t: sum(e['text'] == t for e in entries.values())
                                    for t in sorted({e['text'] for e in entries.values()})}},
        'field_migrations': {f: sorted(m['component'] for m in migrations if m['field'] == f)
                             for f in sorted({m['field'] for m in migrations})},
        'unchanged': ('Every other component, net, no-connect, library and binding field (Power and Voltage '
                      'included) is identical; '
                      'restoring the ledger texts and migrated fields reproduces the source intent exactly '
                      '(checked by build.py, including field order).')}
    if set(changed) != set(entries) | {m['component'] for m in migrations}:
        raise ValueError('writer intent changes components outside the ledger')
    return writer, ledger, migration


J3_LIMITATIONS = [
    'Source is the DigiKey mirror of the Hirose DM3 Series MicroSD 2010.6 reference catalog, not the latest '
    'engineering drawing; the official Hirose site returned HTTP 403 (retained failed acquisitions).',
    'PDF page 3 names DM3AT-SF-PEJM5 with code 609-0031-0.',
    'The card detection switches A/B are normally open and close on card insertion; the JLCPCB attribute '
    '"Additional Card Detection Pins: No" is contradicted by this manufacturer evidence and does not override it.',
    'Detect mapping verified by agent-509\'s delegated reviewer for these sources: manufacturer B is pad 9 '
    '(DET_B, SD_CD), manufacturer A is pad 10 (DET_A, GND).',
    'PDF page 2 operating temperature -25 to +85 C includes current-induced temperature rise. This shows the '
    'source exists; it does not qualify the actual board thermal or DFM.',
]


def j3_source(root, intent, physical, catalog, item, record):
    """J3's captured identity, datasheet acquisition, failed attempts and detect-mapping evidence."""
    attempt = json.loads((J3_ATTEMPT / 'manifest.json').read_text())
    failed = []
    for name in J3_FAILED:
        manifest = J3_SOURCE / name / 'manifest.json'
        root.copy(manifest, rel(manifest))
        doc = json.loads(manifest.read_text())
        if doc['outcome'] != 'missing':
            raise ValueError('retained failed J3 acquisition is not missing: ' + name)
        failed.append({'path': rel(manifest), 'sha256': sha(manifest), 'outcome': doc['outcome'],
                       'attempts': [{k: p[k] for k in ('id', 'url', 'reason')} for p in doc['parts']]})
    for path in sorted(J3_SOURCE.glob('bindings*.json')) + sorted((J3_SOURCE / 'review').glob('*.txt')):
        root.copy(path, rel(path))
    origin = root.copy(J3_ORIGIN_RECORD, rel(J3_ORIGIN_RECORD))
    # Detect mapping: the footprint pads, symbol pins and intent nets the reviewer cited, re-read here.
    footprint = (root.out / J3_FOOTPRINT).read_text()
    pads = {n: footprint.split(f'(pad "{n}" ', 1)[1].split('(at ', 1)[1].split(')', 1)[0] for n in ('9', '10')}
    symbols = (MICROSD / 'inputs/symbols/Connector.kicad_sym').read_text()
    base = symbols.split('(symbol "Micro_SD_Card_Det2"', 1)[1].split('(symbol "Micro_SD_Card_Det_Hirose_DM3AT"', 1)[0]
    pins = {}
    for chunk in base.split('(pin ')[1:]:
        name, number = chunk.split('(name "', 1)[1].split('"', 1)[0], chunk.split('(number "', 1)[1].split('"', 1)[0]
        pins[number] = name
    nets = {t['pin']['number']: n['name'] for n in intent['nets'] for t in n['terminals']
            if t['component'] == physical['J3']['id']}
    mapping = {'9': {'manufacturer': 'B', 'pad_at_mm': pads['9'], 'symbol_pin': pins['9'], 'net': nets['9']},
               '10': {'manufacturer': 'A', 'pad_at_mm': pads['10'], 'symbol_pin': pins['10'], 'net': nets['10']}}
    expected = {'9': ('-5.875 -7.725', 'DET_B', 'SD_CD'), '10': ('-6.825 2.775', 'DET_A', 'GND')}
    if any((m['pad_at_mm'], m['symbol_pin'], m['net']) != expected[n] for n, m in mapping.items()):
        raise ValueError('J3 detect mapping differs from the reviewed evidence: ' + json.dumps(mapping))
    return {
        'schema': 'pod-capture.j3-source/2', 'reference': 'J3', 'component': physical['J3']['id'],
        'status': 'captured',
        'identity': {k: catalog['parts']['C114218'][k] for k in ('lcsc', 'mpn', 'mfr', 'package', 'stock')},
        'catalog': {'path': rel(J3_CATALOG), 'sha256': sha(J3_CATALOG), 'fetched_at': catalog['requests'][0]['fetched_at'],
                    'response': {'path': rel(MICROSD / 'stock/responses/C114218.json'),
                                 'sha256': sha(MICROSD / 'stock/responses/C114218.json')}},
        'catalog_attributes': {a['attribute_name_en']: a['attribute_value_name'] for a in item['attributes']},
        'assembly_component_flag': item['assemblyComponentFlag'],
        'symbol': physical['J3']['lib_id'], 'footprint': physical['J3']['footprint'],
        'datasheet': {
            'record': {'path': rel(J3_RECORD), 'sha256': sha(J3_RECORD),
                       'producer': 'agent_ee.part_record (prepare_record), --root fome-mc'},
            'origin_record': {**origin, 'note': ('agent-509 sourcing record generated at the volatile root '
                                                 '/tmp/pod-acceptance-j3-source; it differs from the record above '
                                                 'only in the catalog, datasheets and artifact paths')},
            'acquisition': {**record['datasheets'], 'outcome': 'captured', 'url': record['datasheet_url'],
                            'artifact': record['artifact'], 'fetched_at': record['acquisition']['fetched_at']},
            'failed_acquisitions': [
                {'path': rel(J3_ATTEMPT / 'manifest.json'), 'sha256': sha(J3_ATTEMPT / 'manifest.json'),
                 'outcome': attempt['outcome'],
                 'attempts': [{k: p[k] for k in ('id', 'url', 'reason')} for p in attempt['parts']]}, *failed],
        },
        'detect_mapping': {
            'status': 'verified',
            'review': {'path': rel(J3_SOURCE / 'review/509-j3-detect-mapping-20261022.txt'),
                       'sha256': sha(J3_SOURCE / 'review/509-j3-detect-mapping-20261022.txt')},
            'pdf_page': 3, 'pins': mapping,
            'switch': 'normally open; A-B closed with a card inserted. R55 10k pulls SD_CD to 3V3; insertion grounds it.',
            'reread': 'pad positions from ' + J3_FOOTPRINT + ', pin names from Micro_SD_Card_Det2, nets from the intent'},
        'limitations': J3_LIMITATIONS,
    }


def rating_inputs(root):
    """The pilot's documented C40 fact and source selection, rebased onto the retained recovered-pilot bytes.

    Only the path locators move (pilot root -> repository path); quote, page, value and hashes are the
    pilot's (sources/pilot-ratings). The extractor is the pilot's pinned pdftotext."""
    if json.loads(RATINGS.read_text()) != CATALOG_ONLY:
        raise ValueError('captured catalog rating declaration differs')
    for path in sorted(PILOT.glob('*.json')):
        root.copy(path, rel(path))

    def moved(path, sha256):
        target = RECOVERED / path
        if sha(target) != sha256:
            raise ValueError('pilot path does not resolve to the retained bytes: ' + path)
        return rel(target)
    facts = json.loads((PILOT / 'passive-rating-facts.json').read_text())
    for fact in facts['facts']:
        fact['source']['path'] = moved(fact['source']['path'], fact['source']['sha256'])
        root.copy(ROOT / fact['source']['path'], fact['source']['path'])
    facts_blob = root.write('composition/rating-facts.json', facts)
    selection = json.loads((RECOVERED / 'passive-source-selection.json').read_text())
    for entry in selection['parts'].values():
        for item in entry['selected']:
            item['provenance']['path'] = moved(item['provenance']['path'], item['provenance']['sha256'])
            root.copy(ROOT / item['provenance']['path'], item['provenance']['path'])
    selection_blob = root.write('composition/datasheet-source-selection.json', selection)
    pilot = json.loads((PILOT / 'passive-ratings.json').read_text())
    declaration = {**CATALOG_ONLY, 'facts': facts_blob, 'extractor': pilot['extractor']}
    blob = root.write('composition/rating-sources.json', declaration)
    return blob, selection_blob, declaration


def rating_comparison(intent, writer, output, report, catalog_only):
    """Every original rating record and field against the producer's regenerated value.

    The original records are the v9 pilot's receipted binding-fill report (sources/pilot-ratings); each
    must differ from its regenerated record only by the part id and source path/hash migration
    explained here, and every native value must be equal. Anything else refuses."""
    names = ('AGENT_EE_Ratings', 'Power', 'Voltage')
    pilot = json.loads((PILOT / 'binding-fill.json').read_text())['ratings']['derived']
    by_hash = {v['record_sha256']: v['record'] for v in pilot.values()}
    produced = {c['id']: c.get('part_binding', {}) for c in output['components']}
    written = {c['id']: c.get('part_binding', {}) for c in writer['components']}
    rows = {}
    for comp in intent['components']:
        fields = {k: v for k, v in comp.get('part_binding', {}).items() if k in names}
        if not fields:
            continue
        original_hash = json.loads(fields['AGENT_EE_Ratings'])['record_sha256']
        old, new = by_hash[original_hash], report['ratings']['derived'][comp['reference']]
        record = new['record']
        values = {k: produced[comp['id']].get(k) for k in fields if k != 'AGENT_EE_Ratings'}
        if values != {k: v for k, v in fields.items() if k != 'AGENT_EE_Ratings'} or any(
                written[comp['id']].get(k) != v for k, v in values.items()):
            raise ValueError('regenerated rating value differs: ' + comp['id'])
        if json.loads(fields['AGENT_EE_Ratings'])['ratings'] != json.loads(produced[comp['id']]['AGENT_EE_Ratings'])['ratings']:
            raise ValueError('regenerated rating field values differ: ' + comp['id'])
        sources = []
        for field, rating in old['ratings'].items():
            other = record['ratings'][field]
            if {k: rating[k] for k in ('value', 'si', 'unit')} != {k: other[k] for k in ('value', 'si', 'unit')}:
                raise ValueError('regenerated rating record value differs: ' + comp['id'])
            for a, b in zip(rating['sources'], other['sources'], strict=True):
                keep = {k: v for k, v in a.items() if k not in ('path', 'sha256')}
                if keep != {k: v for k, v in b.items() if k not in ('path', 'sha256')}:
                    raise ValueError('regenerated rating source differs beyond its path: ' + comp['id'])
                if rel(RECOVERED / a['path']) != b['path']:
                    retained = RECOVERED / a['path']
                    if sha(retained) != a['sha256'] or a['kind'] != 'catalog':
                        raise ValueError('pilot rating source is not retained: ' + a['path'])
                    rows_ = [[x for x in json.loads(Path(p).read_text())['data']['componentPageInfo']['list']
                              if x['componentCode'] == a['id']][0] for p in (retained, ROOT / b['path'])]
                    attrs = [{x['attribute_name_en']: x['attribute_value_name'] for x in r['attributes']}[a['attribute']]
                             for r in rows_]
                    if attrs[0] != attrs[1] or attrs[0] != rating['value']:
                        raise ValueError('pilot and current catalog attributes differ: ' + comp['id'])
                    kind = 'other captured response with the same attribute'
                else:
                    kind = 'same bytes, repository path'
                    if a['sha256'] != b['sha256']:
                        raise ValueError('rating source hash differs at the same retained path: ' + comp['id'])
                sources.append({'field': field, 'kind': a['kind'], 'pilot': {'path': a['path'], 'sha256': a['sha256']},
                                'regenerated': {'path': b['path'], 'sha256': b['sha256']}, 'migration': kind})
        if {k: v for k, v in old['part'].items() if k != 'id'} != {k: v for k, v in record['part'].items() if k != 'id'} \
                or old['limitations'] != record['limitations']:
            raise ValueError('regenerated rating record part differs beyond its id: ' + comp['id'])
        rows[comp['id']] = {'reference': comp['reference'], 'fields': sorted(fields), 'values': values,
                            'original_record_sha256': original_hash, 'regenerated_record_sha256': new['record_sha256'],
                            'part_id': {'pilot': old['part']['id'], 'regenerated': record['part']['id']},
                            'sources': sources}
    added = {c: sorted(k for k in f if k in names) for c, f in produced.items()
             if any(k in f for k in names) and c not in rows}
    return {'schema': 'pod-capture.rating-comparison/1',
            'pilot_report': {'path': rel(PILOT / 'binding-fill.json'), 'sha256': sha(PILOT / 'binding-fill.json'),
                             'origin': '/tmp/agent469-coordination/pod-campaign-v1/driver-preparation-v9-90x65/'
                                       'inputs/binding-fill.json (v9 pilot binding-fill report)'},
            'sources_sha256': report['ratings']['sources_sha256'],
            'catalog_only': catalog_only,
            'counts': {k: sum(k in r['fields'] for r in rows.values()) for k in names},
            'components': len(rows), 'values_equal': len(rows),
            'record_migrations': {kind: sum(any(x['migration'] == kind for x in r['sources']) for r in rows.values())
                                  for kind in ('same bytes, repository path', 'other captured response with the same attribute')},
            'datasheet_sourced': sorted(c for c, r in rows.items() if any(x['kind'] == 'datasheet' for x in r['sources'])),
            'added': {'components': len(added), 'note': 'catalog ratings derived for parts the pilot left unrated; '
                                                        'new producer fields, not changes', 'fields': added},
            'missing': report['ratings']['missing'], 'rows': dict(sorted(rows.items()))}


def build(out, agent_ee, mechanical=False, materials=False):
    sys.path[:0] = [str(Path(agent_ee).resolve() / 'src')]
    from agent_ee import binding_fill, board_envelope
    from agent_ee.footprint_library import (antenna_placement_context, esp32_s3_wroom_1_datasheet_facts,
                                            esp32_s3_wroom_1_placement_policy, probe_rule_areas,
                                            validate_declarations)
    from agent_ee.jlc_stock_capture import validate_capture
    from agent_ee.part_decisions import validate_deviation
    from agent_ee.part_record import qualify_record, qualify_external_record, prepare_external_record
    from agent_ee.parts_manifest import qualify_manifest, validate_manifest
    from agent_ee.scaffold_rule_areas import load_retention
    from agent_ee.storage import identity

    out = Path(out).absolute()
    if out.exists():
        raise ValueError('output must not exist')
    out.mkdir(parents=True)
    root = Root(out)
    with tempfile.TemporaryDirectory(prefix='pod-capture-native-') as tmp:
        native = native_inventory(Path(tmp))

    # Library closure and the writer-owned microSD intent, both unchanged except D-PCB-1/13.
    updates, bindings = libraries(root)
    intent_blob = root.copy(MICROSD / 'inputs/intent.json', 'composition/intent.json')
    source_intent_blob = dict(intent_blob)
    root.copy(MICROSD / 'inputs/emitter-layout.json', 'composition/emitter-layout.json')
    intent = json.loads((out / intent_blob['path']).read_text())
    j2 = next(c for c in intent['components'] if c['reference'] == 'J2')
    j2_before = copy.deepcopy(j2)
    record2 = json.loads(J2_RECORD.read_text())
    if (record2['mpn'], record2['lcsc']) != ('132134', 'NO_LCSC'):
        raise ValueError('J2 must be captured Amphenol 132134, never the Molex identity')
    j2.update(footprint=J2_FP, value='132134')
    j2['part_binding'] = {k: v for k, v in j2['part_binding'].items() if k == 'Qualification'}
    j2['part_binding'].update(LCSC='NO_LCSC', Partnumber='132134', Manufacturer='Amphenol RF',
                            Datasheet=record2['datasheet_url'], PARAM_Datasheet=json.dumps({
                                'schema': 'agent-ee.datasheet-binding/1',
                                'url': record2['datasheet_url'], 'sha256': record2['artifact']['sha256']},
                                sort_keys=True, separators=(',', ':')))
    intent_blob = root.write('composition/intent.adopted.json', intent)
    physical = {c['reference']: c for c in intent['components'] if not c['reference'].startswith('#')}
    additions = json.loads(ADDITIONS.read_text())['additions']
    if set(physical) != set(native['components']) or len(physical) != 305 + len(additions):
        raise ValueError('intent and native references differ')
    constraints_blob = root.copy(CONSTRAINTS, rel(CONSTRAINTS))
    relay_text = RELAY.read_text()
    sections = {s.split(' ', 1)[0]: s for s in relay_text.split('--- Cairn ')[1:]}  # one verbatim relay each
    missing = [k for k, q in RELAY_QUOTES.items() if q not in sections.get(k.split('/')[0], '')]
    if missing or 'Class: owner-relayed' not in relay_text:
        raise ValueError(f'relay quotes absent from their Cairn sections of {rel(RELAY)}: {missing}')
    root.copy(RELAY, rel(RELAY))  # the cited relay record travels with the candidate
    spec_blob = root.copy(X / 'requirements/compiled/requirements-map/spec.md', 'composition/spec.md')

    # Existing named records, probes and copper features, re-verified against the microSD intent.
    old = json.loads(OLD_PARTS.read_text())
    # Requalify the external record against the actual combined deviations document, not a detached J2 list.
    root.copy(J2_RECORD, rel(J2_RECORD))
    for path in qualify_external_record(record2, ROOT):
        root.copy(ROOT / path, path)
    j1_source = next(p for p in old['parts'] if p['instances'][0]['reference'] == 'J1')
    production_deviations = {'schema': 'agent-ee.part-deviations/1',
                            'deviations': [j1_deviation(spec_blob['path'], j1_source),
                                           *json.loads((J2_SOURCE / 'deviations.json').read_text())['deviations']]}
    root.write('composition/deviations.json', production_deviations)
    # The writer owns deviations.json; parts provenance must pin an immutable source with the same full document.
    production_deviations_blob = root.write('composition/j1-j2-assembly-source.json', production_deviations)
    record2 = prepare_external_record(out, record2['identity_source'], record2['datasheets'], 'J2',
                                      {**production_deviations_blob, 'index': 1})
    record2_blob = root.write('composition/J2.external-part-record.json', record2)
    parts, kept = [], {}
    rebind = {r['reference']: r for r in json.loads(ADDITIONS.read_text()).get('rebindings', [])}  # AGENTEE-488
    old_by_ref = {p['instances'][0]['reference']: p for p in old['parts'] if len(p['instances']) == 1}
    rebound = {}
    for part in old['parts']:
        refs = [i['reference'] for i in part['instances']]
        if refs == ['J2']:
            part = {**copy.deepcopy(part), 'footprint': J2_FP,
                    **{k: record2[k] for k in ('lcsc', 'mpn', 'manufacturer', 'package', 'stock')},
                    'datasheet': {'status': 'captured', 'required': True, 'artifact': record2['artifact'],
                                  'provenance': {**record2['datasheets'], 'locator': 'parts[id=J2]'}},
                    'selection': {'kind': 'external', 'lcsc': 'NO_LCSC', 'part_record': record2_blob['path'],
                                  'part_record_sha256': record2_blob['sha256'],
                                  'decision_ref': {**intent_blob, 'locator': 'components[reference=J2]'}}}
        elif refs and refs[0] in rebind and 'record' in rebind[refs[0]]:  # AGENTEE-491: identity from its canonical record
            r = rebind[refs[0]]
            record = json.loads((ROOT / r['record']).read_text())
            part = {**copy.deepcopy(part), 'role': f"Expanded pod {refs[0]} {physical[refs[0]]['value']}",
                    **{k: record[k] for k in ('lcsc', 'mpn', 'manufacturer', 'package', 'stock')},
                    'datasheet': {'status': 'captured', 'required': True, 'artifact': record['artifact'],
                                  'provenance': {**record['datasheets'], 'locator': 'parts[id=' + record['datasheet_id'] + ']'}},
                    'selection': {**part['selection'], 'lcsc': record['lcsc'], 'part_record': r['record'],
                                  'part_record_sha256': sha(ROOT / r['record'])}}
        elif refs and refs[0] in rebind:  # take the template's verified part with this reference's identity
            r = rebind[refs[0]]
            tmpl = old_by_ref[r['template']]
            if physical[refs[0]]['part_binding'] != physical[r['template']]['part_binding']:
                raise ValueError('rebound part differs from its template binding: ' + refs[0])
            part = {**copy.deepcopy(tmpl), 'id': r['id'], 'selection_id': r['id'],
                    'role': f"Expanded pod {refs[0]} {physical[refs[0]]['value']}", 'instances': copy.deepcopy(part['instances'])}
            rebound[r['id']] = tmpl['id']
        if not set(refs) <= set(physical):
            if set(refs) & set(physical):
                raise ValueError('partly removed part: ' + part['id'])
            continue
        part = copy.deepcopy(part)
        for instance in part['instances']:
            instance['sheet'] = native['components'][instance['reference']]['sheet']
        (ref,) = refs
        comp = physical[ref]
        if ((part.get('kind') != 'bare_copper_probe' and part['id'] != comp['id']) or
                any(part[k] != comp[k] for k in ('lib_id', 'footprint'))):
            raise ValueError('CAD identity differs from the microSD intent: ' + ref)
        if part.get('kind') == 'copper_feature':
            nets = {pin: next(n['name'] for n in native['nets'].values() if (ref, pin) in n['terminals'])
                    for pin in native['components'][ref]['pins']}
            if part['instances'][0]['nets'] != nets:
                raise ValueError('copper feature nets differ: ' + ref)
        elif 'selection' in part:
            record_root = out if ref == 'J2' else ROOT
            record_path = record_root / part['selection']['part_record']
            record = json.loads(record_path.read_text())
            binding = comp['part_binding']
            sheet = json.loads(binding['PARAM_Datasheet'])
            if ((record['lcsc'], record['mpn'], record['manufacturer']) !=
                    (binding['LCSC'], binding['Partnumber'], binding['Manufacturer']) or
                    (record['artifact']['sha256'], record['datasheet_url']) != (sheet['sha256'], sheet['url'])):
                raise ValueError('binding differs from the canonical record: ' + ref)
            if ref != 'J2':
                root.copy(record_path, part['selection']['part_record'])
            qualifier = qualify_external_record if part['selection']['kind'] == 'external' else qualify_record
            for path in qualifier(record, record_root):
                if ref != 'J2':
                    root.copy(ROOT / path, path)
            part['selection']['decision_ref'] = {**intent_blob, 'locator': f'components[reference={ref}]'}
        parts.append(part)
        kept[ref] = part['id']
    root.copy(ADDITIONS, rel(ADDITIONS))
    added = {}
    for add in additions:  # copy the template's verified part; only identity fields change
        ref, tmpl_ref = add['reference'], add['template']
        tmpl = next(p for p in parts if [i['reference'] for i in p['instances']] == [tmpl_ref])
        comp, tcomp = physical[ref], physical[tmpl_ref]
        if (comp['id'] != add['id'] or comp['part_binding'] != tcomp['part_binding'] or
                any(comp[k] != tcomp[k] for k in ('lib_id', 'footprint', 'value'))):
            raise ValueError('added part differs from its template: ' + ref)
        part = copy.deepcopy(tmpl)
        part.update({'id': add['id'], 'selection_id': add['id'], 'role': f"Expanded pod {ref} {comp['value']}",
                     'instances': [{'sheet': native['components'][ref]['sheet'], 'reference': ref}]})
        part['selection']['decision_ref'] = {**intent_blob, 'locator': f'components[reference={ref}]'}
        parts.append(part)
        kept[ref] = part['id']
        added[part['id']] = tmpl['id']
    j3 = j3_part(root, physical['J3'], native['components']['J3']['sheet'], intent_blob, qualify_record)
    parts.append(j3)
    kept['J3'] = j3['id']
    gaps = sorted(set(physical) - set(kept))
    if gaps:
        raise ValueError('unexpected undeclared references: ' + ', '.join(gaps))
    for part in parts:  # probe/copper symbol and footprint pins must match the capture root
        feature = part.get('probe') or part.get('copper')
        for blob in ([feature['symbol'], feature['footprint']] if feature else []):
            if sha(out / blob['path']) != blob['sha256']:
                raise ValueError('feature CAD differs from the capture: ' + part['id'])

    ratings_blob, selection_blob, rating_declaration = rating_inputs(root)
    c40 = next(p for p in parts if p['id'] == 'power/C40')
    if c40['lcsc'] != 'C452751' or 'source_selection' in c40['datasheet']:
        raise ValueError('C40 is not the pilot-selected C452751 source')
    c40['datasheet']['source_selection'] = {**selection_blob, 'part_key': 'C452751'}
    manifest = footprint_manifest(root, updates, bindings)
    models = project_models(root, bindings)
    manifest_blob = root.write('composition/footprints.json', manifest)
    old_assignments = {c['reference']: c for c in json.loads(OLD_ASSIGNMENTS.read_text())['components']}
    assignments = {'schema': 'agent-ee.footprint-assignments-input/1', 'libraries': intent['libraries'],
                   'components': [({**old_assignments[rebound[p['id']]], 'reference': p['id']} if p['id'] in rebound else None) or
                                  old_assignments.get(p['id']) or (
                       {**old_assignments[added[p['id']]], 'reference': p['id']} if p['id'] in added else None) or {
                       'reference': p['id'], 'lib_id': p['lib_id'], 'footprint': p['footprint'],
                       'assembly': 'smd', 'connector': None} for p in parts]}
    if sum(p['id'] not in old_assignments and p['id'] not in added for p in parts) != 1:
        raise ValueError('only J3 may lack an earlier footprint assignment')
    a2 = next(a for a in assignments['components'] if a['reference'] == physical['J2']['id'])
    a2.update(footprint=J2_FP, assembly='through_hole')
    assignments_blob = root.write('composition/assignments.json', assignments)
    declared = declarations()
    validate_declarations(declared)
    declarations_blob = root.write('composition/declarations.json', declared)
    members = [m for lib in manifest['libraries'] for m in lib['members']] + [
        {k: lib[k] for k in ('path', 'sha256')} for lib in intent['libraries']]
    document = {
        'schema': 'agent-ee.parts/1', 'declaration_source': {**intent_blob, 'locator': 'components'},
        'catalog': None, 'selection': None,
        'cad': {'manifest': manifest_blob, 'assignments': assignments_blob,
                'members_sha256': identity(sorted(members, key=lambda m: m['path'])),
                'declarations': declarations_blob},
        'property_fields': old['property_fields'], 'population': old['population'], 'parts': parts}
    validate_manifest(document)
    parts_blob = root.write('composition/parts.json', document)
    qualification = qualify_manifest(document, out)

    # Preserve J1's reviewed chain; J2 has its own verbatim approval and engineering identity mapping.
    j1_policy = json.loads((HERE / 'assembly/hand-fit-policy.json').read_text())['hand_fit_policy']
    for cited in j1_policy['selection']['records']:
        if cited['source'] == 'composition/parts.json':
            cited['sha256'] = parts_blob['sha256']
            cited['pointer'] = '/parts/' + str(next(i for i, p in enumerate(parts)
                                                   if p['instances'][0]['reference'] == 'J1'))
    approval = J2_SOURCE / 'owner-handfit-ccbe2294.md'
    approval_blob = root.copy(approval, rel(approval))
    mapping = {'class': 'engineering', 'reference': 'J2', 'mpn': '132134', 'lcsc': None,
               'approval': {'source': approval_blob['path'], 'sha256': approval_blob['sha256'],
                            'record_id': 'ccbe2294@1'},
               'context': {'source': rel(J2_RECORD), 'sha256': sha(J2_RECORD), 'pointer': ''}}
    mapping_blob = root.write('composition/j2-hand-fit-mapping.json', mapping)
    quote = approval.read_text().splitlines()[5]
    root.write('composition/hand-fit-policy.json', [j1_policy, {
        'source': approval_blob['path'], 'sha256': approval_blob['sha256'], 'line': 6, 'quote': quote,
        'identities': [{'mpn': '132134', 'lcsc': None}],
        'mapping': {'source': mapping_blob['path'], 'sha256': mapping_blob['sha256'], 'pointer': ''}}])

    # Part refs: every non-power component.
    refs = {'schema': 'agent-ee.part-refs/1',
            'components': {physical[r]['id']: {'part_ref': kept[r]} for r in sorted(kept)}}
    if {p['id'] for p in parts} != {v['part_ref'] for v in refs['components'].values()}:
        raise ValueError('part refs differ from the manifest')
    root.write('composition/part-refs.json', refs)

    # The actual deviations: J1 only (POD-AC-5 hand fit, zero captured stock).
    j1 = next(p for p in parts if p['instances'][0]['reference'] == 'J1')
    deviations = {'schema': 'agent-ee.part-deviations/1',
                  'deviations': [j1_deviation(spec_blob['path'], j1),
                                 *json.loads((J2_SOURCE / 'deviations.json').read_text())['deviations']]}
    for d in deviations['deviations']:
        validate_deviation(d)
        for ref in d['evidence_refs']:
            if ref['path'] not in (spec_blob['path'],):
                root.copy(ROOT / ref['path'], ref['path'])
    root.write('composition/deviations.json', deviations)

    # J3: captured catalog identity, datasheet acquisition, failed attempts and detect mapping.
    root.copy(J3_CATALOG, rel(J3_CATALOG))
    response = MICROSD / 'stock/responses/C114218.json'
    root.copy(response, rel(response))
    catalog = json.loads(J3_CATALOG.read_text())
    validate_capture(catalog, lambda name: (J3_CATALOG.parent / name).read_bytes())
    item = json.loads(response.read_text())['data']['componentPageInfo']['list'][0]
    j3_record = json.loads(J3_RECORD.read_text())
    root.copy(J3_ATTEMPT / 'manifest.json', rel(J3_ATTEMPT / 'manifest.json'))
    root.copy(J3_ATTEMPT / 'bindings.json', rel(J3_ATTEMPT / 'bindings.json'))
    j3 = j3_source(root, intent, physical, catalog, item, j3_record)
    root.write('composition/j3-source.json', j3)

    # Envelope: microSD decisions, antenna facts (AGENTEE-211) and captured antenna CAD retention.
    for name in ('jlcpcb-capabilities.txt', 'jlcpcb-stackup.txt', 'jlcpcb-thickness.txt'):
        root.copy(FAB / 'sources' / name, 'sources/' + name)
    source_profile = root.copy(FAB / 'fab-profile.json', 'sources/fab-profile.json')
    revised = envelope(constraints_blob)
    if revised['fab_profile']['sha256'] != source_profile['sha256']:
        raise ValueError('envelope fab profile differs from the captured profile')
    # j6: each fab-profile/1 limit names the requirement its check binds, and agent-ee requires that to be
    # this envelope's derived fab-profile requirement (routing_rules.validate_mappings). The captured profile
    # was written for envelope id telemetry-pod; the production copy relabels only that field. Values, tiers,
    # stackup, tolerance and every source citation stay byte-identical (checked below).
    profile = json.loads((FAB / 'fab-profile.json').read_text())
    relabel = {'from': 'R-envelope-telemetry-pod-fab-profile', 'to': f"R-envelope-{revised['id']}-fab-profile"}
    if {limit['requirement'] for limit in profile['limits']} != {relabel['from']}:
        raise ValueError('captured fab profile limits name another requirement')
    production = copy.deepcopy(profile)
    for limit in production['limits']:
        limit['requirement'] = relabel['to']
    if [{k: v for k, v in l.items() if k != 'requirement'} for l in production['limits']] != [
            {k: v for k, v in l.items() if k != 'requirement'} for l in profile['limits']] or (
            {k: v for k, v in production.items() if k != 'limits'} != {k: v for k, v in profile.items() if k != 'limits'}):
        raise ValueError('fab profile relabel changed more than the requirement mapping')
    profile_blob = root.write('composition/fab-profile.json', production)
    revised['fab_profile']['sha256'] = profile_blob['sha256']
    if mechanical:
        mech = json.loads((MECHANICAL / 'reservations.json').read_text())
        expected = {mech['source']['path']: mech['source']['sha256'],
                    mech['original_board_path']: mech['original_board_sha256']}
        if set(expected) != set(MECHANICAL_SOURCES):
            raise ValueError('mechanical reservations name other captured paths')
        for dest, source in MECHANICAL_SOURCES.items():
            if root.copy(source, dest)['sha256'] != expected[dest]:
                raise ValueError('mechanical reservations are stale against ' + rel(source))
        revised['mechanical_reservations'] = root.copy(MECHANICAL / 'reservations.json', 'mechanics/reservations.json')
        # AGENTEE-485 F6 disposition: canonical acquisition is deferred, so the retained Amphenol 132134 Rev C
        # drawing and its source/PCB-pattern bindings ride in the production capture at their fome-mc paths,
        # each verified against the 494-j2 SHA256SUMS (provenance only; nothing reads them as acceptance).
        sums = dict(line.split()[::-1] for line in (J2_132134 / 'SHA256SUMS').read_text().splitlines() if line.strip())
        for name in J2_132134_CARRIED:
            if root.copy(J2_132134 / name, rel(J2_132134 / name))['sha256'] != sums[name]:
                raise ValueError(f'{rel(J2_132134 / name)} differs from its 494-j2 SHA256SUMS')
    if materials:
        stackup_materials = json.loads(STACKUP_MATERIALS.read_text())
        if stackup_materials.get('schema') != 'agentee-489.stackup-materials/1':
            raise ValueError('stackup materials are not agentee-489.stackup-materials/1')
        dielectrics = [l for l in revised['stackup']['layers'] if l['kind'] == 'dielectric']
        if [(l['name'], l['thickness_mm']) for l in dielectrics] != [
                (l['name'], l['thickness_mm']) for l in stackup_materials['layers']]:
            raise ValueError('stackup materials name other dielectric layers or thicknesses than the envelope')
        for layer, material in zip(dielectrics, stackup_materials['layers']):
            layer.update({k: material[k] for k in ('dielectric_type', 'epsilon_r', 'loss_tangent')})
        root.copy(STACKUP_MATERIALS, 'mechanics/stackup-materials.json')
    envelope_blob = root.write('composition/envelope.json', revised)
    from agent_ee.scaffold import NAMESPACE as scaffold_namespace
    area_sources = {'460352a8-dace-51a2-842b-c1e4ef7ad212': 'D-PCB-7v2-In1-no-tracks',
                    '93d1ddf1-382d-5ed8-abfa-2bf617ad0cae': 'D-PCB-6-RF-reference'}
    area_bindings = {}
    for source_uuid, name in area_sources.items():
        native_uuid = str(uuid.uuid5(scaffold_namespace, envelope_blob['sha256'] + ':area:' + name))
        area = next(k for k in revised['keepouts'] if k['id'] == name)
        area_bindings[native_uuid] = {
            'source_uuid': source_uuid, 'name': name, 'polygon_mm': area['polygon'],
            'tracks_forbidden': 'tracks' in area['forbid'], 'vias_forbidden': 'vias' in area['forbid']}
    root.write('composition/j2-rf-binding.json', {
        'class': 'engineering', 'reference': 'J2', 'footprint': J2_FP,
        'anchor_mm': [80, 28], 'side': 'front', 'rotation_deg': 0, 'insertion': 'from_top',
        'signal_pad': {'number': '1', 'centre_mm': [80, 28]},
        'ground_pads': {'number': '2', 'centres_mm': [[80 + x, 28 + y] for x in (-2.54, 2.54) for y in (-2.54, 2.54)]},
        'rule_area_uuids': ['460352a8-dace-51a2-842b-c1e4ef7ad212', '93d1ddf1-382d-5ed8-abfa-2bf617ad0cae'],
        'rule_area_bindings': area_bindings,
        'native_uuid_derivation': {'class': 'engineering', 'envelope': envelope_blob,
                                   'algorithm': 'scaffold.NAMESPACE / uuid5(envelope sha256 + :area: + keepout id)',
                                   'note': 'Original logical area identities map to generated UUIDs; changing envelope bytes changes native area UUIDs.'},
        'polygon_mm': [[76, 26.5], [81.5, 26.5], [81.5, 30.6], [76, 30.6]],
        'source': {'path': rel(J2_132134 / 'pad-map.json'), 'sha256': sha(J2_132134 / 'pad-map.json')},
        'limitations': 'Writer pose and advisory corridor; final native geometry checked separately. No routed RF or filled-return-path qualification.'})
    files = {p.relative_to(out).as_posix(): sha(p) for p in out.rglob('*') if p.is_file()}
    record = board_envelope.validate((out / envelope_blob['path']).read_bytes(),
                                     profile=(out / profile_blob['path']).read_bytes(), captured=(files, out))
    if record['fab_profile'].get('status') != 'referenced':
        raise ValueError(f"production fab profile not referenced: {record['fab_profile']}")
    datasheet = root.copy(ESP32_DATASHEET, rel(ESP32_DATASHEET))
    facts = esp32_s3_wroom_1_datasheet_facts(pdf_path=datasheet['path'], pdf_sha256=datasheet['sha256'])
    root.write('composition/antenna-facts.json', facts)
    pdf = next(GUIDELINES.glob('*.pdf'))
    guideline = root.copy(pdf, rel(pdf))
    root.copy(GUIDELINES / 'manifest.json', rel(GUIDELINES / 'manifest.json'))
    policy = esp32_s3_wroom_1_placement_policy('outside_board', pdf_path=guideline['path'])
    member = next(m for lib in manifest['libraries'] for m in lib['members']
                  if m['path'] == 'footprints/RF_Module.pretty/ESP32-S3-WROOM-1.kicad_mod')
    u1 = next(f for f in record['fixed_footprints'] if f['reference'] == 'U1')
    retention = {
        'schema': 'agent-ee.captured-rule-areas/1', 'purpose': 'retain-captured-cad-only',
        'envelope': envelope_blob, 'parts': parts_blob,
        'items': [{'keepout_id': 'radio-antenna', 'reference': 'U1', 'footprint': 'RF_Module:ESP32-S3-WROOM-1',
                   'pose': {k: u1[k] for k in ('anchor_mm', 'rotation_deg', 'side')}, 'source': member,
                   'rule_areas': probe_rule_areas((out / member['path']).read_bytes(), library='RF_Module',
                                                  path=member['path'], declared=validate_declarations(declared)[0]),
                   'policy': policy,
                   'context': antenna_placement_context(policy, {guideline['path']: (out / guideline['path']).read_bytes()})}]}
    retention_blob = root.write('composition/captured-rule-areas.json', retention)
    retained = load_retention(out, retention_blob['path'], envelope_blob['path'], parts_blob['path'], record, document)

    refs_record = {'schema': 'pod-capture.microsd-refs/1', 'source': {**intent_blob, 'locator': 'components'},
                   'native_schematic': {'path': rel(MICROSD / 'project/telemetry-pod.kicad_sch'),
                                        'sha256': sha(MICROSD / 'project/telemetry-pod.kicad_sch')},
                   'count': len(physical),
                   'references': {r: {'id': c['id'], 'lib_id': c['lib_id'], 'footprint': c['footprint'],
                                      'value': c['value'], 'sheet': native['components'][r]['sheet'],
                                      'declaration': next(p.get('kind', 'named') for p in parts
                                                          if p['instances'][0]['reference'] == r)}
                                  for r, c in sorted(physical.items())}}
    root.write('composition/refs.json', refs_record)
    root.write('composition/library-updates.json', {
        'schema': 'pod-capture.library-updates/1',
        'decisions': ['D-PCB-1 (thermal-via drills)', 'D-PCB-13 v2 (J3 card-lane courtyard)'],
        'decision_source': constraints_blob, 'updates': updates,
        'model_bindings': bindings, 'model_bindings_source': 'FOMEMC-34 (composition/project-models.json)'})
    root.write('composition/project-models.json', models)

    # Writer intent: Qualification into the ledger; the bound projection is seeded with its bytes
    # (binding_fill.configuration(output=...) needs a captured output; the step replaces it).
    writer, ledger, migration = writer_intent(intent, intent_blob, j3_record)
    ledger['j2_adoption'] = {'class': 'engineering', 'original': j2_before, 'adopted': physical['J2'],
                            'source_intent': source_intent_blob, 'adopted_intent': intent_blob,
                            'record': {'path': rel(J2_RECORD), 'sha256': sha(J2_RECORD)},
                            'preserved': 'component id, UUID and electrical membership; writer pose is not owner text'}
    writer_blob = root.write('composition/intent.writer.json', writer)
    root.write('composition/intent.bound.json', writer)
    root.write('composition/binding-ledger.json', ledger)
    root.write('composition/binding-migration.json', migration)
    root.copy(LOCALITY, rel(LOCALITY))

    # Binding-fill on the writer intent with the captured catalog rating declaration: the genuine
    # producer. Every original binding, rating included, must equal its regenerated value.
    root.copy(RATINGS, rel(RATINGS))
    try:  # the captured catalog-only declaration first: C40's catalog row has null attributes
        binding_fill.fill(out, writer, document, refs, deviations, captures='.', ratings=CATALOG_ONLY,
                          source_migration=True)
        catalog_only = {'declaration': rel(RATINGS), 'execution': 'ok'}
    except ValueError as exc:
        catalog_only = {'declaration': rel(RATINGS), 'execution': 'refused', 'error': str(exc)}
    output, report = binding_fill.fill(out, writer, document, refs, deviations, captures='.',
                                       ratings=rating_declaration, source_migration=True)
    comparison = rating_comparison(intent, writer, output, report, catalog_only)
    root.write('composition/rating-comparison.json', comparison)
    fill = {'execution': 'ok', 'components': len(report['components']), 'writer_intent': writer_blob['path'],
            'ratings': {k: len(report['ratings'][k]) for k in ('derived', 'missing')},
            'probe_migrations': len(report['probe_migrations']),
            'assembly_deviations': sorted(r['reference'] for r in report['components']
                                          if r.get('assembly_deviation') is not None),
            'rating_fields': comparison['counts'], 'newly_rated': comparison['added']['components'],
            'catalog_only': comparison['catalog_only']['execution'],
            'added_fields': {c['reference']: sorted(added) for c, w in zip(output['components'], writer['components'])
                             if (added := set(c.get('part_binding', {})) - set(w.get('part_binding', {})) -
                                 {'AGENT_EE_Ratings', 'Power', 'Voltage'})}}
    summary = {
        'references': len(physical), 'declared': len(kept), 'gaps': gaps,
        'parts': {'named': sum('selection' in p for p in parts),
                  'bare_copper_probe': sum(p.get('kind') == 'bare_copper_probe' for p in parts),
                  'copper_feature': sum(p.get('kind') == 'copper_feature' for p in parts)},
        'qualify_manifest': {'dependencies': len(qualification['dependencies']),
                             'missing_provenance': qualification['missing_provenance'],
                             'cad': {k: qualification['cad'][k] for k in ('execution', 'outcome', 'coverage')}},
        'envelope': {'structural': record.get('structural'), 'outcome': record.get('outcome'),
                     'fixed': [f['reference'] for f in record['fixed_footprints']],
                     'keepouts': [k['id'] for k in revised['keepouts']],
                     'provenance_status': record['constraint_provenance']['status']},
        'retention': sorted(retained['items']), 'binding_fill': fill,
        'fab_profile': {'source': source_profile, 'production': profile_blob, 'relabel': relabel,
                        'limits': len(production['limits'])},
        'ledger': migration['qualification']['classes'],
        'project_models': {m['reference']: {'candidate': m['candidate']['path'], 'sha256': m['candidate']['sha256']}
                           for m in models['models']}}
    root.copied = dict(sorted(root.copied.items()))
    (out / 'reconstruction.json').write_text(text({'copied': root.copied, 'summary': summary}))
    return summary


def check(agent_ee):
    """Rebuild in a fresh directory and compare every generated file with the committed copy."""
    with tempfile.TemporaryDirectory(prefix='pod-capture-check-') as tmp:
        summary = build(Path(tmp) / 'root', agent_ee)
        differ = [n for n in GENERATED + ['../reconstruction.json']
                  if (Path(tmp) / 'root/composition' / n).read_bytes() != (HERE / 'composition' / n).read_bytes()]
    if differ:
        raise SystemExit('differs from the committed capture: ' + ', '.join(differ))
    print(json.dumps(summary, indent=1, sort_keys=True))
    print('production capture reproduces byte for byte')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('agent_ee')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--out', type=Path)
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--mechanical-reservations', action='store_true',
                        help='AGENTEE-489: bind agentee-489-source/reservations.json into the envelope (--out only)')
    parser.add_argument('--stackup-materials', action='store_true',
                        help='AGENTEE-485 G3: declared dielectric materials into the envelope stackup (--out only)')
    args = parser.parse_args()
    if args.check and (args.mechanical_reservations or args.stackup_materials):
        parser.error('--check reproduces the committed capture, which does not opt in')
    if args.check:
        check(args.agent_ee)
    else:
        print(json.dumps(build(args.out, args.agent_ee, args.mechanical_reservations, args.stackup_materials), indent=1, sort_keys=True))
