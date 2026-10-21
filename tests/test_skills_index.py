"""Regression checks for metadata parsing and safe endpoint rebuilds."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_skills_index import build, skill_entries, validate_index


class SkillsIndexTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.home() / ".polymorfa-agent-work" / "agentkit-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        self.workspace = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.skills = self.root / "skills"
        self.skill = self.skills / "example"
        self.skill.mkdir(parents=True)
        self.write_skill("Set up the API.")

    def write_skill(self, description):
        (self.skill / "SKILL.md").write_text(
            f"---\nname: example\ndescription: {description}\n---\nBody.\n",
            encoding="utf-8",
        )

    def test_rejects_yaml_syntax_in_descriptions(self):
        descriptions = ["# fast", "Setup # fast", "Setup\t# fast", "Use API: safely",
                        "Use API:\tsafely", "Use API:", " leading", "trailing "]
        descriptions += [character + "value" for character in "-?:,[]{}#&*!|>'\"%@`"]
        for description in descriptions:
            with self.subTest(description=description):
                self.write_skill(description)
                with self.assertRaises(ValueError):
                    skill_entries(self.skills)

    def test_accepts_plain_description_punctuation(self):
        description = "Use https://example.com/#guide and C# with API:key."
        self.write_skill(description)
        output = build(self.skills, self.root / "output")
        validate_index(output, self.skills)
        self.assertEqual(json.loads((output / "index.json").read_text())["skills"][0]["description"], description)

    def test_rejects_overlapping_output_without_changing_sources(self):
        source = (self.skill / "SKILL.md").read_bytes()
        for output in (self.skills, self.root, self.skill, self.skills / "generated"):
            with self.subTest(output=output):
                with self.assertRaisesRegex(ValueError, "overlap"):
                    build(self.skills, output)
                self.assertEqual((self.skill / "SKILL.md").read_bytes(), source)
                self.assertFalse((self.skills / "generated").exists())

    def test_rejects_overlap_through_symlinked_ancestor(self):
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "overlap"):
            build(self.skills, alias / "skills" / "example" / "generated")
        self.assertTrue((self.skill / "SKILL.md").is_file())

    def test_rebuild_preserves_nested_files_and_removes_stale_files(self):
        references = self.skill / "references"
        references.mkdir()
        (references / "guide.md").write_bytes(b"Nested reference.\n")
        output = build(self.skills, self.root / "output")
        (output / "stale.json").write_text("broken")
        build(self.skills, output)
        validate_index(output, self.skills)
        self.assertFalse((output / "stale.json").exists())
        self.assertEqual((output / "example/references/guide.md").read_bytes(), b"Nested reference.\n")

    def test_validator_rebuilds_malformed_generated_json(self):
        checkout = self.root / "checkout"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
        output = checkout / "dist/well-known-skills"
        output.mkdir(parents=True)
        (output / "index.json").write_text("broken")
        (output / "stale.json").write_text("also broken")
        result = subprocess.run([sys.executable, str(checkout / "scripts/validate.py")],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skills", json.loads((output / "index.json").read_text()))
        self.assertFalse((output / "stale.json").exists())
        # Rebuilding generated state must not hide malformed source manifests.
        (checkout / "plugin.json").write_text("broken")
        result = subprocess.run([sys.executable, str(checkout / "scripts/validate.py")],
                                capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JSONDecodeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
