---
name: prompter
description: Session mode that rebuilds each substantial user message into a short goal-oriented brief (goal, permission, ordered tasks, measurable done, stop conditions, report format) before Claude acts, so long runs finish without early check-ins; also checks that the shell commands a long run needs are allowlisted. Use when the user types /prompter, says "prompter on", "turn on prompter", or asks to stop stopping early / work more goal-oriented for the whole session. "/prompter off" or "prompter off" turns it off.
---

# prompter

Turn on once per session with `/prompter`. From then on a UserPromptSubmit hook
(`hooks/prompter_hook.py`) attaches `protocol.txt` to every **substantial** message
(≥ 300 chars, ≥ 5 lines, or a question). Short replies such as "yes", "go" and
"continue" pass through untouched. `prompter off` turns it off for this session only.

## On activation

- `/prompter` → reply with one line: "prompter on - substantial messages get a brief first. `prompter off` to stop."
- `/prompter off` → reply "prompter off."
- If the hook is not registered (no `PROMPTER ACTIVE` context shows up on the next long
  message), apply the protocol below yourself for the rest of the session and say once
  that the hook is missing (see README, "Install").

## The protocol

Why: in real transcripts, agents stopped early when the prompt ended in a question,
gave permission only conditionally ("if everything checks out, I would like us to…"),
mixed several goals, or had no measurable "done". A second cause was the auto-mode
safety check denying shell commands until the turn ended. Evidence: `docs/design.md`.

### 1. Brief first

The brief is your **first output, before any tool call**, even when context is missing
(put the gap in the brief: "Tasks: 1. find the repo…"). Show 3-6 lines, then start working
in the same turn. Do not wait for approval. Reading files to fill gaps comes after the brief.

```text
Goal: <one line>
Permission: <only what the user said + CLAUDE.md; e.g. "commit and push to feat/x; no merge">
Tasks: 1. … 2. … 3. …   (ordered, each one bounded)
Done: <measurable per task: failing test passes, full suite green, file exists, command output>
Stop only if: <named conditions, e.g. unexplained test failure, a fix would weaken an invariant>
Report: <what the final message lists>
```

### 2. Fill gaps from files, not from the user

Read CLAUDE.md, the issue, the project notes, or the code before asking. Ask only what only
the user can answer (a business choice, a credential, authority not given), in **one**
batched question **before** starting, and only when it blocks. Otherwise pick the safe
default and state it in the brief ("assuming: separate branch, no push").

### 3. Never add authority

The brief restructures what the user said; it never widens it. Push, merge, delete,
deploy, settings changes, messages to others: only when the user's words allow it.
Conditional permission stays conditional but becomes testable:
"if everything checks out, merge" → "merge to main only if the full suite passes and the
build is green; otherwise stop and report".

### 4. Pasted text with no instruction

State the most likely intent in the brief ("reading this as: verify the report's root
cause, then fix it"), do the read-only part, and ask only before anything irreversible.

### 5. Long run: check permissions before starting

When the run has 3+ tasks or will need many shell commands:

1. List the exact commands it will run into a scratch file, one per line
   (`PowerShell: <cmd>` for PowerShell).
2. Run `py -3 "<this skill dir>/scripts/check_allowlist.py" --commands <file>` from the repo root.
3. Put any missing rules it proposes into the same up-front question. Never edit
   `settings.json` without a yes. Commands it refuses to propose (destructive, inline
   `-c` code) stay as prompts; write inline code to a script file instead.
4. Prefer simple single commands over pipes and `cd … &&` chains: every part of a
   compound command must be allowed on its own.

### 6. Execute to the end

No mid-run check-ins other than the named stop conditions. End with the report format
from the brief.

### 7. Close every item from the original message

The brief is a summary and can drop small items; the user's message stays the source
(logs, pasted text, side questions). Before the report, re-read the original message.
The report:

- answers **every** question in it, one line each ("Why Google API? …", "Refresh log - where? …");
- ticks off every item or step it mentions: done, or not done and why.

Nothing is silently dropped. Real miss that led to this rule: a mobile-app message with
terminal logs and four questions, where "Refresh log - where?" had no task in the
brief (`tests/fixtures/prompter-case-6.txt`).

### Skip the brief

Only a question you can answer without any tool call, or a message the hook did not flag.
If you will run a tool or change anything, the brief comes first.

## Example

Input (real, shortened): "I did all the steps. If we finish with this part of the plan,
and we can go live, and everything checks out, and all the tests pass, and we can safely
merge everything into main, I would like us to do it."

```text
Goal: finish plan part N and merge to main.
Permission: merge to main, only if the checks below pass. No deploy.
Tasks: 1. finish remaining plan items 2. run full test suite + build 3. merge to main
Done: suite green, build green, main contains the branch
Stop only if: a test fails that I can't explain, or merge conflicts touch business logic
Report: what was finished, test/build result, merge commit
```
