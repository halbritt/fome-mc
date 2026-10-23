"""AGENTEE-485 X1: the explicit REQUIRED preparation stages of pipeline.py.

A refused, missing or unclassified required stage invalidates the candidate: pipeline.py still writes pipeline.json
(every stage record and the diagnostics stay retained) but exits non-zero, `runtime_receipt.py write` refuses to
record a receipt for it and launch.py refuses to launch it. Every stage pipeline.py runs is classified here; a stage
that is not named refuses as unclassified, so a new stage cannot silently become optional. Diagnostics
(pipeline.json `diagnostics`) are scratch-only and are not stages.

The set names at least the five stages of the 530 dispatch (scope locality binding, validate_plan, block candidate
repack, stage-owned C1 variants, authorized budget) plus every other stage whose refusal invalidates the prepared
candidate. There is no OPTIONAL class: at this head every stage pipeline.py runs is required.
"""

SCHEMA = 'pod-capture.required-stages/1'
REQUIRED = (
    # The five the 530 dispatch names (AGENTEE-485 slice A, X1).
    'placement.scope_locality_binding',
    'pod_driver.validate_plan',
    'placement.block_candidates_repack',
    'blocks.stage_owned_variants C1 (AGENTEE-485 R2)',
    'campaign.authorized_budget production scope',
    # Every other stage whose refusal invalidates the candidate.
    'scope.envelope_obligation_coverage',
    'placement.scope_envelope_binding',
    'binding_fill.configuration',
    'binding_fill.fill',
    'scaffold.scaffold production scope',
    'scaffold.write_envelope_content production scope',
    'scaffold.content_step',
    'schematic_stage.configuration',
    'add_planes.step',
    'producers.import_from_declared_mount',
    'placement.refuse_policy_sources',
    'placement.envelope_overhangs',
    'placement.policy_vs_subjects',
    'engine.placement_adapter.blocks_request (AGENTEE-439 G1)',
    'routing_adapter.preflight (agent-ee 7d5b0d4d, ROUTER_CHECKOUT)',
    'pod_driver.build(dry_run) production scope',
    'pod_driver.rating_provenance',
    'emission.schematic_stage production (AGENTEE-445)',
    'models.candidate_resolution (FOMEMC-34)',
    'fab.copper_features JP1-JP5 (agent-509 ruling)',
    'j1.native_inspection (agent-509 iter8t audit, AGENTEE-446)',
    'campaign.initial_candidate',
    'review.packet_obligations production scope',
    'scope.block_obligations production scope',
)


def problems(stages):
    """Every reason the stage records (pipeline.json `stages`) do not make a valid candidate; [] when valid."""
    if not isinstance(stages, dict):
        return ['pipeline.json has no stage records']
    found = []
    for name in REQUIRED:
        record = stages.get(name)
        if record is None:
            found.append(f'required stage {name!r} is missing')
        elif record.get('status') != 'accepted':
            found.append(f'required stage {name!r} is {record.get("status")!r}: {str(record.get("error", ""))[:300]}')
    found += [f'stage {name!r} is not classified in required_stages.REQUIRED' for name in stages if name not in REQUIRED]
    return found


def summary(stages):
    """The record pipeline.json carries: the required set, its refusals and the verdict."""
    found = problems(stages)
    return {'schema': SCHEMA, 'required': list(REQUIRED), 'problems': found, 'valid_candidate': not found}
