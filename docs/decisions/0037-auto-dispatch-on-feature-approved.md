# ADR 0037 — Auto-dispatch on `feature_approved`

- **Status:** Proposed
- **Date:** 2026-05-22
- **Author:** Head (drafter, dASH)
- **Director:** dASH
- **Feature:** Draft ADR 0037: Auto-dispatch on `feature_approved` (`uO8TyaFOqTNsFiveVUje`)
- **Subtask:** `a1hU6f4ZK291CBa6JcvV`
- **Agent:** `F3tIASfmKdrImraO054M`
- **Related:** `agents/director.md` (ADR-workflow Step 4 → Step 5, Hard rule #10); `functions/main.py` (`on_message_created`) — **now lives in the `dASH` repo (`C:\Users\randa\source\repos\dASH\functions\main.py`) after the 2026-05-23 split**; `dcli approve-feature` (`agent_cli.py`).

> **File-path note (added 2026-05-23 by Jones / dIRT):** When this ADR was written, `functions/main.py` lived in the same repo as the doctrine. After the dIRT / dASH split, the Cloud Functions implementation moved to `dapp-controls/dASH` while this ADR (system-level — describes the auto-dispatch *design*) stayed in dIRT. Every reference to `functions/main.py` below resolves inside the dASH repo now. The design described is unchanged.

---

## Major Findings (Director TL;DR)

- **Recommendation:** New `on_feature_approved` Cloud Function — second trigger in `functions/main.py` that fires on `events/` writes where `type == feature_approved` and synthesizes the same `workflow_dispatch` `on_message_created` already issues. Approval click → Director wake-up, no human in the middle.
- **Idempotency** = CAS on `features/{id}.dispatched_at`. **Opt-out** = `features/{id}.auto_execute = false`. Both are single-field additions to the existing doc; no schema migration.
- **Doctrine update ships with v1:** `agents/director.md` Step 5 + Hard rule #10 must say "check `dispatched_at` before decomposing" so the auto-dispatch and a waking human Director never both write Tasks against the same approved feature.
- **Two follow-ups deferred** (named explicitly so they don't get lost): Option 2 (split decompose-from-execute) and Option 3 (hourly janitor backstop) are additive on top of this ADR — build them after v1 produces real failure-mode data, not on speculation.

---

## Context

A `feature_approved` event is emitted whenever the User clicks the green Approve button on a feature card, or whenever `dcli approve-feature --feature-id <id>` is run. The event flips the feature's `status` from `blocked` → `open`, broadcasts a cross-ref to every other Director (per `agent_cli.py` `cmd_approve_feature`), and marks the ADR review loop closed. Per `agents/director.md` Step 5, the feature is then "yours to decompose and execute."

In practice, **nothing acts on the event itself.** Decomposition and execution depend on the approving Director being awake — sitting in a Claude Code session, watching the board, ready to read the event, write 2–4 Tasks with `dcli add-subtask`, register a Head, claim, and dispatch via the Agent / Task tool. When the Director is asleep — outside a session, between conversations, overnight, or simply not the recipient of a chat that would have woken them — the feature sits in `status=open` indefinitely. The audit trail records that the User approved the ADR; the work does not start.

Today the only Cloud Function that bridges Firestore to GitHub Actions is `on_message_created` in `functions/main.py`. It triggers on `messages/{messageId}` create, validates that the message is a `user_director` thread with a human sender, posts an "On it." acknowledgement, resolves the target Director's `github_repo` and `default_branch`, then issues a `workflow_dispatch` against `director-agent.yml` with the user's intent. That same dispatch shape is what wakes a Director on Randall or Matt sending a DM. Once dispatched, the GitHub Actions run is where all reasoning and code work happens.

The asymmetry is the problem. **A chat message** to a Director triggers an automatic wake-up via a Cloud Function. **An ADR approval** — arguably the higher-signal event, because the User has read and ratified a Decision — does not. Randall and Matt have to DM the Director afterward ("dASH, you've got an approved ADR, decompose it") to produce the same effect. That message is mechanical, predictable, and forgettable. ADR-blocked Stories stall until someone notices and types the prompt.

Three forces shape the decision:

- **The Cloud Function substrate already exists** — adding a second trigger costs one function and reuses the `workflow_dispatch` shape `on_message_created` already proved out.
- **The approval signal is unambiguous** — `feature_approved` is emitted exactly once per feature (gated by `status=blocked` precondition in `cmd_approve_feature`), so the trigger has a clean idempotency anchor.
- **The User's "human Director" doesn't disappear** — Randall or Matt may still want to nudge a Director manually after approval, or skip auto-dispatch entirely on a sensitive feature. The mechanism must accommodate both without surprising anyone.

---

## Decision

**Add a second Cloud Function trigger** in `functions/main.py` that fires on Firestore `events/{eventId}` document create where `type == "feature_approved"`, and **synthesizes the same `workflow_dispatch`** the existing `on_message_created` handler builds — targeting `director-agent.yml` on the approving Director's `github_repo` at its `default_branch`, with an `intent` payload phrased as the approved ADR's decomposition prompt.

Three properties are non-negotiable:

1. **Idempotency via compare-and-set on `features/{id}.dispatched_at`.** Before issuing the dispatch, the function reads the feature doc, verifies `dispatched_at` is unset (or older than a configured cool-off, e.g. 24h), and writes `dispatched_at = serverTimestamp()` in the same transaction it uses to decide. If the CAS fails — another invocation got there first, or the field is already set — the function returns early with a log line and emits no dispatch. This is the same shape Firestore transactions already give us; no new primitives. The `feature_approved` event itself remains the audit anchor; `dispatched_at` is the action anchor.

2. **Opt-out via `features/{id}.auto_execute = false`.** A Director or the User can pre-set this flag on a feature before approving it; the Cloud Function reads it and skips dispatch when false. The flag defaults to unset (treated as `true`), so existing features inherit the new behavior automatically. The dashboard can surface this as a per-feature toggle later; for v1 it's a CLI/Firestore-write affordance. This gives the User an escape valve for features that need human-paced decomposition — e.g., a sensitive policy change, or a feature the User wants to walk through with the Director live.

3. **The dispatched intent is decomposition, not execution.** The Cloud Function does not start coding; it wakes the Director to do Step 5 (decompose into Tasks, then dispatch execution Heads). The `workflow_dispatch` payload's `intent` field is a fixed template — something like `"ADR <NNNN> approved by <approver>. Decompose feature <feature_id> into 2–4 Tasks and dispatch execution Heads per agents/director.md Step 5."` — not a free-form prompt. The Director picks up that intent the same way it picks up a user message, runs its startup ritual, and proceeds. Reasoning stays in the Director session; the Cloud Function is plumbing, not logic.

The function reuses `_db()`, `_get_director()`, and `_gh_headers()` from the existing module, and the dispatch block (resolve `github_repo`, fetch `default_branch`, POST to `actions/workflows/director-agent.yml/dispatches`) is structurally identical. The only divergences from `on_message_created`: the trigger source is `events/{eventId}` instead of `messages/{messageId}`; the validation gate is `type == "feature_approved"` instead of `thread_type == "user_director"`; the lookup chain is `event.feature_id → features/{id} → director_id → directors/{id}`; and there is no "On it." reply (no chat thread to post into — the audit log already records the approval, and the resulting dispatch will surface in the Director's next session).

---

## Options considered

### Option 1 — Auto-dispatch Cloud Function on `feature_approved` (**recommended**)

A second `@functions_framework.cloud_event` handler in `functions/main.py` triggered by Firestore document-create on `events/{eventId}`, gated on `type == "feature_approved"`, that synthesizes a `workflow_dispatch` against the approving Director's `director-agent.yml`. Idempotency via CAS on `features/{id}.dispatched_at`; opt-out via `features/{id}.auto_execute = false`.

**Why this:**
- Reuses the exact substrate `on_message_created` already proved in production — same headers, same workflow, same default-branch resolution, same failure modes. Zero new infrastructure to operate.
- The trigger fires within seconds of the User's button-press. End-to-end latency from approval to "Director is awake and decomposing" goes from "whenever Randall remembers to DM" to "as long as a GitHub Actions cold start." The User's mental model — "I approved the ADR, the work starts" — is honored mechanically.
- Idempotency is local to the function (CAS on a single doc field) and uses a Firestore primitive the codebase already leans on. No external lock, no message queue.
- Opt-out is a single field. The User retains full manual control on features that warrant it, with no new ceremony — set the flag before clicking Approve.

**Costs:**
- One new Cloud Function to deploy, monitor, and version. Operationally trivial; conceptually a second moving piece in a pipeline that previously had one.
- The doctrine in `agents/director.md` Step 5 now has two paths to "Director is decomposing" — the auto-dispatch path (default) and the manual nudge path (when `auto_execute=false`, or when the Cloud Function fails). Both must coexist cleanly. See Consequences for the rule update that makes that coexistence explicit.
- A race exists between the auto-dispatched workflow run and a human Director who happens to be awake when the approval lands. Both could try to decompose the same feature simultaneously. The CAS on `dispatched_at` prevents *duplicate dispatches*, but doesn't prevent a parallel-running Director session from also writing Tasks. Mitigation lives in the doctrine update (Step 5 + Hard rule #10): the Director must check `dispatched_at` before starting decomposition and back off if it's set.

### Option 2 — Split "decompose" from "execute" in the Director's workflow

Refactor `agents/director.md` Step 5 so decomposition is its own step (`add-subtask` Tasks for the approved feature) and execution is a separate step (spawn Heads), each independently triggerable. The Cloud Function in Option 1 only triggers decomposition; execution waits on a second trigger (Director session resume, or another auto-dispatch fired when subtasks land).

**Why not this ADR:**
- The split is a doctrine and tooling change, not an automation. It doesn't solve the "nothing wakes the Director" problem on its own — without Option 1, the Director still has to be awake to run *either* step.
- It's a sensible follow-up after Option 1 ships: once auto-dispatch lands and we observe how often the Director is asleep at execution time (vs. decomposition time), we can decide whether splitting is worth the doctrine surface. Decoupling decomposition from execution would let the User review Task lists *before* Heads run, which is a separate quality of life win — but it's an enhancement to a working auto-dispatch, not a substitute.
- Doing both at once doubles the scope and the blast radius of this change. The auto-dispatch ADR should be small and reversible; the split is a more deliberate workflow rework.

### Option 3 — Hourly janitor process

A scheduled Cloud Function (or a `crontab` on the Windows box, or a GitHub Actions cron) that wakes hourly, scans `features` for docs in `status=open` with no `dispatched_at` and a `feature_approved` event in the last N hours, and issues the same `workflow_dispatch`.

**Why not this ADR:**
- Latency is the wrong shape — the User approves and then waits up to an hour before anything happens. The whole point of the trigger is that approval *is* the start signal; a janitor turns it into a periodic sweep.
- Scheduled functions don't compose with the existing event-driven substrate. `on_message_created` is event-driven; adding a polling sibling makes the system harder to reason about (now we have two pipelines, one push, one pull).
- A janitor is, however, a reasonable belt-and-suspenders backstop *underneath* an event-driven trigger — if Option 1's CAS misfires or the Cloud Function fails silently, an hourly janitor catches the gap. That makes it a follow-up, not the primary mechanism, and only worth building once we have evidence of misfires.

---

## Consequences

### Direct

- **One new Cloud Function** in `functions/main.py` named `on_feature_approved` (or similar), wired in `firebase.json` / function config to the `events` collection in database `prj-tracker`. Operationally identical lifecycle to `on_message_created`: deploy with `firebase deploy --only functions`; monitor via the same Cloud Functions log surface.
- **Two new fields on `features/{id}`:** `dispatched_at` (`Timestamp`, the CAS anchor) and `auto_execute` (`bool`, default unset / treated as `true`). Both are forward-compatible additions to the existing doc shape — no schema migration; existing docs read as "dispatched_at is unset, auto_execute is true." Firestore rules need a new clause permitting the Cloud Function service account to write `dispatched_at`, and permitting the Director (or User) to set `auto_execute`. The rules deployment gap caveat from prior ADRs applies — production rules trail `main` until `firebase deploy --only firestore:rules`.
- **No change to `dcli approve-feature`** (`agent_cli.py` `cmd_approve_feature`). The CLI still flips status and emits the event; the new Cloud Function attaches to the event downstream. The dashboard's green button behavior is unchanged.
- **Doctrine update to `agents/director.md`** at the ADR-workflow Step 5 and at Hard rule #10:
  - **Step 5 update:** the section is currently "Decompose and execute. Now (and only now): ..." It must say that decomposition can arrive automatically via the new Cloud Function and that the Director, on session start, **reads `features/{id}.dispatched_at` before beginning Step 5 work** — if it's set within the cool-off window, decomposition is already underway (or done) and the Director joins the in-flight workflow run rather than starting a parallel one. If `auto_execute=false`, the Director proceeds manually as today. The "Send a cross-ref to Randall and Matt that work has started" line stays — it now fires from whichever path actually started the work.
  - **Hard rule #10 update:** the rule currently reads *"Watch for stuck Heads at every wake-up (`list-stuck`). Never let a Task rot in `in_progress` longer than a working day."* It must add a sibling clause that names the auto-dispatch race directly — something to the effect of *"On wake-up after a `feature_approved` event, check `features/{id}.dispatched_at` before decomposing. If set, the auto-dispatch path is in flight; do not double-write Tasks."* The exact wording is the implementation Head's call; the doctrinal contract is that the Director **never** runs `add-subtask` against a feature whose `dispatched_at` is already set without first reading the resulting workflow run.
- **No code-level changes to anything outside `functions/main.py`, `firestore.rules`, and `agents/director.md`** are required for v1. The dashboard, the CLI, the Head template, the existing workflows — all unchanged.

### Positive

- Removes a manual step that the User and the Director both forget. The button-press becomes the start signal mechanically, not socially.
- Reuses the proven `workflow_dispatch` substrate from `on_message_created` — no new pipeline shape, no new failure modes to learn.
- Idempotency is a single CAS on a single field; opt-out is a single flag. Both are inspectable from the dashboard once surfaced, and from `dcli` / Firestore directly until then.
- The doctrine update makes the race against the human Director explicit and resolvable — no silent collision behavior.
- Foundation for Option 2 (split decompose-from-execute) and Option 3 (janitor backstop) as later refinements. Both follow-ups are additive against this design; neither requires re-doing it.

### Negative

- A new operational surface — one more Cloud Function to keep deployed, observable, and rolled forward when the runtime image moves. Each individual cost is small; the aggregate is "the pipeline has two trigger sources now, not one."
- The doctrine update introduces a precondition (`check dispatched_at`) the Director must observe at every wake-up. If a Director ever forgets to read the field — a Sonnet-class session glitch, an out-of-date prompt — duplicate Tasks could land. The CAS prevents duplicate *dispatches* but does not prevent a human Director that's awake from also running `add-subtask` against a feature the Cloud Function just woke a parallel workflow on. The mitigation is doctrinal, not technical, in v1.
- The Cloud Function's failure modes are silent by default (logs, no chat surface) — unlike `on_message_created` which posts "On it." back to the thread. An ops bug here looks like "the Director didn't wake up after approval, and nobody noticed." Mitigation: emit a `note` event from the Cloud Function on dispatch success and a `note` of `type=error` on dispatch failure, so the dashboard event stream surfaces both paths. Cheap; the implementation Head adds it as part of v1.
- The `auto_execute` flag is currently invisible from the dashboard — it's settable only via direct Firestore write (or a future `dcli` command). For v1 that's acceptable since the default behavior (auto-dispatch on) is what the User wants in the common case. A dashboard surface is a follow-up.

### Risks

- **Cloud Function cold-start latency.** The dispatch firing several seconds after the button-press is fine; firing several minutes after would erode the "approval = start" mental model. Mitigation: nothing special — the same cold-start budget governs `on_message_created` today and the User tolerates it. If it becomes a problem, set `min_instances=1` on this function (modest cost, sub-second wake-up).
- **`workflow_dispatch` rate limits.** GitHub's API caps `workflow_dispatch` at a per-repo rate; in theory a burst of approvals (e.g., Randall mass-approving a backlog) could exceed it. In practice approvals are sparse and the existing `on_message_created` traffic stays well under the cap. If we ever see 429s here, a queue-and-retry shim is a small addition.
- **Stale `dispatched_at`.** If the auto-dispatch fires but the workflow never completes (Cloud Function dispatched, Actions run failed at the runner step), `dispatched_at` is set but no work happens. The doctrine's Hard rule #10 "stuck Heads" sweep already covers `in_progress` Tasks rotting; it doesn't yet cover features whose dispatch quietly died. A janitor (Option 3) is the natural backstop here, but only worth building once we have evidence of failures — for v1, the Director's own startup ritual (read recent events, look for `feature_approved` without a corresponding workflow_dispatch_result) is enough.
- **`auto_execute=false` set after approval.** If the User flips the flag *after* clicking Approve but *before* the Cloud Function reads it, behavior depends on read ordering. The Cloud Function's transaction reads the feature doc fresh on each invocation, so the latest flag value wins — but the race window is short (seconds). The User-facing rule is "set `auto_execute=false` *before* approving" if the goal is to suppress dispatch; setting it after is best-effort. Document this in the eventual dashboard surface.

### Follow-ups (out of scope for this ADR — see Options 2 and 3)

- **Split decompose from execute** (Option 2). Once auto-dispatch is observed in production for a sprint, decide whether the Cloud Function should wake a "decompose-only" workflow that then waits for a second trigger to execute Heads. That gives the User a review window between Task list creation and Head dispatch. Not this ADR because it's a doctrine and tooling change with its own design questions (where does the User approve the Task list? what's the second trigger?) that deserve their own document.
- **Hourly janitor** (Option 3). A scheduled function that sweeps for approved features with no `dispatched_at` (or with a `dispatched_at` older than the cool-off and no `subtask_created` events to show for it) and re-issues the dispatch. Not this ADR because it's a belt-and-suspenders backstop that's only worth building once we have evidence of CAS misfires or Cloud Function failures. Plan it once we see one.
- **Dashboard surface for `auto_execute`.** A per-feature toggle on the card UI so the User doesn't have to remember a Firestore-write CLI. Trivial UI work; defers naturally until the v1 numbers are in.
- **`note`-event surface for Cloud Function dispatch outcomes.** Folded into v1 above as the answer to "the Cloud Function fails silently," but worth restating: every dispatch attempt should produce a visible event on the dashboard's stream.

---

## Implementation amendments (post-merge)

The shipped implementation refined the Decision in four ways worth recording so future readers don't get confused by the diff between the original draft and what's actually running:

- **Intent collapsed to one line.** The Decision described an intent payload like `"ADR <NNNN> approved by <approver>. Decompose feature <feature_id> into 2–4 Tasks and dispatch execution Heads per agents/director.md Step 5."` In practice this wasted turns at the coder Head — it re-stated procedure already encoded in the `execute-adr` skill. The deployed Cloud Function now sends `"Execute ADR N"` (or `"Execute the approved ADR for feature <id>"` when no ADR number is set), matching what a human types when DMing the director. The auto-dispatch path is therefore indistinguishable downstream from a manual DM, which is a property worth keeping.

- **Decomposition is the Head's job, not the Director's.** The Decision section described `agents/director.md` Step 5 as where 2–4 Tasks are written, and framed that as a Director-level action. The shipped `execute-adr` skill owns decomposition in its Step 2 instead — a single Sonnet head receives the approval intent, lists 2–4 Tasks on the board immediately (so progress is visible before any code is touched), then implements them, all in one 7–8 turn run. `agents/director.md` Step 5 was rewritten to match: the Director only intervenes if auto-dispatch did not fire (`auto_execute=false`, `dispatched_at` stale, Cloud Function down). End state of both paths is identical.

- **Drafter scope discipline added to `write-adr`.** Adjacent improvement that pays for itself once auto-dispatch is live: the `write-adr` skill now instructs drafters to name specific files / modules / steps in the Decision section so the downstream coder's decomposition is mechanical. A Decision that reads "refactor the rate limiter" costs the coder turns guessing scope; "(1) swap token-bucket impl in `rate_limit.py`, (2) update callers in `api/` and `worker/`, (3) add benchmark" gives them three Tasks for free. The contract is soft — the coder will still decompose either way — but the turn-budget delta is real.

- **One Cloud Run IAM grant needed at deploy.** Not anticipated in the Decision: deploying a new gen-2 Cloud Function creates a new Cloud Run service whose default IAM policy lacks the trigger SA's `roles/run.invoker`. The first deploy of `on-feature-approved` rejected every incoming event with `IAM principal lacks {run.routes.invoke} permission` for ~5 minutes before this was diagnosed. The fix is one extra `gcloud run services add-iam-policy-binding` call; the README's deploy command now includes it. `on-message-created` had this grant from its original deploy, which is why DMs continued working while approvals were broken. Worth folding into any future Cloud Function deploy script.

---

*Drafted by Head (drafter) under dASH — subtask `a1hU6f4ZK291CBa6JcvV`. Implementation amendments added by dASH Director after PR #19 merge.*
