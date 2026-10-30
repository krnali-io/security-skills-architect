import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_preview
import scaffold


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = scaffold.scaffold("fixture-skill", "Extract headings from supplied text.", self.root)
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text().replace("---\n\n#", 'metadata:\n  version: "0.1.0-preview.1"\n---\n\n#', 1))

    def test_reproducible_archives_and_matching_checksums(self):
        first = build_preview.build([self.skill], self.root / "one")
        second = build_preview.build([self.skill], self.root / "two")
        self.assertEqual(first, second)
        package = first["packages"][0]
        archive = self.root / "one" / package["archive"]
        self.assertEqual(package["sha256"], hashlib.sha256(archive.read_bytes()).hexdigest())
        with zipfile.ZipFile(archive) as bundle:
            for relative, digest in package["files"].items():
                self.assertEqual(hashlib.sha256(bundle.read("fixture-skill/" + relative)).hexdigest(), digest)

    def test_private_runs_and_unknown_files_are_excluded(self):
        private = self.skill / "evals/results/private"
        private.mkdir(parents=True)
        (private / "trace.json").write_text('{"private":"synthetic secret"}')
        (self.skill / ".env").write_text("SYNTHETIC=private")
        (self.skill / "profile.json").write_text('{"private":"app"}')
        result = build_preview.build([self.skill], self.root / "out")
        names = result["packages"][0]["files"]
        self.assertIn("evals/scenarios.json", names)
        self.assertFalse(any("results/" in name or name in {".env", "profile.json"} for name in names))

    def test_existing_output_refused(self):
        output = self.root / "out"
        output.mkdir()
        with self.assertRaises(FileExistsError):
            build_preview.build([self.skill], output)

    def test_omitted_referenced_private_resource_fails_without_leaking(self):
        (self.skill / "profile.json").write_text('{"private":"synthetic application"}')
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text() + "\nRead [the profile](profile.json).\n")
        with self.assertRaisesRegex(ValueError, "Selected preview is incomplete"):
            build_preview.build([self.skill], self.root / "out")
        self.assertFalse((self.root / "out").exists())

    def test_symlink_is_refused_before_content_is_packaged(self):
        (self.skill / "references").mkdir()
        (self.skill / "references/private.md").symlink_to(self.root / "missing")
        with self.assertRaises(ValueError):
            build_preview.build([self.skill], self.root / "out")
        self.assertFalse((self.root / "out").exists())

    def test_unsafe_version_and_duplicate_names_refused(self):
        with self.assertRaises(ValueError):
            build_preview.build([self.skill, self.skill], self.root / "duplicates")
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text().replace("0.1.0-preview.1", "../../escape"))
        with self.assertRaises(ValueError):
            build_preview.build([self.skill], self.root / "unsafe")
        self.assertFalse((self.root / "unsafe").exists())


if __name__ == "__main__":
    unittest.main()
