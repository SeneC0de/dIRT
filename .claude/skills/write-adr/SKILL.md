---
name: write-adr
description: Draft an architecture decision record (ADR) for this repo. Trigger when the user asks for an ADR, decision record, design writeup, or "write up the decision to X". Produces a Proposed-status ADR stored on the board (Firestore).
---

# Writing an ADR

You are the **drafter head**. The workflow has already reserved an ADR number AND created its Firestore document for you. `drafter_brief.md` has:

- The user's request
- The reserved ADR number
- The reserved ADR id (Firestore document id — you patch this document with the body)
- The project's director description and a few recent ADR titles for tone

**ADRs live in Firestore, not in the git repo.** The board is the source of truth. Do NOT commit ADR files, do NOT create branches, do NOT open PRs. The agent that implements the ADR (`execute-adr`) reads the body from Firestore.

## Harness pitfalls (READ BEFORE YOU TYPE BASH)

1. **No `\` line continuations.** Single line, `&&`-chained.
2. **No `"$VAR:something"`.** A double-quoted string containing `$var:` is rejected as "zsh `$name:mod` inside double-quotes." Unquote, or inline the value.
3. **No writes to `/tmp/`.** Use `.work/` for scratch files (`mkdir -p .work` then write to `.work/...`).

Every Bash invocation is one turn. Chain with `&&` inside ONE call. Parallelize `Read`/`Write`/`Edit` in a single message.

Target: **3 turns**.

## Turn 1 — Write the ADR

The workflow's prompt already had you Read `drafter_brief.md` and this skill in Turn 0. You have everything you need. Use `Write` to create `.work/adr.md` with the body.

Required structure:

```markdown
# NNNN. <Title in sentence case>

- **Status:** Proposed
- **Date:** YYYY-MM-DD

## Context

<Why this decision is needed. Reference the user's request. Cite constraints.>

## Decision

<What we are doing. One paragraph, then bullets if needed. **Name files, modules, and concrete steps explicitly when you can** — the coder that implements this will decompose Decision + Consequences into 2–4 Tasks, and a vague Decision forces them to guess.>

## Options considered

<2–4 options with one-line rationale each. The chosen option goes first.>

## Consequences

<Positive, negative, and trade-offs. Be honest about costs.>
```

Keep it tight. 1–2 pages, not 5.

You may also `Read` a relevant source file in the SAME message as the Write if the decision hinges on it — but no fishing. ADRs are decision documents, not code reviews.

## Turn 2 — Persist to Firestore

ONE Bash invocation. Inline the ADR id (from `drafter_brief.md`) and title — no shell vars for the title because it may contain spaces.

```
mkdir -p .work && python .github/scripts/agent_cli.py --director $DIRECTOR_ID update-adr <ADR_ID> --body-file .work/adr.md --title "<Title>" --status proposed
```

That single call writes the full Markdown into the ADR document's `body` field, sets the title, and flips the status to `proposed`. The board now shows the ADR.

## Turn 3 — Write the result file

`Write .work/agent_result.json`:

```json
{
  "adr_number": NNNN,
  "adr_id": "<the Firestore id from the brief>",
  "adr_slug": "<short-slug>",
  "adr_title": "<Title>",
  "decision_summary": "<one sentence>"
}
```

The post-step uses this to create the implementation Story on the board.

## Stop conditions

You are **done** when all of these are true:

- `.work/adr.md` exists.
- The Firestore ADR document has been updated with `body`, `title`, and `status=proposed`.
- `.work/agent_result.json` exists with the fields above.

Then:

- **Do not** create a branch.
- **Do not** commit any files.
- **Do not** push anything.
- **Do not** open a PR.
- **Do not** call `mark-adr-accepted` — approval is a separate step (the User approves on the board).
- **Do not** re-read the ADR you just wrote.

## When you bust the budget

If you're on turn 5+ and still not done, write a stub ADR with what you have and persist it. The worst ADR with a `body` saved beats no ADR at all — the User can request edits and the next iteration is cheap.
