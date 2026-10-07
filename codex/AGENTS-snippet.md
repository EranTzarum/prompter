## prompter (manual variant)

Paste this block into `~/.codex/AGENTS.md` (all projects) or a repo's `AGENTS.md`.
There is no hook in Codex, so the rule below is how it triggers: by your judgment of
the message, not by code.

---

### Brief first, then work to the end

Applies to a **substantial** message: 300+ characters, 5+ lines, or one that ends in a
question. Short replies ("yes", "go", "continue") skip this. If the user says
"prompter off", stop applying it for the rest of the session.

1. **Brief FIRST.** Your first output, before any tool call, even if a gap blocks you
   (name the gap in it). 3-6 lines:
   `Goal / Permission / Tasks (ordered, bounded) / Done (measurable per task) / Stop only if / Report`.
   Permission is only what the user said plus AGENTS.md. Then start working in the same
   turn; do not wait for approval.
2. **Fill gaps from files** (AGENTS.md, issues, project notes), not from the user. Ask
   only what only the user can answer, in ONE batched question up front, and only if it
   blocks. Otherwise pick a safe default and state it in the brief.
3. **Never add authority.** Push, merge, delete, deploy, settings changes: only if the
   user said so. Conditional permission stays conditional, with a measurable test
   ("merge only if the full suite and build pass; otherwise stop and report").
4. **Pasted text with no instruction:** state the likely intent in the brief, do the
   read-only part, ask only before anything irreversible.
5. **Long run** (3+ tasks or many shell commands): prefer simple single commands over
   pipes and `cd ... &&` chains, so each command can be approved on its own.
6. **Execute to the end.** No check-ins except the named stop conditions.
7. **Close every item.** The brief is a summary; the user's message stays the source.
   Before the report, re-read it. The report answers EVERY question in it, one line
   each, and ticks off every item or step it mentions (done / not done + why).

Skip the brief only for a question you can answer without any tool call.
