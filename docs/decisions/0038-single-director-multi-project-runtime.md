# ADR 0038 — dIRT: Single-Director, Multi-Project Runtime

**Status:** Proposed
**Date:** 2026-05-23
**Authors:** Jones (dIRT), drafted at Randall's direction

## Context

dIRT inherited the multi-Director model from director-pattern: each project repo carries its own `directors/{id}` record with a persona (Carl Sagan, Hermione Granger, Dmitri Mendeleev, etc.), plus duplicated copies of the runtime (`agent_cli.py`, `firestore_db.py`, `dcli`, `agents/director.md`, `agents/head.md`, `.github/workflows/director-agent.yml`, `.github/scripts/*`). Across 7 personal projects (dCAD, dERP, dWEB, dACE, dASH, dOCS, dPART) that's roughly 14,000 duplicated lines of runtime code that drift out of sync.

Randall has elected to collapse this to **one Director — Jones, on `directors/dirt`** — running all 7 projects. director-pattern stays as the company-side runtime (persona-less, unchanged in scope). The two CLIs intentionally diverge; that's Randall's call. Per-project character names survive only as commit `Co-Authored-By` trailers — a nod to the old lore.

Per-repo runtime strip is already complete (see `chore/strip-runtime-to-dirt` branches across the 7 project repos). What remains is the dIRT-side work: data model shift, CLI updates, doctrine update, and project.json reshape.

## Decision

1. **Single Director identity.** Jones (`directors/dirt`) is the only Director for Randall's personal stack. The records for dCAD/dERP/dWEB/dACE/dASH/dOCS/dPART are repurposed as **project records** under Jones.
2. **Semantic shift, not data migration.** The existing `directors/{project_id}` records keep their IDs and history. `features.director_id` continues to scope work to a project. Zero feature/subtask data migration.
3. **The `directors` collection now holds two record shapes**, disambiguated by a new `runtime` field:
   - `runtime: "dirt"` on `directors/dirt` itself + on every project record under Jones.
   - Records that don't carry `runtime` (or carry something else) are unaffected (e.g., company-side Directors under director-pattern).
4. **Per-repo character names survive as commit signatures.** Each project record carries a `commit_signature` block (name + email). Commits made by Jones in that repo carry the project's character as a `Co-Authored-By` trailer.
5. **dcli walks up from cwd to find `project.json`.** From dIRT root → system mode. From a project repo → project-scoped mode. Same binary, same Jones identity, different scope.
6. **Cross-project features under `director_id="dirt"`** represent dIRT system-level work (infrastructure, doctrine, migration). Distinct from project work.
7. **ADRs will be tracked on dASH, not on GH.** ADRs should be drafted and posted to dASH for review. There is no reason to send a user to Github to read a file. 
## Options considered

- **A. Keep multi-Director model.** Per-project Directors continue to exist. Rejected — duplication is the entire problem being solved.
- **B. Full data migration: every feature gets `director_id="dirt"` + new `project_id` field.** Cleaner schema but requires touching every feature/subtask document in Firestore. High risk for marginal cleanliness gain. Rejected.
- **C (CHOSEN). Semantic shift: `directors/{id}` records become project records; `feature.director_id` continues to identify project; zero data migration.** Lowest disruption. Preserves existing URLs and tracking. Mixed-shape collection is acceptable cost.

## Consequences

**Positive:**
- One agent identity (Jones). No persona switching.
- One canonical runtime location (dIRT). One CLI. One doctrine.
- Per-project repos shed ~2,000 lines of duplicated runtime each.
- Head-spawn costs drop — slimmer doctrine, no persona ceremony.
- Existing dashboard URLs and board tracking continue to work unchanged.

**Negative:**
- The `directors` collection now mixes "real Director records" with "project records." Schema isn't pure. Mitigated by the `runtime` field disambiguating; the cost is conceptual, not operational.
- director-pattern and dIRT CLIs will drift in capabilities. Accepted.
- The `personality` and `head_naming_pool` fields linger on project records as dead data until a later cleanup pass.

## Schema delta — Firestore `directors` collection

