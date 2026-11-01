# prompter: takeover

For the session that continues prompter. Read this first, then `AGENTS.md`, `SKILL.md`,
`docs/design.md` (the evidence) and `docs/evals.md`.

Last updated: 2026-11-01 · branch `main` @ `e903019` (pushed, clean)

## Where this session lives

The session's working folder is the **umbrella** folder that holds all the repos, so it is listed with the
manager in the app sidebar. It works **only inside `umbrella/prompter/`**: edits, commits and pushes happen
in this repo. The umbrella files (`AGENTS.md`, `README.md`, `docs/`) belong to the manager session.

## State (2026-11-01)

- **Repo:** public, `main` only, gate green (`py -3 -m unittest discover tests`, 35 tests), 0 `LEAK:`.
- **Hosts:** one hook script (`hooks/prompter_hook.py`) serves every host. See `SKILL.md` ("Hosts").
  - Claude Code and Codex: `UserPromptSubmit`, attached to each substantial message.
  - Antigravity (app, IDE, `agy`): `PreInvocation` in `~/.gemini/config/hooks.json`, answering with an
    `injectSteps` `ephemeralMessage`. A `systemMessage` step did not reach the model in a probe.
    `agy` splits the command on spaces, so the hook path must have none.
  - Cursor: `sessionStart` → `additional_context`, once per chat. Its `beforeSubmitPrompt` can't add context.
  - Verified: Codex CLI (Windows + WSL), `agy`, `cursor-agent` (WSL) by probe. Eran confirmed the
    Cursor IDE and the Antigravity app (2026-11-01).
- **Install:** `scripts/install.py` finds the hosts, adds one hook entry each (never a second one,
  never overwrites a config it can't parse), copies the skill and sets the always-on flag.
  `INSTALL.md` is the agent version ("Install this skill for me: <repo link>").
- **On/off:** flags in `~/.claude/prompter/` for every host. `always` = on in every new session;
  `prompter off` = off for one session (Cursor follows `always` only).
- **Misfire fixed:** `substantial()` ignores `<system-reminder>` blocks (harness status pings were 23%
  of injections).
- **Measured (2026-10-31):** 1,884 real turns. Brief before work on 82-91% of long messages,
  turns ending in a question 8% vs 14%, interrupts 1% vs 4%. Table in `docs/evals.md` and in the README.
- **README:** hero banner (`docs/assets/hero.webp`, the "prompter SKILL" text rendered onto the
  owner's image), `how-it-works.webp`, "Measured on real work", two install options, "Works in" table.
- **Elsewhere:** the `ready` skill checks and installs prompter on all four hosts (ready `659f3a1`).
  The vault decision is "2026-10-31 prompter runs on every host through one hook".

## Where we stopped

Done and pushed. The owner is about to send a WhatsApp message to a friend who mostly uses Codex,
asking him to install prompter (README link) and answer five questions: was the brief first, did it
match his intent, did the run finish without stopping, was it noisy on small tasks, and what he would
change.

## Open items, best first

1. **Friend's Codex feedback.** When the owner relays it, add a row to `docs/evals.md` and change only
   what the feedback shows is needed.
2. **Not measured yet: does a real unattended run reach its report with no unplanned stop?** Run one
   real long task with prompter on and add a row to `docs/evals.md`.
3. **Cursor per-prompt.** If Cursor's `beforeSubmitPrompt` gains `additional_context`, move Cursor from
   `sessionStart` to it, so short replies skip the protocol there too.
4. **Hook resilience.** The hook must stay exit-0 and silent on bad input; keep the tests for that.
   Check it after host updates that change the hook input or output format.

Measured and decided not to change: the substantial-message heuristic. Short questions get the
protocol, and the agent skips the brief on about half of them, which is correct.

## Gate

```bash
py -3 -m unittest discover tests
node ../readmelyzer/scripts/check-readme.mjs . --public --all-files --no-budget
```

Behaviour changes to the protocol also need a pass of `docs/evals.md`.

## Releasing a change

1. Keep `SKILL.md` and `protocol.txt` consistent; `protocol.txt` is the short form the hook injects.
2. Run the gate.
3. Commit, then push `main` only after the owner says `push` (public repo).
4. Claude Code picks the change up at once through the junction. The Codex, Cursor and Antigravity
   skill copies need `py -3 scripts/install.py` again (it refreshes the copies; hooks stay as they are).

## Boundaries

- **Never edit a host's config without a yes.** The hook entries are the user's config.
- **Public repo:** fixtures are invented prompts with the same problem shape; never real prompts
  or logs. Check images by eye too; the leak check reads text only.
- **Old commits** hold pre-anonymization text (no secrets; checked 2026-10-04). Accepted.
