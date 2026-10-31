# prompter - evals

Run this after any change to `protocol.txt` or `SKILL.md`. Unit tests don't cover how the model behaves; this does.

## Protocol

1. Open a fresh Claude Code session in any repo, in **plan mode** so nothing changes.
2. Send `/prompter`. Expect the one-line "prompter on" reply.
3. Send each of `tests/fixtures/prompter-case-1..4.txt` and `prompter-case-6.txt` as the message, without the `# source:` line. Use one session per case.
4. For case 5, run `check_allowlist.py` against `tests/fixtures/case5-*`, the way `test_check_allowlist.Case5` does.
5. Send `yes`. Expect no brief.
6. Send `prompter off`, then a long message. Expect no brief.

A case passes when all four of these hold:
- A brief appears before any work.
- The brief has ordered tasks and a measurable "done".
- The brief adds no authority the prompt didn't give.
- The turn doesn't end with a question the prompt already answered.
- (case 6) The report answers every question in the original message and ticks off every item.

## Results

| Date | Commit | Case | Brief | Ordered + done | No added authority | No needless question | Notes |
|---|---|---|---|---|---|---|---|
| 2026-09-30 | 69ab714 (+ protocol fix) | all | — | — | — | — | Round 1, eval run from a scratch folder: hook injected in 4/4; briefs in 1 and 3; case 2 used a tool first; case 4 no brief (no repo) |
| 2026-09-30 | 252ed36 | 1 | yes | yes | yes | n/a | Round 2, real repo, plan mode, max 3 turns |
| 2026-09-30 | 252ed36 | 2 | yes | yes | yes | n/a | Brief now before any tool call ("Brief FIRST" wording) |
| 2026-09-30 | 252ed36 | 3 | yes | yes | yes (merge only if gates pass; flags that main auto-deploys) | n/a | Uses the prompt's "go live" as deploy permission |
| 2026-09-30 | 252ed36 | 4 | yes | yes | yes | n/a | Passed after narrowing "skip the brief" to answers that need no tool |
| 2026-09-30 | — | 5 | — | — | — | — | check_allowlist flags all 7 parts vs old settings; only inline `py -3 -c` left vs new (unit test) |

| 2026-10-04 | 6317b8d | 6 | yes | yes | yes | yes | Mobile-app message, 4.8k chars with terminal logs + 4 questions; real repo, plan mode, 30 turns. Brief lists "where is Refresh log"; report answers all of them (spike link, Refresh log, wasm error, secrets, Google API, logos). Added after rule 7 |

## Real use (2026-10-31)

Scripted pass over one owner's Claude Code transcripts: 1,884 turns where the hook attached the protocol (71 sessions, 2026-09-29 to 2026-10-31), against 530 substantial messages without it (most from before 2026-09-29). This compares before and after, not a controlled trial: the model and the owner's habits changed over the same weeks. Briefs and questions are detected by keywords, so treat the numbers as directions.

| Measure | With prompter | Without | Note |
|---|---|---|---|
| Brief before the first tool call, message ≥ 300 chars | 82-91% | 0-1% | Stable through October. Misses are mostly post-compact resumes and messages that already were a brief |
| Brief before the first tool call, message < 300 chars | 45% | 0% | Short questions; skipping the brief there is fine |
| Turn ends with a question to the user | 8% | 14% | Most remaining ones are real decisions (A/B, wording, price) |
| Unneeded check-in answered with a bare "yes"/"go" | 1.5% of turns | 0.4% | Rare either way |
| User interrupted the turn | 1% | 4% | |
| Next message says a question was missed (prompts with 2+ "?") | 2.4% (4/167) | 5.9% (3/51) | Small samples |
| Tool calls per turn (median) | 11 | 14 | Runs are not longer; they stop less to ask |

Misfire found and fixed: 23% of injections were on harness status pings (`<system-reminder>` blocks such as "Linked sessions now" or "session finished"), and the agent wrote a brief on 110 of the 207 pure pings. `substantial()` now ignores `<system-reminder>` blocks and judges only the user's own text.

Not yet measured: whether a full run reaches the report with no unplanned stop. That needs a real unattended task with prompter on; add a row when one happens.
