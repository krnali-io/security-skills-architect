#!/usr/bin/env python3
"""Create a reviewable skill draft from bundled templates (no network or code execution)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def scaffold(name: str, description: str, output: Path) -> Path:
    if len(name) > 64 or not NAME_RE.fullmatch(name):
        raise ValueError("Skill name must be 1–64 lowercase letters/digits separated by single hyphens")
    if not description.strip() or len(description) > 1024 or any(ord(c) < 32 for c in description):
        raise ValueError("Description must be 1–1024 characters, on one line")
    template = Path(__file__).resolve().parent.parent / "templates" / "skill"
    target = output.expanduser().resolve() / name
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Destination already exists: {target}")
    sources = list(template.rglob("*"))
    if not sources or any(p.is_symlink() for p in sources):
        raise ValueError("Template must be present and contain no symlinks")
    target.mkdir(parents=True, exist_ok=False)
    # Ensure paths are local and generated content is inert Markdown/JSON, not executable code.
    for source in sources:
        if not source.is_file():
            continue
        destination = target / source.relative_to(template)
        if destination.name.endswith(".template"):
            destination = destination.with_name(destination.name.removesuffix(".template"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        contents = source.read_text(encoding="utf-8")
        contents = contents.replace("__SKILL_NAME__", name)
        contents = contents.replace("__SKILL_YAML_DESCRIPTION__", json.dumps(description.strip(), ensure_ascii=False))
        contents = contents.replace("__SKILL_DESCRIPTION__", description.strip())
        destination.write_text(contents, encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Lowercase hyphenated skill name")
    parser.add_argument("--description", required=True, help="What the skill does and when to invoke it")
    parser.add_argument("--output", type=Path, default=Path("."), help="Parent output directory")
    args = parser.parse_args()
    try:
        print(f"Created draft: {scaffold(args.name, args.description, args.output)}")
        print("Next: replace TODOs, run scripts/validate.py, then perform REAL agent evaluations.")
    except (ValueError, FileExistsError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
