#!/usr/bin/env python3
"""Build local review ZIPs with checksums; never publish or install them."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile

from validate import MAX_TEXT_BYTES, UniqueLoader, validate
import yaml

ROOT_FILES = {"SKILL.md", "SPEC.md", "README.md", "VALIDATION.md", "requirements-dev.txt", "release.json", "LICENSE", "LICENSE.txt", "LICENSE.md"}
TREES = {"agents", "references", "scripts", "templates", "tests"}
EVALS = {"evals/triggers.json", "evals/scenarios.json"}
SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".txt"}


def snapshot(skill: Path) -> tuple[str, str, dict[str, bytes]]:
    if skill.expanduser().is_symlink(): raise ValueError("Symlink package root is not supported")
    skill = skill.expanduser().resolve()
    report = validate(skill, "engineered")
    if report["static_conformance"] != "pass":
        raise ValueError(f"Invalid skill {skill.name}: {report['errors']}")
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    metadata = yaml.load(match.group(1), Loader=UniqueLoader)
    version = metadata.get("metadata", {}).get("version", "")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9][A-Za-z0-9.-]{0,63}", version):
        raise ValueError("A safe metadata.version is required for preview naming")
    files = {}
    for path in sorted(skill.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(skill)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        name = relative.as_posix()
        selected = name in ROOT_FILES or name in EVALS or name == "templates/skill/SKILL.md.template" or (relative.parts[0] in TREES and path.suffix in SUFFIXES)
        if selected:
            if path.stat().st_size > MAX_TEXT_BYTES: raise ValueError("Selected file exceeds 256 KiB limit")
            files[name] = path.read_bytes()
            if sum(len(data) for data in files.values()) > 1024 * 1024: raise ValueError("Selected package exceeds 1 MiB limit")
    # Check the selected artifact itself, not only the richer development tree.
    # A private/unsupported resource must not silently become a broken download.
    with tempfile.TemporaryDirectory() as staging:
        packaged = Path(staging) / metadata["name"]
        for name, data in files.items():
            target = packaged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        packaged_report = validate(packaged, "engineered")
        if packaged_report["static_conformance"] != "pass":
            raise ValueError(f"Selected preview is incomplete: {packaged_report['errors']}")
    return metadata["name"], version, files


def build(skills: list[Path], output: Path) -> dict:
    if not skills:
        raise ValueError("At least one skill is required")
    output = output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("Preview output already exists")
    packages = [snapshot(skill) for skill in skills]
    if len({name for name, _, _ in packages}) != len(packages):
        raise ValueError("Duplicate skill names")
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": "skill-preview-distribution/v1",
        "status": "local-review-preview",
        "published": False,
        "notice": "Checksums identify bytes, not signatures or behavioral certification. Public licence and release approval must be established separately.",
        "packages": [],
    }
    for name, version, files in packages:
        filename = f"{name}-{version}.zip"
        archive = output / filename
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
            for relative, data in sorted(files.items()):
                info = zipfile.ZipInfo(f"{name}/{relative}", date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, data)
        manifest["packages"].append({
            "name": name, "version": version, "archive": filename,
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "files": {relative: hashlib.sha256(data).hexdigest() for relative, data in sorted(files.items())},
        })
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    sums = [(p["archive"], p["sha256"]) for p in manifest["packages"]]
    sums.append(("manifest.json", hashlib.sha256(manifest_path.read_bytes()).hexdigest()))
    (output / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for name, digest in sorted(sums)), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.skill, args.output)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({"output": str(args.output), "archives": [p["archive"] for p in result["packages"]], "published": False}))


if __name__ == "__main__":
    main()
