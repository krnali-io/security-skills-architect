import importlib.util
import json
import contextlib
import io
import os
import subprocess
import time
from unittest.mock import patch
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import evaluate as ev


class TestEvaluation(unittest.TestCase):
    def test_codex_trace_requires_terminal_event(self):
        trace = json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "done"}})
        self.assertFalse(ev.parse_trace("codex", trace)["completed"])
        result = ev.parse_trace("codex", trace + '\n{"type":"turn.completed","usage":{"input_tokens":4}}')
        self.assertTrue(result["completed"])
        self.assertEqual(result["final"], "done")

    def test_claude_error_is_not_completion(self):
        result = ev.parse_trace("claude", '{"type":"result","subtype":"error_max_turns","is_error":true,"result":"looks fine"}')
        self.assertFalse(result["completed"])

    def test_tool_calls_are_recorded(self):
        result = ev.parse_trace("claude", '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Bash","input":{"command":"echo x"}}]}}')
        self.assertEqual(result["tool_calls"][0]["name"], "Bash")

    def test_artifacts_cannot_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("../outside", "/tmp/outside", ".codex/config.toml", "a/../../outside", "x\\y"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    ev.emit_artifacts(json.dumps({"artifacts": {name: "x"}}), root)
            self.assertEqual(list(root.iterdir()), [])

    def test_artifacts_are_captured_and_hashed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            result = ev.emit_artifacts('{"artifacts":{"demo/SKILL.md":"hello"}}', root)
            self.assertEqual((root / "demo/SKILL.md").read_text(), "hello")
            self.assertEqual(result[0]["sha256"], ev.digest(b"hello"))

    def test_expected_answer_not_sent_to_subject(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fake = root / "fake-host"
            fake.write_text('#!' + sys.executable + '\nimport json,sys\nprompt=sys.stdin.read()\nprint(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":"ok"}}))\nprint(json.dumps({"type":"turn.completed"}))\n')
            fake.chmod(0o700)
            case = {"id": "demo", "prompt": "actual task", "acceptance": ["SECRET_ORACLE"], "checks": [{"type": "contains", "value": "SECRET_ORACLE"}]}
            for variant in ("baseline", "with_skill"):
                out = root / variant
                result = ev.evaluate_case("codex", str(fake), None, case, variant, "scenarios", {}, "SKILL_GUIDANCE", out, 5)
                prompt = (out / "prompt.txt").read_text()
                self.assertNotIn("SECRET_ORACLE", prompt)
                self.assertEqual("SKILL_GUIDANCE" in prompt, variant == "with_skill")
                self.assertEqual(result["status"], "completed")
                self.assertEqual(result["automated_verdict"], "fail")

    def test_timeout_retains_trace(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            result = ev.run_process([sys.executable, "-c", 'import time; print("started", flush=True); time.sleep(10)'], "", root, root, 0.2)
            self.assertEqual(result["status"], "timeout")
            self.assertIn("started", (root / "trace.jsonl").read_text())

    def test_boolean_check_does_not_accept_integer(self):
        result = ev.check_output('{"use_skill":1}', [{"type":"json_field", "path":["use_skill"], "equals":True}], [])
        self.assertFalse(result[0]["passed"])

    def test_report_never_promotes_static_success_to_release(self):
        report = ev.report_results([], {"static_conformance": "pass"})
        self.assertEqual(report["release_decision"], "conditional_review")
        self.assertEqual(report["native_activation"], "not-tested")
        self.assertEqual(report["runs"], 0)

    def test_trigger_failure_blocks(self):
        report = ev.report_results([{"variant":"catalog", "kind":"triggers", "status":"completed", "automated_verdict":"fail"}], {"static_conformance":"pass"})
        self.assertEqual(report["release_decision"], "fail")

    def test_host_commands_do_not_bypass_permissions(self):
        for host in ("codex", "claude"):
            cmd = ev.command(host, host, Path("/tmp/work"), "test-model")
            self.assertNotIn("--dangerously-skip-permissions", cmd)
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", cmd)
            self.assertIn("test-model", cmd)

    def test_case_paths_and_unknown_checks_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "cases.json"
            for case in [
                {"id":"../outside", "prompt":"hello", "acceptance":["ok"]},
                {"id":"valid", "prompt":"hello", "acceptance":["ok"], "checks":[{"type":"run_shell"}]},
            ]:
                path.write_text(json.dumps([case]))
                with self.assertRaises(ValueError): ev.read_cases(path, "scenarios")


class EvaluationSecurityTests(unittest.TestCase):
    def skill(self, root):
        folder = root / "fixture-skill"
        folder.mkdir()
        (folder / "SKILL.md").write_text('---\nname: fixture-skill\ndescription: Audit supplied text.\n---\nUse supplied text.\n')
        return folder

    def test_hidden_and_unselected_files_never_enter_context(self):
        with tempfile.TemporaryDirectory() as d:
            skill = self.skill(Path(d))
            for name in ("references", "scripts", "assets"):
                folder = skill / name
                folder.mkdir()
                (folder / ".env").write_text("SYNTHETIC_HIDDEN_CANARY")
                (folder / ".private").mkdir()
                (folder / ".private" / "notes.txt").write_text("SYNTHETIC_HIDDEN_CANARY")
                (folder / "private.pem").write_text("SYNTHETIC_UNSELECTED_CANARY")
                (folder / "guidance.md").write_text("Visible fixture guidance")
            _, context, _ = ev.package_context(skill)
            self.assertNotIn("SYNTHETIC_HIDDEN_CANARY", context)
            self.assertNotIn("SYNTHETIC_UNSELECTED_CANARY", context)
            files = json.loads(context)
            self.assertEqual(len(files), 4)
            self.assertTrue(all("Visible fixture guidance" in files[name + "/guidance.md"] for name in ("references", "scripts", "assets")))

    def test_source_root_symlink_rejected_by_helper_and_cli(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = self.skill(root)
            alias = root / "linked"
            alias.symlink_to(skill, target_is_directory=True)
            with self.assertRaises(ValueError):
                ev.package_context(alias)
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/evaluate.py"), str(alias), "--host", "codex", "--output", str(root / "results")], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Symlink package root", result.stderr)
            self.assertFalse((root / "results").exists())

    def test_linked_resource_root_rejected_without_reading_canary(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = self.skill(root)
            private = root / "private"
            private.mkdir()
            (private / "notes.md").write_text("SYNTHETIC_PRIVATE_CANARY")
            (skill / "references").symlink_to(private, target_is_directory=True)
            with self.assertRaises(ValueError):
                ev.package_context(skill)

    def test_planner_lists_selected_paths_without_contents(self):
        import scaffold
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = scaffold.scaffold("fixture-skill", "Review supplied text.", root)
            for path in (skill / "evals").glob("*.json"):
                path.write_text(path.read_text().replace("TODO", "fixture"))
            (skill / "references").mkdir()
            (skill / "references/guidance.md").write_text("SELECTED_CONTENT_CANARY")
            (skill / "references/.env").write_text("HIDDEN_CONTENT_CANARY")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/evaluate.py"), str(skill), "--host", "codex", "--suite", "triggers", "--max-runs", "6", "--output", str(root / "results")], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["context_files"], ["SKILL.md", "references/guidance.md"])
            self.assertNotIn("SELECTED_CONTENT_CANARY", result.stdout)
            self.assertNotIn("HIDDEN_CONTENT_CANARY", result.stdout)
            self.assertFalse((root / "results").exists())

    def test_artifact_root_parent_and_leaf_symlinks_do_not_write_outside(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            outside = root / "outside"
            outside.mkdir()
            victim = outside / "victim.txt"
            victim.write_text("original")
            linked_root = root / "linked-artifacts"
            linked_root.symlink_to(outside, target_is_directory=True)
            with self.assertRaises((ValueError, OSError)):
                ev.emit_artifacts('{"artifacts":{"created.txt":"changed"}}', linked_root)
            artifacts = root / "artifacts"
            artifacts.mkdir()
            (artifacts / "linked-dir").symlink_to(outside, target_is_directory=True)
            (artifacts / "linked-file").symlink_to(victim)
            for name in ("linked-dir/created.txt", "linked-file"):
                with self.subTest(name=name), self.assertRaises((ValueError, OSError)):
                    ev.emit_artifacts(json.dumps({"artifacts":{name:"changed"}}), artifacts)
            self.assertFalse((outside / "created.txt").exists())
            self.assertEqual(victim.read_text(), "original")

    def test_normalized_duplicate_artifact_paths_are_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "artifacts"
            with self.assertRaises(ValueError):
                ev.emit_artifacts('{"artifacts":{"a/b.txt":"one","a//b.txt":"two"}}', folder)
            self.assertFalse(folder.exists())

    def test_existing_artifacts_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            (folder / "existing.txt").write_text("original")
            with self.assertRaises(FileExistsError):
                ev.emit_artifacts('{"artifacts":{"existing.txt":"changed"}}', folder)
            self.assertEqual((folder / "existing.txt").read_text(), "original")

    def test_fast_stdout_is_stream_limited(self):
        with tempfile.TemporaryDirectory() as d, patch.object(ev, "TRACE_LIMIT", 2048):
            root = Path(d)
            result = ev.run_process([sys.executable, "-c", 'import os;os.write(1,b"x"*8192)'], "", root, root, 3)
            self.assertEqual(result["status"], "output_limit")
            self.assertLessEqual((root / "trace.jsonl").stat().st_size, 2048)

    def test_stdout_and_stderr_share_one_budget(self):
        with tempfile.TemporaryDirectory() as d, patch.object(ev, "TRACE_LIMIT", 2048):
            root = Path(d)
            result = ev.run_process([sys.executable, "-c", 'import os;os.write(1,b"x"*1500);os.write(2,b"y"*1500)'], "", root, root, 3)
            self.assertEqual(result["status"], "output_limit")
            self.assertLessEqual(sum((root / name).stat().st_size for name in ("trace.jsonl", "stderr.txt")), 2048)

    def test_exactly_at_output_budget_can_complete(self):
        with tempfile.TemporaryDirectory() as d, patch.object(ev, "TRACE_LIMIT", 2048):
            root = Path(d)
            result = ev.run_process([sys.executable, "-c", 'import os;os.write(1,b"x"*2048)'], "", root, root, 3)
            self.assertEqual(result["status"], "completed")
            self.assertEqual((root / "trace.jsonl").stat().st_size, 2048)

    def test_child_cannot_extend_trace_after_leader_exit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            child = 'import time,os;time.sleep(.2);os.write(1,b"LATE_CHILD_CANARY")'
            parent = 'import subprocess,sys;subprocess.Popen([sys.executable,"-c",'+repr(child)+'])'
            result = ev.run_process([sys.executable, "-c", parent], "", root, root, 3)
            self.assertEqual(result["status"], "completed")
            first = (root / "trace.jsonl").read_bytes()
            time.sleep(.35)
            self.assertEqual((root / "trace.jsonl").read_bytes(), first)
            self.assertNotIn(b"LATE_CHILD_CANARY", first)

    def test_recursive_json_is_a_controlled_input_failure(self):
        nested = "["*1500 + "0" + "]"*1500
        with self.assertRaises(ValueError):
            ev.emit_artifacts(nested, Path("unused-artifacts"))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "cases.json"
            path.write_text(nested)
            with self.assertRaises(ValueError):
                ev.read_cases(path, "scenarios")
        self.assertFalse(ev.parse_trace("codex", nested)["completed"])

    def test_malformed_trace_fields_do_not_crash_parser(self):
        result = ev.parse_trace("codex", '{"type":"item.completed","item":null}\n{"type":"item.completed","item":{"type":"agent_message","text":["bad"]}}')
        self.assertTrue(result["errors"])
        self.assertEqual(result["final"], "")
        self.assertFalse(ev.parse_trace("claude", '{"type":"assistant","message":null}')["completed"])

    def test_execution_rejects_non_posix_without_starting_process(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with patch.object(ev.os, "name", "nt"), patch.object(ev.subprocess, "Popen") as start:
                result = ev.run_process(["not-a-real-host"], "", root, root, 3)
            self.assertEqual(result["status"], "unavailable")
            start.assert_not_called()


if __name__ == "__main__":
    unittest.main()
