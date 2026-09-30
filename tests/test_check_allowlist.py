import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_allowlist as ca  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


class RuleMatching(unittest.TestCase):
    def test_exact(self):
        self.assertTrue(ca.rule_matches("codex --version", "codex --version"))
        self.assertFalse(ca.rule_matches("codex --version", "codex --help"))

    def test_glob(self):
        self.assertTrue(ca.rule_matches("git status*", "git status -sb"))
        self.assertTrue(ca.rule_matches("git commit -m *", 'git commit -m "x y"'))
        self.assertFalse(ca.rule_matches("git add bin/*", "git add README.md"))

    def test_legacy_prefix(self):
        self.assertTrue(ca.rule_matches("npm test:*", "npm test -- --watch"))
        self.assertTrue(ca.rule_matches("npm test:*", "npm test"))
        self.assertFalse(ca.rule_matches("npm test:*", "npm testing"))

    def test_bare_tool_allows_all(self):
        allow = ca.parse_rules(["Bash"])
        self.assertTrue(ca.is_allowed("Bash", "anything at all", allow))

    def test_tool_scoping(self):
        allow = ca.parse_rules(["Bash(git status*)"])
        self.assertFalse(ca.is_allowed("PowerShell", "git status", allow))


class CompoundCommands(unittest.TestCase):
    def test_split(self):
        self.assertEqual(
            ca.split_compound('cd x && git status | head -3; echo "a;b"'),
            ["cd x", "git status", "head -3", 'echo "a;b"'],
        )

    def test_every_part_must_be_allowed(self):
        allow = ca.parse_rules(["Bash(codex debug models)"])
        self.assertFalse(ca.is_allowed("Bash", "codex debug models | py -3 -c x", allow))
        allow = ca.parse_rules(["Bash(codex debug models)", "Bash(py -3 -c *)"])
        self.assertTrue(ca.is_allowed("Bash", "codex debug models | py -3 -c x", allow))


class Proposals(unittest.TestCase):
    def test_two_token_prefix(self):
        self.assertEqual(ca.propose("Bash", "codex debug models --json"), "Bash(codex debug *)")
        self.assertEqual(ca.propose("Bash", "codex --version"), "Bash(codex --version)")

    def test_interpreter_is_pinned_to_the_script(self):
        self.assertEqual(ca.propose("Bash", "py -3 bin/tests/test_crew.py -k x"),
                         "Bash(py -3 bin/tests/test_crew.py *)")
        self.assertEqual(ca.propose("Bash", "py -3 -m unittest discover tests"),
                         "Bash(py -3 -m unittest *)")

    def test_inline_code_gets_no_rule(self):
        self.assertIsNone(ca.propose("Bash", 'py -3 -c "print(1)"'))
        self.assertIsNone(ca.propose("Bash", "node -e 1"))

    def test_push_is_exact_only(self):
        self.assertEqual(
            ca.propose("Bash", "git push origin feat/x"), "Bash(git push origin feat/x)"
        )

    def test_destructive_gets_no_rule(self):
        for cmd in ["rm -rf build", "git push --force origin main", "git reset --hard",
                    "Remove-Item -Recurse x", "Stop-Process -Name node",
                    "psql -c 'DELETE FROM users'", "DROP TABLE x"]:
            self.assertIsNone(ca.propose("Bash", cmd), cmd)


class Case5(unittest.TestCase):
    def run_cli(self, settings):
        out = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_allowlist.py"),
             "--commands", str(FIX / "case5-commands.txt"),
             "--settings", str(FIX / settings), "--json"],
            capture_output=True, text=True, check=False,
        )
        return out.returncode, json.loads(out.stdout)

    def test_before_everything_missing(self):
        code, report = self.run_cli("case5-settings-before.json")
        self.assertEqual(code, 1)
        self.assertEqual(len(report["missing"]), 7)

    def test_after_only_the_pipeline_tail_missing(self):
        code, report = self.run_cli("case5-settings-after.json")
        self.assertEqual(code, 1)
        self.assertEqual([m["part"] for m in report["missing"]],
                         ['py -3 -c "import sys,json; print(len(json.load(sys.stdin)))"'])

    def test_missing_settings_file_is_ignored(self):
        allow = ca.load_allow([FIX / "does-not-exist.json"])
        self.assertEqual(allow, [])


if __name__ == "__main__":
    unittest.main()
