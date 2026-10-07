"""prompter - Claude Code UserPromptSubmit hook.

/prompter turns the mode on for this session; "prompter off" turns it off.
"/prompter always" makes it the default for every new session; "/prompter always off"
undoes that (a session can still say "prompter off").
While on, every substantial message gets protocol.txt attached as additionalContext,
so Claude rebuilds it into a brief before acting. Always exits 0: a hook failure
must never block a prompt.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE.parent / "protocol.txt"
ALWAYS = re.compile(r"^\s*/prompter(:prompter)?\s+always(\s+off)?\s*$", re.I)
OFF = re.compile(r"^\s*(/prompter(:prompter)?\s+off\b|prompter\s+off\b|stop\s+prompter\b)", re.I)
ON = re.compile(r"^\s*/prompter(:prompter)?\s*$", re.I)
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def home_dir():
    return Path(os.environ.get("PROMPTER_HOME") or Path.home() / ".claude" / "prompter")


def enabled(flag):
    # session flag wins ("on"/"off"); with none, the global default decides
    if flag.exists():
        return flag.read_text(encoding="utf-8").strip() == "on"
    return (home_dir() / "always").exists()


def substantial(prompt):
    # ponytail: length/shape heuristic; swap for a classifier only if it misfires in real use
    p = prompt.strip()
    if p.startswith("/"):
        return False
    return (len(p) >= 300 or p.count("\n") >= 4
            or p.endswith("?") or p.count("?") >= 2)


def main():
    try:
        data = json.loads(sys.stdin.read())
        prompt, sid = data.get("prompt"), data.get("session_id")
    except (ValueError, AttributeError):
        return
    if not isinstance(prompt, str) or not isinstance(sid, str) or not SAFE_ID.match(sid):
        return
    flag = home_dir() / "active" / sid
    m = ALWAYS.match(prompt)
    if m:
        always = home_dir() / "always"
        if m.group(2):
            always.unlink(missing_ok=True)
        else:
            always.parent.mkdir(parents=True, exist_ok=True)
            always.write_text("on", encoding="utf-8")
        return
    if OFF.match(prompt):
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("off", encoding="utf-8")
        return
    if ON.match(prompt):
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("on", encoding="utf-8")
        return
    if enabled(flag) and substantial(prompt):
        text = PROTOCOL.read_text(encoding="utf-8")
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "additionalContext": text}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never block the user's prompt
        pass
    sys.exit(0)
