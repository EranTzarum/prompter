# Install prompter (instructions for an AI agent)

You are Claude Code, Codex, Cursor or Antigravity, and the user asked you to install this
skill from its GitHub link. Do the steps yourself; ask the user only where a step says
"ask". Finish with the short report at the bottom.

Repo: `https://github.com/EranTzarum/prompter`

Below, `PY` is `py -3` on Windows and `python3` elsewhere, and `HOOK` is the absolute path
to `~/.claude/skills/prompter/hooks/prompter_hook.py` with forward slashes, in double quotes.

## 1. Get the code (every host)

1. Clone it (skip if the folder exists; run `git pull` there instead):
   ```bash
   git clone https://github.com/EranTzarum/prompter.git ~/.claude/skills/prompter
   ```
2. Verify: run `PY -m unittest discover tests` in that folder. Expect `OK`. If it fails,
   stop and show the user the failing line.

## 2. Register the hook for the host you are

**Ask the user** once: "I need to add one hook entry to your <file> so prompter can attach
its brief to your messages. OK?" Only after a yes, merge the entry into the file. Keep every
other setting and hook as is, and add nothing if an entry running `prompter_hook.py` is
already there.

| You are | File | Entry |
|---|---|---|
| Claude Code | `~/.claude/settings.json` | under `"hooks"`: `"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "PY HOOK", "timeout": 5}]}]` |
| Codex | `~/.codex/hooks.json` | same as Claude Code. Then tell the user to trust it once with `/hooks` |
| Antigravity | `~/.gemini/config/hooks.json` | top level: `"prompter": {"PreInvocation": [{"type": "command", "command": "PY HOOK", "timeout": 10}]}` |
| Cursor | `~/.cursor/hooks.json` | under `"hooks"`: `"sessionStart": [{"command": "PY HOOK"}]` (keep `"version": 1`) |

Also copy `SKILL.md`, `protocol.txt` and `scripts/` into the host's skills folder so the agent
can read the full rules: `~/.codex/skills/prompter`, `~/.cursor/skills/prompter` or
`~/.gemini/config/skills/prompter`. Claude Code already has them.

## 3. Turn it on

Tell the user: "Installed. Type `/prompter always` once (in Claude Code or Codex) to have it
on in every new session, on every host." Cursor follows that switch only; per-session
`/prompter` and `prompter off` work in Claude Code, Codex and Antigravity.

## Final report

Say in 3 lines: what you installed, where, and the one thing the user does next. Nothing else.
