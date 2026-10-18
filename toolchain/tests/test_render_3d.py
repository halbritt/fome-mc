"""Isolated tests for render delegation and publication; no heavy renders."""

import argparse
import base64
import importlib.util
import json
import os
import signal
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/render_3d.py"
SPEC = importlib.util.spec_from_file_location("render_3d", SCRIPT)
render_3d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_3d)


def png(width=2, height=3, *, raw=None):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    pixels = raw if raw is not None else b"".join(b"\0" + b"\x40\x80\xc0\xff" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


class RenderPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.board = self.repo / render_3d.BOARD
        self.board.write_text("saved board")
        self.board.with_suffix(".kicad_pro").write_text("saved project")
        self.run = self.repo / "run"
        self.run.mkdir()
        self.manifest = {"schema": "agent-ee.render3d/1", "status": "completed", "source_unchanged": True, "errors": [],
                         "board": {"name": self.board.name, "path": str(self.board),
                                   "sha256": render_3d.sha256(self.board)},
                         "project": {"path": str(self.board.with_suffix(".kicad_pro")),
                                     "sha256": render_3d.sha256(self.board.with_suffix(".kicad_pro"))},
                         "images": [], "views": {}}
        for view in render_3d.VIEWS:
            name = f"fome-mc-3d-{view}.png"
            (self.run / name).write_bytes(png())
            image = {"view": view, "path": name, "width": 2, "height": 3,
                     "sha256": render_3d.sha256(self.run / name)}
            self.manifest["images"].append(image)
            self.manifest["views"][view] = {**image, "status": "completed"}
        self.save_manifest()
        self.destination = self.repo / "docs/renders/3d"
        self.destination.mkdir(parents=True)
        for name in [*(image["path"] for image in self.manifest["images"]), render_3d.MANIFEST]:
            (self.destination / name).write_bytes(b"previous publication")
        (self.destination / "keep.txt").write_text("unrelated artifact")

    def save_manifest(self):
        (self.run / render_3d.MANIFEST).write_text(json.dumps(self.manifest))

    def inventory(self):
        return {path.name: path.read_bytes() for path in self.destination.iterdir()}

    def test_valid_run_publishes_only_owned_files(self):
        render_3d.publish(self.repo, self.run)
        self.assertEqual((self.destination / "keep.txt").read_text(), "unrelated artifact")
        for image in self.manifest["images"]:
            self.assertEqual((self.destination / image["path"]).read_bytes(), png())
        self.assertEqual(json.loads((self.destination / render_3d.MANIFEST).read_text()), self.manifest)

    def test_invalid_runs_preserve_the_previous_publication(self):
        before = self.inventory()
        for failure in ("partial", "changed_source", "missing_view", "wrong_hash", "wrong_size", "wrong_board", "wrong_project", "missing_project", "malformed_png", "bad_idat"):
            with self.subTest(failure=failure):
                original = json.loads(json.dumps(self.manifest))
                image = self.manifest["images"][0]
                if failure == "partial":
                    self.manifest["status"] = "timeout"
                elif failure == "changed_source":
                    self.manifest["source_unchanged"] = False
                elif failure == "missing_view":
                    self.manifest["images"].pop()
                elif failure == "wrong_hash":
                    image["sha256"] = "0" * 64
                    self.manifest["views"]["top"]["sha256"] = image["sha256"]
                elif failure == "wrong_size":
                    image["width"] = 4096
                    self.manifest["views"]["top"]["width"] = 4096
                elif failure == "wrong_board":
                    self.manifest["board"]["sha256"] = "0" * 64
                elif failure == "wrong_project":
                    self.manifest["project"]["sha256"] = "0" * 64
                elif failure == "missing_project":
                    self.manifest["project"] = None
                elif failure == "malformed_png":
                    (self.run / image["path"]).write_bytes(png()[:-5])
                    image["sha256"] = render_3d.sha256(self.run / image["path"])
                    self.manifest["views"]["top"]["sha256"] = image["sha256"]
                elif failure == "bad_idat":
                    (self.run / image["path"]).write_bytes(png(raw=b"not native scanlines"))
                    image["sha256"] = render_3d.sha256(self.run / image["path"])
                    self.manifest["views"]["top"]["sha256"] = image["sha256"]
                self.save_manifest()
                with self.assertRaises(ValueError):
                    render_3d.publish(self.repo, self.run)
                self.assertEqual(self.inventory(), before)
                self.manifest = original
                (self.run / self.manifest["images"][0]["path"]).write_bytes(png())
                self.save_manifest()

    def test_symlink_input_is_refused(self):
        image = self.run / self.manifest["images"][0]["path"]
        image.unlink()
        target = self.repo / "external.png"
        target.write_bytes(png())
        image.symlink_to(target)
        before = self.inventory()
        with self.assertRaises(ValueError):
            render_3d.publish(self.repo, self.run)
        self.assertEqual(self.inventory(), before)

    def test_failed_replacement_restores_the_previous_publication(self):
        before = self.inventory()
        replace = os.replace
        for failure in (OSError, KeyboardInterrupt):
            calls = 0

            def fail_second(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise failure("simulated publication failure")
                return replace(source, destination)

            with self.subTest(failure=failure.__name__):
                with patch.object(render_3d.os, "replace", side_effect=fail_second):
                    with self.assertRaises(failure):
                        render_3d.publish(self.repo, self.run)
                self.assertEqual(self.inventory(), before)

    def test_source_change_during_publication_restores_previous_files(self):
        before = self.inventory()
        replace = os.replace
        changed = False

        def change_project(source, destination):
            nonlocal changed
            replace(source, destination)
            if not changed:
                self.board.with_suffix(".kicad_pro").write_text("changed during publication")
                changed = True

        with patch.object(render_3d.os, "replace", side_effect=change_project):
            with self.assertRaisesRegex(ValueError, "changed during publication"):
                render_3d.publish(self.repo, self.run)
        self.assertEqual(self.inventory(), before)

    def test_adapter_calls_selected_backend_and_preserves_publication(self):
        backend = self.repo / "fake-agent-ee"
        fixture_manifest = self.manifest
        backend.write_text(f'''#!{sys.executable}
import base64, json, pathlib, sys
args = sys.argv[1:]
assert args[0] == 'render3d'
out = pathlib.Path(args[args.index('--out') + 1])
out.mkdir()
manifest = json.loads({json.dumps(fixture_manifest)!r})
for image in manifest['images']:
    (out / image['path']).write_bytes(base64.b64decode({base64.b64encode(png()).decode()!r}))
(out / 'render-manifest.json').write_text(json.dumps(manifest))
(out / 'args.json').write_text(json.dumps(args))
''')
        backend.chmod(0o755)
        args = argparse.Namespace(agent_ee=str(backend), models=str(self.repo / "persistent-models"),
                                  width=4096, height=3072, quality="high", jobs=3,
                                  timeout=1200, fetch_models=False)
        before = self.inventory()
        out = render_3d.render(self.repo, args)
        self.assertEqual(out.parent, self.repo / "build/runs/project/fome-mc")
        invocation = json.loads((out / "args.json").read_text())
        self.assertNotIn("--fetch-models", invocation)
        self.assertEqual(invocation[invocation.index("--models") + 1], args.models)
        self.assertEqual(self.inventory(), before)
        args.fetch_models = True
        other = render_3d.render(self.repo, args)
        self.assertNotEqual(other, out)
        self.assertIn("--fetch-models", json.loads((other / "args.json").read_text()))

        backend.write_text(f"#!{sys.executable}\nraise SystemExit(1)\n")
        with self.assertRaisesRegex(ValueError, "rendering failed"):
            render_3d.render(self.repo, args)
        self.assertEqual(self.inventory(), before)

    def test_interrupt_returns_shell_interrupt_status(self):
        with patch.object(render_3d, "render", side_effect=KeyboardInterrupt):
            self.assertEqual(render_3d.main(["render"]), 130)

    def test_interrupt_waits_for_backend_manifest_and_native_child_cleanup(self):
        backend = self.repo / "interruptible_backend.py"
        receipt = self.repo / "interrupted.json"
        backend.write_text('''import json, os, pathlib, signal, subprocess, sys, time
receipt = pathlib.Path(sys.argv[1])
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
record = {'backend_pid': os.getpid(), 'native_pid': child.pid, 'status': 'running'}
temporary = receipt.with_suffix('.tmp')
temporary.write_text(json.dumps(record))
temporary.replace(receipt)
try:
    child.wait()
except KeyboardInterrupt:
    os.killpg(child.pid, signal.SIGKILL)
    child.wait()
    time.sleep(.5)
    record['status'] = 'interrupted'
    receipt.write_text(json.dumps(record))
    raise SystemExit(130)
''')
        wrapper = self.repo / "wrapper.py"
        wrapper.write_text(f'''import runpy, sys
run_backend = runpy.run_path({str(SCRIPT)!r})['run_backend']
try:
    sys.exit(run_backend([sys.executable, {str(backend)!r}, {str(receipt)!r}], {str(self.repo)!r}))
except KeyboardInterrupt:
    sys.exit(130)
''')
        process = subprocess.Popen([sys.executable, str(wrapper)], start_new_session=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        record = None
        try:
            deadline = time.monotonic() + 5
            while not receipt.exists() and time.monotonic() < deadline:
                time.sleep(.02)
            self.assertTrue(receipt.exists(), "fake backend did not become ready")
            record = json.loads(receipt.read_text())
            os.kill(process.pid, signal.SIGINT)
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 130, stdout + stderr)
            self.assertEqual(json.loads(receipt.read_text())["status"], "interrupted")
            for key in ("backend_pid", "native_pid"):
                with self.assertRaises(ProcessLookupError):
                    os.kill(record[key], 0)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=5)
            if record:
                for key in ("backend_pid", "native_pid"):
                    try:
                        os.killpg(record[key], signal.SIGKILL)
                    except ProcessLookupError:
                        pass


if __name__ == "__main__":
    unittest.main()
