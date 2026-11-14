#!/usr/bin/env python3
"""Regression tests for resource and manifest validation, using temporary copies."""

import csv
import shutil
import tempfile
import unittest
from pathlib import Path

import validate_skill


class ValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="game-director-test-")
        self.addCleanup(temporary.cleanup)
        temporary_root = Path(temporary.name).resolve()
        self.assertEqual(temporary_root.parent, Path(tempfile.gettempdir()).resolve())
        self.package = temporary_root / "package"
        shutil.copytree(
            Path(__file__).resolve().parents[1], self.package,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )
        self.assert_valid()

    def errors(self):
        return validate_skill.validate(self.package)[0]

    def assert_valid(self):
        self.assertEqual(self.errors(), [])

    def edit_csv(self, filename, operation):
        path = self.package / "templates" / filename
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        operation(rows)
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerows(rows)

    def fields(self, audio=False, **values):
        def update(rows):
            for field, value in values.items():
                rows[1][rows[0].index(field)] = value
        filename = "AUDIO_MANIFEST_TEMPLATE.csv" if audio else "ASSET_MANIFEST_TEMPLATE.csv"
        self.edit_csv(filename, update)

    def append_link(self, target):
        path = self.package / "SKILL.md"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n[test resource]({target})\n")

    def test_valid_package(self):
        self.assert_valid()

    def test_wrong_column_count(self):
        self.edit_csv("ASSET_MANIFEST_TEMPLATE.csv", lambda rows: rows[1].pop())
        self.assertTrue(self.errors())

    def test_duplicate_asset_id(self):
        self.edit_csv("ASSET_MANIFEST_TEMPLATE.csv", lambda rows: rows.append(rows[1].copy()))
        self.assertTrue(self.errors())

    def test_broken_resource_link(self):
        self.append_link("references/missing.md")
        self.assertTrue(self.errors())

    def test_resource_outside_package(self):
        (self.package.parent / "outside.md").write_text("# outside\n", encoding="utf-8")
        self.append_link("../outside.md")
        self.assertTrue(self.errors())

    def test_unreachable_reference(self):
        (self.package / "references/orphan.md").write_text("# orphan\n", encoding="utf-8")
        self.assertTrue(self.errors())

    def test_concept_cannot_be_integrated(self):
        self.fields(
            production_stage="concept", status="ready", source_path="art/source.png",
            export_path="art/export.png", evidence_path="qa/import.md",
            integration_status="integrated",
        )
        self.assertTrue(self.errors())

    def test_device_pass_requires_integration(self):
        self.fields(verification_status="passed", evidence_path="qa/device.md")
        self.assertTrue(self.errors())

    def test_nonfinite_number(self):
        self.fields(fps="NaN")
        self.assertTrue(self.errors())

    def test_old_combined_status_is_rejected(self):
        self.fields(status="integrated")
        self.assertTrue(self.errors())

    def test_concept_can_pass_art_review(self):
        self.fields(production_stage="concept", review_status="approved")
        self.assert_valid()

    def test_quoted_comma_in_name(self):
        self.fields(name="example, with comma")
        self.assert_valid()

    def test_reversed_audio_loop(self):
        self.fields(audio=True, loop="true", duration_seconds="5", loop_start_seconds="4", loop_end_seconds="2")
        self.assertTrue(self.errors())

    def test_loop_exceeds_duration(self):
        self.fields(audio=True, loop="true", duration_seconds="3", loop_start_seconds="1", loop_end_seconds="4")
        self.assertTrue(self.errors())

    def test_loop_requires_both_boundaries(self):
        self.fields(audio=True, loop="true", loop_start_seconds="1")
        self.assertTrue(self.errors())

    def test_valid_audio_loop(self):
        self.fields(audio=True, loop="true", duration_seconds="5", loop_start_seconds="1", loop_end_seconds="4")
        self.assert_valid()


if __name__ == "__main__":
    unittest.main(verbosity=2)
