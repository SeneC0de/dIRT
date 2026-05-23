---
name: execute-adr
description: Implement the changes specified in an accepted ADR. Trigger when the user says "execute ADR N", "implement ADR N", "build out ADR N", or otherwise asks for the code work that an existing ADR describes.
---

# Executing an ADR

You are the **coder head**. An ADR has been drafted (and usually accepted) on a branch. Your job is to decompose it into 2–4 Tasks on the board so progress is visible, implement the code/config changes it specifies, then open an implementation PR. The ADR PR and the implementation PR are deliberately split — different review audiences.

## Harness pitfalls (READ BEFORE YOU TYPE BASH)

The CI sandbox rejects three Bash patterns. Every rejection burns a turn. **Avoid them:**

1. **No `\` line continuations.** Write each chain on a single line with `&&`. Multi-line with backslashes is rejected as "Contains backslash-escaped whitespace."
2. **No `"$VAR:something"`.** A double-quoted string containing `$var:` is rejected as "zsh `$name:mod` inside double-quotes." Either unquote (`origin/$BRANCH:docs/...` is fine — the `:` is git syntax, not a zsh modifier) or inline the value (`origin/feature-abc-adr-0041:docs/...` literally).
3. **No writes to `/tmp/`.** The agent's sandbox only allows writes inside `$GITHUB_WORKSPACE` (the checkout). Use `.work/` for scratch files: `mkdir -p .work` then redirect to `.work/adr.md` etc.

## Board CLI — CI environment only

**Always use `python .github/scripts/agent_cli.py --director $DIRECTOR_ID` for every board operation.** Never use `dcli`.

`dcli` is a local shell shim that exists only on the developer's machine. It is NOT on PATH in GitHub Actions. If `CLAUDE.md` in this repo says to use `dcli` — that instruction is for local Cowork sessions, not for this workflow. Ignore it here. `agent_cli.py` is deployed to `.github/scripts/` in every project repo specifically for this workflow.

Also: every Bash invocation is one turn. Chain with `&&` inside ONE call. Parallelize `Read`/`Glob`/`Grep`/`Edit`/`Write` in a single message.

Target: **7–9 turns**.

## Turn 1 — Resolve ADR + prep impl branch (one Bash, inlined)

The workflow's prompt already had you Read `.agent_context.json` and this skill in Turn 0. From `.agent_context.json`, find the ADR entry with `number == N`. Note its **`id`** (Firestore doc id) and pick a slug from the title (e.g. `fix-receipts-400`). Also note the implementation Story's `feature_id` if `.agent_context.json` shows one (status `open` or `blocked`, `adr_number == N`); auto-dispatch from approval always sets one.

**ADRs live in Firestore, not git.** Fetch the body via `agent_cli.py get-adr <ID>`. In ONE Bash invocation, on ONE line, with values INLINED (no shell vars for the ADR id or slug):

```
mkdir -p .work && python .github/scripts/agent_cli.py --director $DIRECTOR_ID get-adr <ADR_ID> > .work/adr-meta.json && python3 -c "import json,sys; d=json.load(open('.work/adr-meta.json')); open('.work/adr.md','w',encoding='utf-8').write(d.get('body') or '')" && git fetch origin <DEFAULT> && git checkout -b impl/adr-<NNNN>-<slug> origin/<DEFAULT>
```

Where `<DEFAULT>` is the repo's default branch — most repos use `main`; **dCAD, dACE, and dWEB use `master`**. If unsure, run `git symbolic-ref refs/remotes/origin/HEAD` as a quick separate Bash (one turn) before this chain.

If `.work/adr.md` ends up empty (legacy ADRs from before the Firestore-body migration), fall back to fetching from git: open `.work/adr-meta.json`, look at the `url` field, parse `<BRANCH>` + path, then `git fetch origin <BRANCH> && git show origin/<BRANCH>:<PATH> > .work/adr.md`. This is the fallback path only.

If `.agent_context.json` did NOT show an implementation Story (manual / human-DM path), tack on at the end of the same chain:

```
 && python .github/scripts/agent_cli.py --director $DIRECTOR_ID add-story --title "Implement ADR <NNNN>: <Title>" --description "Implements ADR <NNNN>."