For each project record `{dcad, derp, dweb, dace, dash, dOCS, dpart}`:

| Field | Action | Value |
|---|---|---|
| `runtime` | ADD | `"dirt"` |
| `commit_signature` | ADD | `{ "name": <character>, "email": "<id>@dapp-controls.com" }` — mirrors existing `director_name` field |
| `github_remote` | ADD | The repo's `origin` URL (looked up from local git config) |
| `repo_path` | ENSURE | Local absolute path (some records have it; ensure all do) |
| `personality` | DEPRECATE | Keep field for back-compat; no longer read by CLI. Removed in a future cleanup. |
| `head_naming_pool` | DEPRECATE | Already empty in most records. Removed in a future cleanup. |
| `director_name` | KEEP | Read-only source for `commit_signature.name` until we phase it out. |

For `directors/dirt`:

| Field | Action | Value |
|---|---|---|
| `runtime` | ADD | `"dirt"` (self-reference) |
| `owned_projects` | ADD | `["dcad", "derp", "dweb", "dace", "dash", "dOCS", "dpart"]` |
| `system_root` | KEEP | Already `true` |

**Features and subtasks: no schema changes.** Their `director_id` field continues to scope work — to a project (`"dcad"`, `"derp"`, ...) or to dIRT system work (`"dirt"`).

## `project.json` shape — each project repo

**New shape:**

```json
{
  "project_id": "dcad",
  "project_name": "dCAD",
  "runtime": "dirt",
  "repo_path": "C:\\Users\\randa\\source\\repos\\dCAD",
  "github_remote": "https://github.com/dapp-controls/dCAD.git",
  "github_org": "dapp-controls",
  "commit_signature": {
    "name": "Carl Sagan",
    "email": "dcad@dapp-controls.com"
  },
  "description": "Panel-shop engine + AutoCAD Electrical 2025 plugin for refrigeration panel drawings. Targets Danfoss + Copeland controllers."
}
```

**Field changes from the old shape:**

| Old | New | Notes |
|---|---|---|
| `director_id` | `project_id` | CLI accepts both during transition. |
| `director_name` | `commit_signature.name` | Same character, new home. |
| `personality` | REMOVED | Jones is the agent everywhere. |
| `head_naming_pool` | REMOVED | Already legacy. |
| — | `runtime` (NEW) | Declares dIRT owns the agentic work. |
| — | `commit_signature.email` (NEW) | Used in `Co-Authored-By` trailers. |
| — | `github_remote`, `github_org` (NEW) | For dashboard linking + Head briefs. |

**Fields that stay only on dIRT's own `project.json`** (not project repos): `system_root`, `system_name`, `scope`, `elevated`, `principal`, `director_name` (Jones).

## CLI changes — dIRT's `agent_cli.py`

| Command | Behavior |
|---|---|
| `dcli info` | **At dIRT root:** prints Jones identity + list of `owned_projects` with repo_path each. **In a project repo:** prints that project's `project.json` resolved + Jones identity. |
| `dcli kickoff` | **At dIRT root:** system-level kickoff (Jones + project list + system-wide recent events). **In a project repo:** project-scoped kickoff (recent events filtered to that project, ready Tasks, blockers). |
| `dcli list-projects` | **NEW.** Returns all records where `runtime == "dirt"`, excluding `directors/dirt` itself. Includes project_id, name, repo_path, github_remote. |
| `dcli list-directors` | Returns records WITHOUT `runtime == "dirt"` + the dIRT record. Used for cross-Director coordination (dirt ↔ director-pattern company-side). |
| `dcli add-feature`, `add-subtask`, `event`, `add-artifact`, etc. | `director_id` is auto-filled from cwd's `project.json` (its `project_id`). From dIRT root with no override, defaults to `"dirt"` (system-level work). `--project <id>` flag overrides explicitly. |
| `dcli register-agent`, `claim-task`, `complete-task` | Same wire format. `agent_id` always belongs to `directors/dirt`; `feature_id` carries the project scope. |
| `dcli whoami` | Unchanged. Reads `user.json`. |
| `dcli doctrine` | Prints absolute paths to canonical `director.md` + `head.md` in dIRT (not director-pattern). |

