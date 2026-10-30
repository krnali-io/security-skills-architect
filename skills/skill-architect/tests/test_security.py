"""Offline regressions for the public tooling security review."""
import importlib.util
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validate,build_preview,scaffold

class SecurityTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.skill=scaffold.scaffold('fixture-skill','Review supplied text safely.',self.root)
  p=self.skill/'SKILL.md';p.write_text(p.read_text().replace('---\n\n#','metadata:\n  version: "0.1.0"\n---\n\n#',1))
 def test_root_symlink_refused_before_validation(self):
  alias=self.root/'alias';alias.symlink_to(self.skill,target_is_directory=True)
  report=validate.validate(alias)
  self.assertEqual(report['static_conformance'],'fail');self.assertIn('symlink root',' '.join(report['errors']))
 def test_root_symlink_not_packaged(self):
  alias=self.root/'alias';alias.symlink_to(self.skill,target_is_directory=True)
  with self.assertRaisesRegex(ValueError,'Symlink'):build_preview.snapshot(alias)
 def test_recursive_yaml_returns_failure_without_echoing_content(self):
  p=self.skill/'SKILL.md';p.write_text('---\nname: fixture-skill\ndescription: PRIVATE_CANARY\nnested: '+'['*1200+'0'+']'*1200+'\n---\nBody\n')
  report=validate.validate(self.skill)
  self.assertEqual(report['static_conformance'],'fail');self.assertNotIn('PRIVATE_CANARY',str(report))
 def test_oversized_skill_rejected(self):
  (self.skill/'SKILL.md').write_text('x'*(validate.MAX_TEXT_BYTES+1))
  self.assertEqual(validate.validate(self.skill)['static_conformance'],'fail')
 def test_template_root_symlink_refused(self):
  fake=self.root/'package';(fake/'scripts').mkdir(parents=True);(fake/'templates').mkdir();external=self.root/'outside';external.mkdir();(external/'README.md').write_text('PRIVATE_CANARY')
  (fake/'templates/skill').symlink_to(external,target_is_directory=True)
  with patch.object(scaffold,'__file__',str(fake/'scripts/scaffold.py')):
   with self.assertRaisesRegex(ValueError,'Template roots'):scaffold.scaffold('another-skill','Useful description.',self.root)
  self.assertFalse((self.root/'another-skill').exists())
 def test_oversized_selected_reference_not_archived(self):
  (self.skill/'references').mkdir();(self.skill/'references/large.md').write_text('x'*(validate.MAX_TEXT_BYTES+1))
  with self.assertRaisesRegex(ValueError,'limit'):build_preview.snapshot(self.skill)

if __name__=='__main__':unittest.main()
