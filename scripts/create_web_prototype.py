#!/usr/bin/env python3
"""Create a new, self-contained Web prototype. Standard library; never overwrite."""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path


def create(destination, title="信标小径", skill_root=None):
    root = Path(skill_root) if skill_root else Path(__file__).resolve().parents[1]
    destination = Path(destination).absolute()
    if not title.strip() or len(title) > 100:
        raise ValueError("title must contain 1–100 characters")
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination already exists; choose a new folder. Nothing was overwritten.")
    if not destination.parent.is_dir():
        raise ValueError("Destination parent must already exist.")
    source = root / "assets/web-prototype"
    checker = root / "scripts/web-check"
    # Validate sources before creating any destination. The explicit list excludes caches.
    game_files = [".gitignore", "index.html", "style.css", "config.js", "package.json", "README.md",
                  "src/main.js", "src/rules.js", "tests/rules.test.js", "browser-plan.json"]
    tool_files = ["check.mjs", "check.test.mjs", "browser.test.mjs", "package.json", "package-lock.json", "README.md"]
    for path in [*(source / name for name in game_files), *(checker / name for name in tool_files), root / "LICENSE"]:
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f"Missing or empty source resource: {path.relative_to(root)}")
    with tempfile.TemporaryDirectory(prefix=".game-director-create-", dir=destination.parent) as temporary:
        stage = Path(temporary) / "project"
        stage.mkdir()
        for name in game_files:
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, target)
        for name in tool_files:
            target = stage / "tools/web-check" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(checker / name, target)
        shutil.copyfile(root / "LICENSE", stage / "tools/web-check/LICENSE")
        config = (stage / "config.js").read_text(encoding="utf-8")
        config = config.replace('"信标小径"', json.dumps(title, ensure_ascii=False), 1)
        (stage / "config.js").write_text(config, encoding="utf-8", newline="\n")
        # copytree exclusively creates the root and refuses even an empty existing folder.
        # A copy failure may leave a new partial folder; it never replaces a prior project.
        shutil.copytree(stage, destination)
    return destination


def main():
    # Paths/titles are UTF-8 even on Windows hosts whose redirected default is cp1252.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--title", default="信标小径")
    args = parser.parse_args()
    try:
        path = create(args.destination, args.title)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Created: {path}\nThis is the starter game, not completion of a different requested mechanic.")
    print("Browser/game checks have not run. Read README.md and adapt rules, tests and plan together.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
