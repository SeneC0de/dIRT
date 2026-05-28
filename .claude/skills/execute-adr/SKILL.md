---
name: execute-adr
description: Implement the changes specified in an accepted ADR. Trigger when the user says "execute ADR N", "implement ADR N", "build out ADR N", or otherwise asks for the code work that an existing ADR describes.
---

# Executing an ADR

Implement a specific ADR's decision in code. ADRs live on the board (Firestore) and may target dIRT itself or any project Jones owns (dASH, dWEB, dCAD, dACE, etc.). You always launch from the dIRT repo; this skill handles `cd`'ing into the target project's repo when the ADR points elsewhere.

ADRs are *decisions*. PRs are *delivery*. This skill ends at `git push`. Opening a PR is not part of executing an ADR.

## CLI

Use dIRT's CLI explicitly — not the bare `dcli` on PATH (that resolves to the company's `director-pattern` CLI):

```
python C:/Users/randa/source/repos/dIRT/agent_cli.py <command> ...
```

## Step 1 — Resolve the ADR

Run both commands in parallel:

```
python C:/Users/randa/source/repos/dIRT/agent_cli.py get-adr <N>
python C:/Users/randa/source/repos/dIRT/agent_cli.py get-adr-body <N>
```

`get-adr` returns metadata: `number`, `title`, `status`, `project`, `feature_id`. `get-adr-body` returns the full markdown text in the `body` field.

- If `body` is null or empty, stop and tell the user — there is nothing to implement.
- If `status` is not `accepted`, ask the user whether to proceed anyway. Don't silently implement a draft or proposed ADR.

Derive a kebab-case slug from the title (e.g. `fix-receipts-400`).

## Step 2 — Resolve the target repo

If `project == "dirt"`, the target is the dIRT repo itself: `C:/Users/randa/source/repos/dIRT`.

Otherwise:

```
python C:/Users/randa/source/repos/dIRT/agent_cli.py list-projects
```

Find the entry whose `project_id == project`. Use its `repo_path`. Every subsequent command runs **inside that repo** — either `cd` once per Bash call, or use absolute paths.

## Step 3 — Prep the implementation branch

In the target repo:

```
git fetch origin && git checkout -b impl/adr-<NNNN>-<slug> origin/<default-branch>
```

Most repos use `main`. **dCAD, dACE, and dWEB use `master`.** If unsure, check first:

```
git symbolic-ref refs/remotes/origin/HEAD
```

## Step 4 — Read the ADR + scope the change

The ADR body is in the `body` field from the `get-adr-body` call in Step 1 — no scratch file needed. In a single message, fire parallel `Glob` / `Grep` / `Read` calls against the files the ADR names or implies. The goal is a clear picture of every site that needs to change before you touch any of them.

## Step 5 — Implement

Single message, parallel `Edit` / `Write` calls — one block per file. `Edit` for surgical changes; `Write` only for new files or full rewrites.

Stay inside the ADR's stated scope. No opportunistic refactoring, no surrounding cleanup, no "while I'm here" fixes. If you spot real adjacent problems, surface them in your final reply for a follow-up — don't widen the diff.

## Step 6 — Verify

Run the project's test command if one obviously applies:

- .NET: `dotnet test`
- Python: `pytest`
- Web/Node: `npm test` (consult `package.json` scripts)

If tests fail, fix the root cause. Don't skip, `xfail`, or comment out.

If the project has no clear test command, or the existing tests don't cover this change, say so out loud in the final reply rather than claiming success. For UI/frontend changes, launch the dev server and click through the change in a browser — type-checks and unit tests verify code, not features.

## Step 7 — Commit + push

```
git add <file1> <file2> ...
git commit -m "ADR <NNNN>: <one-line summary>"
git push -u origin impl/adr-<NNNN>-<slug>
```

Use **explicit file paths** in `git add` — not `-A` or `.`. The user maintains uncommitted scratch work in other paths; sweep-everything stages bring it along.

## Step 8 — Dispatch executor marker

After pushing, signal Jones that the branch is ready:

```
python C:/Users/randa/source/repos/dIRT/agent_cli.py dispatch-executor --feature-id <feature_id> --branch impl/adr-<NNNN>-<slug>
```

`feature_id` comes from the ADR doc's `feature_id` field (set during approval). This call:
- Sets `feature.status = needs-testing` and records the branch on the feature.
- Emits a `note` event: `"execute-adr branch ready: impl/adr-NNNN-<slug>"`.
- Updates `projects_meta` last_action_kind = `executor_dispatched`.

If `feature_id` is missing (ADR not yet approved), skip this step and note it in the report.

## Step 9 — Report

Tell the user, in 2–3 sentences:

- The branch name and the remote URL: `https://github.com/<owner>/<repo>/tree/impl/adr-<NNNN>-<slug>`.
- A one-line summary of what changed.
- Anything that needed a judgment call, plus any scope you deliberately deferred.

Then stop. Jones will run `dcli mark-tested --feature-id <id>` when Randall confirms tests pass.

## Out of scope for this skill

- **No PR creation.** Review/merge is a separate step the user owns.
- **No board task decomposition.** Local execution is interactive — progress is visible directly; board tasks would just add noise.
- **No `mark-adr-accepted`.** Approval happens before this skill runs.
- **No new ADRs.** If implementation reveals a needed decision, surface it in the reply and stop — don't draft.

## When the ADR doesn't fit

If the ADR's scope grows past ~4 files of changes, or you find it contradicts current code in a way that requires reinterpreting the Decision, **stop and ask** rather than reshaping it on the fly. The correct response is usually a follow-up ADR (supersedes / amends), not silent expansion.