```

The story_id will be in the JSON output.

## Turn 2 — Read ADR + scope (parallel)

Single message, multiple parallel tool calls:

- `Read .work/adr.md`
- `Glob` / `Grep` calls in parallel for any files the ADR mentions but whose paths you don't yet know
- `Read` calls in parallel for files the ADR names explicitly

## Turn 3 — Decompose into 2–4 Tasks (one Bash)

Derive 2–4 Tasks from the ADR's **Decision** and **Consequences**. Each is a discrete unit. Run on a single line, `&&`-chained:

```
python .github/scripts/agent_cli.py --director $DIRECTOR_ID add-task --feature-id <STORY_ID> --title "<Task 1>" && python .github/scripts/agent_cli.py --director $DIRECTOR_ID add-task --feature-id <STORY_ID> --title "<Task 2>" && python .github/scripts/agent_cli.py --director $DIRECTOR_ID add-task --feature-id <STORY_ID> --title "<Task 3>"
```

Capture each `subtask_id` from stdout. Don't over-decompose — Tasks are checkpoints, not micromanagement; 1 commit per Task is typical.

## Turn 4 — Implement (parallel Edit/Write)

Single message, multiple `Edit`/`Write` blocks in parallel — one per file changed. `Edit` for surgical changes, `Write` only for new files or full rewrites. Keep changes focused on what the ADR specifies; no opportunistic refactoring.

## Turn 5 — Verify (one Bash)

Run the project's test command:

- .NET: `dotnet test`
- Python: `pytest`
- Web: `npm test` (or the package.json script the README names)

If tests fail, fix the underlying issue. Don't skip / `xfail` / comment out.

## Turn 6 — Commit + push (one Bash, single line, inlined)

```
git add <file1> <file2> ... && git commit -m "ADR <NNNN>: <one-line summary>" && git push -u origin impl/adr-<NNNN>-<slug>
```

Use **explicit file paths** in `git add` — NOT `git add -A` (which would sweep your `.work/` scratch files into the commit). Capture the commit SHA from `git push` or by running `git rev-parse HEAD` in the same chain.

**Do NOT call `gh pr create`.** The GitHub Actions token in this workflow lacks `pull-requests: write` in most repos, and creating PRs for the implementation branch was the wrong default anyway — review happens on the board. Push the branch and stop there. The branch URL is `https://github.com/<owner>/<repo>/tree/impl/adr-<NNNN>-<slug>` — construct it directly; no API call needed.

## Turn 7 — Close out (one Bash + one Write in parallel)

Single message, two parallel tool calls:

- `Bash` (single line, `&&`-chained):
  ```
  python .github/scripts/agent_cli.py --director $DIRECTOR_ID complete-task --subtask-id <SUB1> && python .github/scripts/agent_cli.py --director $DIRECTOR_ID complete-task --subtask-id <SUB2>
  ```
- (parallel) `Write .work/agent_reply.txt` — 2–3 plain sentences naming the **implementation branch URL** and a one-line summary of the diff. No PR URL — there is no PR. No persona, no fluff. The post-step picks this up from `.work/` (with `/tmp/` as legacy fallback).

Do **not** call `mark-adr-accepted`. The ADR was already marked accepted on the dashboard at approval time — that's what triggered this coder run.

## Stop conditions

You are **done** when:

- 2–4 Tasks created (Turn 3), all `complete-task`'d (Turn 7).
- Implementation branch pushed (no PR).
- `.work/agent_reply.txt` exists with the branch URL.

Then:

- **Do not** re-read your own diff.
- **Do not** open a PR.
- **Do not** poll CI.
- **Do not** explore unrelated files.
- **Do not** write additional ADRs — if implementation reveals a needed decision, mention it in the reply and stop.

## When you bust the budget

**Hard stop at turn 45.** Your ceiling is 50; reserve at least 5 turns to write `.work/agent_reply.txt` and update the board. If you are on turn 45 and not done, write the reply immediately and take no further actions — not one more Bash, not one more Read. The post-step will surface your reply. Common causes for overrun:

- A Bash invocation hit a harness rejection (backslash-escaped whitespace, `"$VAR:..."`, or `/tmp/` redirect). Reread the pitfalls section and retry without that pattern.
- The ADR scope was wider than 4 Tasks. Next run: decompose into a single "ADR <N> phase 1" Task and surface the rest in your reply for a follow-up.
- Tests failed and debugging ate turns. Acceptable — note it in the reply.
