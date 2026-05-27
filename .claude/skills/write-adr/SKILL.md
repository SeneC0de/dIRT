---
name: write-adr
description: Draft an architecture decision record (ADR) for this repo. Trigger when the user asks for an ADR, decision record, design writeup, or "write up the decision to X". Produces a Proposed-status ADR stored on the board (Firestore) with proposed subtasks attached.
---

# Writing an ADR

You are the **drafter head**. The workflow has already reserved an ADR number AND created its Firestore document for you. `drafter_brief.md` has:

- The user's request
- The reserved ADR number
- The reserved ADR id (Firestore document id — you post to this document via `dcli draft-adr`)
- The project id (e.g. `dweb`, `dcad`)
- A few recent ADR titles for tone

**ADRs live in Firestore, not in the git repo.** The board is the source of truth. Do NOT commit ADR files, do NOT create branches, do NOT open PRs.

## Harness pitfalls (READ BEFORE YOU TYPE BASH)

1. **No `\` line continuations.** Single line, `&&`-chained.
2. **No `"$VAR:something"`.** A double-quoted string containing `$var:` is rejected. Unquote, or inline the value.
3. **No writes to `/tmp/`.** Use `.work/` for scratch files (`mkdir -p .work` then write to `.work/...`).

Every Bash invocation is one turn. Chain with `&&` inside ONE call. Parallelize `Read`/`Write`/`Edit` in a single message.

Target: **3 turns**.

## Turn 1 — Write the ADR body and proposed subtasks

Use `Write` to create:

**`.work/adr.md`** — the full ADR body. Required structure:

```markdown
# NNNN. <Title in sentence case>

- **Status:** Proposed
- **Date:** YYYY-MM-DD

## Context

<Why this decision is needed. Reference the user's request. Cite constraints.>

## Decision

<What we are doing. One paragraph, then bullets if needed. **Name files, modules, and concrete steps explicitly** — the implementer decomposes Decision + Consequences into subtasks.>

## Options considered

<2–4 options with one-line rationale each. Chosen option goes first.>

## Consequences

<Positive, negative, and trade-offs. Be honest about costs.>
```

Keep it tight. 1–2 pages, not 5.

**`.work/subtasks.json`** — proposed subtasks for the implementation Story. JSON array:

```json
[
  {"title": "...", "description": "...", "priority": 2},
  {"title": "..."}
]
```

`description` and `priority` are optional. Aim for 2–4 subtasks that decompose the Decision into concrete executable units. These are created with `status=proposed` and `adr_id` linked — they become `open` Tasks when the ADR is approved.

You may also `Read` a relevant source file in the SAME message as the Write if the decision hinges on it — but no fishing.

## Turn 2 — Persist to Firestore via draft-adr

ONE Bash invocation. Inline the ADR id and title from `drafter_brief.md`:

```
mkdir -p .work && python C:/Users/randa/source/repos/dIRT/agent_cli.py draft-adr --adr-id <ADR_ID> --body-file .work/adr.md --title "<Title>" --proposed-subtasks .work/subtasks.json
```

This single call:
- Writes the full Markdown into the ADR document's `body` field
- Sets the title and flips status to `proposed`
- Creates each proposed subtask with `adr_id=<ADR_ID>`, `feature_id=null`, `status=proposed`
- Updates `projects_meta` last_action

The board now shows the ADR with real number + title, and subtasks appear in the Awaiting queue.

## Turn 3 — Write the result file

`Write .work/agent_result.json`:

```json
{
  "adr_number": NNNN,
  "adr_id": "<the Firestore id from the brief>",
  "adr_slug": "<short-slug>",
  "adr_title": "<Title>",
  "decision_summary": "<one sentence>",
  "proposed_subtasks_count": N
}
```

## Stop conditions

You are **done** when all of these are true:

- `.work/adr.md` exists.
- `.work/subtasks.json` exists (may be `[]` if no subtasks make sense).
- The Firestore ADR document has been updated with `body`, `title`, and `status=proposed` (confirmed by `draft-adr` success).
- `.work/agent_result.json` exists with the fields above.

Then:

- **Do not** create a branch.
- **Do not** commit any files.
- **Do not** push anything.
- **Do not** open a PR.
- **Do not** call `approve-adr` — approval is a separate step (the User approves on the board).
- **Do not** re-read the ADR you just wrote.

## When you bust the budget

If you're on turn 5+ and still not done, write a stub ADR with what you have, use `[]` for subtasks, and run `draft-adr`. A stub saved beats no ADR — the User can request edits.
