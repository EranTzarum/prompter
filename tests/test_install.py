import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import install  # noqa: E402


class Install(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.hook_path = install.hook_path  # the real one depends on where this repo was cloned
        install.hook_path = lambda home: "/opt/prompter/hooks/prompter_hook.py"

    def tearDown(self):
        install.hook_path = self.hook_path
        self.tmp.cleanup()

    def test_antigravity_refuses_a_path_with_spaces(self):
        (self.home / ".gemini/config").mkdir(parents=True)
        install.hook_path = lambda home: "/my files/prompter/hooks/prompter_hook.py"
        lines = install.install(self.home)
        self.assertFalse((self.home / ".gemini/config/hooks.json").exists())
        self.assertTrue(any(l.startswith("Antigravity: skipped") for l in lines))

    def read(self, rel):
        return json.loads((self.home / rel).read_text(encoding="utf-8"))

    def test_every_host_once_and_existing_config_kept(self):
        for d in (".claude", ".codex", ".cursor", ".gemini/config"):
            (self.home / d).mkdir(parents=True)
        (self.home / ".claude/settings.json").write_text(
            json.dumps({"model": "x", "hooks": {"Stop": [{"hooks": []}]}}), encoding="utf-8")
        install.install(self.home)
        install.install(self.home)  # second run changes nothing
        claude = self.read(".claude/settings.json")
        self.assertEqual(claude["model"], "x")
        self.assertIn("Stop", claude["hooks"])
        self.assertEqual(len(claude["hooks"]["UserPromptSubmit"]), 1)
        self.assertEqual(len(self.read(".codex/hooks.json")["hooks"]["UserPromptSubmit"]), 1)
        self.assertIn("PreInvocation", self.read(".gemini/config/hooks.json")["prompter"])
        cursor = self.read(".cursor/hooks.json")
        self.assertEqual((cursor["version"], len(cursor["hooks"]["sessionStart"])), (1, 1))
        for d in (".codex/skills", ".cursor/skills", ".gemini/config/skills"):
            self.assertTrue((self.home / d / "prompter/SKILL.md").exists(), d)
        self.assertTrue((self.home / ".claude/prompter/always").exists())

    def test_missing_host_skipped_and_bad_json_untouched(self):
        (self.home / ".codex").mkdir()
        (self.home / ".codex/hooks.json").write_text("{not json", encoding="utf-8")
        lines = install.install(self.home)
        self.assertEqual((self.home / ".codex/hooks.json").read_text(encoding="utf-8"), "{not json")
        self.assertTrue(any(l.startswith("Codex: skipped") for l in lines))
        self.assertTrue(any(l.startswith("Cursor: not installed") for l in lines))


if __name__ == "__main__":
    unittest.main()
