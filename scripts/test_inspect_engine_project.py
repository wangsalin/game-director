"""Behavioral metadata checks on isolated projects; no engine install needed."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from inspect_engine_project import inspect_project


class EngineInspectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_godot_version_is_hint_and_no_run_is_claimed(self):
        self.write("project.godot", 'config_version=5\n[application]\nconfig/features=PackedStringArray("4.7", "GL Compatibility")\n')
        r = inspect_project(self.root)
        self.assertEqual(r["engines"][0]["version"], "4.7")
        self.assertEqual(r["validation"]["metadata"], "passed")
        self.assertTrue(all(v == "not_run" for k, v in r["validation"].items() if k != "metadata"))

    def test_unity_exact_version_and_package_json(self):
        self.write("ProjectSettings/ProjectVersion.txt", "m_EditorVersion: 2022.3.62f1\nm_EditorVersionWithRevision: data\n")
        (self.root / "Assets").mkdir()
        self.write("Packages/manifest.json", '{"dependencies":{}}')
        r = inspect_project(self.root)
        self.assertEqual(r["engines"][0]["version"], "2022.3.62f1")
        self.assertEqual(r["validation"]["metadata"], "passed")

    def test_unity_missing_version_fails(self):
        (self.root / "Assets").mkdir()
        (self.root / "ProjectSettings").mkdir()
        self.assertEqual(inspect_project(self.root)["validation"]["metadata"], "failed")

    def test_cocos_uses_creator_version_not_app_version(self):
        self.write("package.json", '{"version":"1.0.0","creator":{"version":"3.8.8"}}')
        (self.root / "assets").mkdir()
        (self.root / "settings").mkdir()
        r = inspect_project(self.root)
        self.assertEqual(r["engines"][0]["version"], "3.8.8")
        self.assertEqual(r["engines"][0]["variant"], "creator-3")
        self.assertEqual(r["validation"]["metadata"], "passed")

    def test_cocos_invalid_version_and_missing_directories_fail(self):
        self.write("package.json", '{"creator":{"version":null}}')
        r = inspect_project(self.root)
        self.assertEqual(r["validation"]["metadata"], "failed")
        self.assertIn("invalid_cocos_version", [f["code"] for f in r["findings"]])

    def test_creator_2_is_not_treated_as_creator_3(self):
        self.write("project.json", '{"engine":"cocos-creator","version":"2.4.10"}')
        r = inspect_project(self.root)
        self.assertEqual(r["engines"][0]["variant"], "legacy-creator")
        self.assertIn("legacy_creator", [f["code"] for f in r["findings"]])

    def test_generic_npm_project_is_not_cocos(self):
        self.write("package.json", '{"name":"game","version":"3.8.8"}')
        self.assertEqual(inspect_project(self.root)["detection"], "not_detected")

    def test_unreal_custom_association_does_not_invent_version(self):
        self.write("Demo.uproject", '{"FileVersion":3,"EngineAssociation":"{custom-guid}"}')
        r = inspect_project(self.root)
        self.assertEqual(r["engines"][0]["engine"], "unreal")
        self.assertIsNone(r["engines"][0]["version"])
        self.assertTrue(r["engines"][0]["metadata"]["custom_engine_association"])

    def test_multiple_unreal_projects_are_ambiguous(self):
        for name in ("A", "B"):
            self.write(name + ".uproject", '{"EngineAssociation":"5.6"}')
        self.assertEqual(inspect_project(self.root)["detection"], "ambiguous")

    def test_conflicting_engine_markers_fail(self):
        self.write("project.godot", "config_version=5\n")
        self.write("Demo.uproject", '{"EngineAssociation":"5.6"}')
        self.assertEqual(inspect_project(self.root)["validation"]["metadata"], "failed")

    def test_invalid_json_and_duplicate_keys_fail(self):
        path = self.write("Demo.uproject", '{"EngineAssociation":')
        self.assertEqual(inspect_project(self.root)["validation"]["metadata"], "failed")
        path.write_text('{"EngineAssociation":"5.6","EngineAssociation":"5.7"}', encoding="utf-8")
        self.assertEqual(inspect_project(self.root)["validation"]["metadata"], "failed")

    def test_large_metadata_rejected(self):
        self.write("Demo.uproject", " " * (1024 * 1024 + 1))
        self.assertIn("unreadable_metadata", [f["code"] for f in inspect_project(self.root)["findings"]])

    def test_utf8_bom_and_cli_from_other_directory_are_read_only(self):
        self.write("Demo.uproject", '\ufeff{"EngineAssociation":"5.6"}')
        def snapshot():
            return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        script = Path(__file__).with_name("inspect_engine_project.py").resolve()
        result = subprocess.run([sys.executable, "-B", str(script), str(self.root)],
                                cwd=self.root.parent, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["validation"]["build"], "not_run")
        self.assertEqual(before, snapshot())

    def test_missing_root_returns_failure(self):
        self.assertEqual(inspect_project(self.root / "absent")["validation"]["metadata"], "failed")

    def test_outside_metadata_symlink_is_not_read(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / "outside.uproject"
            outside.write_text('{"EngineAssociation":"5.6"}', encoding="utf-8")
            try:
                os.symlink(outside, self.root / "Demo.uproject")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            r = inspect_project(self.root)
            self.assertEqual(r["validation"]["metadata"], "failed")
            self.assertIsNone(r["engines"][0]["version"])


if __name__ == "__main__":
    unittest.main()
