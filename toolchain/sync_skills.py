#!/usr/bin/env python3
"""Generate the project's agent skills from the vendored upstream checkouts:
the pinned kicad-happy checkout and the KRT (KiCadRoutingTools) checkout,
which follows KRT's latest release (see toolchain/ROUTING.md).

    toolchain/sync_skills.py          regenerate .agents/skills/kicad-happy-* and
                                      the .claude/skills symlinks
    toolchain/sync_skills.py --check  exit 1 if anything differs (used by doctor)

Follows the skillpack upstream-vendoring pattern: the upstream SKILL.md body is
copied verbatim; only the frontmatter is replaced (a prefixed `name`, so no
generic `kicad`/`spice`/`datasheets` names collide with other skills, and a
short house `description`). A small, clearly marked project header is inserted
above the upstream body. The upstream LICENSE and an UPSTREAM.json provenance
record are written next to each SKILL.md. Scripts and references stay in the
pinned checkout (toolchain/vendor/kicad-happy), which the header names as the
skill path, so upstream's sibling-relative imports keep working.

Skill directories:
  .agents/skills/<name>/  read by Codex, Antigravity (agy) and OpenCode
  .claude/skills/<name>   symlink to the above, read by Claude Code (and OpenCode)
"""
import hashlib
import json
import sys
import tempfile
import tomllib
from pathlib import Path

TOOLCHAIN = Path(__file__).resolve().parent
REPO = TOOLCHAIN.parent
VENDOR = TOOLCHAIN / "vendor" / "kicad-happy"
AGENTS = REPO / ".agents" / "skills"
CLAUDE = REPO / ".claude" / "skills"
PREFIX = "kicad-happy-"

DESCRIPTIONS = {
    "kicad": ("Use for structured KiCad schematic/PCB analysis of fome-mc designs with the pinned "
              "kicad-happy analyzers; see body for the skill path, project overrides, and analyzer usage."),
    "spice": ("Use to simulate analog subcircuits detected by kicad-happy schematic analysis with ngspice "
              "in fome-mc; see body for paths, project overrides, and result fields."),
    "datasheets": ("Use to extract and verify structured specs from component datasheet PDFs with the "
                   "kicad-happy pipeline in fome-mc; see body for paths, local PDF tools, and project overrides."),
}

HEADER = """<!-- BEGIN fome-mc local adaptation (toolchain/sync_skills.py; do not edit by hand) -->
> **fome-mc local adaptation.** Upstream: kicad-happy `{tag}` (`{commit}`), skill
> `{skill}`, MIT licence (see `LICENSE`). The text below the marker is upstream's,
> verbatim. Where it conflicts with this header, this header wins.
>
> - **`<skill-path>`** means `toolchain/vendor/kicad-happy/skills/{skill}` (relative to
>   the fome-mc repo root; created by `make bootstrap`). Run scripts from there with
>   `toolchain/.venv/bin/python -I <skill-path>/scripts/<script>.py`; read upstream
>   `references/` from there too. Do not copy the scripts elsewhere — they import
>   sibling skills by relative path.
> - Sibling skills: `kicad` → `kicad-happy-kicad`, `spice` → `kicad-happy-spice`,
>   `datasheets` → `kicad-happy-datasheets`. The `emc`, `bom` and distributor skills
>   (`digikey`, `mouser`, `lcsc`, `element14`, `jlcpcb`, `pcbway`) are **not installed**
>   in this project; their sourcing, ordering and API conventions do not apply here.
> - Prefer the project entry points (`make analyze`, `make erc`, `make drc`, …; see the
>   `fome-eda-toolchain` skill). They run on snapshots and record versions and hashes.
> - KiCad's own ERC/DRC (`kicad-cli`) are the authoritative native checks. kicad-happy
>   findings supplement them and never replace or suppress them.
> - Analysis is read-only: do not edit, refill, upgrade or re-save design files, and do
>   not change component selections, while following this skill.
> - Upstream's review workflow (mandatory EMC/SPICE steps, report format, "verified"
>   wording) is upstream's default, not this project's review process.
<!-- END fome-mc local adaptation -->

"""


