#!/usr/bin/env python3
"""Static-check Agent Skills + Skill Architect policy. DOES NOT execute an agent."""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    sys.stderr.write("Install required dependency: python -m pip install 'PyYAML>=6,<7'\n")
    raise SystemExit(2)

class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate frontmatter keys instead of silently keeping the last."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise yaml.constructor.ConstructorError(None, None, "duplicate or non-string mapping key", key_node.start_mark)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESOURCE_RE = re.compile(r"(?<![\w/])(?:references|scripts|assets|evals)/[A-Za-z0-9_./-]+\.[A-Za-z0-9_-]+")
def risky_code_patterns(tree: ast.AST) -> set[str]:
    """Flag risky executable AST forms, not references to those forms in docs/regexes."""
    findings: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
            if fn.value.id == "os" and fn.attr == "system":
                findings.add("os.system")
        for keyword in node.keywords:
            if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                findings.add("shell=True")
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if re.search(r"(?:curl|wget)\s+[^\n]*\|\s*(?:sh|bash)", arg.value):
                    findings.add("network installer")
    return findings


def validate(folder: Path, profile: str = "engineered") -> dict:
    if profile not in {"portable", "engineered"}:
        raise ValueError("Unknown validation profile")
    root = folder.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    def error(s: str) -> None:
        errors.append(s)

    def warn(s: str) -> None:
        warnings.append(s)

    if not root.is_dir():
        error("Target is not a directory")
        return _report(root, errors, warnings, checks)
    # Reject links before reading any package content, including linked directories.
    # This checker deliberately uses a stricter local package policy than the format.
    for path in root.rglob("*"):
        if path.is_symlink():
            error(f"Package policy: symlink is not supported: {path.relative_to(root)}")
    if errors:
        return _report(root, errors, warnings, checks)
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        error("SKILL.md is required by the Agent Skills specification")
        return _report(root, errors, warnings, checks)
    try:
        content = skill_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        error("SKILL.md must be readable UTF-8")
        return _report(root, errors, warnings, checks)
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", content, re.DOTALL)
    if not match:
        error("SKILL.md must begin with YAML frontmatter delimited by ---")
        return _report(root, errors, warnings, checks)
    try:
        meta = yaml.load(match.group(1), Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        error(f"Invalid YAML frontmatter: {exc}")
        return _report(root, errors, warnings, checks)
    if not isinstance(meta, dict):
        error("Frontmatter must be a YAML mapping")
        return _report(root, errors, warnings, checks)
    name = meta.get("name")
    desc = meta.get("description")
    if not isinstance(name, str) or len(name) > 64 or not NAME_RE.fullmatch(name):
        error("Invalid name: must be <=64 lowercase letters/digits, optionally separated by single hyphens")
    elif name != root.name:
        error(f"Skill name '{name}' must match parent directory '{root.name}'")
    if not isinstance(desc, str) or not desc.strip() or len(desc) > 1024:
        error("Invalid description: non-empty string up to 1024 characters required")
    if not match.group(2).strip():
        error("SKILL.md instruction body cannot be empty")
    if len(content.splitlines()) > 500:
        warn("SKILL.md exceeds the recommended 500-line limit; use progressive disclosure")
    if len(content.split()) > 3500:
        warn("SKILL.md is large; check its actual token count against the ~5,000-token guidance")
    compat = meta.get("compatibility")
    if compat is not None and (not isinstance(compat, str) or not compat.strip() or len(compat) > 500):
        error("compatibility must be a string <=500 characters")
    if "allowed-tools" in meta and not isinstance(meta["allowed-tools"], str):
        error("allowed-tools must be a string")
    if "license" in meta and not isinstance(meta["license"], str):
        error("license must be a string")
    if "metadata" in meta and (not isinstance(meta["metadata"], dict) or
            any(not isinstance(k, str) or not isinstance(v, str) for k, v in meta["metadata"].items())):
        error("metadata must map string keys to string values")
    unknown = set(meta) - {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    if unknown:
        warn("Unrecognised frontmatter fields require host review: " + ", ".join(map(str, unknown)))
    checks.append("Parsed Agent Skills YAML and instruction body")

    for file_name in (("SPEC.md", "README.md") if profile == "engineered" else ()):
        if not (root / file_name).is_file():
            error(f"Policy: missing {file_name} (extra engineering convention, not an open-spec requirement)")
    checks.append("Checked engineering and human documentation")

    link_targets = re.findall(r"\]\(([^)]+)\)", match.group(2))
    paths = set(RESOURCE_RE.findall(content))
    for link in link_targets:
        link = link.strip()
        if link.startswith("<") and ">" in link:
            link = link[1:link.index(">")]
        else:
            link = link.split(' "', 1)[0]
        if link.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link):
            continue
        paths.add(unquote(link.split("#", 1)[0]))
    for path_name in paths:
        resolved = (root / path_name).resolve()
        if not resolved.is_relative_to(root):
            error(f"Path escapes skill package: {path_name}")
        elif not resolved.is_file():
            error(f"Referenced resource does not exist: {path_name}")
    checks.append("Checked SKILL.md resource references")

    for relative in ("evals/triggers.json", "evals/scenarios.json"):
        if profile == "portable" and not (root / relative).exists():
            continue
        path = root / relative
        if not path.is_file():
            error(f"Policy: missing planned test definitions: {relative}")
            continue
        try:
            fixtures = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            error(f"Invalid JSON in {relative}: {exc}")
            continue
        if not isinstance(fixtures, list) or not fixtures:
            error(f"{relative} must be a non-empty array")
            continue
        seen = set()
        categories = set()
        for i, case in enumerate(fixtures):
            if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case.get("id"):
                error(f"{relative}[{i}] missing string id")
                continue
            if case["id"] in seen:
                error(f"{relative} duplicate case id '{case['id']}'")
            seen.add(case["id"])
            if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                error(f"{relative}[{i}] missing prompt")
            if "triggers" in relative:
                if not isinstance(case.get("should_trigger"), bool):
                    error(f"{relative}[{i}] missing boolean should_trigger")
                else:
                    categories.add(case["should_trigger"])
            else:
                if not isinstance(case.get("category"), str):
                    error(f"{relative}[{i}] missing category")
                elif not isinstance(case.get("acceptance"), list) or not case["acceptance"] or any(not isinstance(x, str) or not x.strip() for x in case["acceptance"]):
                    error(f"{relative}[{i}] missing acceptance criteria")
        if "triggers" in relative and categories != {True, False}:
            error("Trigger evaluations require both should_trigger=true and false cases")
        if any("TODO" in json.dumps(case) for case in fixtures):
            warn(f"{relative} contains TODO cases; cannot claim behavioral readiness")
    checks.append("Validated test plans, NOT test execution")

    for script in (root / "scripts").rglob("*.py") if (root / "scripts").is_dir() else []:
        source = script.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(script))
        except SyntaxError as exc:
            error(f"Syntax error in {script.name}: {exc}")
        else:
            for label in risky_code_patterns(tree):
                warn(f"Security triage: {script.name} contains {label}; manual inspection needed")
    checks.append("Checked Python syntax and selected risky patterns; no scripts executed")

    for path in root.rglob("*"):
        if path.is_symlink() and not path.resolve().is_relative_to(root):
            error(f"Symlink escapes package: {path.relative_to(root)}")
    checks.append("Checked symlinks remain within skill folder")

    for doc in ("SPEC.md", "SKILL.md"):
        path = root / doc
        if path.is_file() and "TODO" in path.read_text(encoding="utf-8"):
            warn(f"{doc} still contains TODO markers")
    return _report(root, errors, warnings, checks)


def _report(root: Path, errors: list[str], warnings: list[str], checks: list[str]) -> dict:
    return {
        "skill": str(root),
        "static_conformance": "fail" if errors else "pass",
        "conformance_scope": "Selected static checks and package policy; not full official format certification",
        "release_decision": "fail" if errors else "review",
        "behavioral_tests": "not-tested",
        "security_review": "not-tested",
        "ux_review": "not-tested",
        "errors": errors,
        "warnings": warnings,
        "checks_performed": checks,
        "interpretation": "Static checks do not establish safe behavior, quality, runtime host compatibility, or release readiness.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("skill", type=Path)
    p.add_argument("--profile", choices=("portable", "engineered"), default="engineered")
    p.add_argument("--json", action="store_true", help="Print machine-readable report")
    args = p.parse_args()
    result = validate(args.skill, args.profile)
    result["validation_profile"] = args.profile
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Static: {result['static_conformance'].upper()} | Release: {result['release_decision'].upper()}")
        for msg in result["errors"]:
            print(f"  ERROR: {msg}")
        for msg in result["warnings"]:
            print(f"  REVIEW: {msg}")
        print("Behavioral tests, security review and UX review: NOT TESTED")
    raise SystemExit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()
