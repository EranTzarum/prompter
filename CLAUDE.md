# prompter

Claude Code session mode: `/prompter` → a UserPromptSubmit hook attaches `protocol.txt`
to every substantial message so Claude rebuilds it into a brief before acting.
Why and evidence: `docs/design.md`.

## Layout

- `SKILL.md`: the skill, with the full protocol. `protocol.txt`: the text the hook injects. Keep the two consistent; `protocol.txt` is the short form.
- `hooks/prompter_hook.py`: the hook (stdlib only).
- `scripts/check_allowlist.py`: the allowlist checker (stdlib only). It reads settings only.
- `tests/`: `unittest`. `tests/fixtures/`: real prompts that stopped early, and the case-5 settings.

## Rules

- The hook always exits 0 and prints nothing on bad input. Never let it block a prompt.
- The hook reads and writes only under `~/.claude/prompter/` (or `PROMPTER_HOME`). Session ids are validated.
- `check_allowlist.py` never writes settings, and never proposes rules for destructive commands or inline code.
- The protocol never grants authority the user didn't give.
- Stdlib only, no dependencies.
- **This repo is public.** No personal paths, usernames, private project or
  client names, real prompts or logs in any tracked file. Examples and fixtures
  use invented details with the same problem shape. Before every push:
  `node ~/.claude/skills/readmelyzer/scripts/check-readme.mjs . --public --all-files`
  must print no `LEAK:` line.

## Gate

```bash
py -3 -m unittest discover tests
```

Run it before every commit. Behaviour changes to the protocol also need a pass of `docs/evals.md`.

## Resuming work

Start at `docs/TAKEOVER.md`: state, open items, gate and release steps. The session runs from the umbrella folder and works only inside this repo.

