# Git remote handoff — dIRT → personal GH, dASH → dapp-controls org

Authored by Jones (dIRT) on 2026-05-23 as part of the dIRT / dASH split.

This is the **manual step Randall runs** after the file-level split is done. Two separate handoffs. Run each section in order. Each one is small. Do not skip the verification commands.

---

## dIRT — point at Randall's personal GitHub

**Personal GH remote:** `https://github.com/SeneC0de/dIRT.git` (provided by Randall, captured in `dIRT/project.json` as `github_remote`).

### 1. Inspect the current remote

```powershell
cd C:\Users\randa\source\repos\dIRT
git remote -v
```

Expected current value (from before the split):

```
origin  https://github.com/dapp-controls/director-pattern.git (fetch)
origin  https://github.com/dapp-controls/director-pattern.git (push)
```

That's wrong. It points at the company repo. We're fixing that.

### 2. Repoint origin to your personal GH

Replace `https://github.com/SeneC0de/dIRT.git` with the actual URL you give me.

```powershell
git remote set-url origin https://github.com/SeneC0de/dIRT.git
git remote -v   # verify
```

### 3. Decide on history strategy

Before pushing, you have one decision to make:

- **(A) Push existing history.** The current dIRT git history is identical to director-pattern's up to the split point — your personal GH repo will contain all that company history (commits, branches, ADRs). Fine if you want continuity; loud if you don't want company history on your personal account.
- **(B) Squash to a clean root.** Start your personal repo from a fresh "Initial commit: dIRT" with no prior history. Cleaner, but you lose the trail.

If **(A)** — just push:

```powershell
# If the personal repo is empty:
git push -u origin main

# If main already exists upstream and you want yours to win:
git push -u origin main --force-with-lease
```

If **(B)** — squash root before pushing:

```powershell
# DESTRUCTIVE — only do this if you're sure
git checkout --orphan fresh-main
git add -A
git commit -m "Initial commit: dIRT (Randall's personal Director runtime)"
git branch -D main
git branch -m main
git push -u origin main --force
```

### 4. Push the in-flight branches you actually want

The repo has ~25 `claude/*` worktree branches and a few `feature-*` / `impl/*` branches from the spinoff. Most are stale. After moving to personal GH, only push the branches you care about — don't carbon-copy every old worktree.

```powershell
git branch       # see what you have
git push origin <branch-you-want-to-keep>
```

To prune the stale local branches afterward (optional cleanup):

```powershell
# List branches NOT merged into main
git branch --no-merged main
# Delete a single dead branch
git branch -D <stale-branch>
```

### 5. Verify

```powershell
git remote -v
gh repo view  # confirms the GH repo is reachable
```

---

## dASH — push to `dapp-controls/dASH`

### 1. Initialize the dASH repo (if not already a git repo)

```powershell
cd C:\Users\randa\source\repos\dASH
git status 2>$null
# If "not a git repository":
git init
git branch -M main
```

### 2. Create the GitHub repo under dapp-controls

```powershell
gh repo create dapp-controls/dASH --private --source=. --description "dAPP Controls dashboard product (Firebase Hosting + Cloud Functions)" --remote origin
```

(`--private` because the dashboard talks to internal Firestore data; flip to `--public` only with explicit reason.)

### 3. First commit & push

```powershell
git add -A
git status              # eyeball before committing
git commit -m "Initial commit: dASH split out from director-pattern

The dashboard product (web/ Firebase Hosting, functions/ Cloud Functions,
and ADRs 0001/0003/0004) was previously co-located with the Director
platform infrastructure in director-pattern. This repo is its standalone
home, owned by Hermione Granger (director_id: dash).

Split executed 2026-05-23 by Jones (dIRT)."
git push -u origin main
```

### 4. Set the GitHub Actions secret

The Director Agent workflow (when it lands here via `deploy_workflow.sh` from dIRT or director-pattern) reads `FIREBASE_SERVICE_ACCOUNT_JSON`:

```powershell
gh secret set FIREBASE_SERVICE_ACCOUNT_JSON --repo dapp-controls/dASH --body (Get-Content C:\Users\randa\source\repos\dIRT\gcp-key.json -Raw)
gh secret set ANTHROPIC_API_KEY --repo dapp-controls/dASH
```

(The second command will prompt you for the key.)

### 5. Verify

```powershell
gh repo view dapp-controls/dASH
gh secret list --repo dapp-controls/dASH
```

---

## After both pushes are green

Run this from dIRT once both remotes are settled, so the `directors/dash` and `directors/dirt` Firestore records know where their code lives:

```powershell
cd C:\Users\randa\source\repos\dIRT
# Sets the github_repo field on the Director's Firestore record (used by Cloud Functions to dispatch workflows)
python agent_cli.py set-director-repo --director-id dash --github-repo dapp-controls/dASH
python agent_cli.py set-director-repo --director-id dirt --github-repo SeneC0de/dIRT
```

If `set-director-repo` isn't a CLI command yet, the Firestore field is `directors/{id}.github_repo`. Set it via the dashboard or by editing the Director doc directly.

---

## Why this is a manual step

I'm not running `git push --force` or `gh repo create` for you from inside a sandbox. Those are decisions about your personal GH account and a billed company GH org — they're yours to make, eyes open, hands on keyboard. I'll prep the commands; you pull the trigger.
