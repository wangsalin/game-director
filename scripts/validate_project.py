#!/usr/bin/env python3
"""Read-only project file/manifest checks. Python 3.10+, standard library only.

This does not run an engine, judge gameplay, review licenses or prove device QA.
"""

import argparse
import csv
import os
import struct
import sys
import wave
import zlib
from pathlib import Path

from validate_skill import (
    ASSET_COLUMNS, AUDIO_COLUMNS, confined_path, document_links, manifest_errors,
)


SKIP_DIRS = {".git", ".venv", "venv", "node_modules", ".godot", "Library", "Temp", "__pycache__"}
UNKNOWN = {"unknown", "tbd", "todo", "pending", "待定", "待补", "待确认", "待补来源", "未知", "未确认"}


def png_info(path):
    """Check PNG chunk framing/CRC and read IHDR; does not render pixels."""
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError("invalid PNG signature")
        info, has_data, transparent = None, False, False
        while True:
            header = handle.read(8)
            if len(header) != 8:
                raise ValueError("truncated PNG or missing IEND")
            length, kind = struct.unpack(">I4s", header)
            if info is None and (kind != b"IHDR" or length != 13):
                raise ValueError("PNG must start with a 13-byte IHDR")
            if kind == b"IHDR" and info is not None:
                raise ValueError("duplicate PNG IHDR")
            remaining, crc, payload = length, zlib.crc32(kind), b""
            while remaining:
                block = handle.read(min(remaining, 65536))
                if not block:
                    raise ValueError("truncated PNG chunk")
                crc = zlib.crc32(block, crc)
                if kind == b"IHDR":
                    payload += block
                remaining -= len(block)
            checksum = handle.read(4)
            if len(checksum) != 4 or struct.unpack(">I", checksum)[0] != crc:
                raise ValueError("PNG chunk CRC mismatch")
            if kind == b"IHDR":
                width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
                valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
                if (width == 0 or height == 0 or depth not in valid_depths.get(color, set())
                        or compression != 0 or filtering != 0 or interlace not in {0, 1}):
                    raise ValueError("invalid PNG IHDR values")
                info = {"width": width, "height": height}
                transparent = color in {4, 6}
            elif kind == b"tRNS":
                transparent = True
            elif kind == b"IDAT":
                has_data = has_data or length > 0
            elif kind == b"IEND":
                if length or not has_data or handle.read(1):
                    raise ValueError("invalid PNG IEND/data layout")
                return info, transparent


def wav_info(path):
    """Read PCM WAV parameters and check declared sample bytes exist."""
    with wave.open(str(path), "rb") as handle:
        frames, rate, channels = handle.getnframes(), handle.getframerate(), handle.getnchannels()
        if rate <= 0 or channels <= 0:
            raise ValueError("invalid WAV sample rate or channel count")
        expected = frames * channels * handle.getsampwidth()
        actual = 0
        while True:
            data = handle.readframes(65536)
            if not data:
                break
            actual += len(data)
        if expected == 0 or actual != expected:
            raise ValueError("WAV sample data is empty or truncated")
        return {"sample_rate_hz": rate, "channels": channels, "duration_seconds": frames / rate}


def discover(root, filename):
    paths = []
    for directory, folders, files in os.walk(root, followlinks=False):
        folders[:] = [name for name in folders if name not in SKIP_DIRS and not (Path(directory) / name).is_symlink()]
        for name in files:
            if name.lower() == filename.lower():
                paths.append(str((Path(directory) / name).relative_to(root)))
    return sorted(paths)


