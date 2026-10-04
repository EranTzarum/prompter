# prompter - design

## Problem

Agents stop early and wait for a nudge. There are two kinds of stop:

- **A. The prompt's shape.** The prompt ends in a question, gives permission only conditionally, mixes several goals, has no measurable "done", or leaves the scope unclear. The agent answers and hands the decision back.
- **B. The harness.** The Claude Code auto-mode safety check denies shell commands ("classifier gave no verdict"). After enough denials the turn ends, however good the prompt is.

The positive case: a short structured prompt with permission up front, an ordered queue, a test per task, and two named stop conditions ran for hours (workflowai-factory issues #1, #6 and #2, 2026-09-29). Vault note: `Knowledge/Claude Code/Prompts that run long without stopping.md`.

## Evidence (transcript scan, 2026-09-30)

The scan covered 444 Windows transcripts (294 of them Codex) and 24 WSL transcripts. It found 48 task prompts that were followed by a nudge:

| Cause | Count | Notes |
|---|---|---|
| C. Usage limit | 18 | "You've hit your session limit". Out of scope: no prompt fixes it. |
| Correct stop | ~10 | The prompt itself said to stop ("wait", "don't change code"). |
| A. Prompt shape | 4 best cases | `tests/fixtures/prompter-case-1..4.txt` |
| B. Harness | 1 main case, plus stats | `prompter-case-5.txt` |
| D. Brief drops an item | 1 (after launch) | `prompter-case-6.txt` |

**Cases**
- **Case 1** (workflowai-factory, 2026-08-23): the prompt ends in "tell me which is right". There is no permission to implement.
- **Case 2** (workflowai-factory, 2026-09-22): several questions are mixed into a long pasted report, with no order and no scope.
- **Case 3** (real-estate CRM, 2026-09-23): the permission is conditional ("if everything checks out … I would like us to"), and "checks out" is not measurable.
- **Case 4** (Resume Automation, 2026-08-23): the prompt ends in a question and never says "run it".
- **Case 5** (workflowai-factory, 2026-09-29): the model-catalogue run, after "Go". Five commands in a row got "no verdict" and the turn ended. All the denied commands were compound: `codex debug models | py -3 -c "…"`, and `cd … && git status`.
- **Case 6** (BroFix, 2026-10, prompter on): a 4.8k-char message with terminal logs and four questions. Claude received the whole message (checked in the transcript), but the brief had no task for "Refresh log - where?". Since a brief is a summary, items can fall out.

**Harness statistics**
- Denials: 58 by the safety check, 20 "no verdict", 22 by Codex policy.
- 15 streaks of 2 or more denials, and 9 main-session turns that ended right after a denial.
- Top command prefixes: `py -3`, `git clone`, `codex debug`.

## Decisions

- **In-session hook, not a copy-paste rewriter** (Eran, 2026-09-30). The first proposal returned a rewritten prompt to paste back, and it was rejected. Eran lives in one chat. A `UserPromptSubmit` hook attaches the protocol as `additionalContext` before Claude reads the message. A hook cannot replace the message text, so Claude rebuilds it as a visible brief.
- **Show the brief, then go.** The brief takes 3-6 lines and costs little. It lets Eran catch a misread early without adding a stop.
- **Per-session flag.** `/prompter` writes `~/.claude/prompter/active/<session_id>`. Caveman keeps one global flag; this one is per session, so other sessions stay untouched.
- **Only substantial messages.** A heuristic (≥ 300 chars, ≥ 5 lines, or a question) keeps "yes / go / continue" untouched. It is a heuristic by design; replace it only if it misfires in real use.
- **Never add authority.** The brief restructures what was said and never widens it. A conditional permission becomes a testable condition.
- **Allowlist check is advisory.** `check_allowlist.py` reads settings and proposes rules. It never writes them. It refuses to propose rules for destructive commands or inline interpreter code (`py -c`, `node -e`), and it splits compound commands because every part must be allowed.
- **The original message stays the source** (2026-10-04, after case 6). The hook never changes or cuts the user's text; Claude sees all of it plus the protocol. Rule 7: before the report, re-read the original message, answer every question in it one line each, and tick off every item. Chosen over a longer brief because the brief has to stay 3-6 lines.
- **`protocol.txt` is the only copy of the injected text.** `SKILL.md` expands on it.

## Out of scope (v1)

- Codex, Cursor and WSL.
- Usage-limit stops.
- Automatic edits to settings.
- Rebuilding short replies.
