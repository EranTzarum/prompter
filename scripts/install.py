"""Install prompter on every AI host found on this machine.

    python3 scripts/install.py          (Windows: py -3 scripts/install.py)

For each host whose config folder exists, it adds one hook entry that runs
hooks/prompter_hook.py and copies the skill files where that host looks for skills.
Then it turns prompter on for every new session. Safe to run again: an entry that
already runs prompter_hook is left alone. A config file it can't parse is skipped,
never overwritten.

    Claude Code   ~/.claude/settings.json      UserPromptSubmit
    Codex         ~/.codex/hooks.json          UserPromptSubmit (trust it once with /hooks)
    Antigravity   ~/.gemini/config/hooks.json  PreInvocation
    Cursor        ~/.cursor/hooks.json         sessionStart
"""
import json
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = "prompter_hook"
SKILL_FILES = ["SKILL.md", "protocol.txt", "scripts"]


def hook_path(home):
    # Prefer the skills link: it usually has no spaces, and Antigravity can't run a path with spaces.
    link = home / ".claude/skills/prompter"
    base = link if link.exists() and link.resolve() == ROOT else ROOT
    return (base / "hooks" / "prompter_hook.py").as_posix()


def command(hook):
    py = "py -3" if platform.system() == "Windows" else "python3"
    return f'{py} "{hook}"' if " " in hook else f"{py} {hook}"


def load(path):
    if not path.exists():
        return {}
    cfg = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(cfg, dict):
        raise ValueError("not a JSON object")
    return cfg


def save(path, cfg):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8", newline="\n")


def add_entry(path, place, cmd):
    """place(cfg) adds the entry; returns a status line. Skips if prompter is already there."""
    try:
        cfg = load(path)
    except ValueError as e:
        return f"skipped, can't parse {path} ({e}); fix it and run again"
    if MARK in json.dumps(cfg):
        return "hook already set"
    place(cfg, cmd)
    save(path, cfg)
    return f"hook added to {path}"


def claude_like(cfg, cmd):
    cfg.setdefault("hooks", {}).setdefault("UserPromptSubmit", []).append(
        {"hooks": [{"type": "command", "command": cmd, "timeout": 5}]})


def antigravity(cfg, cmd):
    cfg["prompter"] = {"PreInvocation": [{"type": "command", "command": cmd, "timeout": 10}]}


def cursor(cfg, cmd):
    cfg.setdefault("version", 1)
    cfg.setdefault("hooks", {}).setdefault("sessionStart", []).append({"command": cmd})


def copy_skill(dest):
    if dest.exists() and dest.resolve() == ROOT:
        return
    dest.mkdir(parents=True, exist_ok=True)
    for name in SKILL_FILES:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, dest / name, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, dest / name)


def install(home):
    hosts = [
        ("Claude Code", home / ".claude", home / ".claude/settings.json", claude_like, home / ".claude/skills/prompter"),
        ("Codex", home / ".codex", home / ".codex/hooks.json", claude_like, home / ".codex/skills/prompter"),
        ("Antigravity", home / ".gemini/config", home / ".gemini/config/hooks.json", antigravity,
         home / ".gemini/config/skills/prompter"),
        ("Cursor", home / ".cursor", home / ".cursor/hooks.json", cursor, home / ".cursor/skills/prompter"),
    ]
    hook = hook_path(home)
    cmd = command(hook)
    lines = []
    for name, folder, cfg, place, skills in hosts:
        if not folder.is_dir():
            lines.append(f"{name}: not installed, skipped")
            continue
        if place is antigravity and " " in hook:
            lines.append(f"{name}: skipped, it can't run a hook path with spaces ({hook}); "
                         "clone prompter to a path without spaces and run again")
            continue
        status = add_entry(cfg, place, cmd)
        if not status.startswith("skipped"):
            copy_skill(skills)
            status += "; skill copied" if skills.resolve() != ROOT else ""
        if name == "Codex" and status.startswith("hook added"):
            status += "; open Codex and trust it once with /hooks"
        lines.append(f"{name}: {status}")
    flag = home / ".claude/prompter/always"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("on", encoding="utf-8")
    lines.append("prompter is on in every new session (/prompter always off to undo)")
    return lines


def main(argv):
    home = Path(argv[argv.index("--home") + 1]) if "--home" in argv else Path.home()
    for line in install(home):
        print(line)
    print("Restart open apps (Cursor, Codex, Antigravity) so they load the hook and the skill.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
