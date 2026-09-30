"""Check that the shell commands a long run will need are allowlisted in Claude Code settings.

Usage:
  py -3 check_allowlist.py --commands cmds.txt [--settings a.json ...] [--json]

cmds.txt: one command per line; "PowerShell: <cmd>" for the PowerShell tool, Bash otherwise.
Lines starting with # are ignored. Without --settings, reads the user settings and the
project's .claude/settings.json and .claude/settings.local.json (cwd).
Exit 0 when everything is allowed, 1 when something is missing.

It only reads settings and prints proposals; it never writes settings.
"""
import argparse
import json
import re
import sys
from pathlib import Path

DESTRUCTIVE = re.compile(
    r"^(rm|rmdir|del|rd|Remove-Item|Stop-Process|kill|taskkill|format|shutdown|dd|mkfs)\b"
    r"|git\s+(push\s+.*(--force|-f\b)|reset\s+--hard|clean\s+-|branch\s+-D|checkout\s+--)"
    r"|\b(DROP|TRUNCATE|DELETE)\b",
    re.IGNORECASE,
)
EXACT_ONLY = re.compile(r"^(git\s+(push|merge|rebase|tag)|gh\s+|npm\s+publish)\b")
INTERPRETERS = {"py", "python", "python3", "node", "bash", "sh", "pwsh", "powershell"}
INLINE_CODE = {"-c", "-e", "--eval", "-Command", "-EncodedCommand"}


def split_compound(cmd):
    """Split on && || ; | outside quotes. Every part must be allowed on its own."""
    parts, cur, quote, i = [], "", None, 0
    while i < len(cmd):
        ch = cmd[i]
        if quote:
            cur += ch
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            cur += ch
        elif cmd.startswith(("&&", "||"), i):
            parts.append(cur)
            cur = ""
            i += 1
        elif ch in ";|":
            parts.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def rule_matches(body, cmd):
    if body.endswith(":*"):  # legacy prefix form
        prefix = body[:-2]
        return cmd == prefix or cmd.startswith(prefix + " ")
    pattern = re.escape(body).replace(r"\*", ".*")
    if body.endswith(" *"):  # "ls *" also matches bare "ls"
        pattern = pattern[: -len(r"\ .*")] + r"(\ .*)?"
    return re.fullmatch(pattern, cmd, re.DOTALL) is not None


def parse_rules(rules):
    parsed = []
    for r in rules:
        m = re.fullmatch(r"(\w+)(?:\((.*)\))?", r.strip(), re.DOTALL)
        if m:
            parsed.append((m.group(1), m.group(2)))
    return parsed


def part_allowed(tool, part, allow):
    return any(t == tool and (body is None or body == "*" or rule_matches(body, part))
               for t, body in allow)


def is_allowed(tool, cmd, allow):
    return all(part_allowed(tool, p, allow) for p in split_compound(cmd))


def propose(tool, part):
    """Narrowest useful rule for one command part, or None when it must stay a prompt."""
    if DESTRUCTIVE.search(part):
        return None
    tokens = part.split()
    if not tokens:
        return None
    if tokens[0] in INTERPRETERS:
        if any(t in INLINE_CODE for t in tokens):
            return None  # inline code: write a script file instead
        # pin to the script / module: keep flags up to and including the first non-flag token
        keep = []
        for t in tokens:
            keep.append(t)
            if len(keep) > 1 and not t.startswith("-"):
                break
        body = " ".join(keep)
    elif EXACT_ONLY.search(part) or len(tokens) <= 2:
        return f"{tool}({part})"
    else:
        body = " ".join(tokens[:2])
    return f"{tool}({part})" if body == part else f"{tool}({body} *)"


def load_allow(paths):
    rules = []
    for p in paths:
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rules += data.get("permissions", {}).get("allow", []) or []
    return parse_rules(rules)


def read_commands(path):
    cmds = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tool = "Bash"
        if line.startswith("PowerShell:"):
            tool, line = "PowerShell", line[len("PowerShell:"):].strip()
        cmds.append((tool, line))
    return cmds


def check(cmds, allow):
    missing, seen = [], set()
    for tool, cmd in cmds:
        for part in split_compound(cmd):
            if (tool, part) in seen or part_allowed(tool, part, allow):
                continue
            seen.add((tool, part))
            missing.append({"tool": tool, "command": cmd, "part": part,
                            "proposed": propose(tool, part)})
    return missing


def default_settings():
    home = Path.home() / ".claude" / "settings.json"
    proj = Path.cwd() / ".claude"
    return [home, proj / "settings.json", proj / "settings.local.json"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--commands", required=True)
    ap.add_argument("--settings", nargs="*")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    missing = check(read_commands(a.commands), load_allow(a.settings or default_settings()))
    if a.json:
        print(json.dumps({"missing": missing}, indent=2))
    elif not missing:
        print("All commands are allowlisted.")
    else:
        print(f"{len(missing)} command part(s) not allowlisted:")
        for m in missing:
            rule = m["proposed"] or "no rule proposed (destructive or inline code) - keep the prompt"
            print(f"- [{m['tool']}] {m['part']}\n    -> {rule}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
