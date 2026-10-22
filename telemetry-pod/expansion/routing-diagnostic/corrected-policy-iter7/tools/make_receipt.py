"""make_receipt.py: write ../policy-receipt.json from the retained files and ../evidence/.

Every hash is computed here from the files; nothing is typed in. Reads only; run after prove.sh
has PASSed and its rule-area-inspection.json / fixtures.json were copied into ../evidence/.
"""
import gzip, hashlib, json, subprocess
from pathlib import Path

here = Path(__file__).resolve().parent.parent
diag = here.parent                      # telemetry-pod/expansion/routing-diagnostic
expansion = diag.parent
repo = Path(subprocess.run(["git", "-C", str(here), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, check=True).stdout.strip())
rel = lambda p: str(p.relative_to(repo))
sha = lambda b: hashlib.sha256(b).hexdigest()
fsha = lambda p: sha(Path(p).read_bytes())

src_pcb = gzip.decompress((here / "source/ca2.kicad_pcb.gz").read_bytes())
snap = json.loads((diag / "iteration-7/candidate/iter8d-campaign-r0/snapshot.json").read_text())
planes = json.loads((diag / "iteration-7/planes/result.json").read_text())
constraints_p = expansion / "design-rules/constraints.json"
dpcb = json.loads(constraints_p.read_text())["decisions_pending_next_seed"]
inspection = json.loads((here / "evidence/rule-area-inspection.json").read_text())
fixtures = json.loads((here / "evidence/fixtures.json").read_text())
silk = expansion / "placement-candidate/iteration-7/candidate-silk-policy.kicad_pcb.gz"
kicad_cli = subprocess.run(["kicad-cli", "--version"], capture_output=True, text=True, check=True).stdout.strip()
areas = {a["name"]: a for a in inspection["rule_areas"]}

source = {"pcb": sha(src_pcb), "pro": fsha(here / "ca2.kicad_pro"), "dru": fsha(here / "ca2.kicad_dru")}
assert source == {"pcb": snap["files"]["ca2.kicad_pcb"], "pro": snap["files"]["ca2.kicad_pro"],
                  "dru": snap["files"]["ca2.kicad_dru"]}, "retained source differs from the archived snapshot"

receipt = {
    "schema": "corrected-policy-iter7/policy-receipt/1",
    "label": "corrected-policy diagnostic input, not a production placement",
    "item": "KICADROUTE-91 (M1b), corrected-policy diagnostic input slice only; the item is not complete",
    "authority": "coordinator agent-509 ruling 2026-10-21 (plan M1): immutable corrected-policy diagnostic input "
                 "from the archived iteration-7 microSD routing input; agent-507 owns baseline identity and routing acceptance",
    "claims_not_made": [
        "not a production or adopted placement",
        "no routing was run on this input; no routed-success or optimisation claim",
        "no routability comparison is made or supported: no sidecar versioning, effective-configuration binding or "
        "mismatch refusal exists for this input",
        "the historical 203/235 result and the 55/32 and 51/30 counts are measurements on the historical source 67782a5d, "
        "not defects in themselves; none is a current-policy qualification of this input or of any route, and nothing here "
        "regrades them (see superseding_annotation)",
        "allowed_trace_layers and allowed_via_spans are summaries; the native rule areas are the enforcement",
    ],
    "open_items": [
        "G1: remaining M1b work: effective-configuration/build/budget identity binding, comparison refusal, "
        "argument-difference exposure and agent-ee boundary integration",
        "G2: the corrected PCB fe533602 needs fresh current-policy grading; the historical routes are not current-policy "
        "qualification and the KICADROUTE-98 partition proof covers the historical source 67782a5d only",
        "G3: the single corrected-policy route (900-second backend ceiling plus measured grade/grace) has not been run",
    ],
    "source": {
        "role": "iteration-7 microSD routing input: the planed board kicad-route campaign iter8d-campaign r0 routed; the historical 203-of-235 count belongs to that campaign and is not a result of this fixture",
        "original_path": snap["source_dir"],
        "files_sha256": {"ca2.kicad_pcb": source["pcb"], "ca2.kicad_pro": source["pro"], "ca2.kicad_dru": source["dru"]},
        "retained_copy": {"source/ca2.kicad_pcb.gz": fsha(here / "source/ca2.kicad_pcb.gz"),
                          "note": "gzip -9n of the archived board; .kicad_pro/.kicad_dru are byte-identical to ../ca2.kicad_pro/.kicad_dru"},
        "identity_chain": [
            {"file": rel(diag / "SHA256SUMS"), "check": "sha256sum -c of its 30 ./iteration-7/ entries: all OK (commit 7c6c678; "
             "iteration-7/ has no README or SHA256SUMS of its own)"},
            {"file": rel(diag / "iteration-7/candidate/iter8d-campaign-r0/snapshot.json"),
             "sha256": fsha(diag / "iteration-7/candidate/iter8d-campaign-r0/snapshot.json"),
             "binds": "ca2.kicad_pcb/.kicad_pro/.kicad_dru hashes of the campaign r0 input and its source_dir"},
            {"file": rel(diag / "iteration-7/campaign.json"), "sha256": fsha(diag / "iteration-7/campaign.json"),
             "binds": "input.dir " + json.loads((diag / "iteration-7/campaign.json").read_text())["input"]["dir"]},
            {"file": rel(diag / "iteration-7/planes/result.json"), "sha256": fsha(diag / "iteration-7/planes/result.json"),
             "binds": "kicad-route planes input board " + planes["input"]["files"]["ca2.kicad_pcb"] + " -> output " + source["pcb"]},
        ],
        "origin": {
            "placement_board": {"file": rel(silk), "gz_sha256": fsha(silk), "sha256": sha(gzip.decompress(silk.read_bytes())),
                                "equals_planes_input": sha(gzip.decompress(silk.read_bytes())) == planes["input"]["files"]["ca2.kicad_pcb"]},
            "project": {"file": rel(expansion / "design-rules/board-setup.kicad_pro"),
                        "sha256": fsha(expansion / "design-rules/board-setup.kicad_pro"),
                        "equals_source_pro": fsha(expansion / "design-rules/board-setup.kicad_pro") == source["pro"]},
            "rules": {"file": rel(expansion / "design-rules/telemetry-pod.kicad_dru"),
                      "sha256": fsha(expansion / "design-rules/telemetry-pod.kicad_dru"),
                      "equals_source_dru": fsha(expansion / "design-rules/telemetry-pod.kicad_dru") == source["dru"]},
            "plane_plan": {"file": rel(expansion / "design-rules/planes.json"), "sha256": fsha(expansion / "design-rules/planes.json"),
                           "equals_planes_receipt": fsha(expansion / "design-rules/planes.json") == planes["input"]["plan_sha256"]},
        },
    },
    "output": {
        "files_sha256": {n: fsha(here / n) for n in ("ca2.kicad_pcb", "ca2.kicad_pro", "ca2.kicad_dru")},
        "pro_dru_unchanged": fsha(here / "ca2.kicad_pro") == source["pro"] and fsha(here / "ca2.kicad_dru") == source["dru"],
        "board_change": "evidence/source-to-corrected.diff: one insertion of two (zone ...) rule areas, 62 lines added, 0 removed; "
                        "every footprint, net, net class, track/via setting, copper zone and fill is byte-identical",
        "diff_sha256": fsha(here / "evidence/source-to-corrected.diff"),
        "built_by": "tools/build_corrected.py (pcbnew, one SaveBoard; deterministic UUIDs, rebuild is byte-identical)",
    },
    "decisions": {
        "file": rel(constraints_p), "sha256": fsha(constraints_p), "key": "decisions_pending_next_seed",
        "D-PCB-6": dpcb["D-PCB-6 RF reference keep-out"],
        "D-PCB-7": dpcb["D-PCB-7 plane layers carry no tracks"],
    },
    "geometry_binding": {
        "captured_for": "D-PCB-6: GNSS line from the U3 RF pad (77.5, 29.1) to the J2 pin (86.96, 28.0)",
        "archived_board": {"U3": "RF_GPS:ublox_NEO at (71.5, 35.0) rot 180, locked; pad 11 /POD_GNSS_RF at (77.5, 29.1)",
                           "J2": "SMA_Molex_73251-1153_EdgeMount_Horizontal at (85.24, 28.0) rot 180, locked; pad 1 /POD_GNSS_RF at (86.96, 28.0)",
                           "board_outline": "Edge.Cuts rectangle (0,0)-(90,65) mm, 4 lines"},
        "match": True,
        "corridor_used": "x 76..88, y 26.5..30.6 mm, unchanged from constraints.json",
    },
    "rule_areas": inspection["rule_areas"],
    "inspection": {"method": "pcbnew reload of a copy (tools/inspect_rule_areas.py); reload+SaveBoard is byte-identical to ca2.kicad_pcb",
                   "file": "evidence/rule-area-inspection.json", "sha256": fsha(here / "evidence/rule-area-inspection.json")},
    "native_enforcement": {
        "fixtures": "evidence/fixtures.json", "sha256": fsha(here / "evidence/fixtures.json"), "verdict": fixtures["verdict"],
        "bases_identical": fixtures["bases_identical"],
        "summary": {k: {"added": v["added"], "items_not_allowed": v["got_items_not_allowed"], "verdict": v["verdict"]}
                    for k, v in fixtures["fixtures"].items()},
    },
    "tools": {"kicad_cli": kicad_cli, "pcbnew": kicad_cli, "pinned": "toolchain/versions.toml kicad_cli_version 10.0.7"},
    "routability_policy": {
        "schema": "routability-policy/1",
        "experiment_class": "current-policy",
        "allowed_trace_layers": ["F.Cu", "In2.Cu", "B.Cu"],
        "allowed_via_spans": [["F.Cu", "B.Cu"]],
        "allowed_via_spans_basis": "the input defines only through vias (Default net class 0.6/0.3 mm; no blind, buried or micro via class)",
        "trace_layer_restriction_enforced_by": {"rule_area": "D-PCB-7v2 In1.Cu no tracks (board outline)",
                                                "uuid": areas["D-PCB-7v2 In1.Cu no tracks (board outline)"]["uuid"]},
        "spatial_exclusions": [{"name": "D-PCB-6 RF reference keep-out",
                                "uuid": areas["D-PCB-6 RF reference keep-out"]["uuid"],
                                "layers": ["In1.Cu", "In2.Cu"], "forbids": ["tracks", "vias"],
                                "polygon_mm": areas["D-PCB-6 RF reference keep-out"]["polygon_mm"],
                                "enforced_by": "native KiCad rule area in ca2.kicad_pcb"}],
        "statement": "The spatial RF exclusion (D-PCB-6) is enforced by the native rule area, not by allowed_via_spans: "
                     "allowed_via_spans is a summary of layer pairs only and cannot express a region. Through vias are allowed on "
                     "In1.Cu everywhere outside the D-PCB-6 polygon. allowed_trace_layers is a summary of the native "
                     "D-PCB-7v2 rule area, which is what KiCad DRC grades.",
    },
    "disclosed_limits": [
        "RF_50 rule 'agent_ee_netclass_RF_50' is inactive: it matches no net on this input",
        "historical results (203/235, 55/32, 51/30) are measurements on source 67782a5d; they are not current-policy qualification, and the changed policy requires new grading on fe533602",
        "the kicad-route builtin engine was reported not to honour inner-layer rule areas; any route must be graded by native DRC",
        "fixture DRC runs use an empty KICAD_CONFIG_HOME, so the bases include 199 lib_footprint_issues, 13 isolated-copper findings and 499 unconnected items; verdicts are deltas against each fixture's base, not a clean or connected design result",
    ],
    "receipt_history": [
        {"commit": "7e6fb02", "note": "first version; wording of README, this receipt and make_receipt.py was stale (baseline/routability framing, historical counts not marked unresolved, allowed_via_spans not called a summary)",
         "sha256_at_that_commit": {"README.md": "32bbbfc7d79814ce8cf1c95d010c3b0e23e7eaef9f131d737ac5c4e3c11ad3b6",
                                   "policy-receipt.json": "0df61bbeed1521c5eea23e4f13745160358b5e889ca93f11f269bdb7794f7d32",
                                   "tools/make_receipt.py": "8134b7496009d5336ba2da8fd0187f16ef197936df6adfc76b378ab5255ffbbd",
                                   "SHA256SUMS": "ced10d96ab144aab5707fe4a6a3a1ecd8c417facf369e2c2fe44339db5a207d5"}},
        {"commit": "c0e811e", "note": "first wording correction; its text called the 55/32, 51/30 counts and the ten lost nets unresolved and ineligible for promotion, an inference superseded by superseding_annotation. Its receipt is preserved in git history and is not rewritten",
         "sha256_at_that_commit": {"README.md": "3976552305d9ac005d9ca94b451d32f50e17787824bd17cf6f68fb39c6670f8d",
                                   "policy-receipt.json": "b96fb490fac183a9b590e51250531b6166bcc6f950a29c39d26bc5d9300c449b",
                                   "tools/make_receipt.py": "b036cf1a87453aa69531c1955509b62e2fe046465d039234f09ca030aab1a00d",
                                   "SHA256SUMS": "e0b6d15ee4471cb1efe971f43055079ab2ee20225a5e853118ac162d3a3cd424"}},
        {"commit": "this commit (KICADROUTE-98 reconciliation)", "note": "wording and receipt metadata only; ca2.kicad_pcb, ca2.kicad_pro, ca2.kicad_dru, source/, evidence/ are byte-identical to 7e6fb02; adds superseding_annotation and corrects the rule-area statement in preserved_as_found"},
    ],
    "preserved_as_found": [
        "ca2.kicad_dru rule 'agent_ee_netclass_RF_50' (track_width min 0.335 mm for net class RF_50) is unchanged; "
        "this input's .kicad_pro defines only the Default class, so /POD_GNSS_RF is Default and that rule matches nothing. "
        "Not altered: width and net-class changes are out of scope.",
        "the source (67782a5d) has 0 BOARD-owned rule areas and 6 FOOTPRINT-owned keepouts (U1 ESP32-S3-WROOM-1: 1; J3 microSD: 5), counted from the decompressed source/ca2.kicad_pcb.gz; their original bytes remain in ca2.kicad_pcb. The two rule areas added here are the only BOARD-owned rule areas; the source does not have zero rule areas globally (the planes receipt's 'keepouts: 0 rule areas' counted board zones only)",
    ],
    "superseding_annotation": {
        "supersedes": "the capped-report inference in earlier receipts and in the c0e811e wording: that the ten lost nets and the 55/32, 51/30 counts were unresolved because the native DRC unconnected list is capped at 499 and so could not show completion. Only that inference is superseded; the receipts containing it are preserved unchanged in git history (7e6fb02, c0e811e)",
        "superseded_by": {
            "repository": "kicad-route",
            "commit": "367578e4c303c02580d338af5ae829a39495ab57",
            "report": "reports/routability-m1-20261021/krt98/README.md",
            "report_sha256": "0a77dac66214348736ec297af32da32a64b8dd13da8fcfd3b64042b383e3b93b",
            "evidence_archive": "reports/routability-m1-20261021/krt98/evidence.tar.gz",
            "evidence_archive_sha256": "f7d030f6d15347f4aae2a5aa5e93cbf72e475d773b4b463f3be7fcfc583ae779",
            "evidence_index": "reports/routability-m1-20261021/krt98/evidence-index.json",
            "evidence_index_sha256": "818113e264a9a42420e7bb793aca4c5e9dea30246a5b94373edf8a2661be91ef",
            "historical_verification": "reports/routability-m1-20261021/krt98/historical-verification.json",
            "historical_verification_sha256": "974e3e65a9bc1c7e75e3bf1bf8e50abe1d6aaeb0ccc76cde8955fd3902049f0b",
            "members_under_independent_verification": {
                "origin-production-terminals.json": "2aeacb0eef3cc15a2d23fc534eb774b6b9adf07a3c6d6258f7591557532b2b12",
                "production-ratchet-verification.json": "d13ab416c85d63e101d7e395a2bf92c18c9d95b85fe1ccbb930214deed535b03",
                "independent-equivalence-expectations.json": "6355b5c2f31144fa0a4d607128e8d469fc52b10e867e9b87e76fcd831eabed6c"},
            "hashes_recomputed": "sha256sum of the files at that commit (git show 367578e4:<path>) and of the members extracted from evidence.tar.gz"
        },
        "input_identity_report": {
            "repository": "kicad-route",
            "commit": "967891c9408047eb5106f4fc3303b8fecb5b19c1",
            "path": "reports/routability-m1-20261021/krt91-input-identity/identity.json",
            "sha256": "2ecccfae2b7a3b4cf2cdcc05f78a96f83ff7134d69c80102e2f42bad579e166a",
            "confirms": "source 67782a5d, pro 7c7933bf, dru ff622083 agree across the gzip, live archive, committed snapshot, campaign and planes output; corrected fe533602 is a pure 62-line insertion with pro/dru identical"},
        "partition_findings": {
            "scope": "historical source 67782a5d8ff7ce3c21dbe90b6f50c2735e4827231f3f474c9db4522de43ca73f and its two archived routed results; 235 terminal-net UUID partitions each",
            "origin_complete_nets": 53,
            "origin_terminal_deficit": 686,
            "result_complete_nets": [203, 205],
            "result_terminal_deficits": [55, 51],
            "all_53_complete_origin_nets_preserved": True,
            "partial_groups_on_incomplete_nets_preserved": 5,
            "ten_alleged_lost_nets": "all ten were already incomplete in the origin; none was a net that was complete and then lost",
            "earlier_inferred_origin_complete_count": "155, from absence in the capped report; superseded by 53",
            "historical_counts_status": "the 55/32 and 51/30 figures are measurements, not defects in themselves"
        },
        "remaining_ineligibility": [
            "the changed policy (current layer policy, native rule areas) requires new grading: this input has had none",
            "historical routes are not current-policy qualification",
            "the KICADROUTE-98 partition proof covers the historical source 67782a5d only; the corrected PCB fe533602 (a pure 62-line insertion) still needs fresh policy grading",
            "no genuine native or policy finding is cleared by this annotation (including the DRC findings in disclosed_limits and the inactive RF_50 rule)",
            "KICADROUTE-91 remains unreleased; G1 and G3 stay open"
        ],
    },
}
(here / "policy-receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")
print("policy-receipt.json written; fixtures", fixtures["verdict"])