KRT = TOOLCHAIN / "vendor" / "krt"
KRT_PREFIX = "krt-"
KRT_SKILLS = {
    "diagnose-routing-failures": ("Use after a fome-mc routing attempt (make route / route.py) leaves nets "
                                  "unrouted or fails validation: root-cause it from the run directory and plan "
                                  "the next attempt; see body for the project mapping."),
    "review-routed-board": ("Use to review a routed fome-mc candidate beyond the wrapper's native grading "
                            "(orphan stubs, dangling vias, length/diff-pair/return-via checks); see body "
                            "for paths and the project mapping."),
}
KRT_HEADER = """<!-- BEGIN fome-mc local adaptation (toolchain/sync_skills.py; do not edit by hand) -->
> **fome-mc local adaptation.** Upstream: KiCadRoutingTools `{describe}` (`{commit}`),
> skill `{skill}`, MIT licence (see `LICENSE`). The text below the marker is upstream's,
> verbatim. Where it conflicts with this header, this header wins. Load the
> `fome-pcb-routing` skill first: it defines how routing runs in this project.
>
> - **Paths.** Upstream's `py_router/…` and `py_tools/…` are under `toolchain/vendor/krt/`;
>   run them as `toolchain/.venv-route/bin/python -X utf8 toolchain/vendor/krt/py_router/<tool>.py`.
> - **Logs.** Upstream's `/tmp/<step>.txt` captures are already in each run directory
>   `build/runs/route/<project>/<label>/<stamp>/`: `work/krt.log` (full KRT output,
>   including `JSON_SUMMARY`), `work/krt-out/summary.json`, `work/freerouting.log` and
>   `work/freerouting-result.json`. The candidate is `candidate/<project>/<board>`; the
>   untouched input is `reference/<project>/<board>`.
> - **Retries go through the wrapper.** Express every retry as
>   `make route BACKEND=… ARGS='…'` / `toolchain/route.py run …`, passing KRT flags with
>   `--backend-arg` and `KICAD_*` knobs with `--backend-env`. Never route the real design
>   in place, and never run KRT on files outside a run directory.
> - **No relaxation.** Do not use or suggest `--escalation board|fab`, `--fab-tier
>   advanced|auto`, `--fab-overrides` that lower a floor, `--clearance-ceiling`,
>   `--relax-drc-severities`, lowering `--track-width`/`--via-size`/`--clearance` below the
>   net class, or re-enabling `KICAD_TERMINAL_ESCALATION`. Tightening is fine.
> - **Grading.** The pass/fail verdict is `result.json` from the wrapper: KiCad's own DRC
>   with schematic parity against the input's unchanged rules, plus the preservation
>   checks. KRT's `check_*` tools are supplementary diagnostics; run them on the candidate
>   (its `.kicad_pro` is the original). Ignore upstream steps about the plugin GUI.
<!-- END fome-mc local adaptation -->

"""