def validate(root, asset_manifests=None, audio_manifests=None, release=False):
    root = Path(root).resolve()
    errors, warnings = [], []
    stats = {"manifests": 0, "assets": 0, "audio": 0, "active": 0, "planned": 0, "documents": 0}
    if not root.is_dir():
        return [f"Project directory not found: {root}"], warnings, stats
    documents = set()
    readme = root / "README.md"
    if not readme.is_file() or readme.stat().st_size == 0:
        errors.append("Missing or empty project README.md")
    else:
        documents.add(readme)

    manifest_sets = (
        (asset_manifests if asset_manifests is not None else discover(root, "ASSET_MANIFEST.csv"), False),
        (audio_manifests if audio_manifests is not None else discover(root, "AUDIO_MANIFEST.csv"), True),
    )
    if not manifest_sets[0][0]:
        errors.append("No ASSET_MANIFEST.csv found; use --asset-manifest for a custom filename")
    seen_ids, seen_manifests = set(), set()
    for names, audio in manifest_sets:
        for name in names:
            try:
                path = confined_path(root, root, str(name))
                if path in seen_manifests:
                    errors.append(f"Duplicate manifest argument: {name}")
                    continue
                seen_manifests.add(path)
                columns = AUDIO_COLUMNS if audio else ASSET_COLUMNS
                row_errors, count = manifest_errors(path, columns, audio)
                errors.extend(f"{name}: {error}" for error in row_errors)
                stats["manifests"] += 1
                stats["audio" if audio else "assets"] += count
                if row_errors:
                    continue
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    entries = list(csv.DictReader(handle))
            except (OSError, UnicodeError, ValueError, csv.Error) as exc:
                errors.append(f"Cannot read manifest {name}: {exc}")
                continue

            for line, entry in enumerate(entries, 2):
                prefix = f"{name}:{line}"
                identifier = entry["audio_id" if audio else "asset_id"]

                def problem(message):
                    errors.append(f"{prefix}: {message}")

                key = (audio, identifier)
                if key in seen_ids:
                    problem(f"Duplicate ID across manifests: {identifier}")
                seen_ids.add(key)
                if identifier.upper().startswith("EXAMPLE-"):
                    problem(f"Replace EXAMPLE- template row with a project asset: {identifier}")
                if entry["status"] == "deprecated":
                    continue
                stats["active"] += 1
                if entry["status"] == "planned":
                    stats["planned"] += 1
                approved = entry["review_status"] == "approved"
                tested = entry["verification_status"] != "not_run"
                integrated = entry["integration_status"] == "integrated"
                needs_files = entry["status"] == "ready" or approved or integrated or tested
                needs_evidence = approved or integrated or tested
                if entry["license"].strip().lower() in UNKNOWN or entry["provenance"].strip().lower() in UNKNOWN | {""}:
                    message = f"{prefix}: license/provenance unresolved; commercial permission needs review"
                    (errors if release else warnings).append(message)
                if release:
                    if (entry["status"] != "ready" or not approved or not integrated
                            or entry["verification_status"] != "passed"
                            or (not audio and entry["production_stage"] != "production")):
                        problem("release asset check requires ready/approved/integrated/passed production records")

                files = {}
                for field in ("source_path", "export_path", "evidence_path"):
                    value = entry[field]
                    required = needs_evidence if field == "evidence_path" else needs_files
                    if not value:
                        if required:
                            problem(f"{field} required by the recorded state")
                        continue
                    try:
                        local = confined_path(root, root, value)
                        exists = local.is_file() and local.stat().st_size > 0
                        if not exists and (required or local.exists()):
                            raise ValueError("missing, empty, or not a regular file")
                        if exists:
                            files[field] = local
                            if field == "evidence_path" and local.suffix.lower() == ".md":
                                documents.add(local)
                    except (OSError, ValueError) as exc:
                        problem(f"{field}: {value!r} ({exc})")
                exported = files.get("export_path")
                if exported is None:
                    continue
                fmt = entry["format"].upper()
                suffixes = {"JPEG": {".jpg", ".jpeg"}, "JPG": {".jpg", ".jpeg"}, "GLTF": {".gltf", ".glb"}}
                if exported.suffix.lower() not in suffixes.get(fmt, {"." + fmt.lower()}):
                    problem(f"export_path suffix does not match declared format {fmt}")
                try:
                    if not audio and fmt == "PNG":
                        info, alpha = png_info(exported)
                        for field, actual in info.items():
                            if entry[field] and float(entry[field]) != actual:
                                problem(f"PNG {field}: declared {entry[field]}, actual {actual}")
                        if entry["transparent"] == "true" and not alpha:
                            problem("PNG transparent=true requires an alpha channel or tRNS")
                    elif audio and fmt == "WAV":
                        info = wav_info(exported)
                        for field, actual in info.items():
                            tolerance = max(1 / info["sample_rate_hz"], 0.005) if field == "duration_seconds" else 0
                            if entry[field] and abs(float(entry[field]) - actual) > tolerance:
                                problem(f"WAV {field}: declared {entry[field]}, actual {actual}")
                    else:
                        warnings.append(f"{prefix}: {fmt} metadata/content needs manual tool/engine verification")
                except wave.Error as exc:
                    if str(exc).startswith("unknown format:"):
                        warnings.append(f"{prefix}: WAV codec needs manual verification ({exc})")
                    else:
                        problem(f"Invalid WAV: {exc}")
                except (OSError, EOFError, ValueError, struct.error) as exc:
                    problem(f"Invalid {fmt}: {exc}")

    if release and stats["active"] == 0:
        errors.append("release asset check requires at least one active asset")
    visited = set()
    pending = list(documents)
    while pending:
        document = pending.pop().resolve()
        if document in visited:
            continue
        if not document.is_relative_to(root):
            errors.append(f"Document escapes project: {document.name}")
            continue
        visited.add(document)
        link_errors, edges = document_links(document, root)
        errors.extend(link_errors)
        pending.extend(path for path in edges if path.suffix.lower() == ".md" and path not in visited)
    stats["documents"] = len(visited)
    if stats["planned"]:
        warnings.append(f"{stats['planned']} planned asset(s); file-check PASS does not mean production is complete")
    return errors, warnings, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="project root containing README.md")
    parser.add_argument("--asset-manifest", action="append", help="project-relative CSV; repeat for multiple lists")
    parser.add_argument("--audio-manifest", action="append", help="project-relative CSV; repeat for multiple lists")
    parser.add_argument("--release", action="store_true", help="require complete asset records, not full release approval")
    args = parser.parse_args()
    try:
        errors, warnings, stats = validate(args.path, args.asset_manifest, args.audio_manifest, args.release)
    except OSError as exc:
        print(f"ERROR: Cannot inspect project: {exc}")
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"{'FAILED' if errors else 'PASS (file checks only)'}: {stats}")
    print("Scope: local links, manifests, real files, PNG container/metadata, PCM WAV samples/metadata.")
    print("Not verified: evidence truth, engine/device execution, model/animation quality, gameplay, license rights, release readiness.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
