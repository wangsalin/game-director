"""Exercise creation in temporary folders, without installing or running game code."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import create_web_prototype


ROOT = Path(__file__).resolve().parents[1]


class CreationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="game-director-create-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.destination = self.root / "中文 prototype"

    def test_self_contained_project_and_checker(self):
        create_web_prototype.create(self.destination)
        files = {p.relative_to(self.destination).as_posix() for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(len(files), 17)
        for name in files:
            self.assertGreater((self.destination / name).stat().st_size, 0)
        self.assertIn("tools/web-check/LICENSE", files)
        self.assertIn("tools/web-check/check.test.mjs", files)
        self.assertIn("tools/web-check/browser.test.mjs", files)
        self.assertEqual(json.loads((self.destination / "browser-plan.json").read_text(encoding="utf-8"))["schema"], 1)
        self.assertEqual(json.loads((self.destination / "package.json").read_text(encoding="utf-8"))["type"], "module")
        self.assertNotIn("node_modules", files)

    @unittest.skipUnless(shutil.which("git"), "Git is needed to verify generated ignore behavior")
    def test_generated_gitignore_keeps_source_and_excludes_local_outputs(self):
        create_web_prototype.create(self.destination)
        empty_excludes = self.root / "empty-excludes"
        empty_excludes.write_text("", encoding="utf-8")
        subprocess.run(["git", "init", "--quiet", "--template=", str(self.destination)], check=True,
                       capture_output=True)
        ignored = ["node_modules/pkg/index.js", "tools/web-check/node_modules/pkg/index.js",
                   "evidence-run-01/report.json", "test-results/screen.png", ".env", ".env.local",
                   "__pycache__/module.pyc"]
        kept = ["README.md", "browser-plan.json", "tools/web-check/package-lock.json",
                ".env.example", "evidence/approved/report.json", "assets/map.data"]
        result = subprocess.run(["git", "-c", f"core.excludesFile={empty_excludes}", "check-ignore",
                                 "--no-index", "--stdin", "-z"],
                                input=b"\0".join(p.encode("utf-8") for p in ignored + kept) + b"\0",
                                cwd=self.destination, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.decode("utf-8").split("\0")[:-1], ignored)

    def test_existing_empty_or_populated_destination_is_preserved(self):
        self.destination.mkdir()
        with self.assertRaises(ValueError):
            create_web_prototype.create(self.destination)
        note = self.destination / "user.txt"
        note.write_text("keep", encoding="utf-8")
        with self.assertRaises(ValueError):
            create_web_prototype.create(self.destination)
        self.assertEqual(note.read_text(), "keep")

    def test_title_is_encoded_as_javascript_string_not_interpolated_code(self):
        title = '海岛 "灯塔"\\夜航'
        create_web_prototype.create(self.destination, title)
        config = (self.destination / "config.js").read_text(encoding="utf-8")
        self.assertIn(json.dumps(title, ensure_ascii=False), config)

    def test_blank_title_and_missing_parent_do_not_create_output(self):
        with self.assertRaises(ValueError):
            create_web_prototype.create(self.destination, " ")
        with self.assertRaises(ValueError):
            create_web_prototype.create(self.root / "missing" / "game")
        self.assertFalse(self.destination.exists())

    def test_missing_source_fails_before_creation(self):
        source = self.root / "incomplete-skill"
        source.mkdir()
        with self.assertRaises(ValueError):
            create_web_prototype.create(self.destination, skill_root=source)
        self.assertFalse(self.destination.exists())

    def test_cli_works_from_another_directory_and_does_not_claim_checks_passed(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/create_web_prototype.py"), str(self.destination)],
                                cwd=self.root, text=True, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("have not run", result.stdout)
        self.assertTrue((self.destination / "src/rules.js").is_file())


if __name__ == "__main__":
    unittest.main()
