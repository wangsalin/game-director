#!/usr/bin/env python3
"""Read selected engine metadata only; never launch an editor or alter a project.

Exit 0: one recognized project and no metadata errors. This is NOT a build pass.
Exit 1: missing/ambiguous/invalid metadata. Exit 2: argparse usage error.
"""

import argparse
import json
import re
import sys
from pathlib import Path


MAX_METADATA_BYTES = 1024 * 1024
STAGES = ("editor", "import", "compile", "play", "build", "artifact_run", "device")


def inspect_project(project):
    root = Path(project).resolve()
    findings, engines = [], []

    def finding(severity, code, path, message):
        findings.append(dict(severity=severity, code=code, path=path, message=message))

    def read(relative):
        path = root / relative
        try:
            if not path.resolve().is_relative_to(root):
                raise ValueError("metadata resolves outside the selected project")
            if path.stat().st_size > MAX_METADATA_BYTES:
                raise ValueError("metadata exceeds 1 MiB limit")
            return path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError, ValueError) as error:
            finding("error", "unreadable_metadata", relative, str(error))
            return None

    def read_json(relative):
        content = read(relative)
        if content is None:
            return None

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate JSON key: " + key)
                result[key] = value
            return result

        try:
            data = json.loads(content, object_pairs_hook=unique)
            if not isinstance(data, dict):
                raise ValueError("metadata root must be an object")
            return data
        except (ValueError, RecursionError) as error:
            finding("error", "invalid_json", relative, str(error))
            return None

    def add(engine, version, source, variant, **metadata):
        engines.append(dict(engine=engine, version=version, version_source=source,
                            variant=variant, metadata=metadata))
        if not version:
            finding("warning", "unknown_version", source,
                    "Confirm the exact editor version before opening the project.")

    if not root.is_dir():
        finding("error", "invalid_root", ".", "Select an existing project directory.")
    else:
        if (root / "project.godot").exists():
            text = read("project.godot")
            features = re.search(r'^config/features\s*=\s*PackedStringArray\(([^\n]*)\)', text or "", re.M)
            versions = re.findall(r'"(\d+\.\d+(?:\.\d+)?)"', features[1]) if features else []
            config = re.search(r'^config_version\s*=\s*(\d+)\s*$', text or "", re.M)
            valid_config = config is not None and len(config[1]) <= 9
            add("godot", versions[0] if versions else None, "project.godot",
                "godot", config_version=int(config[1]) if valid_config else None,
                export_presets=(root / "export_presets.cfg").is_file())
            if text is not None and not valid_config:
                finding("error", "invalid_godot_config", "project.godot", "Missing or invalid config_version.")
            finding("warning", "godot_version_hint", "project.godot",
                    "Feature version is a compatibility hint, not proof of the exact editor patch or .NET edition.")

        unity_version = root / "ProjectSettings/ProjectVersion.txt"
        if unity_version.exists() or ((root / "Assets").is_dir() and (root / "ProjectSettings").is_dir()):
            text = read("ProjectSettings/ProjectVersion.txt")
            match = re.search(r'^m_EditorVersion:\s*(\S+)\s*$', text or "", re.M)
            add("unity", match[1] if match else None, "ProjectSettings/ProjectVersion.txt", "unity")
            if text is not None and not match:
                finding("error", "invalid_unity_version", "ProjectSettings/ProjectVersion.txt", "Missing m_EditorVersion.")
            if not (root / "Assets").is_dir():
                finding("error", "missing_assets", "Assets", "Unity Assets directory is absent.")
            if (root / "Packages/manifest.json").exists():
                read_json("Packages/manifest.json")
            else:
                finding("warning", "missing_packages", "Packages/manifest.json", "Check this Unity version's package requirements.")

        package = None
        # A generic package.json is not evidence of Cocos. Invalid generic npm
        # metadata must not make a valid project from another engine fail.
        if (root / "package.json").exists():
            before = len(findings)
            package = read_json("package.json")
            if package is None and not (root / "settings").is_dir():
                del findings[before:]
        if package is not None and "creator" in package:
            creator = package["creator"]
            version = creator.get("version") if isinstance(creator, dict) else None
            if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][\w.-]+)?", version):
                finding("error", "invalid_cocos_version", "package.json", "creator.version must contain an editor version.")
                version = None
            add("cocos", version, "package.json:creator.version", "creator-3" if version and version.startswith("3.") else "review-version")
            if not version or not version.startswith("3."):
                finding("warning", "cocos_version_review", "package.json", "Do not apply the Creator 3.x workflow without checking this version.")
            for directory in ("assets", "settings"):
                if not (root / directory).is_dir():
                    finding("error", "missing_cocos_directory", directory, "Creator project directory is absent.")

        if (root / "project.json").exists():
            before = len(findings)
            legacy = read_json("project.json")
            if legacy is not None and legacy.get("engine") == "cocos-creator":
                version = legacy.get("version")
                add("cocos", version if isinstance(version, str) else None,
                    "project.json:version", "legacy-creator")
                finding("warning", "legacy_creator", "project.json", "Use matching legacy documentation; do not migrate or run Creator 3.x commands automatically.")
            elif legacy is None and engines:
                del findings[before:]

        try:
            descriptors = sorted(root.glob("*.uproject"))
        except OSError as error:
            descriptors = []
            finding("error", "unreadable_root", ".", str(error))
        for descriptor in descriptors:
            data = read_json(descriptor.name)
            association = data.get("EngineAssociation") if data else None
            numeric = isinstance(association, str) and re.fullmatch(r"\d+\.\d+(?:\.\d+)?", association)
            add("unreal", association if numeric else None,
                descriptor.name + ":EngineAssociation", "unreal",
                descriptor=descriptor.name, custom_engine_association=bool(association and not numeric),
                cpp_source=(root / "Source").is_dir())

    detection = "detected" if len(engines) == 1 else "ambiguous" if engines else "not_detected"
    if detection != "detected":
        finding("error", detection, ".", "Select one actual engine project root; no engine was chosen automatically.")
    validation = {"metadata": "failed" if any(f["severity"] == "error" for f in findings) else "passed"}
    validation.update({stage: "not_run" for stage in STAGES})
    return dict(schema=1, root=str(root), detection=detection, engines=engines,
                findings=findings, validation=validation,
                scope="Read-only metadata inspection; no editor, SDK, asset UUID, compilation, gameplay or build verification.")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    report = inspect_project(args.project)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["validation"]["metadata"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
