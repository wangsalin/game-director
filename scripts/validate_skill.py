#!/usr/bin/env python3
"""Validate local resource links and manifest templates; Python stdlib only.

This is not a full YAML validator or a behavioral evaluation of the skill.
Use skill-creator's quick_validate.py as an additional metadata check.
"""

import argparse
import csv
import math
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ASSET_COLUMNS = (
    "asset_id,name,category,usage,format,width,height,transparent,pivot,animation,"
    "fps,source_path,export_path,license,status,notes,production_stage,review_status,"
    "integration_status,verification_status,poly_budget,texture_spec,rig_spec,"
    "scale_units,collider_spec,lod_spec,provenance,evidence_path"
).split(",")
AUDIO_COLUMNS = (
    "audio_id,name,category,trigger_event,format,duration_seconds,sample_rate_hz,"
    "channels,loop,loop_start_seconds,loop_end_seconds,gain_db,priority,allow_overlap,"
    "max_instances,cooldown_ms,source_path,export_path,license,status,review_status,"
    "integration_status,verification_status,provenance,evidence_path,notes"
).split(",")
ENUMS = {
    "status": {"planned", "in_progress", "ready", "deprecated"},
    "review_status": {"not_reviewed", "changes_requested", "approved"},
    "integration_status": {"not_integrated", "integrated"},
    "verification_status": {"not_run", "passed", "failed"},
    "production_stage": {"concept", "production"},
}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def resource_errors(root):
    errors = []
    resources = set()
    for folder in ("references", "templates", "scripts"):
        directory = root / folder
        if not directory.is_dir():
            errors.append(f"Missing resource directory: {folder}")
            continue
        resources.update(
            p.resolve() for p in directory.rglob("*")
            if p.is_file() and p.suffix in {".md", ".csv", ".py"}
        )
    for required in ("SKILL.md", "agents/openai.yaml", "VERSION"):
        if not (root / required).is_file():
            errors.append(f"Missing required file: {required}")

    graph = {}
    documents = {p for p in resources if p.suffix == ".md"}
    documents.update(root / name for name in ("SKILL.md", "README_CN.md") if (root / name).is_file())
    for path in sorted(resources | documents):
        if path.stat().st_size == 0:
            errors.append(f"Empty resource: {path.relative_to(root)}")
    for document in sorted(documents):
        edges = set()
        try:
            content = document.read_text(encoding="utf-8-sig")
        except UnicodeError as exc:
            errors.append(f"Invalid UTF-8: {document.relative_to(root)}: {exc}")
            continue
        # Ignore fenced examples. This repository uses ordinary inline links.
        content = re.sub(r"(?ms)^```[^\n]*\n.*?^```\s*$", "", content)
        for target in LINK.findall(content):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            linked = (document.parent / unquote(parsed.path)).resolve()
            if not linked.is_relative_to(root):
                errors.append(f"Resource escapes package: {document.relative_to(root)} -> {target}")
            elif not linked.is_file():
                errors.append(f"Broken link: {document.relative_to(root)} -> {target}")
            else:
                edges.add(linked)
        graph[document.resolve()] = edges

    pending = [(root / "SKILL.md").resolve()]
    reachable = set()
    while pending:
        path = pending.pop()
        if path not in reachable:
            reachable.add(path)
            pending.extend(graph.get(path, ()))
    for path in sorted(resources - reachable):
        errors.append(f"Resource not reachable from SKILL.md: {path.relative_to(root)}")
    return errors, len(resources)


