<div align="center">

<img src="docs/assets/hero.webp" alt="prompter skill: tangled ribbons of a messy request (fix sign-in, broken export, why this API?, no deploy, 2 questions) straighten into the brief: Goal, Permission, Tasks, Done, Stop only if, Report" width="100%">

**Say it messy. Get it finished.**
A mode for Claude Code, Codex, Cursor and Antigravity that turns every long, tangled message into a short plan, then works it through to the end.

[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor%20%C2%B7%20Antigravity-14B8A6)](#works-in)
[![Python](https://img.shields.io/badge/python-stdlib%20only-0F2E2B)](#install)
[![Tests](https://img.shields.io/badge/tests-35%20passing-14B8A6)](#verify)
[![Measured](https://img.shields.io/badge/measured-1%2C884%20real%20messages-0F2E2B)](#measured-on-real-work)
[![License: MIT](https://img.shields.io/badge/license-MIT-0F2E2B)](LICENSE)

</div>

---

## At a glance

| You do | prompter does | You get |
|---|---|---|
| Install once, then talk like you always do | Before the agent acts, it writes a 3-6 line **brief**: goal, permission, ordered tasks, what "done" means, when to stop | Work that runs to the end, and a report that answers **every question** you asked |

<p align="center">
  <img src="docs/assets/how-it-works.webp" alt="Messy request, clear brief, finished work: a request with two side questions becomes a brief (goal, permission, tasks, done, stop only if, report), then work and a report that answers both questions with no deploy" width="980">
</p>

---

## Why

Messages written in a hurry confuse a coding agent. You paste logs, mix in three questions, and add "if it all checks out, merge it". The agent does part of the work, then stops to ask *"want me to…?"*, or misses one of your questions. You type "yes", and it happens again.

The fix isn't a better prompt you have to remember to write. prompter rewrites the message for the agent, every time, before it acts.

A scan of a few hundred real agent sessions found the same few causes behind most of these stops:

| Why the agent stopped | What prompter changes |
|---|---|
| The message ended in a question, so the agent answered it and handed the decision back | The brief states what you allowed and what "done" means |
| Permission was conditional ("if everything checks out…") and nothing was measurable | "Merge only if the full test suite passes" |
| Several goals were mixed into one long paste with no order | An ordered, bounded task list |
| A side question got lost in a long message with logs | The report answers every question, one line each |
| Shell commands were blocked by the permission check until the turn ended | Before a long run, it checks the commands are allowlisted and asks you once |

---

## Measured on real work

prompter was checked against a month of real use: **1,884 messages** sent with it on, in 71 sessions, compared with 530 long messages sent without it.

| | With prompter | Without |
|---|---|---|
| Wrote a brief before starting work (messages of 300+ characters) | **82-91%** | 0-1% |
| Ended a turn by asking the user something | **8%** | 14% |
| Turns the user had to interrupt | **1%** | 4% |
| "You didn't answer my question" in the next message (prompts with 2+ questions) | **2.4%** | 5.9% |

What that means in practice:
- The agent states the goal, the limits and what "done" means before it touches anything.
- It stops to ask about half as often, and most of the questions left are real decisions only you can make.
- Side questions buried in a long message get answered.

> [!NOTE]
> This compares before and after on one developer's sessions, not a controlled trial. Models and habits changed in the same weeks. Briefs and questions were counted by a script. The method and every number are in [docs/evals.md](docs/evals.md).

---

## What it does

- 🎚️ **On everywhere, off when you want.** After install it's on in every new session, in every tool. `prompter off` turns it off for one session; `/prompter always off` turns the default off.
- 🧹 **Only when it helps.** Long messages, pastes and questions get a brief. `yes`, `go` and `continue` don't.
- 📝 **Shows the plan, doesn't wait.** The brief comes first, then work starts in the same turn.
- ✅ **Nothing dropped.** Your original message stays the source. The final report closes every question and item in it.
- 🛡️ **Never adds permission.** Push, merge, delete and deploy happen only if you said so.
- 🔑 **No surprise stalls.** `scripts/check_allowlist.py` finds the shell commands a long run needs that your settings don't allow yet. It proposes narrow rules and never writes them itself.

---

## Install

Pick one.

**Option 1: ask your AI agent.** Paste this into Claude Code, Codex, Cursor or Antigravity:

```text
Install this skill for me: https://github.com/EranTzarum/prompter
```

The agent follows [INSTALL.md](INSTALL.md). It asks you once before it touches any config.

**Option 2: two commands.**

```bash
git clone https://github.com/EranTzarum/prompter.git ~/.claude/skills/prompter
python3 ~/.claude/skills/prompter/scripts/install.py
```

On Windows, use `py -3` instead of `python3`.

Either way, the installer finds every AI tool on your machine and sets up each one:
- It adds one hook entry and copies the skill next to that tool's other skills.
- It turns prompter on for every new session.
- It keeps your other settings and never adds a second entry, so running it again is safe.

Then restart any AI app that is open. In Codex, trust the new hook once with `/hooks`.

### Works in

| Tool | Hook | When the rules arrive |
|---|---|---|
| Claude Code | `UserPromptSubmit` | with each long message |
| Codex | `UserPromptSubmit` | with each long message |
| Antigravity (app, IDE, CLI) | `PreInvocation` | with each long message |
| Cursor (IDE, CLI) | `sessionStart` | once, at the start of each chat |

Cursor's per-message hook can't add context yet, so there the rules arrive once and cover the whole chat.

---

## Try it

You send this (a typical end-of-day message):

```text
done with step 1. logs below:
  ERROR web bundling failed: cannot resolve ./worker.wasm
  WARN  no route named "(auth)" in layout
if everything checks out and tests pass, merge it.
also - why do I need a maps API key? and where is the "refresh log" button?
```

Claude answers with a brief, then starts working:

```text
Goal:         fix the web bundle error and the route warning, merge, answer 2 questions
Permission:   merge to main only if the full test suite passes; no deploy
Tasks:        1. fix bundle  2. fix route  3. run tests  4. merge  5. answer questions
Done:         suite green, merge commit on main
Stop only if: a failing test I can't explain
Report:       what changed, test result, merge commit, one line per question
```

The final report ends with one line for the API key and one for the refresh button. Nothing you asked gets skipped.

### Before a long run

<p align="center">
  <img src="docs/assets/terminal.svg" alt="check_allowlist lists seven commands that would have been blocked and the narrow rule for each" width="860">
</p>

```bash
python3 scripts/check_allowlist.py --commands run-commands.txt
```

---

## How it works

```mermaid
sequenceDiagram
    participant You
    participant Hook as prompter_hook.py
    participant Claude
    You->>Hook: your message (unchanged)
    Hook->>Hook: on for this session? long enough?
    Hook-->>Claude: + the protocol, as extra context
    Claude-->>You: brief
    Claude->>Claude: work through the tasks
    Claude-->>You: report: every question answered
```

1. **A hook adds, never edits.** Your AI tool runs the hook before the model reads your message. The hook attaches the rules next to your text; your text arrives untouched.
2. **Two kinds of stop, two fixes.** The brief handles stops caused by how a message is written. The allowlist check handles stops caused by permissions.
3. **One question at most, up front.** Gaps get filled from the repo first. Anything only you can decide is asked once, before work starts.

| Part | Takes | Produces |
|---|---|---|
| `hooks/prompter_hook.py` | your message and session id | the protocol as extra context, or nothing |
| `protocol.txt` | — | the 7 rules Claude follows |
| `SKILL.md` | `/prompter` | the full rules, with an example |
| `scripts/check_allowlist.py` | a command list + your settings | what's blocked, and narrow rules to allow it |
| `scripts/install.py` | the AI tools it finds on your machine | one hook entry and a skill copy in each |

---

## Verify

```bash
python3 -m unittest discover tests
```

The tests prove the on/off switch, that sessions stay separate, that short replies pass through, and that bad input never blocks a prompt. They also prove the allowlist check catches compound commands and refuses risky ones.

> [!NOTE]
> Unit tests can't judge what Claude writes. [docs/evals.md](docs/evals.md) has the model-level checks: headless runs on anonymized real prompts.

---

## Extend

- **Change what counts as "long enough":** `substantial()` in `hooks/prompter_hook.py`, plus `tests/test_hook.py`.
- **Change the rules:** edit `protocol.txt` and `SKILL.md` together, then rerun [docs/evals.md](docs/evals.md).
- **Add a risky-command pattern:** `DESTRUCTIVE` in `scripts/check_allowlist.py`, plus `tests/test_check_allowlist.py`.

---

## FAQ

<details><summary><b>Does it change what I wrote?</b></summary>

No. Your message reaches Claude exactly as typed. The hook only adds context next to it.
</details>

<details><summary><b>Does Claude still read my logs and pasted text, or only the brief?</b></summary>

All of it. The brief is Claude's own summary; your full message stays the source for the final report.
</details>

<details><summary><b>Can it push, merge or deploy on its own?</b></summary>

No. The brief never adds permission you didn't give, and the allowlist check only proposes rules.
</details>

<details><summary><b>Will it slow down quick replies?</b></summary>

No. Short replies pass straight through.
</details>

<details><summary><b>What if I forget to register the hook?</b></summary>

The skill tells Claude to follow the rules on its own for the session and to tell you the hook is missing.
</details>

<details><summary><b>Does it work in Codex, Cursor or Antigravity?</b></summary>

Yes. One installer sets up all four with the same hook script; see [Works in](#works-in).
</details>

---

## License

[MIT](LICENSE) © 2026 Eran Tzarum

<div align="center"><sub>For agents that should finish what they start.</sub></div>
