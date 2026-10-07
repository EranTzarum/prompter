# Install prompter (instructions for an AI agent)

You are Claude Code or Codex, and the user asked you to install this skill from its
GitHub link. Follow the section for the agent you are. Do the steps yourself; ask the user
only where a step says "ask". Finish with the short report at the bottom.

Repo: `https://github.com/EranTzarum/prompter`

## If you are Claude Code

1. Clone it into the skills folder (skip if it already exists; run `git pull` there instead):
   ```bash
   git clone https://github.com/EranTzarum/prompter.git ~/.claude/skills/prompter
   ```
2. Verify (use `py -3` instead of `python3` on Windows):
   ```bash
   cd ~/.claude/skills/prompter && python3 -m unittest discover tests
   ```
   Expect `OK`. If it fails, stop and show the user the failing line.
3. **Ask the user**: "I need to add one `UserPromptSubmit` hook entry to your
   `~/.claude/settings.json` so prompter can attach its brief to your messages. OK?"
   Only after a yes, merge this into the existing `hooks` object. Keep every other setting
   and hook as is, and do not add a duplicate if an entry running `prompter_hook.py`
   already exists:
   ```json
   "UserPromptSubmit": [{ "hooks": [{ "type": "command",
     "command": "python3 ~/.claude/skills/prompter/hooks/prompter_hook.py", "timeout": 5 }] }]
   ```
   On Windows use `py -3` instead of `python3`, and write the path with forward slashes in quotes.
4. Tell the user: "Installed. Open a new session and type `/prompter` to turn it on.
   Type `/prompter always` once to have it on in every new session."

## If you are Codex

Codex has no per-message hook, so this is the manual variant (experimental).

1. Fetch `https://raw.githubusercontent.com/EranTzarum/prompter/main/codex/AGENTS-snippet.md`.
2. Append everything below its `---` line to `~/.codex/AGENTS.md`. Create the file if it
   does not exist. If a `## prompter (manual variant)` heading is already there, replace that
   block instead of adding a second one.
3. Tell the user: "Installed. Open a new Codex session and send a task that is a few lines
   long. I should start with a short brief before touching any tool."

## Final report

Say in 3 lines: what you installed, where, and the one thing the user does next. Nothing else.