## Kickoff behavior — explicit

**At dIRT root (cwd = `C:\Users\randa\source\repos\dIRT`):**

> "You are Jones, dIRT system root. You have the personality of Steve jobs. You behave like him in every regard. Exact, diligent, innovator, craftsman, unrelenting, high standard, never settles. You orchestrate Randall's dAPP projects: dCAD, dERP, dWEB, dACE, dASH, dOCS, dPART. Recent activity across all of them: [last 5 events]. Open Stories: [count by project]. Blockers: [count]. What's first?"

**In a project repo (cwd has a `project.json` with `runtime: "dirt"`):**

> "You are Jones, scoped to <project_name>. Recent activity in this project: [last 5 events]. Open Stories: [list]. Blockers: [list]. Commit signature for this repo: <character>. What's first?"

Same agent (Jones). Different scope. No persona switching.

## Migration steps (one-time, in order)

1. **Firestore data updates** (script or interactive):
   - For each `directors/{dcad,derp,dweb,dace,dash,dOCS,dpart}`: add `runtime`, `commit_signature` (name from existing `director_name`; email = `<id>@dapp-controls.com`), `github_remote` (from local git config of corresponding repo), ensure `repo_path`.
   - For `directors/dirt`: add `runtime: "dirt"`, `owned_projects: [...]`.
2. **dIRT CLI updates** in `agent_cli.py` + `.github/scripts/agent_cli.py` (sync both root + scripts copy per dIRT's existing mirror pattern):
   - Add `cmd_list_projects`.
   - Modify `cmd_info` and `cmd_kickoff` to branch on `system_root`.
   - Add `--project` flag support to relevant commands; default fill from cwd's `project.json`.
3. **dIRT doctrine update** — `agents/director.md` (dIRT-specific; **separate from the director-pattern rewrite already shipped**):
   - Single-Director, multi-project model.
   - Project switching by cwd. Commit signature ceremony per project.
4. **Per-project `project.json` reshape** (on each existing `chore/strip-runtime-to-dirt` branch, or new branches as needed):
   - Replace old shape with new shape per the spec above.
   - CLI accepts both shapes during transition; once all 7 are migrated, deprecate old shape.
5. **Smoke test:**
   - From dIRT root: `dcli info` → shows Jones + 7 projects. `dcli list-projects` → returns 7. `dcli kickoff` → system-level brief.
   - `cd ../dCAD` → `dcli info` → shows dCAD context, Jones identity. `dcli add-feature --title "Test"` lands on `directors/dcad`'s feature list with author = Randall.
   - From dIRT root with `--project dcad`: same as previous, but cwd doesn't change.
   - Trigger a Head from a project repo; verify commit has `Co-Authored-By: <character>` trailer.

## Out of scope

- **Dashboard UI relabeling** (Directors → Projects semantically). Cosmetic; defer.
- **Removing legacy fields** (`personality`, `head_naming_pool`). Defer to a cleanup pass once we're confident nothing reads them.
- **Renaming the `directors` Firestore collection to `projects`.** Would require touching every reference in every script. Not worth the risk for cosmetic gain.
- **dWEB on Matt's machine** (`C:/Users/mbarl/source/repos/dWEB`). Out of dIRT's scope. Matt continues his own workflow against the same repo.
- **director-pattern CLI parity.** Intentionally diverging per Randall's call.
- **Auto-dispatch on `feature_approved`** (ADR 0037). Independent decision; not touched here.

## Implementation order

1. Firestore data delta (manual script or `dcli`-level commands).
2. dIRT CLI updates.
3. dIRT doctrine rewrite (`agents/director.md`).
4. Per-project `project.json` reshape (extend `chore/strip-runtime-to-dirt` branches).
5. Smoke test end-to-end.
6. Merge all 7 strip branches to their respective `main`/`master` once smoke test passes.

Each step is a candidate for a separate Head dispatch (Sonnet) once this ADR is approved.

## Approval

Awaiting Randall.
