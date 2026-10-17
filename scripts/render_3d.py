#!/usr/bin/env python3
"""Delegate native 3D rendering to agent-ee and publish validated FOME images."""

import argparse
import hashlib
import json
import os
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BOARD = "fome-mc.kicad_pcb"
VIEWS = ("top", "bottom", "isometric")
MANIFEST = "render-manifest.json"


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def png_dimensions(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    offset, dimensions, compressed = 8, None, bytearray()
    while offset < len(data):
        if offset + 12 > len(data):
            break
        length, kind = struct.unpack_from(">I4s", data, offset)
        end = offset + length + 12
        if end > len(data):
            break
        chunk = data[offset + 8:end - 4]
        crc = struct.unpack_from(">I", data, end - 4)[0]
        if zlib.crc32(kind + chunk) != crc:
            raise ValueError(f"PNG checksum mismatch: {path}")
        if dimensions is None:
            if kind != b"IHDR" or length != 13:
                break
            dimensions = struct.unpack_from(">II", chunk)
            if not all(dimensions):
                break
            depth, color, compression, filtering, interlace = chunk[8:]
            valid_depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
            if depth not in valid_depths.get(color, ()) or compression or filtering or interlace:
                raise ValueError(f"unsupported native PNG format: {path}")
            channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
            row_bytes = (dimensions[0] * channels * depth + 7) // 8 + 1
        elif kind == b"IHDR":
            break
        if kind == b"IDAT":
            compressed.extend(chunk)
        if kind == b"IEND":
            if length == 0 and end == len(data) and compressed:
                expected = row_bytes * dimensions[1]
                decoder = zlib.decompressobj()
                try:
                    scanlines = decoder.decompress(compressed, expected + 1)
                except zlib.error as exc:
                    raise ValueError(f"invalid compressed PNG pixels: {path}") from exc
                if (not decoder.eof or decoder.unused_data or decoder.unconsumed_tail
                        or len(scanlines) != expected
                        or any(scanlines[offset] > 4 for offset in range(0, expected, row_bytes))):
                    raise ValueError(f"invalid PNG scanlines: {path}")
                return dimensions
            break
        offset = end
    raise ValueError(f"incomplete or malformed PNG: {path}")


def validated_images(repo, run):
    run = Path(run).resolve()
    manifest_path = run / MANIFEST
    if manifest_path.is_symlink():
        raise ValueError("render manifest must be a regular file")
    manifest = json.loads(manifest_path.read_text())
    if (not isinstance(manifest, dict) or manifest.get("schema") != "agent-ee.render3d/1"
            or manifest.get("status") != "completed" or manifest.get("source_unchanged") is not True
            or manifest.get("errors")):
        raise ValueError("a completed agent-ee.render3d/1 manifest is required")
    board = repo / BOARD
    expected_hash = sha256(board)
    source = manifest.get("board", {})
    if not isinstance(source, dict) or source.get("name") != BOARD or source.get("sha256") != expected_hash:
        raise ValueError("rendered board differs from the current FOME board")
    project = manifest.get("project")
    if (not isinstance(project, dict)
            or project.get("sha256") != sha256(board.with_suffix(".kicad_pro"))):
        raise ValueError("rendered project differs from the current FOME project")
    if "name" in project and project["name"] != board.with_suffix(".kicad_pro").name:
        raise ValueError("rendered project name differs from the current FOME project")
    images = manifest.get("images")
    if (not isinstance(images, list) or len(images) != len(VIEWS)
            or not all(isinstance(image, dict) for image in images)):
        raise ValueError("all three rendered images are required")
    by_view = {image.get("view"): image for image in images}
    if set(by_view) != set(VIEWS):
        raise ValueError("exactly top, bottom and isometric views are required")
    executions = manifest.get("views")
    if not isinstance(executions, dict) or set(executions) != set(VIEWS):
        raise ValueError("all three native view executions are required")
    files = []
    for view in VIEWS:
        image = by_view[view]
        name = f"{board.stem}-3d-{view}.png"
        if image.get("path") != name:
            raise ValueError(f"unexpected render path for {view}")
        path = run / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing regular render image: {name}")
        execution = executions[view]
        if not isinstance(execution, dict) or execution.get("status") != "completed":
            raise ValueError(f"view did not complete: {view}")
        if any(execution.get(key) != image.get(key) for key in ("path", "width", "height", "sha256")):
            raise ValueError(f"image record differs from view execution: {view}")
        dimensions = png_dimensions(path)
        if dimensions != (image.get("width"), image.get("height")):
            raise ValueError(f"render dimensions differ from manifest: {name}")
        if sha256(path) != image.get("sha256"):
            raise ValueError(f"render hash differs from manifest: {name}")
        files.append(path)
    return files + [manifest_path], {BOARD: expected_hash, "fome-mc.kicad_pro": project["sha256"]}


def run_backend(command, repo):
    # Give agent-ee time to stop its independently grouped native renderers and
    # finish the interrupted manifest before this adapter exits.
    process = subprocess.Popen(command, cwd=repo, start_new_session=True)
    try:
        return process.wait()
    except KeyboardInterrupt:
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            try:
                os.killpg(process.pid, signal.SIGINT)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                print("render-3d: backend did not stop within 20 seconds; forced shutdown", file=sys.stderr)
        finally:
            signal.signal(signal.SIGINT, previous_handler)
        raise


def render(repo, args):
    board = repo / BOARD
    source_hash = sha256(board)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    out = repo / "build/runs/project/fome-mc" / f"3d-renders-{stamp}"
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [args.agent_ee, "render3d", str(board), "--out", str(out),
               "--width", str(args.width), "--height", str(args.height),
               "--quality", args.quality, "--jobs", str(args.jobs), "--timeout", str(args.timeout),
               "--models", str(Path(args.models).expanduser().resolve())]
    if args.fetch_models:
        command.append("--fetch-models")
    returncode = run_backend(command, repo)
    if returncode:
        raise ValueError(f"agent-ee rendering failed (exit {returncode}); retained output: {out}")
    if sha256(board) != source_hash:
        raise ValueError(f"source board changed during rendering; refuse publication: {out}")
    validated_images(repo, out)
    print(f"Render run: {out}", flush=True)
    print(f"Publish after inspection: make render-3d-publish RUN={out}", flush=True)
    return out


def publish(repo, run):
    files, source_hashes = validated_images(repo, run)
    destination = repo / "docs/renders/3d"
    if destination.is_symlink():
        raise ValueError("render publication directory must not be a symlink")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".render-3d-", dir=destination.parent) as temporary:
        stage = Path(temporary)
        for source in files:
            target = destination / source.name
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise ValueError(f"publication target must be a regular file: {target}")
            shutil.copyfile(source, stage / source.name)
            if target.exists():
                shutil.copyfile(target, stage / (source.name + ".previous"))
        validated_images(repo, stage)
        if any(sha256(repo / name) != expected for name, expected in source_hashes.items()):
            raise ValueError("board or project changed before publication")
        destination.mkdir(exist_ok=True)
        installed = []
        try:
            # Publish the manifest last so it identifies the completed image set.
            for source in files:
                target = destination / source.name
                os.replace(stage / source.name, target)
                installed.append(target)
            if any(sha256(repo / name) != expected for name, expected in source_hashes.items()):
                raise ValueError("board or project changed during publication")
        except BaseException:
            for target in reversed(installed):
                backup = stage / (target.name + ".previous")
                if backup.exists():
                    os.replace(backup, target)
                else:
                    target.unlink()
            raise
    print(f"Published three views and manifest: {destination}", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    rendering = sub.add_parser("render")
    rendering.add_argument("--agent-ee", default="agent-ee")
    rendering.add_argument("--models", default="~/.cache/agent-ee/models")
    rendering.add_argument("--fetch-models", action="store_true")
    rendering.add_argument("--width", type=int, default=4096)
    rendering.add_argument("--height", type=int, default=3072)
    rendering.add_argument("--quality", choices=("basic", "high"), default="high")
    rendering.add_argument("--jobs", type=int, default=3)
    rendering.add_argument("--timeout", type=float, default=1200)
    publication = sub.add_parser("publish")
    publication.add_argument("run", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "render":
            render(REPO, args)
        else:
            publish(REPO, args.run)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"render-3d: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("render-3d: interrupted", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
