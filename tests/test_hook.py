import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "hooks" / "prompter_hook.py"
FIX = ROOT / "tests" / "fixtures"
LONG = "Please fix the login bug and then update the docs. " * 8


class Hook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, PROMPTER_HOME=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def send(self, prompt, session="s1", raw=None):
        stdin = raw if raw is not None else json.dumps(
            {"session_id": session, "prompt": prompt, "hook_event_name": "UserPromptSubmit"})
        out = subprocess.run([sys.executable, str(HOOK)], input=stdin, env=self.env,
                             capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(out.returncode, 0, out.stderr)
        if not out.stdout.strip():
            return None
        return json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_off_by_default(self):
        self.assertIsNone(self.send(LONG))

    def test_on_then_long_prompt_gets_protocol(self):
        self.send("/prompter")
        ctx = self.send(LONG)
        self.assertIn("PROMPTER", ctx)
        self.assertIn("Brief", ctx)

    def test_short_replies_pass_through(self):
        self.send("/prompter")
        for p in ["yes", "go", "continue", "המשך", "ok do it"]:
            self.assertIsNone(self.send(p), p)

    def test_question_is_substantial(self):
        self.send("/prompter")
        self.assertIsNotNone(self.send("why did the build fail?"))

    def test_many_lines_is_substantial(self):
        self.send("/prompter")
        self.assertIsNotNone(self.send("a\nb\nc\nd\ne"))

    def test_slash_commands_pass_through(self):
        self.send("/prompter")
        self.assertIsNone(self.send("/code-review high " + LONG))

    def test_off_commands(self):
        for off in ["/prompter off", "prompter off", "stop prompter", "Prompter OFF please"]:
            self.send("/prompter")
            self.send(off)
            self.assertIsNone(self.send(LONG), off)

    def test_always_applies_to_new_sessions(self):
        self.send("/prompter always")
        self.assertIsNotNone(self.send(LONG, session="new"))

    def test_session_off_beats_always(self):
        self.send("/prompter always")
        self.send("prompter off", session="a")
        self.assertIsNone(self.send(LONG, session="a"))
        self.assertIsNotNone(self.send(LONG, session="b"))

    def test_always_off_restores_default(self):
        self.send("/prompter always")
        self.send("/prompter always off")
        self.assertIsNone(self.send(LONG))

    def test_sessions_are_isolated(self):
        self.send("/prompter", session="a")
        self.assertIsNotNone(self.send(LONG, session="a"))
        self.assertIsNone(self.send(LONG, session="b"))

    def test_bad_session_id_never_touches_disk_outside_home(self):
        self.send("/prompter", session="../../evil")
        self.assertEqual(list(Path(self.tmp.name).rglob("evil*")), [])

    def test_broken_stdin_is_silent(self):
        for raw in ["", "not json", "[]", '{"prompt": 5}']:
            self.assertIsNone(self.send(None, raw=raw), raw)

    def test_real_cases_are_substantial(self):
        self.send("/prompter")
        for i in range(1, 7):
            text = (FIX / f"prompter-case-{i}.txt").read_text(encoding="utf-8")
            self.assertIsNotNone(self.send(text), f"case {i}")


if __name__ == "__main__":
    unittest.main()
