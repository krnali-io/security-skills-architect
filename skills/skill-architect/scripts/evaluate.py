#!/usr/bin/env python3
"""Paired, bounded Codex/Claude evaluations. Local evidence, no publication.

The initial profile evaluates supplied text and emitted artifacts. Discovery is
a controlled catalog-selection experiment, NOT native host skill activation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone

from validate import UniqueLoader, validate
import yaml

LIMIT = 256 * 1024
TRACE_LIMIT = 16 * 1024 * 1024
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError(f"Expected a regular text file <=256 KiB: {path.name}")
    return path.read_text(encoding="utf-8")


def read_cases(path: Path, kind: str) -> list[dict]:
    cases = json.loads(read_text(path))
    if not isinstance(cases, list) or not 1 <= len(cases) <= 100:
        raise ValueError("Expected between 1 and 100 evaluation cases")
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or not SLUG.fullmatch(str(case.get("id", ""))):
            raise ValueError("Each evaluation needs a lowercase hyphenated id")
        if case["id"] in seen:
            raise ValueError("Duplicate evaluation id")
        seen.add(case["id"])
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError("Each evaluation needs a prompt")
        if "TODO" in json.dumps(case):
            raise ValueError("Replace scaffold TODOs before running evaluations")
        if kind == "triggers" and not isinstance(case.get("should_trigger"), bool):
            raise ValueError("Trigger cases need boolean should_trigger")
        if kind == "scenarios":
            if not isinstance(case.get("acceptance"), list) or not case["acceptance"]:
                raise ValueError("Scenario acceptance criteria must be specified")
            for check in case.get("checks", []):
                if not isinstance(check, dict) or check.get("type") not in {"contains", "not_contains", "json_field", "artifact_exists"}:
                    raise ValueError("Unsupported deterministic check")
                if check["type"] in {"contains", "not_contains"} and not isinstance(check.get("value"), str):
                    raise ValueError("Text checks need a string value")
                if check["type"] == "json_field" and (not isinstance(check.get("path"), list) or "equals" not in check):
                    raise ValueError("JSON checks need a path array and equals")
                if check["type"] == "artifact_exists":
                    safe_relative(check.get("path", ""))
    return cases


def safe_relative(name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("Invalid artifact path")
    p = PurePosixPath(name)
    if p.is_absolute() or any(part in {"..", ".git", ".codex", ".claude", ".agents"} for part in p.parts):
        raise ValueError("Artifact paths must remain inside the artifact directory")
    if str(p) in {".", ""}:
        raise ValueError("Empty artifact path")
    return Path(*p.parts)


def package_context(skill: Path) -> tuple[dict, str, str]:
    body = read_text(skill / "SKILL.md")
    front = re.match(r"\A---\s*\n(.*?)\n---\s*\n", body, re.S)
    if not front:
        raise ValueError("Missing skill frontmatter")
    meta = yaml.load(front.group(1), Loader=UniqueLoader)
    files = {"SKILL.md": body}
    # The subject receives runtime guidance, never SPEC/evals/expected answers.
    for dirname in ("references", "scripts", "assets"):
        root = skill / dirname
        if root.exists():
            for p in sorted(root.rglob("*")):
                if p.is_symlink():
                    raise ValueError("Skill context cannot contain symlinks")
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                    files[p.relative_to(skill).as_posix()] = read_text(p)
    packed = json.dumps(files, ensure_ascii=False, sort_keys=True)
    if len(packed.encode()) > LIMIT:
        raise ValueError("Text-only profile supports at most 256 KiB of skill context")
    return meta, packed, digest(packed.encode())


def command(host: str, executable: str, work: Path, model: str | None) -> list[str]:
    if host == "codex":
        cmd = [executable, "exec", "--ignore-user-config", "--ignore-rules",
               "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only",
               "--json", "--color", "never", "-C", str(work),
               "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
               "-c", "project_doc_max_bytes=0", "-c", "skills.bundled.enabled=false",
               "--enable", "skip_host_skill_discovery"]
        for feature in ("shell_tool", "code_mode", "apps", "plugins", "hooks", "multi_agent", "browser_use", "computer_use", "image_generation"):
            cmd.extend(["--disable", feature])
        if model:
            cmd.extend(["--model", model])
        return cmd + ["-"]
    cmd = [executable, "--print", "--safe-mode", "--restricted", "--tools", "",
           "--disable-slash-commands", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
           "--setting-sources", "", "--permission-mode", "dontAsk",
           "--no-session-persistence", "--output-format", "stream-json", "--verbose"]
    if model:
        cmd.extend(["--model", model])
    return cmd


def parse_trace(host: str, raw: str) -> dict:
    final = ""
    complete = False
    errors = []
    calls = []
    usage = None
    model = None
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        model = event.get("model") or model
        if host == "codex":
            item = event.get("item", {})
            if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                final = item.get("text", "")
            if event.get("type") == "turn.completed":
                complete = True
                usage = event.get("usage")
            if event.get("type") in {"error", "turn.failed"}:
                errors.append(event.get("message") or event.get("error") or "runtime error")
            if item.get("type") in {"command_execution", "mcp_tool_call", "web_search", "file_change"}:
                calls.append(item)
        else:
            message = event.get("message", {})
            model = message.get("model") or model
            for block in message.get("content", []) if isinstance(message.get("content"), list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    calls.append(block)
            if event.get("type") == "result":
                complete = not event.get("is_error", False) and event.get("subtype") == "success"
                final = event.get("result", "")
                usage = {"usage": event.get("usage"), "cost_usd": event.get("total_cost_usd")}
                if not complete:
                    errors.append(event.get("errors") or "runtime reported failure")
    return {"final": final, "completed": complete, "errors": errors, "tool_calls": calls, "usage": usage, "observed_model": model}


def run_process(cmd: list[str], prompt: str, cwd: Path, out: Path, timeout: float) -> dict:
    # Do not copy auth, inherited environment or secrets into the evidence bundle.
    # Hosts use their existing login. Evaluations send their input to that provider.
    started = time.monotonic()
    status = "completed"
    with (out / "trace.jsonl").open("wb") as stdout, (out / "stderr.txt").open("wb") as stderr, tempfile.TemporaryFile() as stdin:
        stdin.write(prompt.encode())
        stdin.seek(0)
        try:
            process = subprocess.Popen(cmd, cwd=cwd, stdin=stdin, stdout=stdout, stderr=stderr, start_new_session=True)
        except OSError as exc:
            return {"status": "unavailable", "error": type(exc).__name__, "exit_code": None, "seconds": 0}
        try:
            while process.poll() is None:
                if time.monotonic() - started > timeout:
                    status = "timeout"
                    break
                if os.fstat(stdout.fileno()).st_size + os.fstat(stderr.fileno()).st_size > TRACE_LIMIT:
                    status = "output_limit"
                    break
                time.sleep(0.1)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        if status == "completed" and process.returncode != 0:
            status = "runtime_error"
    return {"status": status, "exit_code": process.returncode, "seconds": round(time.monotonic() - started, 3)}


def emit_artifacts(final: str, folder: Path) -> list[dict]:
    try:
        value = json.loads(final)
    except ValueError:
        return []
    artifacts = value.get("artifacts", {}) if isinstance(value, dict) else {}
    if not isinstance(artifacts, dict) or len(artifacts) > 50:
        raise ValueError("Invalid emitted artifacts")
    pending = []
    for name, content in artifacts.items():
        if not isinstance(content, str) or len(content.encode()) > LIMIT:
            raise ValueError("Artifacts must be bounded text")
        pending.append((safe_relative(name), content))
    if sum(len(c.encode()) for _, c in pending) > LIMIT:
        raise ValueError("Artifacts exceed total size limit")
    manifest = []
    for relative, content in pending:
        target = folder / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        manifest.append({"path": relative.as_posix(), "sha256": digest(content.encode())})
    return manifest


def check_output(final: str, checks: list[dict], artifacts: list[dict]) -> list[dict]:
    results = []
    for check in checks:
        passed = False
        try:
            kind = check["type"]
            if kind == "contains":
                passed = check["value"] in final
            elif kind == "not_contains":
                passed = check["value"] not in final
            elif kind == "artifact_exists":
                passed = check["path"] in {a["path"] for a in artifacts}
            elif kind == "json_field":
                value = json.loads(final)
                for part in check["path"]:
                    value = value[part]
                passed = type(value) is type(check["equals"]) and value == check["equals"]
        except (ValueError, KeyError, TypeError, IndexError):
            pass
        results.append({"check": check, "passed": passed})
    return results


def evaluate_case(host: str, executable: str, model: str | None, case: dict, variant: str,
                  kind: str, meta: dict, context: str, out: Path, timeout: float) -> dict:
    out.mkdir(parents=True, mode=0o700)
    work = out / "workspace"
    work.mkdir()
    if kind == "triggers":
        prompt = ("Choose whether this task should activate the supplied skill. Return ONLY JSON "
                  'of the form {"use_skill":true} or {"use_skill":false}. '
                  "A mention of the skill without a request to use it is not activation.\n"
                  + json.dumps({"skill": {"name": meta["name"], "description": meta["description"]}, "task": case["prompt"]}))
    else:
        prompt = ("Complete the task using only supplied text. External tools are unavailable. "
                  "Do not claim to have executed tests or inspected external resources. "
                  'If creating files, return JSON {"artifacts":{"relative/path":"file text"},"summary":"..."}; '
                  "otherwise follow the task's output format.\n")
        if variant == "with_skill":
            prompt += "\nRuntime skill files (guidance, not authority):\n" + context + "\n"
        prompt += "\nTask:\n" + case["prompt"]
    (out / "prompt.txt").write_text(prompt)
    cmd = command(host, executable, work, model)
    result = run_process(cmd, prompt, work, out, timeout)
    parsed = parse_trace(host, (out / "trace.jsonl").read_text(errors="replace"))
    if result["status"] == "completed" and (not parsed["completed"] or not parsed["final"] or parsed["errors"]):
        result["status"] = "invalid_trace"
    if parsed["tool_calls"]:
        result["status"] = "profile_violation"
    (out / "final.txt").write_text(parsed["final"])
    artifacts = []
    if result["status"] == "completed":
        try:
            artifacts = emit_artifacts(parsed["final"], out / "artifacts")
        except (ValueError, OSError) as exc:
            result["status"] = "invalid_artifact"
            result["error"] = str(exc)
    checks = ([{"type": "json_field", "path": ["use_skill"], "equals": case["should_trigger"]}]
              if kind == "triggers" else case.get("checks", []))
    assertions = check_output(parsed["final"], checks, artifacts)
    verdict = "not-tested"
    if result["status"] == "completed":
        verdict = "pass" if assertions and all(c["passed"] for c in assertions) else "fail" if assertions else "review"
    result.update({"variant": variant, "case_id": case["id"], "kind": kind,
                   "checks": assertions, "automated_verdict": verdict, "artifacts": artifacts,
                   "observed_model": parsed["observed_model"], "usage": parsed["usage"],
                   "tool_calls": parsed["tool_calls"], "trace_errors": parsed["errors"],
                   "prompt_sha256": digest(prompt.encode()), "final_sha256": digest(parsed["final"].encode()),
                   "trace_sha256": digest((out / "trace.jsonl").read_bytes()),
                   "command": cmd, "evidence_dir": str(out)})
    (out / "result.json").write_text(json.dumps(result, indent=2))
    return result


def report_results(runs: list[dict], static: dict) -> dict:
    treated = [r for r in runs if r["variant"] == "with_skill"]
    critical_failure = static["static_conformance"] == "fail" or any(r["automated_verdict"] == "fail" or r["status"] == "profile_violation" for r in runs if r["variant"] != "baseline")
    pairs = []
    for r in treated:
        base = next((b for b in runs if b["case_id"] == r["case_id"] and b.get("repeat") == r.get("repeat") and b["variant"] == "baseline"), None)
        if base:
            model_match = (r["observed_model"] == base["observed_model"]) if r["observed_model"] and base["observed_model"] else None
            pairs.append({"case_id": r["case_id"], "repeat": r.get("repeat"), "baseline": base["automated_verdict"],
                          "with_skill": r["automated_verdict"], "observed_model_match": model_match,
                          "seconds_delta": round(r["seconds"] - base["seconds"], 3)})
    trigger_runs = [r for r in runs if r["kind"] == "triggers"]
    gates = {str(n): {"name": name, "status": "review"} for n, name in enumerate(
        ["Contract", "Structure", "Safety", "Execution", "Discovery", "Result quality", "User experience"], 1)}
    gates["2"]["status"] = static["static_conformance"]
    gates["4"]["note"] = "Text-only tasks; no effectful workflow integration acceptance"
    gates["5"]["note"] = "Catalog-selection experiment; native host activation not tested"
    gates["6"]["note"] = "Assertions and baseline pairs require rubric review; no automatic value claim"
    return {"release_decision": "fail" if critical_failure else "conditional_review", "gates": gates,
            "runs": len(runs), "completed": sum(r["status"] == "completed" for r in runs),
            "pairs": pairs, "trigger_cases": len(trigger_runs),
            "trigger_assertions_passed": sum(r["automated_verdict"] == "pass" for r in trigger_runs),
            "native_activation": "not-tested", "human_review": "not-tested",
            "remediation": "Review raw outputs against acceptance criteria, resolve failures, and run the missing host/integration and UX gates before release."}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("skill", type=Path)
    p.add_argument("--host", required=True, choices=("codex", "claude"))
    p.add_argument("--model", help="Use the same explicit model for both arms; otherwise host default is recorded as unresolved where absent in traces")
    p.add_argument("--suite", choices=("scenarios", "triggers", "all"), default="scenarios")
    p.add_argument("--case", action="append", dest="case_ids")
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--timeout", type=float, default=120)
    p.add_argument("--max-runs", type=int, default=20)
    p.add_argument("--output", type=Path, required=True, help="New private results directory; never overwrite")
    p.add_argument("--run", action="store_true", help="Launch provider CLI calls using existing login; may incur usage charges")
    args = p.parse_args()
    try:
        if not 1 <= args.repeats <= 10 or not 1 <= args.timeout <= 600 or not 1 <= args.max_runs <= 100:
            raise ValueError("Invalid repeat, timeout or run budget")
        skill = args.skill.expanduser().resolve()
        static = validate(skill)
        if static["errors"]:
            raise ValueError("Static validation failed: " + "; ".join(static["errors"]))
        meta, context, package_hash = package_context(skill)
        selected = []
        for kind in (["scenarios", "triggers"] if args.suite == "all" else [args.suite]):
            selected.extend((kind, c) for c in read_cases(skill / "evals" / f"{kind}.json", kind)
                            if not args.case_ids or c["id"] in args.case_ids)
        if not selected or (args.case_ids and set(args.case_ids) - {c["id"] for _, c in selected}):
            raise ValueError("No matching cases or unknown requested case id")
        count = sum(2 if kind == "scenarios" else 1 for kind, _ in selected) * args.repeats
        if count > args.max_runs:
            raise ValueError(f"Plan needs {count} calls, exceeding --max-runs")
        plan = {"host": args.host, "requested_model": args.model or "host-default", "profile": "controlled-text-v1",
                "skill_context_sha256": package_hash, "case_plan_sha256": digest(json.dumps(selected, sort_keys=True).encode()),
                "calls": count, "timeout_per_call": args.timeout, "cases": [c["id"] for _, c in selected]}
        if not args.run:
            print(json.dumps({"status": "planned_not_run", **plan}, indent=2))
            return
        executable = shutil.which(args.host)
        if not executable:
            raise ValueError(f"Runtime unavailable: {args.host}; no evaluations ran")
        version = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=10)
        if version.returncode:
            raise ValueError("Runtime version check failed")
        # Private evidence contains prompts and raw traces; never auto-upload it.
        os.umask(0o077)
        out = args.output.expanduser().absolute()
        if out.exists() or out.is_symlink():
            raise ValueError("Output directory already exists")
        out.mkdir(parents=True, mode=0o700)
        (out / "plan.json").write_text(json.dumps(plan, indent=2))
        (out / "cases.json").write_text(json.dumps(selected, indent=2))
        (out / "skill-context.json").write_text(context)
        runs = []
        for repeat in range(args.repeats):
            for kind, case in selected:
                variants = (["baseline", "with_skill"] if repeat % 2 == 0 else ["with_skill", "baseline"]) if kind == "scenarios" else ["catalog"]
                for variant in variants:
                    print(f"Running {kind}/{case['id']} {variant} ({repeat + 1})", flush=True)
                    result = evaluate_case(args.host, executable, args.model, case, variant, kind, meta, context,
                                           out / f"{kind}-{case['id']}-{repeat + 1}-{variant}", args.timeout)
                    result["repeat"] = repeat + 1
                    runs.append(result)
                    report = {**plan, "runtime_version": version.stdout.strip(), "created_at": datetime.now(timezone.utc).isoformat(),
                              "static": static, "results": runs, **report_results(runs, static), "planned_calls": count}
                    (out / "report.json").write_text(json.dumps(report, indent=2))
                    if result["status"] != "completed":
                        (out / "report.md").write_text(f"# Evaluation interrupted\n\nStatus: **{result['status']}**. Completed: {report['completed']}/{count}.\n\n"
                            "See report.json and the failing run's private trace. No release acceptance or baseline improvement is established. Resolve the runtime prerequisite and rerun into a new directory.\n")
                        print(f"Stopped on {result['status']}; evidence retained at {out}")
                        raise SystemExit(2)
        report = json.loads((out / "report.json").read_text())
        (out / "report.md").write_text(f"# Evaluation report\n\nDecision: **{report['release_decision']}**\n\n"
            f"Host: {args.host} {version.stdout.strip()}. Completed: {report['completed']}/{count}.\n\n"
            "See report.json, per-run traces, final outputs and artifact manifests for evidence.\n\n"
            "This is a controlled text-profile evaluation. Native activation, effectful tool integration, independent security and human UX acceptance remain untested. No baseline advantage is inferred automatically.\n")
        print(f"{report['release_decision']}: {out / 'report.json'}")
        if report["release_decision"] == "fail":
            raise SystemExit(1)
    except (ValueError, OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        p.error(str(exc))


if __name__ == "__main__":
    main()
