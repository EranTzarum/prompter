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