def manifest_errors(path, columns, audio=False):
    errors = []
    if not path.is_file():
        return [f"Missing manifest template: {path.name}"], 0
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle, strict=True))
    except (UnicodeError, csv.Error) as exc:
        return [f"Invalid CSV {path.name}: {exc}"], 0
    if not rows or rows[0] != columns:
        return [f"Unexpected columns in {path.name}; expected {len(columns)} ordered fields"], 0
    seen = set()
    count = 0
    id_field = "audio_id" if audio else "asset_id"
    for line, row in enumerate(rows[1:], 2):
        if not row:
            continue
        count += 1
        prefix = f"{path.name}:{line}"
        if len(row) != len(columns):
            errors.append(f"{prefix}: {len(row)} columns; expected {len(columns)}")
            continue
        entry = dict(zip(columns, row))

        def problem(message):
            errors.append(f"{prefix}: {message}")

        required = (id_field, "name", "category", "format", "license", "trigger_event" if audio else "usage")
        for field in required:
            if not entry[field].strip():
                problem(f"Empty {field}")
        identifier = entry[id_field]
        if identifier in seen:
            problem(f"Duplicate ID: {identifier}")
        seen.add(identifier)
        for field, allowed in ENUMS.items():
            if field in entry and entry[field] not in allowed:
                problem(f"Invalid {field}: {entry[field]!r}")
        for field in (("loop", "allow_overlap") if audio else ("transparent",)):
            if entry[field] not in {"", "true", "false"}:
                problem(f"{field} must be true, false, or empty when not applicable")

        positive = ("duration_seconds", "sample_rate_hz", "channels", "max_instances") if audio else ("width", "height", "fps", "poly_budget")
        nonnegative = ("loop_start_seconds", "loop_end_seconds", "cooldown_ms") if audio else ()
        numeric = positive + nonnegative + (("gain_db", "priority") if audio else ())
        numbers = {}
        for field in numeric:
            if not entry[field]:
                continue
            try:
                number = float(entry[field])
                if not math.isfinite(number):
                    raise ValueError("not finite")
                if field in positive and number <= 0:
                    raise ValueError("must be positive")
                if field in nonnegative and number < 0:
                    raise ValueError("must be nonnegative")
                numbers[field] = number
            except ValueError as exc:
                problem(f"Invalid {field}: {entry[field]!r} ({exc})")

        if entry["status"] == "ready":
            for field in ("source_path", "export_path", "provenance"):
                if not entry[field].strip():
                    problem(f"ready requires {field}")
        if entry["integration_status"] == "integrated":
            if entry["status"] != "ready" or not entry["export_path"]:
                problem("integrated requires ready status and an export path")
            if not entry["evidence_path"]:
                problem("integrated requires evidence_path")
        if entry["verification_status"] in {"passed", "failed"}:
            if entry["integration_status"] != "integrated" or not entry["evidence_path"]:
                problem("device verification requires integration and evidence_path")
        if not audio and entry["production_stage"] == "concept":
            if entry["integration_status"] == "integrated" or entry["verification_status"] != "not_run":
                problem("concept cannot claim production integration or device verification")
        if audio:
            if entry["category"] not in {"BGM", "SFX", "Voice", "Ambience"}:
                problem("Invalid audio category")
            start, end = numbers.get("loop_start_seconds"), numbers.get("loop_end_seconds")
            if (bool(entry["loop_start_seconds"]) != bool(entry["loop_end_seconds"])):
                problem("Loop boundaries must both be set or both be empty")
            if start is not None and end is not None:
                if entry["loop"] != "true" or end <= start:
                    problem("Explicit loop requires loop=true and end > start")
                if "duration_seconds" in numbers and end > numbers["duration_seconds"]:
                    problem("Loop end exceeds duration")
    if count == 0:
        errors.append(f"{path.name}: template needs at least one clearly marked format example")
    return errors, count


def validate(root):
    root = root.resolve()
    errors, resources = resource_errors(root)
    asset_errors, assets = manifest_errors(root / "templates/ASSET_MANIFEST_TEMPLATE.csv", ASSET_COLUMNS)
    audio_errors, audio = manifest_errors(root / "templates/AUDIO_MANIFEST_TEMPLATE.csv", AUDIO_COLUMNS, audio=True)
    return errors + asset_errors + audio_errors, resources, assets, audio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, resources, assets, audio = validate(args.path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} problem(s)")
        return 1
    print(f"PASS: {resources} reachable resources; {assets} asset and {audio} audio example rows")
    print("Scope: local resource paths/reachability and CSV constraints; not full YAML or behavior.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
