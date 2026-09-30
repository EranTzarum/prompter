# prompter - evals

Run this after any change to `protocol.txt` or `SKILL.md`. Unit tests don't cover how the model behaves; this does.

## Protocol

1. Open a fresh Claude Code session in any repo, in **plan mode** so nothing changes.
2. Send `/prompter`. Expect the one-line "prompter on" reply.
3. Send each of `tests/fixtures/prompter-case-1..4.txt` as the message, without the `# source:` line. Use one session per case.
4. For case 5, run `check_allowlist.py` against `tests/fixtures/case5-*`, the way `test_check_allowlist.Case5` does.
5. Send `yes`. Expect no brief.
6. Send `prompter off`, then a long message. Expect no brief.

A case passes when all four of these hold:
- A brief appears before any work.
- The brief has ordered tasks and a measurable "done".
- The brief adds no authority the prompt didn't give.
- The turn doesn't end with a question the prompt already answered.

## Results

| Date | Commit | Case | Brief | Ordered + done | No added authority | No needless question | Notes |
|---|---|---|---|---|---|---|---|
| 2026-09-30 | 69ab714 (+ protocol fix) | all | — | — | — | — | Round 1, eval run from a scratch folder: hook injected in 4/4; briefs in 1 and 3; case 2 used a tool first; case 4 no brief (no repo) |
| 2026-09-30 | next commit | 1 | yes | yes | yes | n/a | Round 2, real repo, plan mode, max 3 turns |
| 2026-09-30 | next commit | 2 | yes | yes | yes | n/a | Brief now before any tool call ("Brief FIRST" wording) |
| 2026-09-30 | next commit | 3 | yes | yes | yes (merge only if gates pass; flags that main auto-deploys) | n/a | Uses the prompt's "go live" as deploy permission |
| 2026-09-30 | next commit | 4 | yes | yes | yes | n/a | Passed after narrowing "skip the brief" to answers that need no tool |
| 2026-09-30 | — | 5 | — | — | — | — | check_allowlist flags all 7 parts vs old settings; only inline `py -3 -c` left vs new (unit test) |

Not yet measured: whether a full run reaches the report with no unplanned stop. That needs a real unattended task with prompter on; add a row when one happens.
