#!/usr/bin/env python3
"""Export the pinned agent-ee src/ and print its path.

The pin is [upstream.agent-ee] in toolchain/versions.toml. The export is read from the
local checkout's object store with `git archive <commit> src`. The checkout's working tree
and HEAD are never used or changed. The export goes to build/agent-ee/<commit>/src and is
reused while its recorded tree id still matches the commit.
"""
import io
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def pin() -> dict:
    with open(REPO / "toolchain/versions.toml", "rb") as f:
        return tomllib.load(f)["upstream"]["agent-ee"]


def pinned_src() -> Path:
    declared = pin()
    checkout = Path(declared["repo"]).expanduser()
    commit = declared["commit"]
    git = ["git", "-C", str(checkout)]
    tree = subprocess.run(git + ["rev-parse", "--verify", "--quiet", f"{commit}^{{tree}}"],
                          capture_output=True, text=True, check=False).stdout.strip()
    if not tree:
        raise SystemExit(f"agent-ee pin {commit} is not in {checkout}")
    root = REPO / "build/agent-ee" / commit
    marker = root / "TREE"
    if not (marker.is_file() and marker.read_text().strip() == tree):
        archive = subprocess.run(git + ["archive", commit, "src"], capture_output=True, check=True).stdout
        tmp = root.with_name(commit + ".tmp")
        subprocess.run(["rm", "-rf", str(tmp), str(root)], check=True)
        tmp.mkdir(parents=True)
        tarfile.open(fileobj=io.BytesIO(archive)).extractall(tmp, filter="data")
        (tmp / "TREE").write_text(tree + "\n")
        tmp.rename(root)
    return root / "src"


if __name__ == "__main__":
    print(pinned_src())
    sys.exit(0)
