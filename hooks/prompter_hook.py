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
SYSTEM = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
SESSION_NOTE = ("PROMPTER is on for this whole session. Apply the rules below to every substantial "
                "user message (300+ characters, 5+ lines, or a question). Short replies such as yes, "
                "go or continue skip them. If the user says \"prompter off\", stop applying them.\n")
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
    # Harness status pings arrive as <system-reminder> blocks; only the user's own text counts.
    p = SYSTEM.sub("", prompt).strip()
    if p.startswith("/"):
        return False
    return (len(p) >= 300 or p.count("\n") >= 4
            or p.endswith("?") or p.count("?") >= 2)


def main():
    try:
        data = json.loads(sys.stdin.read())
    except ValueError:
        return
    if not isinstance(data, dict):
        return
    if data.get("hook_event_name") == "sessionStart":
        # Cursor: its per-prompt hook can't add context, so the always-on default
        # attaches the protocol once, for the whole session.
        if (home_dir() / "always").exists():
            print(json.dumps({"additional_context": SESSION_NOTE + PROTOCOL.read_text(encoding="utf-8")}))
        return
    agy = "lastUserInput" in data  # Antigravity PreInvocation: runs before every model call
    prompt = data.get("lastUserInput") if agy else data.get("prompt")
    sid = data.get("conversationId") if agy else data.get("session_id")
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
        if agy:  # an ephemeral step reaches the model; a systemMessage step did not (tested)
            print(json.dumps({"injectSteps": [{"ephemeralMessage": text}]}))
            return
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "additionalContext": text}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never block the user's prompt
        pass
    sys.exit(0)
