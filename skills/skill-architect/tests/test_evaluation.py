import importlib.util
import json
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


if __name__ == "__main__":
    unittest.main()
