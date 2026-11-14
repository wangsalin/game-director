#!/usr/bin/env python3
"""Exercise project acceptance with real temporary PNG/WAV files; stdlib only."""

import csv
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
import zlib
from pathlib import Path

import validate_project
from validate_skill import ASSET_COLUMNS, AUDIO_COLUMNS


def write_png(path, width=16, height=8):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    pixels = (b"\x00" + b"\x22\x66\xaa\xff" * width) * height
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                     + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


class ProjectTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="game-director-project-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "真实项目 with spaces"
        self.root.mkdir()
        (self.root / "README.md").write_text(
            "# Project\nFixture for file validation, no game or device test.\n[Assets](ASSET_MANIFEST.csv)\n",
            encoding="utf-8",
        )
        (self.root / "art").mkdir()
        write_png(self.root / "art/source.png")
        write_png(self.root / "art/player.png")
        self.assets = [dict.fromkeys(ASSET_COLUMNS, "")]
        self.assets[0].update(
            asset_id="PLAYER", name="Player", category="character", usage="gameplay", format="PNG",
            width="16", height="8", transparent="true", source_path="art/source.png",
            export_path="art/player.png", license="original", provenance="test fixture generator",
            status="ready", production_stage="production", review_status="not_reviewed",
            integration_status="not_integrated", verification_status="not_run",
        )
        self.audio = []
        self.save()

    def save(self):
        for filename, columns, rows in (
            ("ASSET_MANIFEST.csv", ASSET_COLUMNS, self.assets),
            ("AUDIO_MANIFEST.csv", AUDIO_COLUMNS, self.audio),
        ):
            if not rows and filename.startswith("AUDIO"):
                continue
            with (self.root / filename).open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)

    def result(self, **kwargs):
        self.save()
        return validate_project.validate(self.root, **kwargs)

    def assert_valid(self, **kwargs):
        self.assertEqual(self.result(**kwargs)[0], [])

    def assert_invalid(self, expected, **kwargs):
        errors = self.result(**kwargs)[0]
        self.assertTrue(any(expected in error for error in errors), errors)

    def evidence(self):
        (self.root / "qa.md").write_text(
            "# Fixture evidence\nSynthetic file-validation fixture; no engine/device execution.\n",
            encoding="utf-8",
        )
        self.assets[0]["evidence_path"] = "qa.md"

    def add_audio(self):
        with wave.open(str(self.root / "confirm.wav"), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(8000)
            handle.writeframes(b"\x00\x00" * 800)
        self.audio = [dict.fromkeys(AUDIO_COLUMNS, "")]
        self.audio[0].update(
            audio_id="CONFIRM", name="Confirm", category="SFX", trigger_event="confirm", format="WAV",
            duration_seconds="0.1", sample_rate_hz="8000", channels="1", loop="false",
            allow_overlap="false", source_path="confirm.wav", export_path="confirm.wav",
            license="original", provenance="test fixture generator", status="ready",
            review_status="not_reviewed", integration_status="not_integrated", verification_status="not_run",
        )

    def test_real_png_passes(self):
        self.assert_valid()

    def test_png_dimension_mismatch(self):
        self.assets[0]["width"] = "32"
        self.assert_invalid("width")

    def test_text_renamed_as_png(self):
        (self.root / "art/player.png").write_text("not an image", encoding="utf-8")
        self.assert_invalid("PNG")

    def test_truncated_png(self):
        path = self.root / "art/player.png"
        path.write_bytes(path.read_bytes()[:33])
        self.assert_invalid("PNG")

    def test_png_bad_crc(self):
        path = self.root / "art/player.png"
        data = bytearray(path.read_bytes())
        data[29] ^= 1
        path.write_bytes(data)
        self.assert_invalid("CRC")

    def test_missing_ready_export(self):
        (self.root / "art/player.png").unlink()
        self.assert_invalid("export_path")

    def test_empty_ready_source(self):
        (self.root / "art/source.png").write_bytes(b"")
        self.assert_invalid("source_path")

    def test_planned_can_have_future_paths(self):
        self.assets[0].update(status="planned", source_path="future/source.psd", export_path="future/player.png")
        errors, warnings, stats = self.result()
        self.assertEqual(errors, [])
        self.assertEqual(stats["planned"], 1)
        self.assertTrue(warnings)

    def test_approved_requires_real_files_and_evidence(self):
        self.assets[0].update(review_status="approved", evidence_path="absent.md")
        self.assert_invalid("evidence_path")

    def test_concept_can_be_reviewed_with_evidence(self):
        self.assets[0].update(production_stage="concept", review_status="approved")
        self.evidence()
        self.assert_valid()

    def test_integrated_requires_real_evidence(self):
        self.assets[0].update(integration_status="integrated", evidence_path="absent.md")
        self.assert_invalid("evidence_path")

    def test_empty_evidence_is_rejected(self):
        self.assets[0].update(review_status="approved", evidence_path="qa.md")
        (self.root / "qa.md").write_bytes(b"")
        self.assert_invalid("evidence_path")

    def test_evidence_link_is_checked(self):
        self.evidence()
        (self.root / "qa.md").write_text("[Capture](absent.png)\n", encoding="utf-8")
        self.assert_invalid("absent.png")

    def test_paths_are_root_relative_for_nested_manifests(self):
        self.save()
        folder = self.root / "03_Art_Assets"
        folder.mkdir()
        (self.root / "ASSET_MANIFEST.csv").rename(folder / "ASSET_MANIFEST.csv")
        (self.root / "README.md").write_text("[Assets](03_Art_Assets/ASSET_MANIFEST.csv)\n", encoding="utf-8")
        self.assertEqual(validate_project.validate(self.root)[0], [])

    def test_escape_is_rejected_even_when_planned(self):
        self.assets[0].update(status="planned", source_path="../outside.png")
        self.assert_invalid("source_path")

    def test_absolute_path_is_rejected(self):
        self.assets[0]["source_path"] = "C:/missing.png"
        self.assert_invalid("source_path")

    def test_file_uri_is_rejected(self):
        self.assets[0]["source_path"] = "file:///C:/missing.png"
        self.assert_invalid("source_path")

    def test_readme_anchor_is_checked(self):
        (self.root / "README.md").write_text("# Project\n[Rule](#absent)\n", encoding="utf-8")
        self.assert_invalid("anchor")

    def test_missing_readme_is_rejected(self):
        (self.root / "README.md").unlink()
        self.assert_invalid("README.md")

    def test_examples_cannot_count_as_project_assets(self):
        self.assets[0]["asset_id"] = "EXAMPLE-2D"
        self.assert_invalid("EXAMPLE-")

    def test_real_wav_passes(self):
        self.add_audio()
        self.assert_valid()

    def test_wav_rate_mismatch(self):
        self.add_audio()
        self.audio[0]["sample_rate_hz"] = "48000"
        self.assert_invalid("sample_rate_hz")

    def test_wav_duration_mismatch(self):
        self.add_audio()
        self.audio[0]["duration_seconds"] = "1"
        self.assert_invalid("duration_seconds")

    def test_wav_channel_mismatch(self):
        self.add_audio()
        self.audio[0]["channels"] = "2"
        self.assert_invalid("channels")

    def test_truncated_wav(self):
        self.add_audio()
        path = self.root / "confirm.wav"
        path.write_bytes(path.read_bytes()[:-100])
        self.assert_invalid("WAV")

    def test_invalid_wav_zero_sample_rate(self):
        self.add_audio()
        path = self.root / "confirm.wav"
        data = bytearray(path.read_bytes())
        struct.pack_into("<I", data, 24, 0)
        path.write_bytes(data)
        self.assert_invalid("WAV")

    def test_unknown_license_warns(self):
        self.assets[0]["license"] = "unknown"
        errors, warnings, _ = self.result()
        self.assertEqual(errors, [])
        self.assertTrue(any("license" in warning for warning in warnings))

    def test_release_rejects_incomplete_states(self):
        self.assert_invalid("release", release=True)

    def test_release_rejects_unknown_license(self):
        self.evidence()
        self.assets[0].update(review_status="approved", integration_status="integrated",
                              verification_status="passed", license="unknown")
        self.assert_invalid("license", release=True)

    def test_release_file_checks_pass_with_records(self):
        self.evidence()
        self.assets[0].update(review_status="approved", integration_status="integrated", verification_status="passed")
        self.assert_valid(release=True)

    def test_unsupported_format_reports_manual_checks(self):
        path = self.root / "art/player.svg"
        path.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        self.assets[0].update(format="SVG", export_path="art/player.svg")
        errors, warnings, _ = self.result()
        self.assertEqual(errors, [])
        self.assertTrue(any("manual" in warning for warning in warnings))

    def test_custom_manifest_argument(self):
        self.save()
        (self.root / "ASSET_MANIFEST.csv").rename(self.root / "art-list.csv")
        (self.root / "README.md").write_text("# Custom layout\n", encoding="utf-8")
        self.assertEqual(validate_project.validate(self.root, asset_manifests=["art-list.csv"])[0], [])

    def test_cross_manifest_duplicate_id(self):
        self.save()
        (self.root / "second.csv").write_bytes((self.root / "ASSET_MANIFEST.csv").read_bytes())
        self.assert_invalid("Duplicate ID", asset_manifests=["ASSET_MANIFEST.csv", "second.csv"])

    def test_empty_manifest_is_rejected(self):
        self.assets = []
        self.assert_invalid("ASSET_MANIFEST.csv")

    def test_missing_custom_manifest_is_rejected(self):
        self.assert_invalid("absent.csv", asset_manifests=["absent.csv"])

    def test_custom_manifest_cannot_escape_root(self):
        self.assert_invalid("escapes root", asset_manifests=["../outside.csv"])

    def test_generated_directory_is_skipped(self):
        folder = self.root / "node_modules"
        folder.mkdir()
        (folder / "ASSET_MANIFEST.csv").write_text("garbage", encoding="utf-8")
        self.assert_valid()

    def test_export_extension_matches_format(self):
        (self.root / "art/player.jpg").write_bytes((self.root / "art/player.png").read_bytes())
        self.assets[0]["export_path"] = "art/player.jpg"
        self.assert_invalid("suffix")

    def test_symlink_export_cannot_escape_root(self):
        target = self.root.parent / "outside.png"
        write_png(target)
        link = self.root / "art/link.png"
        try:
            link.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"Platform does not allow symbolic links: {exc}")
        self.assets[0]["export_path"] = "art/link.png"
        self.assert_invalid("escapes root")

    def test_release_rejects_no_active_assets(self):
        self.assets[0].update(status="deprecated", source_path="", export_path="")
        self.assert_invalid("active", release=True)

    def test_cli_exit_codes_from_another_directory(self):
        script = Path(validate_project.__file__).resolve()
        command = [sys.executable, "-B", str(script), str(self.root)]
        passed = subprocess.run(command, cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        (self.root / "art/player.png").unlink()
        failed = subprocess.run(command, cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
