import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scaffold = load_tool("scaffold")
validate = load_tool("validate")


class TestTooling(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.skill = scaffold.scaffold("sample-skill", "Review patch changes. Use when reviewing code changes.", self.root)

    def test_scaffold_passes_static(self):
        report = validate.validate(self.skill)
        self.assertEqual(report["static_conformance"], "pass", report["errors"])
        self.assertEqual(report["release_decision"], "review")
        self.assertEqual(report["behavioral_tests"], "not-tested")

    def test_invalid_slug_rejected(self):
        with self.assertRaises(ValueError):
            scaffold.scaffold("Bad_Skill", "description", self.root)

    def test_description_with_colon_is_valid_yaml(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = scaffold.scaffold("colon-skill", "Review code: apply checks when asked.", Path(temp))
            self.assertEqual(validate.validate(folder)["static_conformance"], "pass")

    def test_missing_skill_rejected(self):
        (self.skill / "SKILL.md").unlink()
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_mismatched_name_rejected(self):
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text().replace("name: sample-skill", "name: another-skill"))
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_trigger_negative_required(self):
        path = self.skill / "evals" / "triggers.json"
        fixture = json.loads(path.read_text())
        path.write_text(json.dumps([f for f in fixture if f["should_trigger"]]))
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_missing_reference_rejected(self):
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text() + "\nRead references/nonexistent.md when needed.\n")
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_bad_script_rejected(self):
        scripts = self.skill / "scripts"
        scripts.mkdir()
        (scripts / "bad.py").write_text("def broken(:\n")
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_shell_true_is_warning(self):
        scripts = self.skill / "scripts"
        scripts.mkdir()
        (scripts / "dangerous.py").write_text("import subprocess\nsubprocess.run('whoami', shell=True)\n")
        report = validate.validate(self.skill)
        self.assertEqual(report["static_conformance"], "pass")
        self.assertTrue(any("shell=True" in warning for warning in report["warnings"]))

    def test_no_overwrite(self):
        with self.assertRaises(FileExistsError):
            scaffold.scaffold("sample-skill", "Different description", self.root)

    def test_duplicate_frontmatter_rejected(self):
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text().replace("name: sample-skill", "name: wrong\nname: sample-skill"))
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_portable_profile_does_not_require_engineering_files(self):
        for name in ("SPEC.md", "README.md", "evals/triggers.json", "evals/scenarios.json"):
            (self.skill / name).unlink()
        self.assertEqual(validate.validate(self.skill, "portable")["static_conformance"], "pass")
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_standard_markdown_link_checked(self):
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text() + "\n[Missing](missing.md)\n")
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")

    def test_symlink_read_refused_before_parsing(self):
        (self.skill / "SKILL.md").unlink()
        (self.skill / "SKILL.md").symlink_to(self.root / "nonexistent")
        report = validate.validate(self.skill)
        self.assertEqual(report["static_conformance"], "fail")
        self.assertTrue(any("symlink" in e for e in report["errors"]))

    def test_scaffold_dangling_symlink_refused(self):
        (self.root / "dangling-skill").symlink_to(self.root / "elsewhere")
        with self.assertRaises(FileExistsError):
            scaffold.scaffold("dangling-skill", "Useful description", self.root)
        self.assertFalse((self.root / "elsewhere").exists())

    def test_metadata_values_must_be_strings(self):
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text().replace("name: sample-skill", "name: sample-skill\nmetadata:\n  version: 1"))
        self.assertEqual(validate.validate(self.skill)["static_conformance"], "fail")


if __name__ == "__main__":
    unittest.main()
