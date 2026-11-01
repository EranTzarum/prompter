# Install prompter (instructions for an AI agent)

You are Claude Code, Codex, Cursor or Antigravity, and the user asked you to install this
skill from its GitHub link. Do the steps yourself; ask the user only where a step says "ask".
`PY` below is `py -3` on Windows and `python3` elsewhere.

1. Clone the repo (skip if the folder exists; run `git pull` there instead):
   ```bash
   git clone https://github.com/EranTzarum/prompter.git ~/.claude/skills/prompter
   ```
2. Verify: in that folder run `PY -m unittest discover tests`. Expect `OK`. If it fails, stop
   and show the user the failing line.
3. **Ask the user**: "The installer adds one prompter hook entry to the config of each AI
   tool it finds (Claude Code, Codex, Cursor, Antigravity), copies the skill next to their
   other skills, and turns prompter on for every new session. OK?"
4. Only after a yes, run it from that folder:
   ```bash
   PY scripts/install.py
   ```
   It keeps every other setting, never adds a second prompter entry, and skips a config file
   it can't parse.
5. Report its output in 3 lines, then tell the user to restart any AI app that is open
   (Cursor, Codex, Antigravity), and in Codex to trust the new hook once with `/hooks`.