def krt_provenance():
    import subprocess

    def git(*args):
        r = subprocess.run(["git", "-C", str(KRT), *args], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    return {"describe": git("describe", "--tags", "--always"), "commit": git("rev-parse", "HEAD")}


def render_krt(dest_root):
    """KRT's routing-analysis skills; skipped (returns []) when KRT is not installed."""
    if not (KRT / ".claude" / "skills").is_dir():
        return []
    prov = krt_provenance()
    license_text = (KRT / "LICENSE").read_text()
    names = []
    for skill, desc in KRT_SKILLS.items():
        raw = (KRT / ".claude" / "skills" / skill / "SKILL.md").read_text()
        _, body = split_frontmatter(raw)
        name = KRT_PREFIX + skill
        out = dest_root / name
        out.mkdir(parents=True, exist_ok=True)
        (out / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {json.dumps(desc)}\n---\n\n"
            + KRT_HEADER.format(skill=skill, **prov) + body.lstrip("\n"))
        (out / "LICENSE").write_text(license_text)
        (out / "UPSTREAM.json").write_text(json.dumps({
            "upstream": "https://github.com/drandyhaas/KiCadRoutingTools",
            "describe": prov["describe"], "commit": prov["commit"],
            "skill_subdir": f".claude/skills/{skill}",
            "upstream_skill_md_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "license": "MIT",
            "update": "follows the installed KRT release; regenerated by `make route-update`",
            "adaptations": [
                f"frontmatter name {skill!r} -> {name!r} (avoid generic skill-name collisions)",
                "frontmatter description replaced with a short house description",
                "project header inserted above the verbatim upstream body",
                "tools stay in toolchain/vendor/krt (not copied)",
            ],
        }, indent=2) + "\n")
        names.append(name)
    return names


def pins():
    with open(TOOLCHAIN / "versions.toml", "rb") as f:
        return tomllib.load(f)["upstream"]["kicad-happy"]


def split_frontmatter(text):
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md has no frontmatter")
    end = text.index("\n---\n", 4)
    return text[4:end], text[end + 5:]


def render(dest_root, pin):
    """Write the generated skill directories under dest_root."""
    import subprocess
    head = subprocess.run(["git", "-C", str(VENDOR), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if head != pin["commit"]:
        raise SystemExit(f"kicad-happy checkout is at {head or 'nothing'}, pinned {pin['commit']}; run make bootstrap")
    license_text = (VENDOR / "LICENSE").read_text()
    for skill in pin["skills"]:
        upstream = VENDOR / "skills" / skill / "SKILL.md"
        raw = upstream.read_text()
        _, body = split_frontmatter(raw)
        name = PREFIX + skill
        out = dest_root / name
        out.mkdir(parents=True, exist_ok=True)
        desc = DESCRIPTIONS[skill]
        (out / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {json.dumps(desc)}\n---\n\n"
            + HEADER.format(tag=pin["tag"], commit=pin["commit"], skill=skill) + body.lstrip("\n"))
        (out / "LICENSE").write_text(license_text)
        (out / "UPSTREAM.json").write_text(json.dumps({
            "upstream": pin["url"],
            "tag": pin["tag"],
            "commit": pin["commit"],
            "skill_subdir": f"skills/{skill}",
            "upstream_skill_md_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "license": pin["license"],
            "adaptations": [
                f"frontmatter name {skill!r} -> {name!r} (avoid generic skill-name collisions)",
                "frontmatter description replaced with a short house description",
                "project header inserted above the verbatim upstream body",
                "scripts/references stay in toolchain/vendor/kicad-happy (not copied)",
            ],
        }, indent=2) + "\n")


def tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def main():
    pin = pins()
    check = "--check" in sys.argv[1:]
    names = [PREFIX + s for s in pin["skills"]]
    if check:
        problems = []
        with tempfile.TemporaryDirectory() as tmp:
            render(Path(tmp), pin)
            krt_names = render_krt(Path(tmp))
            if not krt_names:
                print("NOTE krt-* skills not checked: toolchain/vendor/krt is not installed (make route-update)")
            for name in names + krt_names:
                if not (AGENTS / name).exists() or tree(Path(tmp) / name) != tree(AGENTS / name):
                    problems.append(f"{name}: generated content differs (run toolchain/sync_skills.py)")
        for d in sorted(AGENTS.iterdir()) if AGENTS.exists() else []:
            link = CLAUDE / d.name
            if not (link.is_symlink() and link.resolve() == d.resolve()):
                problems.append(f".claude/skills/{d.name} is not a symlink to .agents/skills/{d.name}")
        for p in problems:
            print("DRIFT", p)
        print("skills: OK" if not problems else f"skills: {len(problems)} problem(s)")
        return 1 if problems else 0
    render(AGENTS, pin)
    krt_names = render_krt(AGENTS)
    names = names + krt_names
    CLAUDE.mkdir(parents=True, exist_ok=True)
    for d in sorted(AGENTS.iterdir()):
        link = CLAUDE / d.name
        if link.is_symlink() or link.exists():
            if not link.is_symlink():
                raise SystemExit(f"refusing to replace real directory {link}")
            link.unlink()
        link.symlink_to(Path("..") / ".." / ".agents" / "skills" / d.name)
    for link in CLAUDE.iterdir():
        if link.is_symlink() and not link.exists():
            link.unlink()  # prune links to removed skills
    print("skills: generated", ", ".join(names), "and .claude/skills links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
