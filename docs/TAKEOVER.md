# prompter: takeover

For the session that continues prompter. Read this first, then `CLAUDE.md`, `SKILL.md`,
`docs/design.md` (the evidence) and `docs/evals.md`.

## Where this session lives

The session's working folder is the **umbrella** folder that holds all the repos, so it is listed with the
manager in the app sidebar. It works **only inside `prompter/`**: edits, commits and pushes happen
in this repo. The umbrella files (`CLAUDE.md`, `README.md`, `docs/`) belong to the manager session.

## State (2026-10-07)

- **Repo:** public, `main` only, gate green (`py -3 -m unittest discover tests`, 29 tests).
- **How it's installed:**
  - Claude Code only, through a junction in `~/.claude/skills/prompter`.
  - Its hook is registered in the user's `~/.claude/settings.json` as a `UserPromptSubmit` entry
    running `py -3 ".../prompter/hooks/prompter_hook.py"`.
  - No Codex or Cursor copies: they have no `UserPromptSubmit` hook.
- **What it does:**
  - `/prompter` turns the mode on for one session, with a flag in `~/.claude/prompter/active/<id>`.
  - Every substantial message then gets `protocol.txt` attached: a brief before any tool call,
    ordered tasks with a measurable "done", no added authority, and a report that answers every
    question asked.
  - `/prompter always` sets a global default (`~/.claude/prompter/always`): every new session starts
    with the mode on; `prompter off` still wins per session. 29 tests.
  - `scripts/check_allowlist.py` checks a long run's shell commands against the permission
    allowlist.
- **Evals:** cases 1–6 pass (`docs/evals.md`).

## Open items, best first

1. **Not measured yet: does a real unattended run reach its report with no unplanned stop?** That
   is the whole point of the skill. Run one real long task with prompter on and add a row to
   `docs/evals.md` (stops, check-ins, whether the report answered everything).
2. **The brief can be noisy on short tasks.** Messages over 300 characters always get a brief. The
   substantial-message heuristic (`substantial()` in the hook) may need a look once there is real
   use data.
3. **Codex and Cursor.** If either gains a prompt-submit hook, port it. A manual variant now exists
   (`codex/AGENTS-snippet.md`, experimental, untested in Codex): get a Codex user's feedback and add
   a row to `docs/evals.md`.
4. **Hook resilience.** The hook must stay exit-0 and silent on bad input; keep the tests for that.
   Check it after Claude Code updates that change the hook input or output format.

## Gate

```bash
py -3 -m unittest discover tests
node ~/.claude/skills/readmelyzer/scripts/check-readme.mjs . --public --all-files
```

Behaviour changes to the protocol also need a pass of `docs/evals.md`.

## Releasing a change

1. Keep `SKILL.md` and `protocol.txt` consistent; `protocol.txt` is the short form the hook injects.
2. Run the gate.
3. Commit and push `main`.
4. No copies to sync. The junction makes the change live immediately, including in sessions that
   are running now.

## Boundaries

- **Never edit the user's `settings.json` without a yes.** The hook entry is the user's config.
- **Public repo:** fixtures are invented prompts with the same problem shape; never real prompts
  or logs.
- **Old commits** hold pre-anonymization text (no secrets; checked 2026-10-04). Accepted.
